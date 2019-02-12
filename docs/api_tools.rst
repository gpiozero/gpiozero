.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2017-2019 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016 Edward Betts <edward@4angle.com>
.. Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
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

=========================
API - Device Source Tools
=========================

.. module:: gpiozero.tools

GPIO Zero includes several utility routines which are intended to be used with
the :doc:`source_values` attributes common to most devices in the library.
These utility routines are in the ``tools`` module of GPIO Zero and are
typically imported as follows::

    from gpiozero.tools import scaled, negated, all_values

Given that :attr:`~gpiozero.SourceMixin.source` and
:attr:`~gpiozero.ValuesMixin.values` deal with infinite iterators, another
excellent source of utilities is the :mod:`itertools` module in the standard
library.

Single source conversions
=========================

.. autofunction:: absoluted

.. autofunction:: booleanized

.. autofunction:: clamped

.. autofunction:: inverted

.. autofunction:: negated

.. autofunction:: post_delayed

.. autofunction:: post_periodic_filtered

.. autofunction:: pre_delayed

.. autofunction:: pre_periodic_filtered

.. autofunction:: quantized

.. autofunction:: queued

.. autofunction:: smoothed

.. autofunction:: scaled

Combining sources
=================

.. autofunction:: all_values

.. autofunction:: any_values

.. autofunction:: averaged

.. autofunction:: multiplied

.. autofunction:: summed

.. autofunction:: zip_values

Artificial sources
==================

.. autofunction:: alternating_values

.. autofunction:: cos_values

.. autofunction:: ramping_values

.. autofunction:: random_values

.. autofunction:: sin_values
