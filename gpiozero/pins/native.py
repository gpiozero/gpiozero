# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2020 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
try:
    range = xrange
except NameError:
    pass
nstr = str
str = type('')

import io
import os
import sys
import mmap
import errno
import struct
import select
import warnings
from time import sleep
from threading import Thread, Event, RLock
from collections import Counter
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from .local import LocalPiPin, LocalPiFactory
from ..exc import (
    PinInvalidPull,
    PinInvalidEdges,
    PinInvalidFunction,
    PinFixedPull,
    PinSetInput,
    )


def dt_resolve_alias(alias, root='/proc/device-tree'):
    """
    Returns the full path of a device-tree alias. For example:

        >>> dt_resolve_alias('gpio')
        '/proc/device-tree/soc/gpio@7e200000'
        >>> dt_resolve_alias('ethernet0', root='/proc/device-tree')
        '/proc/device-tree/scb/ethernet@7d580000'
    """
    # XXX Change this return a pathlib.Path when we drop 2.x
    filename = os.path.join(root, 'aliases', alias)
    with io.open(filename, 'rb') as f:
        node, tail = f.read().split(b'\0', 1)
        fs_encoding = sys.getfilesystemencoding()
        return os.path.join(root, node.decode(fs_encoding).lstrip('/'))

def dt_peripheral_reg(node, root='/proc/device-tree'):
    """
    Returns the :class:`range` covering the registers of the specified *node*
    of the device-tree, mapped to the CPU's address space. For example:

        >>> reg = dt_peripheral_reg(dt_resolve_alias('gpio'))
        >>> '%#x..%#x' % (reg.start, reg.stop)
        '0xfe200000..0xfe2000b4'
        >>> hex(dt_peripheral_reg(dt_resolve_alias('ethernet0')).start)
        '0xfd580000'
    """
    # Returns a tuple of (address-cells, size-cells) for *node*
    def _cells(node):
        with io.open(os.path.join(node, '#address-cells'), 'rb') as f:
            address_cells = struct.unpack(nstr('>L'), f.read())[0]
        with io.open(os.path.join(node, '#size-cells'), 'rb') as f:
            size_cells = struct.unpack(nstr('>L'), f.read())[0]
        return (address_cells, size_cells)

    # Returns a generator function which, given a file-like object *source*
    # iteratively decodes it, yielding a tuple of values from it. Each tuple
    # contains one integer for each specified *length*, which is the number of
    # 32-bit device-tree cells that make up that value.
    def _reader(*lengths):
        structs = [struct.Struct(nstr('>{cells}L'.format(cells=cells)))
                   for cells in lengths]
        offsets = [sum(s.size for s in structs[:i])
                   for i in range(len(structs))]
        buf_len = sum(s.size for s in structs)

        def fn(source):
            while True:
                buf = source.read(buf_len)
                if not buf:
                    break
                elif len(buf) < buf_len:
                    raise IOError('failed to read {buf_len} bytes'.format(
                        buf_len=buf_len))
                row = ()
                for offset, s in zip(offsets, structs):
                    cells = s.unpack_from(buf, offset)
                    value = 0
                    for cell in cells:
                        value = (value << 32) | cell
                    row += (value,)
                yield row
        return fn

    # Returns a list of (child-range, parent-range) tuples for *node*
    def _ranges(node):
        child_cells, size_cells = _cells(node)
        parent = os.path.dirname(node)
        parent_cells, _ = _cells(parent)
        ranges_reader = _reader(child_cells, parent_cells, size_cells)
        with io.open(os.path.join(node, 'ranges'), 'rb') as f:
            return [
                (range(child_base, child_base + size),
                 range(parent_base, parent_base + size))
                for child_base, parent_base, size in ranges_reader(f)
            ]

    # XXX Replace all this gubbins with pathlib.Path stuff once we drop 2.x
    node = os.path.join(root, node)
    parent = os.path.dirname(node)
    child_cells, size_cells = _cells(parent)
    reg_reader = _reader(child_cells, size_cells)
    with io.open(os.path.join(node, 'reg'), 'rb') as f:
        base, size = list(reg_reader(f))[0]
    while parent != root:
        # Iterate up the hierarchy, resolving the base address as we go
        if os.path.exists(os.path.join(parent, 'ranges')):
            for child_range, parent_range in _ranges(parent):
                if base in child_range:
                    # XXX Can't use .start here as python2's crappy xrange
                    # lacks it; change this when we drop 2.x!
                    base += parent_range[0] - child_range[0]
                    break
        parent = os.path.dirname(parent)
    return range(base, base + size)


class GPIOMemory(object):
    GPIO_BASE_OFFSET = 0x200000
    PERI_BASE_OFFSET = {
        'BCM2835': 0x20000000,
        'BCM2836': 0x3f000000,
        'BCM2837': 0x3f000000,
        'BCM2711': 0xfe000000,
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
    # pull-control registers for BCM2711
    GPPUPPDN_OFFSET = 0xe4 >> 2

    def __init__(self, soc):
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
                offset = self.gpio_base(soc)
        else:
            offset = 0
        self.mem = mmap.mmap(self.fd, 4096, offset=offset)
        # Register reads and writes must be in native format (otherwise
        # struct resorts to individual byte reads/writes and you can't hit
        # half a register :). For arm64 compat we have to figure out what the
        # native unsigned 32-bit type is...
        try:
            self.reg_fmt = {
                struct.calcsize(fmt): fmt
                for fmt in (nstr('@I'), nstr('@L'))
            }[4]
        except KeyError:
            raise RuntimeError('unable to find native unsigned 32-bit type')

    def close(self):
        self.mem.close()
        os.close(self.fd)

    def gpio_base(self, soc):
        try:
            # XXX Replace this with .start when 2.x is dropped
            return dt_peripheral_reg(dt_resolve_alias('gpio'))[0]
        except IOError:
            try:
                return self.PERI_BASE_OFFSET[soc] + self.GPIO_BASE_OFFSET
            except KeyError:
                pass
        raise IOError('unable to determine gpio base')

    def __getitem__(self, index):
        return struct.unpack_from(self.reg_fmt, self.mem, index * 4)[0]

    def __setitem__(self, index, value):
        struct.pack_into(self.reg_fmt, self.mem, index * 4, value)


class GPIOFS(object):
    GPIO_PATH = '/sys/class/gpio'

    def __init__(self, factory, queue):
        self._lock = RLock()
        self._exports = {}
        self._thread = NativeWatchThread(factory, queue)

    def close(self):
        # We *could* track the stuff we've exported and unexport it here, but
        # exports are a system global resource. We can't guarantee that some
        # other process isn't relying on something we've exported. In other
        # words, once exported it's *never* safe to unexport something. The
        # unexport method below is largely provided for debugging and testing.
        if self._thread is not None:
            self._thread.close()
            self._thread = None

    def path(self, name):
        return os.path.join(self.GPIO_PATH, name)

    def path_value(self, pin):
        return self.path('gpio%d/value' % pin)

    def path_dir(self, pin):
        return self.path('gpio%d/direction' % pin)

    def path_edge(self, pin):
        return self.path('gpio%d/edge' % pin)

    def exported(self, pin):
        return pin in self._exports

    def export(self, pin):
        with self._lock:
            try:
                result = self._exports[pin]
            except KeyError:
                result = None
                # Dirty hack to wait for udev to set permissions on
                # gpioN/value; there's no other way around this as there's no
                # synchronous mechanism for setting permissions on sysfs
                for i in range(10):
                    try:
                        # Must be O_NONBLOCK for use with epoll in edge
                        # triggered mode
                        result = os.open(self.path_value(pin),
                                         os.O_RDONLY | os.O_NONBLOCK)
                    except IOError as e:
                        if e.errno == errno.ENOENT:
                            with io.open(self.path('export'), 'wb') as f:
                                f.write(str(pin).encode('ascii'))
                        elif e.errno == errno.EACCES:
                            sleep(i / 100)
                        else:
                            raise
                    else:
                        self._exports[pin] = result
                        break
                # Same for gpioN/edge. It must exist by this point but the
                # chmod -R may not have reached it yet...
                for i in range(10):
                    try:
                        with io.open(self.path_edge(pin), 'w+b'):
                            pass
                    except IOError as e:
                        if e.errno == errno.EACCES:
                            sleep(i / 100)
                        else:
                            raise
                if result is None:
                    raise RuntimeError('failed to export pin %d' % pin)
            return result

    def unexport(self, pin):
        with self._lock:
            try:
                os.close(self._exports.pop(pin))
            except KeyError:
                # unexport should be idempotent
                pass
            else:
                try:
                    with io.open(self.path('unexport'), 'wb') as f:
                        f.write(str(pin).encode('ascii'))
                except IOError as e:
                    if e.errno == errno.EINVAL:
                        # Someone already unexported it; ignore the error
                        pass

    def watch(self, pin):
        with self._lock:
            self._thread.watch(self.export(pin), pin)

    def unwatch(self, pin):
        with self._lock:
            try:
                self._thread.unwatch(self._exports[pin])
            except KeyError:
                pass


class NativeWatchThread(Thread):
    def __init__(self, factory, queue):
        super(NativeWatchThread, self).__init__(
            target=self._run, args=(factory, queue))
        self.daemon = True
        self._stop_evt = Event()
        # XXX Make this compatible with BSDs with poll() option?
        self._epoll = select.epoll()
        self._watches = {}
        self.start()

    def close(self):
        self._stop_evt.set()
        self.join()
        self._epoll.close()

    def watch(self, fd, pin):
        self._watches[fd] = pin
        flags = select.EPOLLIN | select.EPOLLPRI | select.EPOLLET
        self._epoll.register(fd, flags)

    def unwatch(self, fd):
        self._epoll.unregister(fd)
        fd = self._watches.pop(fd, None)

    def _run(self, factory, queue):
        ticks = factory.ticks
        while not self._stop_evt.wait(0):
            for fd, event in self._epoll.poll(0.01):
                when = ticks()
                state = os.read(fd, 1) == b'1'
                os.lseek(fd, 0, 0)
                try:
                    queue.put((self._watches[fd], when, state))
                except KeyError:
                    pass


class NativeDispatchThread(Thread):
    def __init__(self, factory, queue):
        super(NativeDispatchThread, self).__init__(
            target=self._run, args=(factory, queue))
        self.daemon = True
        self._stop_evt = Event()
        self.start()

    def close(self):
        self._stop_evt.set()
        self.join()

    def _run(self, factory, queue):
        pins = factory.pins
        while not self._stop_evt.wait(0):
            try:
                num, ticks, state = queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                pin = pins[num]
            except KeyError:
                pass
            else:
                if (
                        pin._bounce is None or pin._last_call is None or
                        factory.ticks_diff(ticks, pin._last_call) > pin._bounce
                ):
                    pin._call_when_changed(ticks, state)
                    pin._last_call = ticks


class NativeFactory(LocalPiFactory):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiFactory`. Uses a built-in pure
    Python implementation to interface to the Pi's GPIO pins. This is the
    default pin implementation if no third-party libraries are discovered.

    .. warning::

        This implementation does *not* currently support PWM. Attempting to
        use any class which requests PWM will raise an exception.

    You can construct native pin instances manually like so::

        from gpiozero.pins.native import NativeFactory
        from gpiozero import LED

        factory = NativeFactory()
        led = LED(12, pin_factory=factory)
    """
    def __init__(self):
        super(NativeFactory, self).__init__()
        queue = Queue()
        self.mem = GPIOMemory(self.pi_info.soc)
        self.fs = GPIOFS(self, queue)
        self.dispatch = NativeDispatchThread(self, queue)
        if self.pi_info.soc == 'BCM2711':
            self.pin_class = Native2711Pin
        else:
            self.pin_class = Native2835Pin

    def close(self):
        if self.dispatch is not None:
            self.dispatch.close()
            self.dispatch = None
        super(NativeFactory, self).close()
        if self.fs is not None:
            self.fs.close()
            self.fs = None
        if self.mem is not None:
            self.mem.close()
            self.mem = None


class NativePin(LocalPiPin):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiPin`. Native pin
    implementation. See :class:`NativeFactory` for more information.
    """
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

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}

    def __init__(self, factory, number):
        super(NativePin, self).__init__(factory, number)
        self._reg_init(factory, number)
        self._last_call = None
        self._when_changed = None
        self._change_thread = None
        self._change_event = Event()
        self.function = 'input'
        self.pull = 'up' if self.factory.pi_info.pulled_up(repr(self)) else 'floating'
        self.bounce = None
        self.edges = 'none'

    def _reg_init(self, factory, number):
        self._func_offset = self.factory.mem.GPFSEL_OFFSET + (number // 10)
        self._func_shift = (number % 10) * 3
        self._set_offset = self.factory.mem.GPSET_OFFSET + (number // 32)
        self._set_shift = number % 32
        self._clear_offset = self.factory.mem.GPCLR_OFFSET + (number // 32)
        self._clear_shift = number % 32
        self._level_offset = self.factory.mem.GPLEV_OFFSET + (number // 32)
        self._level_shift = number % 32
        self._edge_offset = self.factory.mem.GPEDS_OFFSET + (number // 32)
        self._edge_shift = number % 32
        self._rising_offset = self.factory.mem.GPREN_OFFSET + (number // 32)
        self._rising_shift = number % 32
        self._falling_offset = self.factory.mem.GPFEN_OFFSET + (number // 32)
        self._falling_shift = number % 32

    def close(self):
        self.edges = 'none'
        self.frequency = None
        self.when_changed = None
        self.function = 'input'
        self.pull = 'up' if self.factory.pi_info.pulled_up(repr(self)) else 'floating'

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[(self.factory.mem[self._func_offset] >> self._func_shift) & 7]

    def _set_function(self, value):
        try:
            value = self.GPIO_FUNCTIONS[value]
        except KeyError:
            raise PinInvalidFunction('invalid function "%s" for pin %r' % (value, self))
        self.factory.mem[self._func_offset] = (
            self.factory.mem[self._func_offset]
            & ~(7 << self._func_shift)
            | (value << self._func_shift)
            )

    def _get_state(self):
        return bool(self.factory.mem[self._level_offset] & (1 << self._level_shift))

    def _set_state(self, value):
        if self.function == 'input':
            raise PinSetInput('cannot set state of pin %r' % self)
        if value:
            self.factory.mem[self._set_offset] = 1 << self._set_shift
        else:
            self.factory.mem[self._clear_offset] = 1 << self._clear_shift

    def _get_pull(self):
        raise NotImplementedError

    def _set_pull(self, value):
        raise NotImplementedError

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        self._bounce = None if value is None else float(value)

    def _get_edges(self):
        try:
            with io.open(self.factory.fs.path_edge(self.number), 'r') as f:
                return f.read().strip()
        except IOError as e:
            if e.errno == errno.ENOENT:
                return 'none'
            else:
                raise

    def _set_edges(self, value):
        if value != 'none':
            self.factory.fs.export(self.number)
        try:
            with io.open(self.factory.fs.path_edge(self.number), 'w') as f:
                f.write(value)
        except IOError as e:
            if e.errno == errno.ENOENT and value == 'none':
                pass
            elif e.errno == errno.EINVAL:
                raise PinInvalidEdges('invalid edge specification "%s" for pin %r' % self)
            else:
                raise

    def _enable_event_detect(self):
        self.factory.fs.watch(self.number)
        self._last_call = None

    def _disable_event_detect(self):
        self.factory.fs.unwatch(self.number)


class Native2835Pin(NativePin):
    """
    Extends :class:`NativePin` for Pi hardware prior to the Pi 4 (Pi 0, 1, 2,
    3, and 3+).
    """
    GPIO_PULL_UPS = {
        'up':       0b10,
        'down':     0b01,
        'floating': 0b00,
    }

    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}

    def _reg_init(self, factory, number):
        super(Native2835Pin, self)._reg_init(factory, number)
        self._pull_offset = self.factory.mem.GPPUDCLK_OFFSET + (number // 32)
        self._pull_shift = number % 32
        self._pull = 'floating'

    def _get_pull(self):
        return self.GPIO_PULL_UP_NAMES[self._pull]

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull('cannot set pull on non-input pin %r' % self)
        if value != 'up' and self.factory.pi_info.pulled_up(repr(self)):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            value = self.GPIO_PULL_UPS[value]
        except KeyError:
            raise PinInvalidPull('invalid pull direction "%s" for pin %r' % (value, self))
        self.factory.mem[self.factory.mem.GPPUD_OFFSET] = value
        sleep(0.000000214)
        self.factory.mem[self._pull_offset] = 1 << self._pull_shift
        sleep(0.000000214)
        self.factory.mem[self.factory.mem.GPPUD_OFFSET] = 0
        self.factory.mem[self._pull_offset] = 0
        self._pull = value


class Native2711Pin(NativePin):
    """
    Extends :class:`NativePin` for Pi 4 hardware (Pi 4, CM4, Pi 400 at the time
    of writing).
    """
    GPIO_PULL_UPS = {
        'up':       0b01,
        'down':     0b10,
        'floating': 0b00,
    }

    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}

    def _reg_init(self, factory, number):
        super(Native2711Pin, self)._reg_init(factory, number)
        self._pull_offset = self.factory.mem.GPPUPPDN_OFFSET + (number // 16)
        self._pull_shift = (number % 16) * 2

    def _get_pull(self):
        pull = (self.factory.mem[self._pull_offset] >> self._pull_shift) & 3
        return self.GPIO_PULL_UP_NAMES[pull]

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull('cannot set pull on non-input pin %r' % self)
        if value != 'up' and self.factory.pi_info.pulled_up(repr(self)):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            value = self.GPIO_PULL_UPS[value]
        except KeyError:
            raise PinInvalidPull('invalid pull direction "%s" for pin %r' % (value, self))
        self.factory.mem[self._pull_offset] = (
            self.factory.mem[self._pull_offset]
            & ~(3 << self._pull_shift)
            | (value << self._pull_shift)
            )
