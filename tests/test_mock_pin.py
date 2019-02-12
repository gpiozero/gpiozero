# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
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


from threading import Event

import pytest

from gpiozero.pins.mock import MockPWMPin, MockPin
from gpiozero import *


def test_mock_pin_init(mock_factory):
    with pytest.raises(ValueError):
        Device.pin_factory.pin(60)
    assert Device.pin_factory.pin(2).number == 2

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
    pin2 = Device.pin_factory.pin(pin1.number)
    assert pin1 is pin2

def test_mock_pin_init_twice_different_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(pin1.number+1)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

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
    pin2 = Device.pin_factory.pin(pin1.number, pin_class=MockPWMPin)
    assert pin1 is pin2

def test_mock_pwm_pin_init_twice_different_pin(mock_factory):
    pin1 = Device.pin_factory.pin(2, pin_class=MockPWMPin)
    pin2 = Device.pin_factory.pin(pin1.number + 1, pin_class=MockPWMPin)
    assert pin1 != pin2
    assert pin1.number == 2
    assert pin2.number == pin1.number+1

def test_mock_pin_init_twice_different_modes(mock_factory):
    pin1 = Device.pin_factory.pin(2, pin_class=MockPin)
    pin2 = Device.pin_factory.pin(pin1.number + 1, pin_class=MockPWMPin)
    assert pin1 != pin2
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin1.number, pin_class=MockPWMPin)
    with pytest.raises(ValueError):
        Device.pin_factory.pin(pin2.number, pin_class=MockPin)

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

