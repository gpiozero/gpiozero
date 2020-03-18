.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2016-2020 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
.. Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
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

============================
API - Boards and Accessories
============================

.. module:: gpiozero.boards

.. currentmodule:: gpiozero

These additional interfaces are provided to group collections of components
together for ease of use, and as examples. They are composites made up of
components from the various :doc:`api_input` and :doc:`api_output` provided by
GPIO Zero. See those pages for more information on using components
individually.

.. note::

    All GPIO pin numbers use Broadcom (BCM) numbering by default. See the
    :ref:`pin-numbering` section for more information.


Regular Classes
===============

The following classes are intended for general use with the devices they are
named after. All classes in this section are concrete (not abstract).


LEDBoard
--------

.. autoclass:: LEDBoard(\*pins, pwm=False, active_high=True, initial_value=False, pin_factory=None, \*\*named_pins)
    :members: on, off, blink, pulse, toggle


LEDBarGraph
-----------

.. autoclass:: LEDBarGraph(\*pins, pwm=False, active_high=True, initial_value=0, pin_factory=None)
    :members: value, source, values, lit_count


ButtonBoard
-----------

.. autoclass:: ButtonBoard(\*pins, pull_up=True, active_state=None, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None, \*\*named_pins)
    :members: wait_for_press, wait_for_release, is_pressed, pressed_time, when_pressed, when_released, value


TrafficLights
-------------

.. autoclass:: TrafficLights(red, amber, green, \*, yellow=None, pwm=False, initial_value=False, pin_factory=None)
    :members:


TrafficLightsBuzzer
-------------------

.. autoclass:: TrafficLightsBuzzer(lights, buzzer, button, \*, pin_factory=None)
    :members:


PiHutXmasTree
-------------

.. autoclass:: PiHutXmasTree(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


LedBorg
-------

.. autoclass:: LedBorg(\*, pwm=True, initial_value=(0, 0, 0), pin_factory=None)
    :members:


PiLiter
-------

.. autoclass:: PiLiter(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


PiLiterBarGraph
---------------

.. autoclass:: PiLiterBarGraph(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


PiTraffic
---------

.. autoclass:: PiTraffic(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


PiStop
------

.. autoclass:: PiStop(location, \*, pwm=False, initial_value=False, pin_factory=None)
    :members:


FishDish
--------

.. autoclass:: FishDish(\*, pwm=False, pin_factory=None)
    :members:


TrafficHat
----------

.. autoclass:: TrafficHat(\*, pwm=False, pin_factory=None)
    :members:


TrafficpHat
-----------

.. autoclass:: TrafficpHat(\*, pwm=False, pin_factory=None)
    :members:


JamHat
------

.. autoclass:: JamHat(\*, pwm=False, pin_factory=None)
    :members:


Pibrella
--------

.. autoclass:: Pibrella(\*, pwm=False, pin_factory=None)
    :members:


Robot
-----

.. autoclass:: Robot(left, right, \*, pwm=True, pin_factory=None)
    :members:


PhaseEnableRobot
----------------

.. autoclass:: PhaseEnableRobot(left, right, \*, pwm=True, pin_factory=None)
    :members:


RyanteckRobot
-------------

.. autoclass:: RyanteckRobot(\*, pwm=True, pin_factory=None)
    :members:


CamJamKitRobot
--------------

.. autoclass:: CamJamKitRobot(\*, pwm=True, pin_factory=None)
    :members:


PololuDRV8835Robot
------------------

.. autoclass:: PololuDRV8835Robot(\*, pwm=True, pin_factory=None)
    :members:


Energenie
---------

.. autoclass:: Energenie(socket, \*, initial_value=False, pin_factory=None)
    :members: on, off, socket, value


StatusZero
----------

.. autoclass:: StatusZero(\*labels, pwm=False, active_high=True, initial_value=False, pin_factory=None)
    :members:


StatusBoard
-----------

.. autoclass:: StatusBoard(\*labels, pwm=False, active_high=True, initial_value=False, pin_factory=None)
    :members:


SnowPi
------

.. autoclass:: SnowPi(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


PumpkinPi
---------

.. autoclass:: PumpkinPi(\*, pwm=False, initial_value=False, pin_factory=None)
    :members:


Base Classes
============

The classes in the sections above are derived from a series of base classes,
some of which are effectively abstract. The classes form the (partial)
hierarchy displayed in the graph below:

.. image:: images/composite_device_hierarchy.*

For composite devices, the following chart shows which devices are composed of
which other devices:

.. image:: images/composed_devices.*

The following sections document these base classes for advanced users that wish
to construct classes for their own devices.


LEDCollection
-------------

.. autoclass:: LEDCollection(\*pins, pwm=False, active_high=True, initial_value=False, pin_factory=None, \*\*named_pins)
    :members:


CompositeOutputDevice
---------------------

.. autoclass:: CompositeOutputDevice(\*args, _order=None, pin_factory=None, \*\*kwargs)
    :members:


CompositeDevice
---------------

.. autoclass:: CompositeDevice(\*args, _order=None, pin_factory=None, \*\*kwargs)
    :members:
