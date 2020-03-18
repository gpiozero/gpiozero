.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2020 damosurfer <35042619+damosurfer@users.noreply.github.com>
.. Copyright (c) 2020 Andrew Scheller <github@loowis.durge.org>
.. Copyright (c) 2019 Steveis <SteveAmor@users.noreply.github.com>
.. Copyright (c) 2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
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

.. _migrating_from_rpigpio:

=======================
Migrating from RPi.GPIO
=======================

.. currentmodule:: gpiozero

If you are familiar with the `RPi.GPIO`_ library, you will be used to writing
code which deals with *pins* and the *state of pins*. You will see from the
examples in this documentation that we generally refer to things like LEDs and
Buttons rather than input pins and output pins.

GPIO Zero provides classes which represent *devices*, so instead of having a
pin number and telling it to go high, you have an LED and you tell it to turn
on, and instead of having a pin number and asking if it's high or low, you have
a button and ask if it's pressed. There is also no boilerplate code to get
started — you just import the parts you need.

GPIO Zero provides many device classes, each with specific methods and
properties bespoke to that device. For example, the functionality for an
HC-SR04 Distance Sensor can be found in the :class:`DistanceSensor` class.

As well as specific device classes, we provide base classes
:class:`InputDevice` and :class:`OutputDevice`. One main difference between
these and the equivalents in RPi.GPIO is that they are classes, not functions,
which means that you initialize one to begin, and provide its pin number, but
then you never need to use the pin number again, as it's stored by the object.

GPIO Zero was originally just a layer on top of RPi.GPIO, but we later added
support for various other underlying pin libraries. RPi.GPIO is currently the
default pin library used. Read more about this in :ref:`changing-pin-factory`.


Output devices
==============

Turning an LED on in `RPi.GPIO`_::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(2, GPIO.OUT)

    GPIO.output(2, GPIO.HIGH)

Turning an LED on in GPIO Zero::

    from gpiozero import LED

    led = LED(2)

    led.on()

The :class:`LED` class also supports threaded blinking through the
:meth:`~LED.blink` method.

:class:`OutputDevice` is the base class for output devices, and can be used in a
similar way to output devices in RPi.GPIO.

See a full list of supported :doc:`output devices <api_output>`. Other output
devices have similar property and method names. There is commonality in naming
at base level, such as :attr:`OutputDevice.is_active`, which is aliased in a
device class, such as :attr:`LED.is_lit`.


Input devices
=============

Reading a button press in `RPi.GPIO`_::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)

    if not GPIO.input(4):
        print("button is pressed")

Reading a button press in GPIO Zero::

    from gpiozero import Button

    btn = Button(4)

    if btn.is_pressed:
        print("button is pressed")

Note that in the RPi.GPIO example, the button is set up with the option
``GPIO.PUD_UP`` which means "pull-up", and therefore when the button is not
pressed, the pin is high. When the button is pressed, the pin goes low, so the
condition requires negation (``if not``). If the button was configured as
pull-down, the logic is reversed and the condition would become ``if
GPIO.input(4)``::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(4, GPIO.IN, GPIO.PUD_DOWN)

    if GPIO.input(4):
        print("button is pressed")

In GPIO Zero, the default configuration for a button is pull-up, but this can
be configured at initialization, and the rest of the code stays the same::

    from gpiozero import Button

    btn = Button(4, pull_up=False)

    if btn.is_pressed:
        print("button is pressed")

RPi.GPIO also supports blocking edge detection.

Wait for a pull-up button to be pressed in RPi.GPIO::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)

    GPIO.wait_for_edge(4, GPIO.FALLING):
    print("button was pressed")

The equivalent in GPIO Zero::

    from gpiozero import Buttons

    btn = Button(4)

    btn.wait_for_press()
    print("button was pressed")

Again, if the button is pulled down, the logic is reversed. Instead of waiting
for a falling edge, we're waiting for a rising edge::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)

    GPIO.wait_for_edge(4, GPIO.FALLING):
    print("button was pressed")

Again, in GPIO Zero, the only difference is in the initialization::

    from gpiozero import Buttons

    btn = Button(4, pull_up=False)

    btn.wait_for_press()
    print("button was pressed")

RPi.GPIO has threaded callbacks. You create a function (which must take one
argument), and pass it in to ``add_event_detect``, along with the pin number
and the edge direction::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def pressed(pin):
        print("button was pressed")

    def released(pin):
        print("button was released")

    GPIO.setup(4, GPIO.IN, GPIO.PUD_UP)

    GPIO.add_event_detect(4, GPIO.FALLING, pressed)
    GPIO.add_event_detect(4, GPIO.RISING, released)

In GPIO Zero, you assign the :attr:`~Button.when_pressed` and
:attr:`~Button.when_released` properties to set up callbacks on those actions::

    from gpiozero import Buttons

    def pressed():
        print("button was pressed")

    def released():
        print("button was released")

    btn = Button(4)

    btn.when_pressed = pressed
    btn.when_released = released

:attr:`~Button.when_held` is also provided, where the length of time considered
a "hold" is configurable.

The callback functions don't have to take any arguments, but if they take one,
the button object is passed in, allowing you to determine which button called
the function.

:class:`InputDevice` is the base class for input devices, and can be used in a
similar way to input devices in RPi.GPIO.

See a full list of :doc:`input devices <api_input>`. Other input devices have
similar property and method names. There is commonality in naming at base level,
such as :attr:`InputDevice.is_active`, which is aliased in a device class, such
as :attr:`Button.is_pressed` and :attr:`LightSensor.light_detected`.


Composite devices, boards and accessories
=========================================

Some devices require connections to multiple pins, for example a distance
sensor, a combination of LEDs or a HAT. Some GPIO Zero devices comprise
multiple device connections within one object, such as :class:`RGBLED`,
:class:`LEDBoard`, :class:`DistanceSensor`, :class:`Motor` and :class:`Robot`.

With RPi.GPIO, you would have one output pin for the trigger, and one input pin
for the echo. You would time the echo and calculate the distance. With GPIO
Zero, you create a single :class:`DistanceSensor` object, specifying the
trigger and echo pins, and you would read the :attr:`DistanceSensor.distance`
property which automatically calculates the distance within the implementation
of the class.

The :class:`Motor` class controls two output pins to drive the motor forwards
or backwards. The :class:`Robot` class controls four output pins (two motors)
in the right combination to drive a robot forwards or backwards, and turn left
and right.

The :class:`LEDBoard` class takes an arbitrary number of pins, each controlling
a single LED. The resulting :class:`LEDBoard` object can be used to control all
LEDs together (all on / all off), or individually by index. Also the object can
be iterated over to turn LEDs on in order. See examples of this (including
slicing) in the :ref:`advanced recipes <ledboard-advanced>`.


PWM (Pulse-width modulation)
============================

Both libraries support software PWM control on any pin. Depending on the pin
library used, GPIO Zero can also support hardware PWM (using
:class:`~pins.rpigpio.RPIOPin` or :class:`~pins.rpigpio.PiGPIOPin`).

A simple example of using PWM is to control the brightness of an LED.

In `RPi.GPIO`_::

    import RPi.GPIO as GPIO
    from time import sleep

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(2, GPIO.OUT)
    pwm = GPIO.PWM(2, 100)
    pwm.start(0)

    for dc in range(101):
        pwm.changeDutyCycle(dc)
        sleep(0.01)

In GPIO Zero::

    from gpiozero import PWMLED
    from time import sleep

    led = PWMLED(2)

    for b in range(101):
        led.value = b / 100.0
        sleep(0.01)

:class:`PWMLED` has a :meth:`~PWMLED.blink` method which can be used the same
was as :class:`LED`'s :meth:`~LED.blink` method, but its PWM capabilities allow
for ``fade_in`` and ``fade_out`` options to be provided. There is also the
:meth:`~PWMLED.pulse` method which provides a neat way to have an LED fade in
and out repeatedly.

Other devices can make use of PWM, such as motors (for variable speed) and
servos. See the :class:`Motor`, :class:`Servo` and :class:`AngularServo`
classes for information on those. :class:`Motor` and :class:`Robot` default to
using PWM, but it can be disabled with ``pwm=False`` at initialization. Servos
cannot be used without PWM. Devices containing LEDs default to not using PWM,
but ``pwm=True`` can be specified and any LED objects within the device will be
initialized as :class:`PWMLED` objects.


Cleanup
=======

Pin state cleanup is explicit in RPi.GPIO, and is done manually with
``GPIO.cleanup()`` but in GPIO Zero, cleanup is automatically performed on every
pin used, at the end of the script. Manual cleanup is possible by use of the
:meth:`~Device.close` method on the device.

Read more in the relevant FAQ: :ref:`gpio-cleanup`


Pi Information
==============

RPi.GPIO provides information about the Pi you're using. The equivalent in GPIO
Zero is the function :func:`pi_info`:

.. code-block:: pycon

    >>> from gpiozero import pi_info
    >>> pi = pi_info()
    >>> pi
    PiBoardInfo(revision='a02082', model='3B', pcb_revision='1.2', released='2016Q1', soc='BCM2837', manufacturer='Sony', memory=1024, storage='MicroSD', usb=4, ethernet=1, wifi=True, bluetooth=True, csi=1, dsi=1, headers=..., board=...)
    >>> pi.soc
    'BCM2837'
    >>> pi.wifi
    True

Read more about what :class:`PiBoardInfo` provides.


More
====

GPIO Zero provides more than just GPIO device support, it includes some support
for :doc:`SPI devices <api_spi>` including a range of analog to digital
converters.

Device classes which are compatible with other GPIO devices, but have no
relation to GPIO pins, such as :class:`CPUTemperature`, :class:`TimeOfDay`,
:class:`PingServer` and :class:`LoadAverage` are also provided.

GPIO Zero features support for multiple pin libraries. The default is to use
``RPi.GPIO`` to control the pins, but you can choose to use another library,
such as ``pigpio``, which supports network controlled GPIO. See
:ref:`changing-pin-factory` and :doc:`remote_gpio` for more information.

It is possible to run GPIO Zero on your PC, both for remote GPIO and for testing
purposes, using :ref:`mock-pins`.

Another feature of this library is configuring devices to be connected together
in a logical way, for example in one line you can say that an LED and button are
"paired", i.e. the button being pressed turns the LED on. Read about this in
:doc:`source_values`.


FAQs
====

Note the following FAQs which may catch out users too familiar with RPi.GPIO:

* :ref:`keep-your-script-running`
* :ref:`pinfactoryfallback-warnings`
* :ref:`gpio-cleanup`

.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
