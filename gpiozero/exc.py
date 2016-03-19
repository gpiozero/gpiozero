from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)
str = type('')


class GPIOZeroError(Exception):
    "Base class for all exceptions in GPIO Zero"

class CompositeDeviceError(GPIOZeroError):
    "Base class for errors specific to the CompositeDevice hierarchy"

class GPIODeviceError(GPIOZeroError):
    "Base class for errors specific to the GPIODevice hierarchy"

class GPIODeviceClosed(GPIODeviceError):
    "Error raised when an operation is attempted on a closed device"

class GPIOPinInUse(GPIODeviceError):
    "Error raised when attempting to use a pin already in use by another device"

class GPIOPinMissing(GPIODeviceError, ValueError):
    "Error raised when a pin number is not specified"

class GPIOBadQueueLen(GPIODeviceError, ValueError):
    "Error raised when non-positive queue length is specified"

class GPIOBadSampleWait(GPIODeviceError, ValueError):
    "Error raised when a negative sampling wait period is specified"

class InputDeviceError(GPIODeviceError):
    "Base class for errors specific to the InputDevice hierarchy"

class OutputDeviceError(GPIODeviceError):
    "Base class for errors specified to the OutputDevice hierarchy"

class OutputDeviceBadValue(OutputDeviceError, ValueError):
    "Error raised when ``value`` is set to an invalid value"

class PinError(GPIOZeroError):
    "Base class for errors related to pin implementations"

class PinFixedFunction(PinError, AttributeError):
    "Error raised when attempting to change the function of a fixed type pin"

class PinInvalidFunction(PinError, ValueError):
    "Error raised when attempting to change the function of a pin to an invalid value"

class PinInvalidState(PinError, ValueError):
    "Error raised when attempting to assign an invalid state to a pin"

class PinInvalidPull(PinError, ValueError):
    "Error raised when attempting to assign an invalid pull-up to a pin"

class PinInvalidEdges(PinError, ValueError):
    "Error raised when attempting to assign an invalid edge detection to a pin"

class PinInvalidBounce(PinError, ValueError):
    "Error raised when attempting to assign an invalid bounce time to a pin"

class PinSetInput(PinError, AttributeError):
    "Error raised when attempting to set a read-only pin"

class PinFixedPull(PinError, AttributeError):
    "Error raised when attempting to set the pull of a pin with fixed pull-up"

class PinEdgeDetectUnsupported(PinError, AttributeError):
    "Error raised when attempting to use edge detection on unsupported pins"

class PinPWMError(PinError):
    "Base class for errors related to PWM implementations"

class PinPWMUnsupported(PinPWMError, AttributeError):
    "Error raised when attempting to activate PWM on unsupported pins"

class PinPWMFixedValue(PinPWMError, AttributeError):
    "Error raised when attempting to initialize PWM on an input pin"

