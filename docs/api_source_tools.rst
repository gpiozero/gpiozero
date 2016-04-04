============
Source Tools
============

.. currentmodule:: gpiozero

GPIO Zero includes several utility routines which are intended to be used with
the :attr:`~SourceMixin.source` and :attr:`~ValuesMixin.values` attributes
common to most devices in the library. Given that ``source`` and ``values``
deal with infinite iterators, another excellent source of utilities is the
:mod:`itertools` module in the standard library.

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

