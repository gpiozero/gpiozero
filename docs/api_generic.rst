===============
Generic Devices
===============

.. currentmodule:: gpiozero

The GPIO Zero class hierarchy is quite extensive. It contains several base
classes:

* :class:`Device` is the root of the hierarchy, implementing base functionality
  like :meth:`~Device.close` and context manager handlers.

* :class:`GPIODevice` represents individual devices that attach to a single
  GPIO pin

* :class:`SPIDevice` represents devices that communicate over an SPI interface
  (implemented as four GPIO pins)

* :class:`InternalDevice` represents devices that are entirely internal to
  the Pi (usually operating system related services)

* :class:`CompositeDevice` represents devices composed of multiple other
  devices like HATs

There are also several `mixin classes`_:

* :class:`ValuesMixin` which defines the ``values`` properties; there is rarely
  a need to use this as the base classes mentioned above both include it
  (so all classes in GPIO Zero include the ``values`` property)

* :class:`SourceMixin` which defines the ``source`` property; this is generally
  included in novel output device classes

* :class:`SharedMixin` which causes classes to track their construction and
  return existing instances when equivalent constructor arguments are passed

* :class:`EventsMixin` which adds activated/deactivated events to devices
  along with the machinery to trigger those events

* :class:`HoldMixin` which derives from :class:`EventsMixin` and adds the
  held event to devices along with the machinery to repeatedly trigger it

.. _mixin classes: https://en.wikipedia.org/wiki/Mixin

The current class hierarchies are displayed below. For brevity, the mixin
classes (and some other details) are omitted, and the chart is broken into
pieces by base class. The lighter boxes represent classes that are "effectively
abstract". These classes aren't directly useful without sub-classing them and
adding bits.

First, the classes below :class:`GPIODevice`:

.. image:: images/gpio_device_hierarchy.*

Next, the classes below :class:`SPIDevice`:

.. image:: images/spi_device_hierarchy.*

Next, the classes below :class:`InternalDevice`:

.. image:: images/other_device_hierarchy.*

Next, the classes below :class:`CompositeDevice`:

.. image:: images/composite_device_hierarchy.*

Finally, for composite devices, the following chart shows which devices are
composed of which other devices:

.. image:: images/composed_devices.*

Base Classes
============

.. autoclass:: Device
    :members: close, closed, value, is_active

.. autoclass:: GPIODevice(pin)
    :members:

.. autoclass:: SPIDevice
    :members:

.. autoclass:: InternalDevice
    :members:

.. autoclass:: CompositeDevice
    :members:

Input Devices
=============

.. autoclass:: InputDevice(pin, pull_up=False)
    :members:

.. autoclass:: DigitalInputDevice(pin, pull_up=False, bounce_time=None)
    :members:

.. autoclass:: SmoothedInputDevice
    :members:

Output Devices
==============

.. autoclass:: OutputDevice(pin, active_high=True, initial_value=False)
    :members:

.. autoclass:: DigitalOutputDevice(pin, active_high=True, initial_value=False)
    :members:

.. autoclass:: PWMOutputDevice(pin, active_high=True, initial_value=0, frequency=100)
    :members:

SPI Devices
===========

.. autoclass:: SPIDevice
    :members:

.. autoclass:: AnalogInputDevice
    :members:

Composite Devices
=================

.. autoclass:: CompositeOutputDevice
    :members:

.. autoclass:: LEDCollection
    :members:

Mixin Classes
=============

.. autoclass:: ValuesMixin(...)
    :members:

.. autoclass:: SourceMixin(...)
    :members:

.. autoclass:: SharedMixin(...)
    :members: _shared_key

.. autoclass:: EventsMixin(...)
    :members:

.. autoclass:: HoldMixin(...)
    :members:

