# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 Martchus <martchus@gmx.net>
#
# SPDX-License-Identifier: BSD-3-Clause

import io
import re
import errno
import pytest
from unittest import mock

import gpiozero.pins.data
import gpiozero.pins.local
from gpiozero.pins.local import LocalPiFactory
from gpiozero.pins.pi import PiBoardInfo
from gpiozero.pins.style import Style
from gpiozero.compat import frozendict
from gpiozero import *


def test_pi_revision():
    with mock.patch('gpiozero.devices.Device.pin_factory', LocalPiFactory()):
        # Can't use MockPin for this as we want something that'll actually try
        # and read /proc/device-tree/system/linux,revision and /proc/cpuinfo
        # (MockPin simply parrots the 3B's data); LocalPiFactory is used as we
        # can definitely instantiate it (strictly speaking it's abstract but
        # we're only interested in the BoardInfo stuff)
        with mock.patch('io.open') as m:
            m.return_value.__enter__.side_effect = [
                # Pretend /proc/device-tree/system/linux,revision doesn't
                # exist, and that /proc/cpuinfo contains the Revision: 0002
                # after some filler
                IOError(errno.ENOENT, 'File not found'),
                ['lots of irrelevant', 'lines', 'followed by', 'Revision: 0002', 'Serial:  xxxxxxxxxxx']
            ]
            assert Device.pin_factory.board_info.revision == '0002'
            # LocalPiFactory caches the revision (because realistically it
            # isn't going to change at runtime); we need to wipe it here though
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: a21042']
            ]
            assert Device.pin_factory.board_info.revision == 'a21042'
            # Check over-volting result (some argument over whether this is 7
            # or 8 character result; make sure both work)
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: 1000003']
            ]
            assert Device.pin_factory.board_info.revision == '0003'
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: 100003']
            ]
            assert Device.pin_factory.board_info.revision == '0003'
            # Check we complain loudly if we can't access linux,revision
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                # Pretend /proc/device-tree/system/linux,revision doesn't
                # exist, and that /proc/cpuinfo contains the Revision: 0002
                # after some filler
                IOError(errno.EACCES, 'Permission denied'),
                ['Revision: 100003']
            ]
            with pytest.raises(IOError):
                Device.pin_factory.board_info
            # Check that parsing /proc/device-tree/system/linux,revision also
            # works properly
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = None
            m.return_value.__enter__.return_value = io.BytesIO(b'\x00\xa2\x20\xd3')
            assert Device.pin_factory.board_info.revision == 'a220d3'
            # Check that if everything's a bust we raise PinUnknownPi
            with pytest.raises(PinUnknownPi):
                Device.pin_factory._info = None
                m.return_value.__enter__.return_value = None
                m.return_value.__enter__.side_effect = [
                    IOError(errno.ENOENT, 'File not found'),
                    ['nothing', 'relevant']
                ]
                Device.pin_factory.board_info
            with pytest.raises(PinUnknownPi):
                PiBoardInfo.from_revision(0xfff)

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_pi_info():
    r = pi_info('900011')
    assert r.model == 'B'
    assert r.pcb_revision == '1.0'
    assert r.memory == 512
    assert r.manufacturer == 'Sony'
    assert r.storage == 'SD'
    assert r.usb == 2
    assert r.ethernet == 1
    assert not r.wifi
    assert not r.bluetooth
    assert r.csi == 1
    assert r.dsi == 1
    r = pi_info('9000f1')
    assert r.model == '???'
    assert r.pcb_revision == '1.1'
    assert r.memory == 512
    assert r.manufacturer == 'Sony'
    assert r.storage == 'MicroSD'
    assert r.usb == 4
    assert r.ethernet == 1
    assert not r.wifi
    assert not r.bluetooth
    assert r.csi == 1
    assert r.dsi == 1
    assert repr(r).startswith('PiBoardInfo(revision=')
    assert 'headers=...' in repr(r)

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_pi_info_other_types():
    assert pi_info(b'9000f1') == pi_info(0x9000f1)

def test_find_pin():
    board_info = PiBoardInfo.from_revision(0xa21041)
    assert {('J8', 1), ('J8', 17)} == {
        (head.name, pin.number)
        for (head, pin) in board_info.find_pin('3V3')
    }
    assert {('J8', 3)} == {
        (head.name, pin.number)
        for (head, pin) in board_info.find_pin('GPIO2')
    }
    assert set() == {
        (head.name, pin.number)
        for (head, pin) in board_info.find_pin('GPIO47')
    }

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_physical_pins():
    # Assert physical pins for some well-known Pi's; a21041 is a Pi2B
    board_info = PiBoardInfo.from_revision(0xa21041)
    assert board_info.physical_pins('3V3') == {('J8', 1), ('J8', 17)}
    assert board_info.physical_pins('GPIO2') == {('J8', 3)}
    assert board_info.physical_pins('GPIO47') == set()

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_physical_pin():
    board_info = PiBoardInfo.from_revision(0xa21041)
    with pytest.raises(PinMultiplePins):
        assert board_info.physical_pin('GND')
    assert board_info.physical_pin('GPIO3') == ('J8', 5)
    with pytest.raises(PinNoPins):
        assert board_info.physical_pin('GPIO47')

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_pulled_up():
    board_info = PiBoardInfo.from_revision(0xa21041)
    assert board_info.pulled_up('GPIO2')
    assert not board_info.pulled_up('GPIO4')
    assert not board_info.pulled_up('GPIO47')

def test_pull():
    board_info = PiBoardInfo.from_revision(0xa21041)
    for header, pin in board_info.find_pin('GPIO2'):
        assert pin.pull == 'up'
    for header, pin in board_info.find_pin('GPIO4'):
        assert pin.pull == ''
    for header, pin in board_info.find_pin('GPIO47'):
        assert pin.pull == ''

def test_pprint_content(capsys):
    PiBoardInfo.from_revision(0x900092).pprint(color=False)
    cap = capsys.readouterr()
    assert ('-' + 'o' * 20) in cap.out # first header row
    assert (' ' + '1' + 'o' * 19) in cap.out # second header row
    assert 'PiZero' in cap.out
    assert 'V1.2' in cap.out # PCB revision
    assert '900092' in cap.out # Pi revision
    assert 'BCM2835' in cap.out # SoC name
    PiBoardInfo.from_revision(0x0002).pprint(color=False)
    cap = capsys.readouterr()
    assert ('o' * 13 + ' ') in cap.out # first header row
    assert ('1' + 'o' * 12 + ' ') in cap.out # second header row
    assert 'Pi Model' in cap.out
    assert 'B  V1.0' in cap.out # PCB revision
    assert '0002' in cap.out # Pi revision
    assert 'BCM2835' in cap.out # SOC name
    PiBoardInfo.from_revision(0x0014).headers['SODIMM'].pprint(color=False)
    cap = capsys.readouterr()
    assert len(cap.out.splitlines()) == 100

def test_format_content(capsys):
    board_info = PiBoardInfo.from_revision(0x900092)
    board_info.pprint(color=False)
    cap = capsys.readouterr()
    assert f'{board_info:mono}\n' == cap.out
    board_info.pprint(color=True)
    cap = capsys.readouterr()
    assert f'{board_info:color full}\n' == cap.out
    with pytest.raises(ValueError):
        f'{board_info:color foo}'

def test_pprint_headers(capsys):
    assert len(PiBoardInfo.from_revision(0x0002).headers) == 3
    assert len(PiBoardInfo.from_revision(0x000e).headers) == 5
    assert len(PiBoardInfo.from_revision(0x900092).headers) == 3
    PiBoardInfo.from_revision(0x0002).pprint()
    cap = capsys.readouterr()
    assert 'P1:\n' in cap.out
    assert 'P5:\n' not in cap.out
    PiBoardInfo.from_revision(0x000e).pprint()
    cap = capsys.readouterr()
    assert 'P1:\n' in cap.out
    assert 'P5:\n' in cap.out
    PiBoardInfo.from_revision(0x900092).pprint()
    cap = capsys.readouterr()
    assert 'J8:\n' in cap.out
    assert 'P1:\n' not in cap.out
    assert 'P5:\n' not in cap.out

def test_format_headers(capsys):
    board_info = PiBoardInfo.from_revision(0xc03131)
    board_info.headers['J8'].pprint(color=False)
    cap = capsys.readouterr()
    assert f'{board_info.headers["J8"]:mono}\n' == cap.out
    board_info.headers['J8'].pprint(color=True)
    cap = capsys.readouterr()
    assert f'{board_info.headers["J8"]:color}\n' == cap.out
    with pytest.raises(ValueError):
        f'{board_info.headers["J8"]:mono foo}'

def test_pprint_color(capsys):
    board_info = PiBoardInfo.from_revision(0x900092)
    board_info.pprint(color=False)
    cap = capsys.readouterr()
    assert '\x1b[0m' not in cap.out
    board_info.pprint(color=True)
    cap = capsys.readouterr()
    assert '\x1b[0m' in cap.out

def test_pprint_style_detect():
    board_info = PiBoardInfo.from_revision(0x900092)
    with mock.patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        stdout.fileno.side_effect = IOError('not a real file')
        board_info.pprint()
        s = ''.join(stdout.output)
        assert '\x1b[0m' not in s # default should output mono
        with mock.patch('os.isatty') as isatty:
            isatty.return_value = True
            stdout.fileno.side_effect = None
            stdout.fileno.return_value = 1
            stdout.output = []
            board_info.pprint()
            s = ''.join(stdout.output)
            assert '\x1b[0m' in s # default should now output color

def test_style_parser():
    with pytest.raises(ValueError):
        Style.from_style_content('mono color full')
    with pytest.raises(ValueError):
        f'{Style():foo on bar}'

def test_pprint_missing_pin(capsys):
    header = HeaderInfo('FOO', 4, 2, {
        1: PinInfo(1, '5V',    {'5V'}, '', 1, 1, set()),
        2: PinInfo(2, 'GND',   {'GND'}, '', 1, 2, set()),
        # Pin 3 is deliberately missing
        4: PinInfo(4, 'GPIO1', {'GPIO1'}, '',   2, 2, {'gpio'}),
        5: PinInfo(5, 'GPIO2', {'GPIO2'}, 'up', 3, 1, {'gpio'}),
        6: PinInfo(6, 'GPIO3', {'GPIO3'}, 'up', 3, 2, {'gpio'}),
        7: PinInfo(7, '3V3',   {'3V3'}, '', 4, 1, set()),
        8: PinInfo(8, 'GND',   {'GND'}, '', 4, 2, set()),
        })
    header.pprint()
    cap = capsys.readouterr()
    for i in range(1, 9):
        if i == 3:
            assert '(3)' not in cap.out
        else:
            assert f'({i:d})' in cap.out

def test_pprint_rows_cols():
    board_info = PiBoardInfo.from_revision(0x900092)
    assert f'{board_info.headers["J8"]:row1}' == '1o'
    assert f'{board_info.headers["J8"]:row2}' == 'oo'
    board_info = PiBoardInfo.from_revision(0x0002)
    assert f'{board_info.headers["P1"]:col1}' == '1oooooooooooo'
    assert f'{board_info.headers["P1"]:col2}' == 'ooooooooooooo'
    with pytest.raises(ValueError):
        f'{board_info.headers["P1"]:row16}'
    with pytest.raises(ValueError):
        f'{board_info.headers["P1"]:col3}'
