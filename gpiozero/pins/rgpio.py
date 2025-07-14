# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import rgpio

from . import SPI
from .pi import spi_port_device
from .local import LocalPiFactory, LocalPiPin
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

try:
    # Patch several constants which changed incompatibly between lg 0.1.6.0
    # and 0.2.0.0
    rgpio.SET_PULL_NONE
except AttributeError:
    rgpio.SET_PULL_NONE = rgpio.SET_BIAS_DISABLE
    rgpio.SET_PULL_UP = rgpio.SET_BIAS_PULL_UP
    rgpio.SET_PULL_DOWN = rgpio.SET_BIAS_PULL_DOWN


class RGPIOFactory(LocalPiFactory):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiFactory`. Uses the `rgpio`_
    library to interface to the local computer's GPIO pins. The lgpio/rgpio library
    simply talks to Linux gpiochip devices; it is not specific to the Raspberry
    Pi although this class is currently constructed under the assumption that
    it is running on a Raspberry Pi.

    You can construct rgpio pins manually like so::

        from gpiozero.pins.rgpio import RGPIOFactory
        from gpiozero import LED

        factory = RGPIOFactory(chip=0, host='localhot', port=8889)
        led = LED(12, pin_factory=factory)

    The *chip* parameter to the factory constructor specifies which gpiochip
    device to attempt to open. It defaults to 0 and thus doesn't normally need
    to be specified (the example above only includes it for completeness).

    The lgpio/rgpio library relies on access to the :file:`/dev/gpiochip*` devices.
    If you run into issues, please check that your user has read/write access
    to the specific gpiochip device you are attempting to open (0 by default).

    .. _rgpio: http://abyz.me.uk/lg/py_rgpio.html
    """
    def __init__(self, chip=None, host="localhost", port=8889):
        super().__init__()
        chip = 4 if (self._get_revision() & 0xff0) >> 4 == 0x17 else 0
        self._sbc = rgpio.sbc(host, port)
        self._handle = self._sbc.gpiochip_open(chip)
        self._chip = chip
        self.pin_class = RGPIOPin

    def close(self):
        super().close()
        if self._handle is not None:
            self._sbc.gpiochip_close(self._handle)
            self._handle = None

    @property
    def chip(self):
        return self._chip

    def _get_spi_class(self, shared, hardware):
        # support via rgpio instead of spidev
        if hardware:
            return [RGPIOHardwareSPI, RGPIOHardwareSPIShared][shared]
        return super()._get_spi_class(shared, hardware=False)


class RGPIOPin(LocalPiPin):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiPin`. Pin implementation for
    the `rgpio`_ library. See :class:`RGPIOFactory` for more information.

    .. _rgpio: http://abyz.me.uk/lg/py_rgpio.html
    """
    GPIO_IS_KERNEL         = 1 << 0
    GPIO_IS_OUT            = 1 << 1
    GPIO_IS_ACTIVE_LOW     = 1 << 2
    GPIO_IS_OPEN_DRAIN     = 1 << 3
    GPIO_IS_OPEN_SOURCE    = 1 << 4
    GPIO_IS_BIAS_PULL_UP   = 1 << 5
    GPIO_IS_BIAS_PULL_DOWN = 1 << 6
    GPIO_IS_BIAS_DISABLE   = 1 << 7
    GPIO_IS_LG_INPUT       = 1 << 8
    GPIO_IS_LG_OUTPUT      = 1 << 9
    GPIO_IS_LG_ALERT       = 1 << 10
    GPIO_IS_LG_GROUP       = 1 << 11

    GPIO_LINE_FLAGS_MASK = (
        GPIO_IS_ACTIVE_LOW | GPIO_IS_OPEN_DRAIN | GPIO_IS_OPEN_SOURCE |
        GPIO_IS_BIAS_PULL_UP | GPIO_IS_BIAS_PULL_DOWN | GPIO_IS_BIAS_DISABLE)

    GPIO_EDGES = {
        'both':    rgpio.BOTH_EDGES,
        'rising':  rgpio.RISING_EDGE,
        'falling': rgpio.FALLING_EDGE,
        }

    GPIO_EDGES_NAMES = {v: k for (k, v) in GPIO_EDGES.items()}

    def __init__(self, factory, info):
        super().__init__(factory, info)
        self._pwm = None
        self._bounce = None
        self._callback = None
        self._edges = rgpio.BOTH_EDGES
        self._sbc = factory._sbc
        self._sbc.gpio_claim_input(
            self.factory._handle, self._number, rgpio.SET_PULL_NONE)

    def close(self):
        if self.factory._handle is not None:
            # Closing is really just "resetting" the function of the pin;
            # we let the factory close deal with actually freeing stuff
            self._sbc.gpio_claim_input(
                self.factory._handle, self._number, rgpio.SET_PULL_NONE)

    def _get_function(self):
        mode = self._sbc.gpio_get_mode(self.factory._handle, self._number)
        return ['input', 'output'][bool(mode & self.GPIO_IS_OUT)]

    def _set_function(self, value):
        if self._callback is not None:
            self._callback.cancel()
            self._callback = None
        try:
            {
                'input': self._sbc.gpio_claim_input,
                'output': self._sbc.gpio_claim_output,
            }[value](self.factory._handle, self._number)
        except KeyError:
            raise PinInvalidFunction(
                f'invalid function "{value}" for pin {self!r}')

    def _get_state(self):
        if self._pwm:
            return self._pwm[1] / 100
        else:
            return bool(self._sbc.gpio_read(self.factory._handle, self._number))

    def _set_state(self, value):
        if self._pwm:
            freq, duty = self._pwm
            self._pwm = (freq, int(value * 100))
            try:
                self._sbc.tx_pwm(self.factory._handle, self._number, *self._pwm)
            except rgpio.error:
                raise PinInvalidState(
                    f'invalid state "{value}" for pin {self!r}')
        elif self.function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        else:
            self._sbc.gpio_write(self.factory._handle, self._number, bool(value))

    def _get_pull(self):
        mode = self._sbc.gpio_get_mode(self.factory._handle, self._number)
        if mode & self.GPIO_IS_BIAS_PULL_UP:
            return 'up'
        elif mode & self.GPIO_IS_BIAS_PULL_DOWN:
            return 'down'
        else:
            return 'floating'

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull(f'cannot set pull on non-input pin {self!r}')
        if self.info.pull not in (value, ''):
            raise PinFixedPull(
                f'{self!r} has a physical pull-{self.info.pull} resistor')
        try:
            flags = {
                'up': rgpio.SET_PULL_UP,
                'down': rgpio.SET_PULL_DOWN,
                'floating': rgpio.SET_PULL_NONE,
            }[value]
        except KeyError:
            raise PinInvalidPull(f'invalid pull "{value}" for pin {self!r}')
        else:
            # Simply calling gpio_claim_input is insufficient to change the
            # line flags on a pin; it needs to be freed and re-claimed
            self._sbc.gpio_free(self.factory._handle, self._number)
            self._sbc.gpio_claim_input(self.factory._handle, self._number, flags)

    def _get_frequency(self):
        if self._pwm:
            freq, duty = self._pwm
            return freq
        else:
            return None

    def _set_frequency(self, value):
        if not self._pwm and value is not None and value > 0:
            if self.function != 'output':
                raise PinPWMFixedValue(f'cannot start PWM on pin {self!r}')
            self._sbc.tx_pwm(self.factory._handle, self._number, value, 0)
            self._pwm = (value, 0)
        elif self._pwm and value is not None and value > 0:
            freq, duty = self._pwm
            self._sbc.tx_pwm(self.factory._handle, self._number, value, duty)
            self._pwm = (value, duty)
        elif self._pwm and (value is None or value == 0):
            self._sbc.tx_pwm(self.factory._handle, self._number, 0, 0)
            self._pwm = None

    def _get_bounce(self):
        return None if not self._bounce else self._bounce / 1000000

    def _set_bounce(self, value):
        if value is None:
            value = 0
        elif value < 0:
            raise PinInvalidBounce('bounce must be 0 or greater')
        value = int(value * 1000000)
        self._sbc.gpio_set_debounce_micros(
            self.factory._handle, self._number, value)
        self._bounce = value

    def _get_edges(self):
        return self.GPIO_EDGES_NAMES[self._edges]

    def _set_edges(self, value):
        f = self.when_changed
        self.when_changed = None
        try:
            self._edges = self.GPIO_EDGES[value]
        finally:
            self.when_changed = f

    def _call_when_changed(self, chip, gpio, level, ticks):
        super()._call_when_changed(ticks / 1000000000, level)

    def _enable_event_detect(self):
        self._sbc.gpio_claim_alert(
            self.factory._handle, self._number, self._edges,
            self._sbc.gpio_get_mode(self.factory._handle, self._number) &
            self.GPIO_LINE_FLAGS_MASK)
        self._callback = self._sbc.callback(
            self.factory._handle, self._number, self._edges,
            self._call_when_changed)

    def _disable_event_detect(self):
        if self._callback is not None:
            self._callback.cancel()
            self._callback = None
        self._sbc.gpio_claim_input(
            self.factory._handle, self._number,
            self._sbc.gpio_get_mode(self.factory._handle, self._number) &
            self.GPIO_LINE_FLAGS_MASK)


class RGPIOHardwareSPI(SPI):
    """
    Hardware SPI implementation for the `rgpio`_ library. Uses the ``spi_*``
    functions from the rgpio API.

    .. _rgpio: http://abyz.me.uk/lg/py_rgpio.html
    """
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        port, device = spi_port_device(
            clock_pin, mosi_pin, miso_pin, select_pin)
        self._port = port
        self._device = device
        self._baud = 500000
        self._spi_flags = 0
        self._handle = None
        super().__init__(pin_factory=pin_factory)
        to_reserve = {clock_pin, select_pin}
        if mosi_pin is not None:
            to_reserve.add(mosi_pin)
        if miso_pin is not None:
            to_reserve.add(miso_pin)
        self.pin_factory.reserve_pins(self, *to_reserve)
        self._sbc = pin_factory._sbc
        self._handle = self._sbc.spi_open(port, device, self._baud, self._spi_flags)

    def _conflicts_with(self, other):
        return not (
            isinstance(other, RGPIOHardwareSPI) and
            (self._port, self._device) != (other._port, other._device)
            )

    def close(self):
        if not self.closed:
            self._sbc.spi_close(self._handle)
        self._handle = None
        self.pin_factory.release_all(self)
        super().close()

    @property
    def closed(self):
        return self._handle is None

    def __repr__(self):
        try:
            self._check_open()
            return f'SPI(port={self._port:d}, device={self._device:d})'
        except DeviceClosed:
            return 'SPI(closed)'

    def _get_clock_mode(self):
        return self._spi_flags

    def _set_clock_mode(self, value):
        self._check_open()
        if not 0 <= value < 4:
            raise SPIInvalidClockMode(f"{value} is not a valid SPI clock mode")
        self._sbc.spi_close(self._handle)
        self._spi_flags = value
        self._handle = self._sbc.spi_open(
            self._port, self._device, self._baud, self._spi_flags)

    def _get_rate(self):
        return self._baud

    def _set_rate(self, value):
        self._check_open()
        value = int(value)
        self._sbc.spi_close(self._handle)
        self._baud = value
        self._handle = self._sbc.spi_open(
            self._port, self._device, self._baud, self._spi_flags)

    def read(self, n):
        self._check_open()
        count, data = self._sbc.spi_read(self._handle, n)
        if count < 0:
            raise IOError(f'SPI transfer error {count}')
        return [int(b) for b in data]

    def write(self, data):
        self._check_open()
        count = self._sbc.spi_write(self._handle, data)
        if count < 0:
            raise IOError(f'SPI transfer error {count}')
        return len(data)

    def transfer(self, data):
        self._check_open()
        count, data = self._sbc.spi_xfer(self._handle, data)
        if count < 0:
            raise IOError(f'SPI transfer error {count}')
        return [int(b) for b in data]


class RGPIOHardwareSPIShared(SharedMixin, RGPIOHardwareSPI):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        return (clock_pin, select_pin)
