.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016-2020 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
.. Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
..
.. SPDX-License-Identifier: BSD-3-Clause

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

.. autoclass:: LEDBoard
    :members: on, off, blink, pulse, toggle


LEDBarGraph
-----------

.. autoclass:: LEDBarGraph
    :members: value, source, values, lit_count


LEDCharDisplay
--------------

.. autoclass:: LEDCharDisplay
    :members: value, font


LEDMultiCharDisplay
-------------------

.. autoclass:: LEDMultiCharDisplay
    :members: value, plex_delay


LEDCharFont
-----------

.. autoclass:: LEDCharFont


ButtonBoard
-----------

.. autoclass:: ButtonBoard
    :members: wait_for_press, wait_for_release, is_pressed, pressed_time, when_pressed, when_released, value


TrafficLights
-------------

.. autoclass:: TrafficLights
    :members:


TrafficLightsBuzzer
-------------------

.. autoclass:: TrafficLightsBuzzer
    :members:


PiHutXmasTree
-------------

.. autoclass:: PiHutXmasTree
    :members:


LedBorg
-------

.. autoclass:: LedBorg
    :members:


PiLiter
-------

.. autoclass:: PiLiter
    :members:


PiLiterBarGraph
---------------

.. autoclass:: PiLiterBarGraph
    :members:


PiTraffic
---------

.. autoclass:: PiTraffic
    :members:


PiStop
------

.. autoclass:: PiStop
    :members:


FishDish
--------

.. autoclass:: FishDish
    :members:


TrafficHat
----------

.. autoclass:: TrafficHat
    :members:


TrafficpHat
-----------

.. autoclass:: TrafficpHat
    :members:


JamHat
------

.. autoclass:: JamHat
    :members:


Pibrella
--------

.. autoclass:: Pibrella
    :members:


Robot
-----

.. autoclass:: Robot
    :members:


PhaseEnableRobot
----------------

.. autoclass:: PhaseEnableRobot
    :members:


RyanteckRobot
-------------

.. autoclass:: RyanteckRobot
    :members:


CamJamKitRobot
--------------

.. autoclass:: CamJamKitRobot
    :members:


PololuDRV8835Robot
------------------

.. autoclass:: PololuDRV8835Robot
    :members:


Energenie
---------

.. autoclass:: Energenie
    :members: on, off, socket, value


StatusZero
----------

.. autoclass:: StatusZero
    :members:


StatusBoard
-----------

.. autoclass:: StatusBoard
    :members:


SnowPi
------

.. autoclass:: SnowPi
    :members:


PumpkinPi
---------

.. autoclass:: PumpkinPi
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

.. autoclass:: LEDCollection
    :members:


CompositeOutputDevice
---------------------

.. autoclass:: CompositeOutputDevice
    :members:


CompositeDevice
---------------

.. autoclass:: CompositeDevice
    :members:
