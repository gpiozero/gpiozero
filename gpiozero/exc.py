# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Kosovan Sofiia <sofiia.kosovan@gmail.com>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause


class GPIOZeroError(Exception):
    "Base class for all exceptions in GPIO Zero"

class DeviceClosed(GPIOZeroError):
    "Error raised when an operation is attempted on a closed device"

class BadEventHandler(GPIOZeroError, ValueError):
    "Error raised when an event handler with an incompatible prototype is specified"

class BadWaitTime(GPIOZeroError, ValueError):
    "Error raised when an invalid wait time is specified"

class BadQueueLen(GPIOZeroError, ValueError):
    "Error raised when non-positive queue length is specified"

class BadPinFactory(GPIOZeroError, ImportError):
    "Error raised when an unknown pin factory name is specified"

class ZombieThread(GPIOZeroError, RuntimeError):
    "Error raised when a thread fails to die within a given timeout"

class CompositeDeviceError(GPIOZeroError):
    "Base class for errors specific to the CompositeDevice hierarchy"

class CompositeDeviceBadName(CompositeDeviceError, ValueError):
    "Error raised when a composite device is constructed with a reserved name"

class CompositeDeviceBadOrder(CompositeDeviceError, ValueError):
    "Error raised when a composite device is constructed with an incomplete order"

class CompositeDeviceBadDevice(CompositeDeviceError, ValueError):
    "Error raised when a composite device is constructed with an object that doesn't inherit from :class:`Device`"

class EnergenieSocketMissing(CompositeDeviceError, ValueError):
    "Error raised when socket number is not specified"

class EnergenieBadSocket(CompositeDeviceError, ValueError):
    "Error raised when an invalid socket number is passed to :class:`Energenie`"

class SPIError(GPIOZeroError):
    "Base class for errors related to the SPI implementation"

class SPIBadArgs(SPIError, ValueError):
    "Error raised when invalid arguments are given while constructing :class:`SPIDevice`"

class SPIBadChannel(SPIError, ValueError):
    "Error raised when an invalid channel is given to an :class:`AnalogInputDevice`"

class SPIFixedClockMode(SPIError, AttributeError):
    "Error raised when the SPI clock mode cannot be changed"

class SPIInvalidClockMode(SPIError, ValueError):
    "Error raised when an invalid clock mode is given to an SPI implementation"

class SPIFixedBitOrder(SPIError, AttributeError):
    "Error raised when the SPI bit-endianness cannot be changed"

class SPIFixedSelect(SPIError, AttributeError):
    "Error raised when the SPI select polarity cannot be changed"

class SPIFixedWordSize(SPIError, AttributeError):
    "Error raised when the number of bits per word cannot be changed"

class SPIFixedRate(SPIError, AttributeError):
    "Error raised when the baud-rate of the interface cannot be changed"

class SPIInvalidWordSize(SPIError, ValueError):
    "Error raised when an invalid (out of range) number of bits per word is specified"

class GPIODeviceError(GPIOZeroError):
    "Base class for errors specific to the GPIODevice hierarchy"

class GPIODeviceClosed(GPIODeviceError, DeviceClosed):
    "Deprecated descendent of :exc:`DeviceClosed`"

class GPIOPinInUse(GPIODeviceError):
    "Error raised when attempting to use a pin already in use by another device"

class GPIOPinMissing(GPIODeviceError, ValueError):
    "Error raised when a pin specification is not given"

class InputDeviceError(GPIODeviceError):
    "Base class for errors specific to the InputDevice hierarchy"

class OutputDeviceError(GPIODeviceError):
    "Base class for errors specified to the OutputDevice hierarchy"

class OutputDeviceBadValue(OutputDeviceError, ValueError):
    "Error raised when ``value`` is set to an invalid value"

class PinError(GPIOZeroError):
    "Base class for errors related to pin implementations"

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

class PinUnsupported(PinError, NotImplementedError):
    "Error raised when attempting to obtain a pin interface on unsupported pins"

class PinSPIUnsupported(PinError, NotImplementedError):
    "Error raised when attempting to obtain an SPI interface on unsupported pins"

class PinPWMError(PinError):
    "Base class for errors related to PWM implementations"

class PinPWMUnsupported(PinPWMError, AttributeError):
    "Error raised when attempting to activate PWM on unsupported pins"

class PinPWMFixedValue(PinPWMError, AttributeError):
    "Error raised when attempting to initialize PWM on an input pin"

class PinUnknownPi(PinError, RuntimeError):
    "Error raised when gpiozero doesn't recognize a revision of the Pi"

class PinMultiplePins(PinError, RuntimeError):
    "Error raised when multiple pins support the requested function"

class PinNoPins(PinError, RuntimeError):
    "Error raised when no pins support the requested function"

class PinInvalidPin(PinError, ValueError):
    "Error raised when an invalid pin specification is provided"

class GPIOZeroWarning(Warning):
    "Base class for all warnings in GPIO Zero"

class DistanceSensorNoEcho(GPIOZeroWarning):
    "Warning raised when the distance sensor sees no echo at all"

class SPIWarning(GPIOZeroWarning):
    "Base class for warnings related to the SPI implementation"

class SPISoftwareFallback(SPIWarning):
    "Warning raised when falling back to the SPI software implementation"

class PWMWarning(GPIOZeroWarning):
    "Base class for PWM warnings"

class PWMSoftwareFallback(PWMWarning):
    "Warning raised when falling back to the PWM software implementation"

class PinWarning(GPIOZeroWarning):
    "Base class for warnings related to pin implementations"

class PinFactoryFallback(PinWarning):
    "Warning raised when a default pin factory fails to load and a fallback is tried"

class NativePinFactoryFallback(PinWarning):
    "Warning raised when all other default pin factories fail to load and NativeFactory is used"

class PinNonPhysical(PinWarning):
    "Warning raised when a non-physical pin is specified in a constructor"

class ThresholdOutOfRange(GPIOZeroWarning):
    "Warning raised when a threshold is out of range specified by min and max values"

class CallbackSetToNone(GPIOZeroWarning):
    "Warning raised when a callback is set to None when its previous value was None"

class AmbiguousTone(GPIOZeroWarning):
    "Warning raised when a Tone is constructed with an ambiguous number"
