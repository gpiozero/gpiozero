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
from functools import partial

from gpiozero.pins.mock import (
    MockPin,
    MockPulledUpPin,
    MockChargingPin,
    MockTriggerPin,
    )
from gpiozero import *
from gpiozero.rotary_encoder import TableValues
from mock import MagicMock

def teardown_function(function):
    MockPin.clear_pins()


def test_rotary_encoder_initialization():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b, pull_up=True) as encoder:
        assert not encoder.closed
        assert encoder.is_active

        assert encoder.pin_a.pin is pin_a
        assert encoder.pin_b.pin is pin_b

        assert encoder.pin_a.pull_up
        assert encoder.pin_b.pull_up

    assert encoder.closed
    assert not encoder.is_active

    with RotaryEncoder(pin_a, pin_b, pull_up=False) as encoder:
        assert not encoder.closed
        assert encoder.is_active

        assert encoder.pin_a.pin is pin_a
        assert encoder.pin_b.pin is pin_b

        assert not encoder.pin_a.pull_up
        assert not encoder.pin_b.pull_up
   
    assert encoder.closed
    assert not encoder.is_active

def test_rotary_encoder_close():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b, pull_up=True) as encoder:
        assert not encoder.closed
        assert encoder.is_active

        encoder.close()

        assert encoder.closed
        assert not encoder.is_active

        encoder = RotaryEncoder(pin_a, pin_b, pull_up=False)
        assert not encoder.closed
        assert encoder.is_active

def test_rotary_encoder_repr():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b, pull_up=True) as encoder:
        assert repr(encoder) == '<gpiozero.RotaryEncoder object on pin_a MOCK2, pin_b MOCK3, pull_up=True, is_active=True>'

def test_rotary_encoder_table_values():
    assert TableValues.calcule_index(True, False, False, False) == 8
    assert TableValues.calcule_index(False, True, False, False) == 4
    assert TableValues.calcule_index(False, False, True, False) == 2
    assert TableValues.calcule_index(False, False, False, True) == 1

    assert TableValues.calcule_index(True, True, True, True) == 15

def test_rotary_encoder_rotate_clockwise():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b) as encoder:
        pin_a.drive_low()
        pin_b.drive_high()

        encoder.when_rotated = MagicMock()

        pin_a.drive_high()

        encoder.when_rotated.assert_called_with(1)

def test_rotary_encoder_rotate_counter_clockwise():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b) as encoder:
        pin_a.drive_low()
        pin_b.drive_high()

        encoder.when_rotated = MagicMock()

        pin_b.drive_low()

        encoder.when_rotated.assert_called_with(-1)

def test_rotary_encoder_value_not_defined():
    pin_a = MockPin(2)
    pin_b = MockPin(3)

    with RotaryEncoder(pin_a, pin_b) as encoder:
        assert encoder.value is None

def test_rotary_encoder_with_button():
    pin_a = MockPin(2)
    pin_b = MockPin(3)
    pin_button = MockPin(4)

    with RotaryEncoderWithButton(pin_a, pin_b, pin_button, encoder_pull_up=True, button_pull_up=True) as encoder:
        assert not encoder.closed
        assert encoder.is_active

        assert encoder.rotary_encoder.pin_a.pin is pin_a
        assert encoder.rotary_encoder.pin_b.pin is pin_b
        assert encoder.button.pin is pin_button

        assert encoder.rotary_encoder.pin_a.pull_up
        assert encoder.rotary_encoder.pin_b.pull_up
        assert encoder.button.pull_up

    assert encoder.closed
    assert not encoder.is_active

    with RotaryEncoderWithButton(pin_a, pin_b, pin_button, encoder_pull_up=False, button_pull_up=False) as encoder:
        assert not encoder.closed
        assert encoder.is_active

        assert encoder.rotary_encoder.pin_a.pin is pin_a
        assert encoder.rotary_encoder.pin_b.pin is pin_b
        assert encoder.button.pin is pin_button

        assert not encoder.rotary_encoder.pin_a.pull_up
        assert not encoder.rotary_encoder.pin_b.pull_up
        assert not encoder.button.pull_up

    assert encoder.closed
    assert not encoder.is_active

def test_rotary_encoder_with_button_value():
    pin_a = MockPin(2)
    pin_b = MockPin(3)
    pin_button = MockPin(4)

    with RotaryEncoderWithButton(pin_a, pin_b, pin_button) as encoder:
        pin_button.drive_low()
        assert encoder.value is None

        pin_button.drive_high()
        assert encoder.value is None

def test_rotary_encoder_repr():
    pin_a = MockPin(2)
    pin_b = MockPin(3)
    pin_button = MockPin(4)

    with RotaryEncoderWithButton(pin_a, pin_b, pin_button) as encoder:
        assert repr(encoder) == '<gpiozero.RotaryEncoderWithButton object on pin_a MOCK2, pin_b MOCK3, button_pin MOCK4, encoder_pull_up=True, button_pull_up=True, is_active=True>'

