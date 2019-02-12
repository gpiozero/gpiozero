.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017-2019 Ben Nuttall <ben@bennuttall.com>
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
