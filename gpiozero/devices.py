# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2015-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
nstr = str
str = type('')

import os
import atexit
import weakref
import warnings
from collections import namedtuple, OrderedDict
from itertools import chain
from types import FunctionType
from threading import Lock

from .pins import Pin
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
    GPIOPinInUse,
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
                self = cls._instances[key]
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
                            try:
                                del cls._instances[key]
                            except KeyError:
                                # If the _refs go negative (too many closes)
                                # just ignore the resulting KeyError here -
                                # it's already gone
                                pass
                self.close = close
                cls._instances[key] = weakref.proxy(self)
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
        # safely called from subclasses without worrying whether super-classes
        # have it (which in turn is useful in conjunction with the SourceMixin
        # class).
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
                '%s is closed or uninitialized' % self.__class__.__name__)

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
    pin_factory = None # instance of a Factory sub-class

    def __init__(self, **kwargs):
        # Force pin_factory to be keyword-only, even in Python 2
        pin_factory = kwargs.pop('pin_factory', None)
        if pin_factory is None:
            if Device.pin_factory is None:
                Device.pin_factory = Device._default_pin_factory()
            self.pin_factory = Device.pin_factory
        else:
            self.pin_factory = pin_factory
        if kwargs:
            raise TypeError("Device.__init__() got unexpected keyword "
                            "argument '%s'" % kwargs.popitem()[0])
        super(Device, self).__init__()

    @staticmethod
    def _default_pin_factory():
        # We prefer RPi.GPIO here as it supports PWM, and all Pi revisions.  If
        # no third-party libraries are available, however, we fall back to a
        # pure Python implementation which supports platforms like PyPy
        #
        # NOTE: If the built-in pin factories are expanded, the dict must be
        # updated along with the entry-points in setup.py.
        default_factories = OrderedDict((
            ('rpigpio', 'gpiozero.pins.rpigpio:RPiGPIOFactory'),
            ('rpio',    'gpiozero.pins.rpio:RPIOFactory'),
            ('pigpio',  'gpiozero.pins.pigpio:PiGPIOFactory'),
            ('native',  'gpiozero.pins.native:NativeFactory'),
        ))
        name = os.environ.get('GPIOZERO_PIN_FACTORY')
        if name is None:
            # If no factory is explicitly specified, try various names in
            # "preferred" order. For speed, we select from the dictionary above
            # rather than importing pkg_resources and using load_entry_point
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
                        PinFactoryFallback(
                            'Falling back from %s: %s' % (name, str(e))))
            raise BadPinFactory('Unable to load any default pin factory!')
        elif name in default_factories:
            # As above, this is a fast-path optimization to avoid loading
            # pkg_resources (which it turns out was 80% of gpiozero's import
            # time!)
            mod_name, cls_name = default_factories[name].split(':', 1)
            module = __import__(mod_name, fromlist=(cls_name,))
            return getattr(module, cls_name)()
        else:
            # Slow path: load pkg_resources and try and find the specified
            # entry-point. Try with the name verbatim first. If that fails,
            # attempt with the lower-cased name (this ensures compatibility
            # names work but we're still case insensitive for all factories)
            import pkg_resources
            group = 'gpiozero_pin_factories'
            for factory in pkg_resources.iter_entry_points(group, name):
                return factory.load()()
            for factory in pkg_resources.iter_entry_points(group, name.lower()):
                return factory.load()()
            raise BadPinFactory('Unable to find pin factory "%s"' % name)

    def __repr__(self):
        return "<gpiozero.%s object>" % (self.__class__.__name__)

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
    def __init__(self, *args, **kwargs):
        self._all = ()
        self._named = frozendict({})
        self._namedtuple = None
        self._order = kwargs.pop('_order', None)
        pin_factory = kwargs.pop('pin_factory', None)
        try:
            if self._order is None:
                self._order = sorted(kwargs.keys())
            else:
                for missing_name in set(kwargs.keys()) - set(self._order):
                    raise CompositeDeviceBadOrder(
                        '%s missing from _order' % missing_name)
            self._order = tuple(self._order)
            for name in set(self._order) & set(dir(self)):
                raise CompositeDeviceBadName(
                    '%s is a reserved name' % name)
            for dev in chain(args, kwargs.values()):
                if not isinstance(dev, Device):
                    raise CompositeDeviceBadDevice(
                        "%s doesn't inherit from Device" % dev)
            self._named = frozendict(kwargs)
            self._namedtuple = namedtuple(
                '%sValue' % self.__class__.__name__, chain(
                    ('device_%d' % i for i in range(len(args))), self._order))
        except:
            for dev in chain(args, kwargs.values()):
                if isinstance(dev, Device):
                    dev.close()
            raise
        self._all = args + tuple(kwargs[v] for v in self._order)
        super(CompositeDevice, self).__init__(pin_factory=pin_factory)

    def __getattr__(self, name):
        # if _named doesn't exist yet, pretend it's an empty dict
        if name == '_named':
            return frozendict({})
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
            named = len(self._named)
            unnamed = len(self) - len(self._named)
            if named > 0 and unnamed > 0:
                return "<gpiozero.%s object containing %d devices: %s and %d unnamed>" % (
                        self.__class__.__name__,
                        len(self), ', '.join(self._order),
                        len(self) - len(self._named)
                        )
            elif named > 0:
                return "<gpiozero.%s object containing %d devices: %s>" % (
                        self.__class__.__name__,
                        len(self),
                        ', '.join(self._order)
                        )
            else:
                return "<gpiozero.%s object containing %d unnamed devices>" % (
                        self.__class__.__name__,
                        len(self)
                        )
        except DeviceClosed:
            return "<gpiozero.%s object closed>" % (self.__class__.__name__)

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
                if isinstance(device, Device):
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
    def __init__(self, pin=None, **kwargs):
        super(GPIODevice, self).__init__(**kwargs)
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
        super(GPIODevice, self).close()
        if getattr(self, '_pin', None) is not None:
            self.pin_factory.release_pins(self, self._pin.number)
            self._pin.close()
        self._pin = None

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
            return "<gpiozero.%s object on pin %r, is_active=%s>" % (
                self.__class__.__name__, self.pin, self.is_active)
        except DeviceClosed:
            return "<gpiozero.%s object closed>" % self.__class__.__name__


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
