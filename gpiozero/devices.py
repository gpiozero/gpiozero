import weakref
from threading import Thread, Event
from collections import deque

from RPi import GPIO


class GPIODeviceError(Exception):
    pass


class GPIODevice(object):
    """
    Generic GPIO Device.
    """
    def __init__(self, pin=None):
        if pin is None:
            raise GPIODeviceError('No GPIO pin number given')
        self._pin = pin
        self._active_state = GPIO.HIGH
        self._inactive_state = GPIO.LOW

    def _read(self):
        return GPIO.input(self.pin) == self._active_state

    def _fire_events(self):
        pass

    @property
    def pin(self):
        return self._pin

    @property
    def is_active(self):
        return self._read()

    def __repr__(self):
        return "<gpiozero.%s object on pin=%d, is_active=%s>" % (
            self.__class__.__name__, self.pin, self.is_active)


_GPIO_THREADS = set()


def _gpio_threads_shutdown():
    while _GPIO_THREADS:
        for t in _GPIO_THREADS.copy():
            t.stop()


class GPIOThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super(GPIOThread, self).__init__(group, target, name, args, kwargs)
        self.stopping = Event()
        self.daemon = True

    def start(self):
        self.stopping.clear()
        _GPIO_THREADS.add(self)
        super(GPIOThread, self).start()

    def stop(self):
        self.stopping.set()
        self.join()

    def join(self):
        super(GPIOThread, self).join()
        _GPIO_THREADS.discard(self)


class GPIOQueue(GPIOThread):
    def __init__(self, parent, queue_len=5, sample_wait=0.0, partial=False):
        assert isinstance(parent, GPIODevice)
        super(GPIOQueue, self).__init__(target=self.fill)
        if queue_len < 1:
            raise InputDeviceError('queue_len must be at least one')
        self.queue = deque(maxlen=queue_len)
        self.partial = partial
        self.sample_wait = sample_wait
        self.full = Event()
        self.parent = weakref.proxy(parent)

    @property
    def value(self):
        if not self.partial:
            self.full.wait()
        try:
            return sum(self.queue) / len(self.queue)
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
