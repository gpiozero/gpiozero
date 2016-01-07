from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

class GPIODeviceError(Exception):
    pass

class GPIODeviceClosed(GPIODeviceError):
    pass

class InputDeviceError(GPIODeviceError):
    pass

class OutputDeviceError(GPIODeviceError):
    pass

