# vim: set fileencoding=utf-8:
#
# GPIO Zero: A simple interface to GPIO devices with Raspberry Pi
#
# Copyright (c) 2026 Ben Nuttall <ben@bennuttall.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import threading
from unittest import mock

from gpiozero.threads import GPIOThread


def test_join_after_already_joined_does_not_rejoin():
    # Regression test for a crash seen when a GPIOThread is joined once (e.g.
    # by gpiozero's atexit handler) and then joined again later (e.g. from a
    # device's __del__-triggered close()). During interpreter shutdown a
    # second real Thread.join() call can raise TypeError because CPython
    # tears down threading internals before running finalizers, so join()
    # must not attempt a second real join once the thread's already finished.
    thread = GPIOThread(target=lambda: None)
    thread.start()
    thread.join(1)
    assert not thread.is_alive()
    with mock.patch.object(
            threading.Thread, 'join',
            side_effect=TypeError("'NoneType' object is not callable")):
        thread.join(1)  # must not raise


def test_stop_after_already_stopped_does_not_rejoin():
    thread = GPIOThread(target=lambda: None)
    thread.start()
    thread.stop(1)
    assert not thread.is_alive()
    with mock.patch.object(
            threading.Thread, 'join',
            side_effect=TypeError("'NoneType' object is not callable")):
        thread.stop(1)  # must not raise


def test_join_still_waits_for_a_running_thread():
    evt = threading.Event()
    thread = GPIOThread(target=evt.wait)
    thread.start()
    assert thread.is_alive()
    evt.set()
    thread.join(1)
    assert not thread.is_alive()
