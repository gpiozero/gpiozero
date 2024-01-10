# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from threading import Thread, Event

from .exc import ZombieThread


_THREADS = set()


def _threads_shutdown():
    while _THREADS:
        threads = _THREADS.copy()
        # Optimization: instead of calling stop() which implicitly calls
        # join(), set all the stopping events simultaneously, *then* join
        # threads with a reasonable timeout
        for t in threads:
            t.stopping.set()
        for t in threads:
            t.join(10)


class GPIOThread(Thread):
    def __init__(self, target, args=(), kwargs=None, name=None):
        if kwargs is None:
            kwargs = {}
        self.stopping = Event()
        super().__init__(None, target, name, args, kwargs)
        self.daemon = True

    def start(self):
        self.stopping.clear()
        _THREADS.add(self)
        super().start()

    def stop(self, timeout=10):
        self.stopping.set()
        self.join(timeout)

    def join(self, timeout=None):
        super().join(timeout)
        if self.is_alive():
            assert timeout is not None
            # timeout can't be None here because if it was, then join()
            # wouldn't return until the thread was dead
            raise ZombieThread(f"Thread failed to die within {timeout} seconds")
        else:
            _THREADS.discard(self)
