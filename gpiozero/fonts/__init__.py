# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import io
from collections import Counter
from itertools import zip_longest
from pathlib import Path


def load_segment_font(filename_or_obj, width, height, pins):
    """
    A generic function for parsing segment font definition files.

    If you're working with "standard" `7-segment`_ or `14-segment`_ displays
    you *don't* want this function; see :func:`load_font_7seg` or
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

    .. _7-segment: https://en.wikipedia.org/wiki/Seven-segment_display
    .. _14-segment: https://en.wikipedia.org/wiki/Fourteen-segment_display
    """
    assert 0 < len(pins) <= (width * height) - 1
    if isinstance(filename_or_obj, bytes):
        filename_or_obj = filename_or_obj.decode('utf-8')
    opened = isinstance(filename_or_obj, (str, Path))
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
        raise ValueError(
            f'number of definition lines is not divisible by {height}')

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
                f'length of definitions starting on line '
                f'{line_numbers[row_index]} is not divisible by {width}')

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
            raise ValueError(f'multiple definitions for {char!r}')

    return {
        char[0]: tuple(int(char[pos] == on) for pos, on in pins)
        for char in chars
    }


def load_font_7seg(filename_or_obj):
    """
    Given a filename or a file-like object, parse it as an font definition for
    a `7-segment display`_, returning a :class:`dict` suitable for use with
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

    In the example above, empty locations are marked with "." but could mostly
    be left as spaces. However, the first item defines the space (" ")
    character and needs *some* non-space characters in its definition as the
    parser also strips empty columns (as typically occur between character
    definitions). This is also why the definition for "1" must include
    something to fill the middle column.

    .. _7-segment display: https://en.wikipedia.org/wiki/Seven-segment_display
    """
    return load_segment_font(filename_or_obj, width=3, height=3, pins=[
        (1, '_'), (5, '|'), (8, '|'), (7, '_'),
        (6, '|'), (3, '|'), (4, '_')])


def load_font_14seg(filename_or_obj):
    """
    Given a filename or a file-like object, parse it as a font definition for a
    `14-segment display`_, returning a :class:`dict` suitable for use with
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

    .. _14-segment display: https://en.wikipedia.org/wiki/Fourteen-segment_display
    """
    return load_segment_font(filename_or_obj, width=5, height=5, pins=[
        (2, '-'),  (9, '|'),  (19, '|'), (22, '-'),
        (15, '|'), (5, '|'),  (11, '-'), (13, '-'),
        (6, '\\'), (7, '|'),  (8, '/'),  (16, '/'),
        (17, '|'), (18, '\\')])
