from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest

import cli.pinout as pinout


def test_args_incorrect():
    with pytest.raises(SystemExit) as ex:
        pinout.parse_args(['--nonexistentarg'])
    assert ex.value.code == 2


def test_args_color():
    args = pinout.parse_args([])
    assert args.color is None
    args = pinout.parse_args(['--color'])
    assert args.color is True
    args = pinout.parse_args(['--monochrome'])
    assert args.color is False


def test_args_revision():
    args = pinout.parse_args(['--revision', '000d'])
    assert args.revision == '000d'


def test_help(capsys):
    with pytest.raises(SystemExit) as ex:
        pinout.parse_args(['--help'])
    out, err = capsys.readouterr()
    assert 'GPIO pinout' in out
    assert ex.value.code == 0
