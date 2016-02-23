# vim: set fileencoding=utf-8:

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

import inspect
from functools import wraps
from time import sleep, time
from threading import Event

from spidev import SpiDev

from .exc import InputDeviceError, GPIODeviceError, GPIODeviceClosed
from .devices import GPIODevice, CompositeDevice, GPIOQueue


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
            if self.pin.function != 'input':
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
        internal queue) per second. Defaults to 10.

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
        if max_distance <= 0:
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

DistanceSensor.when_out_of_range = DistanceSensor.when_activated
DistanceSensor.when_in_range = DistanceSensor.when_deactivated
DistanceSensor.wait_for_out_of_range = DistanceSensor.wait_for_active
DistanceSensor.wait_for_in_range = DistanceSensor.wait_for_inactive


class AnalogInputDevice(CompositeDevice):
    """
    Represents an analog input device connected to SPI (serial interface).

    Typical analog input devices are `analog to digital converters`_ (ADCs).
    Several classes are provided for specific ADC chips, including
    :class:`MCP3004`, :class:`MCP3008`, :class:`MCP3204`, and :class:`MCP3208`.

    The following code demonstrates reading the first channel of an MCP3008
    chip attached to the Pi's SPI pins::

        from gpiozero import MCP3008

        pot = MCP3008(0)
        print(pot.value)

    The :attr:`value` attribute is normalized such that its value is always
    between 0.0 and 1.0 (or in special cases, such as differential sampling,
    -1 to +1). Hence, you can use an analog input to control the brightness of
    a :class:`PWMLED` like so::

        from gpiozero import MCP3008, PWMLED

        pot = MCP3008(0)
        led = PWMLED(17)
        led.source = pot.values

    .. _analog to digital converters: https://en.wikipedia.org/wiki/Analog-to-digital_converter
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
    def bits(self):
        """
        The bit-resolution of the device/channel.
        """
        return self._bits

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
        The current value read from the device, scaled to a value between 0 and
        1.
        """
        return self._read() / (2**self.bits - 1)

    @property
    def raw_value(self):
        """
        The raw value as read from the device.
        """
        return self._read()


class MCP3xxx(AnalogInputDevice):
    """
    Extends :class:`AnalogInputDevice` to implement an interface for all ADC
    chips with a protocol similar to the Microchip MCP3xxx series of devices.
    """

    def __init__(self, channel=0, device=0, bits=10, differential=False):
        self._channel = channel
        self._bits = bits
        self._differential = bool(differential)
        super(MCP3xxx, self).__init__(device, bits)

    @property
    def channel(self):
        """
        The channel to read data from. The MCP3008/3208/3304 have 8 channels
        (0-7), while the MCP3004/3204/3302 have 4 channels (0-3), and the
        MCP3301 only has 1 channel.
        """
        return self._channel

    @property
    def differential(self):
        """
        If ``True``, the device is operated in pseudo-differential mode. In
        this mode one channel (specified by the channel attribute) is read
        relative to the value of a second channel (implied by the chip's
        design).

        Please refer to the device data-sheet to determine which channel is
        used as the relative base value (for example, when using an
        :class:`MCP3008` in differential mode, channel 0 is read relative to
        channel 1).
        """
        return self._differential

    def _read(self):
        # MCP3008/04 or MCP3208/04 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   0001MCCC xxxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx x0RRRRRR RRRRxxxx for the 3004/08
        #     Rx   xxxxxxxx x0RRRRRR RRRRRRxx for the 3204/08
        #
        # The transmit bits start with 3 preamble bits "000" (to warm up), a
        # start bit "1" followed by the single/differential bit (M) which is 1
        # for single-ended read, and 0 for differential read, followed by
        # 3-bits for the channel (C). The remainder of the transmission are
        # "don't care" bits (x).
        #
        # The first byte received and the top 1 bit of the second byte are
        # don't care bits (x). These are followed by a null bit (0), and then
        # the result bits (R). 10 bits for the MCP300x, 12 bits for the
        # MCP320x.
        #
        # XXX Differential mode still requires testing
        data = self._spi.xfer2([16 + [8, 0][self.differential] + self.channel, 0, 0])
        return ((data[1] & 63) << (self.bits - 6)) | (data[2] >> (14 - self.bits))


class MCP33xx(MCP3xxx):
    """
    Extends :class:`MCP3xxx` with functionality specific to the MCP33xx family
    of ADCs; specifically this handles the full differential capability of
    these chips supporting the full 13-bit signed range of output values.
    """

    def __init__(self, channel=0, device=0, differential=False):
        super(MCP33xx, self).__init__(channel, device, 12, differential)

    def _read(self):
        # MCP3304/02 protocol looks like the following:
        #
        #     Byte        0        1        2
        #     ==== ======== ======== ========
        #     Tx   0001MCCC xxxxxxxx xxxxxxxx
        #     Rx   xxxxxxxx x0SRRRRR RRRRRRRx
        #
        # The transmit bits start with 3 preamble bits "000" (to warm up), a
        # start bit "1" followed by the single/differential bit (M) which is 1
        # for single-ended read, and 0 for differential read, followed by
        # 3-bits for the channel (C). The remainder of the transmission are
        # "don't care" bits (x).
        #
        # The first byte received and the top 1 bit of the second byte are
        # don't care bits (x). These are followed by a null bit (0), then the
        # sign bit (S), and then the 12 result bits (R).
        #
        # In single read mode (the default) the sign bit is always zero and the
        # result is effectively 12-bits. In differential mode, the sign bit is
        # significant and the result is a two's-complement 13-bit value.
        #
        # The MCP3301 variant of the chip always operates in differential
        # mode and effectively only has one channel (composed of an IN+ and
        # IN-). As such it requires no input, just output. This is the reason
        # we split out _send() below; so that MCP3301 can override it.
        data = self._spi.xfer2(self._send())
        # Extract the last two bytes (again, for MCP3301)
        data = data[-2:]
        result = ((data[0] & 63) << 7) | (data[1] >> 1)
        # Account for the sign bit
        if self.differential and result > 4095:
            result = -(8192 - result)
        assert -4096 <= result < 4096
        return result

    def _send(self):
        return [16 + [8, 0][self.differential] + self.channel, 0, 0]


class MCP3001(MCP3xxx):
    """
    The `MCP3001`_ is a 10-bit analog to digital converter with 1 channel

    .. _MCP3001: http://www.farnell.com/datasheets/630400.pdf
    """
    def __init__(self, device=0):
        super(MCP3001, self).__init__(0, device, 10, differential=True)


class MCP3002(MCP3xxx):
    """
    The `MCP3002`_ is a 10-bit analog to digital converter with 2 channels
    (0-3).

    .. _MCP3002: http://www.farnell.com/datasheets/1599363.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 2:
            raise InputDeviceError('channel must be 0 or 1')
        super(MCP3002, self).__init__(channel, device, 10, differential)


class MCP3004(MCP3xxx):
    """
    The `MCP3004`_ is a 10-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3004: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 3')
        super(MCP3004, self).__init__(channel, device, 10, differential)


class MCP3008(MCP3xxx):
    """
    The `MCP3008`_ is a 10-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3008: http://www.farnell.com/datasheets/808965.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3008, self).__init__(channel, device, 10, differential)


class MCP3201(MCP3xxx):
    """
    The `MCP3201`_ is a 12-bit analog to digital converter with 1 channel

    .. _MCP3201: http://www.farnell.com/datasheets/1669366.pdf
    """
    def __init__(self, device=0):
        super(MCP3201, self).__init__(0, device, 12, differential=True)


class MCP3202(MCP3xxx):
    """
    The `MCP3202`_ is a 12-bit analog to digital converter with 2 channels
    (0-1).

    .. _MCP3202: http://www.farnell.com/datasheets/1669376.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 2:
            raise InputDeviceError('channel must be 0 or 1')
        super(MCP3202, self).__init__(channel, device, 12, differential)


class MCP3204(MCP3xxx):
    """
    The `MCP3204`_ is a 12-bit analog to digital converter with 4 channels
    (0-3).

    .. _MCP3204: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 3')
        super(MCP3204, self).__init__(channel, device, 12, differential)


class MCP3208(MCP3xxx):
    """
    The `MCP3208`_ is a 12-bit analog to digital converter with 8 channels
    (0-7).

    .. _MCP3208: http://www.farnell.com/datasheets/808967.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3208, self).__init__(channel, device, 12, differential)


class MCP3301(MCP33xx):
    """
    The `MCP3301`_ is a signed 13-bit analog to digital converter.  Please note
    that the MCP3301 always operates in differential mode between its two
    channels and the output value is scaled from -1 to +1.

    .. _MCP3301: http://www.farnell.com/datasheets/1669397.pdf
    """
    def __init__(self, device=0):
        super(MCP3301, self).__init__(0, device, differential=True)

    def _send(self):
        return [0, 0]


class MCP3302(MCP33xx):
    """
    The `MCP3302`_ is a 12/13-bit analog to digital converter with 4 channels
    (0-3). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3302: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 4:
            raise InputDeviceError('channel must be between 0 and 4')
        super(MCP3302, self).__init__(channel, device, differential)


class MCP3304(MCP33xx):
    """
    The `MCP3304`_ is a 12/13-bit analog to digital converter with 8 channels
    (0-7). When operated in differential mode, the device outputs a signed
    13-bit value which is scaled from -1 to +1. When operated in single-ended
    mode (the default), the device outputs an unsigned 12-bit value scaled from
    0 to 1.

    .. _MCP3304: http://www.farnell.com/datasheets/1486116.pdf
    """
    def __init__(self, channel=0, device=0, differential=False):
        if not 0 <= channel < 8:
            raise InputDeviceError('channel must be between 0 and 7')
        super(MCP3304, self).__init__(channel, device, differential)
