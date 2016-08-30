from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import io
from collections import namedtuple

from ..exc import PinUnknownPi, PinMultiplePins, PinNoPins


# Some useful constants for describing pins

V1_8   = '1V8'
V3_3   = '3V3'
V5     = '5V'
GND    = 'GND'
NC     = 'NC' # not connected
GPIO0  = 'GPIO0'
GPIO1  = 'GPIO1'
GPIO2  = 'GPIO2'
GPIO3  = 'GPIO3'
GPIO4  = 'GPIO4'
GPIO5  = 'GPIO5'
GPIO6  = 'GPIO6'
GPIO7  = 'GPIO7'
GPIO8  = 'GPIO8'
GPIO9  = 'GPIO9'
GPIO10 = 'GPIO10'
GPIO11 = 'GPIO11'
GPIO12 = 'GPIO12'
GPIO13 = 'GPIO13'
GPIO14 = 'GPIO14'
GPIO15 = 'GPIO15'
GPIO16 = 'GPIO16'
GPIO17 = 'GPIO17'
GPIO18 = 'GPIO18'
GPIO19 = 'GPIO19'
GPIO20 = 'GPIO20'
GPIO21 = 'GPIO21'
GPIO22 = 'GPIO22'
GPIO23 = 'GPIO23'
GPIO24 = 'GPIO24'
GPIO25 = 'GPIO25'
GPIO26 = 'GPIO26'
GPIO27 = 'GPIO27'
GPIO28 = 'GPIO28'
GPIO29 = 'GPIO29'
GPIO30 = 'GPIO30'
GPIO31 = 'GPIO31'
GPIO32 = 'GPIO32'
GPIO33 = 'GPIO33'
GPIO34 = 'GPIO34'
GPIO35 = 'GPIO35'
GPIO36 = 'GPIO36'
GPIO37 = 'GPIO37'
GPIO38 = 'GPIO38'
GPIO39 = 'GPIO39'
GPIO40 = 'GPIO40'
GPIO41 = 'GPIO41'
GPIO42 = 'GPIO42'
GPIO43 = 'GPIO43'
GPIO44 = 'GPIO44'
GPIO45 = 'GPIO45'

# Pin maps for various board revisions and headers

REV1_P1 = {
#   pin  func  pullup  pin  func  pullup
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO0,  True),  4:  (V5,     False),
    5:  (GPIO1,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO21, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    }

REV2_P1 = {
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO2,  True),  4:  (V5,     False),
    5:  (GPIO3,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO27, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    }

REV2_P5 = {
    1:  (V5,     False), 2:  (V3_3,   False),
    3:  (GPIO28, False), 4:  (GPIO29, False),
    5:  (GPIO30, False), 6:  (GPIO31, False),
    7:  (GND,    False), 8:  (GND,    False),
    }

PLUS_P1 = {
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO2,  True),  4:  (V5,     False),
    5:  (GPIO3,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO27, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    27: (GPIO0,  False), 28: (GPIO1,  False),
    29: (GPIO5,  False), 30: (GND,    False),
    31: (GPIO6,  False), 32: (GPIO12, False),
    33: (GPIO13, False), 34: (GND,    False),
    35: (GPIO19, False), 36: (GPIO16, False),
    37: (GPIO26, False), 38: (GPIO20, False),
    39: (GND,    False), 40: (GPIO21, False),
    }

CM_SODIMM = {
    1:   (GND,              False), 2:   ('EMMC DISABLE N', False),
    3:   (GPIO0,            False), 4:   (NC,               False),
    5:   (GPIO1,            False), 6:   (NC,               False),
    7:   (GND,              False), 8:   (NC,               False),
    9:   (GPIO2,            False), 10:  (NC,               False),
    11:  (GPIO3,            False), 12:  (NC,               False),
    13:  (GND,              False), 14:  (NC,               False),
    15:  (GPIO4,            False), 16:  (NC,               False),
    17:  (GPIO5,            False), 18:  (NC,               False),
    19:  (GND,              False), 20:  (NC,               False),
    21:  (GPIO6,            False), 22:  (NC,               False),
    23:  (GPIO7,            False), 24:  (NC,               False),
    25:  (GND,              False), 26:  (GND,              False),
    27:  (GPIO8,            False), 28:  (GPIO28,           False),
    29:  (GPIO9,            False), 30:  (GPIO29,           False),
    31:  (GND,              False), 32:  (GND,              False),
    33:  (GPIO10,           False), 34:  (GPIO30,           False),
    35:  (GPIO11,           False), 36:  (GPIO31,           False),
    37:  (GND,              False), 38:  (GND,              False),
    39:  ('GPIO0-27 VREF',  False), 40:  ('GPIO0-27 VREF',  False),
    # Gap in SODIMM pins
    41:  ('GPIO28-45 VREF', False), 42:  ('GPIO28-45 VREF', False),
    43:  (GND,              False), 44:  (GND,              False),
    45:  (GPIO12,           False), 46:  (GPIO32,           False),
    47:  (GPIO13,           False), 48:  (GPIO33,           False),
    49:  (GND,              False), 50:  (GND,              False),
    51:  (GPIO14,           False), 52:  (GPIO34,           False),
    53:  (GPIO15,           False), 54:  (GPIO35,           False),
    55:  (GND,              False), 56:  (GND,              False),
    57:  (GPIO16,           False), 58:  (GPIO36,           False),
    59:  (GPIO17,           False), 60:  (GPIO37,           False),
    61:  (GND,              False), 62:  (GND,              False),
    63:  (GPIO18,           False), 64:  (GPIO38,           False),
    65:  (GPIO19,           False), 66:  (GPIO39,           False),
    67:  (GND,              False), 68:  (GND,              False),
    69:  (GPIO20,           False), 70:  (GPIO40,           False),
    71:  (GPIO21,           False), 72:  (GPIO41,           False),
    73:  (GND,              False), 74:  (GND,              False),
    75:  (GPIO22,           False), 76:  (GPIO42,           False),
    77:  (GPIO23,           False), 78:  (GPIO43,           False),
    79:  (GND,              False), 80:  (GND,              False),
    81:  (GPIO24,           False), 82:  (GPIO44,           False),
    83:  (GPIO25,           False), 84:  (GPIO45,           False),
    85:  (GND,              False), 86:  (GND,              False),
    87:  (GPIO26,           False), 88:  ('GPIO46 1V8',     False),
    89:  (GPIO27,           False), 90:  ('GPIO47 1V8',     False),
    91:  (GND,              False), 92:  (GND,              False),
    93:  ('DSI0 DN1',       False), 94:  ('DSI1 DP0',       False),
    95:  ('DSI0 DP1',       False), 96:  ('DSI1 DN0',       False),
    97:  (GND,              False), 98:  (GND,              False),
    99:  ('DSI0 DN0',       False), 100: ('DSI1 CP',        False),
    101: ('DSI0 DP0',       False), 102: ('DSI1 CN',        False),
    103: (GND,              False), 104: (GND,              False),
    105: ('DSI0 CN',        False), 106: ('DSI1 DP3',       False),
    107: ('DSI0 CP',        False), 108: ('DSI1 DN3',       False),
    109: (GND,              False), 110: (GND,              False),
    111: ('HDMI CK N',      False), 112: ('DSI1 DP2',       False),
    113: ('HDMI CK P',      False), 114: ('DSI1 DN2',       False),
    115: (GND,              False), 116: (GND,              False),
    117: ('HDMI D0 N',      False), 118: ('DSI1 DP1',       False),
    119: ('HDMI D0 P',      False), 120: ('DSI1 DN1',       False),
    121: (GND,              False), 122: (GND,              False),
    123: ('HDMI D1 N',      False), 124: (NC,               False),
    125: ('HDMI D1 P',      False), 126: (NC,               False),
    127: (GND,              False), 128: (NC,               False),
    129: ('HDMI D2 N',      False), 130: (NC,               False),
    131: ('HDMI D2 P',      False), 132: (NC,               False),
    133: (GND,              False), 134: (GND,              False),
    135: ('CAM1 DP3',       False), 136: ('CAM0 DP0',       False),
    137: ('CAM1 DN3',       False), 138: ('CAM0 DN0',       False),
    139: (GND,              False), 140: (GND,              False),
    141: ('CAM1 DP2',       False), 142: ('CAM0 CP',        False),
    143: ('CAM1 DN2',       False), 144: ('CAM0 CN',        False),
    145: (GND,              False), 146: (GND,              False),
    147: ('CAM1 CP',        False), 148: ('CAM0 DP1',       False),
    149: ('CAM1 CN',        False), 150: ('CAM0 DN1',       False),
    151: (GND,              False), 152: (GND,              False),
    153: ('CAM1 DP1',       False), 154: (NC,               False),
    155: ('CAM1 DN1',       False), 156: (NC,               False),
    157: (GND,              False), 158: (NC,               False),
    159: ('CAM1 DP0',       False), 160: (NC,               False),
    161: ('CAM1 DN0',       False), 162: (NC,               False),
    163: (GND,              False), 164: (GND,              False),
    165: ('USB DP',         False), 166: ('TVDAC',          False),
    167: ('USB DM',         False), 168: ('USB OTGID',      False),
    169: (GND,              False), 170: (GND,              False),
    171: ('HDMI CEC',       False), 172: ('VC TRST N',      False),
    173: ('HDMI SDA',       False), 174: ('VC TDI',         False),
    175: ('HDMI SCL',       False), 176: ('VC TMS',         False),
    177: ('RUN',            False), 178: ('VC TDO',         False),
    179: ('VDD CORE',       False), 180: ('VC TCK',         False),
    181: (GND,              False), 182: (GND,              False),
    183: (V1_8,             False), 184: (V1_8,             False),
    185: (V1_8,             False), 186: (V1_8,             False),
    187: (GND,              False), 188: (GND,              False),
    189: ('VDAC',           False), 190: ('VDAC',           False),
    191: (V3_3,             False), 192: (V3_3,             False),
    193: (V3_3,             False), 194: (V3_3,             False),
    195: (GND,              False), 196: (GND,              False),
    197: ('VBAT',           False), 198: ('VBAT',           False),
    199: ('VBAT',           False), 200: ('VBAT',           False),
    }

# The following data is sourced from a combination of the following locations:
#
# http://elinux.org/RPi_HardwareHistory
# http://elinux.org/RPi_Low-level_peripherals
# https://git.drogon.net/?p=wiringPi;a=blob;f=wiringPi/wiringPi.c#l807

PI_REVISIONS = {
    # rev     model    pcb_rev released soc        manufacturer ram   storage    usb eth wifi   bt     csi dsi headers
    0x2:      ('B',    '1.0', '2012Q1', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1},               ),
    0x3:      ('B',    '1.0', '2012Q3', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1},               ),
    0x4:      ('B',    '2.0', '2012Q3', 'BCM2835', 'Sony',      256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x5:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Qisda',     256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x6:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x7:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Egoman',    256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x8:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Sony',      256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x9:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Qisda',     256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0xd:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0xe:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Sony',      512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0xf:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5},),
    0x10:     ('B+',   '1.2', '2014Q3', 'BCM2835', 'Sony',      512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0x11:     ('CM',   '1.2', '2014Q2', 'BCM2835', 'Sony',      512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},         ),
    0x12:     ('A+',   '1.2', '2014Q4', 'BCM2835', 'Sony',      256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0x13:     ('B+',   '1.2', '2015Q1', 'BCM2835', 'Egoman',    512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0x14:     ('CM',   '1.1', '2014Q2', 'BCM2835', 'Embest',    512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},         ),
    0x15:     ('A+',   '1.1', '2014Q4', 'BCM2835', 'Sony',      256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0xa01041: ('2B',   '1.1', '2015Q1', 'BCM2836', 'Sony',      1024, 'MicroSD', 4,  1,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0xa21041: ('2B',   '1.1', '2015Q1', 'BCM2836', 'Embest',    1024, 'MicroSD', 4,  1,  False, False, 1,  1,  {'P1': PLUS_P1},               ),
    0x900092: ('Zero', '1.2', '2015Q4', 'BCM2835', 'Sony',      512,  'MicroSD', 1,  0,  False, False, 0,  0,  {'P1': PLUS_P1},               ),
    0xa02082: ('3B',   '1.2', '2016Q1', 'BCM2837', 'Sony',      1024, 'MicroSD', 4,  1,  True,  True,  1,  1,  {'P1': PLUS_P1},               ),
    0xa22082: ('3B',   '1.2', '2016Q1', 'BCM2837', 'Embest',    1024, 'MicroSD', 4,  1,  True,  True,  1,  1,  {'P1': PLUS_P1},               ),
    0x900093: ('Zero', '1.3', '2016Q2', 'BCM2835', 'Sony',      512,  'MicroSD', 1,  0,  False, False, 1,  0,  {'P1': PLUS_P1},               ),
    }


class PinInfo(namedtuple('PinInfo', (
    'number',
    'function',
    'pull_up',
    ))):
    """
    This class is a :func:`~collections.namedtuple` derivative used to
    represent information about a pin present on a GPIO header. The following
    attributes are defined:

    .. attribute:: number

        An integer containing the physical pin number on the header (starting
        from 1 in accordance with convention).

    .. attribute:: function

        A string describing the function of the pin. Some common examples
        include "GND" (for pins connecting to ground), "3V3" (for pins which
        output 3.3 volts), "GPIO9" (for GPIO9 in the Broadcom numbering
        scheme), etc.

    .. attribute:: pull_up

        A bool indicating whether the pin has a physical pull-up resistor
        permanently attached (this is usually ``False`` but GPIO2 and GPIO3
        are *usually* ``True``). This is used internally by gpiozero to raise
        errors when pull-down is requested on a pin with a physical pull-up
        resistor.
    """


class PiBoardInfo(namedtuple('PiBoardInfo', (
    'revision',
    'model',
    'pcb_revision',
    'released',
    'soc',
    'manufacturer',
    'memory',
    'storage',
    'usb',
    'ethernet',
    'wifi',
    'bluetooth',
    'csi',
    'dsi',
    'headers',
    ))):
    """
    This class is a :func:`~collections.namedtuple` derivative used to
    represent information about a particular model of Raspberry Pi. While it is
    a tuple, it is strongly recommended that you use the following named
    attributes to access the data contained within.

    .. automethod:: physical_pin

    .. automethod:: physical_pins

    .. automethod:: pulled_up

    .. attribute:: revision

        A string indicating the revision of the Pi. This is unique to each
        revision and can be considered the "key" from which all other
        attributes are derived. However, in itself the string is fairly
        meaningless.

    .. attribute:: model

        A string containing the model of the Pi (for example, "B", "B+", "A+",
        "2B", "CM" (for the Compute Module), or "Zero").

    .. attribute:: pcb_revision

        A string containing the PCB revision number which is silk-screened onto
        the Pi (on some models).

        .. note::

            This is primarily useful to distinguish between the model B
            revision 1.0 and 2.0 (not to be confused with the model 2B) which
            had slightly different pinouts on their 26-pin GPIO headers.

    .. attribute:: released

        A string containing an approximate release date for this revision of
        the Pi (formatted as yyyyQq, e.g. 2012Q1 means the first quarter of
        2012).

    .. attribute:: soc

        A string indicating the SoC (`system on a chip`_) that this revision
        of the Pi is based upon.

    .. attribute:: manufacturer

        A string indicating the name of the manufacturer (usually "Sony" but a
        few others exist).

    .. attribute:: memory

        An integer indicating the amount of memory (in Mb) connected to the
        SoC.

        .. note::

            This can differ substantially from the amount of RAM available
            to the operating system as the GPU's memory is shared with the
            CPU. When the camera module is activated, at least 128Mb of RAM
            is typically reserved for the GPU.

    .. attribute:: storage

        A string indicating the type of bootable storage used with this
        revision of Pi, e.g. "SD", "MicroSD", or "eMMC" (for the Compute
        Module).

    .. attribute:: usb

        An integer indicating how many USB ports are physically present on
        this revision of the Pi.

        .. note::

            This does *not* include the micro-USB port used to power the Pi.

    .. attribute:: ethernet

        An integer indicating how many Ethernet ports are physically present
        on this revision of the Pi.

    .. attribute:: wifi

        A bool indicating whether this revision of the Pi has wifi built-in.

    .. attribute:: bluetooth

        A bool indicating whether this revision of the Pi has bluetooth
        built-in.

    .. attribute:: csi

        An integer indicating the number of CSI (camera) ports available on
        this revision of the Pi.

    .. attribute:: dsi

        An integer indicating the number of DSI (display) ports available on
        this revision of the Pi.

    .. attribute:: headers

        A dictionary which maps header labels to dictionaries which map
        physical pin numbers to :class:`PinInfo` tuples. For example, to obtain
        information about pin 12 on header P1 you would query
        ``headers['P1'][12]``.

    .. _system on a chip: https://en.wikipedia.org/wiki/System_on_a_chip
    """

    def physical_pins(self, function):
        """
        Return the physical pins supporting the specified *function* as tuples
        of ``(header, pin_number)`` where *header* is a string specifying the
        header containing the *pin_number*. Note that the return value is a
        :class:`set` which is not indexable. Use :func:`physical_pin` if you
        are expecting a single return value.

        :param str function:
            The pin function you wish to search for. Usually this is something
            like "GPIO9" for Broadcom GPIO pin 9, or "GND" for all the pins
            connecting to electrical ground.
        """
        return {
            (header, pin.number)
            for (header, pins) in self.headers.items()
            for pin in pins.values()
            if pin.function == function
            }

    def physical_pin(self, function):
        """
        Return the physical pin supporting the specified *function*. If no pins
        support the desired *function*, this function raises :exc:`PinNoPins`.
        If multiple pins support the desired *function*, :exc:`PinMultiplePins`
        will be raised (use :func:`physical_pins` if you expect multiple pins
        in the result, such as for electrical ground).

        :param str function:
            The pin function you wish to search for. Usually this is something
            like "GPIO9" for Broadcom GPIO pin 9.
        """
        result = self.physical_pins(function)
        if len(result) > 1:
            raise PinMultiplePins('multiple pins can be used for %s' % function)
        elif result:
            return result.pop()
        else:
            raise PinNoPins('no pins can be used for %s' % function)

    def pulled_up(self, function):
        """
        Returns a bool indicating whether a physical pull-up is attached to
        the pin supporting the specified *function*. Either :exc:`PinNoPins`
        or :exc:`PinMultiplePins` may be raised if the function is not
        associated with a single pin.

        :param str function:
            The pin function you wish to determine pull-up for. Usually this is
            something like "GPIO9" for Broadcom GPIO pin 9.
        """
        try:
            header, number = self.physical_pin(function)
        except PinNoPins:
            return False
        else:
            return self.headers[header][number].pull_up


def _parse_pi_revision(revision):
    # For new-style revisions the value's bit pattern is as follows:
    #
    # MSB -----------------------> LSB
    # uuuuuuuuFMMMCCCCPPPPTTTTTTTTRRRR
    #
    # uuuuuuuu - Unused
    # F        - New flag (1=valid new-style revision, 0=old-style)
    # MMM      - Memory size (0=256, 1=512, 2=1024)
    # CCCC     - Manufacturer (0=Sony, 1=Egoman, 2=Embest)
    # PPPP     - Processor (0=2835, 1=2836, 2=2837)
    # TTTTTTTT - Type (0=A, 1=B, 2=A+, 3=B+, 4=2B, 5=Alpha (??), 6=CM, 8=3B, 9=Zero)
    # RRRR     - Revision (0, 1, or 2)
    if not (revision & 0x800000):
        raise PinUnknownPi('cannot parse "%x"; this is not a new-style revision' % revision)
    try:
        model = {
            0: 'A',
            1: 'B',
            2: 'A+',
            3: 'B+',
            4: '2B',
            6: 'CM',
            8: '3B',
            9: 'Zero',
            }[(revision & 0xff0) >> 4]
        if model in ('A', 'B'):
            pcb_revision = {
                0: '1.0', # is this right?
                1: '1.0',
                2: '2.0',
                }[revision & 0x0f]
        else:
            pcb_revision = '1.%d' % (revision & 0x0f)
        released = {
            'A':    '2013Q1',
            'B':    '2012Q1' if pcb_revision == '1.0' else '2012Q4',
            'A+':   '2014Q4',
            'B+':   '2014Q3',
            '2B':   '2015Q1',
            'CM':   '2014Q2',
            '3B':   '2016Q1',
            'Zero': '2015Q4' if pcb_revision == '1.0' else '2016Q2',
            }[model]
        soc = {
            0: 'BCM2835',
            1: 'BCM2836',
            2: 'BCM2837',
            }[(revision & 0xf000) >> 12]
        manufacturer = {
            0: 'Sony',
            1: 'Egoman',
            2: 'Embest',
            }[(revision & 0xf0000) >> 16]
        memory = {
            0: 256,
            1: 512,
            2: 1024,
            }[(revision & 0x700000) >> 20]
        storage = {
            'A': 'SD',
            'B': 'SD',
            'CM': 'eMMC',
            }.get(model, 'MicroSD')
        usb = {
            'A':    1,
            'A+':   1,
            'Zero': 1,
            'B':    2,
            'CM':   0,
            }.get(model, 4)
        ethernet = {
            'A':    0,
            'A+':   0,
            'Zero': 0,
            'CM':   0,
            }.get(model, 1)
        wifi = {
            '3B': True,
            }.get(model, False)
        bluetooth = {
            '3B': True,
            }.get(model, False)
        csi = {
            'Zero': 0 if pcb_revision == '1.0' else 1,
            'CM':   2,
            }.get(model, 1)
        dsi = {
            'Zero': 0,
            }.get(model, csi)
        headers = {
            'A':  {'P1': REV2_P1, 'P5': REV2_P5},
            'B':  {'P1': REV2_P1, 'P5': REV2_P5} if pcb_revision == '2.0' else {'P1': REV1_P1},
            'CM': {'SODIMM': CM_SODIMM},
            }.get(model, {'P1': PLUS_P1})
    except KeyError:
        raise PinUnknownPi('unable to parse new-style revision "%x"' % revision)
    else:
        return (
            model,
            pcb_revision,
            released,
            soc,
            manufacturer,
            memory,
            storage,
            usb,
            ethernet,
            wifi,
            bluetooth,
            csi,
            dsi,
            headers,
            )


def pi_info(revision=None):
    """
    Returns a :class:`PiBoardInfo` instance containing information about a
    *revision* of the Raspberry Pi.

    :param str revision:
        The revision of the Pi to return information about. If this is omitted
        or ``None`` (the default), then the library will attempt to determine
        the model of Pi it is running on and return information about that.
    """
    if revision is None:
        # NOTE: This import is declared locally for two reasons. Firstly it
        # avoids a circular dependency (devices->pins->pins.data->devices).
        # Secondly, pin_factory is one global which might potentially be
        # re-written by a user's script at runtime hence we should re-import
        # here in case it's changed since initialization
        from ..devices import pin_factory
        result = pin_factory.pi_info()
        if result is None:
            raise PinUnknownPi('The default pin_factory is not attached to a Pi')
        else:
            return result
    else:
        if isinstance(revision, bytes):
            revision = revision.decode('ascii')
        if isinstance(revision, str):
            revision = int(revision, base=16)
        else:
            # be nice to people passing an int (or something numeric anyway)
            revision = int(revision)
    try:
        (
            model,
            pcb_revision,
            released,
            soc,
            manufacturer,
            memory,
            storage,
            usb,
            ethernet,
            wifi,
            bluetooth,
            csi,
            dsi,
            headers,
            ) = PI_REVISIONS[revision]
    except KeyError:
        (
            model,
            pcb_revision,
            released,
            soc,
            manufacturer,
            memory,
            storage,
            usb,
            ethernet,
            wifi,
            bluetooth,
            csi,
            dsi,
            headers,
            ) = _parse_pi_revision(revision)
    headers = {
        header: {
            number: PinInfo(number, function, pull_up)
            for number, (function, pull_up) in header_data.items()
            }
        for header, header_data in headers.items()
        }
    return PiBoardInfo(
        '%04x' % revision,
        model,
        pcb_revision,
        released,
        soc,
        manufacturer,
        memory,
        storage,
        usb,
        ethernet,
        wifi,
        bluetooth,
        csi,
        dsi,
        headers,
        )


