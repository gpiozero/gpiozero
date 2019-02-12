# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2019 Andrew Scheller <github@loowis.durge.org>
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


import sys
import pytest
from mock import patch
from collections import namedtuple
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose

from gpiozero.pins.mock import MockSPIDevice, MockPin
from gpiozero import *


def clamp(v, min_value, max_value):
    return min(max_value, max(min_value, v))

def scale(v, ref, bits):
    v /= ref
    vmin = -(2 ** bits)
    vmax = -vmin - 1
    vrange = vmax - vmin
    return int(((v + 1) / 2.0) * vrange + vmin)


class MockMCP3xxx(MockSPIDevice):
    def __init__(
            self, clock_pin, mosi_pin, miso_pin, select_pin=None,
            channels=8, bits=10):
        super(MockMCP3xxx, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin)
        self.vref = 3.3
        self.channels = [0.0] * channels
        self.channel_bits = 3
        self.bits = bits
        self.state = 'idle'

    def on_start(self):
        super(MockMCP3xxx, self).on_start()
        self.state = 'idle'

    def on_bit(self):
        if self.state == 'idle':
            if self.rx_buf[-1]:
                self.state = 'mode'
                self.rx_buf = []
        elif self.state == 'mode':
            if self.rx_buf[-1]:
                self.state = 'single'
            else:
                self.state = 'diff'
            self.rx_buf = []
        elif self.state in ('single', 'diff'):
            if len(self.rx_buf) == self.channel_bits:
                self.on_result(self.state == 'diff', self.rx_word())
                self.state = 'result'
        elif self.state == 'result':
            if not self.tx_buf:
                self.state = 'idle'
                self.rx_buf = []
        else:
            assert False

    def on_result(self, differential, channel):
        if differential:
            pos_channel = channel
            neg_channel = pos_channel ^ 1
            result = self.channels[pos_channel] - self.channels[neg_channel]
            result = clamp(result, 0, self.vref)
        else:
            result = clamp(self.channels[channel], 0, self.vref)
        result = scale(result, self.vref, self.bits)
        self.tx_word(result, self.bits + 2)


class MockMCP3xx1(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None, bits=10):
        super(MockMCP3xx1, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=2, bits=bits)

    def on_start(self):
        super(MockMCP3xx1, self).on_start()
        result = self.channels[0] - self.channels[1]
        result = clamp(result, 0, self.vref)
        result = scale(result, self.vref, self.bits)
        self.tx_word(result, self.bits + 3)

    def on_bit(self):
        pass


class MockMCP3xx2(MockMCP3xxx):
    def __init__(
            self, clock_pin, mosi_pin, miso_pin, select_pin=None,
            bits=10):
        super(MockMCP3xx2, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=2, bits=bits)
        self.channel_bits = 1


class MockMCP33xx(MockMCP3xxx):
    def __init__(
            self, clock_pin, mosi_pin, miso_pin, select_pin=None,
            channels=8):
        super(MockMCP33xx, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels, 12)

    def on_result(self, differential, channel):
        if differential:
            pos_channel = channel
            neg_channel = pos_channel ^ 1
            result = self.channels[pos_channel] - self.channels[neg_channel]
            result = clamp(result, -self.vref, self.vref)
        else:
            result = clamp(self.channels[channel], 0, self.vref)
        result = scale(result, self.vref, self.bits)
        if result < 0:
            result += 8192
        self.tx_word(result, self.bits + 3)


class MockMCP3001(MockMCP3xx1):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3001, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, bits=10)


class MockMCP3002(MockMCP3xx2):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3002, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, bits=10)


class MockMCP3004(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3004, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=4, bits=10)


class MockMCP3008(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3008, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=8, bits=10)


class MockMCP3201(MockMCP3xx1):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3201, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, bits=12)


class MockMCP3202(MockMCP3xx2):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3202, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, bits=12)


class MockMCP3204(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3204, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=4, bits=12)


class MockMCP3208(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3208, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=8, bits=12)


class MockMCP3301(MockMCP3xxx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3301, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=2, bits=12)

    def on_start(self):
        super(MockMCP3301, self).on_start()
        result = self.channels[0] - self.channels[1]
        result = clamp(result, -self.vref, self.vref)
        result = scale(result, self.vref, self.bits)
        if result < 0:
            result += 8192
        self.tx_word(result, self.bits + 4)


class MockMCP3302(MockMCP33xx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3302, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=4)


class MockMCP3304(MockMCP33xx):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin=None):
        super(MockMCP3304, self).__init__(
            clock_pin, mosi_pin, miso_pin, select_pin, channels=8)


def single_mcp_test(mock, pot, channel, bits):
    scale = 2**bits
    tolerance = 1 / scale
    voltage_tolerance = pot.max_voltage / scale
    mock.channels[channel] = 0.0
    assert pot.raw_value == 0
    assert isclose(pot.value, 0.0, abs_tol=tolerance)
    assert isclose(pot.voltage, 0.0, abs_tol=voltage_tolerance)
    mock.channels[channel] = mock.vref / 2
    assert pot.raw_value == (scale / 2) - 1
    assert isclose(pot.value, 0.5, abs_tol=tolerance)
    assert isclose(pot.voltage, pot.max_voltage / 2, abs_tol=voltage_tolerance)
    mock.channels[channel] = mock.vref
    assert pot.raw_value == scale - 1
    assert isclose(pot.value, 1.0, abs_tol=tolerance)
    assert isclose(pot.voltage, pot.max_voltage, abs_tol=voltage_tolerance)

def differential_mcp_test(mock, pot, pos_channel, neg_channel, bits, full=False):
    scale = 2**bits
    tolerance = 1 / scale
    voltage_tolerance = pot.max_voltage / scale
    mock.channels[pos_channel] = 0.0
    mock.channels[neg_channel] = 0.0
    assert pot.raw_value == 0
    assert isclose(pot.value, 0.0, abs_tol=tolerance)
    assert isclose(pot.voltage, 0.0, abs_tol=voltage_tolerance)
    mock.channels[pos_channel] = mock.vref / 2
    assert pot.raw_value == (scale / 2) - 1
    assert isclose(pot.value, 0.5, abs_tol=tolerance)
    assert isclose(pot.voltage, pot.max_voltage / 2, abs_tol=voltage_tolerance)
    mock.channels[pos_channel] = mock.vref
    assert pot.raw_value == scale - 1
    assert isclose(pot.value, 1.0, abs_tol=tolerance)
    assert isclose(pot.voltage, pot.max_voltage, abs_tol=voltage_tolerance)
    mock.channels[neg_channel] = mock.vref / 2
    assert pot.raw_value == (scale / 2) - 1
    assert isclose(pot.value, 0.5, abs_tol=tolerance)
    assert isclose(pot.voltage, pot.max_voltage / 2, abs_tol=voltage_tolerance)
    mock.channels[pos_channel] = mock.vref / 2
    assert pot.raw_value == 0
    assert isclose(pot.value, 0.0, abs_tol=tolerance)
    assert isclose(pot.voltage, 0.0, abs_tol=voltage_tolerance)
    mock.channels[pos_channel] = 0.0
    mock.channels[neg_channel] = mock.vref
    if full:
        assert pot.raw_value == -scale
        assert isclose(pot.value, -1.0, abs_tol=tolerance)
        assert isclose(pot.voltage, -pot.max_voltage, abs_tol=voltage_tolerance)
    else:
        assert pot.raw_value == 0
        assert isclose(pot.value, 0.0, abs_tol=tolerance)
        assert isclose(pot.voltage, 0.0, abs_tol=voltage_tolerance)


def test_analog_input_device_bad_init(mock_factory):
    with pytest.raises(InputDeviceError):
        AnalogInputDevice(None)
    with pytest.raises(InputDeviceError):
        AnalogInputDevice(bits=None)
    with pytest.raises(InputDeviceError):
        AnalogInputDevice(8, 0)
    with pytest.raises(InputDeviceError):
        AnalogInputDevice(bits=8, max_voltage=-1)

def test_MCP3001(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3001(11, 10, 9, 8)
        with MCP3001() as pot:
            assert repr(pot).startswith('<gpiozero.MCP3001 object')
            differential_mcp_test(mock, pot, 0, 1, 10)
            assert not pot.closed
            pot.close()
            assert pot.closed
        with MCP3001(max_voltage=5.0) as pot:
            differential_mcp_test(mock, pot, 0, 1, 10)

def test_MCP3002(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3002(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3002(channel=5)
        with MCP3002(channel=1) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3002 object')
            single_mcp_test(mock, pot, 1, 10)
        with MCP3002(channel=1, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 1, 10)
        with MCP3002(channel=1, differential=True) as pot:
            differential_mcp_test(mock, pot, 1, 0, 10)

def test_MCP3004(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3004(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3004(channel=5)
        with MCP3004(channel=3) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3004 object')
            single_mcp_test(mock, pot, 3, 10)
        with MCP3004(channel=3, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 3, 10)
        with MCP3004(channel=3, differential=True) as pot:
            differential_mcp_test(mock, pot, 3, 2, 10)

def test_MCP3008(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3008(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3008(channel=9)
        with MCP3008(channel=0) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3008 object')
            single_mcp_test(mock, pot, 0, 10)
        with MCP3008(channel=1, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 1, 10)
        with MCP3008(channel=0, differential=True) as pot:
            differential_mcp_test(mock, pot, 0, 1, 10)

def test_MCP3201(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3201(11, 10, 9, 8)
        with MCP3201() as pot:
            assert repr(pot).startswith('<gpiozero.MCP3201 object')
            differential_mcp_test(mock, pot, 0, 1, 12)
        with MCP3201(max_voltage=5.0) as pot:
            differential_mcp_test(mock, pot, 0, 1, 12)

def test_MCP3202(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3202(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3202(channel=5)
        with MCP3202(channel=1) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3202 object')
            single_mcp_test(mock, pot, 1, 12)
        with MCP3202(channel=1, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 1, 12)
        with MCP3202(channel=1, differential=True) as pot:
            differential_mcp_test(mock, pot, 1, 0, 12)

def test_MCP3204(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3204(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3204(channel=5)
        with MCP3204(channel=1) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3204 object')
            single_mcp_test(mock, pot, 1, 12)
        with MCP3204(channel=1, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 1, 12)
        with MCP3204(channel=1, differential=True) as pot:
            differential_mcp_test(mock, pot, 1, 0, 12)

def test_MCP3208(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3208(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3208(channel=9)
        with MCP3208(channel=7) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3208 object')
            single_mcp_test(mock, pot, 7, 12)
        with MCP3208(channel=7, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 7, 12)
        with MCP3208(channel=7, differential=True) as pot:
            differential_mcp_test(mock, pot, 7, 6, 12)

def test_MCP3301(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3301(11, 10, 9, 8)
        with MCP3301() as pot:
            assert repr(pot).startswith('<gpiozero.MCP3301 object')
            differential_mcp_test(mock, pot, 0, 1, 12, full=True)
        with MCP3301(max_voltage=5.0) as pot:
            differential_mcp_test(mock, pot, 0, 1, 12, full=True)

def test_MCP3302(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3302(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3302(channel=4)
        with MCP3302(channel=0) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3302 object')
            single_mcp_test(mock, pot, 0, 12)
        with MCP3302(channel=0, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 0, 12)
        with MCP3302(channel=0, differential=True) as pot:
            differential_mcp_test(mock, pot, 0, 1, 12, full=True)

def test_MCP3304(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None):
        mock = MockMCP3304(11, 10, 9, 8)
        with pytest.raises(ValueError):
            MCP3304(channel=9)
        with MCP3304(channel=5) as pot:
            assert repr(pot).startswith('<gpiozero.MCP3304 object')
            single_mcp_test(mock, pot, 5, 12)
        with MCP3304(channel=5, max_voltage=5.0) as pot:
            single_mcp_test(mock, pot, 5, 12)
        with MCP3304(channel=5, differential=True) as pot:
            differential_mcp_test(mock, pot, 5, 4, 12, full=True)
