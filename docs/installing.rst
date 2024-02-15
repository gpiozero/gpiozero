.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2021 Cameron Davidson-Pilon <cam.davidson.pilon@gmail.com>
.. Copyright (c) 2017-2021 Ben Nuttall <ben@bennuttall.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

====================
Installing GPIO Zero
====================

GPIO Zero is installed by default in the `Raspberry Pi OS`_ desktop image,  `Raspberry Pi OS`_ Lite image, and
the `Raspberry Pi Desktop`_ image for PC/Mac, all available from
`raspberrypi.org`_. Follow these guides to installing on other operating systems, including for PCs using the :doc:`remote GPIO
<remote_gpio>` feature.

.. _Raspberry Pi OS: https://www.raspberrypi.org/software/operating-systems/
.. _Raspberry Pi Desktop: https://www.raspberrypi.org/software/raspberry-pi-desktop/
.. _raspberrypi.org: https://www.raspberrypi.org/software/

Raspberry Pi
============

GPIO Zero is packaged in the apt repositories of Raspberry Pi OS, `Debian`_ and
`Ubuntu`_. It is also available on `PyPI`_.

.. _Debian: https://packages.debian.org/buster/python3-gpiozero
.. _Ubuntu: https://packages.ubuntu.com/hirsute/python3-gpiozero
.. _PyPI: https://pypi.org/project/gpiozero/

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

pip
---

If you're using another operating system on your Raspberry Pi, you may need to
use pip to install GPIO Zero instead. Install pip using `get-pip`_ and then
type:

.. code-block:: console

    pi@raspberrypi:~$ sudo pip3 install gpiozero

or for Python 2:

.. code-block:: console

    pi@raspberrypi:~$ sudo pip install gpiozero

To install GPIO Zero in a virtual environment, see the :doc:`development` page.

.. _get-pip: https://pip.pypa.io/en/stable/installing/

PC/Mac
======

In order to use GPIO Zero's remote GPIO feature from a PC or Mac, you'll need
to install GPIO Zero on that computer using pip. See the :doc:`remote_gpio`
page for more information.

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
To avoid this, you can view the docs from an ``http://`` style URL by starting
a trivial HTTP server with Python, like so:

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
