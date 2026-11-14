========
gpiozero
========

A simple interface to GPIO devices with `Raspberry Pi`_, developed and
maintained by `Ben Nuttall`_ and `Dave Jones`_.

.. _Raspberry Pi: https://www.raspberrypi.com/
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
`source tools`_ to describe the behaviour of devices and their
interactions:

.. code:: python

    from gpiozero import OutputDevice, MotionSensor, LightSensor
    from gpiozero.tools import booleanized, all_values
    from signal import pause

    garden = OutputDevice(17)
    motion = MotionSensor(4)
    light = LightSensor(5)

    garden.source = all_values(booleanized(light, 0, 0.1), motion)

    pause()

See the chapter on `Source/Values`_ for more information.

.. _Source/Values: https://gpiozero.readthedocs.io/en/stable/source_values.html
.. _source tools: https://gpiozero.readthedocs.io/en/stable/api_tools.html

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more. See the `Recipes`_ chapter of the
documentation for ideas on how to get started.

.. _Recipes: https://gpiozero.readthedocs.io/en/stable/recipes.html

Pin factories
=============

GPIO Zero builds on a number of underlying pin libraries. You can select a
particular pin library to be used, either for the whole script or per-device,
according to your needs. See the section on `changing the pin factory`_.

.. _changing the pin factory: https://gpiozero.readthedocs.io/en/stable/api_pins.html#changing-the-pin-factory

A "mock pin" interface is also provided for testing purposes. Read more about
this in the section on `mock pins`_.

.. _mock pins: https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins

Installation
============

GPIO Zero is installed by default in the Raspberry Pi OS desktop images,
available from `raspberrypi.com`_. To install on Raspberry Pi OS Lite or other
operating systems, including for PCs using remote GPIO or mock pins, see the
`Installing`_ chapter.

.. _raspberrypi.com: https://www.raspberrypi.com/software/
.. _Installing: https://gpiozero.readthedocs.io/en/stable/installing.html

Documentation
=============

Comprehensive documentation is available at https://gpiozero.readthedocs.io/.
Please refer to the `Contributing`_ and `Development`_ chapters in the
documentation for information on contributing to the project.

.. _Contributing: https://gpiozero.readthedocs.io/en/stable/contributing.html
.. _Development: https://gpiozero.readthedocs.io/en/stable/development.html

Issues and questions
====================

If you have a feature request or bug report, please open an `issue on GitHub`_.
If you have a question or need help, this may be better suited to our `GitHub
discussion board`_, the `Raspberry Pi Stack Exchange`_ or the `Raspberry Pi
Forums`_.

.. _issue on GitHub: https://github.com/gpiozero/gpiozero/issues/new
.. _GitHub discussion board: https://github.com/gpiozero/gpiozero/discussions
.. _Raspberry Pi Stack Exchange: https://raspberrypi.stackexchange.com/
.. _Raspberry Pi Forums: https://forums.raspberrypi.com/

Contributing
============

Please see the `Contributing guide`_on GitHub for more information, including
our guidance on AI contributions.

.. _Contributing guide: https://github.com/gpiozero/gpiozero/blob/dev/.github/CONTRIBUTING.md

For a list of people who have contributed to the project, see the `contributors
page`_ on GitHub.

.. _contributors page: https://github.com/gpiozero/gpiozero/graphs/contributors?all=1
