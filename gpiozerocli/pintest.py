# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import sys
import warnings

from . import CliTool
from gpiozero import Device
from gpiozero.pins.pi import PiBoardInfo


class PintestTool(CliTool):
    """
    A utility for testing the GPIO pins on a Raspberry Pi, inspired by pigpio's
    gpiotest example script, and wiringPi's pintest utility.
    """
    def __init__(self):
        super().__init__()
        self.parser.add_argument(
            '-p', '--pins',
            dest='pins', default='',
            help="The pin(s) to test. Can be specified as a comma-separated "
            "list of pins. Pin numbers can be given in any form accepted by "
            "gpiozero, e.g. 14, GPIO14, BOARD8. The default is to test all "
            "pins")
        self.parser.add_argument(
            '-s', '--skip',
            dest='skip', default='',
            help="The pin(s) to skip testing. Can be specified as comma-"
            "separated list of pins. Pin numbers can be given in any form "
            "accepted by gpiozero, e.g. 14, GPIO14, BOARD8. The default is "
            "to skip no pins")
        self.parser.add_argument(
            '-y', '--yes',
            dest='prompt', action='store_false',
            help="Proceed without prompting")
        self.parser.add_argument(
            '-r', '--revision',
            dest='revision', type=lambda s: int(s, base=16), default=None,
            help="Force board revision. Default is to autodetect revision of "
            "current device. You should avoid this option unless you are "
            "very sure the detection is incorrect")

    def main(self, args):
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

        pins = self.get_pins(
            board_info,
            include=args.pins.split(',') if args.pins else (),
            exclude=args.skip.split(',') if args.skip else ())
        fmt = self.get_formatter()
        fmt.add_text(
            f"""
            This program checks the board's user-accessible GPIO pins. The
            board's model is: {board_info.description}. The following pins are
            selected for testing:
            """)
        fmt.add_text(', '.join(pin.name for pin in pins))
        fmt.add_text(
            """
            Please ensure that nothing is connected to any of the pins listed
            above for the test duration.
            """)
        print(fmt.format_help())
        if args.prompt:
            s = input('Proceed with test? [y/N] ').strip().lower()
            if s != 'y':
                return 2

        failed = []
        for pin in pins:
            try:
                print(f'Testing {pin.name}...', end='')
                self.test_pin(pin)
            except ValueError as e:
                print(e)
                failed.append(pin)
            else:
                print('ok')

        return 1 if failed else 0

    def get_pins(self, board, include, exclude):
        if not include:
            pins = {
                pin
                for header in board.headers.values()
                for pin in header.pins.values()
                if 'gpio' in pin.interfaces
            }
        else:
            pins = {
                pin
                for name in include
                for header, pin in board.find_pin(name)
            }
        skip = {
            pin
            for name in exclude
            for header, pin in board.find_pin(name)
        }
        pins -= skip
        for pin in pins:
            if 'gpio' not in pin.interfaces:
                raise ValueError(f'{pin.spec} is not a GPIO pin')
        return pins

    def test_pin(self, pin_info):
        with Device.pin_factory.pin(pin_info.name) as pin:
            save_function = pin.function
            save_state = pin.state
            try:
                pin.function = 'output'
                pin.state = 0
                if pin.state != 0:
                    raise ValueError(f'Write 0 to {pin_info.function} failed')
                pin.state = 1
                if pin.state != 1:
                    raise ValueError(f'Write 1 to {pin_info.function} failed')
                pin.function = 'input'
                if pin_info.pull != 'up':
                    pin.pull = 'down'
                    if pin.state != 0:
                        raise ValueError(
                            f'Pull down on {pin_info.function} failed')
                if pin_info.pull != 'down':
                    pin.pull = 'up'
                    if pin.state != 1:
                        raise ValueError(
                            f'Pull up on {pin_info.function} failed')
                if pin_info.pull == '':
                    pin.pull = 'floating'
            finally:
                pin.function = save_function
                if save_function == 'output':
                    pin.state = save_state


main = PintestTool()
