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

from gpiozero.pins.mock import MockPin, MockPWMPin
from gpiozero import *


def setup_function(function):
    # dirty, but it does the job
    Device.pin_factory.pin_class = MockPWMPin if function.__name__ in (
        'test_output_pwm_states',
        'test_output_pwm_read',
        'test_output_pwm_write',
        'test_output_pwm_toggle',
        'test_output_pwm_active_high_read',
        'test_output_pwm_bad_value',
        'test_output_pwm_write_closed',
        'test_output_pwm_write_silly',
        'test_output_pwm_blink_background',
        'test_output_pwm_blink_foreground',
        'test_output_pwm_fade_background',
        'test_output_pwm_fade_foreground',
        'test_output_pwm_pulse_background',
        'test_output_pwm_pulse_foreground',
        'test_output_pwm_blink_interrupt',
        'test_rgbled_initial_value',
        'test_rgbled_initial_bad_value',
        'test_rgbled_value',
        'test_rgbled_bad_value',
        'test_rgbled_toggle',
        'test_rgbled_blink_background',
        'test_rgbled_blink_foreground',
        'test_rgbled_fade_background',
        'test_rgbled_fade_foreground',
        'test_rgbled_pulse_background',
        'test_rgbled_pulse_foreground',
        'test_rgbled_blink_interrupt',
        'test_rgbled_close',
        'test_motor_pins',
        'test_motor_close',
        'test_motor_value',
        'test_motor_bad_value',
        'test_motor_reverse',
        'test_phaseenable_motor_pins',
        'test_phaseenable_motor_close',
        'test_phaseenable_motor_value',
        'test_phaseenable_motor_bad_value',
        'test_phaseenable_motor_reverse',
        'test_servo_pins',
        'test_servo_bad_value',
        'test_servo_close',
        'test_servo_pulse_width',
        'test_servo_values',
        'test_servo_initial_values',
        'test_angular_servo_range',
        'test_angular_servo_angles',
        'test_angular_servo_initial_angles',
        ) else MockPin

def teardown_function(function):
    Device.pin_factory.reset()


def test_output_initial_values():
    pin = Device.pin_factory.pin(2)
    with OutputDevice(2, initial_value=False) as device:
        assert pin.function == 'output'
        assert not pin.state
    with OutputDevice(2, initial_value=True) as device:
        assert pin.state
        state = pin.state
    with OutputDevice(2, initial_value=None) as device:
        assert state == pin.state

def test_output_write_active_high():
    pin = Device.pin_factory.pin(2)
    with OutputDevice(2) as device:
        device.on()
        assert pin.state
        device.off()
        assert not pin.state

def test_output_write_active_low():
    pin = Device.pin_factory.pin(2)
    with OutputDevice(2, active_high=False) as device:
        device.on()
        assert not pin.state
        device.off()
        assert pin.state

def test_output_write_closed():
    with OutputDevice(2) as device:
        device.close()
        assert device.closed
        device.close()
        assert device.closed
        with pytest.raises(GPIODeviceClosed):
            device.on()

def test_output_write_silly():
    pin = Device.pin_factory.pin(2)
    with OutputDevice(2) as device:
        pin.function = 'input'
        with pytest.raises(AttributeError):
            device.on()

def test_output_value():
    pin = Device.pin_factory.pin(2)
    with OutputDevice(2) as device:
        assert not device.value
        assert not pin.state
        device.on()
        assert device.value
        assert pin.state
        device.value = False
        assert not device.value
        assert not pin.state

def test_output_digital_toggle():
    pin = Device.pin_factory.pin(2)
    with DigitalOutputDevice(2) as device:
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
def test_output_blink_background():
    pin = Device.pin_factory.pin(4)
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
def test_output_blink_foreground():
    pin = Device.pin_factory.pin(4)
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

def test_output_blink_interrupt_on():
    pin = Device.pin_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        pin.assert_states([False, True, False])

def test_output_blink_interrupt_off():
    pin = Device.pin_factory.pin(4)
    with DigitalOutputDevice(4) as device:
        device.blink(0.1, 1)
        sleep(0.2)
        device.off() # should interrupt while off
        pin.assert_states([False, True, False])

def test_output_pwm_bad_initial_value():
    with pytest.raises(ValueError):
        PWMOutputDevice(2, initial_value=2)

def test_output_pwm_not_supported():
    with pytest.raises(AttributeError):
        PWMOutputDevice(2)

def test_output_pwm_states():
    pin = Device.pin_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.value = 0.1
        device.value = 0.2
        device.value = 0.0
        pin.assert_states([0.0, 0.1, 0.2, 0.0])

def test_output_pwm_read():
    pin = Device.pin_factory.pin(2)
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

def test_output_pwm_write():
    pin = Device.pin_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.on()
        device.off()
        pin.assert_states([False, True, False])

def test_output_pwm_toggle():
    pin = Device.pin_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.toggle()
        device.value = 0.5
        device.value = 0.1
        device.toggle()
        device.off()
        pin.assert_states([False, True, 0.5, 0.1, 0.9, False])

def test_output_pwm_active_high_read():
    pin = Device.pin_factory.pin(2)
    with PWMOutputDevice(2, active_high=False) as device:
        device.value = 0.1
        assert isclose(device.value, 0.1)
        assert isclose(pin.state, 0.9)
        device.frequency = None
        assert device.value

def test_output_pwm_bad_value():
    pin = Device.pin_factory.pin(2)
    with PWMOutputDevice(2) as device:
        with pytest.raises(ValueError):
            device.value = 2

def test_output_pwm_write_closed():
    pin = Device.pin_factory.pin(2)
    with PWMOutputDevice(2) as device:
        device.close()
        with pytest.raises(GPIODeviceClosed):
            device.on()

def test_output_pwm_write_silly():
    pin = Device.pin_factory.pin(2)
    with PWMOutputDevice(2) as device:
        pin.function = 'input'
        with pytest.raises(AttributeError):
            device.off()

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_output_pwm_blink_background():
    pin = Device.pin_factory.pin(4)
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
def test_output_pwm_blink_foreground():
    pin = Device.pin_factory.pin(4)
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
def test_output_pwm_fade_background():
    pin = Device.pin_factory.pin(4)
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
def test_output_pwm_fade_foreground():
    pin = Device.pin_factory.pin(4)
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
def test_output_pwm_pulse_background():
    pin = Device.pin_factory.pin(4)
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
def test_output_pwm_pulse_foreground():
    pin = Device.pin_factory.pin(4)
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

def test_output_pwm_blink_interrupt():
    pin = Device.pin_factory.pin(4)
    with PWMOutputDevice(4) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        pin.assert_states([0, 1, 0])

def test_rgbled_missing_pins():
    with pytest.raises(ValueError):
        RGBLED()

def test_rgbled_initial_value():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, initial_value=(0.1, 0.2, 0)) as device:
        assert r.frequency
        assert g.frequency
        assert b.frequency
        assert isclose(r.state, 0.1)
        assert isclose(g.state, 0.2)
        assert isclose(b.state, 0.0)

def test_rgbled_initial_value_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False, initial_value=(0, 1, 1)) as device:
        assert r.state == 0
        assert g.state == 1
        assert b.state == 1

def test_rgbled_initial_bad_value():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with pytest.raises(ValueError):
        RGBLED(1, 2, 3, initial_value=(0.1, 0.2, 1.2))

def test_rgbled_initial_bad_value_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with pytest.raises(ValueError):
        RGBLED(1, 2, 3, pwm=False, initial_value=(0.1, 0.2, 0))

def test_rgbled_value():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3) as device:
        assert isinstance(device._leds[0], PWMLED)
        assert isinstance(device._leds[1], PWMLED)
        assert isinstance(device._leds[2], PWMLED)
        assert not device.is_active
        assert device.value == (0, 0, 0)
        device.on()
        assert device.is_active
        assert device.value == (1, 1, 1)
        device.off()
        assert not device.is_active
        assert device.value == (0, 0, 0)
        device.value = (0.5, 0.5, 0.5)
        assert device.is_active
        assert device.value == (0.5, 0.5, 0.5)

def test_rgbled_value_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        assert isinstance(device._leds[0], LED)
        assert isinstance(device._leds[1], LED)
        assert isinstance(device._leds[2], LED)
        assert not device.is_active
        assert device.value == (0, 0, 0)
        device.on()
        assert device.is_active
        assert device.value == (1, 1, 1)
        device.off()
        assert not device.is_active
        assert device.value == (0, 0, 0)

def test_rgbled_bad_value():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3) as device:
        with pytest.raises(ValueError):
            device.value = (2, 0, 0)
    with RGBLED(1, 2, 3) as device:
        with pytest.raises(ValueError):
            device.value = (0, -1, 0)

def test_rgbled_bad_value_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = (2, 0, 0)
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = (0, -1, 0)
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = (0.5, 0, 0)
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = (0, 0.5, 0)
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = (0, 0, 0.5)

def test_rgbled_toggle():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3) as device:
        assert not device.is_active
        assert device.value == (0, 0, 0)
        device.toggle()
        assert device.is_active
        assert device.value == (1, 1, 1)
        device.toggle()
        assert not device.is_active
        assert device.value == (0, 0, 0)

def test_rgbled_toggle_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        assert not device.is_active
        assert device.value == (0, 0, 0)
        device.toggle()
        assert device.is_active
        assert device.value == (1, 1, 1)
        device.toggle()
        assert not device.is_active
        assert device.value == (0, 0, 0)

def test_rgbled_blink_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.blink(fade_in_time=1)
        with pytest.raises(ValueError):
            device.blink(fade_out_time=1)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_blink_background():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
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
def test_rgbled_blink_background_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as device:
        start = time()
        device.blink(0.1, 0.1, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
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
def test_rgbled_blink_foreground():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.blink(0.1, 0.1, n=2, background=False)
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
def test_rgbled_blink_foreground_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as device:
        start = time()
        device.blink(0.1, 0.1, n=2, background=False)
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
def test_rgbled_fade_background():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.blink(0, 0, 0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
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

def test_rgbled_fade_background_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.blink(0, 0, 0.2, 0, n=2)
        with pytest.raises(ValueError):
            device.blink(0, 0, 0, 0.2, n=2)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_fade_foreground():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.blink(0, 0, 0.2, 0.2, n=2, background=False)
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

def test_rgbled_fade_foreground_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.blink(0, 0, 0.2, 0.2, n=2, background=False)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_pulse_background():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.pulse(0.2, 0.2, n=2)
        assert isclose(time() - start, 0, abs_tol=0.05)
        device._blink_thread.join()
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

def test_rgbled_pulse_background_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.pulse(0.2, 0.2, n=2)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_rgbled_pulse_foreground():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        start = time()
        device.pulse(0.2, 0.2, n=2, background=False)
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

def test_rgbled_pulse_foreground_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        with pytest.raises(ValueError):
            device.pulse(0.2, 0.2, n=2, background=False)

def test_rgbled_blink_interrupt():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        r.assert_states([0, 1, 0])
        g.assert_states([0, 1, 0])
        b.assert_states([0, 1, 0])

def test_rgbled_blink_interrupt_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (4, 5, 6))
    with RGBLED(1, 2, 3, pwm=False) as device:
        device.blink(1, 0.1)
        sleep(0.2)
        device.off() # should interrupt while on
        r.assert_states([0, 1, 0])
        g.assert_states([0, 1, 0])
        b.assert_states([0, 1, 0])

def test_rgbled_close():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3) as device:
        assert not device.closed
        device.close()
        assert device.closed
        device.close()
        assert device.closed

def test_rgbled_close_nonpwm():
    r, g, b = (Device.pin_factory.pin(i) for i in (1, 2, 3))
    with RGBLED(1, 2, 3, pwm=False) as device:
        assert not device.closed
        device.close()
        assert device.closed
        device.close()
        assert device.closed

def test_motor_missing_pins():
    with pytest.raises(ValueError):
        Motor()

def test_motor_pins():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2) as device:
        assert device.forward_device.pin is f
        assert isinstance(device.forward_device, PWMOutputDevice)
        assert device.backward_device.pin is b
        assert isinstance(device.backward_device, PWMOutputDevice)

def test_motor_pins_nonpwm():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2, pwm=False) as device:
        assert device.forward_device.pin is f
        assert isinstance(device.forward_device, DigitalOutputDevice)
        assert device.backward_device.pin is b
        assert isinstance(device.backward_device, DigitalOutputDevice)

def test_motor_close():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2) as device:
        device.close()
        assert device.closed
        assert device.forward_device.pin is None
        assert device.backward_device.pin is None
        device.close()
        assert device.closed

def test_motor_close_nonpwm():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2, pwm=False) as device:
        device.close()
        assert device.closed
        assert device.forward_device.pin is None
        assert device.backward_device.pin is None

def test_motor_value():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2) as device:
        device.value = -1
        assert device.is_active
        assert device.value == -1
        assert b.state == 1 and f.state == 0
        device.value = 1
        assert device.is_active
        assert device.value == 1
        assert b.state == 0 and f.state == 1
        device.value = 0.5
        assert device.is_active
        assert device.value == 0.5
        assert b.state == 0 and f.state == 0.5
        device.value = -0.5
        assert device.is_active
        assert device.value == -0.5
        assert b.state == 0.5 and f.state == 0
        device.value = 0
        assert not device.is_active
        assert not device.value
        assert b.state == 0 and f.state == 0

def test_motor_value_nonpwm():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2, pwm=False) as device:
        device.value = -1
        assert device.is_active
        assert device.value == -1
        assert b.state == 1 and f.state == 0
        device.value = 1
        assert device.is_active
        assert device.value == 1
        assert b.state == 0 and f.state == 1
        device.value = 0
        assert not device.is_active
        assert not device.value
        assert b.state == 0 and f.state == 0

def test_motor_bad_value():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2) as device:
        with pytest.raises(ValueError):
            device.value = -2
        with pytest.raises(ValueError):
            device.value = 2
        with pytest.raises(ValueError):
            device.forward(2)
        with pytest.raises(ValueError):
            device.backward(2)
        with pytest.raises(ValueError):
            device.forward(-1)
        with pytest.raises(ValueError):
            device.backward(-1)

def test_motor_bad_value_nonpwm():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = -2
        with pytest.raises(ValueError):
            device.value = 2
        with pytest.raises(ValueError):
            device.value = 0.5
        with pytest.raises(ValueError):
            device.value = -0.5
        with pytest.raises(ValueError):
            device.forward(0.5)
        with pytest.raises(ValueError):
            device.backward(0.5)

def test_motor_reverse():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2) as device:
        device.forward()
        assert device.value == 1
        assert b.state == 0 and f.state == 1
        device.reverse()
        assert device.value == -1
        assert b.state == 1 and f.state == 0
        device.backward(0.5)
        assert device.value == -0.5
        assert b.state == 0.5 and f.state == 0
        device.reverse()
        assert device.value == 0.5
        assert b.state == 0 and f.state == 0.5

def test_motor_reverse_nonpwm():
    f = Device.pin_factory.pin(1)
    b = Device.pin_factory.pin(2)
    with Motor(1, 2, pwm=False) as device:
        device.forward()
        assert device.value == 1
        assert b.state == 0 and f.state == 1
        device.reverse()
        assert device.value == -1
        assert b.state == 1 and f.state == 0

def test_phaseenable_motor_pins():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2) as device:
        assert device.phase_device.pin is p
        assert isinstance(device.phase_device, OutputDevice)
        assert device.enable_device.pin is e
        assert isinstance(device.enable_device, PWMOutputDevice)

def test_phaseenable_motor_pins_nonpwm():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as device:
        assert device.phase_device.pin is p
        assert isinstance(device.phase_device, OutputDevice)
        assert device.enable_device.pin is e
        assert isinstance(device.enable_device, DigitalOutputDevice)

def test_phaseenable_motor_close():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2) as device:
        device.close()
        assert device.closed
        assert device.phase_device.pin is None
        assert device.enable_device.pin is None
        device.close()
        assert device.closed

def test_phaseenable_motor_close_nonpwm():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as device:
        device.close()
        assert device.closed
        assert device.phase_device.pin is None
        assert device.enable_device.pin is None

def test_phaseenable_motor_value():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2) as device:
        device.value = -1
        assert device.is_active
        assert device.value == -1
        assert p.state == 1 and e.state == 1
        device.value = 1
        assert device.is_active
        assert device.value == 1
        assert p.state == 0 and e.state == 1
        device.value = 0.5
        assert device.is_active
        assert device.value == 0.5
        assert p.state == 0 and e.state == 0.5
        device.value = -0.5
        assert device.is_active
        assert device.value == -0.5
        assert p.state == 1 and e.state == 0.5
        device.value = 0
        assert not device.is_active
        assert not device.value
        assert e.state == 0

def test_phaseenable_motor_value_nonpwm():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as device:
        device.value = -1
        assert device.is_active
        assert device.value == -1
        assert p.state == 1 and e.state == 1
        device.value = 1
        assert device.is_active
        assert device.value == 1
        assert p.state == 0 and e.state == 1
        device.value = 0
        assert not device.is_active
        assert not device.value
        assert e.state == 0

def test_phaseenable_motor_bad_value():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2) as device:
        with pytest.raises(ValueError):
            device.value = -2
        with pytest.raises(ValueError):
            device.value = 2
        with pytest.raises(ValueError):
            device.forward(2)
        with pytest.raises(ValueError):
            device.backward(2)

def test_phaseenable_motor_bad_value_nonpwm():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as device:
        with pytest.raises(ValueError):
            device.value = -2
        with pytest.raises(ValueError):
            device.value = 2
        with pytest.raises(ValueError):
            device.value = 0.5
        with pytest.raises(ValueError):
            device.value = -0.5

def test_phaseenable_motor_reverse():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2) as device:
        device.forward()
        assert device.value == 1
        assert p.state == 0 and e.state == 1
        device.reverse()
        assert device.value == -1
        assert p.state == 1 and e.state == 1
        device.backward(0.5)
        assert device.value == -0.5
        assert p.state == 1 and e.state == 0.5
        device.reverse()
        assert device.value == 0.5
        assert p.state == 0 and e.state == 0.5

def test_phaseenable_motor_reverse_nonpwm():
    p = Device.pin_factory.pin(1)
    e = Device.pin_factory.pin(2)
    with PhaseEnableMotor(1, 2, pwm=False) as device:
        device.forward()
        assert device.value == 1
        assert p.state == 0 and e.state == 1
        device.reverse()
        assert device.value == -1
        assert p.state == 1 and e.state == 1

def test_servo_pins():
    p = Device.pin_factory.pin(1)
    with Servo(1) as device:
        assert device.pwm_device.pin is p
        assert isinstance(device.pwm_device, PWMOutputDevice)

def test_servo_bad_value():
    p = Device.pin_factory.pin(1)
    with pytest.raises(ValueError):
        Servo(1, initial_value=2)
    with pytest.raises(ValueError):
        Servo(1, min_pulse_width=30/1000)
    with pytest.raises(ValueError):
        Servo(1, max_pulse_width=30/1000)

def test_servo_pins_nonpwm():
    p = Device.pin_factory.pin(2)
    with pytest.raises(PinPWMUnsupported):
        Servo(1)

def test_servo_close():
    p = Device.pin_factory.pin(2)
    with Servo(2) as device:
        device.close()
        assert device.closed
        assert device.pwm_device.pin is None
        device.close()
        assert device.closed

def test_servo_pulse_width():
    p = Device.pin_factory.pin(2)
    with Servo(2, min_pulse_width=5/10000, max_pulse_width=25/10000) as device:
        assert isclose(device.min_pulse_width, 5/10000)
        assert isclose(device.max_pulse_width, 25/10000)
        assert isclose(device.frame_width, 20/1000)
        assert isclose(device.pulse_width, 15/10000)
        device.value = -1
        assert isclose(device.pulse_width, 5/10000)
        device.value = 1
        assert isclose(device.pulse_width, 25/10000)
        device.value = None
        assert device.pulse_width is None

def test_servo_initial_values():
    p = Device.pin_factory.pin(2)
    with Servo(2) as device:
        assert device.value == 0
    with Servo(2, initial_value=-1) as device:
        assert device.is_active
        assert device.value == -1
        assert isclose(p.state, 0.05)
    with Servo(2, initial_value=0) as device:
        assert device.is_active
        assert device.value == 0
        assert isclose(p.state, 0.075)
    with Servo(2, initial_value=1) as device:
        assert device.is_active
        assert device.value == 1
        assert isclose(p.state, 0.1)
    with Servo(2, initial_value=None) as device:
        assert not device.is_active
        assert device.value is None

def test_servo_values():
    p = Device.pin_factory.pin(1)
    with Servo(1) as device:
        device.min()
        assert device.is_active
        assert device.value == -1
        assert isclose(p.state, 0.05)
        device.max()
        assert device.is_active
        assert device.value == 1
        assert isclose(p.state, 0.1)
        device.mid()
        assert device.is_active
        assert device.value == 0.0
        assert isclose(p.state, 0.075)
        device.value = 0.5
        assert device.is_active
        assert device.value == 0.5
        assert isclose(p.state, 0.0875)
        device.detach()
        assert not device.is_active
        assert device.value is None
        device.value = 0
        assert device.value == 0
        device.value = None
        assert device.value is None

def test_angular_servo_range():
    p = Device.pin_factory.pin(1)
    with AngularServo(1, initial_angle=15, min_angle=0, max_angle=90) as device:
        assert device.min_angle == 0
        assert device.max_angle == 90

def test_angular_servo_initial_angles():
    p = Device.pin_factory.pin(1)
    with AngularServo(1) as device:
        assert device.angle == 0
    with AngularServo(1, initial_angle=-90) as device:
        assert device.angle == -90
        assert isclose(device.value, -1)
    with AngularServo(1, initial_angle=0) as device:
        assert device.angle == 0
        assert isclose(device.value, 0)
    with AngularServo(1, initial_angle=90) as device:
        assert device.angle == 90
        assert isclose(device.value, 1)
    with AngularServo(1, initial_angle=None) as device:
        assert device.angle is None

def test_angular_servo_angles():
    p = Device.pin_factory.pin(1)
    with AngularServo(1) as device:
        device.angle = 0
        assert device.angle == 0
        assert isclose(device.value, 0)
        device.max()
        assert device.angle == 90
        assert isclose(device.value, 1)
        device.min()
        assert device.angle == -90
        assert isclose(device.value, -1)
        device.detach()
        assert device.angle is None
    with AngularServo(1, initial_angle=15, min_angle=0, max_angle=90) as device:
        assert device.angle == 15
        assert isclose(device.value, -2/3)
        device.angle = 0
        assert device.angle == 0
        assert isclose(device.value, -1)
        device.angle = 90
        assert device.angle == 90
        assert isclose(device.value, 1)
        device.angle = None
        assert device.angle is None
    with AngularServo(1, min_angle=45, max_angle=-45) as device:
        assert device.angle == 0
        assert isclose(device.value, 0)
        device.angle = -45
        assert device.angle == -45
        assert isclose(device.value, 1)
        device.angle = -15
        assert device.angle == -15
        assert isclose(device.value, 1/3)

