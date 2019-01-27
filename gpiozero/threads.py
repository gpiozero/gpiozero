from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')

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

    def stop(self, timeout=10):
        self.stopping.set()
        self.join(timeout)

    def join(self, timeout=None):
        super(GPIOThread, self).join(timeout)
        if self.is_alive():
            assert timeout is not None
            # timeout can't be None here because if it was, then join()
            # wouldn't return until the thread was dead
            raise ZombieThread(
                "Thread failed to die within %d seconds" % timeout)
        else:
            _THREADS.discard(self)
