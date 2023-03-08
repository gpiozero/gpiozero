# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from threading import RLock
from types import MethodType
from weakref import ref, WeakMethod
import warnings

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None

from . import Factory, Pin
from .data import PiBoardInfo
from ..exc import (
    PinNoPins,
    PinNonPhysical,
    SPIBadArgs,
    SPISoftwareFallback,
    I2CBadArgs,
    I2CSoftwareFallback,
)


SPI_HARDWARE_PINS = {
    0: {
        'clock':  11,
        'mosi':   10,
        'miso':   9,
        'select': (8, 7),
    },
}


def spi_port_device(clock_pin, mosi_pin, miso_pin, select_pin):
    """
    Convert a mapping of pin definitions, which must contain 'clock_pin', and
    'select_pin' at a minimum, to a hardware SPI port, device tuple. Raises
    :exc:`~gpiozero.SPIBadArgs` if the pins do not represent a valid hardware
    SPI device.
    """
    for port, pins in SPI_HARDWARE_PINS.items():
        if all((
                clock_pin  == pins['clock'],
                mosi_pin   in (None, pins['mosi']),
                miso_pin   in (None, pins['miso']),
                select_pin in pins['select'],
                )):
            device = pins['select'].index(select_pin)
            return (port, device)
    raise SPIBadArgs('invalid pin selection for hardware SPI')


I2C_HARDWARE_PINS = {
    0: {
        'data':  0,
        'clock':   1,
    },
    1: {
        'data':  2,
        'clock':   3,
    },
}


def i2c_port(data_pin, clock_pin):
    """
    Convert a mapping of pin definitions, which must contain 'data_pin' and
    'clock_pin', to a hardware I2C port. Raises
    :exc:`~gpiozero.I2CBadArgs` if the pins do not represent a valid hardware
    I2C device.
    """
    for port, pins in I2C_HARDWARE_PINS.items():
        if all((
                data_pin  == pins['data'],
                clock_pin  == pins['clock'],
                )):
            return port
    raise I2CBadArgs('invalid pin selection for hardware I2C')


class PiFactory(Factory):
    """
    Extends :class:`~gpiozero.Factory`. Abstract base class representing
    hardware attached to a Raspberry Pi. This forms the base of
    :class:`~gpiozero.pins.local.LocalPiFactory`.
    """
    def __init__(self):
        super().__init__()
        self._info = None
        self.pins = {}
        self.pin_class = None

    def close(self):
        for pin in self.pins.values():
            pin.close()
        self.pins.clear()

    def reserve_pins(self, requester, *pins):
        super().reserve_pins(
            requester, *(self.pi_info.to_gpio(pin) for pin in pins))

    def release_pins(self, reserver, *pins):
        super().release_pins(
            reserver, *(self.pi_info.to_gpio(pin) for pin in pins))

    def pin(self, spec):
        n = self.pi_info.to_gpio(spec)
        try:
            pin = self.pins[n]
        except KeyError:
            pin = self.pin_class(self, n)
            self.pins[n] = pin
        return pin

    def _get_revision(self):
        """
        This method must be overridden by descendents to return the Pi's
        revision code as an :class:`int`. The default is unimplemented.
        """
        raise NotImplementedError

    def _get_pi_info(self):
        if self._info is None:
            self._info = PiBoardInfo.from_revision(self._get_revision())
        return self._info

    def spi(self, **spi_args):
        """
        Returns an SPI interface, for the specified SPI *port* and *device*, or
        for the specified pins (*clock_pin*, *mosi_pin*, *miso_pin*, and
        *select_pin*).  Only one of the schemes can be used; attempting to mix
        *port* and *device* with pin numbers will raise
        :exc:`~gpiozero.SPIBadArgs`.

        If the pins specified match the hardware SPI pins (clock on GPIO11,
        MOSI on GPIO10, MISO on GPIO9, and chip select on GPIO8 or GPIO7), and
        the spidev module can be imported, a hardware based interface (using
        spidev) will be returned. Otherwise, a software based interface will be
        returned which will use simple bit-banging to communicate.

        Both interfaces have the same API, support clock polarity and phase
        attributes, and can handle half and full duplex communications, but the
        hardware interface is significantly faster (though for many simpler
        devices this doesn't matter).
        """
        spi_args, kwargs = self._extract_spi_args(**spi_args)
        shared = bool(kwargs.pop('shared', False))
        if kwargs:
            raise SPIBadArgs(
                'unrecognized keyword argument {arg}'.format(
                    arg=kwargs.popitem()[0]))
        try:
            port, device = spi_port_device(**spi_args)
        except SPIBadArgs:
            # Assume request is for a software SPI implementation
            pass
        else:
            try:
                return self._get_spi_class(shared, hardware=True)(
                    pin_factory=self, **spi_args)
            except Exception as e:
                warnings.warn(
                    SPISoftwareFallback(
                        'failed to initialize hardware SPI, falling back to '
                        'software (error was: {e!s})'.format(e=e)))
        return self._get_spi_class(shared, hardware=False)(
            pin_factory=self, **spi_args)

    def _extract_spi_args(self, **kwargs):
        """
        Given a set of keyword arguments, splits it into those relevant to SPI
        implementations and all the rest. SPI arguments are augmented with
        defaults and converted into the pin format (from the port/device
        format) if necessary.

        Returns a tuple of ``(spi_args, other_args)``.
        """
        dev_defaults = {
            'port': 0,
            'device': 0,
            }
        default_hw = SPI_HARDWARE_PINS[dev_defaults['port']]
        pin_defaults = {
            'clock_pin':  default_hw['clock'],
            'mosi_pin':   default_hw['mosi'],
            'miso_pin':   default_hw['miso'],
            'select_pin': default_hw['select'][dev_defaults['device']],
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
                key: None if spi_args.get(key, default) is None else
                    self.pi_info.to_gpio(spi_args.get(key, default))
                for key, default in pin_defaults.items()
                }
        elif set(spi_args) <= set(dev_defaults):
            spi_args = {
                key: spi_args.get(key, default)
                for key, default in dev_defaults.items()
                }
            try:
                selected_hw = SPI_HARDWARE_PINS[spi_args['port']]
            except KeyError:
                raise SPIBadArgs(
                    'port {spi_args[port]} is not a valid SPI port'.format(
                        spi_args=spi_args))
            try:
                selected_hw['select'][spi_args['device']]
            except IndexError:
                raise SPIBadArgs(
                    'device must be in the range 0..{count}'.format(
                        count=len(selected_hw['select'])))
            spi_args = {
                key: value if key != 'select_pin' else selected_hw['select'][spi_args['device']]
                for key, value in pin_defaults.items()
                }
        else:
            raise SPIBadArgs(
                'you must either specify port and device, or clock_pin, '
                'mosi_pin, miso_pin, and select_pin; combinations of the two '
                'schemes (e.g. port and clock_pin) are not permitted')
        return spi_args, kwargs

    def _get_spi_class(self, shared, hardware):
        """
        Returns a sub-class of the :class:`SPI` which can be constructed with
        *clock_pin*, *mosi_pin*, *miso_pin*, and *select_pin* arguments. The
        *shared* argument dictates whether the returned class uses the
        :class:`SharedMixin` to permit sharing instances between components,
        while *hardware* indicates whether the returned class uses the kernel's
        SPI device(s) rather than a bit-banged software implementation.
        """
        raise NotImplementedError

    def i2c(self, **i2c_args):
        """
        Returns an I2C interface, for the specified I2C *port*, or for the
        specified pins (*data_pin* and *clock_pin*). Additionally, the *device*
        address must be specified. Only one of the schemes can be used;
        attempting to mix *port* with pin numbers will raise
        :exc:`~gpiozero.I2CBadArgs`.
        """
        i2c_args, kwargs = self._extract_i2c_args(**i2c_args)
        shared = bool(kwargs.pop('shared', False))
        if kwargs:
            raise I2CBadArgs(
                'unrecognized keyword argument {arg}'.format(
                    arg=kwargs.popitem()[0]))
        try:
            return self._get_i2c_class(shared, hardware=True)(
                pin_factory=self, **i2c_args)
        except Exception as e:
            warnings.warn(
                I2CSoftwareFallback(
                    'failed to initialize hardware I2C, falling back to '
                    'software (error was: {e!s})'.format(e=e)))
        return self._get_i2c_class(shared, hardware=False)(
            pin_factory=self, **i2c_args)
    
    def _extract_i2c_args(self, **kwargs):
        """
        Given a set of keyword arguments, splits it into those relevant to I2C
        implementations and all the rest. I2C arguments are augmented with
        defaults and converted into the pin format (from the port format) if
        necessary.

        The *device* keyword specifying the device address has no default and
        must by specified.

        Returns a tuple of ``(i2c_args, other_args)``.
        """
        try:
            device = kwargs.pop("device")
        except KeyError:
            raise I2CBadArgs(
                'device address is not specified as the *device* keyword'
            )
        dev_defaults = {
            'port': 1,
            }
        default_hw = I2C_HARDWARE_PINS[dev_defaults['port']]
        pin_defaults = {
            'data_pin':  default_hw['data'],
            'clock_pin':  default_hw['clock'],
            }
        i2c_args = {
            key: value for (key, value) in kwargs.items()
            if key in pin_defaults or key in dev_defaults
            }
        kwargs = {
            key: value for (key, value) in kwargs.items()
            if key not in i2c_args
            }
        if not i2c_args:
            i2c_args = pin_defaults
        elif set(i2c_args) <= set(pin_defaults):
            i2c_args = {
                key: None if i2c_args.get(key, default) is None else
                    self.pi_info.to_gpio(i2c_args.get(key, default))
                for key, default in pin_defaults.items()
                }
        elif set(i2c_args) <= set(dev_defaults):
            try:
                selected_hw = I2C_HARDWARE_PINS[i2c_args['port']]
            except KeyError:
                raise I2CBadArgs(
                    'port {i2c_args[port]} is not a valid I2C port'.format(
                        i2c_args=i2c_args))
            i2c_args = {
                "data_pin": selected_hw["data"],
                "clock_pin": selected_hw["clock"]
                }
        else:
            raise I2CBadArgs(
                'you must either specify port, or data_pin and clock_pin; '
                'combinations of the two schemes (e.g. port and clock_pin) '
                'are not permitted')
        return i2c_args | {"device": device}, kwargs

    def _get_i2c_class(self, shared, hardware):
        """
        Returns a sub-class of the :class:`I2C` which can be constructed with
        *data_pin* and *clock_pin* arguments. The
        *shared* argument dictates whether the returned class uses the
        :class:`SharedMixin` to permit sharing instances between components,
        while *hardware* indicates whether the returned class uses the kernel's
        I2C device(s) rather than a bit-banged software implementation.
        """
        raise NotImplementedError


class PiPin(Pin):
    """
    Extends :class:`~gpiozero.Pin`. Abstract base class representing a
    multi-function GPIO pin attached to a Raspberry Pi. Descendents *must*
    override the following methods:

    * :meth:`_get_function`
    * :meth:`_set_function`
    * :meth:`_get_state`
    * :meth:`_call_when_changed`
    * :meth:`_enable_event_detect`
    * :meth:`_disable_event_detect`

    Descendents *may* additionally override the following methods, if
    applicable:

    * :meth:`close`
    * :meth:`output_with_state`
    * :meth:`input_with_pull`
    * :meth:`_set_state`
    * :meth:`_get_frequency`
    * :meth:`_set_frequency`
    * :meth:`_get_pull`
    * :meth:`_set_pull`
    * :meth:`_get_bounce`
    * :meth:`_set_bounce`
    * :meth:`_get_edges`
    * :meth:`_set_edges`
    """
    def __init__(self, factory, number):
        super().__init__()
        self._factory = factory
        self._when_changed_lock = RLock()
        self._when_changed = None
        self._number = number
        try:
            factory.pi_info.physical_pin(repr(self))
        except PinNoPins:
            warnings.warn(PinNonPhysical(
                'no physical pins exist for {self!r}'.format(self=self)))

    @property
    def number(self):
        return self._number

    def __repr__(self):
        return 'GPIO{self._number}'.format(self=self)

    @property
    def factory(self):
        return self._factory

    def _call_when_changed(self, ticks, state):
        """
        Called to fire the :attr:`when_changed` event handler; override this
        in descendents if additional (currently redundant) parameters need
        to be passed.
        """
        method = self._when_changed()
        if method is None:
            self.when_changed = None
        else:
            method(ticks, state)

    def _get_when_changed(self):
        return None if self._when_changed is None else self._when_changed()

    def _set_when_changed(self, value):
        with self._when_changed_lock:
            if value is None:
                if self._when_changed is not None:
                    self._disable_event_detect()
                self._when_changed = None
            else:
                enabled = self._when_changed is not None
                # Have to take care, if value is either a closure or a bound
                # method, not to keep a strong reference to the containing
                # object
                if isinstance(value, MethodType):
                    self._when_changed = WeakMethod(value)
                else:
                    self._when_changed = ref(value)
                if not enabled:
                    self._enable_event_detect()

    def _enable_event_detect(self):
        """
        Enables event detection. This is called to activate event detection on
        pin :attr:`number`, watching for the specified :attr:`edges`. In
        response, :meth:`_call_when_changed` should be executed.
        """
        raise NotImplementedError

    def _disable_event_detect(self):
        """
        Disables event detection. This is called to deactivate event detection
        on pin :attr:`number`.
        """
        raise NotImplementedError
