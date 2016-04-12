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

.. warning::

    While the devices API is now considered stable and won't change in
    backwards incompatible ways, the tools API is *not* yet considered stable.
    It is potentially subject to change in future versions. We welcome any
    comments from testers!

Single source conversions
=========================

.. autofunction:: absoluted

.. autofunction:: clamped

.. autofunction:: inverted

.. autofunction:: negated

.. autofunction:: post_delayed

.. autofunction:: pre_delayed

.. autofunction:: quantized

.. autofunction:: queued

.. autofunction:: scaled

Combining sources
=================

.. autofunction:: all_values

.. autofunction:: any_values

.. autofunction:: averaged

Artifical sources
=================

.. autofunction:: cos_values

.. autofunction:: random_values

.. autofunction:: sin_values

