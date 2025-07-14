# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2024 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2015-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import atexit
import weakref
import warnings
from collections import namedtuple
from itertools import chain
from types import FunctionType

# NOTE: Remove try when compatibility moves beyond Python 3.10
try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points

from .threads import _threads_shutdown
from .mixins import (
    ValuesMixin,
    SharedMixin,
)
from .exc import (
    BadPinFactory,
    DeviceClosed,
    CompositeDeviceBadName,
    CompositeDeviceBadOrder,
    CompositeDeviceBadDevice,
    GPIOPinMissing,
    GPIODeviceClosed,
    NativePinFactoryFallback,
    PinFactoryFallback,
)

from .compat import frozendict

native_fallback_message = (
    'Falling back to the experimental pin factory NativeFactory because no other '
    'pin factory could be loaded. For best results, install RPi.GPIO or pigpio. '
    'See https://gpiozero.readthedocs.io/en/stable/api_pins.html for more information.'
)


class GPIOMeta(type):
    # NOTE Yes, this is a metaclass. Don't be scared - it's a simple one.

    def __new__(mcls, name, bases, cls_dict):
        # Construct the class as normal
        cls = super().__new__(mcls, name, bases, cls_dict)
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
                self = cls._instances[key]()
                self._refs += 1
            except (KeyError, AttributeError) as e:
                self = super().__call__(*args, **kwargs)
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
                            try:
                                del cls._instances[key]
                            except KeyError:
                                # If the _refs go negative (too many closes)
                                # just ignore the resulting KeyError here -
                                # it's already gone
                                pass

                self.close = close
                cls._instances[key] = weakref.ref(self)
        else:
            # Construct the instance as normal
            self = super().__call__(*args, **kwargs)
        # At this point __new__ and __init__ have all been run. We now fix the
        # set of attributes on the class by dir'ing the instance and creating a
        # frozenset of the result called __attrs__ (which is queried by
        # GPIOBase.__setattr__). An exception is made for SharedMixin devices
        # which can be constructed multiple times, returning the same instance
        if not issubclass(cls, SharedMixin) or self._refs == 1:
            self.__attrs__ = frozenset(dir(self))
        return self


class GPIOBase(metaclass=GPIOMeta):
    def __setattr__(self, name, value):
        # This overridden __setattr__ simply ensures that additional attributes
        # cannot be set on the class after construction (it manages this in
        # conjunction with the meta-class above). Traditionally, this is
        # managed with __slots__; however, this doesn't work with Python's
        # multiple inheritance system which we need to use in order to avoid
        # repeating the "source" and "values" property code in myriad places
        if hasattr(self, '__attrs__') and name not in self.__attrs__:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return super().__setattr__(name, value)

    def __del__(self):
        # NOTE: Yes, we implicitly call close() on __del__(), and yes for you
        # dear hacker-on-this-library, this means pain!
        #
        # It's entirely for the convenience of command line experimenters and
        # newbies who want to re-gain those pins when stuff falls out of scope
        # without managing their object lifetimes "properly" with "with" (but,
        # hey, this is an educational library at heart so that's the way we
        # roll).
        #
        # What does this mean for you? It means that in close() you cannot
        # assume *anything*. If someone calls a constructor with a fundamental
        # mistake like the wrong number of params, then your close() method is
        # going to be called before __init__ ever ran so all those attributes
        # you *think* exist, erm, don't. Basically if you refer to anything in
        # "self" within your close method, be preprared to catch AttributeError
        # on its access to avoid spurious warnings for the end user.
        #
        # "But we're exiting anyway; surely exceptions in __del__ get
        # squashed?" Yes, but they still cause verbose warnings and remember
        # that this is an educational library; keep it friendly!
        self.close()

    def close(self):
        """
        Shut down the device and release all associated resources (such as GPIO
        pins).

        This method is idempotent (can be called on an already closed device
        without any side-effects). It is primarily intended for interactive use
        at the command line. It disables the device and releases its pin(s) for
        use by another device.

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
        # safely called from subclasses without worrying whether super-classes
        # have it (which in turn is useful in conjunction with the mixin
        # classes).
        #
        # P.S. See note in __del__ above.
        pass

    @property
    def closed(self):
        """
        Returns :data:`True` if the device is closed (see the :meth:`close`
        method). Once a device is closed you can no longer use any other
        methods or properties to control or query the device.
        """
        raise NotImplementedError

    def _check_open(self):
        if self.closed:
            raise DeviceClosed(
                f"{self.__class__.__name__} is closed or uninitialized")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class Device(ValuesMixin, GPIOBase):
    """
    Represents a single device of any type; GPIO-based, SPI-based, I2C-based,
    etc. This is the base class of the device hierarchy. It defines the basic
    services applicable to all devices (specifically the :attr:`is_active`
    property, the :attr:`value` property, and the :meth:`close` method).

    .. attribute:: pin_factory

        This attribute exists at both a class level (representing the default
        pin factory used to construct devices when no *pin_factory* parameter
        is specified), and at an instance level (representing the pin factory
        that the device was constructed with).

        The pin factory provides various facilities to the device including
        allocating pins, providing low level interfaces (e.g. SPI), and clock
        facilities (querying and calculating elapsed times).
    """
    pin_factory = None  # instance of a Factory sub-class

    def __init__(self, *, pin_factory=None):
        if pin_factory is None:
            Device.ensure_pin_factory()
            self.pin_factory = Device.pin_factory
        else:
            self.pin_factory = pin_factory
        super().__init__()

    @staticmethod
    def ensure_pin_factory():
        """
        Ensures that :attr:`Device.pin_factory` is set appropriately.

        This is called implicitly upon construction of any device, but there
        are some circumstances where you may need to call it manually.
        Specifically, when you wish to retrieve board information without
        constructing any devices, e.g.::

            Device.ensure_pin_factory()
            info = Device.pin_factory.board_info

        If :attr:`Device.pin_factory` is not :data:`None`, this function does
        nothing. Otherwise it will attempt to locate and initialize a default
        pin factory. This may raise a number of different exceptions including
        :exc:`ImportError` if no valid pin driver can be imported.
        """
        if Device.pin_factory is None:
            Device.pin_factory = Device._default_pin_factory()

    @staticmethod
    def _default_pin_factory():
        # We prefer lgpio here as it supports PWM, and all Pi revisions without
        # banging on registers directly.  If no third-party libraries are
        # available, however, we fall back to a pure Python implementation
        # which supports platforms like PyPy
        #
        # NOTE: If the built-in pin factories are expanded, the dict must be
        # updated along with the entry-points in setup.py.
        default_factories = {
            'lgpio':   'gpiozero.pins.lgpio:LGPIOFactory',
            'gpiod':   'gpiozero.pins.gpiod:GpiodFactory',
            'rpigpio': 'gpiozero.pins.rpigpio:RPiGPIOFactory',
            'pigpio':  'gpiozero.pins.pigpio:PiGPIOFactory',
            'native':  'gpiozero.pins.native:NativeFactory',
        }
        name = os.environ.get('GPIOZERO_PIN_FACTORY')
        if name is None:
            # If no factory is explicitly specified, try various names in
            # "preferred" order
            for name, entry_point in default_factories.items():
                try:
                    mod_name, cls_name = entry_point.split(':', 1)
                    module = __import__(mod_name, fromlist=(cls_name,))
                    pin_factory = getattr(module, cls_name)()
                    if name == 'native':
                        warnings.warn(NativePinFactoryFallback(native_fallback_message))
                    return pin_factory
                except Exception as e:
                    warnings.warn(
                        PinFactoryFallback(f'Falling back from {name}: {e!s}'))
            raise BadPinFactory('Unable to load any default pin factory!')
        else:
            # Use importlib's entry_points to try and find the specified
            # entry-point. Try with name verbatim first. If that fails, attempt
            # with the lower-cased name (this ensures compatibility names work
            # but we're still case insensitive for all factories)
            with warnings.catch_warnings():
                # The dict interface of entry_points is deprecated ... already
                # and this deprecation is for us to worry about, not our users
                group = entry_points(group='gpiozero_pin_factories')
            for ep in group:
                if ep.name == name:
                    return ep.load()()
            for ep in group:
                if ep.name == name.lower():
                    return ep.load()()
            raise BadPinFactory(f'Unable to find pin factory {name!r}')

    def __repr__(self):
        try:
            self._check_open()
            return f"<gpiozero.{self.__class__.__name__} object>"
        except DeviceClosed:
            return f"<gpiozero.{self.__class__.__name__} object closed>"

    def _conflicts_with(self, other):
        """
        Called by :meth:`Factory.reserve_pins` to test whether the *other*
        :class:`Device` using a common pin conflicts with this device's intent
        to use it. The default is :data:`True` indicating that all devices
        conflict with common pins.  Sub-classes may override this to permit
        more nuanced replies.
        """
        return True

    @property
    def value(self):
        """
        Returns a value representing the device's state. Frequently, this is a
        boolean value, or a number between 0 and 1 but some devices use larger
        ranges (e.g. -1 to +1) and composite devices usually use tuples to
        return the states of all their subordinate components.
        """
        raise NotImplementedError

    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is currently active and
        :data:`False` otherwise. This property is usually derived from
        :attr:`value`. Unlike :attr:`value`, this is *always* a boolean.
        """
        return bool(self.value)


class CompositeDevice(Device):
    """
    Extends :class:`Device`. Represents a device composed of multiple devices
    like simple HATs, H-bridge motor controllers, robots composed of multiple
    motors, etc.

    The constructor accepts subordinate devices as positional or keyword
    arguments.  Positional arguments form unnamed devices accessed by treating
    the composite device as a container, while keyword arguments are added to
    the device as named (read-only) attributes.

    For example:

    .. code-block:: pycon

        >>> from gpiozero import *
        >>> d = CompositeDevice(LED(2), LED(3), LED(4), btn=Button(17))
        >>> d[0]
        <gpiozero.LED object on pin GPIO2, active_high=True, is_active=False>
        >>> d[1]
        <gpiozero.LED object on pin GPIO3, active_high=True, is_active=False>
        >>> d[2]
        <gpiozero.LED object on pin GPIO4, active_high=True, is_active=False>
        >>> d.btn
        <gpiozero.Button object on pin GPIO17, pull_up=True, is_active=False>
        >>> d.value
        CompositeDeviceValue(device_0=False, device_1=False, device_2=False, btn=False)

    :param Device \\*args:
        The un-named devices that belong to the composite device. The
        :attr:`value` attributes of these devices will be represented within
        the composite device's tuple :attr:`value` in the order specified here.

    :type _order: list or None
    :param _order:
        If specified, this is the order of named items specified by keyword
        arguments (to ensure that the :attr:`value` tuple is constructed with a
        specific order). All keyword arguments *must* be included in the
        collection. If omitted, an alphabetically sorted order will be selected
        for keyword arguments.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :param Device \\*\\*kwargs:
        The named devices that belong to the composite device. These devices
        will be accessible as named attributes on the resulting device, and
        their :attr:`value` attributes will be accessible as named elements of
        the composite device's tuple :attr:`value`.
    """

    def __init__(self, *args, _order=None, pin_factory=None, **kwargs):
        self._all = ()
        self._named = frozendict({})
        self._namedtuple = None
        self._order = _order
        try:
            if self._order is None:
                self._order = sorted(kwargs.keys())
            else:
                for missing_name in set(kwargs.keys()) - set(self._order):
                    raise CompositeDeviceBadOrder(
                        f'{missing_name} missing from _order')
            self._order = tuple(self._order)
            for name in set(self._order) & set(dir(self)):
                raise CompositeDeviceBadName(f'{name} is a reserved name')
            for dev in chain(args, kwargs.values()):
                if not isinstance(dev, Device):
                    raise CompositeDeviceBadDevice(
                        f"{dev} doesn't inherit from Device")
            self._named = frozendict(kwargs)
            self._namedtuple = namedtuple(
                f'{self.__class__.__name__}Value',
                chain((f'device_{i}' for i in range(len(args))), self._order))
        except:
            for dev in chain(args, kwargs.values()):
                if isinstance(dev, Device):
                    dev.close()
            raise
        self._all = args + tuple(kwargs[v] for v in self._order)
        super().__init__(pin_factory=pin_factory)

    def __getattr__(self, name):
        # if _named doesn't exist yet, pretend it's an empty dict
        if name == '_named':
            return frozendict({})
        try:
            return self._named[name]
        except KeyError:
            raise AttributeError(f"no such attribute {name}")

    def __setattr__(self, name, value):
        # make named components read-only properties
        if name in self._named:
            raise AttributeError(f"can't set attribute {name}")
        return super().__setattr__(name, value)

    def __repr__(self):
        try:
            self._check_open()
            named = len(self._named)
            names = ', '.join(self._order)
            unnamed = len(self) - len(self._named)
            if named > 0 and unnamed > 0:
                return (
                    f"<gpiozero.{self.__class__.__name__} object containing "
                    f"{len(self)} devices: {names} and {unnamed} unnamed>")
            elif named > 0:
                return (
                    f"<gpiozero.{self.__class__.__name__} object containing "
                    f"{len(self)} devices: {names}>")
            else:
                return (
                    f"<gpiozero.{self.__class__.__name__} object containing "
                    f"{len(self)} unnamed devices>")
        except DeviceClosed:
            return super().__repr__()

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
        if getattr(self, '_all', None):
            for device in self._all:
                device.close()
            self._all = ()

    @property
    def closed(self):
        return all(device.closed for device in self)

    @property
    def namedtuple(self):
        """
        The :func:`~collections.namedtuple` type constructed to represent the
        value of the composite device. The :attr:`value` attribute returns
        values of this type.
        """
        return self._namedtuple

    @property
    def value(self):
        """
        A :func:`~collections.namedtuple` containing a value for each
        subordinate device. Devices with names will be represented as named
        elements. Unnamed devices will have a unique name generated for them,
        and they will appear in the position they appeared in the constructor.
        """
        return self.namedtuple(*(device.value for device in self))

    @property
    def is_active(self):
        """
        Composite devices are considered "active" if any of their constituent
        devices have a "truthy" value.
        """
        return any(self.value)


class GPIODevice(Device):
    """
    Extends :class:`Device`. Represents a generic GPIO device and provides
    the services common to all single-pin GPIO devices (like ensuring two
    GPIO devices do no share a :attr:`pin`).

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised. If the pin is already in use by another device,
        :exc:`GPIOPinInUse` will be raised.
    """

    def __init__(self, pin=None, *, pin_factory=None):
        super().__init__(pin_factory=pin_factory)
        # self._pin must be set before any possible exceptions can be raised
        # because it's accessed in __del__. However, it mustn't be given the
        # value of pin until we've verified that it isn't already allocated
        self._pin = None
        if pin is None:
            raise GPIOPinMissing('No pin given')
        # Check you can reserve *before* constructing the pin
        self.pin_factory.reserve_pins(self, pin)
        pin = self.pin_factory.pin(pin)
        self._pin = pin
        self._active_state = True
        self._inactive_state = False

    def _state_to_value(self, state):
        return int(state == self._active_state)

    def _read(self):
        try:
            return self._state_to_value(self.pin.state)
        except (AttributeError, TypeError):
            self._check_open()
            raise

    def close(self):
        super().close()
        if getattr(self, '_pin', None) is not None:
            self.pin_factory.release_pins(self, self._pin.info.name)
            self._pin.close()
        self._pin = None

    @property
    def closed(self):
        try:
            return self._pin is None
        except AttributeError:
            return True

    def _check_open(self):
        try:
            super()._check_open()
        except DeviceClosed as e:
            # For backwards compatibility; GPIODeviceClosed is deprecated
            raise GPIODeviceClosed(str(e))

    @property
    def pin(self):
        """
        The :class:`Pin` that the device is connected to. This will be
        :data:`None` if the device has been closed (see the
        :meth:`~Device.close` method). When dealing with GPIO pins, query
        ``pin.number`` to discover the GPIO pin (in BCM numbering) that the
        device is connected to.
        """
        return self._pin

    @property
    def value(self):
        return self._read()

    def __repr__(self):
        try:
            return (
                f"<gpiozero.{self.__class__.__name__} object on pin "
                f"{self.pin!r}, is_active={self.is_active}>")
        except DeviceClosed:
            return f"<gpiozero.{self.__class__.__name__} object closed>"


def _devices_shutdown():
    if Device.pin_factory is not None:
        with Device.pin_factory._res_lock:
            reserved_devices = {
                dev
                for ref_list in Device.pin_factory._reservations.values()
                for ref in ref_list
                for dev in (ref(),)
                if dev is not None
            }
        for dev in reserved_devices:
            dev.close()
        Device.pin_factory.close()
        Device.pin_factory = None


def _shutdown():
    _threads_shutdown()
    _devices_shutdown()


atexit.register(_shutdown)
