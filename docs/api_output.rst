.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
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

.. autoclass:: LED(pin, \*, active_high=True, initial_value=False, pin_factory=None)
    :members: on, off, toggle, blink, pin, is_lit, value


PWMLED
------

.. autoclass:: PWMLED(pin, \*, active_high=True, initial_value=0, frequency=100, pin_factory=None)
    :members: on, off, toggle, blink, pulse, pin, is_lit, value


RGBLED
------

.. autoclass:: RGBLED(red, green, blue, \*, active_high=True, initial_value=(0, 0, 0), pwm=True, pin_factory=None)
    :members: on, off, toggle, blink, pulse, red, green, blue, is_lit, color, value


Buzzer
------

.. autoclass:: Buzzer(pin, \*, active_high=True, initial_value=False, pin_factory=None)
    :members: on, off, toggle, beep, pin, is_active, value


TonalBuzzer
-----------

.. autoclass:: TonalBuzzer(pin, \*, initial_value=None, mid_tone=Tone('A4'), octaves=1, pin_factory=None)
    :members: play, stop, octaves, min_tone, mid_tone, max_tone, tone, is_active, value


Motor
-----

.. autoclass:: Motor(forward, backward, \*, pwm=True, pin_factory=None)
    :members: forward, backward, reverse, stop, is_active, value


PhaseEnableMotor
----------------

.. autoclass:: PhaseEnableMotor(phase, enable, \*, pwm=True, pin_factory=None)
    :members: forward, backward, reverse, stop, is_active, value


Servo
-----

.. autoclass:: Servo(pin, \*, initial_value=0, min_pulse_width=1/1000, max_pulse_width=2/1000, frame_width=20/1000, pin_factory=None)
    :members:


AngularServo
------------

.. autoclass:: AngularServo(pin, \*, initial_angle=0, min_angle=-90, max_angle=90, min_pulse_width=1/1000, max_pulse_width=2/1000, frame_width=20/1000, pin_factory=None)
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

.. autoclass:: DigitalOutputDevice(pin, \*, active_high=True, initial_value=False, pin_factory=None)
    :members: on, off, blink, value


PWMOutputDevice
---------------

.. autoclass:: PWMOutputDevice(pin, \*, active_high=True, initial_value=0, frequency=100, pin_factory=None)
    :members: on, off, blink, pulse, toggle, frequency, is_active, value


OutputDevice
------------

.. autoclass:: OutputDevice(pin, \*, active_high=True, initial_value=False, pin_factory=None)
    :members:


GPIODevice
----------

.. autoclass:: GPIODevice(pin, \*, pin_factory=None)
    :members:
    :noindex:
