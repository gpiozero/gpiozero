# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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


class GPIOMemory(object):

    GPIO_BASE_OFFSET = 0x200000
    PERI_BASE_OFFSET = {
        'BCM2835': 0x20000000,
        'BCM2836': 0x3f000000,
        'BCM2837': 0x3f000000,
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
                offset = self.peripheral_base(soc) + self.GPIO_BASE_OFFSET
        else:
            offset = 0
        self.mem = mmap.mmap(self.fd, 4096, offset=offset)

    def close(self):
        self.mem.close()
        os.close(self.fd)

    def peripheral_base(self, soc):
        try:
            with io.open('/proc/device-tree/soc/ranges', 'rb') as f:
                f.seek(4)
                # This is deliberately a big-endian read
                return struct.unpack(nstr('>L'), f.read(4))[0]
        except IOError:
            try:
                return self.PERI_BASE_OFFSET[soc]
            except KeyError:
                pass
        raise IOError('unable to determine peripheral base')

    def __getitem__(self, index):
        return struct.unpack_from(nstr('<L'), self.mem, index * 4)[0]

    def __setitem__(self, index, value):
        struct.pack_into(nstr('<L'), self.mem, index * 4, value)


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
                            with io.open(self.path('export'), 'w+b') as f:
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
                    with io.open(self.path('unexport'), 'w+b') as f:
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
        self.pin_class = NativePin

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

    GPIO_PULL_UPS = {
        'up':       0b10,
        'down':     0b01,
        'floating': 0b00,
        'reserved': 0b11,
        }

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}
    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}

    def __init__(self, factory, number):
        super(NativePin, self).__init__(factory, number)
        self._func_offset = self.factory.mem.GPFSEL_OFFSET + (number // 10)
        self._func_shift = (number % 10) * 3
        self._set_offset = self.factory.mem.GPSET_OFFSET + (number // 32)
        self._set_shift = number % 32
        self._clear_offset = self.factory.mem.GPCLR_OFFSET + (number // 32)
        self._clear_shift = number % 32
        self._level_offset = self.factory.mem.GPLEV_OFFSET + (number // 32)
        self._level_shift = number % 32
        self._pull_offset = self.factory.mem.GPPUDCLK_OFFSET + (number // 32)
        self._pull_shift = number % 32
        self._edge_offset = self.factory.mem.GPEDS_OFFSET + (number // 32)
        self._edge_shift = number % 32
        self._rising_offset = self.factory.mem.GPREN_OFFSET + (number // 32)
        self._rising_shift = number % 32
        self._falling_offset = self.factory.mem.GPFEN_OFFSET + (number // 32)
        self._falling_shift = number % 32
        self._last_call = None
        self._when_changed = None
        self._change_thread = None
        self._change_event = Event()
        self.function = 'input'
        self._pull = 'floating'
        self.pull = 'up' if self.factory.pi_info.pulled_up(repr(self)) else 'floating'
        self.bounce = None
        self.edges = 'none'

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
