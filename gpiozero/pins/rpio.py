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

import RPIO
import RPIO.PWM
from RPIO.Exceptions import InvalidChannelException

from .local import LocalPiPin, LocalPiFactory
from .data import pi_info
from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    PinInvalidPull,
    PinInvalidBounce,
    PinInvalidState,
    PinPWMError,
    )


class RPIOFactory(LocalPiFactory):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiFactory`. Uses the `RPIO`_
    library to interface to the Pi's GPIO pins. This is the default pin
    implementation if the RPi.GPIO library is not installed, but RPIO is.
    Supports all features including PWM (hardware via DMA).

    .. note::

        Please note that at the time of writing, RPIO is only compatible with
        Pi 1's; the Raspberry Pi 2 Model B is *not* supported. Also note that
        root access is required so scripts must typically be run with ``sudo``.

    You can construct RPIO pins manually like so::

        from gpiozero.pins.rpio import RPIOFactory
        from gpiozero import LED

        factory = RPIOFactory()
        led = LED(12, pin_factory=factory)

    .. _RPIO: https://pythonhosted.org/RPIO/
    """
    def __init__(self):
        super(RPIOFactory, self).__init__()
        RPIO.setmode(RPIO.BCM)
        RPIO.setwarnings(False)
        RPIO.wait_for_interrupts(threaded=True)
        RPIO.PWM.setup()
        RPIO.PWM.init_channel(0, 10000)
        self.pin_class = RPIOPin

    def close(self):
        RPIO.PWM.cleanup()
        RPIO.stop_waiting_for_interrupts()
        RPIO.cleanup()


class RPIOPin(LocalPiPin):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiPin`. Pin implementation for
    the `RPIO`_ library. See :class:`RPIOFactory` for more information.

    .. _RPIO: https://pythonhosted.org/RPIO/
    """
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

    def __init__(self, factory, number):
        super(RPIOPin, self).__init__(factory, number)
        self._pull = 'up' if self.factory.pi_info.pulled_up(repr(self)) else 'floating'
        self._pwm = False
        self._duty_cycle = None
        self._bounce = None
        self._edges = 'both'
        try:
            RPIO.setup(self.number, RPIO.IN, self.GPIO_PULL_UPS[self._pull])
        except InvalidChannelException as e:
            raise ValueError(e)

    def close(self):
        self.frequency = None
        self.when_changed = None
        RPIO.setup(self.number, RPIO.IN, RPIO.PUD_OFF)

    def _get_function(self):
        return self.GPIO_FUNCTION_NAMES[RPIO.gpio_function(self.number)]

    def _set_function(self, value):
        if value != 'input':
            self._pull = 'floating'
        try:
            RPIO.setup(self.number, self.GPIO_FUNCTIONS[value], self.GPIO_PULL_UPS[self._pull])
        except KeyError:
            raise PinInvalidFunction('invalid function "%s" for pin %r' % (value, self))

    def _get_state(self):
        if self._pwm:
            return self._duty_cycle
        else:
            return RPIO.input(self.number)

    def _set_state(self, value):
        if not 0 <= value <= 1:
            raise PinInvalidState('invalid state "%s" for pin %r' % (value, self))
        if self._pwm:
            RPIO.PWM.clear_channel_gpio(0, self.number)
            if value == 0:
                RPIO.output(self.number, False)
            elif value == 1:
                RPIO.output(self.number, True)
            else:
                RPIO.PWM.add_channel_pulse(0, self.number, start=0, width=int(1000 * value))
            self._duty_cycle = value
        else:
            try:
                RPIO.output(self.number, value)
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
            RPIO.setup(self.number, RPIO.IN, self.GPIO_PULL_UPS[value])
            self._pull = value
        except KeyError:
            raise PinInvalidPull('invalid pull "%s" for pin %r' % (value, self))

    def _get_frequency(self):
        if self._pwm:
            return 100
        else:
            return None

    def _set_frequency(self, value):
        if value is not None and value != 100:
            raise PinPWMError(
                'RPIOPin implementation is currently limited to '
                '100Hz sub-cycles')
        if not self._pwm and value is not None:
            self._pwm = True
            # Dirty hack to get RPIO's PWM support to setup, but do nothing,
            # for a given GPIO pin
            RPIO.PWM.add_channel_pulse(0, self.number, start=0, width=0)
            RPIO.PWM.clear_channel_gpio(0, self.number)
        elif self._pwm and value is None:
            RPIO.PWM.clear_channel_gpio(0, self.number)
            self._pwm = False

    def _get_bounce(self):
        return None if self._bounce is None else (self._bounce / 1000)

    def _set_bounce(self, value):
        if value is not None and value < 0:
            raise PinInvalidBounce('bounce must be 0 or greater')
        f = self.when_changed
        self.when_changed = None
        try:
            self._bounce = None if value is None else int(value * 1000)
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

    def _call_when_changed(self, channel, value):
        super(RPIOPin, self)._call_when_changed()

    def _enable_event_detect(self):
        RPIO.add_interrupt_callback(
            self.number, self._call_when_changed, self._edges,
            self.GPIO_PULL_UPS[self._pull], self._bounce)

    def _disable_event_detect(self):
        try:
            RPIO.del_interrupt_callback(self.number)
        except KeyError:
            # Ignore this exception which occurs during shutdown; this
            # simply means RPIO's built-in cleanup has already run and
            # removed the handler
            pass
