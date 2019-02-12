# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 Philippe Muller <philippe.muller@gmail.com>
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
import pytest
import warnings
from time import sleep
from threading import Event
from functools import partial

import mock

from gpiozero.pins.mock import MockChargingPin, MockTriggerPin
from gpiozero.threads import GPIOThread
from gpiozero import *



def test_input_initial_values(mock_factory):
    pin = mock_factory.pin(4)
    with InputDevice(4, pull_up=True) as device:
        assert repr(device).startswith('<gpiozero.InputDevice object')
        assert pin.function == 'input'
        assert pin.pull == 'up'
        assert device.pull_up
    with InputDevice(4, pull_up=False) as device:
        assert pin.pull == 'down'
        assert not device.pull_up

def test_input_is_active_low(mock_factory):
    pin = mock_factory.pin(2)
    with InputDevice(2, pull_up=True) as device:
        pin.drive_high()
        assert not device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin GPIO2, pull_up=True, is_active=False>'
        pin.drive_low()
        assert device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin GPIO2, pull_up=True, is_active=True>'

def test_input_is_active_high(mock_factory):
    pin = mock_factory.pin(4)
    with InputDevice(4, pull_up=False) as device:
        pin.drive_high()
        assert device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=False, is_active=True>'
        pin.drive_low()
        assert not device.is_active
        assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=False, is_active=False>'

def test_input_pulled_up(mock_factory):
    pin = mock_factory.pin(2)
    with pytest.raises(PinFixedPull):
        InputDevice(2, pull_up=False)

def test_input_is_active_low_externally_pulled_up(mock_factory):
    pin = mock_factory.pin(4)
    device = InputDevice(4, pull_up=None, active_state=False)
    pin.drive_high()
    assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=None, is_active=False>'
    assert not device.is_active
    pin.drive_low()
    assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=None, is_active=True>'
    assert device.is_active

def test_input_is_active_high_externally_pulled_down(mock_factory):
    pin = mock_factory.pin(4)
    device = InputDevice(4, pull_up=None, active_state=True)
    pin.drive_high()
    assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=None, is_active=True>'
    assert device.is_active
    pin.drive_low()
    assert repr(device) == '<gpiozero.InputDevice object on pin GPIO4, pull_up=None, is_active=False>'
    assert not device.is_active

def test_input_invalid_pull_up(mock_factory):
    with pytest.raises(PinInvalidState) as exc:
        InputDevice(4, pull_up=None)
    assert str(exc.value) == 'Pin 4 is defined as floating, but "active_state" is not defined'

def test_input_invalid_active_state(mock_factory):
    with pytest.raises(PinInvalidState) as exc:
        InputDevice(4, active_state=True)
    assert str(exc.value) == 'Pin 4 is not floating, but "active_state" is not None'

def test_input_event_activated(mock_factory):
    event = Event()
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as device:
        assert repr(device).startswith('<gpiozero.DigitalInputDevice object')
        device.when_activated = lambda: event.set()
        assert not event.is_set()
        pin.drive_high()
        assert event.is_set()

def test_input_event_deactivated(mock_factory):
    event = Event()
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as device:
        device.when_deactivated = lambda: event.set()
        assert not event.is_set()
        pin.drive_high()
        assert not event.is_set()
        pin.drive_low()
        assert event.is_set()

def test_input_activated_callback_warning(mock_factory):
    def foo(): pass

    with DigitalInputDevice(4) as device:
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            device.when_activated = foo()
            assert len(w) == 1
            assert w[0].category == CallbackSetToNone

    with DigitalInputDevice(4) as device:
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            device.when_deactivated = foo()
            assert len(w) == 1
            assert w[0].category == CallbackSetToNone

def test_input_partial_callback(mock_factory):
    event = Event()
    pin = mock_factory.pin(4)
    def foo(a, b):
        event.set()
        return a + b
    bar = partial(foo, 1)
    baz = partial(bar, 2)
    with DigitalInputDevice(4) as device:
        device.when_activated = baz
        assert not event.is_set()
        pin.drive_high()
        assert event.is_set()

def test_input_wait_active(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as device:
        pin.drive_high()
        assert device.wait_for_active(1)
        assert not device.wait_for_inactive(0)

def test_input_wait_inactive(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as device:
        assert device.wait_for_inactive(1)
        assert not device.wait_for_active(0)

def test_input_init_fail(mock_factory):
    with pytest.raises(ValueError):
        DigitalInputDevice(4, bounce_time='foo')
    with pytest.raises(ValueError):
        SmoothedInputDevice(4, threshold='foo')

def test_input_smoothed_attrib(mock_factory):
    pin = mock_factory.pin(4)
    with SmoothedInputDevice(4, threshold=0.5, queue_len=5, partial=False) as device:
        assert repr(device) == '<gpiozero.SmoothedInputDevice object on pin GPIO4, pull_up=False>'
        assert device.threshold == 0.5
        assert device.queue_len == 5
        assert not device.partial
        device._queue.start()
        assert not device.is_active
        with pytest.raises(InputDeviceError):
            device.threshold = 1
    with pytest.raises(BadQueueLen):
        SmoothedInputDevice(4, queue_len=-1)
    with pytest.raises(BadWaitTime):
        SmoothedInputDevice(4, sample_wait=-1)

def test_input_smoothed_values(mock_factory):
    pin = mock_factory.pin(4)
    with SmoothedInputDevice(4) as device:
        device._queue.start()
        assert not device.is_active
        pin.drive_high()
        assert device.wait_for_active(1)
        pin.drive_low()
        assert device.wait_for_inactive(1)

def test_input_button(mock_factory):
    pin = mock_factory.pin(2)
    with Button(2) as button:
        assert repr(button).startswith('<gpiozero.Button object')
        assert pin.pull == 'up'
        assert not button.is_pressed
        pin.drive_low()
        assert button.is_pressed
        assert button.wait_for_press(1)
        pin.drive_high()
        assert not button.is_pressed
        assert button.wait_for_release(1)

def test_input_button_hold(mock_factory):
    pin = mock_factory.pin(2)
    evt = Event()
    evt2 = Event()
    with Button(2) as button:
        with pytest.raises(ValueError):
            button.hold_time = -1
        button.hold_time = 0.1
        assert button.hold_time == 0.1
        assert not button.hold_repeat
        assert button.when_held is None
        button.when_held = evt.set
        assert button.when_held is not None
        pin.drive_low()
        assert evt.wait(1)
        assert button.is_held
        assert button.held_time >= 0.0
        pin.drive_high()
        evt.clear()
        assert button.held_time is None
        assert not button.is_held
        button.hold_repeat = True
        pin.drive_low()
        assert evt.wait(1)
        evt.clear()
        assert evt.wait(1)
        pin.drive_high()
        evt.clear()
        assert not evt.wait(0.1)

def test_input_line_sensor(mock_factory):
    pin = mock_factory.pin(4)
    with LineSensor(4) as sensor:
        assert repr(sensor).startswith('<gpiozero.LineSensor object')
        pin.drive_low()  # logic is inverted for line sensor
        assert sensor.wait_for_line(1)
        assert sensor.line_detected
        pin.drive_high()
        assert sensor.wait_for_no_line(1)
        assert not sensor.line_detected

def test_input_motion_sensor(mock_factory):
    pin = mock_factory.pin(4)
    with MotionSensor(4) as sensor:
        assert repr(sensor).startswith('<gpiozero.MotionSensor object')
        pin.drive_high()
        assert sensor.wait_for_motion(1)
        assert sensor.motion_detected
        pin.drive_low()
        assert sensor.wait_for_no_motion(1)
        assert not sensor.motion_detected

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_input_light_sensor(mock_factory):
    pin = mock_factory.pin(4, pin_class=MockChargingPin)
    assert isinstance(pin, MockChargingPin)
    with LightSensor(4) as sensor:
        assert repr(sensor).startswith('<gpiozero.LightSensor object')
        pin.charge_time = 0.1
        assert sensor.wait_for_dark(1)
        pin.charge_time = 0.0
        assert sensor.wait_for_light(1)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_input_distance_sensor(mock_factory):
    echo_pin = mock_factory.pin(4)
    trig_pin = mock_factory.pin(5, pin_class=MockTriggerPin,
                                echo_pin=echo_pin, echo_time=0.02)
    with pytest.raises(ValueError):
        DistanceSensor(4, 5, max_distance=-1)
    # normal queue len is large (because the sensor is *really* jittery) but
    # we want quick tests and we've got precisely controlled pins :)
    with DistanceSensor(4, 5, queue_len=5, max_distance=1) as sensor:
        assert repr(sensor).startswith('<gpiozero.DistanceSensor object')
        assert sensor.max_distance == 1
        assert sensor.trigger is trig_pin
        assert sensor.echo is echo_pin
        assert sensor.wait_for_out_of_range(1)
        assert not sensor.in_range
        # should be waay before max-distance so this should work
        assert sensor.distance == 1.0
        trig_pin.echo_time = 0.0
        assert sensor.wait_for_in_range(1)
        assert sensor.in_range
        # depending on speed of machine, may not reach 0 here
        assert sensor.distance < sensor.threshold_distance
        sensor.threshold_distance = 0.1
        assert sensor.threshold_distance == 0.1
        with pytest.raises(ValueError):
            sensor.max_distance = -1
        sensor.max_distance = 20
        assert sensor.max_distance == 20
        assert sensor.threshold_distance == 0.1

def test_input_distance_sensor_edge_cases(mock_factory):
    echo_pin = mock_factory.pin(4)
    trig_pin = mock_factory.pin(5)  # note: normal pin
    with warnings.catch_warnings(record=True) as w:
        warnings.resetwarnings()
        with DistanceSensor(4, 5, queue_len=5, max_distance=1, partial=True) as sensor:
            # Test we get a warning about the echo pin being set high
            echo_pin.drive_high()
            sleep(0.5)
            assert sensor.value == 0
            # Test we get a warning about receiving no echo
            echo_pin.drive_low()
            sleep(0.5)
        for rec in w:
            if str(rec.message) == 'echo pin set high':
                break
        else:
            assert False
        for rec in w:
            if str(rec.message) == 'no echo received':
                break
        else:
            assert False
