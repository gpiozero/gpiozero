# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 Martchus <martchus@gmx.net>
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

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import io
import re
import errno
import pytest
from mock import patch, MagicMock

import gpiozero.pins.data
import gpiozero.pins.local
from gpiozero.pins.local import LocalPiFactory
from gpiozero.pins.data import Style, HeaderInfo, PinInfo
from gpiozero import *


def test_pi_revision():
    with patch('gpiozero.devices.Device.pin_factory', LocalPiFactory()):
        # Can't use MockPin for this as we want something that'll actually try
        # and read /proc/device-tree/system/linux,revision and /proc/cpuinfo
        # (MockPin simply parrots the 3B's data); LocalPiFactory is used as we
        # can definitely instantiate it (strictly speaking it's abstract but
        # we're only interested in the pi_info stuff)
        with patch('io.open') as m:
            m.return_value.__enter__.side_effect = [
                # Pretend /proc/device-tree/system/linux,revision doesn't
                # exist, and that /proc/cpuinfo contains the Revision: 0002
                # after some filler
                IOError(errno.ENOENT, 'File not found'),
                ['lots of irrelevant', 'lines', 'followed by', 'Revision: 0002', 'Serial:  xxxxxxxxxxx']
            ]
            assert pi_info().revision == '0002'
            # LocalPiFactory caches the revision (because realistically it
            # isn't going to change at runtime); we need to wipe it here though
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: a21042']
            ]
            assert pi_info().revision == 'a21042'
            # Check over-volting result (some argument over whether this is 7
            # or 8 character result; make sure both work)
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: 1000003']
            ]
            assert pi_info().revision == '0003'
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = [
                IOError(errno.ENOENT, 'File not found'),
                ['Revision: 100003']
            ]
            assert pi_info().revision == '0003'
            # Check that parsing /proc/device-tree/system/linux,revision also
            # works properly
            Device.pin_factory._info = None
            m.return_value.__enter__.side_effect = None
            m.return_value.__enter__.return_value = io.BytesIO(b'\x00\xa2\x20\xd3')
            assert pi_info().revision == 'a220d3'
            # Finally, check that if everything's a bust we raise PinUnknownPi
            with pytest.raises(PinUnknownPi):
                Device.pin_factory._info = None
                m.return_value.__enter__.return_value = None
                m.return_value.__enter__.side_effect = [
                    IOError(errno.ENOENT, 'File not found'),
                    ['nothing', 'relevant']
                ]
                pi_info()
            with pytest.raises(PinUnknownPi):
                pi_info('0fff')

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

def test_pi_info_other_types():
    assert pi_info(b'9000f1') == pi_info(0x9000f1)

def test_physical_pins():
    # Assert physical pins for some well-known Pi's; a21041 is a Pi2B
    assert pi_info('a21041').physical_pins('3V3') == {('J8', 1), ('J8', 17)}
    assert pi_info('a21041').physical_pins('GPIO2') == {('J8', 3)}
    assert pi_info('a21041').physical_pins('GPIO47') == set()

def test_physical_pin():
    with pytest.raises(PinMultiplePins):
        assert pi_info('a21041').physical_pin('GND')
    assert pi_info('a21041').physical_pin('GPIO3') == ('J8', 5)
    with pytest.raises(PinNoPins):
        assert pi_info('a21041').physical_pin('GPIO47')

def test_pulled_up():
    assert pi_info('a21041').pulled_up('GPIO2')
    assert not pi_info('a21041').pulled_up('GPIO4')
    assert not pi_info('a21041').pulled_up('GPIO47')

def test_pprint_content():
    with patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        pi_info('900092').pprint(color=False)
        s = ''.join(stdout.output)
        assert ('o' * 20 + ' ') in s # first header row
        assert ('1' + 'o' * 19 + ' ') in s # second header row
        assert 'PiZero' in s
        assert 'V1.2' in s # PCB revision
        assert '900092' in s # Pi revision
        assert 'BCM2835' in s # SOC name
        stdout.output = []
        pi_info('0002').pprint(color=False)
        s = ''.join(stdout.output)
        assert ('o' * 13 + ' ') in s # first header row
        assert ('1' + 'o' * 12 + ' ') in s # second header row
        assert 'Pi Model' in s
        assert 'B  V1.0' in s # PCB revision
        assert '0002' in s # Pi revision
        assert 'BCM2835' in s # SOC name
        stdout.output = []
        pi_info('0014').headers['SODIMM'].pprint(color=False)
        assert len(''.join(stdout.output).splitlines()) == 100

def test_format_content():
    with patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        pi_info('900092').pprint(color=False)
        s = ''.join(stdout.output)
        assert '{0:mono}\n'.format(pi_info('900092')) == s
        stdout.output = []
        pi_info('900092').pprint(color=True)
        s = ''.join(stdout.output)
        assert '{0:color full}\n'.format(pi_info('900092')) == s

def test_pprint_headers():
    assert len(pi_info('0002').headers) == 1
    assert len(pi_info('000e').headers) == 2
    assert len(pi_info('900092').headers) == 1
    with patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        pi_info('0002').pprint()
        s = ''.join(stdout.output)
        assert 'P1:\n' in s
        assert 'P5:\n' not in s
        stdout.output = []
        pi_info('000e').pprint()
        s = ''.join(stdout.output)
        assert 'P1:\n' in s
        assert 'P5:\n' in s
        stdout.output = []
        pi_info('900092').pprint()
        s = ''.join(stdout.output)
        assert 'J8:\n' in s
        assert 'P1:\n' not in s
        assert 'P5:\n' not in s

def test_pprint_color():
    with patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        pi_info('900092').pprint(color=False)
        s = ''.join(stdout.output)
        assert '\x1b[0m' not in s # make sure ANSI reset code isn't in there
        stdout.output = []
        pi_info('900092').pprint(color=True)
        s = ''.join(stdout.output)
        assert '\x1b[0m' in s # check the ANSI reset code *is* in there (can't guarantee much else!)
        stdout.output = []
        stdout.fileno.side_effect = IOError('not a real file')
        pi_info('900092').pprint()
        s = ''.join(stdout.output)
        assert '\x1b[0m' not in s # default should output mono
        with patch('os.isatty') as isatty:
            isatty.return_value = True
            stdout.fileno.side_effect = None
            stdout.output = []
            pi_info('900092').pprint()
            s = ''.join(stdout.output)
            assert '\x1b[0m' in s # default should now output color

def test_pprint_styles():
    with pytest.raises(ValueError):
        Style.from_style_content('mono color full')
    with pytest.raises(ValueError):
        Style.from_style_content('full specs')
    with patch('sys.stdout') as stdout:
        s = '{0:full}'.format(pi_info('900092'))
        assert '\x1b[0m' not in s # ensure default is mono when stdout is not a tty
    with pytest.raises(ValueError):
        '{0:foo on bar}'.format(Style())

def test_pprint_missing_pin():
    header = HeaderInfo('FOO', 4, 2, {
        1: PinInfo(1, '5V',    False, 1, 1),
        2: PinInfo(2, 'GND',   False, 1, 2),
        # Pin 3 is deliberately missing
        4: PinInfo(4, 'GPIO1', False, 2, 2),
        5: PinInfo(5, 'GPIO2', False, 3, 1),
        6: PinInfo(6, 'GPIO3', False, 3, 2),
        7: PinInfo(7, '3V3',   False, 4, 1),
        8: PinInfo(8, 'GND',   False, 4, 2),
        })
    with patch('sys.stdout') as stdout:
        stdout.output = []
        stdout.write = lambda buf: stdout.output.append(buf)
        s = ''.join(stdout.output)
        header.pprint()
        for i in range(1, 9):
            if i == 3:
                assert '(3)' not in s
            else:
                assert ('(%d)' % i)

def test_pprint_rows_cols():
    assert '{0:row1}'.format(pi_info('900092').headers['J8']) == '1o'
    assert '{0:row2}'.format(pi_info('900092').headers['J8']) == 'oo'
    assert '{0:col1}'.format(pi_info('0002').headers['P1']) == '1oooooooooooo'
    assert '{0:col2}'.format(pi_info('0002').headers['P1']) == 'ooooooooooooo'
    with pytest.raises(ValueError):
        '{0:row16}'.format(pi_info('0002').headers['P1'])
    with pytest.raises(ValueError):
        '{0:col3}'.format(pi_info('0002').headers['P1'])
