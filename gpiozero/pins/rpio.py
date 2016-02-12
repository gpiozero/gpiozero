from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from threading import Lock

import RPIO
import RPIO.PWM

from . import Pin, PINS_CLEANUP
from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    )


class RPIOPin(Pin):
    """
    Uses the `RPIO`_ library to interface to the Pi's GPIO pins. This is
    the default pin implementation if the RPi.GPIO library is not installed,
    but RPIO is. Supports all features including PWM (hardware via DMA).

    .. note::

        Please note that at the time of writing, RPIO is only compatible with
        Pi 1's; the Raspberry Pi 2 Model B is *not* supported. Also note that
        root access is required so scripts must typically be run with ``sudo``.

    You can construct RPIO pins manually like so::

        from gpiozero.pins.rpio import RPIOPin
        from gpiozero import LED

        led = LED(RPIOPin(12))

    .. _RPIO: https://pythonhosted.org/RPIO/
    """

    _PINS = {}

    GPIO_FUNCTIONS = {
        'input':   RPIO.IN,
        'output':  RPIO.OUT,
        'alt0':    RPIO.ALT0,
        }

    GPIO_PULL_UPS = {
        'up':       RPIO.PUD_UP,
        'down':     RPIO.PUD_DOWN,
        'floating': RPIO.PUD_OFF,
        }

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}
    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}

    def __new__(cls, number):
        if not cls._PINS:
            RPIO.setmode(RPIO.BCM)
            RPIO.setwarnings(False)
            RPIO.wait_for_interrupts(threaded=True)
            RPIO.PWM.setup()
            RPIO.PWM.init_channel(0, 10000)
            PINS_CLEANUP.append(RPIO.PWM.cleanup)
            PINS_CLEANUP.append(RPIO.stop_waiting_for_interrupts)
            PINS_CLEANUP.append(RPIO.cleanup)
        try:
            return cls._PINS[number]
        except KeyError:
            self = super(RPIOPin, cls).__new__(cls)
            cls._PINS[number] = self
            self._number = number
            self._pull = 'up' if number in (2, 3) else 'floating'
            self._pwm = False
            self._duty_cycle = None
            self._bounce = None
            self._when_changed = None
            self._edges = 'both'
            RPIO.setup(self._number, RPIO.IN, self.GPIO_PULL_UPS[self._pull])
            return self

    def __repr__(self):
        return "GPIO%d" % self._number

    @property
    def number(self):
        return self._number

    def close(self):
        self.frequency = None
        self.when_changed = None
        RPIO.setup(self._number, RPIO.IN, RPIO.PUD_OFF)

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[RPIO.gpio_function(self._number)]

    def _set_function(self, value):
        if value != 'input':
            self._pull = 'floating'
        try:
            RPIO.setup(self._number, self.GPIO_FUNCTIONS[value], self.GPIO_PULL_UPS[self._pull])
        except KeyError:
            raise PinInvalidFunction('invalid function "%s" for pin %r' % (value, self))

    def _get_state(self):
        if self._pwm:
            return self._duty_cycle
        else:
            return RPIO.input(self._number)

    def _set_state(self, value):
        if not 0 <= value <= 1:
            raise PinInvalidValue('invalid state "%s" for pin %r' % (value, self))
        if self._pwm:
            RPIO.PWM.clear_channel_gpio(0, self._number)
            if value == 0:
                RPIO.output(self._number, False)
            elif value == 1:
                RPIO.output(self._number, True)
            else:
                RPIO.PWM.add_channel_pulse(0, self._number, start=0, width=int(1000 * value))
            self._duty_cycle = value
        else:
            try:
                RPIO.output(self._number, value)
            except ValueError:
                raise PinInvalidState('invalid state "%s" for pin %r' % (value, self))
            except RuntimeError:
                raise PinSetInput('cannot set state of pin %r' % self)

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull('cannot set pull on non-input pin %r' % self)
        if value != 'up' and self._number in (2, 3):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            RPIO.setup(self._number, RPIO.IN, self.GPIO_PULL_UPS[value])
            self._pull = value
        except KeyError:
            raise PinInvalidPull('invalid pull "%s" for pin %r' % (value, self))

    def _get_frequency(self):
        return 100

    def _set_frequency(self, value):
        if value is not None and value != 100:
            raise PinPWMError(
                'RPIOPin implementation is currently limited to '
                '100Hz sub-cycles')
        if not self._pwm and value is not None:
            self._pwm = True
            # Dirty hack to get RPIO's PWM support to setup, but do nothing,
            # for a given GPIO pin
            RPIO.PWM.add_channel_pulse(0, self._number, start=0, width=0)
            RPIO.PWM.clear_channel_gpio(0, self._number)
        elif self._pwm and value is None:
            RPIO.PWM.clear_channel_gpio(0, self._number)
            self._pwm = False

    def _get_bounce(self):
        return None if self._bounce is None else (self._bounce / 1000)

    def _set_bounce(self, value):
        f = self.when_changed
        self.when_changed = None
        try:
            self._bounce = None if value is None else (value * 1000)
        finally:
            self.when_changed = f

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        f = self.when_changed
        self.when_changed = None
        try:
            self._edges = value
        finally:
            self.when_changed = f

    def _get_when_changed(self):
        return self._when_changed

    def _set_when_changed(self, value):
        if self._when_changed is None and value is not None:
            self._when_changed = value
            RPIO.add_interrupt_callback(
                self._number,
                lambda channel, value: self._when_changed(),
                self._edges, self.GPIO_PULL_UPS[self._pull], self._bounce)
        elif self._when_changed is not None and value is None:
            try:
                RPIO.del_interrupt_callback(self._number)
            except KeyError:
                # Ignore this exception which occurs during shutdown; this
                # simply means RPIO's built-in cleanup has already run and
                # removed the handler
                pass
            self._when_changed = None
        else:
            self._when_changed = value

