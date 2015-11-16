========
gpiozero
========

A simple interface to everyday GPIO components used with Raspberry Pi.

Created by `Ben Nuttall`_ of the `Raspberry Pi Foundation`_, `Dave Jones`_, and
other contributors.

Latest release
==============

The latest release is 1.0 released on 16th November 2015.

About
=====

With very little code, you can quickly get going connecting your physical
components together::

    from gpiozero import LED, Button

    led = LED(2)
    button = Button(3)

    button.when_pressed = led.on
    button.when_released = led.off

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more.

Install
=======

First, install the dependencies::

    sudo apt-get install python-pip python3-pip python-spidev python3-spidev

Install with pip::

    sudo pip install gpiozero
    sudo pip-3.2 install gpiozero

Both Python 3 and Python 2 are supported. Python 3 is recommended!

Documentation
=============

Comprehensive documentation is available at `pythonhosted.org/gpiozero`_.

Development
===========

This project is being developed on `GitHub`_. Join in:

* Provide suggestions, report bugs and ask questions as `Issues`_
* Provide examples we can use as `recipes`_
* Contribute to the code

Alternatively, email suggestions and feedback to ben@raspberrypi.org or add to
the `Google Doc`_.

Contributors
============

- `Ben Nuttall`_ (project maintainer)
- `Dave Jones`_
- `Martin O'Hanlon`_


.. _Ben Nuttall: https://github.com/bennuttall
.. _Raspberry Pi Foundation: https://www.raspberrypi.org/
.. _Dave Jones: https://github.com/waveform80
.. _pythonhosted.org/gpiozero: http://pythonhosted.org/gpiozero
.. _GitHub: https://github.com/RPi-Distro/python-gpiozero
.. _Issues: https://github.com/RPi-Distro/python-gpiozero/issues
.. _recipes: http://pythonhosted.org/gpiozero/recipes/
.. _Google Doc: https://goo.gl/8zJLif
.. _Ben Nuttall: https://github.com/bennuttall
.. _Dave Jones: https://github.com/waveform80
.. _Martin O'Hanlon: https://github.com/martinohanlon
