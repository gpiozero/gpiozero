# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
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

import inspect
import weakref
from functools import wraps, partial
from threading import Event
from collections import deque
try:
    from statistics import median
except ImportError:
    from .compat import median
import warnings

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

class ValuesMixin(object):
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


class SourceMixin(object):
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
        super(SourceMixin, self).__init__(*args, **kwargs)

    def close(self):
        self.source = None
        super(SourceMixin, self).close()

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

    When :meth:`~Device.close` is called, an internal reference counter will be
    decremented and the instance will only close when it reaches zero.
    """
    _instances = {}

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


class EventsMixin(object):
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
        super(EventsMixin, self).__init__(*args, **kwargs)
        self._active_event = Event()
        self._inactive_event = Event()
        self._when_activated = None
        self._when_deactivated = None
        self._last_active = None
        self._last_changed = self.pin_factory.ticks()

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

    @property
    def when_activated(self):
        """
        The function to run when the device changes state from inactive to
        active.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """
        return self._when_activated

    @when_activated.setter
    def when_activated(self, value):
        if self.when_activated is None and value is None:
            warnings.warn(CallbackSetToNone(callback_warning))
        self._when_activated = self._wrap_callback(value)

    @property
    def when_deactivated(self):
        """
        The function to run when the device changes state from active to
        inactive.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that deactivated will be
        passed as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """
        return self._when_deactivated

    @when_deactivated.setter
    def when_deactivated(self, value):
        if self.when_deactivated is None and value is None:
            warnings.warn(CallbackSetToNone(callback_warning))
        self._when_deactivated = self._wrap_callback(value)

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

    def _wrap_callback(self, fn):
        if fn is None:
            return None
        elif not callable(fn):
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
                    inspect.getcallargs(wrapped_fn, *(args + (self,)))
                    @wraps(fn)
                    def wrapper():
                        return fn(self)
                    return wrapper
                except TypeError:
                    raise BadEventHandler(
                        'value must be a callable which accepts up to one '
                        'mandatory parameter')

    def _fire_activated(self):
        # These methods are largely here to be overridden by descendents
        if self.when_activated:
            self.when_activated()

    def _fire_deactivated(self):
        # These methods are largely here to be overridden by descendents
        if self.when_deactivated:
            self.when_deactivated()

    def _fire_events(self, ticks, new_active):
        # NOTE: in contrast to the pin when_changed event, this method takes
        # ticks and *is_active* (i.e. the device's .is_active) as opposed to a
        # pin's *state*.
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


class HoldMixin(EventsMixin):
    """
    Extends :class:`EventsMixin` to add the :attr:`when_held` event and the
    machinery to fire that event repeatedly (when :attr:`hold_repeat` is
    :data:`True`) at internals defined by :attr:`hold_time`.
    """
    def __init__(self, *args, **kwargs):
        self._hold_thread = None
        super(HoldMixin, self).__init__(*args, **kwargs)
        self._when_held = None
        self._held_from = None
        self._hold_time = 1
        self._hold_repeat = False
        self._hold_thread = HoldThread(self)

    def close(self):
        if self._hold_thread is not None:
            self._hold_thread.stop()
        self._hold_thread = None
        super(HoldMixin, self).close()

    def _fire_activated(self):
        super(HoldMixin, self)._fire_activated()
        self._hold_thread.holding.set()

    def _fire_deactivated(self):
        self._held_from = None
        super(HoldMixin, self)._fire_deactivated()

    def _fire_held(self):
        if self.when_held:
            self.when_held()

    @property
    def when_held(self):
        """
        The function to run when the device has remained active for
        :attr:`hold_time` seconds.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """
        return self._when_held

    @when_held.setter
    def when_held(self, value):
        self._when_held = self._wrap_callback(value)

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
        super(HoldThread, self).__init__(
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
        super(GPIOQueue, self).__init__(target=self.fill)
        if queue_len < 1:
            raise BadQueueLen('queue_len must be at least one')
        if sample_wait < 0:
            raise BadWaitTime('sample_wait must be 0 or greater')
        if ignore is None:
            ignore = set()
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
