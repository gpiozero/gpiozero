class GPIODeviceError(Exception):
    pass


class GPIODevice(object):
    def __init__(self, pin=None):
        if pin is None:
            raise GPIODeviceError('No GPIO pin number given')
        self._pin = pin

    @property
    def pin(self):
        return self._pin

