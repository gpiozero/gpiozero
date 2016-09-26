====
Pins
====

.. currentmodule:: gpiozero

As of release 1.1, the GPIO Zero library can be roughly divided into two
things: pins and the devices that are connected to them. The majority of the
documentation focuses on devices as pins are below the level that most users
are concerned with. However, some users may wish to take advantage of the
capabilities of alternative GPIO implementations or (in future) use GPIO
extender chips. This is the purpose of the pins portion of the library.

When you construct a device, you pass in a pin specification. However, what the
library actually expects is a :class:`Pin` implementation. If it finds anything
else, it uses the existing ``Device._pin_factory`` to construct a :class:`Pin`
implementation based on the specification.

Changing the pin factory
========================

The default pin factory can be replaced by specifying a value for the
``GPIOZERO_PIN_FACTORY`` environment variable. For example:

.. code-block:: console

    pi@raspberrypi $ GPIOZERO_PIN_FACTORY=native python
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> gpiozero.Device._pin_factory
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>

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
| pigpio  | :class:`gpiozero.pins.pigpiod.PiGPIOFactory`  | :class:`gpiozero.pins.pigpiod.PiGPIOPin`  |
+---------+-----------------------------------------------+-------------------------------------------+
| native  | :class:`gpiozero.pins.native.NativeFactory`   | :class:`gpiozero.pins.native.NativePin`   |
+---------+-----------------------------------------------+-------------------------------------------+

If you need to change the default pin factory from within a script, use the
``Device._set_pin_factory`` class method, passing in the instance of the new
factory to use. This is only supported at script startup (replacing the factory
closes all existing pin instances which can have interesting consequences for
any devices using them)::

    from gpiozero.pins.native import NativeFactory
    from gpiozero import *
    Device._set_pin_factory(NativeFactory())

    from gpiozero import LED

    # This will now use NativePin instead of RPiGPIOPin
    led = LED(16)

Certain factories may take default information from additional sources.
For example, to default to creating pins with
:class:`gpiozero.pins.pigpiod.PiGPIOPin` on a remote pi called ``remote-pi``
you can set the :envvar:`PIGPIO_ADDR` environment variable when running your
script:

.. code-block:: console

    $ export GPIOZERO_PIN_FACTORY=pigpio
    $ PIGPIO_ADDR=remote-pi python3 my_script.py

.. warning::

    The astute and mischievous reader may note that it is possible to mix pin
    implementations, e.g. using ``RPiGPIOPin`` for one pin, and ``NativePin``
    for another. This is unsupported, and if it results in your script
    crashing, your components failing, or your Raspberry Pi turning into an
    actual raspberry pie, you have only yourself to blame.


RPi.GPIO
========

.. autoclass:: gpiozero.pins.rpigpio.RPiGPIOFactory

.. autoclass:: gpiozero.pins.rpigpio.RPiGPIOPin


RPIO
====

.. autoclass:: gpiozero.pins.rpio.RPIOFactory

.. autoclass:: gpiozero.pins.rpio.RPIOPin


PiGPIO
======

.. autoclass:: gpiozero.pins.pigpiod.PiGPIOFactory

.. autoclass:: gpiozero.pins.pigpiod.PiGPIOPin


Native
======

.. autoclass:: gpiozero.pins.native.NativeFactory

.. autoclass:: gpiozero.pins.native.NativePin


Base classes
============

.. autoclass:: Factory
    :members:

.. autoclass:: Pin
    :members:

.. autoclass:: SPI
    :members:


Utilities
=========

The pins module also contains a database of information about the various
revisions of Raspberry Pi. This is used internally to raise warnings when
non-physical pins are used, or to raise exceptions when pull-downs are
requested on pins with physical pull-up resistors attached. The following
functions and classes can be used to query this database:

.. autofunction:: pi_info

.. autoclass:: PiBoardInfo

.. autoclass:: HeaderInfo

.. autoclass:: PinInfo

