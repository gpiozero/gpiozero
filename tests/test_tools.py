# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
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


import pytest
from math import sin, cos, radians
from time import time, sleep
from itertools import islice

from gpiozero import Device, LED, Button, Robot
from gpiozero.tools import *
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose
try:
    from statistics import mean
except ImportError:
    from gpiozero.compat import mean
try:
    from statistics import median
except ImportError:
    from gpiozero.compat import median


epsilon = 0.01  # time to sleep after setting source before checking value

def test_set_source_by_value(mock_factory):
    with LED(2) as led, Button(3) as btn:
        led.source_delay = 0
        assert not led.value
        assert not btn.value
        led.source = btn.values
        sleep(epsilon)
        assert not led.value
        assert not btn.value
        btn.pin.drive_low()
        sleep(epsilon)
        assert led.value
        assert btn.value

def test_set_source_by_device(mock_factory):
    with LED(2) as led, Button(3) as btn:
        led.source_delay = 0
        assert not led.value
        assert not btn.value
        led.source = btn
        sleep(epsilon)
        assert not led.value
        assert not btn.value
        btn.pin.drive_low()
        sleep(epsilon)
        assert led.value
        assert btn.value

def test_negated(mock_factory):
    assert list(negated(())) == []
    assert list(negated((True, True, False, False))) == [False, False, True, True]

def test_negated_source_by_value(mock_factory):
    with LED(2) as led, Button(3) as btn:
        led.source_delay = 0
        assert not led.value
        assert not btn.value
        led.source = negated(btn.values)
        sleep(epsilon)
        assert led.value
        assert not btn.value
        btn.pin.drive_low()
        sleep(epsilon)
        assert not led.value
        assert btn.value

def test_negated_source_by_device(mock_factory):
    with LED(2) as led, Button(3) as btn:
        led.source_delay = 0
        assert not led.value
        assert not btn.value
        led.source = negated(btn)
        sleep(epsilon)
        assert led.value
        assert not btn.value
        btn.pin.drive_low()
        sleep(epsilon)
        assert not led.value
        assert btn.value

def test_inverted():
    with pytest.raises(ValueError):
        list(inverted((), 0, 0))
    with pytest.raises(ValueError):
        list(inverted((), 1, 1))
    with pytest.raises(ValueError):
        list(inverted((), 1, 0))
    assert list(inverted(())) == []
    assert list(inverted((1, 0, 0.1, 0.5))) == [0, 1, 0.9, 0.5]
    assert list(inverted((1, 0, 0.1, 0.5), 0, 1)) == [0, 1, 0.9, 0.5]
    assert list(inverted((-1, 0, -0.1, -0.5), -1, 0)) == [0, -1, -0.9, -0.5]
    assert list(inverted((1, 0, 0.1, 0.5, -1, -0.1, -0.5), -1, 1)) == [-1, 0, -0.1, -0.5, 1, 0.1, 0.5]
    assert list(inverted((2, 1, 1.1, 1.5), 1, 2)) == [1, 2, 1.9, 1.5]

def test_scaled():
    with pytest.raises(ValueError):
        list(scaled((), 0, 1, 0, 0))
    with pytest.raises(ValueError):
        list(scaled((), 0, 1, 1, 1))
    with pytest.raises(ValueError):
        list(scaled((), 0, 1, 1, 0))
    assert list(scaled((), 0, 1)) == []
    # no scale
    assert list(scaled((0, 1, 0.5, 0.1), 0, 1)) == [0, 1, 0.5, 0.1]
    assert list(scaled((0, 1, 0.5, 0.1), 0, 1, 0, 1)) == [0, 1, 0.5, 0.1]
    # multiply by 2
    assert list(scaled((0, 1, 0.5, 0.1), 0, 2, 0, 1)) == [0, 2, 1, 0.2]
    # add 1
    assert list(scaled((0, 1, 0.5, 0.1), 1, 2, 0, 1)) == [1, 2, 1.5, 1.1]
    # multiply by 2 then add 1
    assert list(scaled((0, 1, 0.5, 0.1), 1, 3, 0, 1)) == [1, 3, 2, 1.2]
    # add 1 then multiply by 2
    assert list(scaled((0, 1, 0.5, 0.1), 2, 4, 0, 1)) == [2, 4, 3, 2.2]
    # invert
    assert list(scaled((0, 1, 0.5, 0.1), 1, 0, 0, 1)) == [1, 0, 0.5, 0.9]
    # multiply by -1 then subtract 1
    assert list(scaled((0, 1, 0.5, 0.1), -1, -2, 0, 1)) == [-1, -2, -1.5, -1.1]
    # scale 0->1 to -1->+1
    assert list(scaled((0, 1, 0.5, 0.1), -1, 1)) == [-1, 1, 0.0, -0.8]
    assert list(scaled((0, 1, 0.5, 0.1), -1, 1, 0, 1)) == [-1, 1, 0.0, -0.8]
    # scale -1->+1 to 0->1
    assert list(scaled((-1, 1, 0.0, -0.5), 0, 1, -1, 1)) == [0, 1, 0.5, 0.25]

def test_clamped():
    with pytest.raises(ValueError):
        list(clamped((), 0, 0))
    with pytest.raises(ValueError):
        list(clamped((), 1, 1))
    with pytest.raises(ValueError):
        list(clamped((), 1, 0))
    assert list(clamped(())) == []
    assert list(clamped((-2, -1, -0.5, 0, 0.5, 1, 2))) == [0, 0, 0, 0, 0.5, 1, 1]
    assert list(clamped((-2, -1, -0.5, 0, 0.5, 1, 2), 0, 1)) == [0, 0, 0, 0, 0.5, 1, 1]
    assert list(clamped((-2, -1, -0.5, 0, 0.5, 1, 2), -1, 1)) == [-1, -1, -0.5, 0, 0.5, 1, 1]
    assert list(clamped((-2, -1, -0.5, 0, 0.5, 1, 2), -2, 2)) == [-2, -1, -0.5, 0, 0.5, 1, 2]

def test_absoluted(mock_factory):
    assert list(absoluted(())) == []
    assert list(absoluted((-2, -1, 0, 1, 2))) == [2, 1, 0, 1, 2]

def test_quantized():
    with pytest.raises(ValueError):
        list(quantized((), 0))
    with pytest.raises(ValueError):
        list(quantized((), 4, 0, 0))
    with pytest.raises(ValueError):
        list(quantized((), 4, 1, 1))
    with pytest.raises(ValueError):
        list(quantized((), 4, 1, 0))
    assert list(quantized((), 4)) == []
    assert list(quantized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 4)) == [
            0.0, 0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 1.0]
    assert list(quantized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 4, 0, 1)) == [
            0.0, 0.0, 0.0, 0.25, 0.25, 0.5, 0.5, 0.5, 0.75, 0.75, 1.0]
    assert list(quantized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 5)) == [
            0.0, 0.0, 0.2, 0.2, 0.4, 0.4, 0.6, 0.6, 0.8, 0.8, 1.0]
    assert list(quantized((0, 0.25, 0.5, 0.75, 1.0, 1.5, 1.75, 2.0), 2, 0, 2)) == [
            0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0]
    assert list(quantized((1, 1.25, 1.5, 1.75, 2.0, 2.5, 2.75, 3.0), 2, 1, 3)) == [
            1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0]

def test_booleanized():
    with pytest.raises(ValueError):
        list(booleanized((), 0, 0))
    with pytest.raises(ValueError):
        list(booleanized((), 1, 1))
    with pytest.raises(ValueError):
        list(booleanized((), 1, 0))
    with pytest.raises(ValueError):
        list(booleanized((), 0, 0.5, -0.2))
    with pytest.raises(ValueError):
        list(booleanized((), 0, 0.5, 0.5))
    assert list(booleanized((), 0, 0.5)) == []
    assert list(booleanized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 0, 0.5)) == [
            True, True, True, True, True, True, False, False, False, False, False]
    assert list(booleanized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0), 0.25, 0.75)) == [
            False, False, False, True, True, True, True, True, False, False, False, False]
    assert list(booleanized((0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 0), 0.25, 0.75, 0.2)) == [
            False, False, False, False, False, True, True, True, True, True, False, False]
    assert list(booleanized((1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 1), 0.25, 0.75)) == [
            False, False, False, True, True, True, True, True, False, False, False, False]
    assert list(booleanized((1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 1), 0.25, 0.75, 0.2)) == [
            False, False, False, False, False, True, True, True, True, True, False, False]

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
    assert list(averaged((0, 0.5, 1))) == [0, 0.5, 1]
    assert list(averaged((0, 0.5, 1), (1, 1, 1))) == [0.5, 0.75, 1]

def test_summed():
    assert list(summed(())) == []
    assert list(summed((0, 0.5, 0.5, 1))) == [0, 0.5, 0.5, 1]
    assert list(summed((0, 0.5, 0.5, 1), (1, 0.5, 1, 1))) == [1, 1, 1.5, 2]

def test_multiplied():
    assert list(multiplied(())) == []
    assert list(multiplied((0, 0.5, 0.5, 1))) == [0, 0.5, 0.5, 1]
    assert list(multiplied((0, 0.5, 0.5, 1), (1, 0.5, 1, 1))) == [0, 0.25, 0.5, 1]

def test_queued():
    with pytest.raises(ValueError):
        list(queued((), 0))
    assert list(queued((), 5)) == []
    assert list(queued((1, 2, 3, 4, 5), 5)) == [1]
    assert list(queued((1, 2, 3, 4, 5, 6), 5)) == [1, 2]

def test_smoothed():
    with pytest.raises(ValueError):
        list(smoothed((), 0))
    assert list(smoothed((), 5)) == []
    assert list(smoothed((1, 2, 3, 4, 5), 5)) == [3.0]
    assert list(smoothed((1, 2, 3, 4, 5, 6), 5)) == [3.0, 4.0]
    assert list(smoothed((1, 2, 3, 4, 5, 6), 5, average=mean)) == [3.0, 4.0]
    assert list(smoothed((1, 1, 1, 4, 5, 5), 5, average=mean)) == [2.4, 3.2]
    assert list(smoothed((1, 1, 1, 4, 5, 5), 5, average=median)) == [1, 4]

def test_pre_delayed():
    with pytest.raises(ValueError):
        list(pre_delayed((), -1))
    assert list(pre_delayed((), 0.01)) == []
    count = 0
    start = time()
    for v in pre_delayed((0, 0, 0), 0.01):
        count += 1
        assert v == 0
        assert time() - start >= 0.01
        start = time()
    assert count == 3

def test_post_delayed():
    with pytest.raises(ValueError):
        list(post_delayed((), -1))
    assert list(post_delayed((), 0.01)) == []
    count = 0
    start = time()
    for v in post_delayed((1, 2, 2), 0.01):
        count += 1
        if v == 1:
            assert time() - start < 0.01
        else:
            assert v == 2
            assert time() - start >= 0.01
        start = time()
    assert time() - start >= 0.01
    assert count == 3

def test_pre_periodic_filtered():
    with pytest.raises(ValueError):
        list(pre_periodic_filtered((), 2, -1))
    with pytest.raises(ValueError):
        list(pre_periodic_filtered((), 0, 0))
    assert list(pre_periodic_filtered((), 2, 0)) == []
    assert list(pre_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2, 0)) == [3, 4, 5, 6, 7, 8, 9, 10]
    assert list(pre_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 1, 1)) == [2, 4, 6, 8, 10]
    assert list(pre_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 1, 2)) == [2, 3, 5, 6, 8, 9]
    assert list(pre_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2, 1)) == [3, 6, 9]

def test_post_periodic_filtered():
    with pytest.raises(ValueError):
        list(post_periodic_filtered((), 1, 0))
    with pytest.raises(ValueError):
        list(post_periodic_filtered((), 0, 1))
    assert list(pre_periodic_filtered((), 1, 1)) == []
    assert list(post_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 1, 1)) == [1, 3, 5, 7, 9]
    assert list(post_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 1, 2)) == [1, 4, 7, 10]
    assert list(post_periodic_filtered((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2, 1)) == [1, 2, 4, 5, 7, 8, 10]

def test_alternating_values():
    assert list(islice(alternating_values(), 5)) == [False, True, False, True, False]
    assert list(islice(alternating_values(True), 5)) == [True, False, True, False, True]

def test_random_values():
    for _, v in zip(range(1000), random_values()):
        assert 0 <= v <= 1

def test_sin_values():
    for e, v in zip([0, 0], sin_values(2)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    for e, v in zip([0, 1, 0, -1], sin_values(4)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    for e, v in zip([0, 2**0.5/2, 1, 2**0.5/2, 0, -2**0.5/2, -1, -2**0.5/2], sin_values(8)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    firstval = None
    for i, v in zip(range(1000), sin_values()):
        assert -1 <= v <= 1
        assert isclose(v, sin(radians(i)), abs_tol=1e-9)
        if i == 0:
            firstval = v
        else:
            if i % 360 == 0:
                assert v == firstval
    for period in (360, 100):
        firstval = None
        for i, v in zip(range(1000), sin_values(period)):
            assert -1 <= v <= 1
            if i == 0:
                firstval = v
            else:
                if i % period == 0:
                    assert v == firstval

def test_cos_values():
    for e, v in zip([1, -1], cos_values(2)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    for e, v in zip([1, 0, -1, 0], cos_values(4)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    for e, v in zip([1, 2**0.5/2, 0, -2**0.5/2, -1, -2**0.5/2, 0, 2**0.5/2], cos_values(8)):
        assert -1 <= v <= 1
        assert isclose(e, v, abs_tol=1e-9)
    firstval = None
    for i, v in zip(range(1000), cos_values()):
        assert -1 <= v <= 1
        assert isclose(v, cos(radians(i)), abs_tol=1e-9)
        if i == 0:
            firstval = v
        else:
            if i % 360 == 0:
                assert v == firstval
    for period in (360, 100):
        firstval = None
        for i, v in zip(range(1000), cos_values(period)):
            assert -1 <= v <= 1
            if i == 0:
                firstval = v
            else:
                if i % period == 0:
                    assert v == firstval

def test_ramping_values():
    assert list(islice(ramping_values(2), 2)) == [0, 1]
    assert list(islice(ramping_values(3), 5)) == [0, 2/3, 2/3, 0, 2/3]
    assert list(islice(ramping_values(4), 4)) == [0, 0.5, 1, 0.5]
    assert list(islice(ramping_values(8), 8)) == [0, 0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25]
    firstval = None
    for i, v in zip(range(1000), ramping_values()):
        assert 0 <= v <= 1
        if i == 0:
            firstval = v
        else:
            if i % 360 == 0:
                v == firstval
    for period in (360, 100):
        firstval = None
        for i, v in zip(range(1000), ramping_values(period)):
            assert 0 <= v <= 1
            if i == 0:
                firstval = v
            else:
                if i % period == 0:
                    assert v == firstval

def test_zip_values(mock_factory):
    with Button(2) as btn1, Button(3) as btn2:
        zv = zip_values(btn1, btn2)
        assert next(zv) == (False, False)
        btn1.pin.drive_low()
        assert next(zv) == (True, False)
        btn2.pin.drive_low()
        assert next(zv) == (True, True)
        btn1.pin.drive_high()
        assert next(zv) == (False, True)
        btn2.pin.drive_high()
        assert next(zv) == (False, False)
    with Button(2) as btn1, Button(3) as btn2, Button(4) as btn3, Button(5) as btn4:
        zv = zip_values(btn1, btn2, btn3, btn4)
        assert next(zv) == (False, False, False, False)
        btn1.pin.drive_low()
        btn3.pin.drive_low()
        assert next(zv) == (True, False, True, False)
        btn2.pin.drive_low()
        btn4.pin.drive_low()
        assert next(zv) == (True, True, True, True)
        btn1.pin.drive_high()
        btn2.pin.drive_high()
        btn3.pin.drive_high()
        btn4.pin.drive_high()
        sleep(epsilon)
        assert next(zv) == (False, False, False, False)
