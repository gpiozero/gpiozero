.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2018-2021 Ben Nuttall <ben@bennuttall.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

======================
API - Internal Devices
======================

.. module:: gpiozero.internal_devices

.. currentmodule:: gpiozero

GPIO Zero also provides several "internal" devices which represent facilities
provided by the operating system itself. These can be used to react to things
like the time of day, or whether a server is available on the network.

These devices provide an API similar to and compatible with GPIO devices so that
internal device events can trigger changes to GPIO output devices the way input
devices can. In the same way a :class:`~gpiozero.Button` object is *active* when
it's pressed, and can be used to trigger other devices when its state changes,
a :class:`TimeOfDay` object is *active* during a particular time period.

Consider the following code in which a :class:`~gpiozero.Button` object is used
to control an :class:`~gpiozero.LED` object::

    from gpiozero import LED, Button
    from signal import pause

    led = LED(2)
    btn = Button(3)

    btn.when_pressed = led.on
    btn.when_released = led.off

    pause()

Now consider the following example in which a :class:`TimeOfDay` object is used
to control an :class:`~gpiozero.LED` using the same method::

    from gpiozero import LED, TimeOfDay
    from datetime import time
    from signal import pause

    led = LED(2)
    tod = TimeOfDay(time(9), time(10))

    tod.when_activated = led.on
    tod.when_deactivated = led.off

    pause()

Here, rather than the LED being controlled by the press of a button, it's
controlled by the time. When the time reaches 09:00AM, the LED comes on, and at
10:00AM it goes off.

Like the :class:`~gpiozero.Button` object, internal devices like the
:class:`TimeOfDay` object has :attr:`~TimeOfDay.value`,
:attr:`~TimeOfDay.values`, :attr:`~TimeOfDay.is_active`,
:attr:`~TimeOfDay.when_activated` and :attr:`~TimeOfDay.when_deactivated`
attributes, so alternative methods using the other paradigms would also work.

.. note::
    Note that although the constructor parameter ``pin_factory`` is available
    for internal devices, and is required to be valid, the pin factory chosen
    will not make any practical difference. Reading a remote Pi's CPU
    temperature, for example, is not currently possible.


Regular Classes
===============

The following classes are intended for general use with the devices they are
named after. All classes in this section are concrete (not abstract).


TimeOfDay
---------

.. autoclass:: TimeOfDay
    :members: start_time, end_time, utc, value, is_active, when_activated, when_deactivated


PingServer
----------

.. autoclass:: PingServer
    :members: host, value, is_active, when_activated, when_deactivated


CPUTemperature
--------------

.. autoclass:: CPUTemperature
    :members: temperature, value, is_active, when_activated, when_deactivated


LoadAverage
-----------

.. autoclass:: LoadAverage
    :members: load_average, value, is_active, when_activated, when_deactivated


DiskUsage
---------

.. autoclass:: DiskUsage
    :members: usage, value, is_active, when_activated, when_deactivated


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/internal_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


PolledInternalDevice
--------------------

.. autoclass:: PolledInternalDevice


InternalDevice
--------------

.. autoclass:: InternalDevice
