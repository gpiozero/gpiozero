===============
Generic Devices
===============

.. currentmodule:: gpiozero

The GPIO Zero class hierarchy is quite extensive. It contains a couple of base
classes:

* :class:`GPIODevice` for individual devices that attach to a single GPIO pin

* :class:`CompositeDevice` for devices composed of multiple other devices like
  HATs

There are also a couple of `mixin classes`_:

* :class:`ValuesMixin` which defines the ``values`` properties; there is rarely
  a need to use this as the base classes mentioned above both include it
  (so all classes in GPIO Zero include the ``values`` property)

* :class:`SourceMixin` which defines the ``source`` property; this is generally
  included in novel output device classes

.. _mixin classes: https://en.wikipedia.org/wiki/Mixin

The current class hierarchies are displayed below. For brevity, the mixin
classes are omitted:

.. image:: images/gpio_device_hierarchy.*

.. image:: images/composite_device_hierarchy.*

Finally, for composite devices, the following chart shows which devices are
composed of which other devices:

.. image:: images/composed_devices.*

Base Classes
============

.. autoclass:: GPIODevice(pin)
    :inherited-members:
    :members:

.. autoclass:: CompositeDevice
    :inherited-members:
    :members:

Input Devices
=============

.. autoclass:: InputDevice(pin, pull_up=False)
    :members:

.. autoclass:: WaitableInputDevice
    :members:

.. autoclass:: DigitalInputDevice(pin, pull_up=False, bounce_time=None)
    :members:

.. autoclass:: SmoothedInputDevice
    :members:

.. autoclass:: AnalogInputDevice
    :members:

Output Devices
==============

.. autoclass:: OutputDevice(pin, active_high=True)
    :members:

.. autoclass:: PWMOutputDevice(pin, frequency=100)
    :members:

.. autoclass:: DigitalOutputDevice(pin, active_high=True)
    :members:

Mixin Classes
=============

.. autoclass:: ValuesMixin(...)
    :members:

.. autoclass:: SourceMixin(...)
    :members:

