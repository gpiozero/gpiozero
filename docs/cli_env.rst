.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

=====================
Environment Variables
=====================

All utilities provided by GPIO Zero accept the following environment variables:

.. envvar:: GPIOZERO_PIN_FACTORY

    The library to use when communicating with the GPIO pins. Defaults to
    attempting to load lgpio, then RPi.GPIO, then pigpio, and finally uses a
    native Python implementation. Valid values include "lgpio", "rpigpio",
    "pigpio", "native", and "mock". The latter is most useful on non-Pi
    platforms as it emulates a Raspberry Pi model 3B (by default).

.. envvar:: PIGPIO_ADDR

    The hostname of the Raspberry Pi the pigpio library should attempt to
    connect to (if the pigpio pin factory is being used). Defaults to
    ``localhost``.

.. envvar:: PIGPIO_PORT

    The port number the pigpio library should attempt to connect to (if the
    pigpio pin factory is being used). Defaults to ``8888``.


.. only:: builder_man

    See Also
    --------

    :manpage:`pinout(1)`, :manpage:`pintest(1)`
