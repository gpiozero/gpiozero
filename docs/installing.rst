.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017 Ben Nuttall <ben@bennuttall.com>
..
.. Redistribution and use in source and binary forms, with or without
.. modification, are permitted provided that the following conditions are met:
..
.. * Redistributions of source code must retain the above copyright notice,
..   this list of conditions and the following disclaimer.
..
.. * Redistributions in binary form must reproduce the above copyright notice,
..   this list of conditions and the following disclaimer in the documentation
..   and/or other materials provided with the distribution.
..
.. * Neither the name of the copyright holder nor the names of its contributors
..   may be used to endorse or promote products derived from this software
..   without specific prior written permission.
..
.. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
.. AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
.. IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
.. ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
.. LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
.. CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
.. SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
.. INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
.. CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
.. ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
.. POSSIBILITY OF SUCH DAMAGE.

====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in the `Raspbian`_ image, and the
`Raspberry Pi Desktop`_ image for PC/Mac, both available from
`raspberrypi.org`_. Follow these guides to installing on Raspbian Lite
and other operating systems, including for PCs using the
:doc:`remote GPIO <remote_gpio>` feature.

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


.. _Raspbian: https://www.raspberrypi.org/downloads/raspbian/
.. _Raspberry Pi Desktop: https://www.raspberrypi.org/downloads/raspberry-pi-desktop/
.. _raspberrypi.org: https://www.raspberrypi.org/downloads/
.. _get-pip: https://pip.pypa.io/en/stable/installing/
