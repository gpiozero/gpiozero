from importlib import import_module
from threading import Lock

from .devices import GPIOBase
from .mixins import SharedMixin
from .pins.data import pi_info


def get_default_bus():
    """Find the default I2C bus, according to the current RPi board.
    """
    return 0 if pi_info().revision == 1 else 1


def find_smbus_module(candidates=('smbus', 'smbus2', 'Adafruit_PureIO.smbus')):
    """Iterate over ``candidates`` SMBus modules and return the 1st available.
    """
    for candidate in candidates:
        try:
            module = import_module(candidate)
        except ImportError:
            pass
        else:
            return module
    else:
        raise ImportError('No smbus module found')


class I2C(SharedMixin, GPIOBase):
    """Interface with an I2C bus.
    """

    def __init__(self, bus=None, interface_class=None, lock=None):
        self.bus = get_default_bus() if bus is None else bus
        interface_class = interface_class or find_smbus_module().SMBus
        self.interface = interface_class(self.bus)
        self.lock = lock or Lock()

    @classmethod
    def _shared_key(cls, *args, **kwargs):
        if args:
            return args[0]

        return kwargs['bus'] if 'bus' in kwargs else get_default_bus()

    def __repr__(self):
        return 'I2C(bus=%r)' % self.bus

    def read(self, device, register, size):
        """Read ``size`` bytes from ``device``'s ``register``.
        """
        with self.lock:
            return self.interface.read_i2c_block_data(device, register, size)

    def write(self, device, register, data):
        """Write ``data`` to ``device``'s ``register``.
        """
        with self.lock:
            self.interface.write_i2c_block_data(device, register, data)
