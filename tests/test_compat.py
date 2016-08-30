from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest
import random

from gpiozero.compat import *


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

