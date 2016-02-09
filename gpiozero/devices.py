from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
nstr = str
str = type('')

import atexit
import weakref
from threading import Thread, Event, RLock
from collections import deque
from types import FunctionType
try:
    from statistics import median, mean
except ImportError:
    from .compat import median, mean

from .exc import (
    GPIOPinMissing,
    GPIOPinInUse,
    GPIODeviceClosed,
    GPIOBadQueueLen,
    GPIOBadSampleWait,
    )

# Get a pin implementation to use as the default; we prefer RPi.GPIO's here
# as it supports PWM, and all Pi revisions. If no third-party libraries are
# available, however, we fall back to a pure Python implementation which
# supports platforms like PyPy
from .pins import PINS_CLEANUP
try:
    from .pins.rpigpio import RPiGPIOPin
    DefaultPin = RPiGPIOPin
except ImportError:
    try:
        from .pins.rpio import RPIOPin
        DefaultPin = RPIOPin
    except ImportError:
        from .pins.native import NativePin
        DefaultPin = NativePin


_THREADS = set()
_PINS = set()
# Due to interactions between RPi.GPIO cleanup and the GPIODevice.close()
# method the same thread may attempt to acquire this lock, leading to deadlock
# unless the lock is re-entrant
_PINS_LOCK = RLock()

def _shutdown():
    while _THREADS:
        for t in _THREADS.copy():
            t.stop()
    with _PINS_LOCK:
        while _PINS:
            _PINS.pop().close()
    # Any cleanup routines registered by pins libraries must be called *after*
    # cleanup of pin objects used by devices
    for routine in PINS_CLEANUP:
        routine()

atexit.register(_shutdown)


class GPIOMeta(type):
    # NOTE Yes, this is a metaclass. Don't be scared - it's a simple one.

    def __new__(mcls, name, bases, cls_dict):
        # Construct the class as normal
        cls = super(GPIOMeta, mcls).__new__(mcls, name, bases, cls_dict)
        for attr_name, attr in cls_dict.items():
            # If there's a method in the class which has no docstring, search
            # the base classes recursively for a docstring to copy
            if isinstance(attr, FunctionType) and not attr.__doc__:
                for base_cls in cls.__mro__:
                    if hasattr(base_cls, attr_name):
                        base_fn = getattr(base_cls, attr_name)
                        if base_fn.__doc__:
                            attr.__doc__ = base_fn.__doc__
                            break
        return cls

    def __call__(mcls, *args, **kwargs):
        # Construct the instance as normal and ensure it's an instance of
        # GPIOBase (defined below with a custom __setattrs__)
        result = super(GPIOMeta, mcls).__call__(*args, **kwargs)
        assert isinstance(result, GPIOBase)
        # At this point __new__ and __init__ have all been run. We now fix the
        # set of attributes on the class by dir'ing the instance and creating a
        # frozenset of the result called __attrs__ (which is queried by
        # GPIOBase.__setattr__)
        result.__attrs__ = frozenset(dir(result))
        return result


# Cross-version compatible method of using a metaclass
class GPIOBase(GPIOMeta(nstr('GPIOBase'), (), {})):
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
        Returns ``True`` if the device is closed (see the :meth:`close`
        method). Once a device is closed you can no longer use any other
        methods or properties to control or query the device.
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
    basic services applicable to all devices (specifically the :attr:`pin`
    property, :attr:`is_active` property, and the :attr:`close` method).

    :param int pin:
        The GPIO pin (in BCM numbering) that the device is connected to. If
        this is ``None``, :exc:`GPIOPinMissing` will be raised. If the pin is
        already in use by another device, :exc:`GPIOPinInUse` will be raised.
    """
    def __init__(self, pin=None):
        super(GPIODevice, self).__init__()
        # self._pin must be set before any possible exceptions can be raised
        # because it's accessed in __del__. However, it mustn't be given the
        # value of pin until we've verified that it isn't already allocated
        self._pin = None
        if pin is None:
            raise GPIOPinMissing('No pin given')
        if isinstance(pin, int):
            pin = DefaultPin(pin)
        with _PINS_LOCK:
            if pin in _PINS:
                raise GPIOPinInUse(
                    'pin %r is already in use by another gpiozero object' % pin
                )
            _PINS.add(pin)
        self._pin = pin
        self._active_state = True
        self._inactive_state = False

    def _read(self):
        try:
            return self.pin.state == self._active_state
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

        :class:`GPIODevice` descendents can also be used as context managers
        using the :keyword:`with` statement. For example:

            >>> from gpiozero import *
            >>> with Buzzer(16) as bz:
            ...     bz.on()
            ...
            >>> with LED(16) as led:
            ...     led.on()
            ...
        """
        super(GPIODevice, self).close()
        with _PINS_LOCK:
            pin = self._pin
            self._pin = None
            if pin in _PINS:
                _PINS.remove(pin)
                pin.close()

    @property
    def closed(self):
        return self._pin is None

    @property
    def pin(self):
        """
        The :class:`Pin` that the device is connected to. This will be ``None``
        if the device has been closed (see the :meth:`close` method). When
        dealing with GPIO pins, query ``pin.number`` to discover the GPIO
        pin (in BCM numbering) that the device is connected to.
        """
        return self._pin

    @property
    def value(self):
        """
        Returns ``True`` if the device is currently active and ``False``
        otherwise.
        """
        return self._read()

    is_active = value

    def __repr__(self):
        try:
            return "<gpiozero.%s object on pin %r, is_active=%s>" % (
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

