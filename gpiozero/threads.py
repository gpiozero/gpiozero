from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')

from threading import Thread, Event


_THREADS = set()
def _threads_shutdown():
    while _THREADS:
        for t in _THREADS.copy():
            t.stop()


class GPIOThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.stopping = Event()
        super(GPIOThread, self).__init__(group, target, name, args, kwargs)
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

