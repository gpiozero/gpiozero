====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in `Raspbian Jessie`_ and `PIXEL x86`_,
available from `raspberrypi.org`_. Follow these guides to installing on other
operating systems, including for PCs using the :doc:`remote_gpio` feature.

Raspberry Pi
============

First, update your repositories list:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt update

Then install the package for Python 3:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt install python3-gpiozero

or Python 2:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt install python-gpiozero

Linux
=====

First, update your distribution's repositories list. For example:

.. code-block:: console

    $ sudo apt update

Then install pip for Python 3:

.. code-block:: console

    $ sudo apt install python3-pip

or Python 3:

.. code-block:: console

    $ sudo apt install python-pip

(Alternatively, install pip with `get-pip`_.)

Next, install gpiozero for Python 3:

.. code-block:: console

    $ sudo pip3 install gpiozero

or Python 2:

.. code-block:: console

    $ sudo pip install gpiozero

.. note::

    We welcome Linux distribution maintainers to include the gpiozero packages
    in their repositories. Any questions you have, please ask questions on
    `GitHub`_ and we'll be happy to help.

Mac OS
======

First, install pip:

.. code-block:: console

    $ ???

Next, install gpiozero with pip:

.. code-block:: console

    $ pip install gpiozero

Windows
=======

First, install pip:

.. code-block:: doscon

    C:\Users\user1> ???

Next, install gpiozero with pip:

.. code-block:: doscon

    C:\Users\user1> pip install gpiozero


.. _Raspbian Jessie: https://www.raspberrypi.org/downloads/raspbian/
.. _PIXEL x86: https://www.raspberrypi.org/blog/pixel-pc-mac/
.. _raspberrypi.org: https://www.raspberrypi.org/downloads/
.. _get-pip: https://pip.pypa.io/en/stable/installing/
.. _GitHub: https://github.com/RPi-Distro/python-gpiozero/issues
