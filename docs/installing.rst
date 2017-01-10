====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in `Raspbian Jessie`_ and `PIXEL x86`_, available
from `raspberrypi.org`_. Follow these guides to installing on other operating
systems, including for PCs using the :doc:`remote_gpio` feature.

Raspberry Pi
============

First, update your repositories list::

    sudo apt-get update

Then install the package for Python 3::

    sudo apt-get install python3-gpiozero

or Python 2::

    sudo apt-get install python-gpiozero

Linux
=====

First, update your distribution's repositories list. For example::

    sudo apt-get update

Then install pip for Python 3::

    sudo apt-get install python3-pip

or Python 3::

    sudo apt-get install python-pip

(Alternatively, install pip with `get-pip`_.)

Next, install gpiozero for Python 3::

    sudo pip3 install gpiozero

or Python 2::

    sudo pip install gpiozero

.. note::

    We welcome Linux distribution maintainers to include the gpiozero packages
    in their repositories. Any questions you have, please ask questions on
    `GitHub`_ and we'll be happy to help.

Mac OS
======

First, install pip::

    ???

Next, install gpiozero with pip::

    pip install gpiozero

Windows
=======

First, install pip::

    ???

Next, install gpiozero with pip::

    pip install gpiozero


.. Raspbian Jessie_: https://www.raspberrypi.org/downloads/raspbian/
.. PIXEL x86_: https://www.raspberrypi.org/blog/pixel-pc-mac/
.. raspberrypi.org_: https://www.raspberrypi.org/downloads/
.. get-pip_: https://pip.pypa.io/en/stable/installing/
.. GitHub: https://github.com/RPi-Distro/python-gpiozero/issues
