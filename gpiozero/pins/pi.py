from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import io
from threading import RLock
from types import MethodType
try:
    from weakref import ref, WeakMethod
except ImportError:

    from ..compat import WeakMethod
import warnings

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None

from . import Factory, Pin
from .data import pi_info
from ..exc import (
    PinNoPins,
    PinNonPhysical,
    PinInvalidPin,
    SPIBadArgs,
    SPISoftwareFallback,
    )


class PiFactory(Factory):
    """
    Abstract base class representing hardware attached to a Raspberry Pi. This
    forms the base of :class:`~gpiozero.pins.local.LocalPiFactory`.
    """
    def __init__(self):
        self._info = None
        self.pins = {}
        self.pin_class = None
        self.spi_classes = {
            ('hardware', 'exclusive'): None,
            ('hardware', 'shared'):    None,
            ('software', 'exclusive'): None,
            ('software', 'shared'):    None,
            }

    def close(self):
        for pin in self.pins.values():
            pin.close()
        self.pins.clear()

    def pin(self, spec):
        n = self._to_gpio(spec)
        try:
            pin = self.pins[n]
        except KeyError:
            pin = self.pin_class(self, n)
            self.pins[n] = pin
        return pin

    def pin_address(self, spec):
        n = self._to_gpio(spec)
        return self.address + ('GPIO%d' % n,)

    def _to_gpio(self, spec):
        """
        Converts the pin *spec* to a GPIO port number.
        """
        if not 0 <= spec < 54:
            raise PinInvalidPin('invalid GPIO port %d specified (range 0..53) ' % spec)
        return spec

    def _get_revision(self):
        raise NotImplementedError

    def _get_pi_info(self):
        if self._info is None:
            self._info = pi_info(self._get_revision())
        return self._info

    def spi(self, **spi_args):
        """
        Returns an SPI interface, for the specified SPI *port* and *device*, or
        for the specified pins (*clock_pin*, *mosi_pin*, *miso_pin*, and
        *select_pin*).  Only one of the schemes can be used; attempting to mix
        *port* and *device* with pin numbers will raise :exc:`SPIBadArgs`.

        If the pins specified match the hardware SPI pins (clock on GPIO11,
        MOSI on GPIO10, MISO on GPIO9, and chip select on GPIO8 or GPIO7), and
        the spidev module can be imported, a :class:`SPIHardwareInterface`
        instance will be returned. Otherwise, a :class:`SPISoftwareInterface`
        will be returned which will use simple bit-banging to communicate.

        Both interfaces have the same API, support clock polarity and phase
        attributes, and can handle half and full duplex communications, but the
        hardware interface is significantly faster (though for many things this
        doesn't matter).
        """
        spi_args, kwargs = self._extract_spi_args(**spi_args)
        shared = 'shared' if kwargs.pop('shared', False) else 'exclusive'
        if kwargs:
            raise SPIBadArgs(
                'unrecognized keyword argument %s' % kwargs.popitem()[0])
        if all((
                spi_args['clock_pin'] == 11,
                spi_args['mosi_pin'] == 10,
                spi_args['miso_pin'] == 9,
                spi_args['select_pin'] in (7, 8),
                )):
            try:
                return self.spi_classes[('hardware', shared)](
                    self, port=0, device=0 if spi_args['select_pin'] == 8 else 1
                    )
            except Exception as e:
                warnings.warn(
                    SPISoftwareFallback(
                        'failed to initialize hardware SPI, falling back to '
                        'software (error was: %s)' % str(e)))
        # Convert all pin arguments to integer GPIO numbers. This is necessary
        # to ensure the shared-key for shared implementations get matched
        # correctly, and is a bit of a hack for the pigpio bit-bang
        # implementation which just wants the pin numbers too.
        spi_args = {
            key: pin.number if isinstance(pin, Pin) else pin
            for key, pin in spi_args.items()
            }
        return self.spi_classes[('software', shared)](self, **spi_args)

    def _extract_spi_args(self, **kwargs):
        """
        Given a set of keyword arguments, splits it into those relevant to SPI
        implementations and all the rest. SPI arguments are augmented with
        defaults and converted into the pin format (from the port/device
        format) if necessary.

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
                key: self._to_gpio(spi_args.get(key, default))
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
                'you must either specify port and device, or clock_pin, '
                'mosi_pin, miso_pin, and select_pin; combinations of the two '
                'schemes (e.g. port and clock_pin) are not permitted')
        return spi_args, kwargs


class PiPin(Pin):
    """
    Abstract base class representing a multi-function GPIO pin attached to a
    Raspberry Pi. This overrides several methods in the abstract base
    :class:`~gpiozero.Pin`. Descendents must override the following methods:

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
        super(PiPin, self).__init__()
        self._factory = factory
        self._when_changed_lock = RLock()
        self._when_changed = None
        self._number = number
        try:
            factory.pi_info.physical_pin(self.address[-1])
        except PinNoPins:
            warnings.warn(
                PinNonPhysical(
                    'no physical pins exist for %s' % self.address[-1]))

    @property
    def number(self):
        return self._number

    @property
    def factory(self):
        return self._factory

    def _get_address(self):
        return self.factory.address + ('GPIO%d' % self.number,)

    def _call_when_changed(self):
        """
        Called to fire the :attr:`when_changed` event handler; override this
        in descendents if additional (currently redundant) parameters need
        to be passed.
        """
        method = self.when_changed()
        if method is None:
            self.when_changed = None
        else:
            method()

    def _get_when_changed(self):
        return self._when_changed

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

