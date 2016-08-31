from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')


import warnings
import operator
from threading import RLock

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None

from .devices import Device, SharedMixin, _PINS, _PINS_LOCK
from .input_devices import InputDevice
from .output_devices import OutputDevice
from .exc import SPIBadArgs, SPISoftwareFallback, GPIOPinInUse, DeviceClosed


class SPIHardwareInterface(Device):
    def __init__(self, port, device):
        self._device = None
        super(SPIHardwareInterface, self).__init__()
        # XXX How can we detect conflicts with existing GPIO instances? This
        # isn't ideal ... in fact, it's downright crap and doesn't guard
        # against conflicts created *after* this instance, but it's all I can
        # come up with right now ...
        conflicts = (11, 10, 9, (8, 7)[device])
        with _PINS_LOCK:
            for pin in _PINS:
                if pin.number in conflicts:
                    raise GPIOPinInUse(
                        'pin %r is already in use by another gpiozero object' % pin
                    )
        self._device_num = device
        self._device = SpiDev()
        self._device.open(port, device)
        self._device.max_speed_hz = 500000

    def close(self):
        if self._device:
            try:
                self._device.close()
            finally:
                self._device = None
        super(SPIHardwareInterface, self).close()

    @property
    def closed(self):
        return self._device is None

    def __repr__(self):
        try:
            self._check_open()
            return (
                "hardware SPI on clock_pin=11, mosi_pin=10, miso_pin=9, "
                "select_pin=%d" % (
                    8 if self._device_num == 0 else 7))
        except DeviceClosed:
            return "hardware SPI closed"

    def read(self, n):
        return self.transfer((0,) * n)

    def write(self, data):
        return len(self.transfer(data))

    def transfer(self, data):
        """
        Writes data (a list of integer words where each word is assumed to have
        :attr:`bits_per_word` bits or less) to the SPI interface, and reads an
        equivalent number of words, returning them as a list of integers.
        """
        return self._device.xfer2(data)

    def _get_clock_mode(self):
        return self._device.mode

    def _set_clock_mode(self, value):
        self._device.mode = value

    def _get_clock_polarity(self):
        return bool(self.mode & 2)

    def _set_clock_polarity(self, value):
        self.mode = self.mode & (~2) | (bool(value) << 1)

    def _get_clock_phase(self):
        return bool(self.mode & 1)

    def _set_clock_phase(self, value):
        self.mode = self.mode & (~1) | bool(value)

    def _get_lsb_first(self):
        return self._device.lsbfirst

    def _set_lsb_first(self, value):
        self._device.lsbfirst = bool(value)

    def _get_select_high(self):
        return self._device.cshigh

    def _set_select_high(self, value):
        self._device.cshigh = bool(value)

    def _get_bits_per_word(self):
        return self._device.bits_per_word

    def _set_bits_per_word(self, value):
        self._device.bits_per_word = value

    clock_polarity = property(_get_clock_polarity, _set_clock_polarity)
    clock_phase = property(_get_clock_phase, _set_clock_phase)
    clock_mode = property(_get_clock_mode, _set_clock_mode)
    lsb_first = property(_get_lsb_first, _set_lsb_first)
    select_high = property(_get_select_high, _set_select_high)
    bits_per_word = property(_get_bits_per_word, _set_bits_per_word)


class SPISoftwareBus(SharedMixin, Device):
    def __init__(self, clock_pin, mosi_pin, miso_pin):
        self.lock = None
        self.clock = None
        self.mosi = None
        self.miso = None
        super(SPISoftwareBus, self).__init__()
        self.lock = RLock()
        self.clock_phase = False
        self.lsb_first = False
        self.bits_per_word = 8
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
        if self.lock:
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

    def read(self, n):
        return self.transfer((0,) * n)

    def write(self, data):
        return len(self.transfer(data))

    def transfer(self, data):
        """
        Writes data (a list of integer words where each word is assumed to have
        :attr:`bits_per_word` bits or less) to the SPI interface, and reads an
        equivalent number of words, returning them as a list of integers.
        """
        result = []
        with self.lock:
            shift = operator.lshift if self.lsb_first else operator.rshift
            for write_word in data:
                mask = 1 if self.lsb_first else 1 << (self.bits_per_word - 1)
                read_word = 0
                for _ in range(self.bits_per_word):
                    if self.mosi is not None:
                        self.mosi.value = bool(write_word & mask)
                    self.clock.on()
                    if self.miso is not None and not self.clock_phase:
                        if self.miso.value:
                            read_word |= mask
                    self.clock.off()
                    if self.miso is not None and self.clock_phase:
                        if self.miso.value:
                            read_word |= mask
                    mask = shift(mask, 1)
                result.append(read_word)
        return result


class SPISoftwareInterface(OutputDevice):
    def __init__(self, clock_pin, mosi_pin, miso_pin, select_pin):
        self._bus = None
        super(SPISoftwareInterface, self).__init__(select_pin, active_high=False)
        try:
            self._bus = SPISoftwareBus(clock_pin, mosi_pin, miso_pin)
        except:
            self.close()
            raise

    def close(self):
        if self._bus:
            self._bus.close()
            self._bus = None
        super(SPISoftwareInterface, self).close()

    def __repr__(self):
        try:
            self._check_open()
            return (
                "software SPI on clock_pin=%d, mosi_pin=%d, miso_pin=%d, "
                "select_pin=%d" % (
                    self._bus.clock.pin.number,
                    self._bus.mosi.pin.number,
                    self._bus.miso.pin.number,
                    self.pin.number))
        except DeviceClosed:
            return "software SPI closed"

    def read(self, n):
        return self._bus.read(n)

    def write(self, data):
        return self._bus.write(data)

    def transfer(self, data):
        with self._bus.lock:
            self.on()
            try:
                return self._bus.transfer(data)
            finally:
                self.off()

    def _get_clock_mode(self):
        return (self.clock_polarity << 1) | self.clock_phase

    def _set_clock_mode(self, value):
        value = int(value)
        if not 0 <= value <= 3:
            raise ValueError('clock_mode must be a value between 0 and 3 inclusive')
        with self._bus.lock:
            self._bus.clock.active_high = not (value & 2)
            self._bus.clock.off()
            self._bus.clock_phase = bool(value & 1)

    def _get_clock_polarity(self):
        return not self._bus.clock.active_high

    def _set_clock_polarity(self, value):
        with self._bus.lock:
            self._bus.clock.active_high = not value

    def _get_clock_phase(self):
        return self._bus.clock_phase

    def _set_clock_phase(self, value):
        with self._bus.lock:
            self._bus.clock_phase = bool(value)

    def _get_lsb_first(self):
        return self._bus.lsb_first

    def _set_lsb_first(self, value):
        with self._bus.lock:
            self._bus.lsb_first = bool(value)

    def _get_bits_per_word(self):
        return self._bus.bits_per_word

    def _set_bits_per_word(self, value):
        if value < 1:
            raise ValueError('bits_per_word must be positive')
        with self._bus.lock:
            self._bus.bits_per_word = int(value)

    def _get_select_high(self):
        return self.active_high

    def _set_select_high(self, value):
        with self._bus.lock:
            self.active_high = value
            self.off()

    clock_polarity = property(_get_clock_polarity, _set_clock_polarity)
    clock_phase = property(_get_clock_phase, _set_clock_phase)
    clock_mode = property(_get_clock_mode, _set_clock_mode)
    lsb_first = property(_get_lsb_first, _set_lsb_first)
    bits_per_word = property(_get_bits_per_word, _set_bits_per_word)
    select_high = property(_get_select_high, _set_select_high)


class SharedSPIHardwareInterface(SharedMixin, SPIHardwareInterface):
    @classmethod
    def _shared_key(cls, port, device):
        return (port, device)


class SharedSPISoftwareInterface(SharedMixin, SPISoftwareInterface):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin):
        return (clock_pin, mosi_pin, miso_pin, select_pin)


def extract_spi_args(**kwargs):
    """
    Given a set of keyword arguments, splits it into those relevant to SPI
    implementations and all the rest. SPI arguments are augmented with defaults
    and converted into the pin format (from the port/device format) if
    necessary.

    Returns a tuple of ``(spi_args, other_args)``.
    """
    pin_defaults = {
        'clock_pin': 11,
        'mosi_pin': 10,
        'miso_pin': 9,
        'select_pin': 8,
        }
    dev_defaults = {
        'port': 0,
        'device': 0,
        }
    spi_args = {
        key: value for (key, value) in kwargs.items()
        if key in pin_defaults or key in dev_defaults
        }
    kwargs = {
        key: value for (key, value) in kwargs.items()
        if key not in spi_args
        }
    if not spi_args:
        spi_args = pin_defaults
    elif set(spi_args) <= set(pin_defaults):
        spi_args = {
            key: spi_args.get(key, default)
            for key, default in pin_defaults.items()
            }
    elif set(spi_args) <= set(dev_defaults):
        spi_args = {
            key: spi_args.get(key, default)
            for key, default in dev_defaults.items()
            }
        if spi_args['port'] != 0:
            raise SPIBadArgs('port 0 is the only valid SPI port')
        if spi_args['device'] not in (0, 1):
            raise SPIBadArgs('device must be 0 or 1')
        spi_args = {
            key: value if key != 'select_pin' else (8, 7)[spi_args['device']]
            for key, value in pin_defaults.items()
            }
    else:
        raise SPIBadArgs(
            'you must either specify port and device, or clock_pin, mosi_pin, '
            'miso_pin, and select_pin; combinations of the two schemes (e.g. '
            'port and clock_pin) are not permitted')
    return spi_args, kwargs


def SPI(**spi_args):
    """
    Returns an SPI interface, for the specified SPI *port* and *device*, or for
    the specified pins (*clock_pin*, *mosi_pin*, *miso_pin*, and *select_pin*).
    Only one of the schemes can be used; attempting to mix *port* and *device*
    with pin numbers will raise :exc:`SPIBadArgs`.

    If the pins specified match the hardware SPI pins (clock on GPIO11, MOSI on
    GPIO10, MISO on GPIO9, and chip select on GPIO8 or GPIO7), and the spidev
    module can be imported, a :class:`SPIHardwareInterface` instance will be
    returned. Otherwise, a :class:`SPISoftwareInterface` will be returned which
    will use simple bit-banging to communicate.

    Both interfaces have the same API, support clock polarity and phase
    attributes, and can handle half and full duplex communications, but the
    hardware interface is significantly faster (though for many things this
    doesn't matter).

    Finally, the *shared* keyword argument specifies whether the resulting
    SPI interface can be repeatedly created and used by multiple devices
    (useful with multi-channel devices like numerous ADCs).
    """
    spi_args, kwargs = extract_spi_args(**spi_args)
    shared = kwargs.pop('shared', False)
    if kwargs:
        raise SPIBadArgs(
            'unrecognized keyword argument %s' % kwargs.popitem()[0])
    if all((
            spi_args['clock_pin'] == 11,
            spi_args['mosi_pin'] == 10,
            spi_args['miso_pin'] == 9,
            spi_args['select_pin'] in (7, 8),
            )):
        if SpiDev is None:
            warnings.warn(
                SPISoftwareFallback(
                    'failed to import spidev, falling back to software SPI'))
        else:
            try:
                hardware_spi_args = {
                    'port': 0,
                    'device': {8: 0, 7: 1}[spi_args['select_pin']],
                    }
                if shared:
                    return SharedSPIHardwareInterface(**hardware_spi_args)
                else:
                    return SPIHardwareInterface(**hardware_spi_args)
            except Exception as e:
                warnings.warn(
                    SPISoftwareFallback(
                        'failed to initialize hardware SPI, falling back to '
                        'software (error was: %s)' % str(e)))
    if shared:
        return SharedSPISoftwareInterface(**spi_args)
    else:
        return SPISoftwareInterface(**spi_args)

