# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2016-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from random import random
from time import sleep
from itertools import cycle
from math import sin, cos, pi, isclose
from statistics import mean

from .mixins import ValuesMixin


def _normalize(values):
    """
    If *values* is a ``ValuesMixin`` derivative, return ``values.values``,
    otherwise return `values` as provided. Intended to allow support for::

        led.source = foo(btn)

    and::

        led.source = foo(btn.values)

    and::

        led.source = foo(some_iterator)
    """
    if isinstance(values, ValuesMixin):
        return values.values
    return values


def negated(values):
    """
    Returns the negation of the supplied values (:data:`True` becomes
    :data:`False`, and :data:`False` becomes :data:`True`). For example::

        from gpiozero import Button, LED
        from gpiozero.tools import negated
        from signal import pause

        led = LED(4)
        btn = Button(17)

        led.source = negated(btn)

        pause()
    """
    values = _normalize(values)
    for v in values:
        yield not v


def inverted(values, input_min=0, input_max=1):
    """
    Returns the inversion of the supplied values (*input_min* becomes
    *input_max*, *input_max* becomes *input_min*, `input_min + 0.1` becomes
    `input_max - 0.1`, etc.). All items in *values* are assumed to be between
    *input_min* and *input_max* (which default to 0 and 1 respectively), and
    the output will be in the same range. For example::

        from gpiozero import MCP3008, PWMLED
        from gpiozero.tools import inverted
        from signal import pause

        led = PWMLED(4)
        pot = MCP3008(channel=0)

        led.source = inverted(pot)

        pause()
    """
    values = _normalize(values)
    if input_min >= input_max:
        raise ValueError('input_min must be smaller than input_max')
    for v in values:
        yield input_min + input_max - v


def scaled(values, output_min, output_max, input_min=0, input_max=1):
    """
    Returns *values* scaled from *output_min* to *output_max*, assuming that
    all items in *values* lie between *input_min* and *input_max* (which
    default to 0 and 1 respectively). For example, to control the direction of
    a motor (which is represented as a value between -1 and 1) using a
    potentiometer (which typically provides values between 0 and 1)::

        from gpiozero import Motor, MCP3008
        from gpiozero.tools import scaled
        from signal import pause

        motor = Motor(20, 21)
        pot = MCP3008(channel=0)

        motor.source = scaled(pot, -1, 1)

        pause()

    .. warning::

        If *values* contains elements that lie outside *input_min* to
        *input_max* (inclusive) then the function will not produce values that
        lie within *output_min* to *output_max* (inclusive).
    """
    values = _normalize(values)
    if input_min >= input_max:
        raise ValueError('input_min must be smaller than input_max')
    input_size = input_max - input_min
    output_size = output_max - output_min
    for v in values:
        yield (((v - input_min) / input_size) * output_size) + output_min


def scaled_full(values):
    """
    A convenience function that builds on :func:`scaled`. It converts a
    "half-range" value (0..1) to a "full-range" value (-1..1). This is
    equivalent to calling::

        scaled(values, -1, 1, 0, 1)
    """
    return scaled(values, -1, 1, 0, 1)


def scaled_half(values):
    """
    A convenience function that builds on :func:`scaled`. It converts a
    "full-range" value (-1..1) to a "half-range" value (0..1). This is
    equivalent to calling::

        scaled(values, 0, 1, -1, 1)
    """
    return scaled(values, 0, 1, -1, 1)


def clamped(values, output_min=0, output_max=1):
    """
    Returns *values* clamped from *output_min* to *output_max*, i.e. any items
    less than *output_min* will be returned as *output_min* and any items
    larger than *output_max* will be returned as *output_max* (these default to
    0 and 1 respectively). For example::

        from gpiozero import PWMLED, MCP3008
        from gpiozero.tools import clamped
        from signal import pause

        led = PWMLED(4)
        pot = MCP3008(channel=0)

        led.source = clamped(pot, 0.5, 1.0)

        pause()
    """
    values = _normalize(values)
    if output_min >= output_max:
        raise ValueError('output_min must be smaller than output_max')
    for v in values:
        yield min(max(v, output_min), output_max)


def absoluted(values):
    """
    Returns *values* with all negative elements negated (so that they're
    positive). For example::

        from gpiozero import PWMLED, Motor, MCP3008
        from gpiozero.tools import absoluted, scaled
        from signal import pause

        led = PWMLED(4)
        motor = Motor(22, 27)
        pot = MCP3008(channel=0)

        motor.source = scaled(pot, -1, 1)
        led.source = absoluted(motor)

        pause()
    """
    values = _normalize(values)
    for v in values:
        yield abs(v)


def quantized(values, steps, input_min=0, input_max=1):
    """
    Returns *values* quantized to *steps* increments. All items in *values* are
    assumed to be between *input_min* and *input_max* (which default to 0 and
    1 respectively), and the output will be in the same range.

    For example, to quantize values between 0 and 1 to 5 "steps" (0.0, 0.25,
    0.5, 0.75, 1.0)::

        from gpiozero import PWMLED, MCP3008
        from gpiozero.tools import quantized
        from signal import pause

        led = PWMLED(4)
        pot = MCP3008(channel=0)

        led.source = quantized(pot, 4)

        pause()
    """
    values = _normalize(values)
    if steps < 1:
        raise ValueError("steps must be 1 or larger")
    if input_min >= input_max:
        raise ValueError('input_min must be smaller than input_max')
    input_size = input_max - input_min
    for v in scaled(values, 0, 1, input_min, input_max):
        yield ((int(v * steps) / steps) * input_size) + input_min


def booleanized(values, min_value, max_value, hysteresis=0):
    """
    Returns True for each item in *values* between *min_value* and
    *max_value*, and False otherwise. *hysteresis* can optionally be used to
    add `hysteresis`_ which prevents the output value rapidly flipping when
    the input value is fluctuating near the *min_value* or *max_value*
    thresholds. For example, to light an LED only when a potentiometer is
    between ¼ and ¾ of its full range::

        from gpiozero import LED, MCP3008
        from gpiozero.tools import booleanized
        from signal import pause

        led = LED(4)
        pot = MCP3008(channel=0)

        led.source = booleanized(pot, 0.25, 0.75)

        pause()

    .. _hysteresis: https://en.wikipedia.org/wiki/Hysteresis
    """
    values = _normalize(values)
    if min_value >= max_value:
        raise ValueError('min_value must be smaller than max_value')
    min_value = float(min_value)
    max_value = float(max_value)
    if hysteresis < 0:
        raise ValueError("hysteresis must be 0 or larger")
    else:
        hysteresis = float(hysteresis)
    if (max_value - min_value) <= hysteresis:
        raise ValueError('The gap between min_value and max_value must be '
                         'larger than hysteresis')
    last_state = None
    for v in values:
        if v < min_value:
            new_state = 'below'
        elif v > max_value:
            new_state = 'above'
        else:
            new_state = 'in'
        switch = False
        if last_state == None or not hysteresis:
            switch = True
        elif new_state == last_state:
            pass
        else: # new_state != last_state
            if last_state == 'below' and new_state == 'in':
                switch = v >= min_value + hysteresis
            elif last_state == 'in' and new_state == 'below':
                switch = v < min_value - hysteresis
            elif last_state == 'in' and new_state == 'above':
                switch = v > max_value + hysteresis
            elif last_state == 'above' and new_state == 'in':
                switch = v <= max_value - hysteresis
            else: # above->below or below->above
                switch = True
        if switch:
            last_state = new_state
        yield last_state == 'in'


def all_values(*values):
    """
    Returns the `logical conjunction`_ of all supplied values (the result is
    only :data:`True` if and only if all input values are simultaneously
    :data:`True`). One or more *values* can be specified. For example, to light
    an :class:`~gpiozero.LED` only when *both* buttons are pressed::

        from gpiozero import LED, Button
        from gpiozero.tools import all_values
        from signal import pause

        led = LED(4)
        btn1 = Button(20)
        btn2 = Button(21)

        led.source = all_values(btn1, btn2)

        pause()

    .. _logical conjunction: https://en.wikipedia.org/wiki/Logical_conjunction
    """
    values = [_normalize(v) for v in values]
    for v in zip(*values):
        yield all(v)


def any_values(*values):
    """
    Returns the `logical disjunction`_ of all supplied values (the result is
    :data:`True` if any of the input values are currently :data:`True`). One or
    more *values* can be specified. For example, to light an
    :class:`~gpiozero.LED` when *any* button is pressed::

        from gpiozero import LED, Button
        from gpiozero.tools import any_values
        from signal import pause

        led = LED(4)
        btn1 = Button(20)
        btn2 = Button(21)

        led.source = any_values(btn1, btn2)

        pause()

    .. _logical disjunction: https://en.wikipedia.org/wiki/Logical_disjunction
    """
    values = [_normalize(v) for v in values]
    for v in zip(*values):
        yield any(v)


def averaged(*values):
    """
    Returns the mean of all supplied values. One or more *values* can be
    specified. For example, to light a :class:`~gpiozero.PWMLED` as the average
    of several potentiometers connected to an :class:`~gpiozero.MCP3008` ADC::

        from gpiozero import MCP3008, PWMLED
        from gpiozero.tools import averaged
        from signal import pause

        pot1 = MCP3008(channel=0)
        pot2 = MCP3008(channel=1)
        pot3 = MCP3008(channel=2)
        led = PWMLED(4)

        led.source = averaged(pot1, pot2, pot3)

        pause()
    """
    values = [_normalize(v) for v in values]
    for v in zip(*values):
        yield mean(v)


def summed(*values):
    """
    Returns the sum of all supplied values. One or more *values* can be
    specified. For example, to light a :class:`~gpiozero.PWMLED` as the
    (scaled) sum of several potentiometers connected to an
    :class:`~gpiozero.MCP3008` ADC::

        from gpiozero import MCP3008, PWMLED
        from gpiozero.tools import summed, scaled
        from signal import pause

        pot1 = MCP3008(channel=0)
        pot2 = MCP3008(channel=1)
        pot3 = MCP3008(channel=2)
        led = PWMLED(4)

        led.source = scaled(summed(pot1, pot2, pot3), 0, 1, 0, 3)

        pause()
    """
    values = [_normalize(v) for v in values]
    for v in zip(*values):
        yield sum(v)


def multiplied(*values):
    """
    Returns the product of all supplied values. One or more *values* can be
    specified. For example, to light a :class:`~gpiozero.PWMLED` as the product
    (i.e. multiplication) of several potentiometers connected to an
    :class:`~gpiozero.MCP3008`
    ADC::

        from gpiozero import MCP3008, PWMLED
        from gpiozero.tools import multiplied
        from signal import pause

        pot1 = MCP3008(channel=0)
        pot2 = MCP3008(channel=1)
        pot3 = MCP3008(channel=2)
        led = PWMLED(4)

        led.source = multiplied(pot1, pot2, pot3)

        pause()
    """
    values = [_normalize(v) for v in values]
    def _product(it):
        p = 1
        for n in it:
            p *= n
        return p
    for v in zip(*values):
        yield _product(v)


def queued(values, qsize):
    """
    Queues up readings from *values* (the number of readings queued is
    determined by *qsize*) and begins yielding values only when the queue is
    full. For example, to "cascade" values along a sequence of LEDs::

        from gpiozero import LEDBoard, Button
        from gpiozero.tools import queued
        from signal import pause

        leds = LEDBoard(5, 6, 13, 19, 26)
        btn = Button(17)

        for i in range(4):
            leds[i].source = queued(leds[i + 1], 5)
            leds[i].source_delay = 0.01

        leds[4].source = btn

        pause()
    """
    values = [_normalize(v) for v in values]
    if qsize < 1:
        raise ValueError("qsize must be 1 or larger")
    q = []
    it = iter(values)
    try:
        for i in range(qsize):
            q.append(next(it))
        for i in cycle(range(qsize)):
            yield q[i]
            q[i] = next(it)
    except StopIteration:
        pass


def smoothed(values, qsize, average=mean):
    """
    Queues up readings from *values* (the number of readings queued is
    determined by *qsize*) and begins yielding the *average* of the last
    *qsize* values when the queue is full. The larger the *qsize*, the more the
    values are smoothed. For example, to smooth the analog values read from an
    ADC::

        from gpiozero import MCP3008
        from gpiozero.tools import smoothed

        adc = MCP3008(channel=0)

        for value in smoothed(adc, 5):
            print(value)
    """
    values = _normalize(values)
    if qsize < 1:
        raise ValueError("qsize must be 1 or larger")
    q = []
    it = iter(values)
    try:
        for i in range(qsize):
            q.append(next(it))
        for i in cycle(range(qsize)):
            yield average(q)
            q[i] = next(it)
    except StopIteration:
        pass


def pre_delayed(values, delay):
    """
    Waits for *delay* seconds before returning each item from *values*.
    """
    values = _normalize(values)
    if delay < 0:
        raise ValueError("delay must be 0 or larger")
    for v in values:
        sleep(delay)
        yield v


def post_delayed(values, delay):
    """
    Waits for *delay* seconds after returning each item from *values*.
    """
    values = _normalize(values)
    if delay < 0:
        raise ValueError("delay must be 0 or larger")
    for v in values:
        yield v
        sleep(delay)


def pre_periodic_filtered(values, block, repeat_after):
    """
    Blocks the first *block* items from *values*, repeating the block after
    every *repeat_after* items, if *repeat_after* is non-zero. For example, to
    discard the first 50 values read from an ADC::

        from gpiozero import MCP3008
        from gpiozero.tools import pre_periodic_filtered

        adc = MCP3008(channel=0)

        for value in pre_periodic_filtered(adc, 50, 0):
            print(value)

    Or to only display every even item read from an ADC::

        from gpiozero import MCP3008
        from gpiozero.tools import pre_periodic_filtered

        adc = MCP3008(channel=0)

        for value in pre_periodic_filtered(adc, 1, 1):
            print(value)
    """
    values = _normalize(values)
    if block < 1:
        raise ValueError("block must be 1 or larger")
    if repeat_after < 0:
        raise ValueError("repeat_after must be 0 or larger")
    it = iter(values)
    try:
        if repeat_after == 0:
            for _ in range(block):
                next(it)
            while True:
                yield next(it)
        else:
            while True:
                for _ in range(block):
                    next(it)
                for _ in range(repeat_after):
                    yield next(it)
    except StopIteration:
        pass


def post_periodic_filtered(values, repeat_after, block):
    """
    After every *repeat_after* items, blocks the next *block* items from
    *values*. Note that unlike :func:`pre_periodic_filtered`, *repeat_after*
    can't be 0. For example, to block every tenth item read from an ADC::

        from gpiozero import MCP3008
        from gpiozero.tools import post_periodic_filtered

        adc = MCP3008(channel=0)

        for value in post_periodic_filtered(adc, 9, 1):
            print(value)
    """
    values = _normalize(values)
    if repeat_after < 1:
        raise ValueError("repeat_after must be 1 or larger")
    if block < 1:
        raise ValueError("block must be 1 or larger")
    it = iter(values)
    try:
        while True:
            for _ in range(repeat_after):
                yield next(it)
            for _ in range(block):
                next(it)
    except StopIteration:
        pass


def random_values():
    """
    Provides an infinite source of random values between 0 and 1. For example,
    to produce a "flickering candle" effect with an LED::

        from gpiozero import PWMLED
        from gpiozero.tools import random_values
        from signal import pause

        led = PWMLED(4)

        led.source = random_values()

        pause()

    If you require a wider range than 0 to 1, see :func:`scaled`.
    """
    while True:
        yield random()


def sin_values(period=360):
    """
    Provides an infinite source of values representing a sine wave (from -1 to
    +1) which repeats every *period* values. For example, to produce a "siren"
    effect with a couple of LEDs that repeats once a second::

        from gpiozero import PWMLED
        from gpiozero.tools import sin_values, scaled_half, inverted
        from signal import pause

        red = PWMLED(2)
        blue = PWMLED(3)

        red.source_delay = 0.01
        blue.source_delay = red.source_delay
        red.source = scaled_half(sin_values(100))
        blue.source = inverted(red)

        pause()

    If you require a different range than -1 to +1, see :func:`scaled`.
    """
    angles = (2 * pi * i / period for i in range(period))
    for a in cycle(angles):
        yield sin(a)


def cos_values(period=360):
    """
    Provides an infinite source of values representing a cosine wave (from -1
    to +1) which repeats every *period* values. For example, to produce a
    "siren" effect with a couple of LEDs that repeats once a second::

        from gpiozero import PWMLED
        from gpiozero.tools import cos_values, scaled_half, inverted
        from signal import pause

        red = PWMLED(2)
        blue = PWMLED(3)

        red.source_delay = 0.01
        blue.source_delay = red.source_delay
        red.source = scaled_half(cos_values(100))
        blue.source = inverted(red)

        pause()

    If you require a different range than -1 to +1, see :func:`scaled`.
    """
    angles = (2 * pi * i / period for i in range(period))
    for a in cycle(angles):
        yield cos(a)


def alternating_values(initial_value=False):
    """
    Provides an infinite source of values alternating between :data:`True` and
    :data:`False`, starting wth *initial_value* (which defaults to
    :data:`False`). For example, to produce a flashing LED::

        from gpiozero import LED
        from gpiozero.tools import alternating_values
        from signal import pause

        red = LED(2)

        red.source_delay = 0.5
        red.source = alternating_values()

        pause()
    """
    value = initial_value
    while True:
        yield value
        value = not value


def ramping_values(period=360):
    """
    Provides an infinite source of values representing a triangle wave (from 0
    to 1 and back again) which repeats every *period* values. For example, to
    pulse an LED once a second::

        from gpiozero import PWMLED
        from gpiozero.tools import ramping_values
        from signal import pause

        red = PWMLED(2)

        red.source_delay = 0.01
        red.source = ramping_values(100)

        pause()

    If you require a wider range than 0 to 1, see :func:`scaled`.
    """
    step = 2 / period
    value = 0
    while True:
        yield value
        value += step
        if isclose(value, 1, abs_tol=1e-9):
            value = 1
            step *= -1
        elif isclose(value, 0, abs_tol=1e-9):
            value = 0
            step *= -1
        elif value > 1 or value < 0:
            step *= -1
            value += step


def zip_values(*devices):
    """
    Provides a source constructed from the values of each item, for example::

        from gpiozero import MCP3008, Robot
        from gpiozero.tools import zip_values
        from signal import pause

        robot = Robot(left=(4, 14), right=(17, 18))

        left = MCP3008(0)
        right = MCP3008(1)

        robot.source = zip_values(left, right)

        pause()

    ``zip_values(left, right)`` is equivalent to ``zip(left.values,
    right.values)``.
    """
    return zip(*[d.values for d in devices])
