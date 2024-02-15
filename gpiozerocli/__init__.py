# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2024 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import argparse

# Remove the try clause when 3.7 support is no longer trivial
try:
    from importlib_metadata import version
except ImportError:
    from importlib.metadata import version


class CliTool:
    """
    Base class for simple command line utilities.

    The doc-string of the class forms the basis for the utility's help text.
    Instances are constructed with a :attr:`parser` which you can customize.
    The :meth:`main` method will be called with the parsed command line
    arguments and should return an appropriate exit code.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.__class__.__doc__)
        self.parser.add_argument(
            '--version',
            action='version',
            version=version('gpiozero'))

    def get_formatter(self):
        return self.parser._get_formatter()

    def get_gpiozero_help(self):
        fmt = self.get_formatter()
        fmt.add_text(
            """
            Unable to initialize GPIO Zero. This usually means that you are not
            running %(prog)s on a Raspberry Pi. If you still wish to run
            %(prog)s, set the GPIOZERO_PIN_FACTORY environment variable to
            'mock' and retry, or refer to the Remote GPIO section of the
            manual* to configure your environment to remotely access your
            Pi.
            """)
        fmt.add_text(
            "* https://gpiozero.readthedocs.io/en/stable/remote_gpio.html")
        return fmt.format_help()

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
            # Output anything else nicely formatted on stderr and exit code 1
            if int(os.environ.get('DEBUG', '0')):
                raise
            self.parser.exit(1, f'{self.parser.prog}: error: {e}\n')

    def main(self, args):
        raise NotImplementedError
