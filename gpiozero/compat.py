# vim: set fileencoding=utf-8:

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import cmath
import collections
import operator
import functools


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


# Copied from the MIT-licensed https://github.com/slezica/python-frozendict
class frozendict(collections.Mapping):
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
