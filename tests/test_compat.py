# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import gc
import sys
import pytest
import random
import weakref

from gpiozero.compat import *


def test_frozendict():
    d = {1: 'a', 2: 'b'}
    e = {1: 'a', 2: 'b', 'foo': 'bar'}
    f = frozendict(d)
    assert f[1] == 'a'
    assert f[2] == 'b'
    with pytest.raises(KeyError):
        f[3]
    with pytest.raises(TypeError):
        f[3] = 'c'
    assert d == f
    assert d == f.copy()
    assert e == f.copy(foo='bar')
    assert len(f) == 2
    assert {k: v for k, v in f.items()} == d
    h = hash(f)
    assert h is not None
    assert hash(f) == h

# ported from the official test cases; see
# https://github.com/python/cpython/blob/master/Lib/test/test_math.py for original

NAN = float('nan')
INF = float('inf')
NINF = float('-inf')

def test_isclose_negative_tolerances():
    with pytest.raises(ValueError):
        isclose(1, 1, rel_tol=-1e-100)
    with pytest.raises(ValueError):
        isclose(1, 1, rel_tol=1e-100, abs_tol=-1e10)

def test_isclose_identical():
    examples = [
        (2.0, 2.0),
        (0.1e200, 0.1e200),
        (1.123e-300, 1.123e-300),
        (12345, 12345.0),
        (0.0, -0.0),
        (345678, 345678),
        ]
    for a, b in examples:
        assert isclose(a, b, rel_tol=0.0, abs_tol=0.0)

def test_isclose_eight_decimals():
    examples = [
        (1e8, 1e8 + 1),
        (-1e-8, -1.000000009e-8),
        (1.12345678, 1.12345679),
        ]
    for a, b in examples:
        assert isclose(a, b, rel_tol=1e-8)
        assert not isclose(a, b, rel_tol=1e-9)

def test_isclose_near_zero():
    examples = [1e-9, -1e-9, -1e-150]
    for a in examples:
        assert not isclose(a, 0.0, rel_tol=0.9)
        assert isclose(a, 0.0, abs_tol=1e-8)

def test_isclose_inf():
    assert isclose(INF, INF)
    assert isclose(INF, INF, abs_tol=0.0)
    assert isclose(NINF, NINF)
    assert isclose(NINF, NINF, abs_tol=0.0)

def test_isclose_inf_ninf_nan():
    examples = [
        (NAN, NAN),
        (NAN, 1e-100),
        (1e-100, NAN),
        (INF, NAN),
        (NAN, INF),
        (INF, NINF),
        (INF, 1.0),
        (1.0, INF),
        (INF, 1e308),
        (1e308, INF),
        ]
    for a, b in examples:
        assert not isclose(a, b, abs_tol=0.999999999999999)

def test_isclose_zero_tolerance():
    examples = [
        (1.0, 1.0),
        (-3.4, -3.4),
        (-1e-300, -1e-300),
        ]
    for a, b in examples:
        assert isclose(a, b, rel_tol=0.0)
    examples = [
        (1.0, 1.000000000000001),
        (0.99999999999999, 1.0),
        (1.0e200, .999999999999999e200),
        ]
    for a, b in examples:
        assert not isclose(a, b, rel_tol=0.0)

def test_isclose_assymetry():
    assert isclose(9, 10, rel_tol=0.1)
    assert isclose(10, 9, rel_tol=0.1)

def test_isclose_integers():
    examples = [
        (100000001, 100000000),
        (123456789, 123456788),
        ]
    for a, b in examples:
        assert isclose(a, b, rel_tol=1e-8)
        assert not isclose(a, b, rel_tol=1e-9)

# ported from the official test cases; see
# https://github.com/python/cpython/blob/master/Lib/test/test_statistics.py for
# original

def test_mean():
    examples = [
        (4.8125, (0, 1, 2, 3, 3, 3, 4, 5, 5, 6, 7, 7, 7, 7, 8, 9)),
        (22.015625, (17.25, 19.75, 20.0, 21.5, 21.75, 23.25, 25.125, 27.5)),
        (INF, (1, 3, 5, 7, 9, INF)),
        (NINF, (1, 3, 5, 7, 9, NINF)),
        ]
    for result, values in examples:
        values = list(values)
        random.shuffle(values)
        assert mean(values) == result
        assert mean(iter(values)) == result

def test_mean_big_data():
    c = 1e9
    data = [3.4, 4.5, 4.9, 6.7, 6.8, 7.2, 8.0, 8.1, 9.4]
    expected = mean(data) + c
    assert expected != c
    assert mean([x + c for x in data]) == expected

def test_mean_doubled_data():
    data = [random.uniform(-3, 5) for _ in range(1000)]
    expected = mean(data)
    actual = mean(data * 2)
    assert isclose(expected, actual)

def test_mean_empty():
    with pytest.raises(ValueError):
        mean(())

def test_median():
    assert median([1, 2, 3, 4, 5, 6]) == 3.5
    assert median([1, 2, 3, 4, 5, 6, 9]) == 4

def test_median_empty():
    with pytest.raises(ValueError):
        median(())

# ported from the official test cases; see
# https://github.com/python/cpython/blob/master/Lib/test/test_weakref.py for
# original

class Object(object):
    def __init__(self, arg):
        self.arg = arg
    def __repr__(self):
        return "<Object %r>" % self.arg
    def __eq__(self, other):
        if isinstance(other, Object):
            return self.arg == other.arg
        return NotImplemented
    def __ne__(self, other):
        if isinstance(other, Object):
            return self.arg != other.arg
        return NotImplemented
    def __lt__(self, other):
        if isinstance(other, Object):
            return self.arg < other.arg
        return NotImplemented
    def __hash__(self):
        return hash(self.arg)
    def some_method(self):
        return 4
    def other_method(self):
        return 5

@pytest.fixture()
def subclass(request):
    class C(Object):
        def some_method(self):
            return 6
    return C


def test_weakmethod_alive():
    o = Object(1)
    r = WeakMethod(o.some_method)
    assert isinstance(r, weakref.ReferenceType)
    assert isinstance(r(), type(o.some_method))
    assert r().__self__ is o
    assert r().__func__ is o.some_method.__func__
    assert r()() == 4

def test_weakmethod_object_dead():
    o = Object(1)
    r = WeakMethod(o.some_method)
    del o
    gc.collect()
    assert r() is None

@pytest.mark.xfail((3, 2) <= sys.version_info[:2] <= (3, 3),
                   reason='intermittent failure on py3.2 and py3.3')
def test_weakmethod_method_dead(subclass):
    o = subclass(1)
    r = WeakMethod(o.some_method)
    del subclass.some_method
    gc.collect()
    assert r() is None

def test_weakmethod_callback_when_object_dead(subclass):
    calls = []
    def cb(arg):
        calls.append(arg)
    o = subclass(1)
    r = WeakMethod(o.some_method, cb)
    del o
    gc.collect()
    assert calls == [r]
    # Callback is only called once
    subclass.some_method = Object.some_method
    gc.collect()
    assert calls == [r]

@pytest.mark.xfail((3, 2) <= sys.version_info[:2] <= (3, 3),
                   reason='intermittent failure on py3.2 and py3.3')
def test_weakmethod_callback_when_method_dead(subclass):
    calls = []
    def cb(arg):
        calls.append(arg)
    o = subclass(1)
    r = WeakMethod(o.some_method, cb)
    del subclass.some_method
    gc.collect()
    assert calls == [r]
    # Callback is only called once
    del o
    gc.collect()
    assert calls == [r]

@pytest.mark.xfail(hasattr(sys, 'pypy_version_info'),
                   reason='pypy memory management is different')
def test_weakmethod_no_cycles():
    o = Object(1)
    def cb(_):
        pass
    r = WeakMethod(o.some_method, cb)
    wr = weakref.ref(r)
    del r
    assert wr() is None

def test_weakmethod_equality():
    def _eq(a, b):
        assert a == b
        assert not (a != b)
    def _ne(a, b):
        assert not (a == b)
        assert a != b
    x = Object(1)
    y = Object(1)
    a = WeakMethod(x.some_method)
    b = WeakMethod(y.some_method)
    c = WeakMethod(x.other_method)
    d = WeakMethod(y.other_method)
    # Objects equal, same method
    _eq(a, b)
    _eq(c, d)
    # Objects equal, different method
    _ne(a, c)
    _ne(a, d)
    _ne(b, c)
    _ne(b, d)
    # Objects unequal, same or different method
    z = Object(2)
    e = WeakMethod(z.some_method)
    f = WeakMethod(z.other_method)
    _ne(a, e)
    _ne(a, f)
    _ne(b, e)
    _ne(b, f)
    del x, y, z
    gc.collect()
    # Dead WeakMethods compare by identity
    refs = a, b, c, d, e, f
    for q in refs:
        for r in refs:
            assert (q == r) == (q is r)
            assert (q != r) == (q is not r)

def test_weakmethod_hashing():
    x = Object(1)
    y = Object(1)
    a = WeakMethod(x.some_method)
    b = WeakMethod(y.some_method)
    c = WeakMethod(y.other_method)
    # Since WeakMethod objects are equal, the hashes should be equal
    assert hash(a) == hash(b)
    ha = hash(a)
    # Dead WeakMethods retain their old hash value
    del x, y
    gc.collect()
    assert hash(a) == ha
    assert hash(b) == ha
    # If it wasn't hashed when alive, a dead WeakMethod cannot be hashed
    with pytest.raises(TypeError):
        hash(c)

def test_weakmethod_bad_method():
    with pytest.raises(TypeError):
        WeakMethod('foo')

def test_weakmethod_other_equality():
    x = Object(1)
    a = WeakMethod(x.some_method)
    b = WeakMethod(x.other_method)
    assert not a == 1
    assert a != 1
