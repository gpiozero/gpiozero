# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2021 Kyle Morgan <kyle@knmorgan.net>
# Copyright (c) 2020 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2019 Maksim Levental <maksim.levental@gmail.com>
# Copyright (c) 2019 Aaron Rogers <aaron.kyle.rogers@gmail.com>
# Copyright (c) 2016 BuildTools <david.glaude@gmail.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import pigpio

from . import SPI
from .pi import PiPin, PiFactory, spi_port_device
from ..mixins import SharedMixin
from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    PinInvalidPull,
    PinInvalidBounce,
    PinInvalidState,
    SPIBadArgs,
    SPIInvalidClockMode,
    PinPWMFixedValue,
    DeviceClosed
)


class PiGPIOFactory(PiFactory):
    """
    Extends :class:`~gpiozero.pins.pi.PiFactory`. Uses the `pigpio`_ library to
    interface to the Pi's GPIO pins. The pigpio library relies on a daemon
    (:command:`pigpiod`) to be running as root to provide access to the GPIO
    pins, and communicates with this daemon over a network socket.

    While this does mean only the daemon itself should control the pins, the
    architecture does have several advantages:

    * Pins can be remote controlled from another machine (the other
      machine doesn't even have to be a Raspberry Pi; it simply needs the
      `pigpio`_ client library installed on it)
    * The daemon supports hardware PWM via the DMA controller
    * Your script itself doesn't require root privileges; it just needs to
      be able to communicate with the daemon

    You can construct pigpio pins manually like so::

        from gpiozero.pins.pigpio import PiGPIOFactory
        from gpiozero import LED

        factory = PiGPIOFactory()
        led = LED(12, pin_factory=factory)

    This is particularly useful for controlling pins on a remote machine. To
    accomplish this simply specify the host (and optionally port) when
    constructing the pin::

        from gpiozero.pins.pigpio import PiGPIOFactory
        from gpiozero import LED

        factory = PiGPIOFactory(host='192.168.0.2')
        led = LED(12, pin_factory=factory)

    .. note::

        In some circumstances, especially when playing with PWM, it does appear
        to be possible to get the daemon into "unusual" states. We would be
        most interested to hear any bug reports relating to this (it may be a
        bug in our pin implementation). A workaround for now is simply to
        restart the :command:`pigpiod` daemon.

    .. _pigpio: http://abyz.me.uk/rpi/pigpio/
    """
    def __init__(self, host=None, port=None):
        super().__init__()
        if host is None:
            host = os.environ.get('PIGPIO_ADDR', 'localhost')
        if port is None:
            # XXX Use getservbyname
            port = int(os.environ.get('PIGPIO_PORT', 8888))
        self.pin_class = PiGPIOPin
        self._connection = pigpio.pi(host, port)
        # Annoyingly, pigpio doesn't raise an exception when it fails to make a
        # connection; it returns a valid (but disconnected) pi object
        if self.connection is None:
            raise IOError(f'failed to connect to {host}:{port}')
        self._host = host
        self._port = port
        self._spis = []

    def close(self):
        super().close()
        # We *have* to keep track of SPI interfaces constructed with pigpio;
        # if we fail to close them they prevent future interfaces from using
        # the same pins
        if self.connection:
            while self._spis:
                self._spis[0].close()
            self.connection.stop()
            self._connection = None

    @property
    def connection(self):
        # If we're shutting down, the connection may have disconnected itself
        # already. Unfortunately, the connection's "connected" property is
        # rather buggy - disconnecting doesn't set it to False! So we're
        # naughty and check an internal variable instead...
        try:
            if self._connection.sl.s is not None:
                return self._connection
        except AttributeError:
            pass

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def _get_revision(self):
        return self.connection.get_hardware_revision()

    def _get_spi_class(self, shared, hardware):
        return {
            (False, True):  PiGPIOHardwareSPI,
            (True,  True):  PiGPIOHardwareSPIShared,
            (False, False): PiGPIOSoftwareSPI,
            (True,  False): PiGPIOSoftwareSPIShared,
            }[shared, hardware]

    def spi(self, **spi_args):
        intf = super().spi(**spi_args)
        self._spis.append(intf)
        return intf

    def ticks(self):
        return self._connection.get_current_tick()

    @staticmethod
    def ticks_diff(later, earlier):
        # NOTE: pigpio ticks are unsigned 32-bit quantities that wrap every
        # 71.6 minutes. The modulo below (oh the joys of having an *actual*
        # modulo operator, unlike C's remainder) ensures the result is valid
        # even when later < earlier due to wrap-around (assuming the duration
        # measured is not longer than the period)
        return ((later - earlier) % 0x100000000) / 1000000


class PiGPIOPin(PiPin):
    """
    Extends :class:`~gpiozero.pins.pi.PiPin`. Pin implementation for the
    `pigpio`_ library. See :class:`PiGPIOFactory` for more information.

    .. _pigpio: http://abyz.me.uk/rpi/pigpio/
    """
    GPIO_FUNCTIONS = {
        'input':   pigpio.INPUT,
        'output':  pigpio.OUTPUT,
        'alt0':    pigpio.ALT0,
        'alt1':    pigpio.ALT1,
        'alt2':    pigpio.ALT2,
        'alt3':    pigpio.ALT3,
        'alt4':    pigpio.ALT4,
        'alt5':    pigpio.ALT5,
        }

    GPIO_PULL_UPS = {
        'up':       pigpio.PUD_UP,
        'down':     pigpio.PUD_DOWN,
        'floating': pigpio.PUD_OFF,
        }

    GPIO_EDGES = {
        'both':    pigpio.EITHER_EDGE,
        'rising':  pigpio.RISING_EDGE,
        'falling': pigpio.FALLING_EDGE,
        }

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}
    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}
    GPIO_EDGES_NAMES = {v: k for (k, v) in GPIO_EDGES.items()}

    def __init__(self, factory, info):
        super().__init__(factory, info)
        self._pull = info.pull or 'floating'
        self._pwm = False
        self._bounce = None
        self._callback = None
        self._edges = pigpio.EITHER_EDGE
        try:
            self.factory.connection.set_mode(self._number, pigpio.INPUT)
        except pigpio.error as e:
            raise ValueError(e)
        self.factory.connection.set_pull_up_down(
            self._number, self.GPIO_PULL_UPS[self._pull])
        self.factory.connection.set_glitch_filter(self._number, 0)

    def close(self):
        if self.factory.connection:
            self.frequency = None
            self.when_changed = None
            self.function = 'input'
            self.pull = self.info.pull or 'floating'

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[
            self.factory.connection.get_mode(self._number)]

    def _set_function(self, value):
        if value != 'input':
            self._pull = 'floating'
        try:
            self.factory.connection.set_mode(
                self._number, self.GPIO_FUNCTIONS[value])
        except KeyError:
            raise PinInvalidFunction(
                f'invalid function "{value}" for pin {self!r}')

    def _get_state(self):
        if self._pwm:
            return (
                self.factory.connection.get_PWM_dutycycle(self._number) /
                self.factory.connection.get_PWM_range(self._number)
                )
        else:
            return bool(self.factory.connection.read(self._number))

    def _set_state(self, value):
        if self._pwm:
            try:
                value = int(value * self.factory.connection.get_PWM_range(self._number))
                if value != self.factory.connection.get_PWM_dutycycle(self._number):
                    self.factory.connection.set_PWM_dutycycle(self._number, value)
            except pigpio.error:
                raise PinInvalidState(
                    f'invalid state "{value}" for pin {self!r}')
        elif self.function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        else:
            # write forces pin to OUTPUT, hence the check above
            self.factory.connection.write(self._number, bool(value))

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull(f'cannot set pull on non-input pin {self!r}')
        if self.info.pull and value != self.info.pull:
            raise PinFixedPull(f'{self!r} has a fixed pull resistor')
        try:
            self.factory.connection.set_pull_up_down(
                self._number, self.GPIO_PULL_UPS[value])
            self._pull = value
        except KeyError:
            raise PinInvalidPull(f'invalid pull "{value}" for pin {self!r}')

    def _get_frequency(self):
        if self._pwm:
            return self.factory.connection.get_PWM_frequency(self._number)
        return None

    def _set_frequency(self, value):
        if not self._pwm and value is not None:
            if self.function != 'output':
                raise PinPWMFixedValue(f'cannot start PWM on pin {self!r}')
            # NOTE: the pin's state *must* be set to zero; if it's currently
            # high, starting PWM and setting a 0 duty-cycle *doesn't* bring
            # the pin low; it stays high!
            self.factory.connection.write(self._number, 0)
            self.factory.connection.set_PWM_frequency(self._number, int(value))
            self.factory.connection.set_PWM_range(self._number, 10000)
            self.factory.connection.set_PWM_dutycycle(self._number, 0)
            self._pwm = True
        elif self._pwm and value is not None:
            if value != self.factory.connection.get_PWM_frequency(self._number):
                self.factory.connection.set_PWM_frequency(self._number, int(value))
                self.factory.connection.set_PWM_range(self._number, 10000)
        elif self._pwm and value is None:
            self.factory.connection.write(self._number, 0)
            self._pwm = False

    def _get_bounce(self):
        return None if not self._bounce else self._bounce / 1000000

    def _set_bounce(self, value):
        if value is None:
            value = 0
        elif not 0 <= value <= 0.3:
            raise PinInvalidBounce('bounce must be between 0 and 0.3')
        self.factory.connection.set_glitch_filter(
            self._number, int(value * 1000000))

    def _get_edges(self):
        return self.GPIO_EDGES_NAMES[self._edges]

    def _set_edges(self, value):
        f = self.when_changed
        self.when_changed = None
        try:
            self._edges = self.GPIO_EDGES[value]
        finally:
            self.when_changed = f

    def _call_when_changed(self, gpio, level, ticks):
        super()._call_when_changed(ticks, level)

    def _enable_event_detect(self):
        self._callback = self.factory.connection.callback(
                self._number, self._edges, self._call_when_changed)

    def _disable_event_detect(self):
        if self._callback is not None:
            self._callback.cancel()
            self._callback = None


class PiGPIOHardwareSPI(SPI):
    """
    Hardware SPI implementation for the `pigpio`_ library. Uses the ``spi_*``
    functions from the pigpio API.

    .. _pigpio: http://abyz.me.uk/rpi/pigpio/
    """
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        port, device = spi_port_device(
            clock_pin, mosi_pin, miso_pin, select_pin)
        self._port = port
        self._device = device
        self._handle = None
        super().__init__(pin_factory=pin_factory)
        to_reserve = {clock_pin, select_pin}
        if mosi_pin is not None:
            to_reserve.add(mosi_pin)
        if miso_pin is not None:
            to_reserve.add(miso_pin)
        self.pin_factory.reserve_pins(self, *to_reserve)
        self._spi_flags = (8 << 16) | (port << 8)
        self._baud = 500000
        self._handle = self.pin_factory.connection.spi_open(
            device, self._baud, self._spi_flags)

    def _conflicts_with(self, other):
        return not (
            isinstance(other, PiGPIOHardwareSPI) and
            (self.pin_factory.host, self._port, self._device) !=
            (other.pin_factory.host, other._port, other._device)
            )

    def close(self):
        try:
            self.pin_factory._spis.remove(self)
        except (ReferenceError, ValueError):
            # If the factory has died already or we're not present in its
            # internal list, ignore the error
            pass
        if not self.closed:
            self.pin_factory.connection.spi_close(self._handle)
        self._handle = None
        self.pin_factory.release_all(self)
        super().close()

    @property
    def closed(self):
        return self._handle is None or self.pin_factory.connection is None

    def __repr__(self):
        try:
            self._check_open()
            return f'SPI(port={self._port:d}, device={self._device:d})'
        except DeviceClosed:
            return 'SPI(closed)'

    def _get_clock_mode(self):
        return self._spi_flags & 0x3

    def _set_clock_mode(self, value):
        self._check_open()
        if not 0 <= value < 4:
            raise SPIInvalidClockMode(f"{value} is not a valid SPI clock mode")
        self.pin_factory.connection.spi_close(self._handle)
        self._spi_flags = (self._spi_flags & ~0x3) | value
        self._handle = self.pin_factory.connection.spi_open(
            self._device, self._baud, self._spi_flags)

    def _get_select_high(self):
        return bool((self._spi_flags >> (2 + self._device)) & 0x1)

    def _set_select_high(self, value):
        self._check_open()
        self.pin_factory.connection.spi_close(self._handle)
        self._spi_flags = (self._spi_flags & ~0x1c) | (bool(value) << (2 + self._device))
        self._handle = self.pin_factory.connection.spi_open(
            self._device, self._baud, self._spi_flags)

    def _get_bits_per_word(self):
        return (self._spi_flags >> 16) & 0x3f

    def _set_bits_per_word(self, value):
        self._check_open()
        self.pin_factory.connection.spi_close(self._handle)
        self._spi_flags = (self._spi_flags & ~0x3f0000) | ((value & 0x3f) << 16)
        self._handle = self.pin_factory.connection.spi_open(
            self._device, self._baud, self._spi_flags)

    def _get_rate(self):
        return self._baud

    def _set_rate(self, value):
        self._check_open()
        value = int(value)
        self.pin_factory.connection.spi_close(self._handle)
        self._baud = value
        self._handle = self.pin_factory.connection.spi_open(
            self._device, self._baud, self._spi_flags)

    def _get_lsb_first(self):
        return bool((self._spi_flags >> 14) & 0x1) if self._port else False

    def _set_lsb_first(self, value):
        if self._port:
            self._check_open()
            self.pin_factory.connection.spi_close(self._handle)
            self._spi_flags = (
                (self._spi_flags & ~0xc000)
                | (bool(value) << 14)
                | (bool(value) << 15)
                )
            self._handle = self.pin_factory.connection.spi_open(
                self._device, self._baud, self._spi_flags)
        else:
            super()._set_lsb_first(value)

    def transfer(self, data):
        self._check_open()
        count, data = self.pin_factory.connection.spi_xfer(self._handle, data)
        if count < 0:
            raise IOError(f'SPI transfer error {count}')
        # Convert returned bytearray to list of ints.
        # XXX Not sure how non-byte sized words (aux intf only) are returned
        # ... padded to 16/32-bits?
        return [int(b) for b in data]


class PiGPIOSoftwareSPI(SPI):
    """
    Software SPI implementation for the `pigpio`_ library. Uses the ``bb_spi_*``
    functions from the pigpio API.

    .. _pigpio: http://abyz.me.uk/rpi/pigpio/
    """
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        self._closed = True
        self._select_pin = select_pin
        self._clock_pin = clock_pin
        self._mosi_pin = mosi_pin
        self._miso_pin = miso_pin
        super().__init__(pin_factory=pin_factory)
        # Can't "unreserve" MOSI/MISO on this implementation
        self.pin_factory.reserve_pins(
            self,
            clock_pin,
            mosi_pin,
            miso_pin,
            select_pin,
            )
        self._spi_flags = 0
        self._baud = 100000
        try:
            self.pin_factory.connection.bb_spi_open(
                select_pin, miso_pin, mosi_pin, clock_pin,
                self._baud, self._spi_flags)
            # Only set after opening bb_spi; if that fails then close() will
            # also fail if bb_spi_close is attempted on an un-open interface
            self._closed = False
        except:
            self.close()
            raise

    def _conflicts_with(self, other):
        return not (
            isinstance(other, PiGPIOSoftwareSPI) and
            (self._select_pin) != (other._select_pin)
            )

    def close(self):
        try:
            self.pin_factory._spis.remove(self)
        except (ReferenceError, ValueError):
            # If the factory has died already or we're not present in its
            # internal list, ignore the error
            pass
        if not self._closed and self.pin_factory.connection:
            self._closed = True
            self.pin_factory.connection.bb_spi_close(self._select_pin)
        self.pin_factory.release_all(self)
        super().close()

    @property
    def closed(self):
        return self._closed

    def __repr__(self):
        try:
            self._check_open()
            return (
                f'SPI(clock_pin={self._clock_pin}, mosi_pin={self._mosi_pin}, '
                f'miso_pin={self._miso_pin}, select_pin={self._select_pin})')
        except DeviceClosed:
            return 'SPI(closed)'

    def _spi_flags(self):
        return (
            self._mode          << 0  |
            self._select_high   << 2  |
            self._lsb_first     << 14 |
            self._lsb_first     << 15
            )

    def _get_clock_mode(self):
        return self._spi_flags & 0x3

    def _set_clock_mode(self, value):
        self._check_open()
        if not 0 <= value < 4:
            raise SPIInvalidClockMode(f"{value} is not a valid SPI clock mode")
        self.pin_factory.connection.bb_spi_close(self._select_pin)
        self._spi_flags = (self._spi_flags & ~0x3) | value
        self.pin_factory.connection.bb_spi_open(
            self._select_pin, self._miso_pin, self._mosi_pin, self._clock_pin,
            self._baud, self._spi_flags)

    def _get_select_high(self):
        return bool(self._spi_flags & 0x4)

    def _set_select_high(self, value):
        self._check_open()
        self.pin_factory.connection.bb_spi_close(self._select_pin)
        self._spi_flags = (self._spi_flags & ~0x4) | (bool(value) << 2)
        self.pin_factory.connection.bb_spi_open(
            self._select_pin, self._miso_pin, self._mosi_pin, self._clock_pin,
            self._baud, self._spi_flags)

    def _get_lsb_first(self):
        return bool(self._spi_flags & 0xc000)

    def _set_lsb_first(self, value):
        self._check_open()
        self.pin_factory.connection.bb_spi_close(self._select_pin)
        self._spi_flags = (
            (self._spi_flags & ~0xc000)
            | (bool(value) << 14)
            | (bool(value) << 15)
            )
        self.pin_factory.connection.bb_spi_open(
            self._select_pin, self._miso_pin, self._mosi_pin, self._clock_pin,
            self._baud, self._spi_flags)

    def _get_rate(self):
        return self._baud

    def _set_rate(self, value):
        self._check_open()
        value = int(value)
        self.pin_factory.connection.bb_spi_close(self._select_pin)
        self._baud = value
        self.pin_factory.connection.bb_spi_open(
            self._select_pin, self._miso_pin, self._mosi_pin, self._clock_pin,
            self._baud, self._spi_flags)

    def transfer(self, data):
        self._check_open()
        count, data = self.pin_factory.connection.bb_spi_xfer(
            self._select_pin, data)
        if count < 0:
            raise IOError(f'SPI transfer error {count}')
        # Convert returned bytearray to list of ints. bb_spi only supports
        # byte-sized words so no issues here
        return [int(b) for b in data]


class PiGPIOHardwareSPIShared(SharedMixin, PiGPIOHardwareSPI):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        return (pin_factory.host, clock_pin, select_pin)


class PiGPIOSoftwareSPIShared(SharedMixin, PiGPIOSoftwareSPI):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        return (pin_factory.host, clock_pin, select_pin)
