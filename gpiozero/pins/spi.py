# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import operator
from threading import RLock

from . import SPI
from ..devices import Device, SharedMixin
from ..input_devices import InputDevice
from ..output_devices import OutputDevice
from ..exc import DeviceClosed, SPIInvalidClockMode


class SPISoftware(SPI):
    """
    A software bit-banged implementation of the :class:`gpiozero.pins.SPI`
    interface.

    This is a reasonable basis for a *local* SPI software implementation, but
    be aware that it's unlikely to be usable for remote operation (a dedicated
    daemon that locally handles SPI transactions should be used for such
    operations). Instances will happily share their clock, mosi, and miso pins
    with other instances provided each has a distinct select pin.

    See :class:`~gpiozero.pins.spi.SPISoftwareBus` for the actual SPI
    transfer logic.
    """
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin, *,
                 pin_factory):
        self._bus = None
        self._select = None
        super().__init__(pin_factory=pin_factory)
        try:
            # XXX We *should* be storing clock_mode locally, not clock_phase;
            # after all different users of the bus can disagree about the
            # clock's polarity and even select pin polarity
            self._clock_phase = False
            self._lsb_first = False
            self._bits_per_word = 8
            self._bus = SPISoftwareBus(
                clock_pin, mosi_pin, miso_pin, pin_factory=pin_factory)
            self._select = OutputDevice(
                select_pin, active_high=False, pin_factory=pin_factory)
        except:
            self.close()
            raise

    def _conflicts_with(self, other):
        if isinstance(other, SoftwareSPI):
            return self._select.pin.info.name == other._select.pin.info.name
        else:
            return True

    def close(self):
        if self._select:
            self._select.close()
        self._select = None
        if self._bus is not None:
            self._bus.close()
        self._bus = None
        super().close()

    @property
    def closed(self):
        return self._bus is None

    def __repr__(self):
        try:
            self._check_open()
            return (
                f'SPI(clock_pin={self._bus.clock.pin.info.name!r}, '
                f'mosi_pin={self._bus.mosi.pin.info.name!r}, '
                f'miso_pin={self._bus.miso.pin.info.name!r}, '
                f'select_pin={self._select.pin.info.name!r})')
        except DeviceClosed:
            return 'SPI(closed)'

    def transfer(self, data):
        with self._bus.lock:
            self._select.on()
            try:
                return self._bus.transfer(
                    data, self._clock_phase, self._lsb_first,
                    self._bits_per_word)
            finally:
                self._select.off()

    def _get_clock_mode(self):
        with self._bus.lock:
            return (not self._bus.clock.active_high) << 1 | self._clock_phase

    def _set_clock_mode(self, value):
        if not (0 <= value < 4):
            raise SPIInvalidClockMode(f"{value} is not a valid clock mode")
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
        return self._select.active_high

    def _set_select_high(self, value):
        with self._bus.lock:
            self._select.active_high = value
            self._select.off()


class SPISoftwareBus(SharedMixin, Device):
    """
    A software bit-banged SPI bus implementation, used by
    :class:`~gpiozero.pins.spi.SPISoftware` to implement shared SPI interfaces.

    .. warning::

        This implementation has no rate control; it simply clocks out data as
        fast as it can as Python isn't terribly quick on a Pi anyway, and the
        extra logic required for rate control is liable to reduce the maximum
        achievable data rate quite substantially.
    """
    def __init__(self, clock_pin, mosi_pin, miso_pin, *, pin_factory):
        self.lock = None
        self.clock = None
        self.mosi = None
        self.miso = None
        super().__init__()
        # XXX Should probably just use CompositeDevice for this; would make
        # close() a bit cleaner - any implications with the RLock?
        self.lock = RLock()
        try:
            self.clock = OutputDevice(
                clock_pin, active_high=True, pin_factory=pin_factory)
            if mosi_pin is not None:
                self.mosi = OutputDevice(mosi_pin, pin_factory=pin_factory)
            if miso_pin is not None:
                self.miso = InputDevice(miso_pin, pin_factory=pin_factory)
        except:
            self.close()
            raise

    def close(self):
        super().close()
        if getattr(self, 'lock', None):
            with self.lock:
                if self.miso is not None:
                    self.miso.close()
                    self.miso = None
                if self.mosi is not None:
                    self.mosi.close()
                    self.mosi = None
                if self.clock is not None:
                    self.clock.close()
                    self.clock = None
        self.lock = None

    @property
    def closed(self):
        return self.lock is None

    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, *, pin_factory=None):
        return (clock_pin, mosi_pin, miso_pin)

    def transfer(self, data, clock_phase=False, lsb_first=False, bits_per_word=8):
        """
        Writes data (a list of integer words where each word is assumed to have
        :attr:`bits_per_word` bits or less) to the SPI interface, and reads an
        equivalent number of words, returning them as a list of integers.
        """
        result = []
        with self.lock:
            # See https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
            # (specifically the section "Example of bit-banging the master
            # protocol") for a simpler C implementation of this which ignores
            # clock polarity, phase, variable word-size, and multiple input
            # words
            if lsb_first:
                shift = operator.lshift
                init_mask = 1
            else:
                shift = operator.rshift
                init_mask = 1 << (bits_per_word - 1)
            for write_word in data:
                mask = init_mask
                read_word = 0
                for _ in range(bits_per_word):
                    if self.mosi is not None:
                        self.mosi.value = bool(write_word & mask)
                    # read bit on clock activation
                    self.clock.on()
                    if not clock_phase:
                        if self.miso is not None and self.miso.value:
                            read_word |= mask
                    # read bit on clock deactivation
                    self.clock.off()
                    if clock_phase:
                        if self.miso is not None and self.miso.value:
                            read_word |= mask
                    mask = shift(mask, 1)
                result.append(read_word)
        return result
