# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import io
import errno
import struct
from collections import defaultdict
from threading import Lock
from time import monotonic

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None

from . import SPI
from .pi import PiFactory, PiPin, SPI_HARDWARE_PINS, spi_port_device
from .spi import SPISoftware
from ..devices import Device
from ..mixins import SharedMixin
from ..output_devices import OutputDevice
from ..exc import DeviceClosed, PinUnknownPi, SPIInvalidClockMode


def get_pi_revision():
    revision = None
    try:
        with io.open('/proc/device-tree/system/linux,revision', 'rb') as f:
            revision = hex(struct.unpack('>L', f.read(4))[0])[2:]
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise e
        with io.open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    revision = line.split(':')[1].strip().lower()
    if revision is not None:
        overvolted = revision.startswith('100')
        if overvolted:
            revision = revision[-4:]
        return int(revision, base=16)
    raise PinUnknownPi(
        'unable to locate Pi revision in /proc/device-tree or /proc/cpuinfo')


class LocalPiFactory(PiFactory):
    """
    Extends :class:`~gpiozero.pins.pi.PiFactory`. Abstract base class
    representing pins attached locally to a Pi. This forms the base class for
    local-only pin interfaces (:class:`~gpiozero.pins.rpigpio.RPiGPIOPin`,
    :class:`~gpiozero.pins.lgpio.LGPIOPin`, and
    :class:`~gpiozero.pins.native.NativePin`).
    """
    pins = {}
    _reservations = defaultdict(list)
    _res_lock = Lock()

    def __init__(self):
        super().__init__()
        # Override the reservations and pins dict to be this class' attributes.
        # This is a bit of a dirty hack, but ensures that anyone evil enough to
        # mix pin implementations doesn't try and control the same pin with
        # different backends
        self.pins = LocalPiFactory.pins
        self._reservations = LocalPiFactory._reservations
        self._res_lock = LocalPiFactory._res_lock

    def _get_revision(self):
        return get_pi_revision()

    def _get_spi_class(self, shared, hardware):
        return {
            (False, True):  LocalPiHardwareSPI,
            (True,  True):  LocalPiHardwareSPIShared,
            (False, False): LocalPiSoftwareSPI,
            (True,  False): LocalPiSoftwareSPIShared,
            }[shared, hardware]

    @staticmethod
    def ticks():
        return monotonic()

    @staticmethod
    def ticks_diff(later, earlier):
        return later - earlier


class LocalPiPin(PiPin):
    """
    Extends :class:`~gpiozero.pins.pi.PiPin`. Abstract base class representing
    a multi-function GPIO pin attached to the local Raspberry Pi.
    """
    def _call_when_changed(self, ticks=None, state=None):
        """
        Overridden to provide default ticks from the local Pi factory.

        .. warning::

            The local pin factory uses a seconds-based monotonic value for
            its ticks but you *must not* rely upon this behaviour. Ticks are
            an opaque value that should only be compared with the associated
            :meth:`Factory.ticks_diff` method.
        """
        super()._call_when_changed(
            self._factory.ticks() if ticks is None else ticks,
            self.state if state is None else state)


class LocalPiHardwareSPI(SPI):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, pin_factory):
        self._port, self._device = spi_port_device(
            clock_pin, mosi_pin, miso_pin, select_pin)
        self._bus = None
        if SpiDev is None:
            raise ImportError('failed to import spidev')
        super().__init__(pin_factory=pin_factory)
        to_reserve = {clock_pin, select_pin}
        if mosi_pin is not None:
            to_reserve.add(mosi_pin)
        if miso_pin is not None:
            to_reserve.add(miso_pin)
        self.pin_factory.reserve_pins(self, *to_reserve)
        self._bus = SpiDev()
        self._bus.open(self._port, self._device)
        self._bus.max_speed_hz = 500000

    def _conflicts_with(self, other):
        if isinstance(other, LocalPiHardwareSPI):
            return (
                (self._port == other._port) and
                (self._device == other._device))
        else:
            return True

    def close(self):
        if self._bus is not None:
            self._bus.close()
        self._bus = None
        self.pin_factory.release_all(self)
        super().close()

    @property
    def closed(self):
        return self._bus is None

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
        return self._bus.xfer2(data)

    def _get_clock_mode(self):
        return self._bus.mode

    def _set_clock_mode(self, value):
        self._bus.mode = value

    def _get_lsb_first(self):
        return self._bus.lsbfirst

    def _set_lsb_first(self, value):
        self._bus.lsbfirst = bool(value)

    def _get_select_high(self):
        return self._bus.cshigh

    def _set_select_high(self, value):
        self._bus.cshigh = bool(value)

    def _get_bits_per_word(self):
        return self._bus.bits_per_word

    def _set_bits_per_word(self, value):
        self._bus.bits_per_word = value

    def _get_rate(self):
        return self._bus.max_speed_hz

    def _set_rate(self, value):
        self._bus.max_speed_hz = int(value)


class LocalPiSoftwareSPI(SPISoftware):
    pass


class LocalPiHardwareSPIShared(SharedMixin, LocalPiHardwareSPI):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin,
                    pin_factory):
        return (clock_pin, select_pin)


class LocalPiSoftwareSPIShared(SharedMixin, LocalPiSoftwareSPI):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin,
                    pin_factory):
        return (clock_pin, select_pin)
