===========
Remote GPIO
===========

.. currentmodule:: gpiozero

GPIO Zero supports a number of different pin implementations (low-level pin
libraries which deal with the GPIO pins directly). By default, the `RPi.GPIO`_
library is used (assuming it is installed on your system), but you can
optionally specify one to use. For more information, see the :doc:`pins`
documentation page.

One of the pin libraries supported, `pigpio`_, provides the ability to control
GPIO pins remotely over the network, which means you can use GPIO Zero to
control devices connected to a Raspberry Pi on the network. You can do this from
another Raspberry Pi, or even from a PC.

See the :doc:`recipes_remote_gpio` page for examples on how remote pins can be
used.

Preparing the Raspberry Pi
==========================

If you're using Raspbian Jessie (desktop - not Jessie Lite) then you have
everything you need to use the remote GPIO feature. If you're using Jessie Lite,
or another distribution, you'll need to install pigpio::

    sudo apt install pigpio

Then you just need to enable **Remote GPIO** in the Raspberry Pi configuration
tool:

.. image:: images/raspi-config.png

(Alternatively, use ``sudo raspi-config`` on the command line)

Then launch the pigpio daemon::

    sudo pigpiod

To only allow connections from a specific IP address, use the ``-n`` flag. For
example::

    sudo pigpiod -n localhost # allow localhost only
    sudo pigpiod -n 192.168.1.65 # allow 192.168.1.65 only
    sudo pigpiod -n localhost -n 192.168.1.65 # allow localhost and 192.168.1.65 only

You will need to launch the pigpio daemon every time you wish to use this
feature. To automate running the daemon at boot time::

    sudo systemctl enable pigpiod

Preparing the host computer
===========================

If the host computer is a Raspberry Pi running Raspbian Jessie (or a PC running
x86 PIXEL), then you have everything you need. If you're using another Linux
distribution, Mac OS or Windows then you'll need to install the ``pigpio``
Python library on the PC.

Raspberry Pi
------------

First, update your repositories list::

    sudo apt update

Then install the pigpio library for Python 3::

    sudo apt install python3-pigpio

or Python 2::

    sudo apt install python-pigpio

Alternatively, install with pip::

    sudo pip3 install pigpio

or::

    sudo pip install pigpio

Linux
-----

First, update your distribution's repositories list. For example::

    sudo apt update

Then install pip for Python 3::

    sudo apt install python3-pip

or Python 2::

    sudo apt install python-pip

(Alternatively, install pip with `get-pip`_.)

Next, install pigpio for Python 3::

    sudo pip3 install pigpio

or Python 2::

    sudo pip install pigpio

Mac OS
------

First, install pip::

    ???

Next, install pigpio with pip::

    pip install pigpio

Windows
-------

First install pip::

    ???

Next, install pigpio with pip::

    pip install pigpio

Environment variables
=====================

The simplest way to use devices with remote pins is to set the ``PIGPIO_ADDR``
environment variable to the IP address of the desired Raspberry Pi. You must
run your Python script or launch your development environment with the
environment variable set using the command line. For example, one of the
following::

    $ PIGPIO_ADDR=192.168.1.3 python3 hello.py
    $ PIGPIO_ADDR=192.168.1.3 python3
    $ PIGPIO_ADDR=192.168.1.3 ipython3
    $ PIGPIO_ADDR=192.168.1.3 idle3 &

If you are running this from a PC (not a Raspberry Pi) with gpiozero and the
pigpio Python library installed, this will work with no further configuration.
However, if you are running this from a Raspberry Pi, you will also need to
ensure the default pin factory is set to ``PiGPIOPin``. If ``RPi.GPIO`` is
installed, this will be selected as the default pin factory, so either uninstall
it, or use another environment variable to set it to ``PiGPIOPin``::

    $ GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=192.168.1.3 python3 hello.py

This usage will set the pin factory to :class:`PiGPIOPin` with a default host of
``192.168.1.3``. The pin factory can be changed inline in the code, as seen in
the following sections.

With this usage, you can write gpiozero code like you would on a Raspberry Pi,
with no modifications needed. For example:

.. literalinclude:: examples/led_1.py

When run with::

    $ PIGPIO_ADDR=192.168.1.3 python3 led.py

will flash the LED connected to pin 17 of the Raspberry Pi with the IP address
``192.168.1.3``. And::

    $ PIGPIO_ADDR=192.168.1.4 python3 led.py

will flash the LED connected to pin 17 of the Raspberry Pi with the IP address
``192.168.1.4``, without any code changes.

Pin objects
===========

An alternative (or additional) method of configuring gpiozero objects to use
remote pins is to create instances of :class:PiGPIOPin objects, and
instantiating device objects with those pin objects, rather than just numbers.
For example, with no environment variables set:

.. literalinclude:: examples/led_remote_1.py

This allows devices on multiple Raspberry Pis to be used in the same script:

.. literalinclude:: examples/led_remote_2.py

You can, of course, continue to create gpiozero device objects as normal, and
create others using remote pins. For example, if run on a Raspberry Pi, the
following script will flash an LED on the host Pi, and also on another Pi on the
network:

.. literalinclude:: examples/led_remote_3.py

Alternatively, when run with the environment variables
``GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=192.168.1.3`` set, the following
script will behave exactly the same as the previous one:

.. literalinclude:: examples/led_remote_4.py

Of course, multiple IP addresses can be used:

.. literalinclude:: examples/led_remote_5.py

Note that these examples use the :class:`LED` class, which takes a ``pin``
argument to initialise. Some classes, particularly those representing HATs and
other add-on boards, do not require their pin numbers to be specified. However,
it is still possible to use remote pins with these devices, either using
environment variables, or by using :meth:`~Device._set_pin_factory`:

.. literalinclude:: examples/traffichat_remote_1.py

This also allows you to swap between two IP addresses and create instances of
multiple HATs connected to different Pis:

.. literalinclude:: examples/traffichat_remote_2.py

You could even use a HAT which is not supported by GPIO Zero (such as the
`Sense HAT`_) on one Pi, and use remote pins to control another over the
network:

.. literalinclude:: examples/sense_hat_remote.py

Note that in this case, the Sense HAT code must be run locally, and the GPIO
remotely.

Pi Zero USB OTG
===============

The `Raspberry Pi Zero`_ and `Pi Zero W`_ feature a USB OTG port, allowing users
to configure the device as (amongst other things) an Ethernet device. In this
mode, it is possible to control the Pi Zero's GPIO pins over USB from another
computer using remote pins.

First, configure the boot partition of the SD card:

1. Edit ``config.txt`` and add ``dtoverlay=dwc2`` on a new line, then save the
file.
2. Create an empty file called ``ssh`` (no file extension) and save it in the
boot partition.
3. Edit ``cmdline.txt`` and insert ``modules-load=dwc2,g_ether`` after
``rootwait``.

(See `blog.gbaman.info`_ for more information)

Then connect the Pi Zero to your computer using a micro USB cable (connecting it
to the USB port, not the power port). You'll see the indicator LED flashing as
the Pi Zero boots. When it's ready, you will be able to ping and SSH into it
using the hostname ``raspberrypi.local``. SSH into the Pi Zero, ensure Remote
GPIO is enabled and the pigpio daemon is running, and you can use remote pins
from the computer, referencing the host by its hostname, like so:

.. literalinclude:: examples/pi_zero_remote.py

.. note::

    When running code directly on a Raspberry Pi, any pin type can be used
    (assuming the relevant library is installed), but when a device is used
    remotely, only :class:`PiGPIOPin` can be used, as pigpio is the only pin
    library which supports remote GPIO.


.. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO
.. _pigpio: http://abyz.co.uk/rpi/pigpio/python.html
.. _get-pip: https://pip.pypa.io/en/stable/installing/
.. _Sense HAT: https://www.raspberrypi.org/products/sense-hat/
.. _Raspberry Pi Zero: https://www.raspberrypi.org/products/pi-zero/
.. _Pi Zero W: https://www.raspberrypi.org/products/pi-zero-w/
.. _blog.gbaman.info: http://blog.gbaman.info/?p=791
