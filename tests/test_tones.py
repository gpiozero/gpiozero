# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2019-2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
)
str = type('')

import warnings
from fractions import Fraction

import pytest

from gpiozero.exc import AmbiguousTone
from gpiozero.tones import Tone


@pytest.fixture
def A4(request):
    return Tone.from_frequency(440.0)

def test_tone_init(A4):
    with warnings.catch_warnings(record=True) as w:
        warnings.resetwarnings()
        assert Tone(440) == A4
        assert Tone("A4") == A4
        assert Tone(Fraction(880, 2)) == A4
        assert len(w) == 0
        assert Tone(69) == A4
        assert len(w) == 1
        assert Tone(0) != A4
        assert len(w) == 1
        assert isinstance(w[0].message, AmbiguousTone)
    assert Tone(frequency=440) == A4
    assert Tone(note="A4") == A4
    assert Tone(midi=69) == A4
    with pytest.raises(TypeError):
        Tone()
    with pytest.raises(TypeError):
        Tone(foo=1)
    with pytest.raises(TypeError):
        Tone(frequency=440, midi=69)
    with pytest.raises(TypeError):
        Tone(440, midi=69)

def test_tone_str(A4):
    assert str(A4) == "A4"
    assert str(A4.up()) == "A#4"
    assert str(A4.down(12)) == "A3"
    assert repr(A4) == "<Tone note={note!r} midi=69 frequency=440.00Hz>".format(note='A4')
    assert repr(Tone(13000)) == '<Tone frequency=13000.00Hz>'

def test_tone_from_frequency(A4):
    assert Tone.from_frequency(440) == A4
    assert Tone.from_frequency(440.0) == A4
    with pytest.raises(ValueError):
        Tone.from_frequency(-100.0)
    with pytest.raises(ValueError):
        Tone.from_frequency(30000.0)

def test_tone_from_note(A4):
    assert Tone.from_note(b"A4") == A4
    assert Tone.from_note("A4") == A4
    with pytest.raises(ValueError):
        Tone.from_note("a4")
    with pytest.raises(ValueError):
        Tone.from_note("foo")
    with pytest.raises(ValueError):
        Tone.from_note(0)

def test_tone_from_midi(A4):
    assert Tone.from_midi(69) == A4
    with pytest.raises(ValueError):
        Tone.from_midi(500)
    with pytest.raises(ValueError):
        Tone.from_midi(-1)

def test_tone_frequency(A4):
    assert A4.frequency == 440.0
    assert A4.up(12).frequency == 880.0
    assert A4.down(12).frequency == 220.0

def test_tone_midi(A4):
    assert A4.midi == 69
    assert A4.up().midi == 70
    assert A4.down().midi == 68
    with pytest.raises(ValueError):
        Tone.from_frequency(2).midi
    with pytest.raises(ValueError):
        Tone.from_frequency(15000).midi

def test_tone_note(A4):
    assert A4.note == "A4"
    assert A4.up().note == "A#4"
    assert A4.down().note == "G#4"
    with pytest.raises(ValueError):
        Tone.from_midi(8).note
