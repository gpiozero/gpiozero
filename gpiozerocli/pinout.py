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
        try:
            from gpiozero import pi_info
        except ImportError:
            formatter = self.parser._get_formatter()
            formatter.add_text(
                "Unable to initialize GPIO Zero. This usually means that you "
                "are not running %(prog)s on a Raspberry Pi. If you still wish "
                "to run %(prog)s, set the GPIOZERO_PIN_FACTORY environment "
                "variable to 'mock' and retry, or refer to the Remote GPIO "
                "section of the manual* to configure your environment to "
                "remotely access your Pi."
            )
            formatter.add_text(
                "* https://gpiozero.readthedocs.io/en/latest/remote_gpio.html"
            )
            sys.stderr.write(formatter.format_help())
        else:
            if args.revision == '':
                try:
                    pi_info().pprint(color=args.color)
                except IOError:
                    raise IOError('This device is not a Raspberry Pi')
            else:
                pi_info(args.revision).pprint(color=args.color)
            formatter = self.parser._get_formatter()
            formatter.add_text(
                "For further information, please refer to https://pinout.xyz/"
            )
            sys.stdout.write('\n')
            sys.stdout.write(formatter.format_help())


main = PinoutTool()
