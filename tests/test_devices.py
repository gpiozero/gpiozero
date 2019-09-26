# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
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

import os
import warnings
from mock import patch
import pytest
import errno

from gpiozero import *
from gpiozero.pins.mock import MockFactory


file_not_found = IOError(errno.ENOENT, 'File not found')


def test_default_pin_factory_order():
    with patch('sys.path') as path, \
         patch('io.open') as io, \
         patch('os.environ.get') as get:
        # ensure no pin libraries can be imported
        path.return_value = []
        # ensure /proc/device-tree... is not found when trying native
        io.return_value.__enter__.side_effect = file_not_found
        # ensure pin factory not set in env var
        get.return_value = None
        with warnings.catch_warnings(record=True) as ws:
            warnings.resetwarnings()
            with pytest.raises(BadPinFactory):
                device = GPIODevice(2)
            assert len(ws) == 4
            assert all(w.category == PinFactoryFallback for w in ws)
            assert ws[0].message.args[0].startswith('Falling back from rpigpio:')
            assert ws[1].message.args[0].startswith('Falling back from rpio:')
            assert ws[2].message.args[0].startswith('Falling back from pigpio:')
            assert ws[3].message.args[0].startswith('Falling back from native:')

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
        warnings.resetwarnings()
        device = GPIODevice('GPIO37')
        assert len(w) == 1
        assert w[0].category == PinNonPhysical

def test_device_init(mock_factory):
    pin = mock_factory.pin(2)
    with GPIODevice(2) as device:
        assert repr(device).startswith('<gpiozero.GPIODevice object')
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
    # MockFactory defaults to a Pi 3B layout
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
        assert repr(device).startswith('<gpiozero.CompositeDevice object')
        assert len(device) == 2
        assert device[0].pin.number == 4
        assert device[1].pin.number == 5
        assert device.namedtuple._fields == ('device_0', 'device_1')

def test_composite_device_values(mock_factory):
    with CompositeDevice(InputDevice(4), InputDevice(5)) as device:
        assert repr(device) == '<gpiozero.CompositeDevice object containing 2 unnamed devices>'
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
        assert repr(device) == '<gpiozero.CompositeDevice object containing 2 devices: foo, bar>'
        assert device.namedtuple._fields == ('foo', 'bar')
        assert device.value == (0, 0)
        assert not device.is_active

def test_composite_device_some_named(mock_factory):
    with CompositeDevice(
            InputDevice(4),
            foobar=InputDevice(5),
            ) as device:
        assert repr(device) == '<gpiozero.CompositeDevice object containing 2 devices: foobar and 1 unnamed>'
        assert device.namedtuple._fields == ('device_0', 'foobar')
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
