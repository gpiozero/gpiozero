from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest

from gpiozero.pins.mock import MockPin
from gpiozero import *


# TODO add more devices tests!

def test_device_no_pin():
    with pytest.raises(GPIOPinMissing):
        device = GPIODevice()

def test_device_init():
    pin = MockPin(2)
    device = GPIODevice(pin)
    assert not device.closed
    assert device.pin == pin

def test_device_init_twice_same_pin():
    pin = MockPin(2)
    device = GPIODevice(pin)
    with pytest.raises(GPIOPinInUse):
        device2 = GPIODevice(pin)

def test_device_init_twice_different_pin():
    pin = MockPin(2)
    device = GPIODevice(pin)
    pin2 = MockPin(3)
    device2 = GPIODevice(pin2)

def test_device_close():
    pin = MockPin(2)
    device = GPIODevice(pin)
    device.close()
    assert device.closed
    assert device.pin is None

def test_device_reopen_same_pin():
    pin = MockPin(2)
    device = GPIODevice(pin)
    device.close()
    device2 = GPIODevice(pin)
    assert not device2.closed
    assert device2.pin == pin
    assert device.closed
    assert device.pin is None

def test_device_repr():
    pin = MockPin(2)
    device = GPIODevice(pin)
    assert repr(device) == '<gpiozero.GPIODevice object on pin %s, is_active=False>' % pin

def test_device_repr_after_close():
    pin = MockPin(2)
    device = GPIODevice(pin)
    device.close()
    assert repr(device) == '<gpiozero.GPIODevice object closed>'

