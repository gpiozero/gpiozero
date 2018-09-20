from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from threading import Event

import pytest

from gpiozero.pins.mock import MockPWMPin, MockPin
from gpiozero import *


def teardown_function(function):
    Device.pin_factory.reset()


# Some rough tests to make sure our MockPin is up to snuff. This is just
# enough to get reasonable coverage but it's by no means comprehensive...

def test_mock_pin_init():
    with pytest.raises(ValueError):
        Device.pin_factory.pin(60)
    assert Device.pin_factory.pin(2).number == 2

def test_mock_pin_defaults():
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

def test_mock_pin_open_close():
    pin = Device.pin_factory.pin(2)
    pin.close()

def test_mock_pin_init_twice_same_pin():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(pin1.number)
    assert pin1 is pin2

def test_mock_pin_init_twice_different_pin():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(pin1.number+1)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

def test_mock_pwm_pin_defaults():
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

def test_mock_pwm_pin_open_close():
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin.close()

def test_mock_pwm_pin_init_twice_same_pin():
    pin1 = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin2 = Device.pin_factory.pin(pin1.number, pin_class=MockPWMPin)
    assert pin1 is pin2

def test_mock_pwm_pin_init_twice_different_pin():
    pin1 = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin2 = Device.pin_factory.pin(pin1.number + 1, pin_class=MockPWMPin)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

def test_mock_pin_init_twice_different_modes():
    pin1 = Device.pin_factory.pin(2, pin_class=MockPin)
    pin2 = Device.pin_factory.pin(pin1.number + 1, pin_class=MockPWMPin)
    assert pin1 != pin2
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin1.number, pin_class=MockPWMPin)
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin2.number, pin_class=MockPin)

def test_mock_pin_frequency_unsupported():
    pin = Device.pin_factory.pin(2)
    pin.frequency = None
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100

def test_mock_pin_frequency_supported():
    pin = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin.function = 'output'
    assert pin.frequency is None
    pin.frequency = 100
    pin.state = 0.5
    pin.frequency = None
    assert not pin.state

def test_mock_pin_pull():
    pin = Device.pin_factory.pin(4)
    pin.function = 'input'
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.state
    pin.pull = 'down'
    assert not pin.state
    pin.close()
    pin = Device.pin_factory.pin(2)
    pin.function = 'input'
    assert pin.pull == 'up'
    with pytest.raises(PinFixedPull):
        pin.pull = 'floating'

def test_mock_pin_state():
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

def test_mock_pwm_pin_state():
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

def test_mock_pin_edges():
    pin = Device.pin_factory.pin(2)
    assert pin.when_changed is None
    fired = Event()
    pin.function = 'input'
    pin.edges = 'both'
    assert pin.edges == 'both'
    pin.drive_low()
    assert not pin.state
    def changed():
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

