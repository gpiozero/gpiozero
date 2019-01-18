.. _migrating_from_rpigpio:

=======================
Migrating from RPi.GPIO
=======================

If you are familiar with the `RPi.GPIO`_ library, you will be used to writing
code which deals with *pins* and the state of pins. You will see from the
examples in this documentation that we refer to things like LEDs and Buttons
rather than input pins and output pins.

.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/

GPIO Zero provides classes which represent devices, so instead of having a pin
number and telling it to go high, you have an LED and you tell it to turn on,
and instead of having a pin number and asking if it's high or low, you have a
button and ask if it's pressed. There is also no boilerplate code to get started
- you just import the parts you need.

GPIO Zero provides many device classes, each with specific methods and
properties bespoke to that device. For example, the functionality for an HC-SR04
Distance Sensor can be found in the :class:`DistanceSensor` class.

As well as specific device classes, we provide base classes :class:`InputDevice`
and :class:`OutputDevice`. One main difference between these and the equivalents
in RPi.GPIO is that they are classes, not functions, which means that you
initialize one to begin, and provide its pin number, but then you never need to
use the pin number again, as it's stored by the object.

GPIO Zero was originally just a layer on top of RPi.GPIO, but we later added
support for various other underlying pin libraries. RPi.GPIO is currently the
default pin library used. Read more about this in :ref:`changing-pin-factory`_.

Output devices
==============

Turning a LED on in RPi.GPIO::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(2, GPIO.OUT)

    GPIO.output(2, GPIO.HIGH)

Turning a LED on in GPIO Zero:

    from gpiozero import LED

    led = LED(2)

    led.on()

The :class:`LED` class also supports threaded blinking through the
:meth:`LED.blink` method.

:class:`OutputDevice` is the base class for output devices, and can be used in a
similar way to output devices in RPi.GPIO.

See a full list of supported :ref:`api_output`.

Input devices
=============

Reading a button press in RPi.GPIO::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(3, GPIO.IN, GPIO.PUD_UP)

    if not GPIO.input(3):
        print("button is pressed")

Reading a button press in GPIO Zero::

    from gpiozero import Button

    btn = Button(3)

    if btn.is_pressed:
        print("button is pressed")

Note that in the RPi.GPIO example, the button is set up with the option
``GPIO.PUD_UP`` which means "pull-up", and therefore when the button is not
pressed, the pin is high. When the button is pressed, the pin goes low, so the
condition requires negation (``if not``). If the button was configured as
pull-down, the logic is reversed and the condition would become ``if
GPIO.input(2)``::

    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(3, GPIO.IN, GPIO.PUD_DOWN)

    if GPIO.input(3):
        print("button is pressed")

In GPIO Zero, the default configuration for a button is pull-up, but this can be
configured at initialization, and the rest of the code stays the same::

    from gpiozero import Button

    btn = Button(4, pull_up=False)

    if btn.is_pressed:
        print("button is pressed")

:class:`InputDevice` is the base class for input devices, and can be used in a
similar way to input devices in RPi.GPIO.

See a full list of :ref:`api_input`.

Composite devices, boards and accessories
=========================================

Some devices require connections to multiple pins, for example a distance
sensor, a combination of LEDs or a HAT. Some GPIO Zero devices comprise multiple
device connections within one object, such as :class:`RGBLED`,
:class:`LEDBoard`, :class:`DistanceSensor`, :class:`Motor` and :class:`Robot`.

With RPi.GPIO, you would have one output pin for the trigger, and one input pin
for the echo. You would time the echo and calculate the distance. With GPIO
Zero, you create a single :class:`DistanceSensor` object, specifying the trigger
and echo pins, and you would read the :attr:`DistanceSensor.distance` property
which automatically calculates the distance within the implementation of the
class.

The :class:`Motor` class controls two output pins to drive the motor forwards or
backwards. The :class:`Robot` class controls four output pins (two motors) in
the right combination to drive a robot forwards or backwards, and turn left and
right.

The :class:`LEDBoard` class takes an arbitrary number of pins, each controlling
a single LED. The resulting :class:`LEDBoard` object can be used to control
all LEDs together (all on / all off), or individually by index. Also the object
can be iterated over to turn LEDs on in order. See examples of this (including
slicing) in the advanced recipes: :ref:`_ledboard-advanced`.

PWM (Pulse-width modulation)
============================

Both libraries support software PWM control on any pin. Depending on the pin
library used, GPIO Zero can also support hardware PWM (using
:class:`gpiozero.pins.rpigpio.RPIOPin` or
:class:`gpiozero.pins.rpigpio.PiGPIOPin`).

A simple example of using PWM is to control the brightness of an LED.

In RPi.GPIO::

    import RPi.GPIO as GPIO
    from time import sleep

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(2, GPIO.OUT)
    pwm = GPIO.PWM(2, 100)
    pwm.start(0)

    for dc in range(100):
        pwm.changeDutyCycle(dc)
        sleep(0.01)

In GPIO Zero:

    from gpiozero import PWMLED
    from time import sleep

    led = PWMLED(2)

    for b in range(100):
        led.value = b / 100
        sleep(0.01)

:class:`PMWLED` has a :meth:`blink` method which can be used the same was as
:class:`LED`'s :meth:`LED.blink` method, but its PWM capabilities allow for
``fade_in`` and ``fade_out`` options to be provided. There is also the
:meth:`PWMLED.pulse` method which provides a neat way to have an LED fade in and
out repeatedly.

Other devices can make use of PWM, such as motors (for variable speed) and
servos. See the :class:`Motor`, :class:`Servo` and :class:`AngularServo` classes
for information on those. :class:`Motor` and :class:`Robot` default to using
PWM, but it can be disabled with ``pwm=False`` at initialization. Servos cannot
be used without PWM. Devices containing LEDs default to not using PWM, but
``pwm=True`` can be specified and any LED objects within the device will be
initialized as :class:`PWMLED` objects.

Cleanup
=======

Pin state cleanup is explicit in RPi.GPIO, and is done manually with
``GPIO.cleanup()`` but in GPIO Zero, cleanup is automatically performed on every
pin used, at the end of the script. Manual cleanup is possible by use of the
:meth:`Device.close` method on the device.

Read more in the relevant FAQ: :ref:`gpio-cleanup`.

Pi Information
==============

RPi.GPIO provides information about the Pi you're using. The equivalent in GPIO
Zero is the function :func:`pi_info`:

.. code-block:: pycon

    >>> from gpiozero import pi_info
    >>> pi = pi_info()
    >>> pi
    PiBoardInfo(revision='a02082', model='3B', pcb_revision='1.2'...
    >>> pi.soc
    'BCM2837'
    >>> pi.wifi
    True

Read more about what :class:`PiInfo` provides.

More
====

GPIO Zero provides more than just GPIO device support, it includes some support
for :ref:`api_spi` including a range of analog to digital converters.

Device classes which are compatible with other GPIO devices, but have no
relation to GPIO pins, such as :class:`CPUtemperature`, :class:`TimeOfDay`,
:class:`PingServer` and :class:`LoadAverage` are also provided.

GPIO Zero features support for multiple pin libraries. The default is to use
``RPi.GPIO`` to control the pins, but you can choose to use another library,
such as ``pigpio``, which supports network controlled GPIO. See
:ref:`changing-pin-factory` and :ref:`remote_gpio` for more information.

It is possible to run GPIO Zero on your PC, both for remote GPIO and for testing
purposes, using :ref:`mock-pins`.

Another feature of this library is configuring devices to be connected together
in a logical way, for example in one line you can say that an LED and button are
"paired", i.e. the button being pressed turns the LED on. Read about this in
:ref:`source_values`.
