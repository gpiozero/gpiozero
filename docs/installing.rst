.. GPIO Zero: A simple interface to GPIO devices with Raspberry Pi
..
.. Copyright (c) 2017-2026 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2025 Andrew Scheller <lurch@durge.org>
.. Copyright (c) 2017-2021 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in the `Raspberry Pi OS`_ desktop image,
`Raspberry Pi OS`_ Lite image, and the `Raspberry Pi Desktop`_ image for PC/Mac,
all available from `raspberrypi.com`_. Follow these guides to installing on
other operating systems, including for PCs using the :doc:`remote GPIO
<remote_gpio>` feature.

.. _Raspberry Pi OS: https://www.raspberrypi.com/software/operating-systems/
.. _Raspberry Pi Desktop: https://www.raspberrypi.com/software/raspberry-pi-desktop/
.. _raspberrypi.com: https://www.raspberrypi.com/software/

Raspberry Pi
============

GPIO Zero is packaged in the apt repositories of Raspberry Pi OS, `Debian`_ and
`Ubuntu`_. It is also available on `PyPI`_.

.. _Debian: https://packages.debian.org/trixie/python3-gpiozero
.. _Ubuntu: https://packages.ubuntu.com/resolute/python3-gpiozero
.. _PyPI: https://pypi.org/project/gpiozero/

.. warning::

    The version of GPIO Zero in Debian may fall significantly behind the pip and
    Raspberry Pi OS versions

apt
---

First, update your repositories list:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt update

Then install the package for Python 3:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt install python3-gpiozero

or Python 2:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt install python-gpiozero

Virtual environment
-------------------

You may need to install GPIO Zero into a virtual environment. The simplest way
is to create a virtual environment with system packages enabled, so that you can
access the apt installed libraries without having to install them separately:

.. code-block:: console

    pi@raspberrypi:~$ python3 -m venv gpiozero-env --system-site-packages

Then activate the environment (each time you need to use it):

.. code-block:: console

    pi@raspberrypi:~$ source ./gpiozero-env/bin/activate

Once activated, the terminal prompt will be preceded by the name of the
environment:

.. code-block:: console

    (gpiozero-env) pi@raspberrypi:~$

You can then type ``python`` to open a Python console or run a Python program,
and use ``apt`` to install additional libraries from the OS, or ``pip`` to
install additional libraries from `PyPI <https://pypi.org/>`__.

pip
---

.. note::

    Note that for some time, pip installing gpiozero would not work on the
    Raspberry Pi 5 due to a bug in the lgpio pin factory. As of July 2026 (the
    2.0.1.post1 release), this is now fixed.

If you need to install GPIO Zero into a virtual environment without system
packages enabled, first activate your environment (as above) and install GPIO
Zero itself with pip:

.. code-block:: console

    (gpiozero-env) pi@raspberrypi:~$ pip install gpiozero

You will also need to install a pin library. The default and recommended one is
lgpio. This may require compilation, so first install ``python3-dev``, ``swig``,
``liblgpio-dev``:

.. code-block:: console

    (gpiozero-env) pi@raspberrypi:~$ sudo apt install python3-dev swig liblgpio-dev -y

Then install lgpio:

.. code-block:: console

    (gpiozero-env) pi@raspberrypi:~$ pip install lgpio

See :doc:`api_pins` for more information on pin libraries.

PC/Mac
======

You may wish to install GPIO Zero on a PC or Mac for either development
purposes, using :ref:`mock-pins` or :doc:`remote_gpio`. Simply install GPIO Zero
with pip, as above. For remote GPIO, you may need the relevant pin library too.

Documentation
=============

This documentation is also available for offline installation like so:

.. code-block:: console

    pi@raspberrypi:~$ sudo apt install python-gpiozero-doc

This will install the HTML version of the documentation under the
:file:`/usr/share/doc/python-gpiozero-doc/html` path. To view the offline
documentation you have several options:

You can open the documentation directly by visiting
file:///usr/share/doc/python-gpiozero-doc/html/index.html in your browser.
However, be aware that using ``file://`` URLs sometimes breaks certain elements.
To avoid this, you can view the docs from an ``http://`` style URL by starting a
trivial HTTP server with Python, like so:

.. code-block:: console

    $ python3 -m http.server -d /usr/share/doc/python-gpiozero-doc/html

Then visit http://localhost:8000/ in your browser.

Alternatively, the package also integrates into Debian's `doc-base`_ system, so
you can install one of the doc-base clients (dochelp, dwww, dhelp, doc-central,
etc.) and use its interface to locate this document.

If you want to view the documentation offline on a different device, such as an
eReader, there are Epub and PDF versions of the documentation available for
download from the `ReadTheDocs site`_. Simply click on the "Read the Docs" box
at the bottom-left corner of the page (under the table of contents) and select
"PDF" or "Epub" from the "Downloads" section.

.. _doc-base: https://wiki.debian.org/doc-base
.. _ReadTheDocs site: https://gpiozero.readthedocs.io/
