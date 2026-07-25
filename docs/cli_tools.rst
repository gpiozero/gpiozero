.. GPIO Zero: A simple interface to GPIO devices with Raspberry Pi
..
.. Copyright (c) 2021-2026 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016 Stewart <stewart@adcock.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

==================
Command-line Tools
==================

The gpiozero package contains a database of information about the various
revisions of Raspberry Pi. This is queried by the :program:`pinout`
command-line tool to output details of the GPIO pins available. The
:program:`pintest` tool is also provided to test the operation of GPIO pins on
the board.

.. toctree::
   :maxdepth: 1

   cli_pinout
   cli_pintest
   cli_env
