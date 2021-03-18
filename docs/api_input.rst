.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

===================
API - Input Devices
===================

.. module:: gpiozero.input_devices

.. currentmodule:: gpiozero

These input device component interfaces have been provided for simple use of
everyday components. Components must be wired up correctly before use in code.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering by default. See the
    :ref:`pin-numbering` section for more information.


Regular Classes
===============

The following classes are intended for general use with the devices they
represent. All classes in this section are concrete (not abstract).


Button
------

.. autoclass:: Button
    :members: wait_for_press, wait_for_release, pin, is_pressed, is_held, hold_time, held_time, hold_repeat, pull_up, when_pressed, when_released, when_held, value


LineSensor (TRCT5000)
---------------------

.. autoclass:: LineSensor
    :members: wait_for_line, wait_for_no_line, pin, line_detected, when_line, when_no_line, value


MotionSensor (D-SUN PIR)
------------------------

.. autoclass:: MotionSensor
    :members: wait_for_motion, wait_for_no_motion, pin, motion_detected, when_motion, when_no_motion, value


LightSensor (LDR)
-----------------

.. autoclass:: LightSensor
    :members: wait_for_light, wait_for_dark, pin, light_detected, when_light, when_dark, value


DistanceSensor (HC-SR04)
------------------------

.. autoclass:: DistanceSensor
    :members: wait_for_in_range, wait_for_out_of_range, trigger, echo, when_in_range, when_out_of_range, max_distance, distance, threshold_distance, value


RotaryEncoder
-------------

.. autoclass:: RotaryEncoder
    :members: wait_for_rotate, wait_for_rotate_clockwise, wait_for_rotate_counter_clockwise, when_rotated, when_rotated_clockwise, when_rotated_counter_clockwise, steps, value, max_steps, threshold_steps, wrap


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/input_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


DigitalInputDevice
------------------

.. autoclass:: DigitalInputDevice
    :members: wait_for_active, wait_for_inactive, when_activated, when_deactivated, active_time, inactive_time, value


SmoothedInputDevice
-------------------

.. autoclass:: SmoothedInputDevice
    :members: is_active, value, threshold, partial, queue_len


InputDevice
-----------

.. autoclass:: InputDevice
    :members: pull_up, is_active, value


GPIODevice
----------

.. autoclass:: GPIODevice
    :members:
