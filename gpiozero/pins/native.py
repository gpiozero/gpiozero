from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
nstr = str
str = type('')

import io
import os
import mmap
import errno
import struct
import warnings
from time import sleep
from threading import Thread, Event, Lock
from collections import Counter

from . import LocalPin, PINS_CLEANUP
from .data import pi_info
from ..exc import (
    PinInvalidPull,
    PinInvalidEdges,
    PinInvalidFunction,
    PinFixedPull,
    PinSetInput,
    PinNonPhysical,
    PinNoPins,
    )


class GPIOMemory(object):

    GPIO_BASE_OFFSET = 0x200000
    PERI_BASE_OFFSET = {
        'BCM2708': 0x20000000,
        'BCM2835': 0x20000000,
        'BCM2709': 0x3f000000,
        'BCM2836': 0x3f000000,
        }

    # From BCM2835 data-sheet, p.91
    GPFSEL_OFFSET   = 0x00 >> 2
    GPSET_OFFSET    = 0x1c >> 2
    GPCLR_OFFSET    = 0x28 >> 2
    GPLEV_OFFSET    = 0x34 >> 2
    GPEDS_OFFSET    = 0x40 >> 2
    GPREN_OFFSET    = 0x4c >> 2
    GPFEN_OFFSET    = 0x58 >> 2
    GPHEN_OFFSET    = 0x64 >> 2
    GPLEN_OFFSET    = 0x70 >> 2
    GPAREN_OFFSET   = 0x7c >> 2
    GPAFEN_OFFSET   = 0x88 >> 2
    GPPUD_OFFSET    = 0x94 >> 2
    GPPUDCLK_OFFSET = 0x98 >> 2

    def __init__(self):
        try:
            self.fd = os.open('/dev/gpiomem', os.O_RDWR | os.O_SYNC)
        except OSError:
            try:
                self.fd = os.open('/dev/mem', os.O_RDWR | os.O_SYNC)
            except OSError:
                raise IOError(
                    'unable to open /dev/gpiomem or /dev/mem; '
                    'upgrade your kernel or run as root')
            else:
                offset = self.peripheral_base() + self.GPIO_BASE_OFFSET
        else:
            offset = 0
        self.mem = mmap.mmap(self.fd, 4096, offset=offset)

    def close(self):
        self.mem.close()
        os.close(self.fd)

    def peripheral_base(self):
        try:
            with io.open('/proc/device-tree/soc/ranges', 'rb') as f:
                f.seek(4)
                return struct.unpack(nstr('>L'), f.read(4))[0]
        except IOError:
            with io.open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Hardware'):
                        try:
                            return self.PERI_BASE_OFFSET[line.split(':')[1].strip()]
                        except KeyError:
                            raise IOError('unable to determine RPi revision')
        raise IOError('unable to determine peripheral base')

    def __getitem__(self, index):
        return struct.unpack_from(nstr('<L'), self.mem, index * 4)[0]

    def __setitem__(self, index, value):
        struct.pack_into(nstr('<L'), self.mem, index * 4, value)


class GPIOFS(object):

    GPIO_PATH = '/sys/class/gpio'

    def __init__(self):
        self._lock = Lock()
        self._pin_refs = Counter()

    def path(self, name):
        return os.path.join(self.GPIO_PATH, name)

    def export(self, pin):
        with self._lock:
            if self._pin_refs[pin] == 0:
                # Set the count to 1 to indicate the GPIO is already exported
                # (we'll correct this if we find it isn't, but this enables us
                # to "leave the system in the state we found it")
                self._pin_refs[pin] = 1
                result = None
                # Dirty hack to wait for udev to set permissions on
                # gpioN/direction; there's no other way around this as there's
                # no synchronous mechanism for setting permissions on sysfs
                for i in range(10):
                    try:
                        result = io.open(self.path('gpio%d/value' % pin), 'w+b', buffering=0)
                    except IOError as e:
                        if e.errno == errno.ENOENT:
                            with io.open(self.path('export'), 'wb') as f:
                                f.write(str(pin).encode('ascii'))
                            # Pin wasn't exported, so correct the ref-count
                            self._pin_refs[pin] = 0
                        elif e.errno == errno.EACCES:
                            sleep(i / 100)
                        else:
                            raise
                    else:
                        break
                if not result:
                    raise RuntimeError('failed to export pin %d' % pin)
            else:
                result = io.open(self.path('gpio%d/value' % pin), 'w+b', buffering=0)
            self._pin_refs[pin] += 1
            return result

    def unexport(self, pin):
        with self._lock:
            self._pin_refs[pin] -= 1
            if self._pin_refs[pin] == 0:
                with io.open(self.path('unexport'), 'wb') as f:
                    f.write(str(pin).encode('ascii'))


class NativePin(LocalPin):
    """
    Uses a built-in pure Python implementation to interface to the Pi's GPIO
    pins. This is the default pin implementation if no third-party libraries
    are discovered.

    .. warning::

        This implementation does *not* currently support PWM. Attempting to
        use any class which requests PWM will raise an exception. This
        implementation is also experimental; we make no guarantees it will
        not eat your Pi for breakfast!

    You can construct native pin instances manually like so::

        from gpiozero.pins.native import NativePin
        from gpiozero import LED

        led = LED(NativePin(12))
    """

    _MEM = None
    _PINS = {}

    GPIO_FUNCTIONS = {
        'input':   0b000,
        'output':  0b001,
        'alt0':    0b100,
        'alt1':    0b101,
        'alt2':    0b110,
        'alt3':    0b111,
        'alt4':    0b011,
        'alt5':    0b010,
        }

    GPIO_PULL_UPS = {
        'up':       0b10,
        'down':     0b01,
        'floating': 0b00,
        'reserved': 0b11,
        }

    GPIO_EDGES = {
        'both':    (True,  True),
        'rising':  (True,  False),
        'falling': (False, True),
        'none':    (False, False),
        }

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}
    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}
    GPIO_EDGES_NAMES = {v: k for (k, v) in GPIO_EDGES.items()}

    PI_INFO = None

    def __new__(cls, number):
        if not cls._PINS:
            cls._MEM = GPIOMemory()
            PINS_CLEANUP.append(cls._MEM.close)
        if cls.PI_INFO is None:
            cls.PI_INFO = pi_info()
        if not (0 <= number < 54):
            raise ValueError('invalid pin %d specified (must be 0..53)' % number)
        try:
            return cls._PINS[number]
        except KeyError:
            self = super(NativePin, cls).__new__(cls)
            try:
                cls.PI_INFO.physical_pin('GPIO%d' % number)
            except PinNoPins:
                warnings.warn(
                    PinNonPhysical(
                        'no physical pins exist for GPIO%d' % number))
            self._number = number
            self._func_offset = self._MEM.GPFSEL_OFFSET + (number // 10)
            self._func_shift = (number % 10) * 3
            self._set_offset = self._MEM.GPSET_OFFSET + (number // 32)
            self._set_shift = number % 32
            self._clear_offset = self._MEM.GPCLR_OFFSET + (number // 32)
            self._clear_shift = number % 32
            self._level_offset = self._MEM.GPLEV_OFFSET + (number // 32)
            self._level_shift = number % 32
            self._pull_offset = self._MEM.GPPUDCLK_OFFSET + (number // 32)
            self._pull_shift = number % 32
            self._edge_offset = self._MEM.GPEDS_OFFSET + (number // 32)
            self._edge_shift = number % 32
            self._rising_offset = self._MEM.GPREN_OFFSET + (number // 32)
            self._rising_shift = number % 32
            self._falling_offset = self._MEM.GPFEN_OFFSET + (number // 32)
            self._falling_shift = number % 32
            self._when_changed = None
            self._change_thread = None
            self._change_event = Event()
            self.function = 'input'
            self.pull = 'up' if cls.PI_INFO.pulled_up('GPIO%d' % number) else 'floating'
            self.bounce = None
            self.edges = 'both'
            cls._PINS[number] = self
            return self

    def __repr__(self):
        return "GPIO%d" % self._number

    @property
    def number(self):
        return self._number

    def close(self):
        self.when_changed = None
        self.function = 'input'
        self.pull = 'up' if self.PI_INFO.pulled_up('GPIO%d' % self.number) else 'floating'

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[(self._MEM[self._func_offset] >> self._func_shift) & 7]

    def _set_function(self, value):
        try:
            value = self.GPIO_FUNCTIONS[value]
        except KeyError:
            raise PinInvalidFunction('invalid function "%s" for pin %r' % (value, self))
        self._MEM[self._func_offset] = (
            self._MEM[self._func_offset]
            & ~(7 << self._func_shift)
            | (value << self._func_shift)
            )

    def _get_state(self):
        return bool(self._MEM[self._level_offset] & (1 << self._level_shift))

    def _set_state(self, value):
        if self.function == 'input':
            raise PinSetInput('cannot set state of pin %r' % self)
        if value:
            self._MEM[self._set_offset] = 1 << self._set_shift
        else:
            self._MEM[self._clear_offset] = 1 << self._clear_shift

    def _get_pull(self):
        return self.GPIO_PULL_UP_NAMES[self._pull]

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull('cannot set pull on non-input pin %r' % self)
        if value != 'up' and self.PI_INFO.pulled_up('GPIO%d' % self.number):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            value = self.GPIO_PULL_UPS[value]
        except KeyError:
            raise PinInvalidPull('invalid pull direction "%s" for pin %r' % (value, self))
        self._MEM[self._MEM.GPPUD_OFFSET] = value
        sleep(0.000000214)
        self._MEM[self._pull_offset] = 1 << self._pull_shift
        sleep(0.000000214)
        self._MEM[self._MEM.GPPUD_OFFSET] = 0
        self._MEM[self._pull_offset] = 0
        self._pull = value

    def _get_edges(self):
        rising = bool(self._MEM[self._rising_offset] & (1 << self._rising_shift))
        falling = bool(self._MEM[self._falling_offset] & (1 << self._falling_shift))
        return self.GPIO_EDGES_NAMES[(rising, falling)]

    def _set_edges(self, value):
        try:
            rising, falling = self.GPIO_EDGES[value]
        except KeyError:
            raise PinInvalidEdges('invalid edge specification "%s" for pin %r' % self)
        f = self.when_changed
        self.when_changed = None
        try:
            self._MEM[self._rising_offset] = (
                self._MEM[self._rising_offset]
                & ~(1 << self._rising_shift)
                | (rising << self._rising_shift)
                )
            self._MEM[self._falling_offset] = (
                self._MEM[self._falling_offset]
                & ~(1 << self._falling_shift)
                | (falling << self._falling_shift)
                )
        finally:
            self.when_changed = f

    def _get_when_changed(self):
        return self._when_changed

    def _set_when_changed(self, value):
        if self._when_changed is None and value is not None:
            self._when_changed = value
            self._change_thread = Thread(target=self._change_watch)
            self._change_thread.daemon = True
            self._change_event.clear()
            self._change_thread.start()
        elif self._when_changed is not None and value is None:
            self._change_event.set()
            self._change_thread.join()
            self._change_thread = None
            self._when_changed = None
        else:
            self._when_changed = value

    def _change_watch(self):
        offset = self._edge_offset
        mask = 1 << self._edge_shift
        self._MEM[offset] = mask # clear any existing detection bit
        while not self._change_event.wait(0.001):
            if self._MEM[offset] & mask:
                self._MEM[offset] = mask
                self._when_changed()

