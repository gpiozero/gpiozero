=============
Basic Recipes
=============

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the GPIO Zero
library. Please note that all recipes are written assuming Python 3. Recipes
*may* work under Python 2, but no guarantees!

Importing GPIO Zero
===================

.. module:: gpiozero

In Python, libraries and functions used in a script must be imported by name
at the top of the file, with the exception of the functions built into Python
by default.

For example, to use the :class:`Button` interface from GPIO Zero, it
should be explicitly imported::

    from gpiozero import Button

Now :class:`~gpiozero.Button` is available directly in your script::

    button = Button(2)

Alternatively, the whole GPIO Zero library can be imported::

    import gpiozero

In this case, all references to items within GPIO Zero must be prefixed::

    button = gpiozero.Button(2)

.. _pin-numbering:

Pin Numbering
=============

This library uses Broadcom (BCM) pin numbering for the GPIO pins, as opposed
to physical (BOARD) numbering. Unlike in the `RPi.GPIO`_ library, this is not
configurable.

.. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO

Any pin marked "GPIO" in the diagram below can be used as a pin number.  For
example, if an LED was attached to "GPIO17" you would specify the pin number as
17 rather than 11:

.. image:: images/pin_layout.*
    :align: center

LED
===

.. image:: images/led.*

Turn an :class:`LED` on and off repeatedly:

.. literalinclude:: examples/led_1.py

Alternatively:

.. literalinclude:: examples/led_2.py

.. note::

    Reaching the end of a Python script will terminate the process and GPIOs
    may be reset. Keep your script alive with :func:`signal.pause`. See
    :ref:`keep-your-script-running` for more information.

LED with variable brightness
============================

Any regular LED can have its brightness value set using PWM
(pulse-width-modulation). In GPIO Zero, this can be achieved using
:class:`PWMLED` using values between 0 and 1:

.. literalinclude:: examples/led_variable_brightness.py

Similarly to blinking on and off continuously, a PWMLED can pulse (fade in and
out continuously):

.. literalinclude:: examples/led_pulse.py

Button
======

.. image:: images/button.*

Check if a :class:`Button` is pressed:

.. literalinclude:: examples/button_1.py

Wait for a button to be pressed before continuing:

.. literalinclude:: examples/button_2.py

Run a function every time the button is pressed:

.. literalinclude:: examples/button_3.py
    :emphasize-lines: 9

.. note::

    Note that the line ``button.when_pressed = say_hello`` does not run the
    function ``say_hello``, rather it creates a reference to the function to
    be called when the button is pressed. Accidental use of
    ``button.when_pressed = say_hello()`` would set the ``when_pressed`` action
    to ``None`` (the return value of this function) which would mean nothing
    happens when the button is pressed.

Similarly, functions can be attached to button releases:

.. literalinclude:: examples/button_4.py

Button controlled LED
=====================

.. image:: images/led_button_bb.*

Turn on an :class:`LED` when a :class:`Button` is pressed:

.. literalinclude:: examples/button_led_1.py

Alternatively:

.. literalinclude:: examples/button_led_2.py

Button controlled camera
========================

Using the button press to trigger :class:`~picamera.PiCamera` to take a picture
using ``button.when_pressed = camera.capture`` would not work because the
:meth:`~picamera.PiCamera.capture` method requires an ``output`` parameter.
However, this can be achieved using a custom function which requires no
parameters:

.. literalinclude:: examples/button_camera_1.py
    :emphasize-lines: 9-11

Another example could use one button to start and stop the camera preview, and
another to capture:

.. literalinclude:: examples/button_camera_2.py

Shutdown button
===============

The :class:`Button` class also provides the ability to run a function when the
button has been held for a given length of time. This example will shut down
the Raspberry Pi when the button is held for 2 seconds:

.. literalinclude:: examples/button_shutdown.py

LEDBoard
========

A collection of LEDs can be accessed using :class:`LEDBoard`:

.. literalinclude:: examples/led_board_1.py

Using :class:`LEDBoard` with ``pwm=True`` allows each LED's brightness to be
controlled:

.. literalinclude:: examples/led_board_2.py

See more :class:`LEDBoard` examples in the :ref:`advanced LEDBoard recipes
<ledboard-advanced>`.

LEDBarGraph
===========

A collection of LEDs can be treated like a bar graph using
:class:`LEDBarGraph`:

.. literalinclude:: examples/led_bargraph_2.py

Note values are essentially rounded to account for the fact LEDs can only be on
or off when ``pwm=False`` (the default).

However, using :class:`LEDBarGraph` with ``pwm=True`` allows more precise
values using LED brightness:

.. literalinclude:: examples/led_bargraph_2.py

Traffic Lights
==============

.. image:: images/traffic_lights_bb.*

A full traffic lights system.

Using a :class:`TrafficLights` kit like Pi-Stop:

.. literalinclude:: examples/traffic_lights_1.py

Alternatively:

.. literalinclude:: examples/traffic_lights_2.py

Using :class:`LED` components:

.. literalinclude:: examples/traffic_lights_3.py

Push button stop motion
=======================

Capture a picture with the camera module every time a button is pressed:

.. literalinclude:: examples/button_stop_motion.py

See `Push Button Stop Motion`_ for a full resource.

Reaction Game
=============

.. image:: images/reaction_game_bb.*

When you see the light come on, the first person to press their button wins!

.. literalinclude:: examples/reaction_game.py

See `Quick Reaction Game`_ for a full resource.

GPIO Music Box
==============

Each button plays a different sound!

.. literalinclude:: examples/music_box.py

See `GPIO Music Box`_ for a full resource.

All on when pressed
===================

While the button is pressed down, the buzzer and all the lights come on.

:class:`FishDish`:

.. literalinclude:: examples/all_on_1.py

Ryanteck :class:`TrafficHat`:

.. literalinclude:: examples/all_on_2.py

Using :class:`LED`, :class:`Buzzer`, and :class:`Button` components:

.. literalinclude:: examples/all_on_3.py

Full color LED
==============

.. image:: images/rgb_led_bb.*

Making colours with an :class:`RGBLED`:

.. literalinclude:: examples/rgbled.py

Motion sensor
=============

.. image:: images/motion_sensor_bb.*

Light an :class:`LED` when a :class:`MotionSensor` detects motion:

.. literalinclude:: examples/motion_sensor.py

Light sensor
============

.. image:: images/light_sensor_bb.*

Have a :class:`LightSensor` detect light and dark:

.. literalinclude:: examples/light_sensor_1.py

Run a function when the light changes:

.. literalinclude:: examples/light_sensor_2.py

Or make a :class:`PWMLED` change brightness according to the detected light
level:

.. literalinclude:: examples/light_sensor_3.py

Distance sensor
===============

.. image:: images/distance_sensor_bb.*

.. note::

    In the diagram above, the wires leading from the sensor to the breadboard
    can be omitted; simply plug the sensor directly into the breadboard facing
    the edge (unfortunately this is difficult to illustrate in the diagram
    without sensor's diagram obscuring most of the breadboard!)

Have a :class:`DistanceSensor` detect the distance to the nearest object:

.. literalinclude:: examples/distance_sensor_1.py

Run a function when something gets near the sensor:

.. literalinclude:: examples/distance_sensor_2.py

Motors
======

.. image:: images/motor_bb.*

Spin a :class:`Motor` around forwards and backwards:

.. literalinclude:: examples/motor.py

Robot
=====

.. IMAGE TBD

Make a :class:`Robot` drive around in (roughly) a square:

.. literalinclude:: examples/robot_1.py

Make a robot with a distance sensor that runs away when things get within
20cm of it:

.. literalinclude:: examples/robot_2.py

Button controlled robot
=======================

Use four GPIO buttons as forward/back/left/right controls for a robot:

.. literalinclude:: examples/robot_buttons_1.py

Keyboard controlled robot
=========================

Use up/down/left/right keys to control a robot:

.. literalinclude:: examples/robot_keyboard_1.py

.. note::

    This recipe uses the standard :mod:`curses` module. This module requires
    that Python is running in a terminal in order to work correctly, hence this
    recipe will *not* work in environments like IDLE.

If you prefer a version that works under IDLE, the following recipe should
suffice:

.. literalinclude:: examples/robot_keyboard_2.py

.. note::

    This recipe uses the third-party ``evdev`` module. Install this library
    with ``sudo pip3 install evdev`` first. Be aware that ``evdev`` will only
    work with local input devices; this recipe will *not* work over SSH.

Motion sensor robot
===================

Make a robot drive forward when it detects motion:

.. literalinclude:: examples/robot_motion_1.py

Alternatively:

.. literalinclude:: examples/robot_motion_2.py

Potentiometer
=============

.. image:: images/potentiometer_bb.*

Continually print the value of a potentiometer (values between 0 and 1)
connected to a :class:`MCP3008` analog to digital converter:

.. literalinclude:: examples/pot_1.py

Present the value of a potentiometer on an LED bar graph using PWM to represent
states that won't "fill" an LED:

.. literalinclude:: examples/pot_2.py

Measure temperature with an ADC
===============================

.. IMAGE TBD

Wire a TMP36 temperature sensor to the first channel of an :class:`MCP3008`
analog to digital converter:

.. literalinclude:: examples/thermometer.py

Full color LED controlled by 3 potentiometers
=============================================

Wire up three potentiometers (for red, green and blue) and use each of their
values to make up the colour of the LED:

.. literalinclude:: examples/rgbled_pot_1.py

Alternatively, the following example is identical, but uses the
:attr:`~SourceMixin.source` property rather than a :keyword:`while` loop:

.. literalinclude:: examples/rgbled_pot_2.py
    :emphasize-lines: 9

.. note::

    Please note the example above requires Python 3. In Python 2, :func:`zip`
    doesn't support lazy evaluation so the script will simply hang.

Timed heat lamp
===============

If you have a pet (e.g. a tortoise) which requires a heat lamp to be switched
on for a certain amount of time each day, you can use an `Energenie Pi-mote`_
to remotely control the lamp, and the :class:`TimeOfDay` class to control the
timing:

.. literalinclude:: examples/timed_heat_lamp.py

Internet connection status indicator
====================================

You can use a pair of green and red LEDs to indicate whether or not your
internet connection is working. Simply use the :class:`PingServer` class to
identify whether a ping to `google.com` is successful. If successful, the green
LED is lit, and if not, the red LED is lit:

.. literalinclude:: examples/internet_status_indicator.py

CPU Temperature Bar Graph
=========================

You can read the Raspberry Pi's own CPU temperature using the built-in
:class:`CPUTemperature` class, and display this on a "bar graph" of LEDs:

.. literalinclude:: examples/cpu_temperature_bar_graph.py

More recipes
============

Continue to:

* :doc:`recipes_advanced`
* :doc:`recipes_remote_gpio`


.. _Push Button Stop Motion: https://www.raspberrypi.org/learning/quick-reaction-game/
.. _Quick Reaction Game: https://www.raspberrypi.org/learning/quick-reaction-game/
.. _GPIO Music Box: https://www.raspberrypi.org/learning/gpio-music-box/
.. _Energenie Pi-mote: https://energenie4u.co.uk/catalogue/product/ENER002-2PI
