.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2021 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016 Stewart <stewart@adcock.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

==================
Command-line Tools
==================

The gpiozero package contains a database of information about the various
revisions of Raspberry Pi. This is queried by the :program:`pinout`
command-line tool to output details of the GPIO pins available.

.. note::

    Note that only the Python 3 version of the Debian package includes the
    pinout command line tool, so as not to create a conflict if both versions
    are installed. If you only installed the ``python-gpiozero`` apt package,
    the pinout tool will not be available. Instead, you can additionally install
    the ``python3-gpiozero`` package, or alternatively install gpiozero using
    pip.

.. include:: cli_pinout.rst
