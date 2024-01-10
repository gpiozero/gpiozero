# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2018-2021 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import inspect
import weakref
import warnings
from functools import wraps, partial
from threading import Event
from collections import deque
from statistics import median

from .threads import GPIOThread
from .exc import (
    BadEventHandler,
    BadWaitTime,
    BadQueueLen,
    DeviceClosed,
    CallbackSetToNone,
    )

callback_warning = (
    'The callback was set to None. This may have been unintentional '
    'e.g. btn.when_pressed = pressed() instead of btn.when_pressed = pressed'
)


class ValuesMixin:
    """
    Adds a :attr:`values` property to the class which returns an infinite
    generator of readings from the :attr:`~Device.value` property. There is
    rarely a need to use this mixin directly as all base classes in GPIO Zero
    include it.

    .. note::

        Use this mixin *first* in the parent class list.
    """

    @property
    def values(self):
        """
        An infinite iterator of values read from :attr:`value`.
        """
        while True:
            try:
                yield self.value
            except DeviceClosed:
                break


class SourceMixin:
    """
    Adds a :attr:`source` property to the class which, given an iterable or a
    :class:`ValuesMixin` descendent, sets :attr:`~Device.value` to each member
    of that iterable until it is exhausted. This mixin is generally included in
    novel output devices to allow their state to be driven from another device.

    .. note::

        Use this mixin *first* in the parent class list.
    """

    def __init__(self, *args, **kwargs):
        self._source = None
        self._source_thread = None
        self._source_delay = 0.01
        super().__init__(*args, **kwargs)

    def close(self):
        self.source = None
        super().close()

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
            raise BadWaitTime('source_delay must be 0 or greater')
        self._source_delay = float(value)

    @property
    def source(self):
        """
        The iterable to use as a source of values for :attr:`value`.
        """
        return self._source

    @source.setter
    def source(self, value):
        if getattr(self, '_source_thread', None):
            self._source_thread.stop()
        self._source_thread = None
        if isinstance(value, ValuesMixin):
            value = value.values
        self._source = value
        if value is not None:
            self._source_thread = GPIOThread(self._copy_values, (value,))
            self._source_thread.start()


class SharedMixin:
    """
    This mixin marks a class as "shared". In this case, the meta-class
    (GPIOMeta) will use :meth:`_shared_key` to convert the constructor
    arguments to an immutable key, and will check whether any existing
    instances match that key. If they do, they will be returned by the
    constructor instead of a new instance. An internal reference counter is
    used to determine how many times an instance has been "constructed" in this
    way.

    When :meth:`~Device.close` is called, an internal reference counter will be
    decremented and the instance will only close when it reaches zero.
    """
    _instances = {}

    def __del__(self):
        self._refs = 0
        super().__del__()

    @classmethod
    def _shared_key(cls, *args, **kwargs):
        """
        This is called with the constructor arguments to generate a unique
        key (which must be storable in a :class:`dict` and, thus, immutable
        and hashable) representing the instance that can be shared. This must
        be overridden by descendents.
        """
        raise NotImplementedError


class event:
    """
    A descriptor representing a callable event on a class descending from
    :class:`EventsMixin`.

    Instances of this class are very similar to a :class:`property` but also
    deal with notifying the owning class when events are assigned (or
    unassigned) and wrapping callbacks implicitly as appropriate.
    """
    def __init__(self, doc=None):
        self.handlers = {}
        self.__doc__ = doc

    def _wrap_callback(self, instance, fn):
        if not callable(fn):
            raise BadEventHandler('value must be None or a callable')
        # If fn is wrapped with partial (i.e. partial, partialmethod, or wraps
        # has been used to produce it) we need to dig out the "real" function
        # that's been wrapped along with all the mandatory positional args
        # used in the wrapper so we can test the binding
        args = ()
        wrapped_fn = fn
        while isinstance(wrapped_fn, partial):
            args = wrapped_fn.args + args
            wrapped_fn = wrapped_fn.func
        if inspect.isbuiltin(wrapped_fn):
            # We can't introspect the prototype of builtins. In this case we
            # assume that the builtin has no (mandatory) parameters; this is
            # the most reasonable assumption on the basis that pre-existing
            # builtins have no knowledge of gpiozero, and the sole parameter
            # we would pass is a gpiozero object
            return fn
        else:
            # Try binding ourselves to the argspec of the provided callable.
            # If this works, assume the function is capable of accepting no
            # parameters
            try:
                inspect.getcallargs(wrapped_fn, *args)
                return fn
            except TypeError:
                try:
                    # If the above fails, try binding with a single parameter
                    # (ourselves). If this works, wrap the specified callback
                    inspect.getcallargs(wrapped_fn, *(args + (instance,)))
                    @wraps(fn)
                    def wrapper():
                        return fn(instance)
                    return wrapper
                except TypeError:
                    raise BadEventHandler(
                        'value must be a callable which accepts up to one '
                        'mandatory parameter')

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self.handlers.get(id(instance))

    def __set__(self, instance, value):
        if value is None:
            try:
                del self.handlers[id(instance)]
            except KeyError:
                warnings.warn(CallbackSetToNone(callback_warning))
        else:
            self.handlers[id(instance)] = self._wrap_callback(instance, value)
        enabled = any(
            obj.handlers.get(id(instance))
            for name in dir(type(instance))
            for obj in (getattr(type(instance), name),)
            if isinstance(obj, event)
        )
        instance._start_stop_events(enabled)


class EventsMixin:
    """
    Adds edge-detected :meth:`when_activated` and :meth:`when_deactivated`
    events to a device based on changes to the :attr:`~Device.is_active`
    property common to all devices. Also adds :meth:`wait_for_active` and
    :meth:`wait_for_inactive` methods for level-waiting.

    .. note::

        Note that this mixin provides no means of actually firing its events;
        call :meth:`_fire_events` in sub-classes when device state changes to
        trigger the events. This should also be called once at the end of
        initialization to set initial states.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_event = Event()
        self._inactive_event = Event()
        self._last_active = None
        self._last_changed = self.pin_factory.ticks()

    def _all_events(self):
        """
        Generator function which yields all :class:`event` instances defined
        against this class.
        """
        for name in dir(type(self)):
            obj = getattr(type(self), name)
            if isinstance(obj, event):
                yield obj

    def close(self):
        for ev in self._all_events():
            try:
                del ev.handlers[id(self)]
            except KeyError:
                pass
        super().close()

    def wait_for_active(self, timeout=None):
        """
        Pause the script until the device is activated, or the timeout is
        reached.

        :type timeout: float or None
        :param timeout:
            Number of seconds to wait before proceeding. If this is
            :data:`None` (the default), then wait indefinitely until the device
            is active.
        """
        return self._active_event.wait(timeout)

    def wait_for_inactive(self, timeout=None):
        """
        Pause the script until the device is deactivated, or the timeout is
        reached.

        :type timeout: float or None
        :param timeout:
            Number of seconds to wait before proceeding. If this is
            :data:`None` (the default), then wait indefinitely until the device
            is inactive.
        """
        return self._inactive_event.wait(timeout)

    when_activated = event(
        """
        The function to run when the device changes state from inactive to
        active.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated it will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from active to
        inactive.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that deactivated it will be
        passed as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    @property
    def active_time(self):
        """
        The length of time (in seconds) that the device has been active for.
        When the device is inactive, this is :data:`None`.
        """
        if self._active_event.is_set():
            return self.pin_factory.ticks_diff(self.pin_factory.ticks(),
                                               self._last_changed)
        else:
            return None

    @property
    def inactive_time(self):
        """
        The length of time (in seconds) that the device has been inactive for.
        When the device is active, this is :data:`None`.
        """
        if self._inactive_event.is_set():
            return self.pin_factory.ticks_diff(self.pin_factory.ticks(),
                                               self._last_changed)
        else:
            return None

    def _fire_activated(self):
        # These methods are largely here to be overridden by descendents
        if self.when_activated:
            self.when_activated()

    def _fire_deactivated(self):
        # These methods are largely here to be overridden by descendents
        if self.when_deactivated:
            self.when_deactivated()

    def _fire_events(self, ticks, new_active):
        """
        This method should be called by descendents whenever the
        :attr:`~Device.is_active` property is likely to have changed (for
        example, in response to a pin's :attr:`~gpiozero.Pin.state` changing).

        The *ticks* parameter must be set to the time when the change occurred;
        this can usually be obtained from the pin factory's
        :meth:`gpiozero.Factory.ticks` method but some pin implementations will
        implicitly provide the ticks when an event occurs as part of their
        reporting mechanism.

        The *new_active* parameter must be set to the device's
        :attr:`~Device.is_active` value at the time indicated by *ticks* (which
        is not necessarily the value of :attr:`~Device.is_active` right now, if
        the pin factory provides means of reporting a pin's historical state).
        """
        old_active, self._last_active = self._last_active, new_active
        if old_active is None:
            # Initial "indeterminate" state; set events but don't fire
            # callbacks as there's not necessarily an edge
            if new_active:
                self._active_event.set()
            else:
                self._inactive_event.set()
        elif old_active != new_active:
            self._last_changed = ticks
            if new_active:
                self._inactive_event.clear()
                self._active_event.set()
                self._fire_activated()
            else:
                self._active_event.clear()
                self._inactive_event.set()
                self._fire_deactivated()

    def _start_stop_events(self, enabled):
        """
        This is a stub method that only exists to be overridden by descendents.
        It is called when :class:`event` properties are assigned (including
        when set to :data:`None) to permit the owning instance to activate or
        deactivate monitoring facilities.

        For example, if a descendent requires a background thread to monitor a
        device, it would be preferable to only run the thread if event handlers
        are present to respond to it.

        The *enabled* parameter is :data:`False` when all :class:`event`
        properties on the owning class are :data:`None`, and :data:`True`
        otherwise.
        """
        pass


class HoldMixin(EventsMixin):
    """
    Extends :class:`EventsMixin` to add the :attr:`when_held` event and the
    machinery to fire that event repeatedly (when :attr:`hold_repeat` is
    :data:`True`) at internals defined by :attr:`hold_time`.
    """
    def __init__(self, *args, **kwargs):
        self._hold_thread = None
        super().__init__(*args, **kwargs)
        self._when_held = None
        self._held_from = None
        self._hold_time = 1
        self._hold_repeat = False
        self._hold_thread = HoldThread(self)

    def close(self):
        if self._hold_thread is not None:
            self._hold_thread.stop()
        self._hold_thread = None
        super().close()

    def _fire_activated(self):
        super()._fire_activated()
        self._hold_thread.holding.set()

    def _fire_deactivated(self):
        self._held_from = None
        super()._fire_deactivated()

    def _fire_held(self):
        if self.when_held:
            self.when_held()

    when_held = event(
        """
        The function to run when the device has remained active for
        :attr:`hold_time` seconds.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    @property
    def hold_time(self):
        """
        The length of time (in seconds) to wait after the device is activated,
        until executing the :attr:`when_held` handler. If :attr:`hold_repeat`
        is True, this is also the length of time between invocations of
        :attr:`when_held`.
        """
        return self._hold_time

    @hold_time.setter
    def hold_time(self, value):
        if value < 0:
            raise BadWaitTime('hold_time must be 0 or greater')
        self._hold_time = float(value)

    @property
    def hold_repeat(self):
        """
        If :data:`True`, :attr:`when_held` will be executed repeatedly with
        :attr:`hold_time` seconds between each invocation.
        """
        return self._hold_repeat

    @hold_repeat.setter
    def hold_repeat(self, value):
        self._hold_repeat = bool(value)

    @property
    def is_held(self):
        """
        When :data:`True`, the device has been active for at least
        :attr:`hold_time` seconds.
        """
        return self._held_from is not None

    @property
    def held_time(self):
        """
        The length of time (in seconds) that the device has been held for.
        This is counted from the first execution of the :attr:`when_held` event
        rather than when the device activated, in contrast to
        :attr:`~EventsMixin.active_time`. If the device is not currently held,
        this is :data:`None`.
        """
        if self._held_from is not None:
            return self.pin_factory.ticks_diff(self.pin_factory.ticks(),
                                               self._held_from)
        else:
            return None


class HoldThread(GPIOThread):
    """
    Extends :class:`GPIOThread`. Provides a background thread that repeatedly
    fires the :attr:`HoldMixin.when_held` event as long as the owning
    device is active.
    """
    def __init__(self, parent):
        super().__init__(
            target=self.held, args=(weakref.proxy(parent),))
        self.holding = Event()
        self.start()

    def held(self, parent):
        try:
            while not self.stopping.is_set():
                if self.holding.wait(0.1):
                    self.holding.clear()
                    while not (
                            self.stopping.is_set() or
                            parent._inactive_event.wait(parent.hold_time)
                            ):
                        if parent._held_from is None:
                            parent._held_from = parent.pin_factory.ticks()
                        parent._fire_held()
                        if not parent.hold_repeat:
                            break
        except ReferenceError:
            # Parent is dead; time to die!
            pass


class GPIOQueue(GPIOThread):
    """
    Extends :class:`GPIOThread`. Provides a background thread that monitors a
    device's values and provides a running *average* (defaults to median) of
    those values. If the *parent* device includes the :class:`EventsMixin` in
    its ancestry, the thread automatically calls
    :meth:`~EventsMixin._fire_events`.
    """
    def __init__(
            self, parent, queue_len=5, sample_wait=0.0, partial=False,
            average=median, ignore=None):
        assert callable(average)
        if queue_len < 1:
            raise BadQueueLen('queue_len must be at least one')
        if sample_wait < 0:
            raise BadWaitTime('sample_wait must be 0 or greater')
        if ignore is None:
            ignore = set()
        super().__init__(target=self.fill)
        self.queue = deque(maxlen=queue_len)
        self.partial = bool(partial)
        self.sample_wait = float(sample_wait)
        self.full = Event()
        self.parent = weakref.proxy(parent)
        self.average = average
        self.ignore = ignore

    @property
    def value(self):
        if not self.partial:
            self.full.wait()
        try:
            return self.average(self.queue)
        except (ZeroDivisionError, ValueError):
            # No data == inactive value
            return 0.0

    def fill(self):
        try:
            while not self.stopping.wait(self.sample_wait):
                value = self.parent._read()
                if value not in self.ignore:
                    self.queue.append(value)
                if not self.full.is_set() and len(self.queue) >= self.queue.maxlen:
                    self.full.set()
                if (self.partial or self.full.is_set()) and isinstance(self.parent, EventsMixin):
                    self.parent._fire_events(self.parent.pin_factory.ticks(), self.parent.is_active)
        except ReferenceError:
            # Parent is dead; time to die!
            pass
