from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )

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


class GPIOFixedAttrs(type):
    # NOTE Yes, this is a metaclass. Don't be scared - it's a simple one.

    def __call__(cls, *args, **kwargs):
        # Construct the class as normal and ensure it's a subclass of GPIOBase
        # (defined below with a custom __setattrs__)
        result = super(GPIOFixedAttrs, cls).__call__(*args, **kwargs)
        assert isinstance(result, GPIOBase)
        # At this point __new__ and __init__ have all been run. We now fix the
        # set of attributes on the class by dir'ing the instance and creating a
        # frozenset of the result called __attrs__ (which is queried by
        # GPIOBase.__setattr__)
        result.__attrs__ = frozenset(dir(result))
        return result


class GPIOBase(object):
    __metaclass__ = GPIOFixedAttrs

    def __setattr__(self, name, value):
        # This overridden __setattr__ simply ensures that additional attributes
        # cannot be set on the class after construction (it manages this in
        # conjunction with the meta-class above). Traditionally, this is
        # managed with __slots__; however, this doesn't work with Python's
        # multiple inheritance system which we need to use in order to avoid
        # repeating the "source" and "values" property code in myriad places
        if hasattr(self, '__attrs__') and name not in self.__attrs__:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (
                self.__class__.__name__, name))
        return super(GPIOBase, self).__setattr__(name, value)

    def __del__(self):
        self.close()

    def close(self):
        # This is a placeholder which is simply here to ensure close() can be
        # safely called from subclasses without worrying whether super-class'
        # have it (which in turn is useful in conjunction with the SourceMixin
        # class).
        """
        Shut down the device and release all associated resources.
        """
        pass

    @property
    def closed(self):
        """
        Returns `True` if the device is closed (see the `close` method). Once a
        device is closed you can no longer use any other methods or properties
        to control or query the device.
        """
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class ValuesMixin(object):
    # NOTE Use this mixin *first* in the parent list

    @property
    def values(self):
        """
        An infinite iterator of values read from `value`.
        """
        while True:
            try:
                yield self.value
            except GPIODeviceClosed:
                break


class SourceMixin(object):
    # NOTE Use this mixin *first* in the parent list

    def __init__(self, *args, **kwargs):
        self._source = None
        self._source_thread = None
        super(SourceMixin, self).__init__(*args, **kwargs)

    def close(self):
        try:
            super(SourceMixin, self).close()
        except AttributeError:
            pass
        self.source = None

    def _copy_values(self, source):
        for v in source:
            self.value = v
            if self._source_thread.stopping.wait(0):
                break

    @property
    def source(self):
        """
        The iterable to use as a source of values for `value`.
        """
        return self._source

    @source.setter
    def source(self, value):
        if self._source_thread is not None:
            self._source_thread.stop()
            self._source_thread = None
        self._source = value
        if value is not None:
            self._source_thread = GPIOThread(target=self._copy_values, args=(value,))
            self._source_thread.start()


class CompositeDevice(ValuesMixin, GPIOBase):
    """
    Represents a device composed of multiple GPIO devices like simple HATs,
    H-bridge motor controllers, robots composed of multiple motors, etc.
    """
    def __repr__(self):
        return "<gpiozero.%s object>" % (self.__class__.__name__)


class GPIODevice(ValuesMixin, GPIOBase):
    """
    Represents a generic GPIO device.

    This is the class at the root of the gpiozero class hierarchy. It handles
    ensuring that two GPIO devices do not share the same pin, and provides
    basic services applicable to all devices (specifically the `pin` property,
    `is_active` property, and the `close` method).

    pin: `None`
        The GPIO pin (in BCM numbering) that the device is connected to. If
        this is `None` a `GPIODeviceError` will be raised.
    """
    def __init__(self, pin=None):
        super(GPIODevice, self).__init__()
        # self._pin must be set before any possible exceptions can be raised
        # because it's accessed in __del__. However, it mustn't be given the
        # value of pin until we've verified that it isn't already allocated
        self._pin = None
        if pin is None:
            raise GPIODeviceError('No GPIO pin number given')
        with _GPIO_PINS_LOCK:
            if pin in _GPIO_PINS:
                raise GPIODeviceError(
                    'pin %d is already in use by another gpiozero object' % pin
                )
            _GPIO_PINS.add(pin)
        self._pin = pin
        self._active_state = GPIO.HIGH
        self._inactive_state = GPIO.LOW

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

    def close(self):
        """
        Shut down the device and release all associated resources.

        This method is primarily intended for interactive use at the command
        line. It disables the device and releases its pin for use by another
        device.

        You can attempt to do this simply by deleting an object, but unless
        you've cleaned up all references to the object this may not work (even
        if you've cleaned up all references, there's still no guarantee the
        garbage collector will actually delete the object at that point).  By
        contrast, the close method provides a means of ensuring that the object
        is shut down.

        For example, if you have a breadboard with a buzzer connected to pin
        16, but then wish to attach an LED instead:

            >>> from gpiozero import *
            >>> bz = Buzzer(16)
            >>> bz.on()
            >>> bz.off()
            >>> bz.close()
            >>> led = LED(16)
            >>> led.blink()

        GPIODevice descendents can also be used as context managers using the
        `with` statement. For example:

            >>> from gpiozero import *
            >>> with Buzzer(16) as bz:
            ...     bz.on()
            ...
            >>> with LED(16) as led:
            ...     led.on()
            ...
        """
        super(GPIODevice, self).close()
        with _GPIO_PINS_LOCK:
            pin = self._pin
            self._pin = None
            if pin in _GPIO_PINS:
                _GPIO_PINS.remove(pin)
                GPIO.remove_event_detect(pin)
                GPIO.cleanup(pin)

    @property
    def closed(self):
        return self._pin is None

    @property
    def pin(self):
        """
        The pin (in BCM numbering) that the device is connected to. This will
        be `None` if the device has been closed (see the `close` method).
        """
        return self._pin

    @property
    def value(self):
        """
        Returns `True` if the device is currently active and `False` otherwise.
        """
        return self._read()

    is_active = value

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

