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

3. :class:`gpiozero.pins.native.NativePin`

You can change the default pin implementation by over-writing the
``DefaultPin`` global in devices like so::

    from gpiozero.pins.native import NativePin
    import gpiozero.devices
    # Force the default pin implementation to be NativePin
    gpiozero.devices.DefaultPin = NativePin

    from gpiozero import LED

    # This will now use NativePin instead of RPiGPIOPin
    led = LED(16)

In future, this separation should allow the library to utilize pins that are
part of IO extender chips. For example::

    from gpiozero import IOExtender, LED

    ext = IOExtender()
    led = LED(ext.pins[0])
    led.on()

.. warning::

    While the devices API is now considered stable and won't change in
    backwards incompatible ways, the pins API is *not* yet considered stable.
    It is potentially subject to change in future versions. We welcome any
    comments from testers!


Abstract Pin
============

.. autoclass:: Pin
    :members:


RPiGPIOPin
==========

.. currentmodule:: gpiozero.pins.rpigpio

.. autoclass:: RPiGPIOPin


RPIOPin
=======

.. currentmodule:: gpiozero.pins.rpio

.. autoclass:: RPIOPin


NativePin
=========

.. currentmodule:: gpiozero.pins.native

.. autoclass:: NativePin

