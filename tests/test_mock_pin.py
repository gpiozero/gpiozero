from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from threading import Event

import pytest

from gpiozero.pins.mock import MockPin, MockPWMPin
from gpiozero import *


def teardown_function(function):
    MockPin.clear_pins()

# Some rough tests to make sure our MockPin is up to snuff. This is just
# enough to get reasonable coverage but it's by no means comprehensive...

def test_mock_pin_init():
    with pytest.raises(TypeError):
        MockPin()
    with pytest.raises(ValueError):
        MockPin(60)
    assert MockPin(2).number == 2

def test_mock_pin_defaults():
    pin = MockPin(2)
    assert pin.bounce == None
    assert pin.edges == 'both'
    assert pin.frequency == None
    assert pin.function == 'input'
    assert pin.pull == 'floating'
    assert pin.state == 0
    assert pin.when_changed == None

def test_mock_pin_open_close():
    pin = MockPin(2)
    pin.close()

def test_mock_pin_init_twice_same_pin():
    pin1 = MockPin(2)
    pin2 = MockPin(pin1.number)
    assert pin1 is pin2

def test_mock_pin_init_twice_different_pin():
    pin1 = MockPin(2)
    pin2 = MockPin(pin1.number+1)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

def test_mock_pwm_pin_init():
    with pytest.raises(TypeError):
        MockPWMPin()
    with pytest.raises(ValueError):
        MockPWMPin(60)
    assert MockPWMPin(2).number == 2

def test_mock_pwm_pin_defaults():
    pin = MockPWMPin(2)
    assert pin.bounce == None
    assert pin.edges == 'both'
    assert pin.frequency == None
    assert pin.function == 'input'
    assert pin.pull == 'floating'
    assert pin.state == 0
    assert pin.when_changed == None

def test_mock_pwm_pin_open_close():
    pin = MockPWMPin(2)
    pin.close()

def test_mock_pwm_pin_init_twice_same_pin():
    pin1 = MockPWMPin(2)
    pin2 = MockPWMPin(pin1.number)
    assert pin1 is pin2

def test_mock_pwm_pin_init_twice_different_pin():
    pin1 = MockPWMPin(2)
    pin2 = MockPWMPin(pin1.number+1)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

def test_mock_pin_init_twice_different_modes():
    pin1 = MockPin(2)
    pin2 = MockPWMPin(pin1.number+1)
    assert pin1 != pin2
    with pytest.raises(ValueError):
        pin3 = MockPWMPin(pin1.number)
    with pytest.raises(ValueError):
        pin4 = MockPin(pin2.number)

def test_mock_pin_frequency_unsupported():
    pin = MockPin(2)
    pin.frequency = None
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100

def test_mock_pin_frequency_supported():
    pin = MockPWMPin(2)
    pin.function = 'output'
    assert pin.frequency is None
    pin.frequency = 100
    pin.state = 0.5
    pin.frequency = None
    assert not pin.state

def test_mock_pin_pull():
    pin = MockPin(2)
    pin.function = 'input'
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.state
    pin.pull = 'down'
    assert not pin.state

def test_mock_pin_state():
    pin = MockPin(2)
    with pytest.raises(PinSetInput):
        pin.state = 1
    pin.function = 'output'
    assert pin.state == 0
    pin.state = 1
    assert pin.state == 1
    pin.state = 0
    assert pin.state == 0
    pin.state = 0.5
    assert pin.state == 1

def test_mock_pwm_pin_state():
    pin = MockPWMPin(2)
    with pytest.raises(PinSetInput):
        pin.state = 1
    pin.function = 'output'
    assert pin.state == 0
    pin.state = 1
    assert pin.state == 1
    pin.state = 0
    assert pin.state == 0
    pin.state = 0.5
    assert pin.state == 0.5

def test_mock_pin_edges():
    pin = MockPin(2)
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

