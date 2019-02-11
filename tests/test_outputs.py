# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
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


import sys
from time import sleep, time
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose

import pytest
from colorzero import Color, Red, Green, Blue

from gpiozero import *


def test_output_initial_values(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with OutputDevice(2, initial_value=False) as device:
        assert repr(device).startswith('<gpiozero.OutputDevice object')
        assert pin.function == 'output'
        assert not pin.state
    with OutputDevice(2, initial_value=True) as device:
        assert pin.state
        state = pin.state
    with OutputDevice(2, initial_value=None) as device:
        assert state == pin.state

def test_output_write_active_high(mock_factory):
    pin = mock_factory.pin(2)
    with OutputDevice(2) as device:
        device.on()
        assert pin.state
        device.off()
        assert not pin.state

def test_output_write_active_low(mock_factory):
    pin = mock_factory.pin(2)
    with OutputDevice(2, active_high=False) as device:
        device.on()
        assert not pin.state
        device.off()
        assert pin.state

def test_output_write_closed(mock_factory):
    with OutputDevice(2) as device:
        device.close()
        assert device.closed
        device.close()
        assert device.closed
        with pytest.raises(GPIODeviceClosed):
            device.on()

def test_output_write_silly(mock_factory):
    pin = mock_factory.pin(2)
    with OutputDevice(2) as device:
        pin.function = 'input'
        with pytest.raises(AttributeError):
            device.on()

def test_output_value(mock_factory):
    pin = mock_factory.pin(2)
    with OutputDevice(2) as device:
        assert not device.value
        assert not pin.state
        device.on()
        assert device.value
        assert pin.state
        device.value = False
        assert not device.value
        assert not pin.state

def test_output_digital_toggle(mock_factory):
    pin = mock_factory.pin(2)
    with DigitalOutputDevice(2) as device:
        assert repr(device).startswith('<gpiozero.DigitalOutputDevice object')
        assert not device.value
        assert not pin.state
        device.toggle()
        assert device.value
        assert pin.state
        device.toggle()
        assert not device.value
        assert not pin.state

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_blink_background(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        start = time()
        device.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join() # naughty, but ensures no arbitrary waits in the test
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_blink_foreground(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        start = time()
        device.blink(0.1, 0.1, n=2, background=False)
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ])

def test_output_blink_interrupt_on(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        pin.assert_states([False, True, False])

def test_output_blink_interrupt_off(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        device.blink(0.1, 1)
        sleep(0.2)
        device.off() # should interrupt while off
        pin.assert_states([False, True, False])

def test_output_pwm_bad_initial_value(mock_factory):
    with pytest.raises(ValueError):
        PWMOutputDevice(2, initial_value=2)

def test_output_pwm_not_supported(mock_factory):
    with pytest.raises(AttributeError):
        PWMOutputDevice(2)

def test_output_pwm_states(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        assert repr(device).startswith('<gpiozero.PWMOutputDevice object')
        device.value = 0.1
        device.value = 0.2
        device.value = 0.0
        pin.assert_states([0.0, 0.1, 0.2, 0.0])

def test_output_pwm_read(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with PWMOutputDevice(2, frequency=100) as device:
        assert device.frequency == 100
        device.value = 0.1
        assert isclose(device.value, 0.1)
        assert isclose(pin.state, 0.1)
        assert device.is_active
        device.frequency = None
        assert not device.value
        assert not device.is_active
        assert device.frequency is None

def test_output_pwm_write(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.on()
        device.off()
        pin.assert_states([False, True, False])

def test_output_pwm_toggle(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.toggle()
        device.value = 0.5
        device.value = 0.1
        device.toggle()
        device.off()
        pin.assert_states([False, True, 0.5, 0.1, 0.9, False])

def test_output_pwm_active_high_read(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with PWMOutputDevice(2, active_high=False) as device:
        device.value = 0.1
        assert isclose(device.value, 0.1)
        assert isclose(pin.state, 0.9)
        device.frequency = None
        assert device.value

def test_output_pwm_bad_value(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with PWMOutputDevice(2) as device:
        with pytest.raises(ValueError):
            device.value = 2

def test_output_pwm_write_closed(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with PWMOutputDevice(2) as device:
        device.close()
        with pytest.raises(GPIODeviceClosed):
            device.on()

def test_output_pwm_write_silly(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with PWMOutputDevice(2) as device:
        pin.function = 'input'
        with pytest.raises(AttributeError):
            device.off()

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_blink_background(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_blink_foreground(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.blink(0.1, 0.1, n=2, background=False)
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_fade_background(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.blink(0, 0, 0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_fade_foreground(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.blink(0, 0, 0.2, 0.2, n=2, background=False)
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_pulse_background(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.pulse(0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_pulse_foreground(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        start = time()
        device.pulse(0.2, 0.2, n=2, background=False)
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        pin.assert_states_and_times([
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ])

def test_output_pwm_blink_interrupt(mock_factory, pwm):
    pin = mock_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        pin.assert_states([0, 1, 0])

def test_rgbled_missing_pins(mock_factory):
    with pytest.raises(GPIOPinMissing):
        RGBLED()

def test_rgbled_initial_value(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, initial_value=(0.1, 0.2, 0)) as led:
        assert repr(led).startswith('<gpiozero.RGBLED object')
        assert r.frequency
        assert g.frequency
        assert b.frequency
        assert isclose(r.state, 0.1)
        assert isclose(g.state, 0.2)
        assert isclose(b.state, 0.0)

def test_rgbled_initial_value_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False, initial_value=(0, 1, 1)) as led:
        assert r.state == 0
        assert g.state == 1
        assert b.state == 1

def test_rgbled_initial_bad_value(mock_factory, pwm):
    with pytest.raises(ValueError):
        RGBLED(1, 2, 3, initial_value=(0.1, 0.2, 1.2))

def test_rgbled_initial_bad_value_nonpwm(mock_factory):
    with pytest.raises(ValueError):
        RGBLED(1, 2, 3, pwm=False, initial_value=(0.1, 0.2, 0))

def test_rgbled_value(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        assert isinstance(led._leds[0], PWMLED)
        assert isinstance(led._leds[1], PWMLED)
        assert isinstance(led._leds[2], PWMLED)
        assert not led.is_active
        assert led.value == (0, 0, 0)
        led.on()
        assert led.is_active
        assert led.value == (1, 1, 1)
        led.off()
        assert not led.is_active
        assert led.value == (0, 0, 0)
        led.value = (0.5, 0.5, 0.5)
        assert led.is_active
        assert led.value == (0.5, 0.5, 0.5)

def test_rgbled_value_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert isinstance(led._leds[0], LED)
        assert isinstance(led._leds[1], LED)
        assert isinstance(led._leds[2], LED)
        assert not led.is_active
        assert led.value == (0, 0, 0)
        led.on()
        assert led.is_active
        assert led.value == (1, 1, 1)
        led.off()
        assert not led.is_active
        assert led.value == (0, 0, 0)

def test_rgbled_bad_value(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        with pytest.raises(ValueError):
            led.value = (2, 0, 0)
    with RGBLED(1, 2, 3) as led:
        with pytest.raises(ValueError):
            led.value = (0, -1, 0)

def test_rgbled_bad_value_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.value = (2, 0, 0)
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.value = (0, -1, 0)
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.value = (0.5, 0, 0)
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.value = (0, 0.5, 0)
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.value = (0, 0, 0.5)

def test_rgbled_toggle(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        assert not led.is_active
        assert led.value == (0, 0, 0)
        led.toggle()
        assert led.is_active
        assert led.value == (1, 1, 1)
        led.toggle()
        assert not led.is_active
        assert led.value == (0, 0, 0)

def test_rgbled_toggle_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert not led.is_active
        assert led.value == (0, 0, 0)
        led.toggle()
        assert led.is_active
        assert led.value == (1, 1, 1)
        led.toggle()
        assert not led.is_active
        assert led.value == (0, 0, 0)

def test_rgbled_bad_color_value_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.color = (0.5, 0, 0)
        with pytest.raises(ValueError):
            led.color = (0, 1.5, 0)
        with pytest.raises(ValueError):
            led.color = (0, 0, -1)

def test_rgbled_bad_color_value_pwm(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        with pytest.raises(ValueError):
            led.color = (0, 1.5, 0)
        with pytest.raises(ValueError):
            led.color = (0, 0, -1)
        with pytest.raises(ValueError):
            led.green = 1.5
        with pytest.raises(ValueError):
            led.blue = -1

def test_rgbled_color_value_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert led.value == (0, 0, 0)
        assert led.red == 0
        assert led.green == 0
        assert led.blue == 0
        led.on()
        assert led.value == (1, 1, 1)
        assert led.color == (1, 1, 1)
        assert led.red == 1
        assert led.green == 1
        assert led.blue == 1
        led.color = (0, 1, 0)
        assert led.value == (0, 1, 0)
        assert led.red == 0
        led.red = 1
        assert led.value == (1, 1, 0)
        assert led.red == 1
        assert led.green == 1
        assert led.blue == 0
        led.green = 0
        led.blue = 1
        assert led.value == (1, 0, 1)

def test_rgbled_color_value_pwm(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        assert led.value == (0, 0, 0)
        assert led.red == 0
        assert led.green == 0
        assert led.blue == 0
        led.on()
        assert led.value == (1, 1, 1)
        assert led.color == (1, 1, 1)
        assert led.red == 1
        assert led.green == 1
        assert led.blue == 1
        led.color = (0.2, 0.5, 0.8)
        assert led.value == (0.2, 0.5, 0.8)
        assert led.red == 0.2
        led.red = 0.5
        assert led.value == (0.5, 0.5, 0.8)
        assert led.red == 0.5
        assert led.green == 0.5
        assert led.blue == 0.8
        led.green = 0.9
        led.blue = 0.4
        assert led.value == (0.5, 0.9, 0.4)

def test_rgbled_bad_rgb_property_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.red = 0.1
        with pytest.raises(ValueError):
            led.green = 0.5
        with pytest.raises(ValueError):
            led.blue = 0.9
        with pytest.raises(ValueError):
            led.red = Red(0.1)
        with pytest.raises(ValueError):
            led.green = Green(0.5)
        with pytest.raises(ValueError):
            led.blue = Blue(0.9)

def test_rgbled_bad_rgb_property_pwm(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        with pytest.raises(ValueError):
            led.red = 1.5
        with pytest.raises(ValueError):
            led.green = 2
        with pytest.raises(ValueError):
            led.blue = -1
        with pytest.raises(ValueError):
            led.red = Red(1.5)
        with pytest.raises(ValueError):
            led.green = Green(2)
        with pytest.raises(ValueError):
            led.blue = Blue(-1)

def test_rgbled_rgb_property_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert led.value == (0, 0, 0)
        led.red = Red(0)
        assert led.value == (0, 0, 0)
        led.red = Red(1)
        assert led.value == (1, 0, 0)
        led.green = Green(1)
        assert led.value == (1, 1, 0)
        led.blue = Blue(1)
        assert led.value == (1, 1, 1)

def test_rgbled_rgb_property_pwm(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        assert led.value == (0, 0, 0)
        led.red = Red(0)
        assert led.value == (0, 0, 0)
        led.red = Red(0.5)
        assert led.value == (0.5, 0, 0)
        led.green = Green(0.5)
        assert led.value == (0.5, 0.5, 0)
        led.blue = Blue(0.5)
        assert led.value == (0.5, 0.5, 0.5)

def test_rgbled_bad_color_name_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.color = Color('green')  # html 'green' is (0, ~0.5, 0)
        with pytest.raises(ValueError):
            led.color = Color(0.5, 0, 0)
        with pytest.raises(ValueError):
            led.color = Color(250, 0, 0)

def test_rgbled_color_name_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert led.value == (0, 0, 0)
        led.color = Color('white')
        assert led.value == (1, 1, 1)
        led.color = Color('black')
        assert led.value == (0, 0, 0)
        led.color = Color('red')
        assert led.value == (1, 0, 0)
        led.color = Color('lime')  # html 'green' is (0, 0.5, 0)
        assert led.value == (0, 1, 0)
        led.color = Color('blue')
        assert led.value == (0, 0, 1)
        led.color = Color('cyan')
        assert led.value == (0, 1, 1)
        led.color = Color('magenta')
        assert led.value == (1, 0, 1)
        led.color = Color('yellow')
        assert led.value == (1, 1, 0)

def test_rgbled_color_name_pwm(mock_factory, pwm):
    with RGBLED(1, 2, 3) as led:
        assert led.value == (0, 0, 0)
        led.color = Color('white')
        assert led.value == (1, 1, 1)
        led.color = Color('green')
        assert led.value == (0, 0.5019607843137255, 0)
        led.color = Color('chocolate')
        assert led.value == (0.8235294117647058, 0.4117647058823529, 0.11764705882352941)
        led.color = Color('purple')
        assert led.value == (0.5019607843137255, 0.0, 0.5019607843137255)

def test_rgbled_blink_nonpwm(mock_factory):
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.blink(fade_in_time=1)
        with pytest.raises(ValueError):
            led.blink(fade_out_time=1)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_blink_background(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        led._blink_thread.join()
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_blink_background_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as led:
        start = time()
        led.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        led._blink_thread.join()
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_blink_foreground(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.blink(0.1, 0.1, n=2, background=False)
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_blink_foreground_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as led:
        start = time()
        led.blink(0.1, 0.1, n=2, background=False)
        assert isclose(time() - start, 0.4, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.0, 1),
            (0.1, 0),
            (0.1, 1),
            (0.1, 0)
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_fade_background(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.blink(0, 0, 0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        led._blink_thread.join()
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

def test_rgbled_fade_background_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.blink(0, 0, 0.2, 0, n=2)
        with pytest.raises(ValueError):
            led.blink(0, 0, 0, 0.2, n=2)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_fade_foreground(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.blink(0, 0, 0.2, 0.2, n=2, background=False)
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

def test_rgbled_fade_foreground_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.blink(0, 0, 0.2, 0.2, n=2, background=False)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_pulse_background(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.pulse(0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        led._blink_thread.join()
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

def test_rgbled_pulse_background_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.pulse(0.2, 0.2, n=2)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_pulse_foreground(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        start = time()
        led.pulse(0.2, 0.2, n=2, background=False)
        assert isclose(time() - start, 0.8, abs_tol=0.05)
        expected = [
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ]
        r.assert_states_and_times(expected)
        g.assert_states_and_times(expected)
        b.assert_states_and_times(expected)

def test_rgbled_pulse_foreground_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as led:
        with pytest.raises(ValueError):
            led.pulse(0.2, 0.2, n=2, background=False)

def test_rgbled_blink_interrupt(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as led:
        led.blink(1, 0.1)
        sleep(0.2)
        led.off() # should interrupt while on
        r.assert_states([0, 1, 0])
        g.assert_states([0, 1, 0])
        b.assert_states([0, 1, 0])

def test_rgbled_blink_interrupt_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as led:
        led.blink(1, 0.1)
        sleep(0.2)
        led.off() # should interrupt while on
        r.assert_states([0, 1, 0])
        g.assert_states([0, 1, 0])
        b.assert_states([0, 1, 0])

def test_rgbled_close(mock_factory, pwm):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3) as led:
        assert not led.closed
        led.close()
        assert led.closed
        led.close()
        assert led.closed

def test_rgbled_close_nonpwm(mock_factory):
    r, g, b = (mock_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as led:
        assert not led.closed
        led.close()
        assert led.closed
        led.close()
        assert led.closed

def test_motor_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        Motor()
    with pytest.raises(GPIOPinMissing):
        Motor(2)
    with pytest.raises(GPIOPinMissing):
        Motor(forward=2)
    with pytest.raises(GPIOPinMissing):
        Motor(backward=2)
    with pytest.raises(TypeError):
        Motor(a=2, b=3)

def test_motor_pins(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2) as motor:
        assert repr(motor).startswith('<gpiozero.Motor object')
        assert motor.forward_device.pin is f
        assert isinstance(motor.forward_device, PWMOutputDevice)
        assert motor.backward_device.pin is b
        assert isinstance(motor.backward_device, PWMOutputDevice)

def test_motor_pins_nonpwm(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2, pwm=False) as motor:
        assert motor.forward_device.pin is f
        assert isinstance(motor.forward_device, DigitalOutputDevice)
        assert motor.backward_device.pin is b
        assert isinstance(motor.backward_device, DigitalOutputDevice)

def test_motor_close(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2) as motor:
        motor.close()
        assert motor.closed
        assert motor.forward_device.pin is None
        assert motor.backward_device.pin is None
        motor.close()
        assert motor.closed

def test_motor_close_nonpwm(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2, pwm=False) as motor:
        motor.close()
        assert motor.closed
        assert motor.forward_device.pin is None
        assert motor.backward_device.pin is None

def test_motor_value(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2) as motor:
        motor.value = -1
        assert motor.is_active
        assert motor.value == -1
        assert b.state == 1 and f.state == 0
        motor.value = 1
        assert motor.is_active
        assert motor.value == 1
        assert b.state == 0 and f.state == 1
        motor.value = 0.5
        assert motor.is_active
        assert motor.value == 0.5
        assert b.state == 0 and f.state == 0.5
        motor.value = -0.5
        assert motor.is_active
        assert motor.value == -0.5
        assert b.state == 0.5 and f.state == 0
        motor.value = 0
        assert not motor.is_active
        assert not motor.value
        assert b.state == 0 and f.state == 0

def test_motor_value_nonpwm(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2, pwm=False) as motor:
        motor.value = -1
        assert motor.is_active
        assert motor.value == -1
        assert b.state == 1 and f.state == 0
        motor.value = 1
        assert motor.is_active
        assert motor.value == 1
        assert b.state == 0 and f.state == 1
        motor.value = 0
        assert not motor.is_active
        assert not motor.value
        assert b.state == 0 and f.state == 0

def test_motor_bad_value(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2) as motor:
        with pytest.raises(ValueError):
            motor.value = -2
        with pytest.raises(ValueError):
            motor.value = 2
        with pytest.raises(ValueError):
            motor.forward(2)
        with pytest.raises(ValueError):
            motor.backward(2)
        with pytest.raises(ValueError):
            motor.forward(-1)
        with pytest.raises(ValueError):
            motor.backward(-1)

def test_motor_bad_value_nonpwm(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2, pwm=False) as motor:
        with pytest.raises(ValueError):
            motor.value = -2
        with pytest.raises(ValueError):
            motor.value = 2
        with pytest.raises(ValueError):
            motor.value = 0.5
        with pytest.raises(ValueError):
            motor.value = -0.5
        with pytest.raises(ValueError):
            motor.forward(0.5)
        with pytest.raises(ValueError):
            motor.backward(0.5)

def test_motor_reverse(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2) as motor:
        motor.forward()
        assert motor.value == 1
        assert b.state == 0 and f.state == 1
        motor.reverse()
        assert motor.value == -1
        assert b.state == 1 and f.state == 0
        motor.backward(0.5)
        assert motor.value == -0.5
        assert b.state == 0.5 and f.state == 0
        motor.reverse()
        assert motor.value == 0.5
        assert b.state == 0 and f.state == 0.5

def test_motor_reverse_nonpwm(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    with Motor(1, 2, pwm=False) as motor:
        motor.forward()
        assert motor.value == 1
        assert b.state == 0 and f.state == 1
        motor.reverse()
        assert motor.value == -1
        assert b.state == 1 and f.state == 0

def test_motor_enable_pin_bad_init(mock_factory, pwm):
    with pytest.raises(GPIOPinMissing):
        Motor(enable=1)
    with pytest.raises(GPIOPinMissing):
        Motor(forward=1, enable=2)
    with pytest.raises(GPIOPinMissing):
        Motor(backward=1, enable=2)
    with pytest.raises(GPIOPinMissing):
        Motor(backward=1, enable=2, pwm=True)

def test_motor_enable_pin_init(mock_factory, pwm):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    e = mock_factory.pin(3)
    with Motor(forward=1, backward=2, enable=3) as motor:
        assert motor.forward_device.pin is f
        assert isinstance(motor.forward_device, PWMOutputDevice)
        assert motor.backward_device.pin is b
        assert isinstance(motor.backward_device, PWMOutputDevice)
        assert motor.enable_device.pin is e
        assert isinstance(motor.enable_device, DigitalOutputDevice)
        assert e.state
    with Motor(1, 2, 3) as motor:
        assert motor.forward_device.pin is f
        assert isinstance(motor.forward_device, PWMOutputDevice)
        assert motor.backward_device.pin is b
        assert isinstance(motor.backward_device, PWMOutputDevice)
        assert motor.enable_device.pin is e
        assert isinstance(motor.enable_device, DigitalOutputDevice)
        assert e.state

def test_motor_enable_pin_nonpwm_init(mock_factory):
    f = mock_factory.pin(1)
    b = mock_factory.pin(2)
    e = mock_factory.pin(3)
    with Motor(forward=1, backward=2, enable=3, pwm=False) as motor:
        assert motor.forward_device.pin is f
        assert isinstance(motor.forward_device, DigitalOutputDevice)
        assert motor.backward_device.pin is b
        assert isinstance(motor.backward_device, DigitalOutputDevice)
        assert motor.enable_device.pin is e
        assert isinstance(motor.enable_device, DigitalOutputDevice)

def test_motor_enable_pin(mock_factory, pwm):
    with Motor(forward=1, backward=2, enable=3) as motor:
        motor.forward()
        assert motor.value == 1
        motor.backward()
        assert motor.value == -1
        motor.stop()
        assert motor.value == 0

def test_phaseenable_motor_pins(mock_factory, pwm):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2) as motor:
        assert repr(motor).startswith('<gpiozero.PhaseEnableMotor object')
        assert motor.phase_device.pin is p
        assert isinstance(motor.phase_device, OutputDevice)
        assert motor.enable_device.pin is e
        assert isinstance(motor.enable_device, PWMOutputDevice)

def test_phaseenable_motor_pins_nonpwm(mock_factory):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as motor:
        assert motor.phase_device.pin is p
        assert isinstance(motor.phase_device, OutputDevice)
        assert motor.enable_device.pin is e
        assert isinstance(motor.enable_device, DigitalOutputDevice)

def test_phaseenable_motor_close(mock_factory, pwm):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2) as motor:
        motor.close()
        assert motor.closed
        assert motor.phase_device.pin is None
        assert motor.enable_device.pin is None
        motor.close()
        assert motor.closed

def test_phaseenable_motor_close_nonpwm(mock_factory):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as motor:
        motor.close()
        assert motor.closed
        assert motor.phase_device.pin is None
        assert motor.enable_device.pin is None

def test_phaseenable_motor_value(mock_factory, pwm):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2) as motor:
        motor.value = -1
        assert motor.is_active
        assert motor.value == -1
        assert p.state == 1 and e.state == 1
        motor.value = 1
        assert motor.is_active
        assert motor.value == 1
        assert p.state == 0 and e.state == 1
        motor.value = 0.5
        assert motor.is_active
        assert motor.value == 0.5
        assert p.state == 0 and e.state == 0.5
        motor.value = -0.5
        assert motor.is_active
        assert motor.value == -0.5
        assert p.state == 1 and e.state == 0.5
        motor.value = 0
        assert not motor.is_active
        assert not motor.value
        assert e.state == 0

def test_phaseenable_motor_value_nonpwm(mock_factory):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as motor:
        motor.value = -1
        assert motor.is_active
        assert motor.value == -1
        assert p.state == 1 and e.state == 1
        motor.value = 1
        assert motor.is_active
        assert motor.value == 1
        assert p.state == 0 and e.state == 1
        motor.value = 0
        assert not motor.is_active
        assert not motor.value
        assert e.state == 0

def test_phaseenable_motor_bad_value(mock_factory, pwm):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2) as motor:
        with pytest.raises(ValueError):
            motor.value = -2
        with pytest.raises(ValueError):
            motor.value = 2
        with pytest.raises(ValueError):
            motor.forward(2)
        with pytest.raises(ValueError):
            motor.backward(2)

def test_phaseenable_motor_bad_value_nonpwm(mock_factory):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as motor:
        with pytest.raises(ValueError):
            motor.value = -2
        with pytest.raises(ValueError):
            motor.value = 2
        with pytest.raises(ValueError):
            motor.value = 0.5
        with pytest.raises(ValueError):
            motor.value = -0.5

def test_phaseenable_motor_reverse(mock_factory, pwm):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2) as motor:
        motor.forward()
        assert motor.value == 1
        assert p.state == 0 and e.state == 1
        motor.reverse()
        assert motor.value == -1
        assert p.state == 1 and e.state == 1
        motor.backward(0.5)
        assert motor.value == -0.5
        assert p.state == 1 and e.state == 0.5
        motor.reverse()
        assert motor.value == 0.5
        assert p.state == 0 and e.state == 0.5

def test_phaseenable_motor_reverse_nonpwm(mock_factory):
    p = mock_factory.pin(1)
    e = mock_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as motor:
        motor.forward()
        assert motor.value == 1
        assert p.state == 0 and e.state == 1
        motor.reverse()
        assert motor.value == -1
        assert p.state == 1 and e.state == 1

def test_servo_pins(mock_factory, pwm):
    p = mock_factory.pin(1)
    with Servo(1) as servo:
        assert repr(servo).startswith('<gpiozero.Servo object')
        assert servo.pwm_device.pin is p
        assert isinstance(servo.pwm_device, PWMOutputDevice)

def test_servo_bad_value(mock_factory, pwm):
    p = mock_factory.pin(1)
    with pytest.raises(ValueError):
        Servo(1, initial_value=2)
    with pytest.raises(ValueError):
        Servo(1, min_pulse_width=30/1000)
    with pytest.raises(ValueError):
        Servo(1, max_pulse_width=30/1000)

def test_servo_pins_nonpwm(mock_factory):
    p = mock_factory.pin(2)
    with pytest.raises(PinPWMUnsupported):
        Servo(1)

def test_servo_close(mock_factory, pwm):
    p = mock_factory.pin(2)
    with Servo(2) as servo:
        servo.close()
        assert servo.closed
        assert servo.pwm_device.pin is None
        servo.close()
        assert servo.closed

def test_servo_pulse_width(mock_factory, pwm):
    p = mock_factory.pin(2)
    with Servo(2, min_pulse_width=5/10000, max_pulse_width=25/10000) as servo:
        assert isclose(servo.min_pulse_width, 5/10000)
        assert isclose(servo.max_pulse_width, 25/10000)
        assert isclose(servo.frame_width, 20/1000)
        assert isclose(servo.pulse_width, 15/10000)
        servo.value = -1
        assert isclose(servo.pulse_width, 5/10000)
        servo.value = 1
        assert isclose(servo.pulse_width, 25/10000)
        servo.value = None
        assert servo.pulse_width is None

def test_servo_initial_values(mock_factory, pwm):
    p = mock_factory.pin(2)
    with Servo(2) as servo:
        assert servo.value == 0
    with Servo(2, initial_value=-1) as servo:
        assert servo.is_active
        assert servo.value == -1
        assert isclose(p.state, 0.05)
    with Servo(2, initial_value=0) as servo:
        assert servo.is_active
        assert servo.value == 0
        assert isclose(p.state, 0.075)
    with Servo(2, initial_value=1) as servo:
        assert servo.is_active
        assert servo.value == 1
        assert isclose(p.state, 0.1)
    with Servo(2, initial_value=None) as servo:
        assert not servo.is_active
        assert servo.value is None

def test_servo_values(mock_factory, pwm):
    p = mock_factory.pin(1)
    with Servo(1) as servo:
        servo.min()
        assert servo.is_active
        assert servo.value == -1
        assert isclose(p.state, 0.05)
        servo.max()
        assert servo.is_active
        assert servo.value == 1
        assert isclose(p.state, 0.1)
        servo.mid()
        assert servo.is_active
        assert servo.value == 0.0
        assert isclose(p.state, 0.075)
        servo.value = 0.5
        assert servo.is_active
        assert servo.value == 0.5
        assert isclose(p.state, 0.0875)
        servo.detach()
        assert not servo.is_active
        assert servo.value is None
        servo.value = 0
        assert servo.value == 0
        servo.value = None
        assert servo.value is None

def test_angular_servo_range(mock_factory, pwm):
    with AngularServo(1, initial_angle=15, min_angle=0, max_angle=90) as servo:
        assert repr(servo).startswith('<gpiozero.AngularServo object')
        assert servo.min_angle == 0
        assert servo.max_angle == 90

def test_angular_servo_initial_angles(mock_factory, pwm):
    with AngularServo(1) as servo:
        assert servo.angle == 0
    with AngularServo(1, initial_angle=-90) as servo:
        assert servo.angle == -90
        assert isclose(servo.value, -1)
    with AngularServo(1, initial_angle=0) as servo:
        assert servo.angle == 0
        assert isclose(servo.value, 0)
    with AngularServo(1, initial_angle=90) as servo:
        assert servo.angle == 90
        assert isclose(servo.value, 1)
    with AngularServo(1, initial_angle=None) as servo:
        assert servo.angle is None

def test_angular_servo_angles(mock_factory, pwm):
    with AngularServo(1) as servo:
        servo.angle = 0
        assert servo.angle == 0
        assert isclose(servo.value, 0)
        servo.max()
        assert servo.angle == 90
        assert isclose(servo.value, 1)
        servo.min()
        assert servo.angle == -90
        assert isclose(servo.value, -1)
        servo.detach()
        assert servo.angle is None

    with AngularServo(1, initial_angle=15, min_angle=0, max_angle=90) as servo:
        assert servo.angle == 15
        assert isclose(servo.value, -2/3)
        servo.angle = 0
        assert servo.angle == 0
        assert isclose(servo.value, -1)
        servo.angle = 90
        assert servo.angle == 90
        assert isclose(servo.value, 1)
        servo.angle = None
        assert servo.angle is None

    with AngularServo(1, min_angle=45, max_angle=-45) as servo:
        assert servo.angle == 0
        assert isclose(servo.value, 0)
        servo.angle = -45
        assert servo.angle == -45
        assert isclose(servo.value, 1)
        servo.angle = -15
        assert servo.angle == -15
        assert isclose(servo.value, 1/3)

def test_tonalbuzzer_bad_init(mock_factory, pwm):
    with pytest.raises(ValueError):
        TonalBuzzer(2, initial_value=-2)
    with pytest.raises(ValueError):
        TonalBuzzer(2, initial_value=2)
    with pytest.raises(ValueError):
        TonalBuzzer(2, mid_tone='foo')
    with pytest.raises(ValueError):
        TonalBuzzer(2, octaves=0)
    with pytest.raises(ValueError):
        TonalBuzzer(2, octaves=0)
    with pytest.raises(ValueError):
        TonalBuzzer(2, mid_tone='B0', octaves=2)
    with pytest.raises(ValueError):
        TonalBuzzer(2, mid_tone='B1', octaves=3)
    with pytest.raises(ValueError):
        TonalBuzzer(2, mid_tone='B2', octaves=4)

def test_tonalbuzzer_init(mock_factory, pwm):
    pin = mock_factory.pin(2)
    with TonalBuzzer(2) as tb:
        assert repr(tb).startswith('<gpiozero.TonalBuzzer object')
        assert tb.pwm_device.pin is pin
        assert tb.value is None
        assert tb.pwm_device.frequency is None
    with TonalBuzzer(2, mid_tone='C4') as tb:
        assert tb.pwm_device.frequency is None
    with TonalBuzzer(2, mid_tone='C4', initial_value=0) as tb:
        assert isclose(tb.pwm_device.frequency, 261.626, abs_tol=1/100)
    with TonalBuzzer(2, initial_value=-1) as tb:
        assert isclose(tb.pwm_device.frequency, 220)
    with TonalBuzzer(2, initial_value=0) as tb:
        assert isclose(tb.pwm_device.frequency, 440)
    with TonalBuzzer(2, initial_value=1) as tb:
        assert isclose(tb.pwm_device.frequency, 880)
    with TonalBuzzer(2, octaves=2, initial_value=-1) as tb:
        assert isclose(tb.pwm_device.frequency, 110)
    with TonalBuzzer(2, octaves=2, initial_value=0) as tb:
        assert isclose(tb.pwm_device.frequency, 440)
    with TonalBuzzer(2, octaves=2, initial_value=1) as tb:
        assert isclose(tb.pwm_device.frequency, 1760)

def test_tonalbuzzer_play(mock_factory, pwm):
    with TonalBuzzer(2) as tb:
        tb.play(60)
        assert isclose(tb.pwm_device.frequency, 261.626, abs_tol=1/100)
        tb.play(None)
        assert tb.value is None
        assert tb.pwm_device.frequency is None
        tb.play('C5')
        assert isclose(tb.pwm_device.frequency, 523.25, abs_tol=1/100)
        tb.play('A#4')
        assert isclose(tb.pwm_device.frequency, 466.16, abs_tol=1/100)
        tb.stop()
        assert tb.value is None
        assert tb.pwm_device.frequency is None
        with pytest.raises(ValueError):
            tb.play('GS3')
        with pytest.raises(ValueError):
            tb.play('AS5')

def test_tonalbuzzer_set_value(mock_factory, pwm):
    with TonalBuzzer(2) as tb:
        assert tb.pwm_device.frequency is None
        tb.value = -1
        assert isclose(tb.pwm_device.frequency, 220)
        tb.value = 1
        assert isclose(tb.pwm_device.frequency, 880)
    with TonalBuzzer(2, octaves=2) as tb:
        assert tb.pwm_device.frequency is None
        tb.value = -1
        assert isclose(tb.pwm_device.frequency, 110)
        tb.value = 1
        assert isclose(tb.pwm_device.frequency, 1760)

def test_tonalbuzzer_read_value(mock_factory, pwm):
    with TonalBuzzer(2) as tb:
        assert tb.value is None
        tb.play('A3')
        assert isclose(tb.value, -1)
        tb.play('A4')
        assert isclose(tb.value, 0)
        tb.play('A5')
        assert isclose(tb.value, 1)
    with TonalBuzzer(2, octaves=2) as tb:
        assert tb.value is None
        tb.play('A2')
        assert isclose(tb.value, -1)
        tb.play('A3')
        assert isclose(tb.value, -0.5)
        tb.play('A4')
        assert isclose(tb.value, 0)
        tb.play('A5')
        assert isclose(tb.value, 0.5)
        tb.play('A6')
        assert isclose(tb.value, 1)
