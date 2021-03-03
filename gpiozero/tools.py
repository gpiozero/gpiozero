# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Ben Nuttall <ben@bennuttall.com>
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
    print_function,
    absolute_import,
    division,
)
str = type('')


import io
from random import random
from time import sleep
from collections import Counter
from .mixins import ValuesMixin
try:
    from itertools import izip as zip, izip_longest as zip_longest
except ImportError:
    from itertools import zip_longest
from itertools import cycle
from math import sin, cos, pi
try:
    from statistics import mean
except ImportError:
    from .compat import mean
try:
    from math import isclose
except ImportError:
    from .compat import isclose


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


def load_segment_font(filename_or_obj, width, height, pins):
    """
    A generic function for parsing segment font definition files.

    If you're working with "standard" 7-segment or 14-segment displays you
    *don't* want this function; see :func:`load_font_7seg` or
    :func:`load_font_14seg` instead. However, if you are working with another
    style of segmented display and wish to construct a parser for a custom
    format, this is the function you want.

    The *filename_or_obj* parameter is simply the file-like object or filename
    to load. This is typically passed in from the calling function.

    The *width* and *height* parameters give the width and height in characters
    of each character definition. For example, these are 3 and 3 for 7-segment
    displays. Finally, *pins* is a list of tuples that defines the position of
    each pin definition in the character array, and the character that marks
    that position "active".

    For example, for 7-segment displays this function is called as follows::

        load_segment_font(filename_or_obj, width=3, height=3, pins=[
            (1, '_'), (5, '|'), (8, '|'), (7, '_'),
            (6, '|'), (3, '|'), (4, '_')])

    This dictates that each character will be defined by a 3x3 character grid
    which will be converted into a nine-character string like so:

    .. code-block:: text

        012
        345  ==>  '012345678'
        678

    Position 0 is always assumed to be the character being defined. The *pins*
    list then specifies: the first pin is the character at position 1 which
    will be "on" when that character is "_". The second pin is the character
    at position 5 which will be "on" when that character is "|", and so on.
    """
    assert 0 < len(pins) <= (width * height) - 1
    if isinstance(filename_or_obj, bytes):
        filename_or_obj = filename_or_obj.decode('utf-8')
    opened = isinstance(filename_or_obj, str)
    if opened:
        filename_or_obj = io.open(filename_or_obj, 'r')
    try:
        lines = filename_or_obj.read()
        if isinstance(lines, bytes):
            lines = lines.decode('utf-8')
        lines = lines.splitlines()
    finally:
        if opened:
            filename_or_obj.close()

    # Strip out comments and blank lines, but remember the original line
    # numbers of each row for error reporting purposes
    rows = [
        (index, line) for index, line in enumerate(lines, start=1)
        # Strip comments and blank (or whitespace) lines
        if line.strip() and not line.startswith('#')
    ]
    line_numbers = {
        row_index: line_index
        for row_index, (line_index, row) in enumerate(rows)
    }
    rows = [row for index, row in rows]
    if len(rows) % height:
        raise ValueError('number of definition lines is not divisible by '
                         '{height}'.format(height=height))

    # Strip out blank columns then transpose back to rows, and make sure
    # everything is the right "shape"
    for n in range(0, len(rows), height):
        cols = [
            col for col in zip_longest(*rows[n:n + height], fillvalue=' ')
            # Strip blank (or whitespace) columns
            if ''.join(col).strip()
        ]
        rows[n:n + height] = list(zip(*cols))
    for row_index, row in enumerate(rows):
        if len(row) % width:
            raise ValueError(
                'length of definitions starting on line {line} is not '
                'divisible by {width}'.format(
                    line=line_numbers[row_index], width=width))

    # Split rows up into character definitions. After this, chars will be a
    # list of strings each with width x height characters. The first character
    # in each string will be the character being defined
    chars = [
        ''.join(
            char
            for row in rows[y::height]
            for char in row
        )[x::width]
        for y in range(height)
        for x in range(width)
    ]
    chars = [''.join(char) for char in zip(*chars)]

    # Strip out blank entries (a consequence of zip_longest above) and check
    # there're no repeat definitions
    chars = [char for char in chars if char.strip()]
    counts = Counter(char[0] for char in chars)
    for char, count in counts.most_common():
        if count > 1:
            raise ValueError(
                'multiple definitions for {char!r}'.format(char=char))

    return {
        char[0]: tuple(int(char[pos] == on) for pos, on in pins)
        for char in chars
    }


def load_font_7seg(filename_or_obj):
    """
    Given a filename or a file-like object, parse it as an font definition for
    a 7-segment display, returning a :class:`dict` suitable for use with
    :class:`~gpiozero.LEDCharDisplay`.

    The file-format is a simple text-based format in which blank and #-prefixed
    lines are ignored. All other lines are assumed to be groups of character
    definitions which are cells of 3x3 characters laid out as follows:

    .. code-block:: text

        Ca
        fgb
        edc

    Where C is the character being defined, and a-g define the states of the
    LEDs for that position. a, d, and g are on if they are "_". b, c, e, and
    f are on if they are "|". Any other character in these positions is
    considered off. For example, you might define the following characters:

    .. code-block:: text

         .  0_  1.  2_  3_  4.  5_  6_  7_  8_  9_
        ... |.| ..| ._| ._| |_| |_. |_. ..| |_| |_|
        ... |_| ..| |_. ._| ..| ._| |_| ..| |_| ._|

    In the example above, empty locations are marked with "." but could equally
    well be left as spaces. However, the first item defines the space (" ")
    character and needs *some* non-space characters in its definition as the
    parser also strips empty columns (as typically occur between character
    definitions).
    """
    return load_segment_font(filename_or_obj, width=3, height=3, pins=[
        (1, '_'), (5, '|'), (8, '|'), (7, '_'),
        (6, '|'), (3, '|'), (4, '_')])


def load_font_14seg(filename_or_obj):
    """
    Given a filename or a file-like object, parse it as a font definition
    for a 14-segment display, returning a :class:`dict` suitable for use with
    :class:`~gpiozero.LEDCharDisplay`.

    The file-format is a simple text-based format in which blank and #-prefixed
    lines are ignored. All other lines are assumed to be groups of character
    definitions which are cells of 5x5 characters laid out as follows:

    .. code-block:: text

        X.a..
        fijkb
        .g.h.
        elmnc
        ..d..

    Where X is the character being defined, and a-n define the states of the
    LEDs for that position. a, d, g, and h are on if they are "-". b, c, e, f,
    j, and m are on if they are "|". i and n are on if they are "\\". Finally,
    k and l are on if they are "/". Any other character in these positions is
    considered off. For example, you might define the following characters:

    .. code-block:: text

         .... 0---  1..   2---  3---  4     5---  6---  7---. 8---  9---
        ..... |  /|    /|     |     | |   | |     |        /  |   | |   |
        ..... | / |     |  ---    --   ---|  ---  |---    |    ---   ---|
        ..... |/  |     | |         |     |     | |   |   |   |   |     |
        .....  ---         ---   ---         ---   ---         ---

    In the example above, several locations have extraneous characters. For
    example, the "/" in the center of the "0" definition, or the "-" in the
    middle of the "8". These locations are ignored, but filled in nonetheless
    to make the shape more obvious.

    These extraneous locations could equally well be left as spaces. However,
    the first item defines the space (" ") character and needs *some* non-space
    characters in its definition as the parser also strips empty columns (as
    typically occur between character definitions) and verifies that
    definitions are 5 columns wide and 5 rows high.

    This also explains why place-holder characters (".") have been inserted at
    the top of the definition of the "1" character. Otherwise the parser will
    strip these empty columns and decide the definition is invalid (as the
    result is only 3 columns wide).
    """
    return load_segment_font(filename_or_obj, width=5, height=5, pins=[
        (2, '-'),  (9, '|'),  (19, '|'), (22, '-'),
        (15, '|'), (5, '|'),  (11, '-'), (13, '-'),
        (6, '\\'), (7, '|'),  (8, '/'),  (16, '/'),
        (17, '|'), (18, '\\')])
