.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

====================
API - Pi Information
====================

.. module:: gpiozero.pins.data

.. currentmodule:: gpiozero

The GPIO Zero library also contains a database of information about the various
revisions of the Raspberry Pi computer. This is used internally to raise
warnings when non-physical pins are used, or to raise exceptions when
pull-downs are requested on pins with physical pull-up resistors attached. The
following functions and classes can be used to query this database:


pi_info
=======

.. autofunction:: pi_info


PiBoardInfo
===========

.. autoclass:: PiBoardInfo


HeaderInfo
==========

.. autoclass:: HeaderInfo


PinInfo
=======

.. autoclass:: PinInfo
