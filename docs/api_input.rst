=============
Input Devices
=============

.. currentmodule:: gpiozero

These input device component interfaces have been provided for simple use of
everyday components. Components must be wired up correctly before use in code.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering. See the :doc:`recipes`
    page for more information.


Button
======

.. autoclass:: Button(pin, pull_up=True, bounce_time=None)
    :members: wait_for_press, wait_for_release, pin, is_pressed, pull_up, when_pressed, when_released


Motion Sensor (PIR)
===================

.. autoclass:: MotionSensor(pin, queue_len=1, sample_rate=10, threshold=0.5, partial=False)
    :members: wait_for_motion, wait_for_no_motion, pin, motion_detected, when_motion, when_no_motion


Light Sensor (LDR)
==================

.. autoclass:: LightSensor(pin, queue_len=5, charge_time_limit=0.01, threshold=0.1, partial=False)
    :members: wait_for_light, wait_for_dark, pin, light_detected, when_light, when_dark

Analog to Digital Converters (ADC)
==================================

.. autoclass:: MCP3004
    :members: bus, device, channel, value, differential

.. autoclass:: MCP3008
    :members: bus, device, channel, value, differential

.. autoclass:: MCP3204
    :members: bus, device, channel, value, differential

.. autoclass:: MCP3208
    :members: bus, device, channel, value, differential

.. autoclass:: MCP3301
    :members: bus, device, value

.. autoclass:: MCP3302
    :members: bus, device, channel, value, differential

.. autoclass:: MCP3304
    :members: bus, device, channel, value, differential

