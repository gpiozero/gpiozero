# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')


import operator
from threading import RLock

from ..devices import Device, SharedMixin
from ..input_devices import InputDevice
from ..output_devices import OutputDevice


class SPISoftwareBus(SharedMixin, Device):
    def __init__(self, clock_pin, mosi_pin, miso_pin):
        self.lock = None
        self.clock = None
        self.mosi = None
        self.miso = None
        super(SPISoftwareBus, self).__init__()
        self.lock = RLock()
        try:
            self.clock = OutputDevice(clock_pin, active_high=True)
            if mosi_pin is not None:
                self.mosi = OutputDevice(mosi_pin)
            if miso_pin is not None:
                self.miso = InputDevice(miso_pin)
        except:
            self.close()
            raise

    def close(self):
        super(SPISoftwareBus, self).close()
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
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin):
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
