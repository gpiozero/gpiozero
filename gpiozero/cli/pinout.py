#!/usr/bin/env python
"""
pinout - gpiozero command-line pinout tool.

Output Raspberry Pi GPIO pinout information.
"""

from __future__ import unicode_literals, absolute_import, print_function, division

import argparse
import sys

from gpiozero import *


def parse_args(args):
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        '-r', '--revision',
        dest='revision',
        default='',
        help='RPi revision. Default is to autodetect revision of current device'
    )

    parser.add_argument(
        '-c', '--color',
        action="store_true",
        default=None,
        help='Force colored output (by default, the output will include ANSI'
        'color codes if run in a color-capable terminal). See also --monochrome'
    )

    parser.add_argument(
        '-m', '--monochrome',
        dest='color',
        action='store_false',
        help='Force monochrome output. See also --color'
    )

    try:
        args = parser.parse_args(args)
    except argparse.ArgumentError as ex:
        print('Error parsing arguments.')
        parser.error(str(ex.message))
        exit(-1)
    return args


def main():
    args = parse_args(sys.argv[1:])

    if args.revision == '':
        try:
            pi_info().pprint(color=args.color)
        except IOError:
            print('This device is not a Raspberry Pi')
            exit(2)
    else:
        pi_info(args.revision).pprint(color=args.color)


if __name__ == '__main__':
    main()
