========
gpiozero
========

.. image:: https://badge.fury.io/gh/gpiozero%2Fgpiozero.svg
    :target: https://badge.fury.io/gh/gpiozero%2Fgpiozero
    :alt: Source code on GitHub

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

Created by `Ben Nuttall`_ and `Dave Jones`_.

.. _Ben Nuttall: https://github.com/bennuttall
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
to describe the behaviour of devices and their interactions:

.. code:: python

    from gpiozero import LED, MotionSensor, LightSensor
    from gpiozero.tools import booleanized, all_values
    from signal import pause

    garden = LED(17)
    motion = MotionSensor(4)
    light = LightSensor(5)

    garden.source = all_values(booleanized(light, 0, 0.1), motion)

    pause()

See the chapter on `Source/Values`_ for more information.

.. _Source/Values: https://gpiozero.readthedocs.io/en/stable/source_values.html

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
needs. See the section on `changing the pin factory`_.

.. _RPi.GPIO: https://pypi.org/project/RPi.GPIO
.. _pigpio: https://pypi.org/project/pigpio
.. _changing the pin factory: https://gpiozero.readthedocs.io/en/stable/api_pins.html#changing-the-pin-factory

A "mock pin" interface is also provided for testing purposes. Read more about
this in the section on `mock pins`_.

.. _mock pins: https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins

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

See the `contributors page`_ on GitHub for more info.

.. _contributors page: https://github.com/gpiozero/gpiozero/graphs/contributors

Core developers:

- `Ben Nuttall`_
- `Dave Jones`_
- `Andrew Scheller`_

Other contributors:

- `Alex Chan`_
- `Alex Eames`_
- `Barry Byford`_
- `Carl Monk`_
- `Claire Pollard`_
- `Clare Macrae`_
- `David Glaude`_
- `Daniele Procida`_
- `Delcio Torres`_
- `Edward Betts`_
- `Fatih Sarhan`_
- `Ian Harcombe`_
- `Jeevan M R`_
- `Mahallon`_
- `Maksim Levental`_
- `Martchus`_
- `Martin O'Hanlon`_
- `Mike Kazantsev`_
- `Phil Howard`_
- `Philippe Muller`_
- `Rick Ansell`_
- `Russel Winder`_
- `Ryan Walmsley`_
- `Schelto van Doorn`_
- `Sofiia Kosovan`_
- `Steve Amor`_
- `Stewart Adcock`_
- `Thijs Triemstra`_
- `Tim Golden`_
- `Yisrael Dov Lebow`_


.. _Alex Chan: https://github.com/gpiozero/gpiozero/commits?author=alexwlchan
.. _Alex Eames: https://github.com/gpiozero/gpiozero/commits?author=raspitv
.. _Andrew Scheller: https://github.com/gpiozero/gpiozero/commits?author=lurch
.. _Barry Byford: https://github.com/gpiozero/gpiozero/commits?author=ukBaz
.. _Carl Monk: https://github.com/gpiozero/gpiozero/commits?author=ForToffee
.. _Claire Pollard: https://github.com/gpiozero/gpiozero/commits?author=tuftii
.. _Clare Macrae: https://github.com/gpiozero/gpiozero/commits?author=claremacrae
.. _David Glaude: https://github.com/gpiozero/gpiozero/commits?author=dglaude
.. _Daniele Procida: https://github.com/evildmp
.. _Delcio Torres: https://github.com/gpiozero/gpiozero/commits?author=delciotorres
.. _Edward Betts: https://github.com/gpiozero/gpiozero/commits?author=edwardbetts
.. _Fatih Sarhan: https://github.com/gpiozero/gpiozero/commits?author=f9n
.. _Ian Harcombe: https://github.com/gpiozero/gpiozero/commits?author=MrHarcombe
.. _Jeevan M R: https://github.com/gpiozero/gpiozero/commits?author=jee1mr
.. _Mahallon: https://github.com/gpiozero/gpiozero/commits?author=Mahallon
.. _Maksim Levental: https://github.com/gpiozero/gpiozero/commits?author=makslevental
.. _Martchus: https://github.com/gpiozero/gpiozero/commits?author=Martchus
.. _Martin O'Hanlon: https://github.com/martinohanlon
.. _Mike Kazantsev: https://github.com/gpiozero/gpiozero/commits?author=mk-fg
.. _Phil Howard: https://github.com/gpiozero/gpiozero/commits?author=Gadgetoid
.. _Philippe Muller: https://github.com/gpiozero/gpiozero/commits?author=pmuller
.. _Rick Ansell: https://github.com/gpiozero/gpiozero/commits?author=ricksbt
.. _Russel Winder: https://github.com/russel
.. _Ryan Walmsley: https://github.com/gpiozero/gpiozero/commits?author=ryanteck
.. _Schelto van Doorn: https://github.com/gpiozero/gpiozero/commits?author=goloplo
.. _Sofiia Kosovan: https://github.com/gpiozero/gpiozero/commits?author=SofiiaKosovan
.. _Steve Amor: https://github.com/gpiozero/gpiozero/commits?author=SteveAmor
.. _Stewart Adcock: https://github.com/gpiozero/gpiozero/commits?author=stewartadcock
.. _Thijs Triemstra: https://github.com/gpiozero/gpiozero/commits?author=thijstriemstra
.. _Tim Golden: https://github.com/gpiozero/gpiozero/commits?author=tjguk
.. _Yisrael Dov Lebow: https://github.com/gpiozero/gpiozero/commits?author=yisraeldov
