.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2021 Dave Jones <dave@waveform.org.uk>
..
.. SPDX-License-Identifier: BSD-3-Clause

===========
API - Fonts
===========

.. module:: gpiozero.fonts

GPIO Zero includes a concept of "fonts" which is somewhat different to that you
may be familiar with. While a typical printing font determines how a particular
character is rendered on a page, a GPIO Zero font determines how a particular
character is rendered by a series of lights, like LED segments (e.g. with
:class:`~gpiozero.LEDCharDisplay` or :class:`~gpiozero.LEDMultiCharDisplay`).

As a result, GPIO Zero's fonts are quite crude affairs, being little more than
mappings of characters to tuples of LED states. Still, it helps to have a
"friendly" format for creating such fonts, and in this module the library
provides several routines for this purpose.

The module itself is typically imported as follows::

    from gpiozero import fonts


Font Parsing
============

.. autofunction:: load_font_7seg

.. autofunction:: load_font_14seg

.. autofunction:: load_segment_font
