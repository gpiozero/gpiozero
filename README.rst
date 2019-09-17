========
gpiozero
========

.. image:: https://badge.fury.io/py/gpiozero.svg
    :target: https://badge.fury.io/py/gpiozero
    :alt: Latest Version

.. image:: https://travis-ci.org/gpiozero/gpiozero.svg?branch=master
    :target: https://travis-ci.org/gpiozero/gpiozero
    :alt: Build Tests

.. image:: https://img.shields.io/codecov/c/github/gpiozero/gpiozero/master.svg?maxAge=2592000
    :target: https://codecov.io/github/gpiozero/gpiozero
    :alt: Code Coverage

A simple interface to GPIO devices with Raspberry Pi.

Created by `Ben Nuttall`_ of the `Raspberry Pi Foundation`_, `Dave Jones`_, and
other contributors.

.. _Ben Nuttall: https://github.com/bennuttall
.. _Raspberry Pi Foundation: https://www.raspberrypi.org/
.. _Dave Jones: https://github.com/waveform80

About
=====

Component interfaces are provided to allow a frictionless way to get started
with physical computing:

.. code:: python

    from gpiozero import LED
    from time import sleep

    led = LED(17)

    while True:
        led.on()
        sleep(1)
        led.off()
        sleep(1)

With very little code, you can quickly get going connecting your components
together:

.. code:: python

    from gpiozero import LED, Button
    from signal import pause

    led = LED(17)
    button = Button(3)

    button.when_pressed = led.on
    button.when_released = led.off

    pause()

You can advance to using the declarative paradigm along with provided
:doc:`source tools <api_tools>` to describe the behaviour of devices and their
interactions:

.. code:: python

    from gpiozero import LED, MotionSensor, LightSensor
    from gpiozero.tools import booleanized, all_values
    from signal import pause

    garden = LED(17)
    motion = MotionSensor(4)
    light = LightSensor(5)

    garden.source = all_values(booleanized(light, 0, 0.1), motion)

    pause()

See the chapter on :doc:`Source/Values <source_values>` for more information.

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more. See the `Recipes`_ chapter of the
documentation for ideas on how to get started.

.. _Recipes: https://gpiozero.readthedocs.io/en/stable/recipes.html

Pin factories
=============

GPIO Zero builds on a number of underlying pin libraries, including `RPi.GPIO`_
and `pigpio`_, each with their own benefits. You can select a particular pin
library to be used, either for the whole script or per-device, according to your
needs. See the section on :ref:`changing the pin factory
<changing-pin-factory>`.

.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO/
.. _pigpio: https://pypi.org/project/pigpio

A "mock pin" interface is also provided for testing purposes. Read more about
this in the section on :ref:`mock pins <mock-pins>`.

Installation
============

GPIO Zero is installed by default in the Raspbian desktop image, available from
`raspberrypi.org`_. To install on Raspbian Lite or other operating systems,
including for PCs using remote GPIO, see the `Installing`_ chapter.

.. _raspberrypi.org: https://www.raspberrypi.org/downloads/
.. _Installing: https://gpiozero.readthedocs.io/en/stable/installing.html

Documentation
=============

Comprehensive documentation is available at https://gpiozero.readthedocs.io/.
Please refer to the `Contributing`_ and `Development`_ chapters in the
documentation for information on contributing to the project.

.. _Contributing: https://gpiozero.readthedocs.io/en/stable/contributing.html
.. _Development: https://gpiozero.readthedocs.io/en/stable/development.html

Contributors
============

Core developers:

- `Ben Nuttall`_
- `Dave Jones`_
- `Andrew Scheller`_

Other contributors:

- `Martin O'Hanlon`_
- `Steve Amor`_
- `David Glaude`_
- `Edward Betts`_
- `Alex Chan`_
- `Thijs Triemstra`_
- `Schelto van Doorn`_
- `Alex Eames`_
- `Barry Byford`_
- `Clare Macrae`_
- `Tim Golden`_
- `Phil Howard`_
- `Stewart Adcock`_
- `Ian Harcombe`_
- `Russel Winder`_
- `Mike Kazantsev`_
- `Fatih Sarhan`_
- `Rick Ansell`_
- `Jeevan M R`_
- `Claire Pollard`_
- `Philippe Muller`_
- `Sofiia Kosovan`_


.. _Andrew Scheller: https://github.com/lurch
.. _Martin O'Hanlon: https://github.com/martinohanlon
.. _Steve Amor: https://github.com/SteveAmor
.. _David Glaude: https://github.com/dglaude
.. _Edward Betts: https://github.com/edwardbetts
.. _Alex Chan: https://github.com/alexwlchan
.. _Thijs Triemstra: https://github.com/thijstriemstra
.. _Schelto van Doorn: https://github.com/goloplo
.. _Alex Eames: https://github.com/raspitv
.. _Barry Byford: https://github.com/ukBaz
.. _Clare Macrae: https://github.com/claremacrae
.. _Tim Golden: https://github.com/tjguk
.. _Phil Howard: https://github.com/Gadgetoid
.. _Stewart Adcock: https://github.com/stewartadcock
.. _Ian Harcombe: https://github.com/MrHarcombe
.. _Russel Winder: https://github.com/russel
.. _Mike Kazantsev: https://github.com/mk-fg
.. _Fatih Sarhan: https://github.com/f9n
.. _Rick Ansell: https://github.com/ricksbt
.. _Jeevan M R: https://github.com/jee1mr
.. _Claire Pollard: https://github.com/tuftii
.. _Philippe Muller: https://github.com/pmuller
.. _Sofiia Kosovan: https://github.com/SofiiaKosovan
