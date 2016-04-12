# vim: set fileencoding=utf-8:

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

from .devices import Device
from .mixins import EventsMixin


class InternalDevice(EventsMixin, Device):
    """
    Extends :class:`Device` to provide a basis for devices which have no
    specific hardware representation. These are effectively pseudo-devices and
    usually represent operating system services like the internal clock, file
    systems or network facilities.
    """


class PingServer(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when a
    *host* on the network can be pinged.

    The following example lights an LED while a server is reachable (note the
    use of :attr:`~SourceMixin.source_delay` to ensure the server is not
    flooded with pings)::

        from gpiozero import PingServer, LED
        from signal import pause

        server = PingServer('my-server')
        led = LED(4)
        led.source_delay = 1
        led.source = server.values
        pause()

    :param str host:
        The hostname or IP address to attempt to ping.
    """
    def __init__(self, host):
        self.host = host
        super(PingServer, self).__init__()
        self._fire_events()

    def __repr__(self):
        return '<gpiozero.PingDevice host="%s">' % self.host

    @property
    def value(self):
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
                return False
            else:
                return True


class TimeOfDay(InternalDevice):
    """
    Extends :class:`InternalDevice` to provide a device which is active when
    the computer's clock indicates that the current time is between
    *start_time* and *end_time* (inclusive) which are :class:`~datetime.time`
    instances.

    The following example turns on a lamp attached to an :class:`Energenie`
    plug between 7 and 8 AM::

        from datetime import time
        from gpiozero import TimeOfDay, Energenie
        from signal import pause

        lamp = Energenie(0)
        morning = TimeOfDay(time(7), time(8))
        morning.when_activated = lamp.on
        morning.when_deactivated = lamp.off
        pause()

    :param ~datetime.time start_time:
        The time from which the device will be considered active.

    :param ~datetime.time end_time:
        The time after which the device will be considered inactive.

    :param bool utc:
        If ``True`` (the default), a naive UTC time will be used for the
        comparison rather than a local time-zone reading.
    """
    def __init__(self, start_time, end_time, utc=True):
        self._start_time = None
        self._end_time = None
        self._utc = True
        super(TimeOfDay, self).__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.utc = utc
        self._fire_events()

    def __repr__(self):
        return '<gpiozero.TimeOfDay active between %s and %s %s>' % (
                self.start_time, self.end_time, ('local', 'UTC')[self.utc])

    @property
    def start_time(self):
        """
        The time of day after which the device will be considered active.
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if isinstance(value, datetime):
            value = value.time()
        if not isinstance(value, time):
            raise ValueError('start_time must be a datetime, or time instance')
        self._start_time = value

    @property
    def end_time(self):
        """
        The time of day after which the device will be considered inactive.
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        if isinstance(value, datetime):
            value = value.time()
        if not isinstance(value, time):
            raise ValueError('end_time must be a datetime, or time instance')
        self._end_time = value

    @property
    def utc(self):
        """
        If ``True``, use a naive UTC time reading for comparison instead of a
        local timezone reading.
        """
        return self._utc

    @utc.setter
    def utc(self, value):
        self._utc = bool(value)

    @property
    def value(self):
        if self.utc:
            return self.start_time <= datetime.utcnow().time() <= self.end_time
        else:
            return self.start_time <= datetime.now().time() <= self.end_time

