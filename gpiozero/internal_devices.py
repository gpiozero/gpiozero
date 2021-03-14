# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2017-2021 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2019 Jeevan M R <14.jeevan@gmail.com>
# Copyright (c) 2019 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)
str = type('')


import os
import io
import subprocess
from datetime import datetime, time
import warnings

from .devices import Device
from .mixins import EventsMixin, event
from .threads import GPIOThread
from .exc import ThresholdOutOfRange, DeviceClosed


class InternalDevice(EventsMixin, Device):
    """
    Extends :class:`Device` to provide a basis for devices which have no
    specific hardware representation. These are effectively pseudo-devices and
    usually represent operating system services like the internal clock, file
    systems or network facilities.
    """
    def __init__(self, pin_factory=None):
        self._closed = False
        super(InternalDevice, self).__init__(pin_factory=pin_factory)

    def close(self):
        self._closed = True
        super(InternalDevice, self).close()

    @property
    def closed(self):
        return self._closed

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.%s object>" % self.__class__.__name__
        except DeviceClosed:
            return "<gpiozero.%s object closed>" % self.__class__.__name__


class PolledInternalDevice(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a background thread to poll
    internal devices that lack any other mechanism to inform the instance of
    changes.
    """
    def __init__(self, event_delay=1.0, pin_factory=None):
        self._event_thread = None
        self._event_delay = event_delay
        super(PolledInternalDevice, self).__init__(pin_factory=pin_factory)

    def close(self):
        try:
            self._start_stop_events(False)
        except AttributeError:
            pass  # pragma: no cover
        super(PolledInternalDevice, self).close()

    @property
    def event_delay(self):
        """
        The delay between sampling the device's value for the purposes of
        firing events.

        Note that this only applies to events assigned to attributes like
        :attr:`~EventsMixin.when_activated` and
        :attr:`~EventsMixin.when_deactivated`. When using the
        :attr:`~SourceMixin.source` and :attr:`~ValuesMixin.values` properties,
        the sampling rate is controlled by the
        :attr:`~SourceMixin.source_delay` property.
        """
        return self._event_delay

    @event_delay.setter
    def event_delay(self, value):
        self._event_delay = float(value)

    def wait_for_active(self, timeout=None):
        self._start_stop_events(True)
        try:
            return super(PolledInternalDevice, self).wait_for_active(timeout)
        finally:
            self._start_stop_events(
                self.when_activated or self.when_deactivated)

    def wait_for_inactive(self, timeout=None):
        self._start_stop_events(True)
        try:
            return super(PolledInternalDevice, self).wait_for_inactive(timeout)
        finally:
            self._start_stop_events(
                self.when_activated or self.when_deactivated)

    def _watch_value(self):
        while not self._event_thread.stopping.wait(self._event_delay):
            self._fire_events(self.pin_factory.ticks(), self.is_active)

    def _start_stop_events(self, enabled):
        if self._event_thread and not enabled:
            self._event_thread.stop()
            self._event_thread = None
        elif not self._event_thread and enabled:
            self._event_thread = GPIOThread(self._watch_value)
            self._event_thread.start()


class PingServer(PolledInternalDevice):
    """
    Extends :class:`PolledInternalDevice` to provide a device which is active
    when a *host* (domain name or IP address) can be pinged.

    The following example lights an LED while ``google.com`` is reachable::

        from gpiozero import PingServer, LED
        from signal import pause

        google = PingServer('google.com')
        led = LED(4)

        google.when_activated = led.on
        google.when_deactivated = led.off

        pause()

    :param str host:
        The hostname or IP address to attempt to ping.

    :type event_delay: float
    :param event_delay:
        The number of seconds between pings (defaults to 10 seconds).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, host, event_delay=10.0, pin_factory=None):
        self._host = host
        super(PingServer, self).__init__(
            event_delay=event_delay, pin_factory=pin_factory)
        self._fire_events(self.pin_factory.ticks(), self.is_active)

    def __repr__(self):
        try:
            self._check_open()
            return '<gpiozero.PingServer object host="%s">' % self.host
        except DeviceClosed:
            return super(PingServer, self).__repr__()

    @property
    def host(self):
        """
        The hostname or IP address to test whenever :attr:`value` is queried.
        """
        return self._host

    @property
    def value(self):
        """
        Returns :data:`1` if the host returned a single ping, and :data:`0`
        otherwise.
        """
        # XXX This is doing a DNS lookup every time it's queried; should we
        # call gethostbyname in the constructor and ping that instead (good
        # for consistency, but what if the user *expects* the host to change
        # address?)
        with io.open(os.devnull, 'wb') as devnull:
            try:
                subprocess.check_call(
                    ['ping', '-c1', self.host],
                    stdout=devnull, stderr=devnull)
            except subprocess.CalledProcessError:
                return 0
            else:
                return 1

    when_activated = event(
        """
        The function to run when the device changes state from inactive
        (host unresponsive) to active (host responsive).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from inactive
        (host responsive) to active (host unresponsive).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)


class CPUTemperature(PolledInternalDevice):
    """
    Extends :class:`PolledInternalDevice` to provide a device which is active
    when the CPU temperature exceeds the *threshold* value.

    The following example plots the CPU's temperature on an LED bar graph::

        from gpiozero import LEDBarGraph, CPUTemperature
        from signal import pause

        # Use minimums and maximums that are closer to "normal" usage so the
        # bar graph is a bit more "lively"
        cpu = CPUTemperature(min_temp=50, max_temp=90)

        print('Initial temperature: {}C'.format(cpu.temperature))

        graph = LEDBarGraph(5, 6, 13, 19, 25, pwm=True)
        graph.source = cpu

        pause()

    :param str sensor_file:
        The file from which to read the temperature. This defaults to the
        sysfs file :file:`/sys/class/thermal/thermal_zone0/temp`. Whatever
        file is specified is expected to contain a single line containing the
        temperature in milli-degrees celsius.

    :param float min_temp:
        The temperature at which :attr:`value` will read 0.0. This defaults to
        0.0.

    :param float max_temp:
        The temperature at which :attr:`value` will read 1.0. This defaults to
        100.0.

    :param float threshold:
        The temperature above which the device will be considered "active".
        (see :attr:`is_active`). This defaults to 80.0.

    :type event_delay: float
    :param event_delay:
        The number of seconds between file reads (defaults to 5 seconds).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, sensor_file='/sys/class/thermal/thermal_zone0/temp',
            min_temp=0.0, max_temp=100.0, threshold=80.0, event_delay=5.0,
            pin_factory=None):
        self.sensor_file = sensor_file
        super(CPUTemperature, self).__init__(
            event_delay=event_delay, pin_factory=pin_factory)
        try:
            if min_temp >= max_temp:
                raise ValueError('max_temp must be greater than min_temp')
            self.min_temp = min_temp
            self.max_temp = max_temp
            if not min_temp <= threshold <= max_temp:
                warnings.warn(ThresholdOutOfRange(
                    'threshold is outside of the range (min_temp, max_temp)'))
            self.threshold = threshold
            self._fire_events(self.pin_factory.ticks(), self.is_active)
        except:
            self.close()
            raise

    def __repr__(self):
        try:
            self._check_open()
            return '<gpiozero.CPUTemperature object temperature=%.2f>' % self.temperature
        except DeviceClosed:
            return super(CPUTemperature, self).__repr__()

    @property
    def temperature(self):
        """
        Returns the current CPU temperature in degrees celsius.
        """
        with io.open(self.sensor_file, 'r') as f:
            return float(f.read().strip()) / 1000

    @property
    def value(self):
        """
        Returns the current CPU temperature as a value between 0.0
        (representing the *min_temp* value) and 1.0 (representing the
        *max_temp* value). These default to 0.0 and 100.0 respectively, hence
        :attr:`value` is :attr:`temperature` divided by 100 by default.
        """
        temp_range = self.max_temp - self.min_temp
        return (self.temperature - self.min_temp) / temp_range

    @property
    def is_active(self):
        """
        Returns :data:`True` when the CPU :attr:`temperature` exceeds the
        *threshold*.
        """
        return self.temperature > self.threshold

    when_activated = event(
        """
        The function to run when the device changes state from inactive to
        active (temperature reaches *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from active to
        inactive (temperature drops below *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)


class LoadAverage(PolledInternalDevice):
    """
    Extends :class:`PolledInternalDevice` to provide a device which is active
    when the CPU load average exceeds the *threshold* value.

    The following example plots the load average on an LED bar graph::

        from gpiozero import LEDBarGraph, LoadAverage
        from signal import pause

        la = LoadAverage(min_load_average=0, max_load_average=2)
        graph = LEDBarGraph(5, 6, 13, 19, 25, pwm=True)

        graph.source = la

        pause()

    :param str load_average_file:
        The file from which to read the load average. This defaults to the
        proc file :file:`/proc/loadavg`. Whatever file is specified is expected
        to contain three space-separated load averages at the beginning of the
        file, representing 1 minute, 5 minute and 15 minute averages
        respectively.

    :param float min_load_average:
        The load average at which :attr:`value` will read 0.0. This defaults to
        0.0.

    :param float max_load_average:
        The load average at which :attr:`value` will read 1.0. This defaults to
        1.0.

    :param float threshold:
        The load average above which the device will be considered "active".
        (see :attr:`is_active`). This defaults to 0.8.

    :param int minutes:
        The number of minutes over which to average the load. Must be 1, 5 or
        15. This defaults to 5.

    :type event_delay: float
    :param event_delay:
        The number of seconds between file reads (defaults to 10 seconds).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, load_average_file='/proc/loadavg', min_load_average=0.0,
        max_load_average=1.0, threshold=0.8, minutes=5, event_delay=10.0,
        pin_factory=None):
        if min_load_average >= max_load_average:
            raise ValueError(
                'max_load_average must be greater than min_load_average')
        self.load_average_file = load_average_file
        self.min_load_average = min_load_average
        self.max_load_average = max_load_average
        if not min_load_average <= threshold <= max_load_average:
            warnings.warn(ThresholdOutOfRange(
                'threshold is outside of the range (min_load_average, '
                'max_load_average)'))
        self.threshold = threshold
        if minutes not in (1, 5, 15):
            raise ValueError('minutes must be 1, 5 or 15')
        self._load_average_file_column = {
            1: 0,
            5: 1,
            15: 2,
        }[minutes]
        super(LoadAverage, self).__init__(
            event_delay=event_delay, pin_factory=pin_factory)
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            self._check_open()
            return '<gpiozero.LoadAverage object load average=%.2f>' % self.load_average
        except DeviceClosed:
            return super(LoadAverage, self).__repr__()

    @property
    def load_average(self):
        """
        Returns the current load average.
        """
        with io.open(self.load_average_file, 'r') as f:
            print(repr(f))
            file_columns = f.read().strip().split()
            return float(file_columns[self._load_average_file_column])

    @property
    def value(self):
        """
        Returns the current load average as a value between 0.0 (representing
        the *min_load_average* value) and 1.0 (representing the
        *max_load_average* value). These default to 0.0 and 1.0 respectively.
        """
        load_average_range = self.max_load_average - self.min_load_average
        return (self.load_average - self.min_load_average) / load_average_range

    @property
    def is_active(self):
        """
        Returns :data:`True` when the :attr:`load_average` exceeds the
        *threshold*.
        """
        return self.load_average > self.threshold

    when_activated = event(
        """
        The function to run when the device changes state from inactive to
        active (load average reaches *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from active to
        inactive (load average drops below *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)


class TimeOfDay(PolledInternalDevice):
    """
    Extends :class:`PolledInternalDevice` to provide a device which is active
    when the computer's clock indicates that the current time is between
    *start_time* and *end_time* (inclusive) which are :class:`~datetime.time`
    instances.

    The following example turns on a lamp attached to an :class:`Energenie`
    plug between 07:00AM and 08:00AM::

        from gpiozero import TimeOfDay, Energenie
        from datetime import time
        from signal import pause

        lamp = Energenie(1)
        morning = TimeOfDay(time(7), time(8))

        morning.when_activated = lamp.on
        morning.when_deactivated = lamp.off

        pause()

    Note that *start_time* may be greater than *end_time*, indicating a time
    period which crosses midnight.

    :param ~datetime.time start_time:
        The time from which the device will be considered active.

    :param ~datetime.time end_time:
        The time after which the device will be considered inactive.

    :param bool utc:
        If :data:`True` (the default), a naive UTC time will be used for the
        comparison rather than a local time-zone reading.

    :type event_delay: float
    :param event_delay:
        The number of seconds between file reads (defaults to 10 seconds).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, start_time, end_time, utc=True, event_delay=5.0,
                 pin_factory=None):
        self._start_time = None
        self._end_time = None
        self._utc = True
        super(TimeOfDay, self).__init__(
            event_delay=event_delay, pin_factory=pin_factory)
        try:
            self._start_time = self._validate_time(start_time)
            self._end_time = self._validate_time(end_time)
            if self.start_time == self.end_time:
                raise ValueError('end_time cannot equal start_time')
            self._utc = utc
            self._fire_events(self.pin_factory.ticks(), self.is_active)
        except:
            self.close()
            raise

    def __repr__(self):
        try:
            self._check_open()
            return '<gpiozero.TimeOfDay object active between %s and %s %s>' % (
                self.start_time, self.end_time, ('local', 'UTC')[self.utc])
        except DeviceClosed:
            return super(TimeOfDay, self).__repr__()

    def _validate_time(self, value):
        if isinstance(value, datetime):
            value = value.time()
        if not isinstance(value, time):
            raise ValueError(
                'start_time and end_time must be a datetime, or time instance')
        return value

    @property
    def start_time(self):
        """
        The time of day after which the device will be considered active.
        """
        return self._start_time

    @property
    def end_time(self):
        """
        The time of day after which the device will be considered inactive.
        """
        return self._end_time

    @property
    def utc(self):
        """
        If :data:`True`, use a naive UTC time reading for comparison instead of
        a local timezone reading.
        """
        return self._utc

    @property
    def value(self):
        """
        Returns :data:`1` when the system clock reads between :attr:`start_time`
        and :attr:`end_time`, and :data:`0` otherwise. If :attr:`start_time` is
        greater than :attr:`end_time` (indicating a period that crosses
        midnight), then this returns :data:`1` when the current time is
        greater than :attr:`start_time` or less than :attr:`end_time`.
        """
        now = datetime.utcnow().time() if self.utc else datetime.now().time()
        if self.start_time < self.end_time:
            return int(self.start_time <= now <= self.end_time)
        else:
            return int(not self.end_time < now < self.start_time)

    when_activated = event(
        """
        The function to run when the device changes state from inactive to
        active (time reaches *start_time*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from active to
        inactive (time reaches *end_time*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)


class DiskUsage(PolledInternalDevice):
    """
    Extends :class:`PolledInternalDevice` to provide a device which is active
    when the disk space used exceeds the *threshold* value.

    The following example plots the disk usage on an LED bar graph::

        from gpiozero import LEDBarGraph, DiskUsage
        from signal import pause

        disk = DiskUsage()

        print('Current disk usage: {}%'.format(disk.usage))

        graph = LEDBarGraph(5, 6, 13, 19, 25, pwm=True)
        graph.source = disk

        pause()

    :param str filesystem:
        A path within the filesystem for which the disk usage needs to be
        computed. This defaults to :file:`/`, which is the root filesystem.

    :param float threshold:
        The disk usage percentage above which the device will be considered
        "active" (see :attr:`is_active`). This defaults to 90.0.

    :type event_delay: float
    :param event_delay:
        The number of seconds between file reads (defaults to 30 seconds).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, filesystem='/', threshold=90.0, event_delay=30.0,
                 pin_factory=None):
        super(DiskUsage, self).__init__(
            event_delay=event_delay, pin_factory=pin_factory)
        os.statvfs(filesystem)
        if not 0 <= threshold <= 100:
            warnings.warn(ThresholdOutOfRange(
                'threshold is outside of the range (0, 100)'))
        self.filesystem = filesystem
        self.threshold = threshold
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            self._check_open()
            return '<gpiozero.DiskUsage object usage=%.2f>' % self.usage
        except DeviceClosed:
            return super(DiskUsage, self).__repr__()

    @property
    def usage(self):
        """
        Returns the current disk usage in percentage.
        """
        return self.value * 100

    @property
    def value(self):
        """
        Returns the current disk usage as a value between 0.0 and 1.0 by
        dividing :attr:`usage` by 100.
        """
        # This slightly convoluted calculation is equivalent to df's "Use%";
        # it calculates the percentage of FS usage as a proportion of the
        # space available to *non-root users*. Technically this means it can
        # exceed 100% (when FS is filled to the point that only root can write
        # to it), hence the clamp.
        vfs = os.statvfs(self.filesystem)
        used = vfs.f_blocks - vfs.f_bfree
        total = used + vfs.f_bavail
        return min(1.0, used / total)

    @property
    def is_active(self):
        """
        Returns :data:`True` when the disk :attr:`usage` exceeds the
        *threshold*.
        """
        return self.usage > self.threshold

    when_activated = event(
        """
        The function to run when the device changes state from inactive to
        active (disk usage reaches *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)

    when_deactivated = event(
        """
        The function to run when the device changes state from active to
        inactive (disk usage drops below *threshold*).

        This can be set to a function which accepts no (mandatory)
        parameters, or a Python function which accepts a single mandatory
        parameter (with as many optional parameters as you like). If the
        function accepts a single mandatory parameter, the device that
        activated it will be passed as that parameter.

        Set this property to ``None`` (the default) to disable the event.
        """)
