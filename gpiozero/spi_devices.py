# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2016-2018 Ben Nuttall <ben@bennuttall.com>
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
    print_function,
    absolute_import,
    division,
    )
str = type('')


from math import log, ceil
from operator import or_
try:
    from functools import reduce
except ImportError:
    pass # py2's reduce is built-in

from .exc import DeviceClosed, SPIBadChannel, InputDeviceError
from .devices import Device


class SPIDevice(Device):
    """
    Extends :class:`Device`. Represents a device that communicates via the SPI
    protocol.

    See :ref:`spi_args` for information on the keyword arguments that can be
    specified with the constructor.
    """
    def __init__(self, **spi_args):
        self._spi = None
        super(SPIDevice, self).__init__(
            pin_factory=spi_args.pop('pin_factory', None)
        )
        self._spi = self.pin_factory.spi(**spi_args)

    def close(self):
        if getattr(self, '_spi', None):
            self._spi.close()
            self._spi = None
        super(SPIDevice, self).close()

    @property
    def closed(self):
        return self._spi is None

    def _int_to_words(self, pattern):
        """
        Given a bit-pattern expressed an integer number, return a sequence of
        the individual words that make up the pattern. The number of bits per
        word will be obtained from the internal SPI interface.
        """
        try:
            bits_required = int(ceil(log(pattern, 2))) + 1
        except ValueError:
            # pattern == 0 (technically speaking, no bits are required to
            # transmit the value zero ;)
            bits_required = 1
        shifts = range(0, bits_required, self._spi.bits_per_word)[::-1]
        mask = 2 ** self._spi.bits_per_word - 1
        return [(pattern >> shift) & mask for shift in shifts]

    def _words_to_int(self, words, expected_bits=None):
        """
        Given a sequence of words which each fit in the internal SPI
        interface's number of bits per word, returns the value obtained by
        concatenating each word into a single bit-string.

        If *expected_bits* is specified, it limits the size of the output to
        the specified number of bits (by masking off bits above the expected
        number). If unspecified, no limit will be applied.
        """
        if expected_bits is None:
            expected_bits = len(words) * self._spi.bits_per_word
        shifts = range(0, expected_bits, self._spi.bits_per_word)[::-1]
        mask = 2 ** expected_bits - 1
        return reduce(or_, (word << shift for word, shift in zip(words, shifts))) & mask

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.%s object using %r>" % (self.__class__.__name__, self._spi)
        except DeviceClosed:
            return "<gpiozero.%s object closed>" % self.__class__.__name__


class AnalogInputDevice(SPIDevice):
    """
    Represents an analog input device connected to SPI (serial interface).

    Typical analog input devices are `analog to digital converters`_ (ADCs).
    Several classes are provided for specific ADC chips, including
    :class:`MCP3004`, :class:`MCP3008`, :class:`MCP3204`, and :class:`MCP3208`.

    The following code demonstrates reading the first channel of an MCP3008
    chip attached to the Pi's SPI pins::

        from gpiozero import MCP3008

        pot = MCP3008(0)
        print(pot.value)

    The :attr:`value` attribute is normalized such that its value is always
    between 0.0 and 1.0 (or in special cases, such as differential sampling,
    -1 to +1). Hence, you can use an analog input to control the brightness of
    a :class:`PWMLED` like so::

        from gpiozero import MCP3008, PWMLED

        pot = MCP3008(0)
        led = PWMLED(17)
        led.source = pot

    The :attr:`voltage` attribute reports values between 0.0 and *max_voltage*
    (which defaults to 3.3, the logic level of the GPIO pins).

    .. _analog to digital converters: https://en.wikipedia.org/wiki/Analog-to-digital_converter
    """

    def __init__(self, bits, max_voltage=3.3, **spi_args):
        if bits is None:
            raise InputDeviceError('you must specify the bit resolution of the device')
        self._bits = bits
        self._min_value = -(2 ** bits)
        self._range = 2 ** (bits + 1) - 1
        if max_voltage <= 0:
            raise InputDeviceError('max_voltage must be positive')
        self._max_voltage = float(max_voltage)
        super(AnalogInputDevice, self).__init__(shared=True, **spi_args)

    @property
    def bits(self):
        """
        The bit-resolution of the device/channel.
        """
        return self._bits

    def _read(self):
        raise NotImplementedError

    @property
    def value(self):
        """
        The current value read from the device, scaled to a value between 0 and
        1 (or -1 to +1 for certain devices operating in differential mode).
        """
        return (2 * (self._read() - self._min_value) / self._range) - 1

    @property
    def raw_value(self):
        """
        The raw value as read from the device.
        """
        return self._read()

    @property
    def max_voltage(self):
        """
        The voltage required to set the device's value to 1.
        """
        return self._max_voltage

    @property
    def voltage(self):
        """
        The current voltage read from the device. This will be a value between
        0 and the *max_voltage* parameter specified in the constructor.
        """
        return self.value * self._max_voltage


class MCP3xxx(AnalogInputDevice):
    """
    Extends :class:`AnalogInputDevice` to implement an interface for all ADC
    chips with a protocol similar to the Microchip MCP3xxx series of devices.
    """

    def __init__(self, channel=0, bits=10, differential=False, max_voltage=3.3,
                 **spi_args):
        self._channel = channel
        self._differential = bool(differential)
        super(MCP3xxx, self).__init__(bits, max_voltage, **spi_args)

    @property
    def channel(self):
        """
        The channel to read data from. The MCP3008/3208/3304 have 8 channels
        (0-7), while the MCP3004/3204/3302 have 4 channels (0-3), the
        MCP3002/3202 have 2 channels (0-1), and the MCP3001/3201/3301 only
        have 1 channel.
        """
        return self._channel

    @property
    def differential(self):
        """
        If ``True``, the device is operated in differential mode. In this mode
        one channel (specified by the channel attribute) is read relative to
        the value of a second channel (implied by the chip's design).

        Please refer to the device data-sheet to determine which channel is
        used as the relative base value (for example, when using an
        :class:`MCP3008` in differential mode, channel 0 is read relative to
        channel 1).
        """
        return self._differential

    def _read(self):
        return self._words_to_int(
            self._spi.transfer(self._send())[-2:], self.bits
            )

    def _send(self):
        # MCP3004/08 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   00000001 MCCCxxxx xxxxxxxx
        #     Rx   xxxxxxxx xxxxx0RR RRRRRRRR
        #
        # MCP3204/08 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   000001MC CCxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx xxx0RRRR RRRRRRRR
        #
        # The transmit bits start with several preamble "0" bits, the number
        # of which is determined by the amount required to align the last byte
        # of the result with the final byte of output. A start "1" bit is then
        # transmitted, followed by the single/differential bit (M); 1 for
        # single-ended read, 0 for differential read. Next comes three bits for
        # channel (C).
        #
        # Read-out begins with a don't care bit (x), then a null bit (0)
        # followed by the result bits (R). All other bits are don't care (x).
        #
        # The 3x01 variant of the chips always operates in differential mode
        # and effectively only has one channel (composed of an IN+ and IN-). As
        # such it requires no input, just output.
        return self._int_to_words(
            (0b10000 | (not self.differential) << 3 | self.channel) << (self.bits + 2)
            )


class MCP3xx2(MCP3xxx):
    def _send(self):
        # MCP3002 protocol looks like the following:
        #
        #     Byte        0        1
        #     ==== ======== ========
        #     Tx   01MCLxxx xxxxxxxx
        #     Rx   xxxxx0RR RRRRRRRR for the 3002
        #
        # MCP3202 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   00000001 MCLxxxxx xxxxxxxx
        #     Rx   xxxxxxxx xxx0RRRR RRRRRRRR
        #
        # The transmit bits start with several preamble "0" bits, the number of
        # which is determined by the amount required to align the last byte of
        # the result with the final byte of output. A start "1" bit is then
        # transmitted, followed by the single/differential bit (M); 1 for
        # single-ended read, 0 for differential read. Next comes a single bit
        # for channel (C) then the MSBF bit (L) which selects whether the data
        # will be read out in MSB form only (1) or whether LSB read-out will
        # occur after MSB read-out (0).
        #
        # Read-out begins with a null bit (0) followed by the result bits (R).
        # All other bits are don't care (x).
        return self._int_to_words(
            (0b1001 | (not self.differential) << 2 | self.channel << 1) << (self.bits + 1)
            )


class MCP30xx(MCP3xxx):
    """
    Extends :class:`MCP3xxx` to implement an interface for all ADC
    chips with a protocol similar to the Microchip MCP30xx series of devices.
    """

    def __init__(self, channel=0, differential=False, max_voltage=3.3,
                 **spi_args):
        super(MCP30xx, self).__init__(channel, 10, differential, max_voltage,
                                      **spi_args)


class MCP32xx(MCP3xxx):
    """
    Extends :class:`MCP3xxx` to implement an interface for all ADC
    chips with a protocol similar to the Microchip MCP32xx series of devices.
    """

    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        super(MCP32xx, self).__init__(channel, 12, differential, max_voltage,
                                      **spi_args)


class MCP33xx(MCP3xxx):
    """
    Extends :class:`MCP3xxx` with functionality specific to the MCP33xx family
    of ADCs; specifically this handles the full differential capability of
    these chips supporting the full 13-bit signed range of output values.
    """

    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        super(MCP33xx, self).__init__(channel, 12, differential, max_voltage,
                                      **spi_args)

    def _read(self):
        if self.differential:
            result = self._words_to_int(
                self._spi.transfer(self._send())[-2:], self.bits + 1)
            # Account for the sign bit
            if result > 4095:
                return -(8192 - result)
            else:
                return result
        else:
            return super(MCP33xx, self)._read()

    def _send(self):
        # MCP3302/04 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   00001MCC Cxxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx xx0SRRRR RRRRRRRR
        #
        # The transmit bits start with 4 preamble bits "0000", a start bit "1"
        # followed by the single/differential bit (M) which is 1 for
        # single-ended read, and 0 for differential read, followed by 3-bits
        # for the channel (C). The remainder of the transmission are "don't
        # care" bits (x).
        #
        # The first byte received and the top 2 bits of the second byte are
        # don't care bits (x). These are followed by a null bit (0), then the
        # sign bit (S), and then the 12 result bits (R).
        #
        # In single read mode (the default) the sign bit is always zero and the
        # result is effectively 12-bits. In differential mode, the sign bit is
        # significant and the result is a two's-complement 13-bit value.
        #
        # The MCP3301 variant operates similarly to the other MCP3x01 variants;
        # no input, just output and always differential.
        return self._int_to_words(
            (0b10000 | (not self.differential) << 3 | self.channel) << (self.bits + 3)
            )

    @property
    def differential(self):
        """
        If ``True``, the device is operated in differential mode. In this mode
        one channel (specified by the channel attribute) is read relative to
        the value of a second channel (implied by the chip's design).

        Please refer to the device data-sheet to determine which channel is
        used as the relative base value (for example, when using an
        :class:`MCP3304` in differential mode, channel 0 is read relative to
        channel 1).
        """
        return super(MCP33xx, self).differential

    @property
    def value(self):
        """
        The current value read from the device, scaled to a value between 0 and
        1 (or -1 to +1 for devices operating in differential mode).
        """
        return super(MCP33xx, self).value


class MCP3001(MCP30xx):
    """
    The `MCP3001`_ is a 10-bit analog to digital converter with 1 channel.
    Please note that the MCP3001 always operates in differential mode,
    measuring the value of IN+ relative to IN-.

    .. _MCP3001: http://www.farnell.com/datasheets/630400.pdf
    """
    def __init__(self, max_voltage=3.3, **spi_args):
        super(MCP3001, self).__init__(0, True, max_voltage, **spi_args)

    def _read(self):
        # MCP3001 protocol looks like the following:
        #
        #     Byte        0        1
        #     ==== ======== ========
        #     Rx   xx0RRRRR RRRRRxxx
        return self._words_to_int(self._spi.read(2), 13) >> 3


class MCP3002(MCP30xx, MCP3xx2):
    """
    The `MCP3002`_ is a 10-bit analog to digital converter with 2 channels
    (0-1).

    .. _MCP3002: http://www.farnell.com/datasheets/1599363.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 2:
            raise SPIBadChannel('channel must be 0 or 1')
        super(MCP3002, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3004(MCP30xx):
    """
    The `MCP3004`_ is a 10-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3004: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 4:
            raise SPIBadChannel('channel must be between 0 and 3')
        super(MCP3004, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3008(MCP30xx):
    """
    The `MCP3008`_ is a 10-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3008: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 8:
            raise SPIBadChannel('channel must be between 0 and 7')
        super(MCP3008, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3201(MCP32xx):
    """
    The `MCP3201`_ is a 12-bit analog to digital converter with 1 channel.
    Please note that the MCP3201 always operates in differential mode,
    measuring the value of IN+ relative to IN-.

    .. _MCP3201: http://www.farnell.com/datasheets/1669366.pdf
    """
    def __init__(self, max_voltage=3.3, **spi_args):
        super(MCP3201, self).__init__(0, True, max_voltage, **spi_args)

    def _read(self):
        # MCP3201 protocol looks like the following:
        #
        #     Byte        0        1
        #     ==== ======== ========
        #     Rx   xx0RRRRR RRRRRRRx
        return self._words_to_int(self._spi.read(2), 13) >> 1


class MCP3202(MCP32xx, MCP3xx2):
    """
    The `MCP3202`_ is a 12-bit analog to digital converter with 2 channels
    (0-1).

    .. _MCP3202: http://www.farnell.com/datasheets/1669376.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 2:
            raise SPIBadChannel('channel must be 0 or 1')
        super(MCP3202, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3204(MCP32xx):
    """
    The `MCP3204`_ is a 12-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3204: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 4:
            raise SPIBadChannel('channel must be between 0 and 3')
        super(MCP3204, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3208(MCP32xx):
    """
    The `MCP3208`_ is a 12-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3208: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 8:
            raise SPIBadChannel('channel must be between 0 and 7')
        super(MCP3208, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3301(MCP33xx):
    """
    The `MCP3301`_ is a signed 13-bit analog to digital converter.  Please note
    that the MCP3301 always operates in differential mode measuring the
    difference between IN+ and IN-. Its output value is scaled from -1 to +1.

    .. _MCP3301: http://www.farnell.com/datasheets/1669397.pdf
    """
    def __init__(self, max_voltage=3.3, **spi_args):
        super(MCP3301, self).__init__(0, True, max_voltage, **spi_args)

    def _read(self):
        # MCP3301 protocol looks like the following:
        #
        #     Byte        0        1
        #     ==== ======== ========
        #     Rx   xx0SRRRR RRRRRRRR
        result = self._words_to_int(self._spi.read(2), 13)
        # Account for the sign bit
        if result > 4095:
            return -(8192 - result)
        else:
            return result


class MCP3302(MCP33xx):
    """
    The `MCP3302`_ is a 12/13-bit analog to digital converter with 4 channels
    (0-3). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3302: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 4:
            raise SPIBadChannel('channel must be between 0 and 4')
        super(MCP3302, self).__init__(channel, differential, max_voltage, **spi_args)


class MCP3304(MCP33xx):
    """
    The `MCP3304`_ is a 12/13-bit analog to digital converter with 8 channels
    (0-7). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3304: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, differential=False, max_voltage=3.3, **spi_args):
        if not 0 <= channel < 8:
            raise SPIBadChannel('channel must be between 0 and 7')
        super(MCP3304, self).__init__(channel, differential, max_voltage, **spi_args)
