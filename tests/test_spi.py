# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
nstr = str
str = type('')


import io
import sys
import pytest
from array import array
from mock import patch
from collections import namedtuple

from gpiozero.pins.native import NativeFactory
from gpiozero.pins.local import (
    LocalPiHardwareSPI,
    LocalPiSoftwareSPI,
    LocalPiHardwareSPIShared,
    LocalPiSoftwareSPIShared,
    )
from gpiozero.pins.mock import MockSPIDevice
from gpiozero import *


def test_spi_hardware_params(mock_factory):
    with patch('gpiozero.pins.local.SpiDev'):
        with mock_factory.spi() as device:
            assert isinstance(device, LocalPiHardwareSPI)
            assert repr(device) == 'SPI(port=0, device=0)'
            device.close()
            assert device.closed
            assert repr(device) == 'SPI(closed)'
        with mock_factory.spi(port=0, device=0) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(port=0, device=1) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(clock_pin=11) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(clock_pin=11, mosi_pin=10, select_pin=8) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(clock_pin=11, mosi_pin=10, select_pin=7) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        # Ensure we support "partial" SPI where we don't reserve a pin because
        # the device wants it for general IO (see SPI screens which use a pin
        # for data/commands)
        with mock_factory.spi(clock_pin=11, mosi_pin=10, miso_pin=None, select_pin=7) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(clock_pin=11, mosi_pin=None, miso_pin=9, select_pin=7) as device:
            assert isinstance(device, LocalPiHardwareSPI)
        with mock_factory.spi(shared=True) as device:
            assert isinstance(device, LocalPiHardwareSPIShared)
        with pytest.raises(ValueError):
            mock_factory.spi(port=1)
        with pytest.raises(ValueError):
            mock_factory.spi(device=2)
        with pytest.raises(ValueError):
            mock_factory.spi(port=0, clock_pin=12)
        with pytest.raises(ValueError):
            mock_factory.spi(foo='bar')

def test_spi_software_params(mock_factory):
    with patch('gpiozero.pins.local.SpiDev'):
        with mock_factory.spi(select_pin=6) as device:
            assert isinstance(device, LocalPiSoftwareSPI)
            assert repr(device) == 'SPI(clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=6)'
            device.close()
            assert device.closed
            assert repr(device) == 'SPI(closed)'
        with mock_factory.spi(clock_pin=11, mosi_pin=9, miso_pin=10) as device:
            assert isinstance(device, LocalPiSoftwareSPI)
            device._bus.close()
            assert device._bus.closed
            device.close()
            assert device.closed
        with mock_factory.spi(select_pin=6, shared=True) as device:
            assert isinstance(device, LocalPiSoftwareSPIShared)
    with patch('gpiozero.pins.local.SpiDev', None):
        # Clear out the old factory's caches (this is only necessary
        # because we're being naughty switching out patches)
        mock_factory.pins.clear()
        mock_factory._reservations.clear()
        # Ensure software fallback works when SpiDev isn't present
        with mock_factory.spi() as device:
            assert isinstance(device, LocalPiSoftwareSPI)

def test_spi_hardware_conflict(mock_factory):
    with patch('gpiozero.pins.local.SpiDev') as spidev:
        with LED(11) as led:
            with pytest.raises(GPIOPinInUse):
                mock_factory.spi(port=0, device=0)
    with patch('gpiozero.pins.local.SpiDev') as spidev:
        with mock_factory.spi(port=0, device=0) as spi:
            with pytest.raises(GPIOPinInUse):
                LED(11)

def test_spi_software_same_bus(mock_factory):
    with patch('gpiozero.pins.local.SpiDev'):
        with mock_factory.spi(select_pin=6) as device:
            with pytest.raises(GPIOPinInUse):
                mock_factory.spi(select_pin=6)
            with mock_factory.spi(select_pin=5) as another_device:
                assert device._bus is another_device._bus

def test_spi_software_shared_bus(mock_factory):
    with patch('gpiozero.pins.local.SpiDev'):
        with mock_factory.spi(select_pin=6, shared=True) as device:
            with mock_factory.spi(select_pin=6, shared=True) as another_device:
                assert device is another_device

def test_spi_hardware_read(mock_factory):
    with patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with mock_factory.spi() as device:
            assert device.read(3) == [0, 1, 2]
            assert device.read(6) == list(range(6))

def test_spi_hardware_write(mock_factory):
    with patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with mock_factory.spi() as device:
            assert device.write([0, 1, 2]) == 3
            assert spidev.return_value.xfer2.called_with([0, 1, 2])
            assert device.write(list(range(6))) == 6
            assert spidev.return_value.xfer2.called_with(list(range(6)))

def test_spi_hardware_modes(mock_factory):
    with patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.mode = 0
        spidev.return_value.lsbfirst = False
        spidev.return_value.cshigh = True
        spidev.return_value.bits_per_word = 8
        with mock_factory.spi() as device:
            assert device.clock_mode == 0
            assert not device.clock_polarity
            assert not device.clock_phase
            device.clock_polarity = False
            assert device.clock_mode == 0
            device.clock_polarity = True
            assert device.clock_mode == 2
            device.clock_phase = True
            assert device.clock_mode == 3
            assert not device.lsb_first
            assert device.select_high
            assert device.bits_per_word == 8
            device.select_high = False
            device.lsb_first = True
            device.bits_per_word = 12
            assert not spidev.return_value.cshigh
            assert spidev.return_value.lsbfirst
            assert spidev.return_value.bits_per_word == 12
            device.rate = 1000000
            assert device.rate == 1000000
            device.rate = 500000
            assert device.rate == 500000

def test_spi_software_read(mock_factory):
    class SPISlave(MockSPIDevice):
        def on_start(self):
            super(SPISlave, self).on_start()
            for i in range(10):
                self.tx_word(i)
    with patch('gpiozero.pins.local.SpiDev', None), \
            SPISlave(11, 10, 9, 8) as slave, \
            mock_factory.spi() as master:
        assert master.read(3) == [0, 1, 2]
        assert master.read(6) == [0, 1, 2, 3, 4, 5]
        slave.clock_phase = True
        master.clock_phase = True
        assert master.read(3) == [0, 1, 2]
        assert master.read(6) == [0, 1, 2, 3, 4, 5]

def test_spi_software_write(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None), \
            MockSPIDevice(11, 10, 9, 8) as test_device, \
            mock_factory.spi() as master:
        master.write([0])
        assert test_device.rx_word() == 0
        master.write([2, 0])
        # 0b 0000_0010 0000_0000
        assert test_device.rx_word() == 512
        master.write([0, 1, 1])
        # 0b 0000_0000 0000_0001 0000_0001
        assert test_device.rx_word() == 257

def test_spi_software_write_lsb_first(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None), \
            MockSPIDevice(11, 10, 9, 8, lsb_first=True) as test_device, \
            mock_factory.spi() as master:
        # lsb_first means the bit-strings above get reversed
        master.write([0])
        assert test_device.rx_word() == 0
        master.write([2, 0])
        # 0b 0000_0000 0100_0000
        assert test_device.rx_word() == 64
        master.write([0, 1, 1])
        # 0b 1000_0000 1000_0000 0000_0000
        assert test_device.rx_word() == 8421376

def test_spi_software_clock_mode(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None), \
            mock_factory.spi() as master:
        assert master.clock_mode == 0
        assert not master.clock_polarity
        assert not master.clock_phase
        master.clock_polarity = False
        assert master.clock_mode == 0
        master.clock_polarity = True
        assert master.clock_mode == 2
        master.clock_phase = True
        assert master.clock_mode == 3
        master.clock_mode = 0
        assert not master.clock_polarity
        assert not master.clock_phase
        with pytest.raises(ValueError):
            master.clock_mode = 5

def test_spi_software_attr(mock_factory):
    with patch('gpiozero.pins.local.SpiDev', None), \
            mock_factory.spi() as master:
        assert not master.lsb_first
        assert not master.select_high
        assert master.bits_per_word == 8
        master.bits_per_word = 12
        assert master.bits_per_word == 12
        master.lsb_first = True
        assert master.lsb_first
        master.select_high = True
        assert master.select_high
        with pytest.raises(ValueError):
            master.bits_per_word = 0


# XXX Test two simultaneous SPI devices sharing clock, MOSI, and MISO, with
# separate select pins (including threaded tests which attempt simultaneous
# reading/writing)
