# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2019 Dave Jones <dave@waveform.org.uk>
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


import gc
import sys
from time import sleep
from threading import Event

import pytest

from gpiozero import *


def test_source_delay(mock_factory):
    with OutputDevice(2) as device:
        device.source_delay = 1
        assert device.source_delay == 1
        device.source_delay = 0.1
        assert device.source_delay == 0.1
        with pytest.raises(ValueError):
            device.source_delay = -1


def test_source(mock_factory):
    pin = mock_factory.pin(4)
    with InputDevice(4) as in_dev, OutputDevice(3) as out_dev:
        assert out_dev.source is None
        out_dev.source = in_dev.values
        assert out_dev.source is not None
        assert out_dev.value == 0
        pin.drive_high()
        # Give the output device some time to read the input device state
        sleep(0.1)
        assert out_dev.value == 1


def test_active_time(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as dev:
        assert dev.active_time is None
        assert dev.inactive_time >= 0.0
        pin.drive_high()
        sleep(0.1)
        assert dev.active_time >= 0.1
        assert dev.inactive_time is None
        pin.drive_low()
        sleep(0.1)
        assert dev.active_time is None
        assert dev.inactive_time >= 0.1


def test_basic_callbacks(mock_factory):
    pin = mock_factory.pin(4)
    evt = Event()
    with DigitalInputDevice(4) as dev:
        dev.when_activated = evt.set
        assert dev.when_activated is not None
        pin.drive_high()
        assert evt.wait(0.1)
        pin.drive_low()
        dev.when_activated = None
        assert dev.when_activated is None
        evt.clear()
        pin.drive_high()
        assert not evt.wait(0.1)


def test_builtin_callbacks(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as dev:
        assert gc.isenabled()
        dev.when_activated = gc.disable
        assert dev.when_activated is gc.disable
        pin.drive_high()
        assert not gc.isenabled()
        gc.enable()


def test_callback_with_param(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as dev:
        devices = []
        evt = Event()
        def cb(d):
            devices.append(d)
            evt.set()
        dev.when_activated = cb
        assert dev.when_activated is not None
        pin.drive_high()
        assert evt.wait(1)
        assert devices == [dev]


def test_bad_callback(mock_factory):
    pin = mock_factory.pin(4)
    with DigitalInputDevice(4) as dev:
        with pytest.raises(BadEventHandler):
            dev.when_activated = 100
        with pytest.raises(BadEventHandler):
            dev.when_activated = lambda x, y: x + y
