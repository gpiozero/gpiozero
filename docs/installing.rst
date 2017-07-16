====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in `Raspbian Jessie`_ and `Raspbian x86`_,
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

If you're using another operating system on your Raspberry Pi, you may need to
use pip to install GPIO Zero instead. Install pip using `get-pip`_ and then
type:

.. code-block:: console

    pi@raspberrypi:~$ sudo pip3 install gpiozero

or for Python 2:

.. code-block:: console

    pi@raspberrypi:~$ sudo pip install gpiozero

To install GPIO Zero in a virtual environment, see the :doc:`development` page.

PC/Mac
======

In order to use GPIO Zero's remote GPIO feature from a PC or Mac, you'll need
to install GPIO Zero on that computer using pip. See the :doc:`remote_gpio`
page for more information.


.. _Raspbian Jessie: https://www.raspberrypi.org/downloads/raspbian/
.. _Raspbian x86: https://www.raspberrypi.org/blog/pixel-pc-mac/
.. _raspberrypi.org: https://www.raspberrypi.org/downloads/
.. _get-pip: https://pip.pypa.io/en/stable/installing/
