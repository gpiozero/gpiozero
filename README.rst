========
gpiozero
========

A simple interface to everyday GPIO components used with Raspberry Pi

Latest release: v0.7.0 Beta 2

Motivation
==========

The "hello world" program in Java is at least 5 lines long, and contains 11
jargon words which students are taught to ignore.

The "hello world" program in Python is one simple line. However, the "hello
world" of physical computing in Python (flashing an LED) is similar to the Java
program: 6 lines of code to flash an LED.

Young children and beginners shouldn't need to sit and copy out several lines
of text they're told to ignore. They should be able to read their code and
understand what it means.

Install
=======

Install with pip::

    sudo pip install gpiozero
    sudo pip-3.2 install gpiozero

Both Python 3 and Python 2 are supported. Python 3 is recommended!

Usage
=====

Example usage for lighting up an LED::

    from gpiozero import LED

    led = LED(2)

    led.on()

Documentation
=============

Comprehensive documentation is available at `pythonhosted.org/gpiozero`_.

Development
===========

This project is being developed on `GitHub`_. Join in:

* Provide suggestions, report bugs and ask questions as `Issues`_
* Help design the `API`_
* Contribute to the code

Alternatively, email suggestions and feedback to ben@raspberrypi.org or add to the `Google Doc`_.

Contributors
============

- `Ben Nuttall`_ (project maintainer)
- `Dave Jones`_
- `Martin O'Hanlon`_


.. _`pythonhosted.org/gpiozero`: http://pythonhosted.org/gpiozero
.. _`GitHub`: https://github.com/RPi-Distro/python-gpiozero
.. _`Issues`: https://github.com/RPi-Distro/python-gpiozero/issues
.. _`API`: https://github.com/RPi-Distro/python-gpiozero/issues/7
.. _`Google Doc`: https://docs.google.com/document/d/1EbbVjdgXbKVPFlgH_pEEtPZ0zOZVSPHT4sQNW88Am7w/edit?usp=sharing
.. _`Ben Nuttall`: https://github.com/bennuttall
.. _`Dave Jones`: https://github.com/waveform80
.. _`Martin O'Hanlon`: https://github.com/martinohanlon
