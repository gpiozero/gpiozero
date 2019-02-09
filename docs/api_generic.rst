.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
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

.. autoclass:: Device(\*, pin_factory=None)
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
