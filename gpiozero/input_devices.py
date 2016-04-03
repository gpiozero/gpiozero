# vim: set fileencoding=utf-8:

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

from .exc import InputDeviceError, GPIODeviceError, GPIODeviceClosed
from .devices import GPIODevice, CompositeDevice
from .threads import GPIOQueue


class InputDevice(GPIODevice):
    """
    Represents a generic GPIO input device.

    This class extends :class:`GPIODevice` to add facilities common to GPIO
    input devices.  The constructor adds the optional *pull_up* parameter to
    specify how the pin should be pulled by the internal resistors. The
    :attr:`~GPIODevice.is_active` property is adjusted accordingly so that
    ``True`` still means active regardless of the :attr:`pull_up` setting.

    :param int pin:
        The GPIO pin (in Broadcom numbering) that the device is connected to.
        If this is ``None`` a :exc:`GPIODeviceError` will be raised.

    :param bool pull_up:
        If ``True``, the pin will be pulled high with an internal resistor. If
        ``False`` (the default), the pin will be pulled low.
    """
    def __init__(self, pin=None, pull_up=False):
        super(InputDevice, self).__init__(pin)
        try:
            self.pin.function = 'input'
            pull = 'up' if pull_up else 'down'
            if self.pin.pull != pull:
                self.pin.pull = pull
        except:
            self.close()
            raise
        self._active_state = False if pull_up else True
        self._inactive_state = True if pull_up else False

    @property
    def pull_up(self):
        """
        If ``True``, the device uses a pull-up resistor to set the GPIO pin
        "high" by default. Defaults to ``False``.
        """
        return self.pin.pull == 'up'

    def __repr__(self):
        try:
            return "<gpiozero.%s object on pin %r, pull_up=%s, is_active=%s>" % (
                self.__class__.__name__, self.pin, self.pull_up, self.is_active)
        except:
            return super(InputDevice, self).__repr__()


class WaitableInputDevice(InputDevice):
    """
    Represents a generic input device with distinct waitable states.

    This class extends :class:`InputDevice` with methods for waiting on the
    device's status (:meth:`wait_for_active` and :meth:`wait_for_inactive`),
    and properties that hold functions to be called when the device changes
    state (:meth:`when_activated` and :meth:`when_deactivated`). These are
    aliased appropriately in various subclasses.

    .. note::

        Note that this class provides no means of actually firing its events;
        it's effectively an abstract base class.
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

        :param float timeout:
            Number of seconds to wait before proceeding. If this is ``None``
            (the default), then wait indefinitely until the device is active.
        """
        return self._active_event.wait(timeout)

    def wait_for_inactive(self, timeout=None):
        """
        Pause the script until the device is deactivated, or the timeout is
        reached.

        :param float timeout:
            Number of seconds to wait before proceeding. If this is ``None``
            (the default), then wait indefinitely until the device is inactive.
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

        Set this property to ``None`` (the default) to disable the event.
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

        Set this property to ``None`` (the default) to disable the event.
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

    This class extends :class:`WaitableInputDevice` with machinery to fire the
    active and inactive events for devices that operate in a typical digital
    manner: straight forward on / off states with (reasonably) clean
    transitions between the two.

    :param float bouncetime:
        Specifies the length of time (in seconds) that the component will
        ignore changes in state after an initial change. This defaults to
        ``None`` which indicates that no bounce compensation will be performed.
    """
    def __init__(self, pin=None, pull_up=False, bounce_time=None):
        super(DigitalInputDevice, self).__init__(pin, pull_up)
        try:
            self.pin.bounce = bounce_time
            self.pin.edges = 'both'
            self.pin.when_changed = self._fire_events
            # Call _fire_events once to set initial state of events
            self._fire_events()
        except:
            self.close()
            raise


class SmoothedInputDevice(WaitableInputDevice):
    """
    Represents a generic input device which takes its value from the mean of a
    queue of historical values.

    This class extends :class:`WaitableInputDevice` with a queue which is
    filled by a background thread which continually polls the state of the
    underlying device. The mean of the values in the queue is compared to a
    threshold which is used to determine the state of the :attr:`is_active`
    property.

    .. note::

        The background queue is not automatically started upon construction.
        This is to allow descendents to set up additional components before the
        queue starts reading values. Effectively this is an abstract base
        class.

    This class is intended for use with devices which either exhibit analog
    behaviour (such as the charging time of a capacitor with an LDR), or those
    which exhibit "twitchy" behaviour (such as certain motion sensors).

    :param float threshold:
        The value above which the device will be considered "on".

    :param int queue_len:
        The length of the internal queue which is filled by the background
        thread.

    :param float sample_wait:
        The length of time to wait between retrieving the state of the
        underlying device. Defaults to 0.0 indicating that values are retrieved
        as fast as possible.

    :param bool partial:
        If ``False`` (the default), attempts to read the state of the device
        (from the :attr:`is_active` property) will block until the queue has
        filled.  If ``True``, a value will be returned immediately, but be
        aware that this value is likely to fluctuate excessively.
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
        determine the overall state of the device. This defaults to 5.
        """
        self._check_open()
        return self._queue.queue.maxlen

    @property
    def partial(self):
        """
        If ``False`` (the default), attempts to read the :attr:`value` or
        :attr:`is_active` properties will block until the queue has filled.
        """
        self._check_open()
        return self._queue.partial

    @property
    def value(self):
        """
        Returns the mean of the values in the internal queue. This is compared
        to :attr:`threshold` to determine whether :attr:`is_active` is
        ``True``.
        """
        self._check_open()
        return self._queue.value

    @property
    def threshold(self):
        """
        If :attr:`value` exceeds this amount, then :attr:`is_active` will
        return ``True``.
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
        Returns ``True`` if the device is currently active and ``False``
        otherwise.
        """
        return self.value > self.threshold


class Button(DigitalInputDevice):
    """
    Extends :class:`DigitalInputDevice` and represents a simple push button
    or switch.

    Connect one side of the button to a ground pin, and the other to any GPIO
    pin. Alternatively, connect one side of the button to the 3V3 pin, and the
    other to any GPIO pin, then set *pull_up* to ``False`` in the
    :class:`Button` constructor.

    The following example will print a line of text when the button is pushed::

        from gpiozero import Button

        button = Button(4)
        button.wait_for_press()
        print("The button was pressed!")

    :param int pin:
        The GPIO pin which the button is attached to. See :doc:`notes` for
        valid pin numbers.

    :param bool pull_up:
        If ``True`` (the default), the GPIO pin will be pulled high by default.
        In this case, connect the other side of the button to ground. If
        ``False``, the GPIO pin will be pulled low by default. In this case,
        connect the other side of the button to 3V3.

    :param float bounce_time:
        If ``None`` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length in time (in seconds) that the
        component will ignore changes in state after an initial change.
    """
    def __init__(self, pin=None, pull_up=True, bounce_time=None):
        super(Button, self).__init__(pin, pull_up, bounce_time)

Button.is_pressed = Button.is_active
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated
Button.wait_for_press = Button.wait_for_active
Button.wait_for_release = Button.wait_for_inactive


class LineSensor(SmoothedInputDevice):
    """
    Extends :class:`DigitalInputDevice` and represents a single pin line sensor
    like the TCRT5000 infra-red proximity sensor found in the `CamJam #3
    EduKit`_.

    A typical line sensor has a small circuit board with three pins: VCC, GND,
    and OUT. VCC should be connected to a 3V3 pin, GND to one of the ground
    pins, and finally OUT to the GPIO specified as the value of the *pin*
    parameter in the constructor.

    The following code will print a line of text indicating when the sensor
    detects a line, or stops detecting a line::

        from gpiozero import LineSensor
        from signal import pause

        sensor = LineSensor(4)
        sensor.when_line = lambda: print('Line detected')
        sensor.when_no_line = lambda: print('No line detected')
        pause()

    :param int pin:
        The GPIO pin which the button is attached to. See :doc:`notes` for
        valid pin numbers.

    :param int queue_len:
        The length of the queue used to store values read from the sensor. This
        defaults to 5.

    :param float sample_rate:
        The number of values to read from the device (and append to the
        internal queue) per second. Defaults to 100.

    :param float threshold:
        Defaults to 0.5. When the mean of all values in the internal queue
        rises above this value, the sensor will be considered "active" by the
        :attr:`~SmoothedInputDevice.is_active` property, and all appropriate
        events will be fired.

    :param bool partial:
        When ``False`` (the default), the object will not return a value for
        :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to ``True`` if you require values
        immediately after object construction.

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    def __init__(
            self, pin=None, queue_len=5, sample_rate=100, threshold=0.5,
            partial=False):
        super(LineSensor, self).__init__(
            pin, pull_up=False, threshold=threshold,
            queue_len=queue_len, sample_wait=1 / sample_rate, partial=partial
        )
        try:
            self._queue.start()
        except:
            self.close()
            raise

    @property
    def line_detected(self):
        return not self.is_active

LineSensor.when_line = LineSensor.when_deactivated
LineSensor.when_no_line = LineSensor.when_activated
LineSensor.wait_for_line = LineSensor.wait_for_inactive
LineSensor.wait_for_no_line = LineSensor.wait_for_active


class MotionSensor(SmoothedInputDevice):
    """
    Extends :class:`SmoothedInputDevice` and represents a passive infra-red
    (PIR) motion sensor like the sort found in the `CamJam #2 EduKit`_.

    .. _CamJam #2 EduKit: http://camjam.me/?page_id=623

    A typical PIR device has a small circuit board with three pins: VCC, OUT,
    and GND. VCC should be connected to a 5V pin, GND to one of the ground
    pins, and finally OUT to the GPIO specified as the value of the *pin*
    parameter in the constructor.

    The following code will print a line of text when motion is detected::

        from gpiozero import MotionSensor

        pir = MotionSensor(4)
        pir.wait_for_motion()
        print("Motion detected!")

    :param int pin:
        The GPIO pin which the button is attached to. See :doc:`notes` for
        valid pin numbers.

    :param int queue_len:
        The length of the queue used to store values read from the sensor. This
        defaults to 1 which effectively disables the queue. If your motion
        sensor is particularly "twitchy" you may wish to increase this value.

    :param float sample_rate:
        The number of values to read from the device (and append to the
        internal queue) per second. Defaults to 100.

    :param float threshold:
        Defaults to 0.5. When the mean of all values in the internal queue
        rises above this value, the sensor will be considered "active" by the
        :attr:`~SmoothedInputDevice.is_active` property, and all appropriate
        events will be fired.

    :param bool partial:
        When ``False`` (the default), the object will not return a value for
        :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to ``True`` if you require values
        immediately after object construction.
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
    Extends :class:`SmoothedInputDevice` and represents a light dependent
    resistor (LDR).

    Connect one leg of the LDR to the 3V3 pin; connect one leg of a 1µf
    capacitor to a ground pin; connect the other leg of the LDR and the other
    leg of the capacitor to the same GPIO pin. This class repeatedly discharges
    the capacitor, then times the duration it takes to charge (which will vary
    according to the light falling on the LDR).

    The following code will print a line of text when light is detected::

        from gpiozero import LightSensor

        ldr = LightSensor(18)
        ldr.wait_for_light()
        print("Light detected!")

    :param int pin:
        The GPIO pin which the button is attached to. See :doc:`notes` for
        valid pin numbers.

    :param int queue_len:
        The length of the queue used to store values read from the circuit.
        This defaults to 5.

    :param float charge_time_limit:
        If the capacitor in the circuit takes longer than this length of time
        to charge, it is assumed to be dark. The default (0.01 seconds) is
        appropriate for a 0.01µf capacitor coupled with the LDR from the
        `CamJam #2 EduKit`_. You may need to adjust this value for different
        valued capacitors or LDRs.

    :param float threshold:
        Defaults to 0.1. When the mean of all values in the internal queue
        rises above this value, the area will be considered "light", and all
        appropriate events will be fired.

    :param bool partial:
        When ``False`` (the default), the object will not return a value for
        :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to ``True`` if you require values
        immediately after object construction.

    .. _CamJam #2 EduKit: http://camjam.me/?page_id=623
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
            self.pin.edges = 'rising'
            self.pin.bounce = None
            self.pin.when_changed = self._charged.set
            self._queue.start()
        except:
            self.close()
            raise

    @property
    def charge_time_limit(self):
        return self._charge_time_limit

    def _read(self):
        # Drain charge from the capacitor
        self.pin.function = 'output'
        self.pin.state = False
        sleep(0.1)
        # Time the charging of the capacitor
        start = time()
        self._charged.clear()
        self.pin.function = 'input'
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


class DistanceSensor(SmoothedInputDevice):
    """
    Extends :class:`SmoothedInputDevice` and represents an HC-SR04 ultrasonic
    distance sensor, as found in the `CamJam #3 EduKit`_.

    The distance sensor requires two GPIO pins: one for the *trigger* (marked
    TRIG on the sensor) and another for the *echo* (marked ECHO on the sensor).
    However, a voltage divider is required to ensure the 5V from the ECHO pin
    doesn't damage the Pi. Wire your sensor according to the following
    instructions:

    1. Connect the GND pin of the sensor to a ground pin on the Pi.

    2. Connect the TRIG pin of the sensor a GPIO pin.

    3. Connect a 330Ω resistor from the ECHO pin of the sensor to a different
       GPIO pin.

    4. Connect a 470Ω resistor from ground to the ECHO GPIO pin. This forms
       the required voltage divider.

    5. Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

    The following code will periodically report the distance measured by the
    sensor in cm assuming the TRIG pin is connected to GPIO17, and the ECHO
    pin to GPIO18::

        from gpiozero import DistanceSensor
        from time import sleep

        sensor = DistanceSensor(18, 17)
        while True:
            print('Distance: ', sensor.distance * 100)
            sleep(1)

    :param int echo:
        The GPIO pin which the ECHO pin is attached to. See :doc:`notes` for
        valid pin numbers.

    :param int trigger:
        The GPIO pin which the TRIG pin is attached to. See :doc:`notes` for
        valid pin numbers.

    :param int queue_len:
        The length of the queue used to store values read from the sensor.
        This defaults to 30.

    :param float max_distance:
        The :attr:`value` attribute reports a normalized value between 0 (too
        close to measure) and 1 (maximum distance). This parameter specifies
        the maximum distance expected in meters. This defaults to 1.

    :param float threshold_distance:
        Defaults to 0.3. This is the distance (in meters) that will trigger the
        ``in_range`` and ``out_of_range`` events when crossed.

    :param bool partial:
        When ``False`` (the default), the object will not return a value for
        :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to ``True`` if you require values
        immediately after object construction.

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    def __init__(
            self, echo=None, trigger=None, queue_len=30, max_distance=1,
            threshold_distance=0.3, partial=False):
        if not (max_distance > 0):
            raise ValueError('invalid maximum distance (must be positive)')
        self._trigger = None
        super(DistanceSensor, self).__init__(
            echo, pull_up=False, threshold=threshold_distance / max_distance,
            queue_len=queue_len, sample_wait=0.0, partial=partial
        )
        try:
            self.speed_of_sound = 343.26 # m/s
            self._max_distance = max_distance
            self._trigger = GPIODevice(trigger)
            self._echo = Event()
            self._trigger.pin.function = 'output'
            self._trigger.pin.state = False
            self.pin.edges = 'both'
            self.pin.bounce = None
            self.pin.when_changed = self._echo.set
            self._queue.start()
        except:
            self.close()
            raise

    def close(self):
        try:
            self._trigger.close()
        except AttributeError:
            if self._trigger is not None:
                raise
        else:
            self._trigger = None
        super(DistanceSensor, self).close()

    @property
    def max_distance(self):
        """
        The maximum distance that the sensor will measure in meters. This value
        is specified in the constructor and is used to provide the scaling
        for the :attr:`value` attribute. When :attr:`distance` is equal to
        :attr:`max_distance`, :attr:`value` will be 1.
        """
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        if not (value > 0):
            raise ValueError('invalid maximum distance (must be positive)')
        t = self.threshold_distance
        self._max_distance = value
        self.threshold_distance = t

    @property
    def threshold_distance(self):
        """
        The distance, measured in meters, that will trigger the
        :attr:`when_in_range` and :attr:`when_out_of_range` events when
        crossed. This is simply a meter-scaled variant of the usual
        :attr:`threshold` attribute.
        """
        return self.threshold * self.max_distance

    @threshold_distance.setter
    def threshold_distance(self, value):
        self.threshold = value / self.max_distance

    @property
    def distance(self):
        """
        Returns the current distance measured by the sensor in meters. Note
        that this property will have a value between 0 and
        :attr:`max_distance`.
        """
        return self.value * self._max_distance

    @property
    def trigger(self):
        """
        Returns the :class:`Pin` that the sensor's trigger is connected to.
        """
        return self._trigger.pin

    @property
    def echo(self):
        """
        Returns the :class:`Pin` that the sensor's echo is connected to. This
        is simply an alias for the usual :attr:`pin` attribute.
        """
        return self.pin

    def _read(self):
        # Make sure the echo event is clear
        self._echo.clear()
        # Fire the trigger
        self._trigger.pin.state = True
        sleep(0.00001)
        self._trigger.pin.state = False
        # Wait up to 1 second for the echo pin to rise
        if self._echo.wait(1):
            start = time()
            self._echo.clear()
            # Wait up to 40ms for the echo pin to fall (35ms is maximum pulse
            # time so any longer means something's gone wrong). Calculate
            # distance as time for echo multiplied by speed of sound divided by
            # two to compensate for travel to and from the reflector
            if self._echo.wait(0.04):
                distance = (time() - start) * self.speed_of_sound / 2.0
                return min(1.0, distance / self._max_distance)
            else:
                # If we only saw one edge it means we missed the echo because
                # it was too fast; report minimum distance
                return 0.0
        else:
            # The echo pin never rose or fell; something's gone horribly
            # wrong (XXX raise a warning?)
            return 1.0

    @property
    def in_range(self):
        return not self.is_active

DistanceSensor.when_out_of_range = DistanceSensor.when_activated
DistanceSensor.when_in_range = DistanceSensor.when_deactivated
DistanceSensor.wait_for_out_of_range = DistanceSensor.wait_for_active
DistanceSensor.wait_for_in_range = DistanceSensor.wait_for_inactive

