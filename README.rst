========
gpiozero
========

A simple interface to GPIO devices with `Raspberry Pi`_, developed and maintained
by `Ben Nuttall`_ and `Dave Jones`_.

.. _Raspberry Pi: https://www.raspberrypi.org/
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

GPIO Zero is installed by default in the Raspberry Pi OS desktop image,
available from `raspberrypi.org`_. To install on Raspberry Pi OS Lite or other
operating systems, including for PCs using remote GPIO, see the `Installing`_
chapter.

.. _raspberrypi.org: https://www.raspberrypi.org/software/
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
.. _Raspberry Pi Forums: https://www.raspberrypi.org/forums/

Python 2 support
================

.. warning::

    Version 1.6.0 of GPIO Zero is the last to support Python 2. The next release
    will be Version 2.0.0 and will support Python 3 only.

Contributors
============

- `Alex Chan`_
- `Alex Eames`_
- `Andrew Scheller`_
- `Barry Byford`_
- `Carl Monk`_
- `Claire Pollard`_
- `Clare Macrae`_
- `Dan Jackson`_
- `Daniele Procida`_
- `damosurfer`_
- `David Glaude`_
- `Delcio Torres`_
- `Edward Betts`_
- `Fatih Sarhan`_
- `G.S.`_
- `Ian Harcombe`_
- `Jack Wearden`_
- `Jeevan M R`_
- `Josh Thorpe`_
- `Kyle Morgan`_
- `Linus Groh`_
- `Mahallon`_
- `Maksim Levental`_
- `Martchus`_
- `Martin O'Hanlon`_
- `Mike Kazantsev`_
- `Paulo Mateus`_
- `Phil Howard`_
- `Philippe Muller`_
- `Rick Ansell`_
- `Robert Erdin`_
- `Russel Winder`_
- `Ryan Walmsley`_
- `Schelto van Doorn`_
- `Sofiia Kosovan`_
- `Steve Amor`_
- `Stewart Adcock`_
- `Thijs Triemstra`_
- `Tim Golden`_
- `Yisrael Dov Lebow`_

See the `contributors page`_ on GitHub for more info.

.. _Alex Chan: https://github.com/gpiozero/gpiozero/commits?author=alexwlchan
.. _Alex Eames: https://github.com/gpiozero/gpiozero/commits?author=raspitv
.. _Andrew Scheller: https://github.com/gpiozero/gpiozero/commits?author=lurch
.. _Barry Byford: https://github.com/gpiozero/gpiozero/commits?author=ukBaz
.. _Carl Monk: https://github.com/gpiozero/gpiozero/commits?author=ForToffee
.. _Chris R: https://github.com/gpiozero/gpiozero/commits?author=chrisruk
.. _Claire Pollard: https://github.com/gpiozero/gpiozero/commits?author=tuftii
.. _Clare Macrae: https://github.com/gpiozero/gpiozero/commits?author=claremacrae
.. _Dan Jackson: https://github.com/gpiozero/gpiozero/commits?author=e28eta
.. _Daniele Procida: https://github.com/evildmp
.. _Dariusz Kowalczyk: https://github.com/gpiozero/gpiozero/commits?author=darton
.. _damosurfer: https://github.com/gpiozero/gpiozero/commits?author=damosurfer
.. _David Glaude: https://github.com/gpiozero/gpiozero/commits?author=dglaude
.. _Delcio Torres: https://github.com/gpiozero/gpiozero/commits?author=delciotorres
.. _Edward Betts: https://github.com/gpiozero/gpiozero/commits?author=edwardbetts
.. _Fatih Sarhan: https://github.com/gpiozero/gpiozero/commits?author=f9n
.. _G.S.: https://github.com/gpiozero/gpiozero/commits?author=gszy
.. _Ian Harcombe: https://github.com/gpiozero/gpiozero/commits?author=MrHarcombe
.. _Jack Wearden: https://github.com/gpiozero/gpiozero/commits?author=NotBobTheBuilder
.. _Jeevan M R: https://github.com/gpiozero/gpiozero/commits?author=jee1mr
.. _Josh Thorpe: https://github.com/gpiozero/gpiozero/commits?author=ThorpeJosh
.. _Kyle Morgan: https://github.com/gpiozero/gpiozero/commits?author=knmorgan
.. _Linus Groh: https://github.com/gpiozero/gpiozero/commits?author=linusg
.. _Mahallon: https://github.com/gpiozero/gpiozero/commits?author=Mahallon
.. _Maksim Levental: https://github.com/gpiozero/gpiozero/commits?author=makslevental
.. _Martchus: https://github.com/gpiozero/gpiozero/commits?author=Martchus
.. _Martin O'Hanlon: https://github.com/martinohanlon/commits?author=martinohanlon
.. _Mike Kazantsev: https://github.com/gpiozero/gpiozero/commits?author=mk-fg
.. _Paulo Mateus: https://github.com/gpiozero/gpiozero/commits?author=SrMouraSilva
.. _Phil Howard: https://github.com/gpiozero/gpiozero/commits?author=Gadgetoid
.. _Philippe Muller: https://github.com/gpiozero/gpiozero/commits?author=pmuller
.. _Rick Ansell: https://github.com/gpiozero/gpiozero/commits?author=ricksbt
.. _Robert Erdin: https://github.com/gpiozero/gpiozero/commits?author=roberterdin
.. _Russel Winder: https://github.com/russel
.. _Ryan Walmsley: https://github.com/gpiozero/gpiozero/commits?author=ryanteck
.. _Schelto van Doorn: https://github.com/gpiozero/gpiozero/commits?author=goloplo
.. _Sofiia Kosovan: https://github.com/gpiozero/gpiozero/commits?author=SofiiaKosovan
.. _Steve Amor: https://github.com/gpiozero/gpiozero/commits?author=SteveAmor
.. _Stewart Adcock: https://github.com/gpiozero/gpiozero/commits?author=stewartadcock
.. _Thijs Triemstra: https://github.com/gpiozero/gpiozero/commits?author=thijstriemstra
.. _Tim Golden: https://github.com/gpiozero/gpiozero/commits?author=tjguk
.. _Yisrael Dov Lebow: https://github.com/gpiozero/gpiozero/commits?author=yisraeldov

.. _contributors page: https://github.com/gpiozero/gpiozero/graphs/contributors
