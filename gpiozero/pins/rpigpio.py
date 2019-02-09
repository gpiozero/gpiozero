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
str = type('')

import warnings

from RPi import GPIO

from .local import LocalPiFactory, LocalPiPin
from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    PinInvalidPull,
    PinInvalidState,
    PinInvalidBounce,
    PinPWMFixedValue,
    )


class RPiGPIOFactory(LocalPiFactory):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiFactory`. Uses the `RPi.GPIO`_
    library to interface to the Pi's GPIO pins. This is the default pin
    implementation if the RPi.GPIO library is installed. Supports all features
    including PWM (via software).

    Because this is the default pin implementation you can use it simply by
    specifying an integer number for the pin in most operations, e.g.::

        from gpiozero import LED

        led = LED(12)

    However, you can also construct RPi.GPIO pins manually if you wish::

        from gpiozero.pins.rpigpio import RPiGPIOFactory
        from gpiozero import LED

        factory = RPiGPIOFactory()
        led = LED(12, pin_factory=factory)

    .. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO
    """

    def __init__(self):
        super(RPiGPIOFactory, self).__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.pin_class = RPiGPIOPin

    def close(self):
        super(RPiGPIOFactory, self).close()
        GPIO.cleanup()


class RPiGPIOPin(LocalPiPin):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiPin`. Pin implementation for
    the `RPi.GPIO`_ library. See :class:`RPiGPIOFactory` for more information.

    .. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO
    """
    GPIO_FUNCTIONS = {
        'input':   GPIO.IN,
        'output':  GPIO.OUT,
        'i2c':     GPIO.I2C,
        'spi':     GPIO.SPI,
        'pwm':     GPIO.HARD_PWM,
        'serial':  GPIO.SERIAL,
        'unknown': GPIO.UNKNOWN,
        }

    GPIO_PULL_UPS = {
        'up':       GPIO.PUD_UP,
        'down':     GPIO.PUD_DOWN,
        'floating': GPIO.PUD_OFF,
        }

    GPIO_EDGES = {
        'both':    GPIO.BOTH,
        'rising':  GPIO.RISING,
        'falling': GPIO.FALLING,
        }

    GPIO_FUNCTION_NAMES = {v: k for (k, v) in GPIO_FUNCTIONS.items()}
    GPIO_PULL_UP_NAMES = {v: k for (k, v) in GPIO_PULL_UPS.items()}
    GPIO_EDGES_NAMES = {v: k for (k, v) in GPIO_EDGES.items()}

    def __init__(self, factory, number):
        super(RPiGPIOPin, self).__init__(factory, number)
        self._pull = 'up' if self.factory.pi_info.pulled_up(repr(self)) else 'floating'
        self._pwm = None
        self._frequency = None
        self._duty_cycle = None
        self._bounce = -666
        self._edges = GPIO.BOTH
        GPIO.setup(self.number, GPIO.IN, self.GPIO_PULL_UPS[self._pull])

    def close(self):
        self.frequency = None
        self.when_changed = None
        GPIO.cleanup(self.number)

    def output_with_state(self, state):
        self._pull = 'floating'
        GPIO.setup(self.number, GPIO.OUT, initial=state)

    def input_with_pull(self, pull):
        if pull != 'up' and self.factory.pi_info.pulled_up(repr(self)):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            GPIO.setup(self.number, GPIO.IN, self.GPIO_PULL_UPS[pull])
            self._pull = pull
        except KeyError:
            raise PinInvalidPull('invalid pull "%s" for pin %r' % (pull, self))

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[GPIO.gpio_function(self.number)]

    def _set_function(self, value):
        if value != 'input':
            self._pull = 'floating'
        if value in ('input', 'output') and value in self.GPIO_FUNCTIONS:
            GPIO.setup(self.number, self.GPIO_FUNCTIONS[value], self.GPIO_PULL_UPS[self._pull])
        else:
            raise PinInvalidFunction('invalid function "%s" for pin %r' % (value, self))

    def _get_state(self):
        if self._pwm:
            return self._duty_cycle
        else:
            return GPIO.input(self.number)

    def _set_state(self, value):
        if self._pwm:
            try:
                self._pwm.ChangeDutyCycle(value * 100)
            except ValueError:
                raise PinInvalidState('invalid state "%s" for pin %r' % (value, self))
            self._duty_cycle = value
        else:
            try:
                GPIO.output(self.number, value)
            except ValueError:
                raise PinInvalidState('invalid state "%s" for pin %r' % (value, self))
            except RuntimeError:
                raise PinSetInput('cannot set state of pin %r' % self)

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull('cannot set pull on non-input pin %r' % self)
        if value != 'up' and self.factory.pi_info.pulled_up(repr(self)):
            raise PinFixedPull('%r has a physical pull-up resistor' % self)
        try:
            GPIO.setup(self.number, GPIO.IN, self.GPIO_PULL_UPS[value])
            self._pull = value
        except KeyError:
            raise PinInvalidPull('invalid pull "%s" for pin %r' % (value, self))

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, value):
        if self._frequency is None and value is not None:
            try:
                self._pwm = GPIO.PWM(self.number, value)
            except RuntimeError:
                raise PinPWMFixedValue('cannot start PWM on pin %r' % self)
            self._pwm.start(0)
            self._duty_cycle = 0
            self._frequency = value
        elif self._frequency is not None and value is not None:
            self._pwm.ChangeFrequency(value)
            self._frequency = value
        elif self._frequency is not None and value is None:
            self._pwm.stop()
            self._pwm = None
            self._duty_cycle = None
            self._frequency = None

    def _get_bounce(self):
        return None if self._bounce == -666 else (self._bounce / 1000)

    def _set_bounce(self, value):
        if value is not None and value < 0:
            raise PinInvalidBounce('bounce must be 0 or greater')
        f = self.when_changed
        self.when_changed = None
        try:
            self._bounce = -666 if value is None else int(value * 1000)
        finally:
            self.when_changed = f

    def _get_edges(self):
        return self.GPIO_EDGES_NAMES[self._edges]

    def _set_edges(self, value):
        f = self.when_changed
        self.when_changed = None
        try:
            self._edges = self.GPIO_EDGES[value]
        finally:
            self.when_changed = f

    def _call_when_changed(self, channel):
        super(RPiGPIOPin, self)._call_when_changed()

    def _enable_event_detect(self):
        GPIO.add_event_detect(
            self.number, self._edges,
            callback=self._call_when_changed,
            bouncetime=self._bounce)

    def _disable_event_detect(self):
        GPIO.remove_event_detect(self.number)
