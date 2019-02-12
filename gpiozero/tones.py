# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
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

import re
import warnings
from collections import namedtuple
try:
    from math import log2
except ImportError:
    from .compat import log2

from .exc import AmbiguousTone


class Tone(float):
    """
    Represents a frequency of sound in a variety of musical notations.

    :class:`Tone` class can be used with the :class:`~gpiozero.TonalBuzzer`
    class to easily represent musical tones. The class can be constructed in a
    variety of ways. For example as a straight frequency in `Hz`_ (which is the
    internal storage format), as an integer MIDI note, or as a string
    representation of a musical note.

    All the following constructors are equivalent ways to construct the typical
    tuning note, `concert A`_ at 440Hz, which is MIDI note #69:

        >>> from gpiozero.tones import Tone
        >>> Tone(440.0)
        >>> Tone(69)
        >>> Tone('A4')

    If you do not want the constructor to guess which format you are using
    (there is some ambiguity between frequencies and MIDI notes at the bottom
    end of the frequencies, from 128Hz down), you can use one of the explicit
    constructors, :meth:`from_frequency`, :meth:`from_midi`, or
    :meth:`from_note`, or you can specify a keyword argument when
    constructing::

        >>> Tone.from_frequency(440)
        >>> Tone.from_midi(69)
        >>> Tone.from_note('A4')
        >>> Tone(frequency=440)
        >>> Tone(midi=69)
        >>> Tone(note='A4')

    Several attributes are provided to permit conversion to any of the
    supported construction formats: :attr:`frequency`, :attr:`midi`, and
    :attr:`note`. Methods are provided to step :meth:`up` or :meth:`down` to
    adjacent MIDI notes.

    .. warning::

        Currently :class:`Tone` derives from :class:`float` and can be used as
        a floating point number in most circumstances (addition, subtraction,
        etc). This part of the API is not yet considered "stable"; i.e. we may
        decide to enhance / change this behaviour in future versions.

    .. _Hz: https://en.wikipedia.org/wiki/Hertz
    .. _concert A: https://en.wikipedia.org/wiki/Concert_pitch
    """

    tones = 'CCDDEFFGGAAB'
    semitones = {
        '♭': -1,
        'b': -1,
        '♮': 0,
        '':  0,
        '♯': 1,
        '#': 1,
    }
    regex = re.compile(
        r'(?P<note>[A-G])'
        r'(?P<semi>[%s]?)'
        r'(?P<octave>[0-9])' % ''.join(semitones.keys()))

    def __new__(cls, value=None, **kwargs):
        if value is None:
            if len(kwargs) != 1:
                raise TypeError('expected precisely one keyword argument')
            key, value = kwargs.popitem()
            try:
                return {
                    'frequency': cls.from_frequency,
                    'midi': cls.from_midi,
                    'note': cls.from_note,
                }[key](value)
            except KeyError:
                raise TypeError('unexpected keyword argument %r' % key)
        else:
            if kwargs:
                raise TypeError('cannot specify keywords with a value')
            if isinstance(value, (int, float)):
                if 0 <= value < 128:
                    if value > 0:
                        warnings.warn(
                            AmbiguousTone(
                                "Ambiguous tone specification; assuming you "
                                "want a MIDI note. To suppress this warning "
                                "use, e.g. Tone(midi=60), or to obtain a "
                                "frequency instead use, e.g. Tone(frequency="
                                "60)"))
                    return cls.from_midi(value)
                else:
                    return cls.from_frequency(value)
            elif isinstance(value, (bytes, str)):
                return cls.from_note(value)
            else:
                return cls.from_frequency(value)

    def __str__(self):
        return self.note

    def __repr__(self):
        try:
            midi = self.midi
        except ValueError:
            midi = ''
        else:
            midi = ' midi=%r' % midi
        try:
            note = self.note
        except ValueError:
            note = ''
        else:
            note = ' note=%r' % note
        return "<Tone%s%s frequency=%.2fHz>" % (note, midi, self.frequency)

    @classmethod
    def from_midi(cls, midi_note):
        """
        Construct a :class:`Tone` from a MIDI note, which must be an integer
        in the range 0 to 127. For reference, A4 (`concert A`_ typically used
        for tuning) is MIDI note #69.

        .. _concert A: https://en.wikipedia.org/wiki/Concert_pitch
        """
        midi = int(midi_note)
        if 0 <= midi_note < 128:
            A4_midi = 69
            A4_freq = 440
            return cls.from_frequency(A4_freq * 2 ** ((midi - A4_midi) / 12))
        raise ValueError('invalid MIDI note: %r' % midi)

    @classmethod
    def from_note(cls, note):
        """
        Construct a :class:`Tone` from a musical note which must consist of
        a capital letter A through G, followed by an optional semi-tone
        modifier ("b" for flat, "#" for sharp, or their Unicode equivalents),
        followed by an octave number (0 through 9).

        For example `concert A`_, the typical tuning note at 440Hz, would be
        represented as "A4". One semi-tone above this would be "A#4" or
        alternatively "Bb4". Unicode representations of sharp and flat are also
        accepted.
        """
        if isinstance(note, bytes):
            note = note.decode('ascii')
        if isinstance(note, str):
            match = Tone.regex.match(note)
            if match:
                octave = int(match.group('octave')) + 1
                return cls.from_midi(
                    Tone.tones.index(match.group('note')) +
                    Tone.semitones[match.group('semi')] +
                    octave * 12)
        raise ValueError('invalid note specification: %r' % note)

    @classmethod
    def from_frequency(cls, freq):
        """
        Construct a :class:`Tone` from a frequency specified in `Hz`_ which
        must be a positive floating-point value in the range 0 < freq <= 20000.

        .. _Hz: https://en.wikipedia.org/wiki/Hertz
        """
        if 0 < freq <= 20000:
            return super(Tone, cls).__new__(cls, freq)
        raise ValueError('invalid frequency: %.2f' % freq)

    @property
    def frequency(self):
        """
        Return the frequency of the tone in `Hz`_.

        .. _Hz: https://en.wikipedia.org/wiki/Hertz
        """
        return float(self)

    @property
    def midi(self):
        """
        Return the (nearest) MIDI note to the tone's frequency. This will be an
        integer number in the range 0 to 127. If the frequency is outside the
        range represented by MIDI notes (which is approximately 8Hz to 12.5KHz)
        :exc:`ValueError` exception will be raised.
        """
        result = int(round(12 * log2(self.frequency / 440) + 69))
        if 0 <= result < 128:
            return result
        raise ValueError('%f is outside the MIDI note range' % self.frequency)

    @property
    def note(self):
        """
        Return the (nearest) note to the tone's frequency. This will be a
        string in the form accepted by :meth:`from_note`. If the frequency is
        outside the range represented by this format ("A0" is approximately
        27.5Hz, and "G9" is approximately 12.5Khz) a :exc:`ValueError`
        exception will be raised.
        """
        offset = self.midi - 60  # self.midi - A4_midi + Tone.tones.index('A')
        index = offset % 12      # offset % len(Tone.tones)
        octave = 4 + offset // 12
        if 0 <= octave <= 9:
            return (
                Tone.tones[index] +
                ('#' if Tone.tones[index] == Tone.tones[index - 1] else '') +
                str(octave)
            )
        raise ValueError('%f is outside the notation range' % self.frequency)

    def up(self, n=1):
        """
        Return the :class:`Tone` *n* semi-tones above this frequency (*n*
        defaults to 1).
        """
        return Tone.from_midi(self.midi + n)

    def down(self, n=1):
        """
        Return the :class:`Tone` *n* semi-tones below this frequency (*n*
        defaults to 1).
        """
        return Tone.from_midi(self.midi - n)
