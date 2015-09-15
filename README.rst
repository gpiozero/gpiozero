========
gpiozero
========

A simple interface to everyday GPIO components used with Raspberry Pi

*A work in progress*

Motivation
==========

The "hello world" program in Java is at least 5 lines long, and contains 11 jargon words which students are taught to ignore.

The "hello world" program in Python is one simple line. However, the "hello world" of physical computing in Python (flashing an LED) is similar to the Java program: 6 lines of code to flash an LED.

Young children and beginners shouldn't need to sit and copy out several lines of text they're told to ignore. They should be able to read their code and understand what it means.

Install
=======

Install with pip::

    sudo pip install gpiozero
    sudo pip-3.2 install gpiozero

Usage
=====

Example usage for flashing an LED::

    from gpiozero import LED
    from time import sleep

    led = LED(2)

    while True:
        led.on()
        sleep(1)
        led.off()
        sleep(1)

Development
===========

This project is being developed on `GitHub`_. Join in:

* Provide suggestions
* Help design the `API`_
* Contribute to the code

Alternatively, email suggestions and feedback to ben@raspberrypi.org


.. _`GitHub`: https://github.com/RPi-Distro/python-gpiozero
.. _`API`: https://github.com/RPi-Distro/python-gpiozero/issues/7
