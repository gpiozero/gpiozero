from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import io
import weakref
import warnings

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None

from . import SPI
from .pi import PiFactory, PiPin
from .spi import SPISoftwareBus
from ..devices import Device, SharedMixin
from ..output_devices import OutputDevice
from ..exc import DeviceClosed, PinUnknownPi, SPIInvalidClockMode


class LocalPiFactory(PiFactory):
    """
    Abstract base class representing pins attached locally to a Pi. This forms
    the base class for local-only pin interfaces (:class:`RPiGPIOPin`,
    :class:`RPIOPin`, and :class:`NativePin`).
    """
    pins = {}

    def __init__(self):
        super(LocalPiFactory, self).__init__()
        self.spi_hardware_class = LocalPiHardwareSPI
        self.spi_software_class = LocalPiSoftwareSPI
        self.shared_spi_hardware_class = LocalPiHardwareSPIShared
        self.shared_spi_software_class = LocalPiSoftwareSPIShared
        # Override the pins dict to be this class' pins dict. This is a bit of
        # a dirty hack, but ensures that anyone evil enough to mix pin
        # implementations doesn't try and control the same pin with different
        # backends
        self.pins = LocalPiFactory.pins

    def _get_address(self):
        return ('localhost',)

    def _get_revision(self):
        # Cache the result as we can reasonably assume it won't change during
        # runtime (this is LocalPin after all; descendents that deal with
        # remote Pis should inherit from Pin instead)
        with io.open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    revision = line.split(':')[1].strip().lower()
                    overvolted = revision.startswith('100')
                    if overvolted:
                        revision = revision[-4:]
                    return revision
        raise PinUnknownPi('unable to locate Pi revision in /proc/cpuinfo')


class LocalPiPin(PiPin):
    """
    Abstract base class representing a multi-function GPIO pin attached to the
    local Raspberry Pi.
    """
    pass


class LocalPiHardwareSPI(SPI, Device):
    def __init__(self, factory, port, device):
        if SpiDev is None:
            raise ImportError('failed to import spidev')
        self._port = port
        self._device = device
        self._intf = None
        self._address = factory.address + ('SPI(port=%d, device=%d)' % (port, device),)
        super(LocalPiHardwareSPI, self).__init__()
        self._reserve_pins(
            factory.pin_address(11),
            factory.pin_address(10),
            factory.pin_address(9),
            factory.pin_address((8, 7)[device])
            )
        self._intf = SpiDev()
        self._intf.open(port, device)
        self._intf.max_speed_hz = 500000

    def _conflicts_with(self, other):
        return not (
            isinstance(other, LocalPiHardwareSPI) and
            (self._port, self._device) != (other._port, other._device)
            )

    def close(self):
        if self._intf:
            try:
                self._intf.close()
            finally:
                self._intf = None
        self._release_all()
        super(LocalPiHardwareSPI, self).close()

    @property
    def closed(self):
        return self._intf is None

    def __repr__(self):
        try:
            self._check_open()
            return 'SPI(port=%d, device=%d)' % (self._port, self._device)
        except DeviceClosed:
            return 'SPI(closed)'

    def transfer(self, data):
        """
        Writes data (a list of integer words where each word is assumed to have
        :attr:`bits_per_word` bits or less) to the SPI interface, and reads an
        equivalent number of words, returning them as a list of integers.
        """
        return self._intf.xfer2(data)

    def _get_clock_mode(self):
        return self._intf.mode

    def _set_clock_mode(self, value):
        self._intf.mode = value

    def _get_lsb_first(self):
        return self._intf.lsbfirst

    def _set_lsb_first(self, value):
        self._intf.lsbfirst = bool(value)

    def _get_select_high(self):
        return self._intf.cshigh

    def _set_select_high(self, value):
        self._intf.cshigh = bool(value)

    def _get_bits_per_word(self):
        return self._intf.bits_per_word

    def _set_bits_per_word(self, value):
        self._intf.bits_per_word = value


class LocalPiSoftwareSPI(SPI, OutputDevice):
    def __init__(self, factory, clock_pin, mosi_pin, miso_pin, select_pin):
        self._bus = None
        self._address = factory.address + (
            'SPI(clock_pin=%d, mosi_pin=%d, miso_pin=%d, select_pin=%d)' % (
            clock_pin, mosi_pin, miso_pin, select_pin),
            )
        super(LocalPiSoftwareSPI, self).__init__(select_pin, active_high=False)
        try:
            self._clock_phase = False
            self._lsb_first = False
            self._bits_per_word = 8
            self._bus = SPISoftwareBus(clock_pin, mosi_pin, miso_pin)
        except:
            self.close()
            raise

    def close(self):
        if self._bus:
            self._bus.close()
            self._bus = None
        super(LocalPiSoftwareSPI, self).close()

    @property
    def closed(self):
        return self._bus is None

    def __repr__(self):
        try:
            self._check_open()
            return 'SPI(clock_pin=%d, mosi_pin=%d, miso_pin=%d, select_pin=%d)' % (
                self._bus.clock.pin.number,
                self._bus.mosi.pin.number,
                self._bus.miso.pin.number,
                self.pin.number)
        except DeviceClosed:
            return 'SPI(closed)'

    def transfer(self, data):
        with self._bus.lock:
            self.on()
            try:
                return self._bus.transfer(
                    data, self._clock_phase, self._lsb_first, self._bits_per_word)
            finally:
                self.off()

    def _get_clock_mode(self):
        with self._bus.lock:
            return (not self._bus.clock.active_high) << 1 | self._clock_phase

    def _set_clock_mode(self, value):
        if not (0 <= value < 4):
            raise SPIInvalidClockMode("%d is not a valid clock mode" % value)
        with self._bus.lock:
            self._bus.clock.active_high = not (value & 2)
            self._clock_phase = bool(value & 1)

    def _get_lsb_first(self):
        return self._lsb_first

    def _set_lsb_first(self, value):
        self._lsb_first = bool(value)

    def _get_bits_per_word(self):
        return self._bits_per_word

    def _set_bits_per_word(self, value):
        if value < 1:
            raise ValueError('bits_per_word must be positive')
        self._bits_per_word = int(value)

    def _get_select_high(self):
        return self.active_high

    def _set_select_high(self, value):
        with self._bus.lock:
            self.active_high = value
            self.off()


class LocalPiHardwareSPIShared(SharedMixin, LocalPiHardwareSPI):
    @classmethod
    def _shared_key(cls, factory, port, device):
        return (port, device)


class LocalPiSoftwareSPIShared(SharedMixin, LocalPiSoftwareSPI):
    @classmethod
    def _shared_key(cls, factory, clock_pin, mosi_pin, miso_pin, select_pin):
        return (select_pin,)

