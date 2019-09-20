# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2017-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Jeevan M R <14.jeevan@gmail.com>
# Copyright (c) 2019 Andrew Scheller <github@loowis.durge.org>
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
str = type('')


import os
import io
import subprocess
from datetime import datetime, time
import warnings

from .devices import Device
from .mixins import EventsMixin
from .exc import ThresholdOutOfRange


class InternalDevice(EventsMixin, Device):
    """
    Extends :class:`Device` to provide a basis for devices which have no
    specific hardware representation. These are effectively pseudo-devices and
    usually represent operating system services like the internal clock, file
    systems or network facilities.
    """
    # XXX Add some mechanism to monitor state and fire events on change.


class PingServer(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when a
    *host* on the network can be pinged.

    The following example lights an LED while a server is reachable (note the
    use of :attr:`~SourceMixin.source_delay` to ensure the server is not
    flooded with pings)::

        from gpiozero import PingServer, LED
        from signal import pause

        google = PingServer('google.com')
        led = LED(4)

        led.source_delay = 60  # check once per minute
        led.source = google

        pause()

    :param str host:
        The hostname or IP address to attempt to ping.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, host, pin_factory=None):
        self._host = host
        super(PingServer, self).__init__(pin_factory=pin_factory)
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            return '<gpiozero.PingServer object host="%s">' % self.host
        except:
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


class CPUTemperature(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when
    the CPU temperature exceeds the *threshold* value.

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

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, sensor_file='/sys/class/thermal/thermal_zone0/temp',
            min_temp=0.0, max_temp=100.0, threshold=80.0, pin_factory=None):
        self.sensor_file = sensor_file
        super(CPUTemperature, self).__init__(pin_factory=pin_factory)
        if min_temp >= max_temp:
            raise ValueError('max_temp must be greater than min_temp')
        self.min_temp = min_temp
        self.max_temp = max_temp
        if not min_temp <= threshold <= max_temp:
            warnings.warn(ThresholdOutOfRange(
                'threshold is outside of the range (min_temp, max_temp)'))
        self.threshold = threshold
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            return '<gpiozero.CPUTemperature object temperature=%.2f>' % self.temperature
        except:
            return super(CPUTemperature, self).__repr__()

    @property
    def temperature(self):
        """
        Returns the current CPU temperature in degrees celsius.
        """
        with io.open(self.sensor_file, 'r') as f:
            return float(f.readline().strip()) / 1000

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


class LoadAverage(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when
    the CPU load average exceeds the *threshold* value.

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

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, load_average_file='/proc/loadavg', min_load_average=0.0,
        max_load_average=1.0, threshold=0.8, minutes=5, pin_factory=None):
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
        super(LoadAverage, self).__init__(pin_factory=pin_factory)
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            return '<gpiozero.LoadAverage object load average=%.2f>' % self.load_average
        except:
            return super(LoadAverage, self).__repr__()

    @property
    def load_average(self):
        """
        Returns the current load average.
        """
        with io.open(self.load_average_file, 'r') as f:
            file_columns = f.readline().strip().split()
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


class TimeOfDay(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when
    the computer's clock indicates that the current time is between
    *start_time* and *end_time* (inclusive) which are :class:`~datetime.time`
    instances.

    The following example turns on a lamp attached to an :class:`Energenie`
    plug between 7 and 8 AM::

        from gpiozero import TimeOfDay, Energenie
        from datetime import time
        from signal import pause

        lamp = Energenie(1)
        morning = TimeOfDay(time(7), time(8))

        lamp.source = morning

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

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, start_time, end_time, utc=True, pin_factory=None):
        self._start_time = None
        self._end_time = None
        self._utc = True
        super(TimeOfDay, self).__init__(pin_factory=pin_factory)
        self._start_time = self._validate_time(start_time)
        self._end_time = self._validate_time(end_time)
        if self.start_time == self.end_time:
            raise ValueError('end_time cannot equal start_time')
        self._utc = utc
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            return '<gpiozero.TimeOfDay object active between %s and %s %s>' % (
                self.start_time, self.end_time, ('local', 'UTC')[self.utc])
        except:
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


class DiskUsage(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when
    the disk space used exceeds the *threshold* value.

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

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, filesystem='/', threshold=90.0, pin_factory=None):
        super(DiskUsage, self).__init__(pin_factory=pin_factory)
        os.statvfs(filesystem)
        if not 0 <= threshold <= 100:
            warnings.warn(ThresholdOutOfRange(
                'threshold is outside of the range (0, 100)'))
        self.filesystem = filesystem
        self.threshold = threshold
        self._fire_events(self.pin_factory.ticks(), None)

    def __repr__(self):
        try:
            return '<gpiozero.DiskUsage object usage=%.2f>' % self.usage
        except:
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
