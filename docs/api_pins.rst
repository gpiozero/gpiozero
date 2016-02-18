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

When you construct a device, you pass in a GPIO pin number. However, what the
library actually expects is a :class:`Pin` implementation. If it finds a simple
integer number instead, it uses one of the following classes to provide the
:class:`Pin` implementation (classes are listed in favoured order):

1. :class:`gpiozero.pins.rpigpio.RPiGPIOPin`

2. :class:`gpiozero.pins.rpio.RPIOPin`

3. :class:`gpiozero.pins.pigpiod.PiGPIOPin`

4. :class:`gpiozero.pins.native.NativePin`

You can change the default pin implementation by over-writing the
``DefaultPin`` global in the ``devices`` module like so::

    from gpiozero.pins.native import NativePin
    import gpiozero.devices
    # Force the default pin implementation to be NativePin
    gpiozero.devices.DefaultPin = NativePin

    from gpiozero import LED

    # This will now use NativePin instead of RPiGPIOPin
    led = LED(16)

Alternatively, instead of passing an integer to the device constructor, you
can pass a :class:`Pin` object itself::

    from gpiozero.pins.native import NativePin
    from gpiozero import LED

    led = LED(NativePin(16))

This is particularly useful with implementations that can take extra parameters
such as :class:`PiGPIOPin` which can address pins on remote machines::

    from gpiozero.pins.pigpiod import PiGPIOPin
    from gpiozero import LED

    led = LED(PiGPIOPin(16, host='my_other_pi'))

In future, this separation of pins and devices should also permit the library
to utilize pins that are part of IO extender chips. For example::

    from gpiozero import IOExtender, LED

    ext = IOExtender()
    led = LED(ext.pins[0])
    led.on()

.. warning::

    While the devices API is now considered stable and won't change in
    backwards incompatible ways, the pins API is *not* yet considered stable.
    It is potentially subject to change in future versions. We welcome any
    comments from testers!


RPiGPIOPin
==========

.. currentmodule:: gpiozero.pins.rpigpio

.. autoclass:: RPiGPIOPin


RPIOPin
=======

.. currentmodule:: gpiozero.pins.rpio

.. autoclass:: RPIOPin


PiGPIOPin
=========

.. currentmodule:: gpiozero.pins.pigpiod

.. autoclass:: PiGPIOPin


NativePin
=========

.. currentmodule:: gpiozero.pins.native

.. autoclass:: NativePin


Abstract Pin
============

.. currentmodule:: gpiozero.pins

.. autoclass:: Pin
    :members:

