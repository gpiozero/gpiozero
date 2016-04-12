from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest
from math import sin, cos, radians
from time import time

from gpiozero.tools import *
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose


def test_negated():
    assert list(negated(())) == []
    assert list(negated((True, True, False, False))) == [False, False, True, True]

def test_inverted():
    assert list(inverted(())) == []
    assert list(inverted((1, 0, 0.1, 0.5))) == [0, 1, 0.9, 0.5]

def test_scaled():
    assert list(scaled((0, 1, 0.5, 0.1), 0, 1)) == [0, 1, 0.5, 0.1]
    assert list(scaled((0, 1, 0.5, 0.1), -1, 1)) == [-1, 1, 0.0, -0.8]

def test_clamped():
    assert list(clamped((-1, 0, 1, 2))) == [0, 0, 1, 1]

def test_absoluted():
    assert list(absoluted((-2, -1, 0, 1, 2))) == [2, 1, 0, 1, 2]

def test_quantized():
    assert list(quantized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 4)) == [
            0.0, 0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 1.0]
    assert list(quantized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 5)) == [
            0.0, 0.0, 0.2, 0.2, 0.4, 0.4, 0.6, 0.6, 0.8, 0.8, 1.0]

def test_all_values():
    assert list(all_values(())) == []
    assert list(all_values((False, True))) == [False, True]
    assert list(all_values((0, 1, 0, 1), (0, 0, 0, 1))) == [0, 0, 0, 1]

def test_any_values():
    assert list(any_values(())) == []
    assert list(any_values((False, True))) == [False, True]
    assert list(any_values((0, 1, 0, 1), (0, 0, 0, 1))) == [0, 1, 0, 1]

def test_averaged():
    assert list(averaged(())) == []
    assert list(averaged((0, 0.5, 1), (1, 1, 1))) == [0.5, 0.75, 1]

def test_queued():
    assert list(queued((1, 2, 3, 4, 5), 5)) == [1]
    assert list(queued((1, 2, 3, 4, 5, 6), 5)) == [1, 2]

def test_pre_delayed():
    start = time()
    for v in pre_delayed((0, 0, 0), 0.01):
        assert v == 0
        assert time() - start >= 0.01
        start = time()

def test_post_delayed():
    start = time()
    for v in post_delayed((1, 2, 2), 0.01):
        if v == 1:
            assert time() - start < 0.01
        else:
            assert time() - start >= 0.01
        start = time()
    assert time() - start >= 0.01

def test_random_values():
    for i, v in zip(range(1000), random_values()):
        assert 0 <= v <= 1

def test_sin_values():
    for i, v in zip(range(1000), sin_values()):
        assert isclose(v, sin(radians(i)), abs_tol=1e-9)

def test_cos_values():
    for i, v in zip(range(1000), cos_values()):
        assert isclose(v, cos(radians(i)), abs_tol=1e-9)

