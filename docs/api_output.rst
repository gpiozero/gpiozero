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

.. autoclass:: TonalBuzzer(pin, \*, initial_value=None, mid_note='A4', octaves=1, pin_factory=None)
    :members: play, stop, note_value, is_active, octaves, min_note, mid_note, max_note

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
