================
Advanced Recipes
================

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the GPIO Zero
library. Please note that all recipes are written assuming Python 3. Recipes
*may* work under Python 2, but no guarantees!

Travis build LED indicator
==========================

Use LEDs to indicate the status of a Travis build. A green light means the
tests are passing, a red light means the build is broken:

.. literalinclude:: examples/led_travis.py

Note this recipe requires `travispy`_. Install with ``sudo pip3 install
travispy``.

Button controlled robot
=======================

Alternatively, use four buttons to program the directions and add a fifth
button to process them in turn, like a Bee-Bot or Turtle robot.

.. literalinclude:: examples/robot_buttons_2.py

Controlling the Pi's own LEDs
=============================

On certain models of Pi (specifically the model A+, B+, and 2B) it's possible
to control the power and activity LEDs.  This can be useful for testing GPIO
functionality without the need to wire up your own LEDs (also useful because
the power and activity LEDs are "known good").

Firstly you need to disable the usual triggers for the built-in LEDs. This can
be done from the terminal with the following commands:

.. code-block:: console

    $ echo none | sudo tee /sys/class/leds/led0/trigger
    $ echo gpio | sudo tee /sys/class/leds/led1/trigger

Now you can control the LEDs with gpiozero like so:

.. literalinclude:: examples/led_builtin.py

To revert the LEDs to their usual purpose you can either reboot your Pi or
run the following commands:

.. code-block:: console

    $ echo mmc0 | sudo tee /sys/class/leds/led0/trigger
    $ echo input | sudo tee /sys/class/leds/led1/trigger

.. note::

    On the Pi Zero you can control the activity LED with this recipe, but
    there's no separate power LED to control (it's also worth noting the
    activity LED is active low, so set ``active_high=False`` when constructing
    your LED component).

    On the original Pi 1 (model A or B), the activity LED can be controlled
    with GPIO16 (after disabling its trigger as above) but the power LED is
    hard-wired on.

    On the Pi 3B the LEDs are controlled by a GPIO expander which is not
    accessible from gpiozero (yet).


.. _travispy: https://travispy.readthedocs.io/
