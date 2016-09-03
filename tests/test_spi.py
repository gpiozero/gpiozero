from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import sys
import mock
import pytest
from collections import namedtuple

from gpiozero import *
from gpiozero.pins.mock import MockPin, MockSPIDevice
from gpiozero.spi import *


def setup_function(function):
    import gpiozero.devices
    gpiozero.devices.pin_factory = MockPin

def teardown_function(function):
    MockPin.clear_pins()


def test_spi_hardware_params():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        with SPI() as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(port=0, device=0) as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(port=0, device=1) as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(clock_pin=11) as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(clock_pin=11, mosi_pin=10, select_pin=8) as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(clock_pin=11, mosi_pin=10, select_pin=7) as device:
            assert isinstance(device, SPIHardwareInterface)
        with SPI(shared=True) as device:
            assert isinstance(device, SharedSPIHardwareInterface)
        with pytest.raises(ValueError):
            SPI(port=1)
        with pytest.raises(ValueError):
            SPI(device=2)
        with pytest.raises(ValueError):
            SPI(port=0, clock_pin=12)
        with pytest.raises(ValueError):
            SPI(foo='bar')

def test_spi_software_params():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        with SPI(select_pin=6) as device:
            assert isinstance(device, SPISoftwareInterface)
        with SPI(clock_pin=11, mosi_pin=9, miso_pin=10) as device:
            assert isinstance(device, SPISoftwareInterface)
        with SPI(select_pin=6, shared=True) as device:
            assert isinstance(device, SharedSPISoftwareInterface)
    # Ensure software fallback works when SpiDev isn't present
    with SPI() as device:
        assert isinstance(device, SPISoftwareInterface)

def test_spi_hardware_conflict():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        with LED(11) as led:
            with pytest.raises(GPIOPinInUse):
                SPI(port=0, device=0)

def test_spi_hardware_read():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with SPI() as device:
            assert device.read(3) == [0, 1, 2]
            assert device.read(6) == list(range(6))

def test_spi_hardware_write():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with SPI() as device:
            assert device.write([0, 1, 2]) == 3
            assert spidev.return_value.xfer2.called_with([0, 1, 2])
            assert device.write(list(range(6))) == 6
            assert spidev.return_value.xfer2.called_with(list(range(6)))

def test_spi_hardware_modes():
    with mock.patch('gpiozero.spi.SpiDev') as spidev:
        spidev.return_value.mode = 0
        spidev.return_value.lsbfirst = False
        spidev.return_value.cshigh = True
        spidev.return_value.bits_per_word = 8
        with SPI() as device:
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

def test_spi_software_read():
    class SPISlave(MockSPIDevice):
        def on_start(self):
            super(SPISlave, self).on_start()
            for i in range(10):
                self.tx_word(i)
    with SPISlave(11, 10, 9, 8) as slave, SPI() as master:
        assert master.read(3) == [0, 1, 2]
        assert master.read(6) == [0, 1, 2, 3, 4, 5]
        slave.clock_phase = True
        master.clock_phase = True
        assert master.read(3) == [0, 1, 2]
        assert master.read(6) == [0, 1, 2, 3, 4, 5]

def test_spi_software_write():
    with MockSPIDevice(11, 10, 9, 8) as test_device, SPI() as master:
        master.write([0])
        assert test_device.rx_word() == 0
        master.write([2, 0])
        assert test_device.rx_word() == 512
        master.write([0, 1, 1])
        assert test_device.rx_word() == 257

def test_spi_software_clock_mode():
    with SPI() as master:
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

def test_spi_software_attr():
    with SPI() as master:
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
