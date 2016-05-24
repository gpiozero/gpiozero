from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')


from .exc import DeviceClosed, InputDeviceError
from .devices import Device
from .spi import SPI


class SPIDevice(Device):
    """
    Extends :class:`Device`. Represents a device that communicates via the SPI
    protocol.

    See :ref:`spi_args` for information on the keyword arguments that can be
    specified with the constructor.
    """
    def __init__(self, **spi_args):
        self._spi = SPI(**spi_args)

    def close(self):
        if self._spi:
            s = self._spi
            self._spi = None
            s.close()
        super(SPIDevice, self).close()

    @property
    def closed(self):
        return self._spi is None

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
        led.source = pot.values

    .. _analog to digital converters: https://en.wikipedia.org/wiki/Analog-to-digital_converter
    """

    def __init__(self, bits=None, **spi_args):
        if bits is None:
            raise InputDeviceError('you must specify the bit resolution of the device')
        self._bits = bits
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
        1 (or -1 to +1 for devices operating in differential mode).
        """
        return self._read() / (2**self.bits - 1)

    @property
    def raw_value(self):
        """
        The raw value as read from the device.
        """
        return self._read()


class MCP3xxx(AnalogInputDevice):
    """
    Extends :class:`AnalogInputDevice` to implement an interface for all ADC
    chips with a protocol similar to the Microchip MCP3xxx series of devices.
    """

    def __init__(self, channel=0, bits=10, differential=False, **spi_args):
        self._channel = channel
        self._differential = bool(differential)
        super(MCP3xxx, self).__init__(bits, **spi_args)

    @property
    def channel(self):
        """
        The channel to read data from. The MCP3008/3208/3304 have 8 channels
        (0-7), while the MCP3004/3204/3302 have 4 channels (0-3), and the
        MCP3301 only has 1 channel.
        """
        return self._channel

    @property
    def differential(self):
        """
        If ``True``, the device is operated in pseudo-differential mode. In
        this mode one channel (specified by the channel attribute) is read
        relative to the value of a second channel (implied by the chip's
        design).

        Please refer to the device data-sheet to determine which channel is
        used as the relative base value (for example, when using an
        :class:`MCP3008` in differential mode, channel 0 is read relative to
        channel 1).
        """
        return self._differential

    def _read(self):
        # MCP3008/04 or MCP3208/04 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   0001MCCC xxxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx x0RRRRRR RRRRxxxx for the 3004/08
        #     Rx   xxxxxxxx x0RRRRRR RRRRRRxx for the 3204/08
        #
        # The transmit bits start with 3 preamble bits "000" (to warm up), a
        # start bit "1" followed by the single/differential bit (M) which is 1
        # for single-ended read, and 0 for differential read, followed by
        # 3-bits for the channel (C). The remainder of the transmission are
        # "don't care" bits (x).
        #
        # The first byte received and the top 1 bit of the second byte are
        # don't care bits (x). These are followed by a null bit (0), and then
        # the result bits (R). 10 bits for the MCP300x, 12 bits for the
        # MCP320x.
        #
        # XXX Differential mode still requires testing
        data = self._spi.transfer([16 + [8, 0][self.differential] + self.channel, 0, 0])
        return ((data[1] & 63) << (self.bits - 6)) | (data[2] >> (14 - self.bits))


class MCP33xx(MCP3xxx):
    """
    Extends :class:`MCP3xxx` with functionality specific to the MCP33xx family
    of ADCs; specifically this handles the full differential capability of
    these chips supporting the full 13-bit signed range of output values.
    """

    def __init__(self, channel=0, differential=False, **spi_args):
        super(MCP33xx, self).__init__(channel, 12, differential, **spi_args)

    def _read(self):
        # MCP3304/02 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   0001MCCC xxxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx x0SRRRRR RRRRRRRx
        #
        # The transmit bits start with 3 preamble bits "000" (to warm up), a
        # start bit "1" followed by the single/differential bit (M) which is 1
        # for single-ended read, and 0 for differential read, followed by
        # 3-bits for the channel (C). The remainder of the transmission are
        # "don't care" bits (x).
        #
        # The first byte received and the top 1 bit of the second byte are
        # don't care bits (x). These are followed by a null bit (0), then the
        # sign bit (S), and then the 12 result bits (R).
        #
        # In single read mode (the default) the sign bit is always zero and the
        # result is effectively 12-bits. In differential mode, the sign bit is
        # significant and the result is a two's-complement 13-bit value.
        #
        # The MCP3301 variant of the chip always operates in differential
        # mode and effectively only has one channel (composed of an IN+ and
        # IN-). As such it requires no input, just output. This is the reason
        # we split out _send() below; so that MCP3301 can override it.
        data = self._spi.transfer(self._send())
        # Extract the last two bytes (again, for MCP3301)
        data = data[-2:]
        result = ((data[0] & 63) << 7) | (data[1] >> 1)
        # Account for the sign bit
        if self.differential and result > 4095:
            result = -(8192 - result)
        assert -4096 <= result < 4096
        return result

    def _send(self):
        return [16 + [8, 0][self.differential] + self.channel, 0, 0]


class MCP3001(MCP3xxx):
    """
    The `MCP3001`_ is a 10-bit analog to digital converter with 1 channel

    .. _MCP3001: http://www.farnell.com/datasheets/630400.pdf
    """
    def __init__(self, **spi_args):
        super(MCP3001, self).__init__(0, 10, differential=True, **spi_args)


class MCP3002(MCP3xxx):
    """
    The `MCP3002`_ is a 10-bit analog to digital converter with 2 channels
    (0-1).

    .. _MCP3002: http://www.farnell.com/datasheets/1599363.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 2:
            raise InputDeviceError('channel must be 0 or 1')
        super(MCP3002, self).__init__(channel, 10, differential, **spi_args)


class MCP3004(MCP3xxx):
    """
    The `MCP3004`_ is a 10-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3004: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 3')
        super(MCP3004, self).__init__(channel, 10, differential, **spi_args)


class MCP3008(MCP3xxx):
    """
    The `MCP3008`_ is a 10-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3008: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3008, self).__init__(channel, 10, differential, **spi_args)


class MCP3201(MCP3xxx):
    """
    The `MCP3201`_ is a 12-bit analog to digital converter with 1 channel

    .. _MCP3201: http://www.farnell.com/datasheets/1669366.pdf
    """
    def __init__(self, **spi_args):
        super(MCP3201, self).__init__(0, 12, differential=True, **spi_args)


class MCP3202(MCP3xxx):
    """
    The `MCP3202`_ is a 12-bit analog to digital converter with 2 channels
    (0-1).

    .. _MCP3202: http://www.farnell.com/datasheets/1669376.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 2:
            raise InputDeviceError('channel must be 0 or 1')
        super(MCP3202, self).__init__(channel, 12, differential, **spi_args)


class MCP3204(MCP3xxx):
    """
    The `MCP3204`_ is a 12-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3204: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 3')
        super(MCP3204, self).__init__(channel, 12, differential, **spi_args)


class MCP3208(MCP3xxx):
    """
    The `MCP3208`_ is a 12-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3208: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3208, self).__init__(channel, 12, differential, **spi_args)


class MCP3301(MCP33xx):
    """
    The `MCP3301`_ is a signed 13-bit analog to digital converter.  Please note
    that the MCP3301 always operates in differential mode between its two
    channels and the output value is scaled from -1 to +1.

    .. _MCP3301: http://www.farnell.com/datasheets/1669397.pdf
    """
    def __init__(self, **spi_args):
        super(MCP3301, self).__init__(0, differential=True, **spi_args)

    def _send(self):
        return [0, 0]


class MCP3302(MCP33xx):
    """
    The `MCP3302`_ is a 12/13-bit analog to digital converter with 4 channels
    (0-3). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3302: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 4')
        super(MCP3302, self).__init__(channel, differential, **spi_args)


class MCP3304(MCP33xx):
    """
    The `MCP3304`_ is a 12/13-bit analog to digital converter with 8 channels
    (0-7). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3304: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, differential=False, **spi_args):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3304, self).__init__(channel, differential, **spi_args)

