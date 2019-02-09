import pytest

from gpiozero.tones import Tone


@pytest.fixture
def A4(request):
    return Tone.from_frequency(440.0)

def test_tone_init(A4):
    assert Tone(440) == A4
    assert Tone("A4") == A4
    assert Tone(69) == A4

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
