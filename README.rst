========
gpiozero
========

.. image:: https://badge.fury.io/py/gpiozero.svg
    :target: https://badge.fury.io/py/gpiozero
    :alt: Latest Version

.. image:: https://travis-ci.org/RPi-Distro/python-gpiozero.svg?branch=master
    :target: https://travis-ci.org/RPi-Distro/python-gpiozero
    :alt: Build Tests

.. image:: https://img.shields.io/codecov/c/github/RPi-Distro/python-gpiozero/master.svg?maxAge=2592000
    :target: https://codecov.io/github/RPi-Distro/python-gpiozero
    :alt: Code Coverage

A simple interface to GPIO devices with Raspberry Pi.

Created by `Ben Nuttall`_ of the `Raspberry Pi Foundation`_, `Dave Jones`_, and
other contributors.

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

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more. See the `Recipes`_ chapter of the
documentation for ideas on how to get started.

Installation
============

GPIO Zero is installed by default in the Raspbian desktop image, available from
`raspberrypi.org`_. To install on Raspbian Lite or other operating systems,
including for PCs using remote GPIO, see the `Installing`_ chapter.

Documentation
=============

Comprehensive documentation is available at https://gpiozero.readthedocs.io/.
Please refer to the `Contributing`_ and `Development`_ chapters in the
documentation for information on contributing to the project.

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
- `Schelto vanDoorn`_
- `Alex Eames`_
- `Barry Byford`_
- `Clare Macrae`_
- `Tim Golden`_
- `Phil Howard`_
- `Stewart Adcock`_
- `Ian Harcombe`_


.. _Raspberry Pi Foundation: https://www.raspberrypi.org/
.. _raspberrypi.org: https://www.raspberrypi.org/downloads/
.. _Recipes: https://gpiozero.readthedocs.io/en/stable/recipes.html
.. _Contributing: https://gpiozero.readthedocs.io/en/stable/contributing.html
.. _Development: https://gpiozero.readthedocs.io/en/stable/development.html
.. _Installing: https://gpiozero.readthedocs.io/en/stable/installing.html

.. _Ben Nuttall: https://github.com/bennuttall
.. _Dave Jones: https://github.com/waveform80
.. _Andrew Scheller: https://github.com/lurch
.. _Martin O'Hanlon: https://github.com/martinohanlon
.. _Steve Amor: https://github.com/SteveAmor
.. _David Glaude: https://github.com/dglaude
.. _Edward Betts: https://github.com/edwardbetts
.. _Alex Chan: https://github.com/alexwlchan
.. _Thijs Triemstra: https://github.com/thijstriemstra
.. _Schelto vanDoorn: https://github.com/goloplo
.. _Alex Eames: https://github.com/raspitv
.. _Barry Byford: https://github.com/ukBaz
.. _Clare Macrae: https://github.com/claremacrae
.. _Tim Golden: https://github.com/tjguk
.. _Phil Howard: https://github.com/Gadgetoid
.. _Stewart Adcock: https://github.com/stewartadcock
.. _Ian Harcombe: https://github.com/MrHarcombe
