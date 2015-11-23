from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

import inspect
import warnings
from functools import wraps
from time import sleep, time
from threading import Event

from RPi import GPIO
from spidev import SpiDev

from .devices import (
    GPIODeviceError,
    GPIODeviceClosed,
    GPIODevice,
    CompositeDevice,
    GPIOQueue,
)


class InputDeviceError(GPIODeviceError):
    pass


class InputDevice(GPIODevice):
    """
    Represents a generic GPIO input device.

    This class extends `GPIODevice` to add facilities common to GPIO input
    devices.  The constructor adds the optional `pull_up` parameter to specify
    how the pin should be pulled by the internal resistors. The `is_active`
    property is adjusted accordingly so that `True` still means active
    regardless of the `pull_up` setting.

    pin: `None`
        The GPIO pin (in BCM numbering) that the device is connected to. If
        this is `None` a GPIODeviceError will be raised.

    pull_up: `False`
        If `True`, the pin will be pulled high with an internal resistor. If
        `False` (the default), the pin will be pulled low.
    """
    def __init__(self, pin=None, pull_up=False):
        if pin in (2, 3) and not pull_up:
            raise InputDeviceError(
                'GPIO pins 2 and 3 are fitted with physical pull up '
                'resistors; you cannot initialize them with pull_up=False'
            )
        # _pull_up should be assigned first as __repr__ relies upon it to
        # support the case where __repr__ is called during debugging of an
        # instance that has failed to initialize (due to an exception in the
        # super-class __init__)
        self._pull_up = pull_up
        super(InputDevice, self).__init__(pin)
        self._active_edge = GPIO.FALLING if pull_up else GPIO.RISING
        self._inactive_edge = GPIO.RISING if pull_up else GPIO.FALLING
        self._active_state = GPIO.LOW if pull_up else GPIO.HIGH
        self._inactive_state = GPIO.HIGH if pull_up else GPIO.LOW
        pull = GPIO.PUD_UP if pull_up else GPIO.PUD_DOWN

        try:
            # NOTE: catch_warnings isn't thread-safe but hopefully no-one's
            # messing around with GPIO init within background threads...
            with warnings.catch_warnings(record=True) as w:
                GPIO.setup(pin, GPIO.IN, pull)
            # The only warning we want to squash is a RuntimeWarning that is
            # thrown when setting pins 2 or 3. Anything else should be replayed
            for warning in w:
                if warning.category != RuntimeWarning or pin not in (2, 3):
                    warnings.showwarning(
                        warning.message, warning.category, warning.filename,
                        warning.lineno, warning.file, warning.line
                    )
        except:
            self.close()
            raise

    @property
    def pull_up(self):
        """
        If `True`, the device uses a pull-up resistor to set the GPIO pin
        "high" by default. Defaults to `False`.
        """
        return self._pull_up

    def __repr__(self):
        try:
            return "<gpiozero.%s object on pin=%d, pull_up=%s, is_active=%s>" % (
                self.__class__.__name__, self.pin, self.pull_up, self.is_active)
        except:
            return super(InputDevice, self).__repr__()


class WaitableInputDevice(InputDevice):
    """
    Represents a generic input device with distinct waitable states.

    This class extends `InputDevice` with methods for waiting on the device's
    status (`wait_for_active` and `wait_for_inactive`), and properties that
    hold functions to be called when the device changes state (`when_activated`
    and `when_deactivated`). These are aliased appropriately in various
    subclasses.

    Note that this class provides no means of actually firing its events; it's
    effectively an abstract base class.
    """
    def __init__(self, pin=None, pull_up=False):
        super(WaitableInputDevice, self).__init__(pin, pull_up)
        self._active_event = Event()
        self._inactive_event = Event()
        self._when_activated = None
        self._when_deactivated = None
        self._last_state = None

    def wait_for_active(self, timeout=None):
        """
        Pause the script until the device is activated, or the timeout is
        reached.

        timeout: `None`
            Number of seconds to wait before proceeding. If this is `None` (the
            default), then wait indefinitely until the device is active.
        """
        return self._active_event.wait(timeout)

    def wait_for_inactive(self, timeout=None):
        """
        Pause the script until the device is deactivated, or the timeout is
        reached.

        timeout: `None`
            Number of seconds to wait before proceeding. If this is `None` (the
            default), then wait indefinitely until the device is inactive.
        """
        return self._inactive_event.wait(timeout)

    @property
    def when_activated(self):
        """
        The function to run when the device changes state from inactive to
        active.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to `None` (the default) to disable the event.

        See also: when_deactivated.
        """
        return self._when_activated

    @when_activated.setter
    def when_activated(self, value):
        self._when_activated = self._wrap_callback(value)

    @property
    def when_deactivated(self):
        """
        The function to run when the device changes state from active to
        inactive.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that deactivated will be
        passed as that parameter.

        Set this property to `None` (the default) to disable the event.

        See also: when_activated.
        """
        return self._when_deactivated

    @when_deactivated.setter
    def when_deactivated(self, value):
        self._when_deactivated = self._wrap_callback(value)

    def _wrap_callback(self, fn):
        if fn is None:
            return None
        elif not callable(fn):
            raise InputDeviceError('value must be None or a callable')
        elif inspect.isbuiltin(fn):
            # We can't introspect the prototype of builtins. In this case we
            # assume that the builtin has no (mandatory) parameters; this is
            # the most reasonable assumption on the basis that pre-existing
            # builtins have no knowledge of gpiozero, and the sole parameter
            # we would pass is a gpiozero object
            return fn
        else:
            # Try binding ourselves to the argspec of the provided callable.
            # If this works, assume the function is capable of accepting no
            # parameters
            try:
                inspect.getcallargs(fn)
                return fn
            except TypeError:
                try:
                    # If the above fails, try binding with a single parameter
                    # (ourselves). If this works, wrap the specified callback
                    inspect.getcallargs(fn, self)
                    @wraps(fn)
                    def wrapper():
                        return fn(self)
                    return wrapper
                except TypeError:
                    raise InputDeviceError(
                        'value must be a callable which accepts up to one '
                        'mandatory parameter')

    def _fire_events(self):
        old_state = self._last_state
        new_state = self._last_state = self.is_active
        if old_state is None:
            # Initial "indeterminate" state; set events but don't fire
            # callbacks as there's not necessarily an edge
            if new_state:
                self._active_event.set()
            else:
                self._inactive_event.set()
        else:
            if not old_state and new_state:
                self._inactive_event.clear()
                self._active_event.set()
                if self.when_activated:
                    self.when_activated()
            elif old_state and not new_state:
                self._active_event.clear()
                self._inactive_event.set()
                if self.when_deactivated:
                    self.when_deactivated()


class DigitalInputDevice(WaitableInputDevice):
    """
    Represents a generic input device with typical on/off behaviour.

    This class extends `WaitableInputDevice` with machinery to fire the active
    and inactive events for devices that operate in a typical digital manner:
    straight forward on / off states with (reasonably) clean transitions
    between the two.

    bounce_time: `None`
        Specifies the length of time (in seconds) that the component will
        ignore changes in state after an initial change. This defaults to
        `None` which indicates that no bounce compensation will be performed.
    """
    def __init__(self, pin=None, pull_up=False, bounce_time=None):
        super(DigitalInputDevice, self).__init__(pin, pull_up)
        try:
            # Yes, that's really the default bouncetime in RPi.GPIO...
            GPIO.add_event_detect(
                self.pin, GPIO.BOTH, callback=self._fire_events,
                bouncetime=-666 if bounce_time is None else int(bounce_time * 1000)
            )
            # Call _fire_events once to set initial state of events
            super(DigitalInputDevice, self)._fire_events()
        except:
            self.close()
            raise

    def _fire_events(self, channel):
        super(DigitalInputDevice, self)._fire_events()


class SmoothedInputDevice(WaitableInputDevice):
    """
    Represents a generic input device which takes its value from the mean of a
    queue of historical values.

    This class extends `WaitableInputDevice` with a queue which is filled by a
    background thread which continually polls the state of the underlying
    device. The mean of the values in the queue is compared to a threshold
    which is used to determine the state of the `is_active` property.

    This class is intended for use with devices which either exhibit analog
    behaviour (such as the charging time of a capacitor with an LDR), or those
    which exhibit "twitchy" behaviour (such as certain motion sensors).

    threshold: `0.5`
        The value above which the device will be considered "on".

    queue_len: `5`
        The length of the internal queue which is filled by the background
        thread.

    sample_wait: `0.0`
        The length of time to wait between retrieving the state of the
        underlying device. Defaults to 0.0 indicating that values are retrieved
        as fast as possible.

    partial: `False`
        If `False` (the default), attempts to read the state of the device
        (from the `is_active` property) will block until the queue has filled.
        If `True`, a value will be returned immediately, but be aware that this
        value is likely to fluctuate excessively.
    """
    def __init__(
            self, pin=None, pull_up=False, threshold=0.5,
            queue_len=5, sample_wait=0.0, partial=False):
        self._queue = None
        super(SmoothedInputDevice, self).__init__(pin, pull_up)
        try:
            self._queue = GPIOQueue(self, queue_len, sample_wait, partial)
            self.threshold = float(threshold)
        except:
            self.close()
            raise

    def close(self):
        try:
            self._queue.stop()
        except AttributeError:
            # If the queue isn't initialized (it's None) ignore the error
            # because we're trying to close anyway
            if self._queue is not None:
                raise
        except RuntimeError:
            # Cannot join thread before it starts; we don't care about this
            # because we're trying to close the thread anyway
            pass
        else:
            self._queue = None
        super(SmoothedInputDevice, self).close()

    def __repr__(self):
        try:
            self._check_open()
        except GPIODeviceClosed:
            return super(SmoothedInputDevice, self).__repr__()
        else:
            if self.partial or self._queue.full.wait(0):
                return super(SmoothedInputDevice, self).__repr__()
            else:
                return "<gpiozero.%s object on pin=%d, pull_up=%s>" % (
                    self.__class__.__name__, self.pin, self.pull_up)

    @property
    def queue_len(self):
        """
        The length of the internal queue of values which is averaged to
        determine the overall state of the device. This defaults to `5`.
        """
        self._check_open()
        return self._queue.queue.maxlen

    @property
    def partial(self):
        """
        If `False` (the default), attempts to read the `value` or `is_active`
        properties will block until the queue has filled.
        """
        self._check_open()
        return self._queue.partial

    @property
    def value(self):
        """
        Returns the mean of the values in the internal queue. This is
        compared to `threshold` to determine whether `is_active` is `True`.
        """
        self._check_open()
        return self._queue.value

    @property
    def threshold(self):
        """
        If `value` exceeds this amount, then `is_active` will return `True`.
        """
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if not (0.0 < value < 1.0):
            raise InputDeviceError(
                'threshold must be between zero and one exclusive'
            )
        self._threshold = float(value)

    @property
    def is_active(self):
        """
        Returns `True` if the device is currently active and `False` otherwise.
        """
        return self.value > self.threshold


class Button(DigitalInputDevice):
    """
    A physical push button or switch.

    A typical configuration of such a device is to connect a GPIO pin to one
    side of the switch, and ground to the other (the default `pull_up` value
    is `True`).
    """
    def __init__(self, pin=None, pull_up=True, bounce_time=None):
        super(Button, self).__init__(pin, pull_up, bounce_time)

Button.is_pressed = Button.is_active
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated
Button.wait_for_press = Button.wait_for_active
Button.wait_for_release = Button.wait_for_inactive


class LineSensor(DigitalInputDevice):
    """
    A single sensor line detector.
    """
    def __init__(self, pin=None, pull_up=True, bounce_time=None):
        super(LineSensor, self).__init__(pin, pull_up, bounce_time)

LineSensor.line_detected = LineSensor.is_active
LineSensor.when_line = LineSensor.when_activated
LineSensor.when_no_line = LineSensor.when_deactivated
LineSensor.wait_for_line = LineSensor.wait_for_active
LineSensor.wait_for_no_line = LineSensor.wait_for_inactive


class MotionSensor(SmoothedInputDevice):
    """
    A PIR (Passive Infra-Red) motion sensor.

    A typical PIR device has a small circuit board with three pins: VCC, OUT,
    and GND. VCC should be connected to the Pi's +5V pin, GND to one of the
    Pi's ground pins, and finally OUT to the GPIO specified as the value of the
    `pin` parameter in the constructor.

    This class defaults `queue_len` to 1, effectively removing the averaging
    of the internal queue. If your PIR sensor has a short fall time and is
    particularly "jittery" you may wish to set this to a higher value (e.g. 5)
    to mitigate this.
    """
    def __init__(
            self, pin=None, queue_len=1, sample_rate=10, threshold=0.5,
            partial=False):
        super(MotionSensor, self).__init__(
            pin, pull_up=False, threshold=threshold,
            queue_len=queue_len, sample_wait=1 / sample_rate, partial=partial
        )
        try:
            self._queue.start()
        except:
            self.close()
            raise

MotionSensor.motion_detected = MotionSensor.is_active
MotionSensor.when_motion = MotionSensor.when_activated
MotionSensor.when_no_motion = MotionSensor.when_deactivated
MotionSensor.wait_for_motion = MotionSensor.wait_for_active
MotionSensor.wait_for_no_motion = MotionSensor.wait_for_inactive


class LightSensor(SmoothedInputDevice):
    """
    An LDR (Light Dependent Resistor) Light Sensor.

    A typical LDR circuit connects one side of the LDR to the 3v3 line from the
    Pi, and the other side to a GPIO pin, and a capacitor tied to ground. This
    class repeatedly discharges the capacitor, then times the duration it takes
    to charge (which will vary according to the light falling on the LDR).
    """
    def __init__(
            self, pin=None, queue_len=5, charge_time_limit=0.01,
            threshold=0.1, partial=False):
        super(LightSensor, self).__init__(
            pin, pull_up=False, threshold=threshold,
            queue_len=queue_len, sample_wait=0.0, partial=partial
        )
        try:
            self._charge_time_limit = charge_time_limit
            self._charged = Event()
            GPIO.add_event_detect(
                self.pin, GPIO.RISING, lambda channel: self._charged.set()
            )
            self._queue.start()
        except:
            self.close()
            raise

    @property
    def charge_time_limit(self):
        return self._charge_time_limit

    def _read(self):
        # Drain charge from the capacitor
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        sleep(0.1)
        # Time the charging of the capacitor
        start = time()
        self._charged.clear()
        GPIO.setup(self.pin, GPIO.IN)
        self._charged.wait(self.charge_time_limit)
        return (
            1.0 - min(self.charge_time_limit, time() - start) /
            self.charge_time_limit
        )

LightSensor.light_detected = LightSensor.is_active
LightSensor.when_light = LightSensor.when_activated
LightSensor.when_dark = LightSensor.when_deactivated
LightSensor.wait_for_light = LightSensor.wait_for_active
LightSensor.wait_for_dark = LightSensor.wait_for_inactive


class AnalogInputDevice(CompositeDevice):
    """
    Represents an analog input device connected to SPI (serial interface).
    """

    def __init__(self, device=0, bits=None):
        if bits is None:
            raise InputDeviceError('you must specify the bit resolution of the device')
        if device not in (0, 1):
            raise InputDeviceError('device must be 0 or 1')
        self._device = device
        self._bits = bits
        self._spi = SpiDev()
        self._spi.open(0, self.device)
        super(AnalogInputDevice, self).__init__()

    def close(self):
        """
        Shut down the device and release all associated resources.
        """
        if self._spi:
            s = self._spi
            self._spi = None
            s.close()
        super(AnalogInputDevice, self).close()

    @property
    def bus(self):
        """
        The SPI bus that the device is connected to. As the Pi only has a
        single (user accessible) SPI bus, this always returns 0.
        """
        return 0

    @property
    def device(self):
        """
        The select pin that the device is connected to. The Pi has two select
        pins so this will be 0 or 1.
        """
        return self._device

    def _read(self):
        raise NotImplementedError

    @property
    def value(self):
        """
        A value read from the device. This will be a floating point value
        between 0 and 1 (scaled according to the number of bits supported by
        the device).
        """
        return self._read() / (2**self._bits - 1)


class MCP3008(AnalogInputDevice):
    def __init__(self, channel=0, device=0):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3008, self).__init__(device=device, bits=10)
        self._channel = channel

    @property
    def channel(self):
        """
        The channel to read data from. The MCP3008 has 8 channels (so this will
        be between 0 and 7) while the MCP3004 has 4 channels (range 0 to 3).
        """
        return self._channel

    def _read(self):
        # MCP3008 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   00000001 MCCCxxxx xxxxxxxx
        #     Rx   xxxxxxxx xxxxx0RR RRRRRRRR
        #
        # The first byte sent is a start byte (1). The top bit of the second
        # holds the mode (M) which is 1 for single-ended read, and 0 for
        # differential read (we only support single here), followed by 3-bits
        # for the channel (C). The remainder of the transmission are "don't
        # care" bits (x).
        #
        # The first byte and the top 5 bits of the second byte received are
        # don't care bits (x). These are followed by a null bit (0), and then
        # the 10 bits of the result (R).
        data = self._spi.xfer2([1, (8 + self.channel) << 4, 0])
        return ((data[1] & 3) << 8) | data[2]


class MCP3004(MCP3008):
    def __init__(self, channel=0, device=0):
        # MCP3004 protocol is identical to MCP3008 but the top bit of the
        # channel number must be 0 (effectively restricting it to 4 channels)
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 3')
        super(MCP3004, self).__init__(channel, device)
