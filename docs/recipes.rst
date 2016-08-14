=======
Recipes
=======

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the gpiozero
library. Please note that all recipes are written assuming Python 3. Recipes
*may* work under Python 2, but no guarantees!


Pin Numbering
=============

This library uses Broadcom (BCM) pin numbering for the GPIO pins, as opposed
to physical (BOARD) numbering. Unlike in the `RPi.GPIO`_ library, this is not
configurable.

.. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO

Any pin marked ``GPIO`` in the diagram below can be used for generic
components:

.. image:: images/pin_layout.*

LED
===

.. image:: images/led.*

Turn an :class:`LED` on and off repeatedly::

    from gpiozero import LED
    from time import sleep

    red = LED(17)

    while True:
        red.on()
        sleep(1)
        red.off()
        sleep(1)

Alternatively::

    from gpiozero import LED
    from signal import pause

    red = LED(17)

    red.blink()

    pause()

.. note::

    Reaching the end of a Python script will terminate the process and GPIOs
    may be reset. Keep your script alive with :func:`signal.pause`. See
    :ref:`keep-your-script-running` for more information.


LED with variable brightness
============================

Any regular LED can have its brightness value set using PWM (pulse-width-modulation).
In GPIO Zero, this can be achieved using :class:`PWMLED` using values between 0
and 1::

    from gpiozero import PWMLED
    from time import sleep

    led = PWMLED(17)

    while True:
        led.value = 0  # off
        sleep(1)
        led.value = 0.5  # half brightness
        sleep(1)
        led.value = 1  # full brightness
        sleep(1)


Similarly to blinking on and off continuously, a PWMLED can pulse (fade in and
out continuously)::

    from gpiozero import PWMLED
    from signal import pause

    led = PWMLED(17)

    led.pulse()

    pause()


Button
======

.. image:: images/button.*

Check if a :class:`Button` is pressed::

    from gpiozero import Button

    button = Button(2)

    while True:
        if button.is_pressed:
            print("Button is pressed")
        else:
            print("Button is not pressed")

Wait for a button to be pressed before continuing::

    from gpiozero import Button

    button = Button(2)

    button.wait_for_press()
    print("Button was pressed")

Run a function every time the button is pressed::

    from gpiozero import Button
    from signal import pause

    def say_hello():
        print("Hello!")

    button = Button(2)

    button.when_pressed = say_hello

    pause()

.. note::

    Note that the line ``button.when_pressed = say_hello`` does not run the
    function ``say_hello``, rather it creates a reference to the function to
    be called when the button is pressed. Accidental use of
    ``button.when_pressed = say_hello()`` would set the ``when_pressed`` action
    to ``None`` (the return value of this function) which would mean nothing
    happens when the button is pressed.

Similarly, functions can be attached to button releases::

    from gpiozero import Button
    from signal import pause

    def say_hello():
        print("Hello!")

    def say_goodbye():
        print("Goodbye!")

    button = Button(2)

    button.when_pressed = say_hello
    button.when_released = say_goodbye

    pause()


Button controlled LED
=====================

.. image:: images/led_button_bb.*

Turn on an :class:`LED` when a :class:`Button` is pressed::

    from gpiozero import LED, Button
    from signal import pause

    led = LED(17)
    button = Button(2)

    button.when_pressed = led.on
    button.when_released = led.off

    pause()

Alternatively::

    from gpiozero import LED, Button
    from signal import pause

    led = LED(17)
    button = Button(2)

    led.source = button.values

    pause()


Button controlled camera
========================

Using the button press to trigger picamera to take a pitcure using
``button.when_pressed = camera.capture`` would not work because it requires an
``output`` parameter. However, this can be achieved using a custom function
which requires no parameters::
    
    from gpiozero import Button
    from picamera import PiCamera
    from datetime import datetime
    from signal import pause

    button = Button(2)
    camera = PiCamera()

    def capture():
        datetime = datetime.now().isoformat()
        camera.capture('/home/pi/%s.jpg' % datetime)

    button.when_pressed = capture

    pause()

Another example could use one button to start and stop the camera preview, and
another to capture::

    from gpiozero import Button
    from picamera import PiCamera
    from datetime import datetime
    from signal import pause

    left_button = Button(2)
    right_button = Button(3)
    camera = PiCamera()

    def capture():
        datetime = datetime.now().isoformat()
        camera.capture('/home/pi/%s.jpg' % datetime)

    left_button.when_pressed = camera.start_preview
    left_button.when_released = camera.stop_preview
    right_button.when_pressed = capture

    pause()


Shutdown button
===============

The :class:`Button` class also provides the ability to run a function when the
button has been held for a given length of time. This example will shut down
the Raspberry Pi when the button is held for 2 seconds::

	from gpiozero import Button
	from subprocess import check_call
	from signal import pause

	def shutdown():
	    check_call(['sudo', 'poweroff'])

	shutdown_btn = Button(17, hold_time=2)
	shutdown_btn.when_held = shutdown

	pause() 

LEDBoard
========

A collection of LEDs can be accessed using :class:`LEDBoard`::

    from gpiozero import LEDBoard
    from time import sleep
    from signal import pause

    leds = LEDBoard(5, 6, 13, 19, 26)

    leds.on()
    sleep(1)
    leds.off()
    sleep(1)
    leds.value = (1, 0, 1, 0, 1)
    sleep(1)
    leds.blink()

    pause()

Using :class:`LEDBoard` with ``pwm=True`` allows each LED's brightness to be
controlled::

    from gpiozero import LEDBoard

    leds = LEDBoard(5, 6, 13, 19, 26, pwm=True)

    leds.value = (0.2, 0.4, 0.6, 0.8, 1.0)

LEDBarGraph
===========

A collection of LEDs can be treated like a bar graph using
:class:`LEDBarGraph`::

    from gpiozero import LEDBarGraph
    from time import sleep

    graph = LEDBarGraph(5, 6, 13, 19, 26, 20)

    graph.value = 1  # (1, 1, 1, 1, 1, 1)
    sleep(1)
    graph.value = 1/2  # (1, 1, 1, 0, 0, 0)
    sleep(1)
    graph.value = -1/2  # (0, 0, 0, 1, 1, 1)
    sleep(1)
    graph.value = 1/4  # (1, 0, 0, 0, 0, 0)
    sleep(1)
    graph.value = -1  # (1, 1, 1, 1, 1, 1)
    sleep(1)

Note values are essentially rounded to account for the fact LEDs can only be on
or off when ``pwm=False`` (the default).

However, using :class:`LEDBarGraph` with ``pwm=True`` allows more precise
values using LED brightness::

    from gpiozero import LEDBarGraph
    from time import sleep

    graph = LEDBarGraph(5, 6, 13, 19, 26, pwm=True)

    graph.value = 1/10  # (0.5, 0, 0, 0, 0)
    sleep(1)
    graph.value = 3/10  # (1, 0.5, 0, 0, 0)
    sleep(1)
    graph.value = -3/10  # (0, 0, 0, 0.5, 1)
    sleep(1)
    graph.value = 9/10  # (1, 1, 1, 1, 0.5)
    sleep(1)
    graph.value = 95/100  # (1, 1, 1, 1, 0.75)
    sleep(1)


Traffic Lights
==============

.. image:: images/traffic_lights_bb.*

A full traffic lights system.

Using a :class:`TrafficLights` kit like Pi-Stop::

    from gpiozero import TrafficLights
    from time import sleep

    lights = TrafficLights(2, 3, 4)

    lights.green.on()

    while True:
        sleep(10)
        lights.green.off()
        lights.amber.on()
        sleep(1)
        lights.amber.off()
        lights.red.on()
        sleep(10)
        lights.amber.on()
        sleep(1)
        lights.green.on()
        lights.amber.off()
        lights.red.off()

Alternatively::

    from gpiozero import TrafficLights
    from time import sleep
    from signal import pause

    lights = TrafficLights(2, 3, 4)

    def traffic_light_sequence():
        while True:
            yield (0, 0, 1) # green
            sleep(10)
            yield (0, 1, 0) # amber
            sleep(1)
            yield (1, 0, 0) # red
            sleep(10)
            yield (1, 1, 0) # red+amber
            sleep(1)

    lights.source = traffic_light_sequence()

    pause()

Using :class:`LED` components::

    from gpiozero import LED
    from time import sleep

    red = LED(2)
    amber = LED(3)
    green = LED(4)

    green.on()
    amber.off()
    red.off()

    while True:
        sleep(10)
        green.off()
        amber.on()
        sleep(1)
        amber.off()
        red.on()
        sleep(10)
        amber.on()
        sleep(1)
        green.on()
        amber.off()
        red.off()


Travis build LED indicator
==========================

Use LEDs to indicate the status of a Travis build. A green light means the
tests are passing, a red light means the build is broken::

    from travispy import TravisPy
    from gpiozero import LED
    from gpiozero.tools import negated
    from time import sleep
    from signal import pause

    def build_passed(repo='RPi-Distro/python-gpiozero', delay=3600):
        t = TravisPy()
        r = t.repo(repo)
        while True:
            yield r.last_build_state == 'passed'
            sleep(delay) # Sleep an hour before hitting travis again

    red = LED(12)
    green = LED(16)

    red.source = negated(green.values)
    green.source = build_passed()
    pause()


Note this recipe requires travispy. Install with ``sudo pip3 install travispy``.

Push button stop motion
=======================

Capture a picture with the camera module every time a button is pressed::

    from gpiozero import Button
    from picamera import PiCamera

    button = Button(2)
    camera = PiCamera()

    camera.start_preview()
    frame = 1
    while True:
        button.wait_for_press()
        camera.capture('/home/pi/frame%03d.jpg' % frame)
        frame += 1

See `Push Button Stop Motion`_ for a full resource.


Reaction Game
=============

.. image:: images/reaction_game_bb.*

When you see the light come on, the first person to press their button wins!

::

    from gpiozero import Button, LED
    from time import sleep
    import random

    led = LED(17)

    player_1 = Button(2)
    player_2 = Button(3)

    time = random.uniform(5, 10)
    sleep(time)
    led.on()

    while True:
        if player_1.is_pressed:
            print("Player 1 wins!")
            break
        if player_2.is_pressed:
            print("Player 2 wins!")
            break

    led.off()

See `Quick Reaction Game`_ for a full resource.


GPIO Music Box
==============

Each button plays a different sound!

::

    from gpiozero import Button
    import pygame.mixer
    from pygame.mixer import Sound
    from signal import pause

    pygame.mixer.init()

    sound_pins = {
        2: Sound("samples/drum_tom_mid_hard.wav"),
        3: Sound("samples/drum_cymbal_open.wav"),
    }

    buttons = [Button(pin) for pin in sound_pins]
    for button in buttons:
        sound = sound_pins[button.pin.number]
        button.when_pressed = sound.play

    pause()

See `GPIO Music Box`_ for a full resource.


All on when pressed
===================

While the button is pressed down, the buzzer and all the lights come on.

:class:`FishDish`::

    from gpiozero import FishDish
    from signal import pause

    fish = FishDish()

    fish.button.when_pressed = fish.on
    fish.button.when_released = fish.off

    pause()

Ryanteck :class:`TrafficHat`::

    from gpiozero import TrafficHat
    from signal import pause

    th = TrafficHat()

    th.button.when_pressed = th.on
    th.button.when_released = th.off

    pause()

Using :class:`LED`, :class:`Buzzer`, and :class:`Button` components::

    from gpiozero import LED, Buzzer, Button
    from signal import pause

    button = Button(2)
    buzzer = Buzzer(3)
    red = LED(4)
    amber = LED(5)
    green = LED(6)

    things = [red, amber, green, buzzer]

    def things_on():
        for thing in things:
            thing.on()

    def things_off():
        for thing in things:
            thing.off()

    button.when_pressed = things_on
    button.when_released = things_off

    pause()


Full color LED
==============

.. image:: images/rgb_led_bb.*

Making colours with an :class:`RGBLED`::

    from gpiozero import RGBLED
    from time import sleep

    led = RGBLED(red=9, green=10, blue=11)

    led.red = 1  # full red
    sleep(1)
    led.red = 0.5  # half red
    sleep(1)

    led.color = (0, 1, 0)  # full green
    sleep(1)
    led.color = (1, 0, 1)  # magenta
    sleep(1)
    led.color = (1, 1, 0)  # yellow
    sleep(1)
    led.color = (0, 1, 1)  # cyan
    sleep(1)
    led.color = (1, 1, 1)  # white
    sleep(1)

    led.color = (0, 0, 0)  # off
    sleep(1)

    # slowly increase intensity of blue
    for n in range(100):
        led.blue = n/100
        sleep(0.1)


Motion sensor
=============

.. image:: images/motion_sensor_bb.*

Light an :class:`LED` when a :class:`MotionSensor` detects motion::

    from gpiozero import MotionSensor, LED
    from signal import pause

    pir = MotionSensor(4)
    led = LED(16)

    pir.when_motion = led.on
    pir.when_no_motion = led.off

    pause()


Light sensor
============

.. image:: images/light_sensor_bb.*

Have a :class:`LightSensor` detect light and dark::

    from gpiozero import LightSensor

    sensor = LightSensor(18)

    while True:
        sensor.wait_for_light()
        print("It's light! :)")
        sensor.wait_for_dark()
        print("It's dark :(")

Run a function when the light changes::

    from gpiozero import LightSensor, LED
    from signal import pause

    sensor = LightSensor(18)
    led = LED(16)

    sensor.when_dark = led.on
    sensor.when_light = led.off

    pause()

Or make a :class:`PWMLED` change brightness according to the detected light
level::

    from gpiozero import LightSensor, PWMLED
    from signal import pause

    sensor = LightSensor(18)
    led = PWMLED(16)

    led.source = sensor.values

    pause()


Distance sensor
===============

.. IMAGE TBD

Have a :class:`DistanceSensor` detect the distance to the nearest object::

    from gpiozero import DistanceSensor
    from time import sleep

    sensor = DistanceSensor(23, 24)

    while True:
        print('Distance to nearest object is', sensor.distance, 'm')
        sleep(1)

Run a function when something gets near the sensor::

    from gpiozero import DistanceSensor, LED
    from signal import pause

    sensor = DistanceSensor(23, 24, max_distance=1, threshold_distance=0.2)
    led = LED(16)

    sensor.when_in_range = led.on
    sensor.when_out_of_range = led.off

    pause()


Motors
======

.. image:: images/motor_bb.*

Spin a :class:`Motor` around forwards and backwards::

    from gpiozero import Motor
    from time import sleep

    motor = Motor(forward=4, backward=14)

    while True:
        motor.forward()
        sleep(5)
        motor.backward()
        sleep(5)


Robot
=====

.. IMAGE TBD

Make a :class:`Robot` drive around in (roughly) a square::

    from gpiozero import Robot
    from time import sleep

    robot = Robot(left=(4, 14), right=(17, 18))

    for i in range(4):
        robot.forward()
        sleep(10)
        robot.right()
        sleep(1)

Make a robot with a distance sensor that runs away when things get within
20cm of it::

    from gpiozero import Robot, DistanceSensor
    from signal import pause

    sensor = DistanceSensor(23, 24, max_distance=1, threshold_distance=0.2)
    robot = Robot(left=(4, 14), right=(17, 18))

    sensor.when_in_range = robot.backward
    sensor.when_out_of_range = robot.stop
    pause()


Button controlled robot
=======================

Use four GPIO buttons as forward/back/left/right controls for a robot::

    from gpiozero import Robot, Button
    from signal import pause

    robot = Robot(left=(4, 14), right=(17, 18))

    left = Button(26)
    right = Button(16)
    fw = Button(21)
    bw = Button(20)

    fw.when_pressed = robot.forward
    fw.when_released = robot.stop

    left.when_pressed = robot.left
    left.when_released = robot.stop

    right.when_pressed = robot.right
    right.when_released = robot.stop

    bw.when_pressed = robot.backward
    bw.when_released = robot.stop

    pause()


Keyboard controlled robot
=========================

Use up/down/left/right keys to control a robot::

    import curses
    from gpiozero import Robot

    robot = Robot(left=(4, 14), right=(17, 18))

    actions = {
        curses.KEY_UP:    robot.forward,
        curses.KEY_DOWN:  robot.backward,
        curses.KEY_LEFT:  robot.left,
        curses.KEY_RIGHT: robot.right,
        }

    def main(window):
        next_key = None
        while True:
            curses.halfdelay(1)
            if next_key is None:
                key = window.getch()
            else:
                key = next_key
                next_key = None
            if key != -1:
                # KEY DOWN
                curses.halfdelay(3)
                action = actions.get(key)
                if action is not None:
                    action()
                next_key = key
                while next_key == key:
                    next_key = window.getch()
                # KEY UP
                robot.stop()

    curses.wrapper(main)

.. note::

    This recipe uses the ``curses`` module. This module requires that Python is
    running in a terminal in order to work correctly, hence this recipe will
    *not* work in environments like IDLE.

If you prefer a version that works under IDLE, the following recipe should
suffice, but will require that you install the evdev library with ``sudo pip3
install evdev`` first::

    from gpiozero import Robot
    from evdev import InputDevice, list_devices, ecodes

    robot = Robot(left=(4, 14), right=(17, 18))

    devices = [InputDevice(device) for device in list_devices()]
    keyboard = devices[0]  # this may vary

    keypress_actions = {
        ecodes.KEY_UP: robot.forward,
        ecodes.KEY_DOWN: robot.backward,
        ecodes.KEY_LEFT: robot.left,
        ecodes.KEY_RIGHT: robot.right,
    }

    for event in keyboard.read_loop():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:  # key down
                keypress_actions[event.code]()
            if event.value == 0:  # key up
                robot.stop()


Motion sensor robot
===================

Make a robot drive forward when it detects motion::

    from gpiozero import Robot, MotionSensor
    from signal import pause

    robot = Robot(left=(4, 14), right=(17, 18))
    pir = MotionSensor(5)

    pir.when_motion = robot.forward
    pir.when_no_motion = robot.stop

    pause()

Alternatively::

    from gpiozero import Robot, MotionSensor
    from signal import pause

    robot = Robot(left=(4, 14), right=(17, 18))
    pir = MotionSensor(5)

    robot.source = zip(pir.values, pir.values)

    pause()


Potentiometer
=============

.. image:: images/potentiometer_bb.*

Continually print the value of a potentiometer (values between 0 and 1)
connected to a :class:`MCP3008` analog to digital converter::

    from gpiozero import MCP3008

    pot = MCP3008(channel=0)
    
    while True:
        print(pot.value)

Present the value of a potentiometer on an LED bar graph using PWM to represent
states that won't "fill" an LED::

    from gpiozero import LEDBarGraph, MCP3008
    from signal import pause

    graph = LEDBarGraph(5, 6, 13, 19, 26, pwm=True)
    pot = MCP3008(channel=0)
    graph.source = pot.values
    pause()


Measure temperature with an ADC
===============================

.. IMAGE TBD

Wire a TMP36 temperature sensor to the first channel of an :class:`MCP3008`
analog to digital converter::

    from gpiozero import MCP3008
    from time import sleep

    def convert_temp(gen):
        for value in gen:
            yield (value * 3.3 - 0.5) * 100

    adc = MCP3008(channel=0)

    for temp in convert_temp(adc.values):
        print('The temperature is', temp, 'C')
        sleep(1)


Full color LED controlled by 3 potentiometers
=============================================

Wire up three potentiometers (for red, green and blue) and use each of their
values to make up the colour of the LED::

    from gpiozero import RGBLED, MCP3008

    led = RGBLED(red=2, green=3, blue=4)
    red_pot = MCP3008(channel=0)
    green_pot = MCP3008(channel=1)
    blue_pot = MCP3008(channel=2)

    while True:
        led.red = red_pot.value
        led.green = green_pot.value
        led.blue = blue_pot.value

Alternatively, the following example is identical, but uses the
:attr:`~SourceMixin.source` property rather than a :keyword:`while` loop::

    from gpiozero import RGBLED, MCP3008
    from signal import pause

    led = RGBLED(2, 3, 4)
    red_pot = MCP3008(0)
    green_pot = MCP3008(1)
    blue_pot = MCP3008(2)

    led.source = zip(red_pot.values, green_pot.values, blue_pot.values)

    pause()

Please note the example above requires Python 3. In Python 2, :func:`zip`
doesn't support lazy evaluation so the script will simply hang.


Controlling the Pi's own LEDs
=============================

On certain models of Pi (specifically the model A+, B+, and 2B) it's possible
to control the power and activity LEDs.  This can be useful for testing GPIO
functionality without the need to wire up your own LEDs (also useful because
the power and activity LEDs are "known good").

Firstly you need to disable the usual triggers for the built-in LEDs. This can
be done from the terminal with the following commands::

    $ echo none | sudo tee /sys/class/leds/led0/trigger
    $ echo gpio | sudo tee /sys/class/leds/led1/trigger

Now you can control the LEDs with gpiozero like so::

    from gpiozero import LED
    from signal import pause

    power = LED(35)
    activity = LED(47)

    activity.blink()
    power.blink()
    pause()

To revert the LEDs to their usual purpose you can either reboot your Pi or
run the following commands::

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


.. _Push Button Stop Motion: https://www.raspberrypi.org/learning/quick-reaction-game/
.. _Quick Reaction Game: https://www.raspberrypi.org/learning/quick-reaction-game/
.. _GPIO Music Box: https://www.raspberrypi.org/learning/gpio-music-box/

