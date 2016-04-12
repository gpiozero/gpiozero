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


def teardown_function(function):
    MockPin.clear_pins()

# TODO add more devices tests!

def test_device_no_pin():
    with pytest.raises(GPIOPinMissing):
        device = GPIODevice()

def test_device_init():
    pin = MockPin(2)
    with GPIODevice(pin) as device:
        assert not device.closed
        assert device.pin == pin

def test_device_init_twice_same_pin():
    pin = MockPin(2)
    with GPIODevice(pin) as device:
        with pytest.raises(GPIOPinInUse):
            device2 = GPIODevice(pin)

def test_device_init_twice_different_pin():
    pin = MockPin(2)
    pin2 = MockPin(3)
    with GPIODevice(pin) as device:
        with GPIODevice(pin2) as device2:
            pass

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
    device2.close()

def test_device_repr():
    pin = MockPin(2)
    with GPIODevice(pin) as device:
        assert repr(device) == '<gpiozero.GPIODevice object on pin %s, is_active=False>' % pin

def test_device_repr_after_close():
    pin = MockPin(2)
    device = GPIODevice(pin)
    device.close()
    assert repr(device) == '<gpiozero.GPIODevice object closed>'

def test_device_unknown_attr():
    pin = MockPin(2)
    with GPIODevice(pin) as device:
        with pytest.raises(AttributeError):
            device.foo = 1

def test_device_context_manager():
    pin = MockPin(2)
    with GPIODevice(pin) as device:
        assert not device.closed
    assert device.closed

def test_composite_device_sequence():
    with CompositeDevice(
            InputDevice(MockPin(2)),
            InputDevice(MockPin(3))
            ) as device:
        assert len(device) == 2
        assert device[0].pin.number == 2
        assert device[1].pin.number == 3
        assert device.namedtuple._fields == ('_0', '_1')

def test_composite_device_values():
    with CompositeDevice(
            InputDevice(MockPin(2)),
            InputDevice(MockPin(3))
            ) as device:
        assert device.value == (0, 0)
        assert not device.is_active
        device[0].pin.drive_high()
        assert device.value == (1, 0)
        assert device.is_active

def test_composite_device_named():
    with CompositeDevice(
            foo=InputDevice(MockPin(2)),
            bar=InputDevice(MockPin(3)),
            _order=('foo', 'bar')
            ) as device:
        assert device.namedtuple._fields == ('foo', 'bar')
        assert device.value == (0, 0)
        assert not device.is_active

def test_composite_device_bad_init():
    with pytest.raises(ValueError):
        CompositeDevice(foo=1, bar=2, _order=('foo',))
    with pytest.raises(ValueError):
        CompositeDevice(close=1)
    with pytest.raises(ValueError):
        CompositeDevice(2)
    with pytest.raises(ValueError):
        CompositeDevice(MockPin(2))

def test_composite_device_read_only():
    device = CompositeDevice(
        foo=InputDevice(MockPin(2)),
        bar=InputDevice(MockPin(3))
        )
    with pytest.raises(AttributeError):
        device.foo = 1

