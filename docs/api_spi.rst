.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017 rgm <roland@securelink.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
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

=================
API - SPI Devices
=================

.. module:: gpiozero.spi_devices

.. currentmodule:: gpiozero

SPI stands for `Serial Peripheral Interface`_ and is a mechanism allowing
compatible devices to communicate with the Pi. SPI is a four-wire protocol
meaning it usually requires four pins to operate:

* A "clock" pin which provides timing information.

* A "MOSI" pin (Master Out, Slave In) which the Pi uses to send information
  to the device.

* A "MISO" pin (Master In, Slave Out) which the Pi uses to receive information
  from the device.

* A "select" pin which the Pi uses to indicate which device it's talking to.
  This last pin is necessary because multiple devices can share the clock,
  MOSI, and MISO pins, but only one device can be connected to each select
  pin.

The gpiozero library provides two SPI implementations:

* A software based implementation. This is always available, can use any four
  GPIO pins for SPI communication, but is rather slow and won't work with all
  devices.

* A hardware based implementation. This is only available when the SPI kernel
  module is loaded, and the Python spidev library is available. It can only use
  specific pins for SPI communication (GPIO11=clock, GPIO10=MOSI, GPIO9=MISO,
  while GPIO8 is select for device 0 and GPIO7 is select for device 1).
  However, it is extremely fast and works with all devices.

.. _Serial Peripheral Interface: https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus


.. _spi_args:

SPI keyword args
================

When constructing an SPI device there are two schemes for specifying which pins
it is connected to:

* You can specify *port* and *device* keyword arguments. The *port* parameter
  must be 0 (there is only one user-accessible hardware SPI interface on the Pi
  using GPIO11 as the clock pin, GPIO10 as the MOSI pin, and GPIO9 as the MISO
  pin), while the *device* parameter must be 0 or 1. If *device* is 0, the
  select pin will be GPIO8. If *device* is 1, the select pin will be GPIO7.

* Alternatively you can specify *clock_pin*, *mosi_pin*, *miso_pin*, and
  *select_pin* keyword arguments. In this case the pins can be any 4 GPIO pins
  (remember that SPI devices can share clock, MOSI, and MISO pins, but not
  select pins - the gpiozero library will enforce this restriction).

You cannot mix these two schemes, i.e. attempting to specify *port* and
*clock_pin* will result in :exc:`SPIBadArgs` being raised. However, you can
omit any arguments from either scheme. The defaults are:

* *port* and *device* both default to 0.

* *clock_pin* defaults to 11, *mosi_pin* defaults to 10, *miso_pin* defaults
  to 9, and *select_pin* defaults to 8.

* As with other GPIO based devices you can optionally specify a *pin_factory*
  argument overriding the default pin factory (see :doc:`api_pins` for more
  information).

Hence the following constructors are all equivalent::

    from gpiozero import MCP3008

    MCP3008(channel=0)
    MCP3008(channel=0, device=0)
    MCP3008(channel=0, port=0, device=0)
    MCP3008(channel=0, select_pin=8)
    MCP3008(channel=0, clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)

Note that the defaults describe equivalent sets of pins and that these pins are
compatible with the hardware implementation. Regardless of which scheme you
use, gpiozero will attempt to use the hardware implementation if it is
available and if the selected pins are compatible, falling back to the software
implementation if not.


Analog to Digital Converters (ADC)
==================================

The following classes are intended for general use with the integrated circuits
they are named after. All classes in this section are concrete (not abstract).


MCP3001
-------

.. autoclass:: MCP3001
    :members: value


MCP3002
-------

.. autoclass:: MCP3002
    :members: channel, value, differential


MCP3004
-------

.. autoclass:: MCP3004
    :members: channel, value, differential


MCP3008
-------

.. autoclass:: MCP3008
    :members: channel, value, differential


MCP3201
-------

.. autoclass:: MCP3201
    :members: value


MCP3202
-------

.. autoclass:: MCP3202
    :members: channel, value, differential


MCP3204
-------

.. autoclass:: MCP3204
    :members: channel, value, differential


MCP3208
-------

.. autoclass:: MCP3208
    :members: channel, value, differential


MCP3301
-------

.. autoclass:: MCP3301
    :members: value


MCP3302
-------

.. autoclass:: MCP3302
    :members: channel, value, differential


MCP3304
-------

.. autoclass:: MCP3304
    :members: channel, value, differential


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below (abstract classes are shaded lighter
than concrete classes):

.. image:: images/spi_device_hierarchy.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


AnalogInputDevice
-----------------

.. autoclass:: AnalogInputDevice
    :members:


SPIDevice
---------

.. autoclass:: SPIDevice
    :members:
