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
    :members: on, off, toggle, blink, pin, is_lit, value

Buzzer
======

.. autoclass:: Buzzer(pin, active_high=True, initial_value=False)
    :members: on, off, toggle, beep, pin, is_active

RGBLED
======

.. autoclass:: RGBLED(red, green, blue, active_high=True)
    :members: on, off, red, green, blue, value

Motor
=====

.. autoclass:: Motor(forward, backward)
    :members: forward, backward, stop
