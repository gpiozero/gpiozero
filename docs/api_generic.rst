.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

=====================
API - Generic Classes
=====================

.. module:: gpiozero.devices

.. currentmodule:: gpiozero

The GPIO Zero class hierarchy is quite extensive. It contains several base
classes (most of which are documented in their corresponding chapters):

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

There are also several `mixin classes`_ for adding important functionality
at numerous points in the hierarchy, which is illustrated below (mixin classes
are represented in purple, while abstract classes are shaded lighter):

.. image:: images/device_hierarchy.*

.. _mixin classes: https://en.wikipedia.org/wiki/Mixin


Device
======

.. autoclass:: Device
    :members: close, closed, value, is_active, pin_factory


ValuesMixin
===========

.. autoclass:: ValuesMixin(...)
    :members:


SourceMixin
===========

.. autoclass:: SourceMixin(...)
    :members:


SharedMixin
===========

.. autoclass:: SharedMixin(...)
    :members: _shared_key


EventsMixin
===========

.. autoclass:: EventsMixin(...)
    :members:


HoldMixin
=========

.. autoclass:: HoldMixin(...)
    :members:
