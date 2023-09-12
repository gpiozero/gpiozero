# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2017 Ben Nuttall <ben@bennuttall.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import sys
import warnings
import webbrowser

from . import CliTool
from gpiozero import Device
from gpiozero.pins.pi import PiBoardInfo
from gpiozero.pins.style import Style


class PinoutTool(CliTool):
    """
    A utility for querying GPIO pin-out information.
    """
    def __init__(self):
        super().__init__()
        self.parser.add_argument(
            '-r', '--revision',
            dest='revision',
            type=lambda s: int(s, base=16),
            default=None,
            help='Board revision. Default is to autodetect revision of '
            'current device')
        self.parser.add_argument(
            '-c', '--color',
            action="store_true",
            default=None,
            help='Force colored output (by default, the output will include '
            'ANSI color codes if run in a color-capable terminal). See also '
            '--monochrome')
        self.parser.add_argument(
            '-m', '--monochrome',
            dest='color',
            action='store_false',
            help='Force monochrome output. See also --color')
        self.parser.add_argument(
            '-x', '--xyz',
            dest='xyz',
            action='store_true',
            help='Open pinout.xyz in the default web browser')

    def main(self, args):
        warnings.simplefilter('ignore')
        if args.xyz:
            webbrowser.open('https://pinout.xyz')
        else:
            if args.revision is None:
                try:
                    Device.ensure_pin_factory()
                    board_info = Device.pin_factory.board_info
                except ImportError:
                    sys.stderr.write(self.get_gpiozero_help())
                    return 1
                except IOError:
                    sys.stderr.write('Unrecognized board')
                    return 1
            else:
                board_info = PiBoardInfo.from_revision(args.revision)
            style = Style(color=args.color)
            sys.stdout.write(f'{board_info:{style} full}')
            formatter = self.get_formatter()
            formatter.add_text(
                "For further information, please refer to "
                "https://pinout.xyz/")
            sys.stdout.write('\n\n')
            sys.stdout.write(formatter.format_help())

    def output(self, board):
        return


main = PinoutTool()
