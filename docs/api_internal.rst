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
