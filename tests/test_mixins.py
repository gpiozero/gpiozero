#
# GPIO Zero: A simple interface to GPIO devices with Raspberry Pi
#
# Copyright (c) 2026 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2019-2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import gc
import threading
from itertools import repeat
from time import sleep
from threading import Event
from unittest import mock

import pytest

from gpiozero import *
from gpiozero.threads import _threads_shutdown


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


def test_close_after_threads_shutdown_is_safe(mock_factory):
    # Regression test: setting .source then exiting the Python shell could
    # raise "TypeError: 'NoneType' object is not callable" from inside
    # __del__.
    #
    # gpiozero's atexit handler joins all live GPIOThreads via
    # _threads_shutdown() *before* interpreter shutdown reaches the point
    # where calling Thread.join() again becomes unsafe. But a device whose
    # close() hadn't been called yet (e.g. because __del__ runs later, after
    # atexit) still holds a reference to that now-already-joined thread. Its
    # own close() -> source setter -> stop() -> join() must not attempt a
    # second real join, or it can crash exactly as threading internals are
    # torn down during shutdown.
    device = OutputDevice(2)
    device.source_delay = 0.01
    device.source = repeat(0)  # a never-ending source, like sin_values()
    sleep(0.05)  # let the source thread actually start running
    assert device._source_thread is not None
    assert device._source_thread.is_alive()

    _threads_shutdown()  # simulates gpiozero's atexit hook running first
    assert not device._source_thread.is_alive()

    with mock.patch.object(
            threading.Thread, 'join',
            side_effect=TypeError("'NoneType' object is not callable")):
        device.close()  # simulates a later __del__-triggered close()

    assert device.closed


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
            super().__init__(pin, pin_factory=pin_factory)

        @classmethod
        def _shared_key(cls, pin, pin_factory=None):
            return pin

        def _conflicts_with(self, other):
            return not isinstance(other, SharedDevice)

    with SharedDevice(4) as dev:
        with SharedDevice(4) as another_dev:
            pass
        with pytest.raises(GPIOPinInUse):
            GPIODevice(4)
