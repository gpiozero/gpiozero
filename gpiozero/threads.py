from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')

import weakref
from collections import deque
from threading import Thread, Event, RLock
try:
    from statistics import median, mean
except ImportError:
    from .compat import median, mean

from .exc import (
    GPIOBadQueueLen,
    GPIOBadSampleWait,
    )


_THREADS = set()
def _threads_shutdown():
    while _THREADS:
        for t in _THREADS.copy():
            t.stop()


class GPIOThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super(GPIOThread, self).__init__(group, target, name, args, kwargs)
        self.stopping = Event()
        self.daemon = True

    def start(self):
        self.stopping.clear()
        _THREADS.add(self)
        super(GPIOThread, self).start()

    def stop(self):
        self.stopping.set()
        self.join()

    def join(self):
        super(GPIOThread, self).join()
        _THREADS.discard(self)


class GPIOQueue(GPIOThread):
    def __init__(
            self, parent, queue_len=5, sample_wait=0.0, partial=False,
            average=median):
        assert isinstance(parent, GPIODevice)
        assert callable(average)
        super(GPIOQueue, self).__init__(target=self.fill)
        if queue_len < 1:
            raise GPIOBadQueueLen('queue_len must be at least one')
        if sample_wait < 0:
            raise GPIOBadSampleWait('sample_wait must be 0 or greater')
        self.queue = deque(maxlen=queue_len)
        self.partial = partial
        self.sample_wait = sample_wait
        self.full = Event()
        self.parent = weakref.proxy(parent)
        self.average = average

    @property
    def value(self):
        if not self.partial:
            self.full.wait()
        try:
            return self.average(self.queue)
        except ZeroDivisionError:
            # No data == inactive value
            return 0.0

    def fill(self):
        try:
            while (not self.stopping.wait(self.sample_wait) and
                    len(self.queue) < self.queue.maxlen):
                self.queue.append(self.parent._read())
                if self.partial:
                    self.parent._fire_events()
            self.full.set()
            while not self.stopping.wait(self.sample_wait):
                self.queue.append(self.parent._read())
                self.parent._fire_events()
        except ReferenceError:
            # Parent is dead; time to die!
            pass

