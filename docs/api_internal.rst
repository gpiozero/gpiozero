.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
..
.. Redistribution and use in source and binary forms, with or without
.. modification, are permitted provided that the following conditions are met:
..
.. * Redistributions of source code must retain the above copyright notice,
..   this list of conditions and the following disclaimer.
..
.. * Redistributions in binary form must reproduce the above copyright notice,
..   this list of conditions and the following disclaimer in the documentation
..   and/or other materials provided with the distribution.
..
.. * Neither the name of the copyright holder nor the names of its contributors
..   may be used to endorse or promote products derived from this software
..   without specific prior written permission.
..
.. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
.. AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
.. IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
.. ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
.. LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
.. CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
.. SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
.. INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
.. CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
.. ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
.. POSSIBILITY OF SUCH DAMAGE.

======================
API - Internal Devices
======================

.. module:: gpiozero.internal_devices

.. currentmodule:: gpiozero

GPIO Zero also provides several "internal" devices which represent facilities
provided by the operating system itself. These can be used to react to things
like the time of day, or whether a server is available on the network.

.. warning::

    These devices are experimental and their API is not yet considered stable.
    We welcome any comments from testers, especially regarding new "internal
    devices" that you'd find useful!


Regular Classes
===============

The following classes are intended for general use with the devices they are
named after. All classes in this section are concrete (not abstract).


TimeOfDay
---------

.. autoclass:: TimeOfDay(start_time, end_time, \*, utc=True, pin_factory=None)
    :members: start_time, end_time, utc, value


PingServer
----------

.. autoclass:: PingServer(host, \*, pin_factory=None)
    :members: host, value


CPUTemperature
--------------

.. autoclass:: CPUTemperature(sensor_file='/sys/class/thermal/thermal_zone0/temp', \*, min_temp=0.0, max_temp=100.0, threshold=80.0, pin_factory=None)
    :members: temperature, value, is_active


LoadAverage
-----------

.. autoclass:: LoadAverage(load_average_file='/proc/loadavg', \*, min_load_average=0.0, max_load_average=1.0, threshold=0.8, minutes=5, pin_factory=None)
    :members: load_average, value, is_active


DiskUsage
---------

.. autoclass:: DiskUsage(filesystem='/', \*, threshold=90.0, pin_factory=None)
    :members: usage, value, is_active


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/internal_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


InternalDevice
--------------

.. autoclass:: InternalDevice(\*, pin_factory=None)
