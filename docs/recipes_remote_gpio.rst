===================
Remote GPIO Recipes
===================

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the feature of the
GPIO Zero library. Before you start following these examples, please read up on
preparing your Pi and your host PC to work with :doc:`remote_gpio`.

Please note that all recipes are written assuming Python 3. Recipes *may* work
under Python 2, but no guarantees!

LED + Button
============

Let a button on one Raspberry Pi control the LED of another:

.. literalinclude:: examples/led_button_remote_1.py

LED + 2 Buttons
===============

The LED will come on when both buttons are pressed:

.. literalinclude:: examples/led_button_remote_2.py

Multi-room motion alert
=======================

Install a Raspberry Pi with a motion sensor in each room of your house, and have
an LED indicator showing when there's motion in each room:

.. literalinclude:: examples/multi_room_motion_alert.py

Multi-room doorbell
===================

Install a Raspberry Pi with a buzzer attached in each room you want to hear the
doorbell, and use a push button ad the doorbell::

.. literalinclude:: examples/multi_room_doorbell.py

This could also be used as an internal doorbell (tell people it's time for
dinner from the kitchen).
