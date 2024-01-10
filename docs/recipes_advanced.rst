.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2017-2021 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017-2019 Ben Nuttall <ben@bennuttall.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

================
Advanced Recipes
================

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the GPIO Zero
library. Please note that all recipes are written assuming Python 3. Recipes
*may* work under Python 2, but no guarantees!

.. _ledboard-advanced:

LEDBoard
========

You can iterate over the LEDs in a :class:`LEDBoard` object one-by-one:

.. literalinclude:: examples/led_board_3.py

:class:`LEDBoard` also supports indexing. This means you can access the
individual :class:`LED` objects using ``leds[i]`` where ``i`` is an integer
from 0 up to (not including) the number of LEDs:

.. literalinclude:: examples/led_board_4.py

This also means you can use slicing to access a subset of the LEDs:

.. literalinclude:: examples/led_board_5.py

:class:`LEDBoard` objects can have their `LED` objects named upon construction.
This means the individual LEDs can be accessed by their name:

.. literalinclude:: examples/led_board_6.py

:class:`LEDBoard` objects can also be nested within other :class:`LEDBoard`
objects:

.. literalinclude:: examples/led_board_7.py

.. _multichar-display:

Multi-character 7-segment display
=================================

The 7-segment display demonstrated in the previous chapter is often available
in multi-character variants (typically 4 characters long). Such displays are
multiplexed meaning that the LED pins are typically the same as for the single
character display but are shared across all characters. Each character in turn
then has its own common line which can be tied to ground (in the case of a
common cathode display) to enable that particular character. By activating each
character in turn very quickly, the eye can be fooled into thinking four
different characters are being displayed simultaneously.

In such circuits you should not attempt to sink all the current from a single
character (which may have up to 8 LEDs, in the case of a decimal-point, active)
into a single GPIO. Rather, use some appropriate transistor (or similar
component, e.g. an opto-coupler) to tie the digit's cathode to ground, and
control that component from a GPIO.

.. image:: images/7seg_multi_bb.*

This circuit demonstrates a 4-character 7-segment (actually 8-segment, with
decimal-point) display, controlled by the Pi's GPIOs with 4 2N-3904 NPN
transistors to control the digits.

.. warning::

    You are strongly advised to check the data-sheet for your particular
    multi-character 7-segment display. The pin-outs of these displays vary
    significantly and are very likely to be different to that shown on the
    breadboard above. For this reason, the schematic for this circuit is
    provided below; adapt it to your particular display.

.. image:: images/7seg_multi_schem.*

The following code can be used to scroll a message across the display:

.. literalinclude:: examples/multichar_scroll.py


Who's home indicator
====================

Using a number of green-red LED pairs, you can show the status of who's home,
according to which IP addresses you can ping successfully. Note that this
assumes each person's mobile phone has a reserved IP address on the home router.

.. literalinclude:: examples/whos_home_leds.py

Alternatively, using the `STATUS Zero`_ board:

.. literalinclude:: examples/whos_home_status.py

Travis build LED indicator
==========================

Use LEDs to indicate the status of a Travis build. A green light means the
tests are passing, a red light means the build is broken:

.. literalinclude:: examples/led_travis.py

Note this recipe requires `travispy`_. Install with ``sudo pip3 install
travispy``.

Button controlled robot
=======================

Alternatively to the examples in the simple recipes, you can use four buttons
to program the directions and add a fifth button to process them in turn, like
a Bee-Bot or Turtle robot.

.. literalinclude:: examples/robot_buttons_2.py

Robot controlled by 2 potentiometers
====================================

Use two potentiometers to control the left and right motor speed of a robot:

.. literalinclude:: examples/robot_pots_1.py

To include reverse direction, scale the potentiometer values from 0->1 to -1->1:

.. literalinclude:: examples/robot_pots_2.py

.. note::

    Please note the example above requires Python 3. In Python 2, :func:`zip`
    doesn't support lazy evaluation so the script will simply hang.

BlueDot LED
===========

BlueDot is a Python library an Android app which allows you to easily add
Bluetooth control to your Raspberry Pi project. A simple example to control a
LED using the BlueDot app:

.. literalinclude:: examples/bluedot_led.py

Note this recipe requires ``bluedot`` and the associated Android app. See the
`BlueDot documentation`_ for installation instructions.

BlueDot robot
=============

You can create a Bluetooth controlled robot which moves forward when the dot is
pressed and stops when it is released:

.. literalinclude:: examples/bluedot_robot_1.py

Or a more advanced example including controlling the robot's speed and precise
direction:

.. literalinclude:: examples/bluedot_robot_2.py

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

    On the Pi 3 the LEDs are controlled by a GPIO expander which is not
    accessible from gpiozero (yet).


.. _travispy: https://travispy.readthedocs.io/
.. _STATUS Zero: https://thepihut.com/status
.. _BlueDot documentation: https://bluedot.readthedocs.io/en/latest/index.html
