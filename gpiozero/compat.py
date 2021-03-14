# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import math
import cmath
import weakref
import operator
import functools

# Handles pre 3.3 versions of Python without collections.abc
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

# Back-ported from python 3.5; see
# github.com/PythonCHB/close_pep/blob/master/is_close.py for original
# implementation
def isclose(a, b, rel_tol=1e-9, abs_tol=0.0):
    if rel_tol < 0.0 or abs_tol < 0.0:
        raise ValueError('error tolerances must be non-negative')
    if a == b: # fast-path for exact equality
        return True
    if cmath.isinf(a) or cmath.isinf(b):
        return False
    diff = abs(b - a)
    return (
        (diff <= abs(rel_tol * b)) or
        (diff <= abs(rel_tol * a)) or
        (diff <= abs_tol)
        )


# Backported from py3.4
def mean(data):
    if iter(data) is data:
        data = list(data)
    n = len(data)
    if not n:
        raise ValueError('cannot calculate mean of empty data')
    return sum(data) / n


# Backported from py3.4
def median(data):
    data = sorted(data)
    n = len(data)
    if not n:
        raise ValueError('cannot calculate median of empty data')
    elif n % 2:
        return data[n // 2]
    else:
        i = n // 2
        return (data[i - 1] + data[i]) / 2


# Backported from py3.4
def mean(data):
    if iter(data) is data:
        data = list(data)
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data) / n


# Backported from py3.3
def log2(x):
    return math.log(x, 2)


# Copied from the MIT-licensed https://github.com/slezica/python-frozendict
class frozendict(Mapping):
    def __init__(self, *args, **kwargs):
        self.__dict = dict(*args, **kwargs)
        self.__hash = None

    def __getitem__(self, key):
        return self.__dict[key]

    def copy(self, **add_or_replace):
        return frozendict(self, **add_or_replace)

    def __iter__(self):
        return iter(self.__dict)

    def __len__(self):
        return len(self.__dict)

    def __repr__(self):
        return '<frozendict %s>' % repr(self.__dict)

    def __hash__(self):
        if self.__hash is None:
            hashes = map(hash, self.items())
            self.__hash = functools.reduce(operator.xor, hashes, 0)
        return self.__hash


# Backported from py3.4
class WeakMethod(weakref.ref):
    """
    A custom `weakref.ref` subclass which simulates a weak reference to
    a bound method, working around the lifetime problem of bound methods.
    """

    __slots__ = "_func_ref", "_meth_type", "_alive", "__weakref__"

    def __new__(cls, meth, callback=None):
        try:
            obj = meth.__self__
            func = meth.__func__
        except AttributeError:
            raise TypeError("argument should be a bound method, not {0}"
                            .format(type(meth)))
        def _cb(arg):
            # The self-weakref trick is needed to avoid creating a reference
            # cycle.
            self = self_wr()
            if self._alive:
                self._alive = False
                if callback is not None:
                    callback(self)
        self = weakref.ref.__new__(cls, obj, _cb)
        self._func_ref = weakref.ref(func, _cb)
        self._meth_type = type(meth)
        self._alive = True
        self_wr = weakref.ref(self)
        return self

    def __call__(self):
        obj = super(WeakMethod, self).__call__()
        func = self._func_ref()
        if obj is None or func is None:
            return None
        return self._meth_type(func, obj)

    def __eq__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is other
            return weakref.ref.__eq__(self, other) and self._func_ref == other._func_ref
        return False

    def __ne__(self, other):
        if isinstance(other, WeakMethod):
            if not self._alive or not other._alive:
                return self is not other
            return weakref.ref.__ne__(self, other) or self._func_ref != other._func_ref
        return True

    __hash__ = weakref.ref.__hash__
