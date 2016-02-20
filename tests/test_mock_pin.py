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


# Some rough tests to make sure our MockPin is up to snuff. This is just
# enough to get reasonable coverage but it's by no means comprehensive...

def test_mock_pin_init():
    with pytest.raises(ValueError):
        MockPin(60)
    assert MockPin(2).number == 2

def test_mock_pin_frequency_unsupported():
    with pytest.raises(PinPWMUnsupported):
        pin = MockPin(3)
        pin.frequency = 100

def test_mock_pin_frequency_supported():
    pin = MockPWMPin(3)
    pin.function = 'output'
    assert pin.frequency is None
    pin.frequency = 100
    pin.state = 0.5
    pin.frequency = None
    assert not pin.state

def test_mock_pin_pull():
    pin = MockPin(4)
    pin.function = 'input'
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.state
    pin.pull = 'down'
    assert not pin.state

def test_mock_pin_edges():
    pin = MockPin(5)
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
    assert fired.wait(0)
    fired.clear()
    pin.edges = 'falling'
    pin.drive_low()
    assert not pin.state
    assert fired.wait(0)
    fired.clear()
    pin.drive_high()
    assert pin.state
    assert not fired.wait(0)
    assert pin.edges == 'falling'

