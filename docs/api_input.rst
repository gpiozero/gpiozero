===================
API - Input Devices
===================

.. module:: gpiozero.input_devices

.. currentmodule:: gpiozero

These input device component interfaces have been provided for simple use of
everyday components. Components must be wired up correctly before use in code.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering. See the :doc:`recipes`
    page for more information.


Button
======

.. autoclass:: Button(pin, \*, pull_up=True, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None)
    :members: wait_for_press, wait_for_release, pin, is_pressed, is_held, hold_time, held_time, hold_repeat, pull_up, when_pressed, when_released, when_held


Line Sensor (TRCT5000)
======================

.. autoclass:: LineSensor(pin, \*, queue_len=5, sample_rate=100, threshold=0.5, partial=False, pin_factory=None)
    :members: wait_for_line, wait_for_no_line, pin, line_detected, when_line, when_no_line


Motion Sensor (D-SUN PIR)
=========================

.. autoclass:: MotionSensor(pin, \*, queue_len=1, sample_rate=10, threshold=0.5, partial=False, pin_factory=None)
    :members: wait_for_motion, wait_for_no_motion, pin, motion_detected, when_motion, when_no_motion


Light Sensor (LDR)
==================

.. autoclass:: LightSensor(pin, \*, queue_len=5, charge_time_limit=0.01, threshold=0.1, partial=False, pin_factory=None)
    :members: wait_for_light, wait_for_dark, pin, light_detected, when_light, when_dark


Distance Sensor (HC-SR04)
=========================

.. autoclass:: DistanceSensor(echo, trigger, \*, queue_len=30, max_distance=1, threshold_distance=0.3, partial=False, pin_factory=None)
    :members: wait_for_in_range, wait_for_out_of_range, trigger, echo, when_in_range, when_out_of_range, max_distance, distance, threshold_distance

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
==================

.. autoclass:: DigitalInputDevice(pin, \*, pull_up=False, bounce_time=None, pin_factory=None)
    :members:

SmoothedInputDevice
===================

.. autoclass:: SmoothedInputDevice(pin, \*, pull_up=False, threshold=0.5, queue_len=5, sample_wait=0.0, partial=False, pin_factory=None)
    :members:

InputDevice
===========

.. autoclass:: InputDevice(pin, \*, pull_up=False, pin_factory=None)
    :members:

GPIODevice
==========

.. autoclass:: GPIODevice(pin, pin_factory=None)
    :members:

