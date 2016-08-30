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

A simple interface to everyday GPIO components used with Raspberry Pi.

Created by `Ben Nuttall`_ of the `Raspberry Pi Foundation`_, `Dave Jones`_, and
other contributors.

About
=====

Component interfaces are provided to allow a frictionless way to get started
with physical computing::

    from gpiozero import LED
    from time import sleep

    led = LED(17)

    while True:
        led.on()
        sleep(1)
        led.off()
        sleep(1)

With very little code, you can quickly get going connecting your components
together::

    from gpiozero import LED, Button
    from signal import pause

    led = LED(17)
    button = Button(3)

    button.when_pressed = led.on
    button.when_released = led.off

    pause()

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more.

Install
=======

First, update your repositories list::

    sudo apt-get update

Then install the package of your choice. Both Python 3 and Python 2 are
supported. Python 3 is recommended::

    sudo apt-get install python3-gpiozero

or::

    sudo apt-get install python-gpiozero

Documentation
=============

Comprehensive documentation is available at https://gpiozero.readthedocs.io/.

Development
===========

This project is being developed on `GitHub`_. Join in:

* Provide suggestions, report bugs and ask questions as `issues`_
* Provide examples we can use as `recipes`_
* `Contribute`_ to the code

Alternatively, email suggestions and feedback to mailto:ben@raspberrypi.org

Contributors
============

- `Ben Nuttall`_ (project maintainer)
- `Dave Jones`_
- `Martin O'Hanlon`_
- `Andrew Scheller`_
- `Schelto vanDoorn`_


.. _Raspberry Pi Foundation: https://www.raspberrypi.org/
.. _GitHub: https://github.com/RPi-Distro/python-gpiozero
.. _issues: https://github.com/RPi-Distro/python-gpiozero/issues
.. _recipes: http://gpiozero.readthedocs.io/en/latest/recipes.html
.. _contribute: http://gpiozero.readthedocs.io/en/latest/contributing.html
.. _Ben Nuttall: https://github.com/bennuttall
.. _Dave Jones: https://github.com/waveform80
.. _Martin O'Hanlon: https://github.com/martinohanlon
.. _Andrew Scheller: https://github.com/lurch
.. _Schelto vanDoorn: https://github.com/pcopa
