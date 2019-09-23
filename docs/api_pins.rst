.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
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

==========
API - Pins
==========

.. module:: gpiozero.pins

.. currentmodule:: gpiozero

As of release 1.1, the GPIO Zero library can be roughly divided into two
things: pins and the devices that are connected to them. The majority of the
documentation focuses on devices as pins are below the level that most users
are concerned with. However, some users may wish to take advantage of the
capabilities of alternative GPIO implementations or (in future) use GPIO
extender chips. This is the purpose of the pins portion of the library.

When you construct a device, you pass in a pin specification. This is passed to
a pin :class:`Factory` which turns it into a :class:`Pin` implementation.  The
default factory can be queried (and changed) with :attr:`Device.pin_factory`.
However, all classes (even internal devices) accept a *pin_factory* keyword
argument to their constructors permitting the factory to be overridden on a
per-device basis (the reason for allowing per-device factories is made apparent
in the :doc:`remote_gpio` chapter).

This is illustrated in the following flow-chart:

.. image:: images/device_pin_flowchart.*
    :align: center

The default factory is constructed when the first device is initialised; if no
default factory can be constructed (e.g. because no GPIO implementations are
installed, or all of them fail to load for whatever reason), a
:exc:`BadPinFactory` exception will be raised at construction time.

After importing gpiozero, until constructing a gpiozero device, the pin factory
is :data:`None`, but at the point of first construction the default pin factory
will come into effect:

.. code-block:: console

    pi@raspberrypi:~ $ python3
    Python 3.7.3 (default, Apr  3 2019, 05:39:12)
    [GCC 8.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from gpiozero import Device, LED
    >>> print(Device.pin_factory)
    None
    >>> led = LED(2)
    >>> Device.pin_factory
    <gpiozero.pins.rpigpio.RPiGPIOFactory object at 0xb667ae30>
    >>> led.pin_factory
    <gpiozero.pins.rpigpio.RPiGPIOFactory object at 0xb6323530>

As above, on a Raspberry Pi with the RPi.GPIO library installed, (assuming no
environment variables are set), the default pin factory will be
:class:`~gpiozero.pins.rpigpio.RPiGPIOFactory`.

On a PC (with no pin libraries installed and no environment variables set),
importing will work but attempting to create a device will raise
:exc:`BadPinFactory`:

.. code-block:: console

    ben@magicman:~ $ python3
    Python 3.6.8 (default, Aug 20 2019, 17:12:48)
    [GCC 8.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from gpiozero import Device, LED
    >>> print(Device.pin_factory)
    None
    >>> led = LED(2)
    ...
    BadPinFactory: Unable to load any default pin factory!

.. _changing-pin-factory:

Changing the pin factory
========================

The default pin factory can be replaced by specifying a value for the
:envvar:`GPIOZERO_PIN_FACTORY` environment variable. For example:

.. code-block:: console

    pi@raspberrypi:~ $ GPIOZERO_PIN_FACTORY=native python3
    Python 3.7.3 (default, Apr  3 2019, 05:39:12)
    [GCC 8.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from gpiozero import Device
    >>> Device._default_pin_factory()
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>

To set the :envvar:`GPIOZERO_PIN_FACTORY` for the rest of your session you can
:command:`export` this value:

.. code-block:: console

    pi@raspberrypi:~ $ export GPIOZERO_PIN_FACTORY=native
    pi@raspberrypi:~ $ python3
    Python 3.7.3 (default, Apr  3 2019, 05:39:12)
    [GCC 8.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> Device._default_pin_factory()
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>
    >>> quit()
    pi@raspberrypi:~ $ python3
    Python 3.7.3 (default, Apr  3 2019, 05:39:12)
    [GCC 8.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> Device._default_pin_factory()
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>

If you add the :command:`export` command to your :file:`~/.bashrc` file, you'll
set the default pin factory for all future sessions too.

If the environment variable is set, the corresponding pin factory will be used,
otherwise each of the four GPIO pin factories will be attempted to be used in
turn.

The following values, and the corresponding :class:`Factory` and :class:`Pin`
classes are listed in the table below. Factories are listed in the order that
they are tried by default.

+---------+-----------------------------------------------+-------------------------------------------+
| Name    | Factory class                                 | Pin class                                 |
+=========+===============================================+===========================================+
| rpigpio | :class:`gpiozero.pins.rpigpio.RPiGPIOFactory` | :class:`gpiozero.pins.rpigpio.RPiGPIOPin` |
+---------+-----------------------------------------------+-------------------------------------------+
| rpio    | :class:`gpiozero.pins.rpio.RPIOFactory`       | :class:`gpiozero.pins.rpio.RPIOPin`       |
+---------+-----------------------------------------------+-------------------------------------------+
| pigpio  | :class:`gpiozero.pins.pigpio.PiGPIOFactory`   | :class:`gpiozero.pins.pigpio.PiGPIOPin`   |
+---------+-----------------------------------------------+-------------------------------------------+
| native  | :class:`gpiozero.pins.native.NativeFactory`   | :class:`gpiozero.pins.native.NativePin`   |
+---------+-----------------------------------------------+-------------------------------------------+

If you need to change the default pin factory from within a script, either set
:attr:`Device.pin_factory` to the new factory instance to use::

    from gpiozero.pins.native import NativeFactory
    from gpiozero import Device, LED

    Device.pin_factory = NativeFactory()

    # These will now implicitly use NativePin instead of RPiGPIOPin
    led1 = LED(16)
    led2 = LED(17)

Or use the *pin_factory* keyword parameter mentioned above::

    from gpiozero.pins.native import NativeFactory
    from gpiozero import LED

    my_factory = NativeFactory()

    # This will use NativePin instead of RPiGPIOPin for led1
    # but led2 will continue to use RPiGPIOPin
    led1 = LED(16, pin_factory=my_factory)
    led2 = LED(17)

Certain factories may take default information from additional sources.
For example, to default to creating pins with
:class:`gpiozero.pins.pigpio.PiGPIOPin` on a remote pi called "remote-pi"
you can set the :envvar:`PIGPIO_ADDR` environment variable when running your
script:

.. code-block:: console

    $ GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=remote-pi python3 my_script.py

Like the :envvar:`GPIOZERO_PIN_FACTORY` value, these can be exported from your
:file:`~/.bashrc` script too.

.. warning::

    The astute and mischievous reader may note that it is possible to mix
    factories, e.g. using :class:`~gpiozero.pins.rpigpio.RPiGPIOFactory` for
    one pin, and :class:`~gpiozero.pins.native.NativeFactory` for another. This
    is unsupported, and if it results in your script crashing, your components
    failing, or your Raspberry Pi turning into an actual raspberry pie, you
    have only yourself to blame.

    Sensible uses of multiple pin factories are given in :doc:`remote_gpio`.


.. _mock-pins:

Mock pins
=========

There's also a :class:`~gpiozero.pins.mock.MockFactory` which generates entirely
fake pins. This was originally intended for GPIO Zero developers who wish to
write tests for devices without having to have the physical device wired in to
their Pi. However, they have also proven useful in developing GPIO Zero scripts
without having a Pi to hand. This pin factory will never be loaded by default;
it must be explicitly specified, either by setting an environment variable or
setting the pin factory within the script. For example:

.. code-block:: console

    pi@raspberrypi:~ $ GPIOZERO_PIN_FACTORY=mock python3

or:

.. code-block:: python

    from gpiozero import Device, LED
    from gpiozero.pins.mock import MockFactory

    Device.pin_factory = MockFactory()

    led = LED(2)

You can create device objects and inspect their value changing as you'd expect:

.. code-block:: pycon

    pi@raspberrypi:~ $ GPIOZERO_PIN_FACTORY=mock python3
    Python 3.7.3 (default, Apr  3 2019, 05:39:12)
    [GCC 8.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from gpiozero import LED
    >>> led = LED(2)
    >>> led.value
    0
    >>> led.on()
    >>> led.value
    1

You can even control pin state changes to simulate device behaviour:

.. code-block:: pycon

    >>> from gpiozero import LED, Button

    # Construct a couple of devices attached to mock pins 16 and 17, and link the devices
    >>> led = LED(17)
    >>> btn = Button(16)
    >>> led.source = btn

    # Initailly the button isn't "pressed" so the LED should be off
    >>> led.value
    0

    # Drive the pin low (this is what would happen electrically when the button is pressed)
    >>> btn.pin.drive_low()
    # The LED is now on
    >>> led.value
    1

    >>> btn.pin.drive_high()
    # The button is now "released", so the LED should be off again
    >>> led.value
    0

Several sub-classes of mock pins exist for emulating various other things
(pins that do/don't support PWM, pins that are connected together, pins that
drive high after a delay, etc), for example, you have to use
:class:`~gpiozero.pins.mock.MockPWMPin` to be able to use devices requiring PWM:

.. code-block:: console

    pi@raspberrypi:~ $ GPIOZERO_PIN_FACTORY=mock GPIOZERO_MOCK_PIN_CLASS=mockpwmpin python3

or:

.. code-block:: python

    from gpiozero import Device, LED
    from gpiozero.pins.mock import MockFactory, MockPWMPin

    Device.pin_factory = MockFactory(pin_class=MockPWMPin)

    led = LED(2)

Interested users are invited to read the `GPIO Zero test suite`_ for further
examples of usage.

.. _`GPIO Zero test suite`: https://github.com/gpiozero/gpiozero/tree/master/tests

Base classes
============

.. autoclass:: Factory
    :members:

.. autoclass:: Pin
    :members:

.. autoclass:: SPI
    :members:

.. module:: gpiozero.pins.pi

.. autoclass:: gpiozero.pins.pi.PiFactory
    :members:

.. autoclass:: gpiozero.pins.pi.PiPin
    :members:

.. module:: gpiozero.pins.local

.. autoclass:: LocalPiFactory
    :members:

.. autoclass:: LocalPiPin
    :members:


RPi.GPIO
========

.. module:: gpiozero.pins.rpigpio

.. autoclass:: gpiozero.pins.rpigpio.RPiGPIOFactory

.. autoclass:: gpiozero.pins.rpigpio.RPiGPIOPin


RPIO
====

.. module:: gpiozero.pins.rpio

.. autoclass:: gpiozero.pins.rpio.RPIOFactory

.. autoclass:: gpiozero.pins.rpio.RPIOPin


PiGPIO
======

.. module:: gpiozero.pins.pigpio

.. autoclass:: gpiozero.pins.pigpio.PiGPIOFactory

.. autoclass:: gpiozero.pins.pigpio.PiGPIOPin


Native
======

.. module:: gpiozero.pins.native

.. autoclass:: gpiozero.pins.native.NativeFactory

.. autoclass:: gpiozero.pins.native.NativePin


Mock
====

.. module:: gpiozero.pins.mock

.. autoclass:: gpiozero.pins.mock.MockFactory
    :members:

.. autoclass:: gpiozero.pins.mock.MockPin

.. autoclass:: gpiozero.pins.mock.MockPWMPin

.. autoclass:: gpiozero.pins.mock.MockConnectedPin

.. autoclass:: gpiozero.pins.mock.MockChargingPin

.. autoclass:: gpiozero.pins.mock.MockTriggerPin
