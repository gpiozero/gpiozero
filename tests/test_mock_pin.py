# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from threading import Event
from time import sleep

import pytest

from gpiozero import *
from gpiozero.pins.mock import *


def test_mock_pin_init(mock_factory):
    with pytest.raises(ValueError):
        Device.pin_factory.pin(60)
    assert Device.pin_factory.pin(2).info.name == 'GPIO2'


def test_mock_pin_defaults(mock_factory):
    pin = Device.pin_factory.pin(4)
    assert pin.bounce == None
    assert pin.edges == 'both'
    assert pin.frequency == None
    assert pin.function == 'input'
    assert pin.pull == 'floating'
    assert pin.state == 0
    assert pin.when_changed == None
    pin.close()
    pin = Device.pin_factory.pin(2)
    assert pin.pull == 'up'


def test_mock_pin_open_close(mock_factory):
    pin = Device.pin_factory.pin(2)
    pin.close()


def test_mock_pin_init_twice_same_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(pin1.info.name)
    assert pin1 is pin2


def test_mock_pin_init_twice_different_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    assert pin1 != pin2
    assert pin1.info.name == 'GPIO2'
    assert pin2.info.name == 'GPIO3'


def test_mock_pwm_pin_defaults(mock_factory):
    pin = Device.pin_factory.pin(4, pin_class=MockPWMPin)
    assert pin.bounce == None
    assert pin.edges == 'both'
    assert pin.frequency == None
    assert pin.function == 'input'
    assert pin.pull == 'floating'
    assert pin.state == 0
    assert pin.when_changed == None
    pin.close()
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    assert pin.pull == 'up'


def test_mock_pwm_pin_open_close(mock_factory):
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin.close()


def test_mock_pwm_pin_init_twice_same_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin2 = Device.pin_factory.pin(pin1.info.name, pin_class=MockPWMPin)
    assert pin1 is pin2


def test_mock_pwm_pin_init_twice_different_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin2 = Device.pin_factory.pin(3, pin_class=MockPWMPin)
    assert pin1 != pin2
    assert pin1.info.name == 'GPIO2'
    assert pin2.info.name == 'GPIO3'


def test_mock_pin_init_twice_different_modes(mock_factory):
    pin1 = Device.pin_factory.pin(2, pin_class=MockPin)
    pin2 = Device.pin_factory.pin(3, pin_class=MockPWMPin)
    assert pin1 != pin2
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin1.info.name, pin_class=MockPWMPin)
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin2.info.name, pin_class=MockPin)


def test_mock_pin_frequency_unsupported(mock_factory):
    pin = Device.pin_factory.pin(2)
    pin.frequency = None
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100


def test_mock_pin_frequency_supported(mock_factory):
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin.function = 'output'
    assert pin.frequency is None
    pin.frequency = 100
    pin.state = 0.5
    pin.frequency = None
    assert not pin.state


def test_mock_pin_pull(mock_factory):
    pin = Device.pin_factory.pin(4)
    pin.function = 'input'
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.state
    pin.pull = 'down'
    assert not pin.state
    with pytest.raises(PinInvalidPull):
        pin.pull = 'foo'
    pin.function = 'output'
    with pytest.raises(PinFixedPull):
        pin.pull = 'floating'
    pin.close()
    pin = Device.pin_factory.pin(2)
    pin.function = 'input'
    assert pin.pull == 'up'
    with pytest.raises(PinFixedPull):
        pin.pull = 'floating'


def test_mock_pin_state(mock_factory):
    pin = Device.pin_factory.pin(2)
    with pytest.raises(PinSetInput):
        pin.state = 1
    pin.function = 'output'
    pin.state = 1
    assert pin.state == 1
    pin.state = 0
    assert pin.state == 0
    pin.state = 0.5
    assert pin.state == 1


def test_mock_pin_connected_state(mock_factory):
    input_pin = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5, pin_class=MockConnectedPin, input_pin=input_pin)
    pin3 = Device.pin_factory.pin(6, pin_class=MockConnectedPin)
    input_pin.function = 'input'
    pin2.function = 'output'
    pin3.function = 'output'
    pin2.state = 0
    assert input_pin.state == 0
    pin2.state = 1
    assert input_pin.state == 1
    pin3.state = 0
    assert input_pin.state == 1
    pin3.state = 1
    assert input_pin.state == 1


def test_mock_pin_functions(mock_factory):
    pin = Device.pin_factory.pin(2)
    assert pin.function == 'input'
    pin.function = 'output'
    assert pin.function == 'output'
    pin.function = 'input'
    assert pin.function == 'input'
    with pytest.raises(ValueError):
        pin.function = 'foo'


def test_mock_pwm_pin_state(mock_factory):
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    with pytest.raises(PinSetInput):
        pin.state = 1
    pin.function = 'output'
    pin.state = 1
    assert pin.state == 1
    pin.state = 0
    assert pin.state == 0
    pin.state = 0.5
    assert pin.state == 0.5


def test_mock_pin_edges(mock_factory):
    pin = Device.pin_factory.pin(2)
    assert pin.when_changed is None
    fired = Event()
    pin.function = 'input'
    pin.edges = 'both'
    assert pin.edges == 'both'
    pin.drive_low()
    assert not pin.state
    def changed(ticks, state):
        fired.set()
    pin.when_changed = changed
    pin.drive_high()
    assert pin.state
    assert fired.is_set()
    fired.clear()
    pin.edges = 'falling'
    pin.drive_low()
    assert not pin.state
    assert fired.is_set()
    fired.clear()
    pin.drive_high()
    assert pin.state
    assert not fired.is_set()
    assert pin.edges == 'falling'


def test_mock_charging_pin(mock_factory):
    pin = Device.pin_factory.pin(4, pin_class=MockChargingPin, charge_time=1)
    pin.function = 'input'
    assert pin.state == 0
    pin.function = 'output'
    assert pin.state == 0
    pin.close()
    mock_factory.reset()
    pin = Device.pin_factory.pin(4, pin_class=MockChargingPin, charge_time=0.01)
    pin.function = 'input'
    sleep(0.1)
    assert pin.state == 1
    pin.function = 'output'
    pin.state = 0
    pin.function = 'output'
    assert pin.state == 0
    pin.function = 'input'
    sleep(0.1)
    assert pin.state == 1
