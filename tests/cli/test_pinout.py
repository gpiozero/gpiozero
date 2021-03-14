# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Stewart <stewart@adcock.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import os

import pytest

from gpiozerocli.pinout import main


def test_args_incorrect():
    with pytest.raises(SystemExit) as ex:
        main(['pinout', '--nonexistentarg'])

def test_args_color():
    args = main.parser.parse_args([])
    assert args.color is None
    args = main.parser.parse_args(['--color'])
    assert args.color is True
    args = main.parser.parse_args(['--monochrome'])
    assert args.color is False

def test_args_revision():
    args = main.parser.parse_args(['--revision', '000d'])
    assert args.revision == '000d'

def test_help(capsys):
    with pytest.raises(SystemExit) as ex:
        main(['pinout', '--help'])
    out, err = capsys.readouterr()
    assert 'GPIO pin-out' in out

def test_execution(capsys, no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
    assert main([]) == 0
