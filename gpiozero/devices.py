import atexit
import weakref
from threading import Thread, Event, RLock
from collections import deque

from RPi import GPIO


_GPIO_THREADS = set()
_GPIO_PINS = set()
# Due to interactions between RPi.GPIO cleanup and the GPIODevice.close()
# method the same thread may attempt to acquire this lock, leading to deadlock
# unless the lock is re-entrant
_GPIO_PINS_LOCK = RLock()

def _gpio_threads_shutdown():
    while _GPIO_THREADS:
        for t in _GPIO_THREADS.copy():
            t.stop()
    with _GPIO_PINS_LOCK:
        while _GPIO_PINS:
            GPIO.remove_event_detect(_GPIO_PINS.pop())
        GPIO.cleanup()

atexit.register(_gpio_threads_shutdown)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class GPIODeviceError(Exception):
    pass

class GPIODeviceClosed(GPIODeviceError):
    pass


class GPIODevice(object):
    """
    Generic GPIO Device.
    """
    def __init__(self, pin=None):
        # self._pin must be set before any possible exceptions can be raised
        # because it's accessed in __del__. However, it mustn't be given the
        # value of pin until we've verified that it isn't already allocated
        self._pin = None
        if pin is None:
            raise GPIODeviceError('No GPIO pin number given')
        with _GPIO_PINS_LOCK:
            if pin in _GPIO_PINS:
                raise GPIODeviceError(
                    'pin %d is already in use by another gpiozero object' % pin)
            _GPIO_PINS.add(pin)
        self._pin = pin
        self._active_state = GPIO.HIGH
        self._inactive_state = GPIO.LOW

    def __del__(self):
        self.close()

    def _read(self):
        try:
            return GPIO.input(self.pin) == self._active_state
        except TypeError:
            self._check_open()
            raise

    def _fire_events(self):
        pass

    def _check_open(self):
        if self.closed:
            raise GPIODeviceClosed(
                '%s is closed or uninitialized' % self.__class__.__name__)

    @property
    def closed(self):
        return self._pin is None

    def close(self):
        with _GPIO_PINS_LOCK:
            pin = self._pin
            self._pin = None
            if pin in _GPIO_PINS:
                _GPIO_PINS.remove(pin)
                GPIO.remove_event_detect(pin)
                GPIO.cleanup(pin)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    @property
    def pin(self):
        return self._pin

    @property
    def is_active(self):
        return self._read()

    def __repr__(self):
        try:
            return "<gpiozero.%s object on pin=%d, is_active=%s>" % (
                self.__class__.__name__, self.pin, self.is_active)
        except GPIODeviceClosed:
            return "<gpiozero.%s object closed>" % self.__class__.__name__


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
