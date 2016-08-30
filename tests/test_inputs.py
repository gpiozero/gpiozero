from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import sys
import pytest
from threading import Event

from gpiozero.pins.mock import (
    MockPin,
    MockPulledUpPin,
    MockChargingPin,
    MockTriggerPin,
    )
from gpiozero import *


def teardown_function(function):
    MockPin.clear_pins()

def test_input_initial_values():
    pin = MockPin(2)
    with InputDevice(pin, pull_up=True) as device:
        assert pin.function == 'input'
        assert pin.pull == 'up'
        assert device.pull_up
        device.close()
        device = InputDevice(pin, pull_up=False)
        assert pin.pull == 'down'
        assert not device.pull_up

def test_input_is_active_low():
    pin = MockPin(2)
    with InputDevice(pin, pull_up=True) as device:
        pin.drive_high()
        assert not device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin MOCK2, pull_up=True, is_active=False>'
        pin.drive_low()
        assert device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin MOCK2, pull_up=True, is_active=True>'

def test_input_is_active_high():
    pin = MockPin(2)
    with InputDevice(pin, pull_up=False) as device:
        pin.drive_high()
        assert device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin MOCK2, pull_up=False, is_active=True>'
        pin.drive_low()
        assert not device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin MOCK2, pull_up=False, is_active=False>'

def test_input_pulled_up():
    pin = MockPulledUpPin(2)
    with pytest.raises(PinFixedPull):
        InputDevice(pin, pull_up=False)

def test_input_event_activated():
    event = Event()
    pin = MockPin(2)
    with DigitalInputDevice(pin) as device:
        device.when_activated = lambda: event.set()
        assert not event.is_set()
        pin.drive_high()
        assert event.is_set()

def test_input_event_deactivated():
    event = Event()
    pin = MockPin(2)
    with DigitalInputDevice(pin) as device:
        device.when_deactivated = lambda: event.set()
        assert not event.is_set()
        pin.drive_high()
        assert not event.is_set()
        pin.drive_low()
        assert event.is_set()

def test_input_wait_active():
    pin = MockPin(2)
    with DigitalInputDevice(pin) as device:
        pin.drive_high()
        assert device.wait_for_active(1)
        assert not device.wait_for_inactive(0)

def test_input_wait_inactive():
    pin = MockPin(2)
    with DigitalInputDevice(pin) as device:
        assert device.wait_for_inactive(1)
        assert not device.wait_for_active(0)

def test_input_smoothed_attrib():
    pin = MockPin(2)
    with SmoothedInputDevice(pin, threshold=0.5, queue_len=5, partial=False) as device:
        assert repr(device) == '<gpiozero.SmoothedInputDevice object on pin=MOCK2, pull_up=False>'
        assert device.threshold == 0.5
        assert device.queue_len == 5
        assert not device.partial
        device._queue.start()
        assert not device.is_active
        with pytest.raises(InputDeviceError):
            device.threshold = 1

def test_input_smoothed_values():
    pin = MockPin(2)
    with SmoothedInputDevice(pin) as device:
        device._queue.start()
        assert not device.is_active
        pin.drive_high()
        assert device.wait_for_active(1)
        pin.drive_low()
        assert device.wait_for_inactive(1)

def test_input_button():
    pin = MockPin(2)
    with Button(pin) as button:
        assert pin.pull == 'up'
        assert not button.is_pressed
        pin.drive_low()
        assert button.is_pressed
        assert button.wait_for_press(1)
        pin.drive_high()
        assert not button.is_pressed
        assert button.wait_for_release(1)

def test_input_line_sensor():
    pin = MockPin(2)
    with LineSensor(pin) as sensor:
        pin.drive_low() # logic is inverted for line sensor
        assert sensor.wait_for_line(1)
        assert sensor.line_detected
        pin.drive_high()
        assert sensor.wait_for_no_line(1)
        assert not sensor.line_detected

def test_input_motion_sensor():
    pin = MockPin(2)
    with MotionSensor(pin) as sensor:
        pin.drive_high()
        assert sensor.wait_for_motion(1)
        assert sensor.motion_detected
        pin.drive_low()
        assert sensor.wait_for_no_motion(1)
        assert not sensor.motion_detected

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_input_light_sensor():
    pin = MockChargingPin(2)
    with LightSensor(pin) as sensor:
        pin.charge_time = 0.1
        assert sensor.wait_for_dark(1)
        pin.charge_time = 0.0
        assert sensor.wait_for_light(1)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_input_distance_sensor():
    echo_pin = MockPin(2)
    trig_pin = MockTriggerPin(3)
    trig_pin.echo_pin = echo_pin
    trig_pin.echo_time = 0.02
    with pytest.raises(ValueError):
        DistanceSensor(echo_pin, trig_pin, max_distance=-1)
    # normal queue len is large (because the sensor is *really* jittery) but
    # we want quick tests and we've got precisely controlled pins :)
    with DistanceSensor(echo_pin, trig_pin, queue_len=5, max_distance=1) as sensor:
        assert sensor.max_distance == 1
        assert sensor.trigger is trig_pin
        assert sensor.echo is echo_pin
        assert sensor.wait_for_out_of_range(1)
        assert not sensor.in_range
        assert sensor.distance == 1.0 # should be waay before max-distance so this should work
        trig_pin.echo_time = 0.0
        assert sensor.wait_for_in_range(1)
        assert sensor.in_range
        assert sensor.distance < sensor.threshold_distance # depending on speed of machine, may not reach 0 here
        sensor.threshold_distance = 0.1
        assert sensor.threshold_distance == 0.1
        with pytest.raises(ValueError):
            sensor.max_distance = -1
        sensor.max_distance = 20
        assert sensor.max_distance == 20
        assert sensor.threshold_distance == 0.1

