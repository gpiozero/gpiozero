# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
)
str = type('')

import io

import pytest

from gpiozero.fonts import *


@pytest.fixture()
def font_text(request):
    return """\
# A comment

 .  0_  1.  2_  3_  4.  5_  6_  7_  8_  9_
... |.| ..| ._| ._| |_| |_. |_. ..| |_| |_|
... |_| ..| |_. ._| ..| ._| |_| ..| |_| ._|
"""


@pytest.fixture()
def font_data(request):
    return {
        ' ': (0, 0, 0, 0, 0, 0, 0),
        '0': (1, 1, 1, 1, 1, 1, 0),
        '1': (0, 1, 1, 0, 0, 0, 0),
        '2': (1, 1, 0, 1, 1, 0, 1),
        '3': (1, 1, 1, 1, 0, 0, 1),
        '4': (0, 1, 1, 0, 0, 1, 1),
        '5': (1, 0, 1, 1, 0, 1, 1),
        '6': (1, 0, 1, 1, 1, 1, 1),
        '7': (1, 1, 1, 0, 0, 0, 0),
        '8': (1, 1, 1, 1, 1, 1, 1),
        '9': (1, 1, 1, 1, 0, 1, 1),
    }


def test_fonts_load_types(tmpdir, font_text, font_data):
    text_stream = io.StringIO(font_text)
    bin_stream = io.BytesIO(font_text.encode('utf-8'))
    tmpfile = tmpdir.join('test.font')
    tmpfile.write_text(font_text, 'utf-8')

    assert load_font_7seg(text_stream) == font_data
    assert load_font_7seg(bin_stream) == font_data
    assert load_font_7seg(str(tmpfile)) == font_data
    assert load_font_7seg(str(tmpfile).encode('utf-8')) == font_data


def test_fonts_bad_data():
    data = """\
 .  0_  1.  2_  3_  4.  5_  6_  7_  8_  9_
... |.| ..| ._| ._| |_| |_. |_. ..| |_| |_|
"""
    with pytest.raises(ValueError):
        load_font_7seg(io.StringIO(data))

    data = """\
 .  0_  1  2_  3_  4.  5_  6_  7_  8_  9_
... |.| .| ._| ._| |_| |_. |_. ..| |_| |_|
... |_| .| |_. ._| ..| ._| |_| ..| |_| ._|
"""
    with pytest.raises(ValueError):
        load_font_7seg(io.StringIO(data))

    data = """\
 .... 0---  2---  2---  3---  4     5---  6---  7---. 8---  9---
..... |  /|     |     |     | |   | |     |        /  |   | |   |
..... | / |  ---   ---    --   ---|  ---  |---    |    ---   ---|
..... |/  | |     |         |     |     | |   |   |   |   |     |
.....  ---   ---   ---   ---         ---   ---         ---
"""
    with pytest.raises(ValueError):
        load_font_14seg(io.StringIO(data))
