# GPIO Zero: A simple interface to GPIO devices with Raspberry Pi
#
# Copyright (c) 2026 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Stewart <stewart@adcock.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

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
    assert args.revision == 13

def test_args_rotate():
    args = main.parser.parse_args([])
    assert args.rotate is False
    args = main.parser.parse_args(['--rotate'])
    assert args.rotate is True
    args = main.parser.parse_args(['-R'])
    assert args.rotate is True

def test_execution_rotate(capsys):
    assert main(['--revision', 'a02082', '--monochrome', '--rotate']) == 0
    out, err = capsys.readouterr()
    j8 = out.split('J8:\n')[1].split('\n\n')[0].splitlines()
    assert len(j8) == 20
    assert j8[0].index('(40)') < j8[0].index('(39)')
    assert 'GPIO21' in j8[0] and 'GND' in j8[0]
    assert j8[-1].index('(2)') < j8[-1].index('(1)')
    assert '5V' in j8[-1] and '3V3' in j8[-1]
    run = out.split('RUN:\n')[1].split('\n\n')[0].splitlines()
    assert '(2)' in run[0] and '(1)' in run[1]

def test_execution_not_rotated(capsys):
    assert main(['--revision', 'a02082', '--monochrome']) == 0
    out, err = capsys.readouterr()
    j8 = out.split('J8:\n')[1].split('\n\n')[0].splitlines()
    assert len(j8) == 20
    assert j8[0].index('(1)') < j8[0].index('(2)')
    assert '3V3' in j8[0] and '5V' in j8[0]
    assert j8[-1].index('(39)') < j8[-1].index('(40)')

def test_help(capsys):
    with pytest.raises(SystemExit) as ex:
        main(['pinout', '--help'])
    out, err = capsys.readouterr()
    assert 'GPIO pin-out' in out

def test_execution(capsys, no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
    assert main([]) == 0
