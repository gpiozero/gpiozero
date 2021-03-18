.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
..
.. SPDX-License-Identifier: BSD-3-Clause

====================
API - Output Devices
====================

.. module:: gpiozero.output_devices

.. currentmodule:: gpiozero

These output device component interfaces have been provided for simple use of
everyday components. Components must be wired up correctly before use in code.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering by default. See the
    :ref:`pin-numbering` section for more information.


Regular Classes
===============

The following classes are intended for general use with the devices they
represent. All classes in this section are concrete (not abstract).


LED
---

.. autoclass:: LED
    :members: on, off, toggle, blink, pin, is_lit, value


PWMLED
------

.. autoclass:: PWMLED
    :members: on, off, toggle, blink, pulse, pin, is_lit, value


RGBLED
------

.. autoclass:: RGBLED
    :members: on, off, toggle, blink, pulse, red, green, blue, is_lit, color, value


Buzzer
------

.. autoclass:: Buzzer
    :members: on, off, toggle, beep, pin, is_active, value


TonalBuzzer
-----------

.. autoclass:: TonalBuzzer
    :members: play, stop, octaves, min_tone, mid_tone, max_tone, tone, is_active, value


Motor
-----

.. autoclass:: Motor
    :members: forward, backward, reverse, stop, is_active, value


PhaseEnableMotor
----------------

.. autoclass:: PhaseEnableMotor
    :members: forward, backward, reverse, stop, is_active, value


Servo
-----

.. autoclass:: Servo
    :members:


AngularServo
------------

.. autoclass:: AngularServo
    :members: angle, max_angle, min_angle, min, max, mid, is_active, value


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/output_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


DigitalOutputDevice
-------------------

.. autoclass:: DigitalOutputDevice
    :members: on, off, blink, value


PWMOutputDevice
---------------

.. autoclass:: PWMOutputDevice
    :members: on, off, blink, pulse, toggle, frequency, is_active, value


OutputDevice
------------

.. autoclass:: OutputDevice
    :members:


GPIODevice
----------

.. autoclass:: GPIODevice
    :members:
    :noindex:
