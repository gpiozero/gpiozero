==============
Output Devices
==============

.. currentmodule:: gpiozero

These output device component interfaces have been provided for simple use of
everyday components. Components must be wired up correctly before use in code.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering. See the :doc:`recipes`
    page for more information.


LED
===

.. autoclass:: LED(pin, active_high=True, initial_value=False)
    :members: on, off, toggle, blink, pin, is_lit

PWMLED
======

.. autoclass:: PWMLED(pin, active_high=True, initial_value=0, frequency=100)
    :members: on, off, toggle, blink, pulse, pin, is_lit, value

RGBLED
======

.. autoclass:: RGBLED(red, green, blue, active_high=True, initial_value=(0, 0, 0))
    :members: on, off, toggle, blink, pulse, red, green, blue, is_lit, color

Buzzer
======

.. autoclass:: Buzzer(pin, active_high=True, initial_value=False)
    :members: on, off, toggle, beep, pin, is_active

Motor
=====

.. autoclass:: Motor(forward, backward)
    :members: forward, backward, stop

Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below:

.. image:: images/output_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.

DigitalOutputDevice
===================

.. autoclass:: DigitalOutputDevice(pin, active_high=True, initial_value=False)
    :members:

PWMOutputDevice
===============

.. autoclass:: PWMOutputDevice(pin, active_high=True, initial_value=0, frequency=100)
    :members:

OutputDevice
============

.. autoclass:: OutputDevice(pin, active_high=True, initial_value=False)
    :members:

GPIODevice
==========

.. autoclass:: GPIODevice(pin)
    :members:
    :noindex:

