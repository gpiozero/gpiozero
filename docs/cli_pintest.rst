.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

pintest
=======

A utility for testing the GPIO pins on a Raspberry Pi, inspired by pigpio's
gpiotest example script, and wiringPi's pintest utility.

.. only:: not builder_man

    .. versionadded:: 2.0
        The :program:`pintest` utility.

    .. image:: images/pintest.png
        :alt: A screenshot of the output from pintest. In a terminal window,
              pintest has prompted the user with the list of GPIOs it intends
              to test and asked for confirmation to proceed. Having received
              this confirmation, it's printed out each GPIO in turn with "ok"
              after it, indicating success.


Synopsis
--------

::

    pintest [-h] [--version] [-p PINS] [-s SKIP] [-y] [-r REVISION]


Description
-----------

A utility for testing the function of GPIOs on a Raspberry Pi. It is possible
to damage the GPIOs on a Pi by passing too much current (or voltage in the case
of inputs) through them. The :program:`pintest` utility can be used to
determine if any of the GPIOs on a Pi are broken.

The utility will test all physically exposed GPIOs (those on the main GPIO
header) by default, but you may wish to only test a subset, or to exclude
certain GPIOs which can be accomplished with the :option:`pintest --pins` or
:option:`pintest --skip` options.

.. note::

    You must ensure that nothing is connected to the GPIOs that you intend to
    test. By default, the utility will prompt you before proceeding, repeating
    this warning.

In the event that any GPIO is found to be faulty, it will be reported in the
output and the utility will exit with a return code of 1. If all specified
GPIOs test fine, the return code is zero.


Options
-------

.. program:: pintest

.. option:: -h, --help

    show this help message and exit

.. option::  --version

    Show the program's version number and exit

.. option:: -p PINS, --pins PINS

   The pin(s) to test. Can be specified as a comma-separated list of pins. Pin
   numbers can be given in any form accepted by gpiozero, e.g. 14, GPIO14,
   BOARD8. The default is to test all pins

.. option:: -s SKIP, --skip SKIP

    The pin(s) to skip testing. Can be specified as comma-separated list of
    pins. Pin numbers can be given in any form accepted by gpiozero, e.g. 14,
    GPIO14, BOARD8. The default is to skip no pins

.. option:: -y, --yes

    Proceed without prompting

.. option:: -r REVISION, --revision REVISION

    Force board revision. Default is to autodetect revision of current device.
    You should avoid this option unless you are very sure the detection is
    incorrect


Examples
--------

Test all physically exposed GPIOs on the board:

.. code-block:: console

    $ pintest

Test just the I2C GPIOs without prompting:

.. code-block:: console

    $ pintest --pins 2,3 --yes

Exclude the SPI GPIOs from testing:

.. code-block:: console

    $ pintest --exclude GPIO7,GPIO8,GPIO9,GPIO10,GPIO11

Note that pin numbers can be given in any form accepted by GPIO Zero, e.g. 14,
GPIO14, or BOARD8.


.. only:: builder_man

    See Also
    --------

    :manpage:`pinout(1)`, :manpage:`gpiozero-env(7)`
