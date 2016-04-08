============
Source Tools
============

.. currentmodule:: gpiozero.tools

GPIO Zero includes several utility routines which are intended to be used with
the :attr:`~gpiozero.SourceMixin.source` and
:attr:`~gpiozero.ValuesMixin.values` attributes common to most devices in the
library. These utility routines are in the ``tools`` module of GPIO Zero and
are typically imported as follows::

    from gpiozero.tools import scaled, negated, conjunction

Given that :attr:`~gpiozero.SourceMixin.source` and
:attr:`~gpiozero.ValuesMixin.values` deal with infinite iterators, another
excellent source of utilities is the :mod:`itertools` module in the standard
library.

Single source conversions
=========================

.. autofunction:: negated

.. autofunction:: inverted

.. autofunction:: scaled

.. autofunction:: clamped

.. autofunction:: post_delayed

.. autofunction:: pre_delayed

.. autofunction:: quantized

.. autofunction:: queued

Combining sources
=================

.. autofunction:: conjunction

.. autofunction:: disjunction

.. autofunction:: averaged

Artifical sources
=================

.. autofunction:: random_values

.. autofunction:: sin_values

.. autofunction:: cos_values

