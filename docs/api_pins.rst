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
default factory can be queried (and changed) with ``Device.pin_factory``, i.e.
the ``pin_factory`` attribute of the :class:`Device` class. However, all
classes accept a ``pin_factory`` keyword argument to their constructors
permitting the factory to be overridden on a per-device basis (the reason for
allowing per-device factories is made apparent later in the :doc:`remote_gpio`
chapter).

This is illustrated in the following flow-chart:

.. image:: images/device_pin_flowchart.*

The default factory is constructed when GPIO Zero is first imported; if no
default factory can be constructed (e.g. because no GPIO implementations are
installed, or all of them fail to load for whatever reason), an
:exc:`ImportError` will be raised.

.. _changing-pin-factory:

Changing the pin factory
========================

The default pin factory can be replaced by specifying a value for the
``GPIOZERO_PIN_FACTORY`` environment variable. For example:

.. code-block:: console

    $ GPIOZERO_PIN_FACTORY=native python
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> gpiozero.Device.pin_factory
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>

To set the ``GPIOZERO_PIN_FACTORY`` for the rest of your session you can
export this value:

.. code-block:: console

    $ export GPIOZERO_PIN_FACTORY=native
    $ python
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> gpiozero.Device.pin_factory
    <gpiozero.pins.native.NativeFactory object at 0x762c26b0>
    >>> quit()
    $ python
    Python 3.4.2 (default, Oct 19 2014, 13:31:11)
    [GCC 4.9.1] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import gpiozero
    >>> gpiozero.Device.pin_factory
    <gpiozero.pins.native.NativeFactory object at 0x76401330>

If you add the ``export`` command to your :file:`~/.bashrc` file, you'll set
the default pin factory for all future sessions too.

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
``Device.pin_factory`` to the new factory instance to use::

    from gpiozero.pins.native import NativeFactory
    from gpiozero import Device, LED

    Device.pin_factory = NativeFactory()

    # These will now implicitly use NativePin instead of
    # RPiGPIOPin
    led1 = LED(16)
    led2 = LED(17)

Or use the ``pin_factory`` keyword parameter mentioned above::

    from gpiozero.pins.native import NativeFactory
    from gpiozero import LED

    my_factory = NativeFactory()

    # This will use NativePin instead of RPiGPIOPin for led1
    # but led2 will continue to use RPiGPIOPin
    led1 = LED(16, pin_factory=my_factory)
    led2 = LED(17)

Certain factories may take default information from additional sources.
For example, to default to creating pins with
:class:`gpiozero.pins.pigpio.PiGPIOPin` on a remote pi called ``remote-pi``
you can set the :envvar:`PIGPIO_ADDR` environment variable when running your
script:

.. code-block:: console

    $ GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=remote-pi python3 my_script.py

Like the ``GPIOZERO_PIN_FACTORY`` value, these can be exported from your
:file:`~/.bashrc` script too.

.. warning::

    The astute and mischievous reader may note that it is possible to mix
    factories, e.g. using ``RPiGPIOFactory`` for one pin, and ``NativeFactory``
    for another. This is unsupported, and if it results in your script
    crashing, your components failing, or your Raspberry Pi turning into an
    actual raspberry pie, you have only yourself to blame.

    Sensible uses of multiple pin factories are given in :doc:`remote_gpio`.


Mock pins
=========

There's also a :class:`gpiozero.pins.mock.MockFactory` which generates entirely
fake pins. This was originally intended for GPIO Zero developers who wish to
write tests for devices without having to have the physical device wired in to
their Pi. However, they have also proven relatively useful in developing GPIO
Zero scripts without having a Pi to hand. This pin factory will never be loaded
by default; it must be explicitly specified. For example:

.. literalinclude:: examples/mock_demo.py

Several sub-classes of mock pins exist for emulating various other things
(pins that do/don't support PWM, pins that are connected together, pins that
drive high after a delay, etc). Interested users are invited to read the GPIO
Zero test suite for further examples of usage.


Base classes
============

.. autoclass:: Factory
    :members:

.. autoclass:: Pin
    :members:

.. autoclass:: SPI
    :members:

.. module:: gpiozero.pins.pi

.. autoclass:: PiFactory
    :members:

.. autoclass:: PiPin
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
    :members:

.. autoclass:: gpiozero.pins.mock.MockPWMPin

.. autoclass:: gpiozero.pins.mock.MockConnectedPin

.. autoclass:: gpiozero.pins.mock.MockChargingPin

.. autoclass:: gpiozero.pins.mock.MockTriggerPin

