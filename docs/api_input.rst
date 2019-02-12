.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
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

.. autoclass:: Button(pin, \*, pull_up=True, active_state=None, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None)
    :members: wait_for_press, wait_for_release, pin, is_pressed, is_held, hold_time, held_time, hold_repeat, pull_up, when_pressed, when_released, when_held, value


LineSensor (TRCT5000)
---------------------

.. autoclass:: LineSensor(pin, \*, queue_len=5, sample_rate=100, threshold=0.5, partial=False, pin_factory=None)
    :members: wait_for_line, wait_for_no_line, pin, line_detected, when_line, when_no_line, value


MotionSensor (D-SUN PIR)
------------------------

.. autoclass:: MotionSensor(pin, \*, queue_len=1, sample_rate=10, threshold=0.5, partial=False, pin_factory=None)
    :members: wait_for_motion, wait_for_no_motion, pin, motion_detected, when_motion, when_no_motion, value


LightSensor (LDR)
-----------------

.. autoclass:: LightSensor(pin, \*, queue_len=5, charge_time_limit=0.01, threshold=0.1, partial=False, pin_factory=None)
    :members: wait_for_light, wait_for_dark, pin, light_detected, when_light, when_dark, value


DistanceSensor (HC-SR04)
------------------------

.. autoclass:: DistanceSensor(echo, trigger, \*, queue_len=30, max_distance=1, threshold_distance=0.3, partial=False, pin_factory=None)
    :members: wait_for_in_range, wait_for_out_of_range, trigger, echo, when_in_range, when_out_of_range, max_distance, distance, threshold_distance, value


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

.. autoclass:: DigitalInputDevice(pin, \*, pull_up=False, active_state=None, bounce_time=None, pin_factory=None)
    :members: wait_for_active, wait_for_inactive, when_activated, when_deactivated, active_time, inactive_time, value


SmoothedInputDevice
-------------------

.. autoclass:: SmoothedInputDevice(pin, \*, pull_up=False, active_state=None, threshold=0.5, queue_len=5, sample_wait=0.0, partial=False, pin_factory=None)
    :members: is_active, value, threshold, partial, queue_len


InputDevice
-----------

.. autoclass:: InputDevice(pin, \*, pull_up=False, active_state=None, pin_factory=None)
    :members: pull_up, is_active, value


GPIODevice
----------

.. autoclass:: GPIODevice(pin, pin_factory=None)
    :members:
