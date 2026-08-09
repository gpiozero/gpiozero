# vim: set fileencoding=utf-8:
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
from gpiozero.mixins import GPIOQueue
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


def test_gpioqueue_thread_safe_value():
    # Regression test for https://github.com/gpiozero/gpiozero/issues/975:
    # GPIOQueue.fill() runs in a background thread and appends to a bounded
    # deque, while .value reads the same deque by iterating over it (e.g.
    # via statistics.mean/median). If an append lands while that iteration
    # is part-way through, the deque raises "RuntimeError: deque mutated
    # during iteration" -- exactly the traceback reported by several users
    # polling MotionSensor.is_active in a tight loop.
    #
    # Rather than relying on real thread-scheduling timing to *happen* to
    # trigger this (found, empirically, to be extremely environment
    # sensitive -- reliably reproducible as a bare `python -c` script, but
    # not from a thread inside a running pytest process), this deterministically
    # forces the exact interleaving: .value's average() is paused
    # mid-iteration by a synthetic average function, an append is attempted
    # (on a separate thread, exactly as fill() would do it -- through
    # queue.lock if it exists), and only then is the iteration allowed to
    # resume.
    #
    # On unpatched code there's no queue.lock, so the append lands
    # immediately, while the paused iterator is still alive, and resuming
    # the iteration raises RuntimeError. On patched code the append blocks
    # on the same lock .value is holding for the duration of average(), so
    # it can't land until iteration has already finished.
    class FakeParent:
        def _read(self):
            return 1

    queue = GPIOQueue(FakeParent(), queue_len=5, sample_wait=0.0, partial=True)
    for v in range(3):
        queue.queue.append(v)

    entered = Event()
    resume = Event()

    def pausing_average(data):
        total = 0
        count = 0
        for i, item in enumerate(data):
            total += item
            count += 1
            if i == 0:
                entered.set()
                assert resume.wait(2), 'test setup timed out'
        return total / count if count else 0

    queue.average = pausing_average

    result = {}

    def call_value():
        try:
            result['value'] = queue.value
        except RuntimeError as e:
            result['error'] = e

    value_thread = threading.Thread(target=call_value)
    value_thread.start()
    assert entered.wait(2), 'average() never started iterating'

    append_finished = Event()

    def do_append():
        lock = getattr(queue, 'lock', None)
        if lock is not None:
            with lock:
                queue.queue.append(999)
        else:
            queue.queue.append(999)
        append_finished.set()

    append_thread = threading.Thread(target=do_append)
    append_thread.start()
    sleep(0.05)  # give the append a moment to run (or block, if locked)

    if hasattr(queue, 'lock'):
        assert not append_finished.is_set(), (
            'append completed while .value was still iterating -- '
            'the lock is not protecting the queue')

    resume.set()
    value_thread.join(2)
    append_thread.join(2)

    assert 'error' not in result, result.get('error')
