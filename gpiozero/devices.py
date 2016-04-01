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
from collections import namedtuple
from itertools import chain
from types import FunctionType
from threading import RLock

from .threads import GPIOThread, _threads_shutdown
from .exc import (
    DeviceClosed,
    GPIOPinMissing,
    GPIOPinInUse,
    GPIODeviceClosed,
    GPIOBadSourceDelay,
    )

# Get a pin implementation to use as the default; we prefer RPi.GPIO's here
# as it supports PWM, and all Pi revisions. If no third-party libraries are
# available, however, we fall back to a pure Python implementation which
# supports platforms like PyPy
from .pins import _pins_shutdown
try:
    from .pins.rpigpio import RPiGPIOPin
    DefaultPin = RPiGPIOPin
except ImportError:
    try:
        from .pins.rpio import RPIOPin
        DefaultPin = RPIOPin
    except ImportError:
        try:
            from .pins.pigipod import PiGPIOPin
            DefaultPin = PiGPIOPin
        except ImportError:
            from .pins.native import NativePin
            DefaultPin = NativePin


_PINS = set()
_PINS_LOCK = RLock() # Yes, this needs to be re-entrant

def _shutdown():
    _threads_shutdown()
    with _PINS_LOCK:
        while _PINS:
            _PINS.pop().close()
    # Any cleanup routines registered by pins libraries must be called *after*
    # cleanup of pin objects used by devices
    _pins_shutdown()

atexit.register(_shutdown)


class GPIOMeta(type):
    # NOTE Yes, this is a metaclass. Don't be scared - it's a simple one.

    def __new__(mcls, name, bases, cls_dict):
        # Construct the class as normal
        cls = super(GPIOMeta, mcls).__new__(mcls, name, bases, cls_dict)
        # If there's a method in the class which has no docstring, search
        # the base classes recursively for a docstring to copy
        for attr_name, attr in cls_dict.items():
            if isinstance(attr, FunctionType) and not attr.__doc__:
                for base_cls in cls.__mro__:
                    if hasattr(base_cls, attr_name):
                        base_fn = getattr(base_cls, attr_name)
                        if base_fn.__doc__:
                            attr.__doc__ = base_fn.__doc__
                            break
        return cls

    def __call__(cls, *args, **kwargs):
        # Make sure cls has GPIOBase somewhere in its ancestry (otherwise
        # setting __attrs__ below will be rather pointless)
        assert issubclass(cls, GPIOBase)
        if issubclass(cls, SharedMixin):
            # If SharedMixin appears in the class' ancestry, convert the
            # constructor arguments to a key and check whether an instance
            # already exists. Only construct the instance if the key's new.
            key = cls._shared_key(*args, **kwargs)
            try:
                self = cls._INSTANCES[key]
                self._refs += 1
            except (KeyError, ReferenceError) as e:
                self = super(GPIOMeta, cls).__call__(*args, **kwargs)
                self._refs = 1
                # Replace the close method with one that merely decrements
                # the refs counter and calls the original close method when
                # it reaches zero
                old_close = self.close
                def close():
                    self._refs = max(0, self._refs - 1)
                    if not self._refs:
                        try:
                            old_close()
                        finally:
                            del cls._INSTANCES[key]
                self.close = close
                cls._INSTANCES[key] = weakref.proxy(self)
        else:
            # Construct the instance as normal
            self = super(GPIOMeta, cls).__call__(*args, **kwargs)
        # At this point __new__ and __init__ have all been run. We now fix the
        # set of attributes on the class by dir'ing the instance and creating a
        # frozenset of the result called __attrs__ (which is queried by
        # GPIOBase.__setattr__). An exception is made for SharedMixin devices
        # which can be constructed multiple times, returning the same instance
        if not issubclass(cls, SharedMixin) or self._refs == 1:
            self.__attrs__ = frozenset(dir(self))
        return self


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
        """
        Shut down the device and release all associated resources. This method
        can be called on an already closed device without raising an exception.

        This method is primarily intended for interactive use at the command
        line. It disables the device and releases its pin(s) for use by another
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

        :class:`Device` descendents can also be used as context managers using
        the :keyword:`with` statement. For example:

            >>> from gpiozero import *
            >>> with Buzzer(16) as bz:
            ...     bz.on()
            ...
            >>> with LED(16) as led:
            ...     led.on()
            ...
        """
        # This is a placeholder which is simply here to ensure close() can be
        # safely called from subclasses without worrying whether super-class'
        # have it (which in turn is useful in conjunction with the SourceMixin
        # class).
        pass

    @property
    def closed(self):
        """
        Returns ``True`` if the device is closed (see the :meth:`close`
        method). Once a device is closed you can no longer use any other
        methods or properties to control or query the device.
        """
        return False

    def _check_open(self):
        if self.closed:
            raise DeviceClosed(
                '%s is closed or uninitialized' % self.__class__.__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class ValuesMixin(object):
    """
    Adds a :attr:`values` property to the class which returns an infinite
    generator of readings from the :attr:`value` property.

    .. note::

        Use this mixin *first* in the parent class list.
    """

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
    """
    Adds a :attr:`source` property to the class which, given an iterable,
    sets :attr:`value` to each member of that iterable until it is exhausted.

    .. note::

        Use this mixin *first* in the parent class list.
    """

    def __init__(self, *args, **kwargs):
        self._source = None
        self._source_thread = None
        self._source_delay = 0.01
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
            if self._source_thread.stopping.wait(self._source_delay):
                break

    @property
    def source_delay(self):
        """
        The delay (measured in seconds) in the loop used to read values from
        :attr:`source`. Defaults to 0.01 seconds which is generally sufficient
        to keep CPU usage to a minimum while providing adequate responsiveness.
        """
        return self._source_delay

    @source_delay.setter
    def source_delay(self, value):
        if value < 0:
            raise GPIOBadSourceDelay('source_delay must be 0 or greater')
        self._source_delay = float(value)

    @property
    def source(self):
        """
        The iterable to use as a source of values for :attr:`value`.
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


class SharedMixin(object):
    """
    This mixin marks a class as "shared". In this case, the meta-class
    (GPIOMeta) will use :meth:`_shared_key` to convert the constructor
    arguments to an immutable key, and will check whether any existing
    instances match that key. If they do, they will be returned by the
    constructor instead of a new instance. An internal reference counter is
    used to determine how many times an instance has been "constructed" in this
    way.

    When :meth:`close` is called, an internal reference counter will be
    decremented and the instance will only close when it reaches zero.
    """
    _INSTANCES = {}

    def __del__(self):
        self._refs = 0
        super(SharedMixin, self).__del__()

    @classmethod
    def _shared_key(cls, *args, **kwargs):
        """
        Given the constructor arguments, returns an immutable key representing
        the instance. The default simply assumes all positional arguments are
        immutable.
        """
        return args


class Device(ValuesMixin, GPIOBase):
    """
    Represents a single device of any type; GPIO-based, SPI-based, I2C-based,
    etc. This is the base class of the device hierarchy.
    """
    def __repr__(self):
        return "<gpiozero.%s object>" % (self.__class__.__name__)


class CompositeDevice(Device):
    """
    Extends :class:`Device`. Represents a device composed of multiple devices
    like simple HATs, H-bridge motor controllers, robots composed of multiple
    motors, etc.

    The constructor accepts subordinate devices as positional or keyword
    arguments.  Positional arguments form unnamed devices accessed via the
    :attr:`all` attribute, while keyword arguments are added to the device
    as named (read-only) attributes.

    :param list _order:
        If specified, this is the order of named items specified by keyword
        arguments (to ensure that the :attr:`value` tuple is constructed with a
        specific order). All keyword arguments *must* be included in the
        collection. If omitted, an arbitrary order will be selected for keyword
        arguments.
    """
    def __init__(self, *args, **kwargs):
        self._all = ()
        self._named = {}
        self._tuple = None
        self._order = kwargs.pop('_order', None)
        if self._order is None:
            self._order = kwargs.keys()
        self._order = tuple(self._order)
        for missing_name in set(self._order) - set(kwargs.keys()):
            raise ValueError('%s missing from _order' % missing_name)
        super(CompositeDevice, self).__init__()
        for name in set(self._order) & set(dir(self)):
            raise CompositeDeviceBadName('%s is a reserved name' % name)
        self._all = args + tuple(kwargs[v] for v in self._order)
        self._named = kwargs
        self._tuple = namedtuple('%sValue' % self.__class__.__name__, chain(
            (str(i) for i in range(len(args))), self._order),
            rename=True)

    def __getattr__(self, name):
        # if _named doesn't exist yet, pretend it's an empty dict
        if name == '_named':
            return {}
        try:
            return self._named[name]
        except KeyError:
            raise AttributeError("no such attribute %s" % name)

    def __setattr__(self, name, value):
        # make named components read-only properties
        if name in self._named:
            raise AttributeError("can't set attribute %s" % name)
        return super(CompositeDevice, self).__setattr__(name, value)

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.%s object containing %d devices: %s and %d unnamed>" % (
                    self.__class__.__name__,
                    len(self), ','.join(self._named),
                    len(self) - len(self._named)
                    )
        except DeviceClosed:
            return "<gpiozero.%s object closed>"

    def __len__(self):
        return len(self._all)

    def __getitem__(self, index):
        return self._all[index]

    def __iter__(self):
        return iter(self._all)

    @property
    def all(self):
        # XXX Deprecate this in favour of using the instance as a container
        return self._all

    def close(self):
        if self._all:
            for device in self._all:
                device.close()

    @property
    def closed(self):
        return all(device.closed for device in self)

    @property
    def tuple(self):
        return self._tuple

    @property
    def value(self):
        return self.tuple(*(device.value for device in self))


class GPIODevice(Device):
    """
    Extends :class:`Device`. Represents a generic GPIO device.

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
        except (AttributeError, TypeError):
            self._check_open()
            raise

    def _fire_events(self):
        pass

    def close(self):
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

    def _check_open(self):
        try:
            super(GPIODevice, self)._check_open()
        except DeviceClosed as e:
            # For backwards compatibility; GPIODeviceClosed is deprecated
            raise GPIODeviceClosed(str(e))

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


