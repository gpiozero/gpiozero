.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2019-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017 Ben Nuttall <ben@bennuttall.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

===================
Remote GPIO Recipes
===================

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the remote GPIO
feature of the GPIO Zero library. Before you start following these examples,
please read up on preparing your Pi and your host PC to work with
:doc:`remote_gpio`.

Please note that all recipes are written assuming Python 3. Recipes *may* work
under Python 2, but no guarantees!


LED + Button
============

Let a :class:`Button` on one Raspberry Pi control the :class:`LED` of another:

.. literalinclude:: examples/led_button_remote_1.py


LED + 2 Buttons
===============

The :class:`LED` will come on when both buttons are pressed:

.. literalinclude:: examples/led_button_remote_2.py


Multi-room motion alert
=======================

Install a Raspberry Pi with a :class:`MotionSensor` in each room of your house,
and have an :class:`LED` indicator showing when there's motion in each room:

.. literalinclude:: examples/multi_room_motion_alert.py


Multi-room doorbell
===================

Install a Raspberry Pi with a :class:`Buzzer` attached in each room you want to
hear the doorbell, and use a push :class:`Button` as the doorbell:

.. literalinclude:: examples/multi_room_doorbell.py

This could also be used as an internal doorbell (tell people it's time for
dinner from the kitchen).


Remote button robot
===================

Similarly to the simple recipe for the button controlled :class:`Robot`, this
example uses four buttons to control the direction of a robot. However, using
remote pins for the robot means the control buttons can be separate from the
robot:

.. literalinclude:: examples/remote_button_robot.py


Light sensor + Sense HAT
=========================

The `Sense HAT`_ (not supported by GPIO Zero) includes temperature, humidity
and pressure sensors, but no light sensor. Remote GPIO allows an external
:class:`LightSensor` to be used as well. The Sense HAT LED display can be used
to show different colours according to the light levels:

.. literalinclude:: examples/sense_hat_remote_2.py

Note that in this case, the Sense HAT code must be run locally, and the GPIO
remotely.


.. _Sense HAT: https://www.raspberrypi.org/products/sense-hat/
