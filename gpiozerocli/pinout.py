# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2017 Ben Nuttall <ben@bennuttall.com>
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

"""
A utility for querying Raspberry Pi GPIO pin-out information.
"""

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
)

import argparse
import sys
import textwrap
import warnings
import webbrowser

from gpiozero import pi_info


class PinoutTool(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=__doc__
        )
        self.parser.add_argument(
            '-r', '--revision',
            dest='revision',
            default='',
            help='RPi revision. Default is to autodetect revision of current device'
        )
        self.parser.add_argument(
            '-c', '--color',
            action="store_true",
            default=None,
            help='Force colored output (by default, the output will include ANSI'
            'color codes if run in a color-capable terminal). See also --monochrome'
        )
        self.parser.add_argument(
            '-m', '--monochrome',
            dest='color',
            action='store_false',
            help='Force monochrome output. See also --color'
        )
        self.parser.add_argument(
            '-x', '--xyz',
            dest='xyz',
            action='store_true',
            help='Open pinout.xyz in the default web browser'
        )

    def __call__(self, args=None):
        if args is None:
            args = sys.argv[1:]
        try:
            return self.main(self.parser.parse_args(args)) or 0
        except argparse.ArgumentError as e:
            # argparse errors are already nicely formatted, print to stderr and
            # exit with code 2
            raise e
        except Exception as e:
            raise
            # Output anything else nicely formatted on stderr and exit code 1
            self.parser.exit(1, '{prog}: error: {message}\n'.format(
                prog=self.parser.prog, message=e))

    def main(self, args):
        warnings.simplefilter('ignore')
        if args.xyz:
            webbrowser.open('https://pinout.xyz')
        else:
            if args.revision == '':
                try:
                    pi_info().pprint(color=args.color)
                except ImportError:
                    formatter = self.parser._get_formatter()
                    formatter.add_text(
                        "Unable to initialize GPIO Zero. This usually means "
                        "that you are not running %(prog)s on a Raspberry Pi. "
                        "If you still wish to run %(prog)s, set the "
                        "GPIOZERO_PIN_FACTORY environment variable to 'mock' "
                        "and retry, or refer to the Remote GPIO section of "
                        "the manual* to configure your environment to "
                        "remotely access your Pi."
                    )
                    formatter.add_text(
                        "* https://gpiozero.readthedocs.io/en/stable/"
                        "remote_gpio.html"
                    )
                    sys.stderr.write(formatter.format_help())
                except IOError:
                    raise IOError('This device is not a Raspberry Pi')
            else:
                pi_info(args.revision).pprint(color=args.color)
            formatter = self.parser._get_formatter()
            formatter.add_text(
                "For further information, please refer to "
                "https://pinout.xyz/"
            )
            sys.stdout.write('\n')
            sys.stdout.write(formatter.format_help())


main = PinoutTool()
