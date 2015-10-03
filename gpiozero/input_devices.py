from __future__ import division

import inspect
import warnings
from functools import wraps
from time import sleep, time
from threading import Event

from RPi import GPIO
from w1thermsensor import W1ThermSensor
from spidev import SpiDev

from .devices import GPIODeviceError, GPIODeviceClosed, GPIODevice, GPIOQueue


def _alias(key, doc=None):
    if doc is None:
        doc = 'Alias for %s' % key
    return property(
        lambda self: getattr(self, key),
        lambda self, val: setattr(self, key, val),
        doc=doc
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

        # NOTE: catch_warnings isn't thread-safe but hopefully no-one's messing
        # around with GPIO init within background threads...
        with warnings.catch_warnings(record=True) as w:
            GPIO.setup(pin, GPIO.IN, pull)
        # The only warning we want to squash is a RuntimeWarning that is thrown
        # when setting pins 2 or 3. Anything else should be replayed
        for warning in w:
            if warning.category != RuntimeWarning or pin not in (2, 3):
                warnings.showwarning(
                    warning.message, warning.category, warning.filename,
                    warning.lineno, warning.file, warning.line
                )

    @property
    def pull_up(self):
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
        Halt the program until the device is activated, or the timeout is
        reached.

        timeout: `None`
            Number of seconds to wait before proceeding. If this is `None` (the
            default), then wait indefinitely until the device is active.
        """
        return self._active_event.wait(timeout)

    def wait_for_inactive(self, timeout=None):
        """
        Halt the program until the device is deactivated, or the timeout is
        reached.

        timeout: `None`
            Number of seconds to wait before proceeding. If this is `None` (the
            default), then wait indefinitely until the device is inactive.
        """
        return self._inactive_event.wait(timeout)

    def _get_when_activated(self):
        return self._when_activated

    def _set_when_activated(self, value):
        self._when_activated = self._wrap_callback(value)

    when_activated = property(_get_when_activated, _set_when_activated, doc="""\
        The function to run when the device changes state from inactive to
        active.

        This can be set to a function which accepts no (mandatory) parameters,
        or a function which accepts a single mandatory parameter (with as many
        optional parameters as you like). If the function accepts a single
        mandatory parameter, the device that activates will be passed as that
        parameter.

        Set this property to `None` (the default) to disable the event.

        See also: when_deactivated.
        """)

    def _get_when_deactivated(self):
        return self._when_deactivated

    def _set_when_deactivated(self, value):
        self._when_deactivated = self._wrap_callback(value)

    when_deactivated = property(_get_when_deactivated, _set_when_deactivated, doc="""\
        The function to run when the device changes state from active to
        inactive.

        This can be set to a function which accepts no (mandatory) parameters,
        or a function which accepts a single mandatory parameter (which as
        many optional parameters as you like). If the function accepts a single
        mandatory parameter, the device the deactives will be passed as that
        parameter.

        Set this property to `None` (the default) to disable the event.

        See also: when_activated.
        """)

    def _wrap_callback(self, fn):
        if fn is None:
            return None
        elif not callable(fn):
            raise InputDeviceError('value must be None or a callable')
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
        # Yes, that's really the default bouncetime in RPi.GPIO...
        GPIO.add_event_detect(
            self.pin, GPIO.BOTH, callback=self._fire_events,
            bouncetime=-666 if bounce_time is None else int(bounce_time * 1000)
        )
        # Call _fire_events once to set initial state of events
        super(DigitalInputDevice, self)._fire_events()

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
        self._queue = GPIOQueue(self, queue_len, sample_wait, partial)
        self.threshold = float(threshold)

    def close(self):
        try:
            self._queue.stop()
        except AttributeError:
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

    def _get_threshold(self):
        return self._threshold

    def _set_threshold(self, value):
        if not (0.0 < value < 1.0):
            raise InputDeviceError(
                'threshold must be between zero and one exclusive'
            )
        self._threshold = float(value)

    threshold = property(_get_threshold, _set_threshold, doc="""\
        If `value` exceeds this amount, then `is_active` will return `True`.
        """)

    @property
    def is_active(self):
        return self.value > self.threshold


class Button(DigitalInputDevice):
    """
    A physical push button or switch.

    A typical configuration of such a device is to connect a GPIO pin to one
    side of the switch, and ground to the other (the default `pull_up` value
    is `True`).
    """
    def __init__(self, pin=None, pull_up=True, bouncetime=None):
        super(Button, self).__init__(pin, pull_up, bouncetime)

    is_pressed = _alias('is_active')

    when_pressed = _alias('when_activated')
    when_released = _alias('when_deactivated')

    wait_for_press = _alias('wait_for_active')
    wait_for_release = _alias('wait_for_inactive')


class MotionSensor(SmoothedInputDevice):
    """
    A PIR (Passive Infra-Red) motion sensor.

    A typical PIR device has a small circuit board with three pins: VCC, OUT,
    and GND. VCC should be connected to the Pi's +5V pin, GND to one of the
    Pi's ground pins, and finally OUT to the GPIO specified as the value of the
    `pin` parameter in the constructor.
    """
    def __init__(
            self, pin=None, queue_len=5, sample_rate=10, threshold=0.5,
            partial=False):
        super(MotionSensor, self).__init__(
            pin, pull_up=False, threshold=threshold,
            queue_len=queue_len, sample_wait=1 / sample_rate, partial=partial
        )
        self._queue.start()

    motion_detected = _alias('is_active')

    when_motion = _alias('when_activated')
    when_no_motion = _alias('when_deactivated')

    wait_for_motion = _alias('wait_for_active')
    wait_for_no_motion = _alias('wait_for_inactive')


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
        self._charge_time_limit = charge_time_limit
        self._charged = Event()
        GPIO.add_event_detect(
            self.pin, GPIO.RISING, lambda channel: self._charged.set()
        )
        self._queue.start()

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

    light_detected = _alias('is_active')

    when_light = _alias('when_activated')
    when_dark = _alias('when_deactivated')

    wait_for_light = _alias('wait_for_active')
    wait_for_dark = _alias('wait_for_inactive')


class TemperatureSensor(W1ThermSensor):
    """
    A Digital Temperature Sensor.
    """
    @property
    def value(self):
        return self.get_temperature()


class MCP3008(object):
    """
    MCP3008 ADC (Analogue-to-Digital converter).
    """
    def __init__(self, bus=0, device=0, channel=0):
        self.bus = bus
        self.device = device
        self.channel = channel
        self.spi = SpiDev()

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.spi.open(self.bus, self.device)

    def read(self):
        adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.spi.close()
