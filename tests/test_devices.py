from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import os
import warnings

import mock
import pytest

from gpiozero import *
from gpiozero.pins.mock import MockFactory


def test_device_bad_pin(mock_factory):
    with pytest.raises(GPIOPinMissing):
        device = GPIODevice()
    with pytest.raises(PinInvalidPin):
        device = GPIODevice(60)
    with pytest.raises(PinInvalidPin):
        device = GPIODevice('BCM60')
    with pytest.raises(PinInvalidPin):
        device = GPIODevice('WPI32')
    with pytest.raises(PinInvalidPin):
        device = GPIODevice(b'P2:2')
    with pytest.raises(PinInvalidPin):
        device = GPIODevice('J8:42')
    with pytest.raises(PinInvalidPin):
        device = GPIODevice('J8:1')
    with pytest.raises(PinInvalidPin):
        device = GPIODevice('foo')

def test_device_non_physical(mock_factory):
    with warnings.catch_warnings(record=True) as w:
        device = GPIODevice('GPIO37')
        assert len(w) == 1
        assert w[0].category == PinNonPhysical

def test_device_init(mock_factory):
    pin = mock_factory.pin(2)
    with GPIODevice(2) as device:
        assert not device.closed
        assert device.pin is pin
    with pytest.raises(TypeError):
        GPIODevice(2, foo='bar')

def test_device_init_twice_same_pin(mock_factory):
    with GPIODevice(2) as device:
        with pytest.raises(GPIOPinInUse):
            GPIODevice(2)

def test_device_init_twice_same_pin_different_spec(mock_factory):
    with GPIODevice(2) as device:
        with pytest.raises(GPIOPinInUse):
            GPIODevice("BOARD3")

def test_device_init_twice_different_pin(mock_factory):
    with GPIODevice(2) as device:
        with GPIODevice(3) as device2:
            pass

def test_device_close(mock_factory):
    device = GPIODevice(2)
    # Don't use "with" here; we're testing close explicitly
    device.close()
    assert device.closed
    assert device.pin is None

def test_device_reopen_same_pin(mock_factory):
    pin = mock_factory.pin(2)
    with GPIODevice(2) as device:
        pass
    with GPIODevice(2) as device2:
        assert not device2.closed
        assert device2.pin is pin
        assert device.closed
        assert device.pin is None

def test_device_pin_parsing(mock_factory):
    # MockFactory defaults to a Pi 2B layout
    pin = mock_factory.pin(2)
    with GPIODevice('GPIO2') as device:
        assert device.pin is pin
    with GPIODevice('BCM2') as device:
        assert device.pin is pin
    with GPIODevice('WPI8') as device:
        assert device.pin is pin
    with GPIODevice('BOARD3') as device:
        assert device.pin is pin
    with GPIODevice('J8:3') as device:
        assert device.pin is pin

def test_device_repr(mock_factory):
    with GPIODevice(4) as device:
        assert repr(device) == (
            '<gpiozero.GPIODevice object on pin %s, '
            'is_active=False>' % device.pin)

def test_device_repr_after_close(mock_factory):
    with GPIODevice(2) as device:
        pass
    assert repr(device) == '<gpiozero.GPIODevice object closed>'

def test_device_unknown_attr(mock_factory):
    with GPIODevice(2) as device:
        with pytest.raises(AttributeError):
            device.foo = 1

def test_device_broken_attr(mock_factory):
    with GPIODevice(2) as device:
        del device._active_state
        with pytest.raises(AttributeError):
            device.value

def test_device_context_manager(mock_factory):
    with GPIODevice(2) as device:
        assert not device.closed
    assert device.closed

def test_composite_device_sequence(mock_factory):
    with CompositeDevice(InputDevice(4), InputDevice(5)) as device:
        assert len(device) == 2
        assert device[0].pin.number == 4
        assert device[1].pin.number == 5
        assert device.namedtuple._fields == ('device_0', 'device_1')

def test_composite_device_values(mock_factory):
    with CompositeDevice(InputDevice(4), InputDevice(5)) as device:
        assert device.value == (0, 0)
        assert not device.is_active
        device[0].pin.drive_high()
        assert device.value == (1, 0)
        assert device.is_active

def test_composite_device_named(mock_factory):
    with CompositeDevice(
            foo=InputDevice(4),
            bar=InputDevice(5),
            _order=('foo', 'bar')
            ) as device:
        assert device.namedtuple._fields == ('foo', 'bar')
        assert device.value == (0, 0)
        assert not device.is_active

def test_composite_device_bad_init(mock_factory):
    with pytest.raises(ValueError):
        CompositeDevice(foo=1, bar=2, _order=('foo',))
    with pytest.raises(ValueError):
        CompositeDevice(close=1)
    with pytest.raises(ValueError):
        CompositeDevice(2)
    with pytest.raises(ValueError):
        CompositeDevice(mock_factory.pin(2))

def test_composite_device_read_only(mock_factory):
    with CompositeDevice(foo=InputDevice(4), bar=InputDevice(5)) as device:
        with pytest.raises(AttributeError):
            device.foo = 1

def test_shutdown(mock_factory):
    from gpiozero.devices import _shutdown
    ds = DistanceSensor(17, 19)
    f = Device.pin_factory
    _shutdown()
    assert ds.closed
    assert not f.pins
    assert Device.pin_factory is None
    # Shutdown must be idempotent
    _shutdown()
