from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest
import mock
from threading import Event

from gpiozero.pins.mock import MockPin, MockPulledUpPin, MockChargingPin
from gpiozero import *


def teardown_function(function):
    MockPin.clear_pins()

def test_input_initial_values():
    pin = MockPin(2)
    device = InputDevice(pin, pull_up=True)
    assert pin.function == 'input'
    assert pin.pull == 'up'
    assert device.pull_up
    device.close()
    device = InputDevice(pin, pull_up=False)
    assert pin.pull == 'down'
    assert not device.pull_up
    device.close()

def test_input_is_active():
    pin = MockPin(2)
    device = InputDevice(pin, pull_up=True)
    pin.drive_high()
    assert not device.is_active
    pin.drive_low()
    assert device.is_active

def test_input_pulled_up():
    pin = MockPulledUpPin(2)
    with pytest.raises(PinFixedPull):
        device = InputDevice(pin, pull_up=False)

def test_input_event_activated():
    event = Event()
    pin = MockPin(2)
    device = DigitalInputDevice(pin)
    device.when_activated = lambda: event.set()
    assert not event.wait(0)
    pin.drive_high()
    assert event.wait(0)

def test_input_event_deactivated():
    event = Event()
    pin = MockPin(2)
    device = DigitalInputDevice(pin)
    device.when_deactivated = lambda: event.set()
    assert not event.wait(0)
    pin.drive_high()
    assert not event.wait(0)
    pin.drive_low()
    assert event.wait(0)

def test_input_wait_active():
    pin = MockPin(2)
    device = DigitalInputDevice(pin)
    pin.drive_high()
    assert device.wait_for_active(1)
    assert not device.wait_for_inactive(0)

def test_input_wait_inactive():
    pin = MockPin(2)
    device = DigitalInputDevice(pin)
    assert device.wait_for_inactive(1)
    assert not device.wait_for_active(0)

def test_input_smoothed_attrib():
    pin = MockPin(2)
    device = SmoothedInputDevice(pin, threshold=0.5, queue_len=5, partial=False)
    assert device.threshold == 0.5
    assert device.queue_len == 5
    assert not device.partial
    device._queue.start()
    assert not device.is_active

def test_input_smoothed_silly():
    pin = MockPin(2)
    with pytest.raises(InputDeviceError):
        device = SmoothedInputDevice(pin, threshold=-1)
    device = SmoothedInputDevice(pin)
    del device._queue.stopping
    with pytest.raises(AttributeError):
        device.close()

def test_input_smoothed_values():
    pin = MockPin(2)
    device = SmoothedInputDevice(pin)
    device._queue.start()
    assert not device.is_active
    pin.drive_high()
    assert device.wait_for_active(1)
    pin.drive_low()
    assert device.wait_for_inactive(1)

def test_input_button():
    pin = MockPin(2)
    button = Button(pin)
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
    sensor = LineSensor(pin)
    pin.drive_low() # logic is inverted for line sensor
    assert sensor.wait_for_line(1)
    assert sensor.line_detected
    pin.drive_high()
    assert sensor.wait_for_no_line(1)
    assert not sensor.line_detected

def test_input_motion_sensor():
    pin = MockPin(2)
    sensor = MotionSensor(pin)
    pin.drive_high()
    assert sensor.wait_for_motion(1)
    assert sensor.motion_detected
    pin.drive_low()
    assert sensor.wait_for_no_motion(1)
    assert not sensor.motion_detected

@pytest.mark.skipif(True, reason='Freezes')
def test_input_light_sensor():
    pin = MockChargingPin(2)
    sensor = LightSensor(pin)
    pin.charge_time = 1
    assert not sensor.light_detected
    pin.charge_time = 0
    assert sensor.light_detected

