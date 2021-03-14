# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2019-2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

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


def test_shared_key(mock_factory):
    class SharedDevice(SharedMixin, GPIODevice):
        def __init__(self, pin, pin_factory=None):
            super(SharedDevice, self).__init__(pin, pin_factory=pin_factory)

        def _conflicts_with(self, other):
            return not isinstance(other, SharedDevice)

    with SharedDevice(4) as dev:
        with SharedDevice(4) as another_dev:
            pass
        with pytest.raises(GPIOPinInUse):
            GPIODevice(4)
