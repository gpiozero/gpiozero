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

    All GPIO pin numbers use Broadcom (BCM) numbering. See the :doc:`recipes`
    page for more information.

LEDBoard
========

.. autoclass:: LEDBoard(\*pins, pwm=False, active_high=True, initial_value=False, pin_factory=None, \*\*named_pins)
    :inherited-members:
    :members:

LEDBarGraph
===========

.. autoclass:: LEDBarGraph(\*pins, pwm=False, active_high=True, initial_value=0, pin_factory=None)
    :inherited-members:
    :members:

ButtonBoard
===========

.. autoclass:: ButtonBoard(\*pins, pull_up=True, bounce_time=None, hold_time=1, hold_repeat=False, pin_factory=None, \*\*named_pins)
    :inherited-members:
    :members:

TrafficLights
=============

.. autoclass:: TrafficLights
    :inherited-members:
    :members:

LedBorg
=======

.. autoclass:: LedBorg
    :inherited-members:
    :members:

PiLITEr
=======

.. autoclass:: PiLiter
    :inherited-members:
    :members:

PiLITEr Bar Graph
=================

.. autoclass:: PiLiterBarGraph
    :inherited-members:
    :members:

PI-TRAFFIC
==========

.. autoclass:: PiTraffic
    :inherited-members:
    :members:

Pi-Stop
=======

.. autoclass:: PiStop
    :inherited-members:
    :members:

TrafficLightsBuzzer
===================

.. autoclass:: TrafficLightsBuzzer
    :inherited-members:
    :members:

Fish Dish
=========

.. autoclass:: FishDish
    :inherited-members:
    :members:

Traffic HAT
===========

.. autoclass:: TrafficHat
    :inherited-members:
    :members:

Robot
=====

.. autoclass:: Robot
    :inherited-members:
    :members:

PhaseEnableRobot
================

.. autoclass:: PhaseEnableRobot
    :inherited-members:
    :members:

Ryanteck MCB Robot
==================

.. autoclass:: RyanteckRobot
    :inherited-members:
    :members:

CamJam #3 Kit Robot
===================

.. autoclass:: CamJamKitRobot
    :inherited-members:
    :members:

Pololu DRV8835 Robot
====================

.. autoclass:: PololuDRV8835Robot
    :inherited-members:
    :members:

Energenie
=========

.. autoclass:: Energenie
    :inherited-members:
    :members:

StatusZero
==========

.. autoclass:: StatusZero(\*labels, pwm=False, active_high=True, initial_value=False, pin_factory=None)
    :inherited-members:
    :members:

StatusBoard
===========

.. autoclass:: StatusBoard(\*labels, pwm=False, active_high=True, initial_value=False, pin_factory=None)
    :inherited-members:
    :members:

SnowPi
======

.. autoclass:: SnowPi
    :inherited-members:
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
=============

.. autoclass:: LEDCollection(\*pins, pwm=False, active_high=True, initial_value=False, pin_factory=None, \*\*named_pins)
    :members:

CompositeOutputDevice
=====================

.. autoclass:: CompositeOutputDevice(\*args, _order=None, pin_factory=None, \*\*kwargs)
    :members:

CompositeDevice
===============

.. autoclass:: CompositeDevice(\*args, _order=None, pin_factory=None, \*\*kwargs)
    :members:
