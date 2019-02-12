# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2019 Dave Jones <dave@waveform.org.uk>
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

import warnings

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
        assert len(w) == 0
        assert Tone(69) == A4
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

def test_tone_str(A4):
    assert str(A4) == "A4"
    assert str(A4.up()) == "A#4"
    assert str(A4.down(12)) == "A3"

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
