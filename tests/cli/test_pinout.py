from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


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
