# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys


# ANSI color codes, for the pretty printers (nothing comprehensive, just enough
# for our purposes)

class Style:
    def __init__(self, color=None):
        self.color = self._term_supports_color() if color is None else bool(color)
        self.effects = {
            'reset':  0,
            'bold':   1,
            'normal': 22,
            }
        self.colors = {
            'black':   0,
            'red':     1,
            'green':   2,
            'yellow':  3,
            'blue':    4,
            'magenta': 5,
            'cyan':    6,
            'white':   7,
            'default': 9,
            }

    @staticmethod
    def _term_supports_color():
        try:
            stdout_fd = sys.stdout.fileno()
        except IOError:
            return False
        else:
            is_a_tty = os.isatty(stdout_fd)
            is_windows = sys.platform.startswith('win')
            return is_a_tty and not is_windows

    @classmethod
    def from_style_content(cls, format_spec):
        specs = set(format_spec.split())
        style = specs & {'mono', 'color'}
        content = specs - style
        if len(style) > 1:
            raise ValueError('cannot specify both mono and color styles')
        try:
            style = style.pop()
        except KeyError:
            style = 'color' if cls._term_supports_color() else 'mono'
        if not content:
            content = 'full'
        else:
            content = ' '.join(content)
        return cls(style == 'color'), content

    def __call__(self, format_spec):
        specs = format_spec.split()
        codes = []
        fore = True
        for spec in specs:
            if spec == 'on':
                fore = False
            else:
                try:
                    codes.append(self.effects[spec])
                except KeyError:
                    try:
                        if fore:
                            codes.append(30 + self.colors[spec])
                        else:
                            codes.append(40 + self.colors[spec])
                    except KeyError:
                        raise ValueError(f'invalid format specification "{spec}"')
        if self.color:
            codes = ';'.join(str(code) for code in codes)
            return f'\x1b[{codes}m'
        else:
            return ''

    def __format__(self, format_spec):
        if format_spec == '':
            return 'color' if self.color else 'mono'
        else:
            return self(format_spec)
