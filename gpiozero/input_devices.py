# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2015-2021 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2020 Robert Erdin <roberte@depop.com>
# Copyright (c) 2020 Dan Jackson <dan@djackson.org>
# Copyright (c) 2016-2020 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2019 Kosovan Sofiia <sofiia.kosovan@gmail.com>
# Copyright (c) 2018 Philippe Muller <philippe.muller@gmail.com>
# Copyright (c) 2016 Steveis <SteveAmor@users.noreply.github.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

import warnings
from time import sleep, time
from threading import Event, Lock
from itertools import tee
try:
    from statistics import median, mean
except ImportError:
    from .compat import median, mean

from .exc import InputDeviceError, DeviceClosed, DistanceSensorNoEcho, \
    PinInvalidState, PWMSoftwareFallback
from .devices import GPIODevice, CompositeDevice
from .mixins import GPIOQueue, EventsMixin, HoldMixin, event
try:
    from .pins.pigpio import PiGPIOFactory
except ImportError:
    PiGPIOFactory = None


class InputDevice(GPIODevice):
    """
    Represents a generic GPIO input device.

    This class extends :class:`GPIODevice` to add facilities common to GPIO
    input devices.  The constructor adds the optional *pull_up* parameter to
    specify how the pin should be pulled by the internal resistors. The
    :attr:`is_active` property is adjusted accordingly so that :data:`True`
    still means active regardless of the *pull_up* setting.

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        If :data:`True`, the pin will be pulled high with an internal resistor.
        If :data:`False` (the default), the pin will be pulled low.  If
        :data:`None`, the pin will be floating. As gpiozero cannot
        automatically guess the active state when not pulling the pin, the
        *active_state* parameter must be passed.

    :type active_state: bool or None
    :param active_state:
        If :data:`True`, when the hardware pin state is ``HIGH``, the software
        pin is ``HIGH``. If :data:`False`, the input polarity is reversed: when
        the hardware pin state is ``HIGH``, the software pin state is ``LOW``.
        Use this parameter to set the active state of the underlying pin when
        configuring it as not pulled (when *pull_up* is :data:`None`). When
        *pull_up* is :data:`True` or :data:`False`, the active state is
        automatically set to the proper value.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, pin=None, pull_up=False, active_state=None,
                 pin_factory=None):
        super(InputDevice, self).__init__(pin, pin_factory=pin_factory)
        try:
            self.pin.function = 'input'
            pull = {None: 'floating', True: 'up', False: 'down'}[pull_up]
            if self.pin.pull != pull:
                self.pin.pull = pull
        except:
            self.close()
            raise

        if pull_up is None:
            if active_state is None:
                raise PinInvalidState(
                    'Pin %d is defined as floating, but "active_state" is not '
                    'defined' % self.pin.number)
            self._active_state = bool(active_state)
        else:
            if active_state is not None:
                raise PinInvalidState(
                    'Pin %d is not floating, but "active_state" is not None' %
                    self.pin.number)
            self._active_state = False if pull_up else True
        self._inactive_state = not self._active_state

    @property
    def pull_up(self):
        """
        If :data:`True`, the device uses a pull-up resistor to set the GPIO pin
        "high" by default.
        """
        pull = self.pin.pull
        if pull == 'floating':
            return None
        else:
            return pull == 'up'

    def __repr__(self):
        try:
            return "<gpiozero.%s object on pin %r, pull_up=%s, is_active=%s>" % (
                self.__class__.__name__, self.pin, self.pull_up, self.is_active)
        except:
            return super(InputDevice, self).__repr__()


class DigitalInputDevice(EventsMixin, InputDevice):
    """
    Represents a generic input device with typical on/off behaviour.

    This class extends :class:`InputDevice` with machinery to fire the active
    and inactive events for devices that operate in a typical digital manner:
    straight forward on / off states with (reasonably) clean transitions
    between the two.

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        See description under :class:`InputDevice` for more information.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

    :type bounce_time: float or None
    :param bounce_time:
        Specifies the length of time (in seconds) that the component will
        ignore changes in state after an initial change. This defaults to
        :data:`None` which indicates that no bounce compensation will be
        performed.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, pull_up=False, active_state=None, bounce_time=None,
            pin_factory=None):
        super(DigitalInputDevice, self).__init__(
            pin, pull_up=pull_up, active_state=active_state,
            pin_factory=pin_factory)
        try:
            self.pin.bounce = bounce_time
            self.pin.edges = 'both'
            self.pin.when_changed = self._pin_changed
            # Call _fire_events once to set initial state of events
            self._fire_events(self.pin_factory.ticks(), self.is_active)
        except:
            self.close()
            raise

    def _pin_changed(self, ticks, state):
        # XXX This is a bit of a hack; _fire_events takes *is_active* rather
        # than *value*. Here we're assuming no-one's overridden the default
        # implementation of *is_active*.
        self._fire_events(ticks, bool(self._state_to_value(state)))


class SmoothedInputDevice(EventsMixin, InputDevice):
    """
    Represents a generic input device which takes its value from the average of
    a queue of historical values.

    This class extends :class:`InputDevice` with a queue which is filled by a
    background thread which continually polls the state of the underlying
    device. The average (a configurable function) of the values in the queue is
    compared to a threshold which is used to determine the state of the
    :attr:`is_active` property.

    .. note::

        The background queue is not automatically started upon construction.
        This is to allow descendents to set up additional components before the
        queue starts reading values. Effectively this is an abstract base
        class.

    This class is intended for use with devices which either exhibit analog
    behaviour (such as the charging time of a capacitor with an LDR), or those
    which exhibit "twitchy" behaviour (such as certain motion sensors).

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        See description under :class:`InputDevice` for more information.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

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
        If :data:`False` (the default), attempts to read the state of the
        device (from the :attr:`is_active` property) will block until the queue
        has filled.  If :data:`True`, a value will be returned immediately, but
        be aware that this value is likely to fluctuate excessively.

    :param average:
        The function used to average the values in the internal queue. This
        defaults to :func:`statistics.median` which is a good selection for
        discarding outliers from jittery sensors. The function specified must
        accept a sequence of numbers and return a single number.

    :type ignore: frozenset or None
    :param ignore:
        The set of values which the queue should ignore, if returned from
        querying the device's value.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, pull_up=False, active_state=None, threshold=0.5,
            queue_len=5, sample_wait=0.0, partial=False, average=median,
            ignore=None, pin_factory=None):
        self._queue = None
        super(SmoothedInputDevice, self).__init__(
            pin, pull_up=pull_up, active_state=active_state,
            pin_factory=pin_factory)
        try:
            self._queue = GPIOQueue(self, queue_len, sample_wait, partial,
                                    average, ignore)
            self.threshold = float(threshold)
        except:
            self.close()
            raise

    def close(self):
        try:
            self._queue.stop()
        except AttributeError:
            # If the queue isn't initialized (it's None), or _queue hasn't been
            # set ignore the error because we're trying to close anyway
            pass
        except RuntimeError:
            # Cannot join thread before it starts; we don't care about this
            # because we're trying to close the thread anyway
            pass
        self._queue = None
        super(SmoothedInputDevice, self).close()

    def __repr__(self):
        try:
            self._check_open()
        except DeviceClosed:
            return super(SmoothedInputDevice, self).__repr__()
        else:
            if self.partial or self._queue.full.is_set():
                return super(SmoothedInputDevice, self).__repr__()
            else:
                return "<gpiozero.%s object on pin %r, pull_up=%s>" % (
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
        If :data:`False` (the default), attempts to read the
        :attr:`~SmoothedInputDevice.value` or
        :attr:`~SmoothedInputDevice.is_active` properties will block until the
        queue has filled.
        """
        self._check_open()
        return self._queue.partial

    @property
    def value(self):
        """
        Returns the average of the values in the internal queue. This is
        compared to :attr:`~SmoothedInputDevice.threshold` to determine whether
        :attr:`is_active` is :data:`True`.
        """
        self._check_open()
        return self._queue.value

    @property
    def threshold(self):
        """
        If :attr:`~SmoothedInputDevice.value` exceeds this amount, then
        :attr:`is_active` will return :data:`True`.
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
        Returns :data:`True` if the :attr:`~SmoothedInputDevice.value`
        currently exceeds :attr:`~SmoothedInputDevice.threshold` and
        :data:`False` otherwise.
        """
        return self.value > self.threshold


class Button(HoldMixin, DigitalInputDevice):
    """
    Extends :class:`DigitalInputDevice` and represents a simple push button
    or switch.

    Connect one side of the button to a ground pin, and the other to any GPIO
    pin. Alternatively, connect one side of the button to the 3V3 pin, and the
    other to any GPIO pin, then set *pull_up* to :data:`False` in the
    :class:`Button` constructor.

    The following example will print a line of text when the button is pushed::

        from gpiozero import Button

        button = Button(4)
        button.wait_for_press()
        print("The button was pressed!")

    :type pin: int or str
    :param pin:
        The GPIO pin which the button is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        If :data:`True` (the default), the GPIO pin will be pulled high by
        default.  In this case, connect the other side of the button to ground.
        If :data:`False`, the GPIO pin will be pulled low by default. In this
        case, connect the other side of the button to 3V3. If :data:`None`, the
        pin will be floating, so it must be externally pulled up or down and
        the ``active_state`` parameter must be set accordingly.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

    :type bounce_time: float or None
    :param bounce_time:
        If :data:`None` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length of time (in seconds) that the
        component will ignore changes in state after an initial change.

    :param float hold_time:
        The length of time (in seconds) to wait after the button is pushed,
        until executing the :attr:`when_held` handler. Defaults to ``1``.

    :param bool hold_repeat:
        If :data:`True`, the :attr:`when_held` handler will be repeatedly
        executed as long as the device remains active, every *hold_time*
        seconds. If :data:`False` (the default) the :attr:`when_held` handler
        will be only be executed once per hold.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, pull_up=True, active_state=None, bounce_time=None,
            hold_time=1, hold_repeat=False, pin_factory=None):
        super(Button, self).__init__(
            pin, pull_up=pull_up, active_state=active_state,
            bounce_time=bounce_time, pin_factory=pin_factory)
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat

    @property
    def value(self):
        """
        Returns 1 if the button is currently pressed, and 0 if it is not.
        """
        return super(Button, self).value

Button.is_pressed = Button.is_active
Button.pressed_time = Button.active_time
Button.when_pressed = Button.when_activated
Button.when_released = Button.when_deactivated
Button.wait_for_press = Button.wait_for_active
Button.wait_for_release = Button.wait_for_inactive


class LineSensor(SmoothedInputDevice):
    """
    Extends :class:`SmoothedInputDevice` and represents a single pin line
    sensor like the TCRT5000 infra-red proximity sensor found in the `CamJam #3
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

    :type pin: int or str
    :param pin:
        The GPIO pin which the sensor is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        See description under :class:`InputDevice` for more information.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

    :param int queue_len:
        The length of the queue used to store values read from the sensor. This
        defaults to 5.

    :param float sample_rate:
        The number of values to read from the device (and append to the
        internal queue) per second. Defaults to 100.

    :param float threshold:
        Defaults to 0.5. When the average of all values in the internal queue
        rises above this value, the sensor will be considered "active" by the
        :attr:`~SmoothedInputDevice.is_active` property, and all appropriate
        events will be fired.

    :param bool partial:
        When :data:`False` (the default), the object will not return a value
        for :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to :data:`True` if you require
        values immediately after object construction.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    def __init__(
            self, pin=None, pull_up=False, active_state=None, queue_len=5,
            sample_rate=100, threshold=0.5, partial=False, pin_factory=None):
        super(LineSensor, self).__init__(
            pin, pull_up=pull_up, active_state=active_state,
            threshold=threshold, queue_len=queue_len,
            sample_wait=1 / sample_rate, partial=partial,
            pin_factory=pin_factory)
        self._queue.start()

    @property
    def value(self):
        """
        Returns a value representing the average of the queued values. This
        is nearer 0 for black under the sensor, and nearer 1 for white under
        the sensor.
        """
        return super(LineSensor, self).value

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

    :type pin: int or str
    :param pin:
        The GPIO pin which the sensor is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :type pull_up: bool or None
    :param pull_up:
        See description under :class:`InputDevice` for more information.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

    :param int queue_len:
        The length of the queue used to store values read from the sensor. This
        defaults to 1 which effectively disables the queue. If your motion
        sensor is particularly "twitchy" you may wish to increase this value.

    :param float sample_rate:
        The number of values to read from the device (and append to the
        internal queue) per second. Defaults to 10.

    :param float threshold:
        Defaults to 0.5. When the average of all values in the internal queue
        rises above this value, the sensor will be considered "active" by the
        :attr:`~SmoothedInputDevice.is_active` property, and all appropriate
        events will be fired.

    :param bool partial:
        When :data:`False` (the default), the object will not return a value
        for :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to :data:`True` if you require
        values immediately after object construction.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, pull_up=False, active_state=None, queue_len=1,
            sample_rate=10, threshold=0.5, partial=False, pin_factory=None):
        super(MotionSensor, self).__init__(
            pin, pull_up=pull_up, active_state=active_state,
            threshold=threshold, queue_len=queue_len, sample_wait=1 /
            sample_rate, partial=partial, pin_factory=pin_factory, average=mean)
        self._queue.start()

    @property
    def value(self):
        """
        With the default *queue_len* of 1, this is effectively boolean where 0
        means no motion detected and 1 means motion detected. If you specify
        a *queue_len* greater than 1, this will be an averaged value where
        values closer to 1 imply motion detection.
        """
        return super(MotionSensor, self).value

MotionSensor.motion_detected = MotionSensor.is_active
MotionSensor.when_motion = MotionSensor.when_activated
MotionSensor.when_no_motion = MotionSensor.when_deactivated
MotionSensor.wait_for_motion = MotionSensor.wait_for_active
MotionSensor.wait_for_no_motion = MotionSensor.wait_for_inactive


class LightSensor(SmoothedInputDevice):
    """
    Extends :class:`SmoothedInputDevice` and represents a light dependent
    resistor (LDR).

    Connect one leg of the LDR to the 3V3 pin; connect one leg of a 1µF
    capacitor to a ground pin; connect the other leg of the LDR and the other
    leg of the capacitor to the same GPIO pin. This class repeatedly discharges
    the capacitor, then times the duration it takes to charge (which will vary
    according to the light falling on the LDR).

    The following code will print a line of text when light is detected::

        from gpiozero import LightSensor

        ldr = LightSensor(18)
        ldr.wait_for_light()
        print("Light detected!")

    :type pin: int or str
    :param pin:
        The GPIO pin which the sensor is attached to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param int queue_len:
        The length of the queue used to store values read from the circuit.
        This defaults to 5.

    :param float charge_time_limit:
        If the capacitor in the circuit takes longer than this length of time
        to charge, it is assumed to be dark. The default (0.01 seconds) is
        appropriate for a 1µF capacitor coupled with the LDR from the
        `CamJam #2 EduKit`_. You may need to adjust this value for different
        valued capacitors or LDRs.

    :param float threshold:
        Defaults to 0.1. When the average of all values in the internal queue
        rises above this value, the area will be considered "light", and all
        appropriate events will be fired.

    :param bool partial:
        When :data:`False` (the default), the object will not return a value
        for :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to :data:`True` if you require
        values immediately after object construction.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #2 EduKit: http://camjam.me/?page_id=623
    """
    def __init__(
            self, pin=None, queue_len=5, charge_time_limit=0.01,
            threshold=0.1, partial=False, pin_factory=None):
        super(LightSensor, self).__init__(
            pin, pull_up=False, threshold=threshold, queue_len=queue_len,
            sample_wait=0.0, partial=partial, pin_factory=pin_factory)
        try:
            self._charge_time_limit = charge_time_limit
            self._charge_time = None
            self._charged = Event()
            self.pin.edges = 'rising'
            self.pin.bounce = None
            self.pin.when_changed = self._cap_charged
            self._queue.start()
        except:
            self.close()
            raise

    @property
    def charge_time_limit(self):
        return self._charge_time_limit

    def _cap_charged(self, ticks, state):
        self._charge_time = ticks
        self._charged.set()

    def _read(self):
        # Drain charge from the capacitor
        self.pin.function = 'output'
        self.pin.state = False
        sleep(0.1)
        self._charge_time = None
        self._charged.clear()
        # Time the charging of the capacitor
        start = self.pin_factory.ticks()
        self.pin.function = 'input'
        self._charged.wait(self.charge_time_limit)
        if self._charge_time is None:
            return 0.0
        else:
            return 1.0 - min(1.0,
                (self.pin_factory.ticks_diff(self._charge_time, start) /
                self.charge_time_limit))

    @property
    def value(self):
        """
        Returns a value between 0 (dark) and 1 (light).
        """
        return super(LightSensor, self).value

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

    3. Connect one end of a 330Ω resistor to the ECHO pin of the sensor.

    4. Connect one end of a 470Ω resistor to the GND pin of the sensor.

    5. Connect the free ends of both resistors to another GPIO pin. This forms
       the required `voltage divider`_.

    6. Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

    Alternatively, the 3V3 tolerant HC-SR04P sensor (which does not require a
    voltage divider) will work with this class.


    .. note::

        If you do not have the precise values of resistor specified above,
        don't worry! What matters is the *ratio* of the resistors to each
        other.

        You also don't need to be absolutely precise; the `voltage divider`_
        given above will actually output ~3V (rather than 3.3V). A simple 2:3
        ratio will give 3.333V which implies you can take three resistors of
        equal value, use one of them instead of the 330Ω resistor, and two of
        them in series instead of the 470Ω resistor.

    .. _voltage divider: https://en.wikipedia.org/wiki/Voltage_divider

    The following code will periodically report the distance measured by the
    sensor in cm assuming the TRIG pin is connected to GPIO17, and the ECHO
    pin to GPIO18::

        from gpiozero import DistanceSensor
        from time import sleep

        sensor = DistanceSensor(echo=18, trigger=17)
        while True:
            print('Distance: ', sensor.distance * 100)
            sleep(1)

    .. note::

        For improved accuracy, use the pigpio pin driver rather than the default
        RPi.GPIO driver (pigpio uses DMA sampling for much more precise edge
        timing). This is particularly relevant if you're using Pi 1 or Pi Zero.
        See :ref:`changing-pin-factory` for further information.

    :type echo: int or str
    :param echo:
        The GPIO pin which the ECHO pin is connected to. See
        :ref:`pin-numbering` for valid pin numbers. If this is :data:`None` a
        :exc:`GPIODeviceError` will be raised.

    :type trigger: int or str
    :param trigger:
        The GPIO pin which the TRIG pin is connected to. See
        :ref:`pin-numbering` for valid pin numbers. If this is :data:`None` a
        :exc:`GPIODeviceError` will be raised.

    :param int queue_len:
        The length of the queue used to store values read from the sensor.
        This defaults to 9.

    :param float max_distance:
        The :attr:`value` attribute reports a normalized value between 0 (too
        close to measure) and 1 (maximum distance). This parameter specifies
        the maximum distance expected in meters. This defaults to 1.

    :param float threshold_distance:
        Defaults to 0.3. This is the distance (in meters) that will trigger the
        ``in_range`` and ``out_of_range`` events when crossed.

    :param bool partial:
        When :data:`False` (the default), the object will not return a value
        for :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to :data:`True` if you require
        values immediately after object construction.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    ECHO_LOCK = Lock()

    def __init__(
            self, echo=None, trigger=None, queue_len=9, max_distance=1,
            threshold_distance=0.3, partial=False, pin_factory=None):
        self._trigger = None
        super(DistanceSensor, self).__init__(
            echo, pull_up=False, queue_len=queue_len, sample_wait=0.06,
            partial=partial, ignore=frozenset({None}), pin_factory=pin_factory
        )
        try:
            if max_distance <= 0:
                raise ValueError('invalid maximum distance (must be positive)')
            self._max_distance = max_distance
            self.threshold = threshold_distance / max_distance
            self.speed_of_sound = 343.26 # m/s
            self._trigger = GPIODevice(trigger, pin_factory=pin_factory)
            self._echo = Event()
            self._echo_rise = None
            self._echo_fall = None
            self._trigger.pin.function = 'output'
            self._trigger.pin.state = False
            self.pin.edges = 'both'
            self.pin.bounce = None
            self.pin.when_changed = self._echo_changed
            self._queue.start()
        except:
            self.close()
            raise

        if PiGPIOFactory is None or not isinstance(self.pin_factory, PiGPIOFactory):
            warnings.warn(PWMSoftwareFallback(
                'For more accurate readings, use the pigpio pin factory.'
                'See https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04 for more info'
            ))

    def close(self):
        try:
            self._trigger.close()
        except AttributeError:
            pass
        self._trigger = None
        super(DistanceSensor, self).close()

    @property
    def max_distance(self):
        """
        The maximum distance that the sensor will measure in meters. This value
        is specified in the constructor and is used to provide the scaling for
        the :attr:`~SmoothedInputDevice.value` attribute. When :attr:`distance`
        is equal to :attr:`max_distance`, :attr:`~SmoothedInputDevice.value`
        will be 1.
        """
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        if value <= 0:
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
        :attr:`~SmoothedInputDevice.threshold` attribute.
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
    def value(self):
        """
        Returns a value between 0, indicating the reflector is either touching
        the sensor or is sufficiently near that the sensor can't tell the
        difference, and 1, indicating the reflector is at or beyond the
        specified *max_distance*.
        """
        return super(DistanceSensor, self).value

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
        is simply an alias for the usual :attr:`~GPIODevice.pin` attribute.
        """
        return self.pin

    def _echo_changed(self, ticks, level):
        if level:
            self._echo_rise = ticks
        else:
            self._echo_fall = ticks
            self._echo.set()

    def _read(self):
        # Wait up to 50ms for the echo pin to fall to low (the maximum echo
        # pulse is 35ms so this gives some leeway); if it doesn't something is
        # horribly wrong (most likely at the hardware level)
        if self.pin.state:
            if not self._echo.wait(0.05):
                warnings.warn(DistanceSensorNoEcho('echo pin set high'))
                return None
        self._echo.clear()
        self._echo_fall = None
        self._echo_rise = None
        # Obtain the class-level ECHO_LOCK to ensure multiple distance sensors
        # don't listen for each other's "pings"
        with DistanceSensor.ECHO_LOCK:
            # Fire the trigger
            self._trigger.pin.state = True
            sleep(0.00001)
            self._trigger.pin.state = False
            # Wait up to 100ms for the echo pin to rise and fall (35ms is the
            # maximum pulse time, but the pre-rise time is unspecified in the
            # "datasheet"; 100ms seems sufficiently long to conclude something
            # has failed)
            if self._echo.wait(0.1):
                if self._echo_fall is not None and self._echo_rise is not None:
                    distance = (
                        self.pin_factory.ticks_diff(
                            self._echo_fall, self._echo_rise) *
                        self.speed_of_sound / 2.0)
                    return min(1.0, distance / self._max_distance)
                else:
                    # If we only saw the falling edge it means we missed
                    # the echo because it was too fast
                    return None
            else:
                # The echo pin never rose or fell; something's gone horribly
                # wrong
                warnings.warn(DistanceSensorNoEcho('no echo received'))
                return None

    @property
    def in_range(self):
        return not self.is_active

DistanceSensor.when_out_of_range = DistanceSensor.when_activated
DistanceSensor.when_in_range = DistanceSensor.when_deactivated
DistanceSensor.wait_for_out_of_range = DistanceSensor.wait_for_active
DistanceSensor.wait_for_in_range = DistanceSensor.wait_for_inactive


class RotaryEncoder(EventsMixin, CompositeDevice):
    """
    Represents a simple two-pin incremental `rotary encoder`_ device.

    These devices typically have three pins labelled "A", "B", and "C". Connect
    A and B directly to two GPIO pins, and C ("common") to one of the ground
    pins on your Pi. Then simply specify the A and B pins as the arguments when
    constructing this classs.

    For example, if your encoder's A pin is connected to GPIO 21, and the B
    pin to GPIO 20 (and presumably the C pin to a suitable GND pin), while an
    LED (with a suitable 300Ω resistor) is connected to GPIO 5, the following
    session will result in the brightness of the LED being controlled by
    dialling the rotary encoder back and forth::

        >>> from gpiozero import RotaryEncoder
        >>> from gpiozero.tools import scaled_half
        >>> rotor = RotaryEncoder(21, 20)
        >>> led = PWMLED(5)
        >>> led.source = scaled_half(rotor.values)

    :type a: int or str
    :param a:
        The GPIO pin connected to the "A" output of the rotary encoder.

    :type b: int or str
    :param b:
        The GPIO pin connected to the "B" output of the rotary encoder.

    :type bounce_time: float or None
    :param bounce_time:
        If :data:`None` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length of time (in seconds) that the
        component will ignore changes in state after an initial change.

    :type max_steps: int
    :param max_steps:
        The number of steps clockwise the encoder takes to change the
        :attr:`value` from 0 to 1, or counter-clockwise from 0 to -1.
        If this is 0, then the encoder's :attr:`value` never changes, but you
        can still read :attr:`steps` to determine the integer number of steps
        the encoder has moved clockwise or counter clockwise.

    :type threshold_steps: tuple of int
    :param threshold_steps:
        A (min, max) tuple of steps between which the device will be considered
        "active", inclusive. In other words, when :attr:`steps` is greater than
        or equal to the *min* value, and less than or equal the *max* value,
        the :attr:`active` property will be :data:`True` and the appropriate
        events (:attr:`when_activated`, :attr:`when_deactivated`) will be
        fired. Defaults to (0, 0).

    :type wrap: bool
    :param wrap:
        If :data:`True` and *max_steps* is non-zero, when the :attr:`steps`
        reaches positive or negative *max_steps* it wraps around by negation.
        Defaults to :data:`False`.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _rotary encoder: https://en.wikipedia.org/wiki/Rotary_encoder
    """
    # The rotary encoder's two pins move through the following sequence when
    # the encoder is rotated one step clockwise:
    #
    #   ────┐     ┌─────┐     ┌────────
    #    _  │     │     │     │          counter        ┌───┐
    #    A  │     │     │     │         clockwise  ┌─── │ 0 │ ───┐  clockwise
    #       └─────┘     └─────┘           (CCW)    │    └───┘    │    (CW)
    #       :     :     :     :             │    ┌───┐         ┌───┐    │
    #   ───────┐  :  ┌─────┐  :  ┌─────     ▾    │ 1 │         │ 2 │    ▾
    #    _  :  │  :  │  :  │  :  │               └───┘         └───┘
    #    B  :  │  :  │  :  │  :  │                 │    ┌───┐    │
    #       :  └─────┘  :  └─────┘                 └─── │ 3 │ ───┘
    #       :  :  :  :  :  :  :  :                      └───┘
    #    0  2  3  1  0  2  3  1  0
    #
    # Treating the A pin as a "high" bit, and the B pin as a "low" bit, this
    # means that the pins return the sequence 0, 2, 3, 1 for each step that the
    # encoder takes clockwise. Conversely, the pins return the sequence 0, 1,
    # 3, 2 for each step counter-clockwise.
    #
    # We can treat these values as edges to take in a simple state machine,
    # which is represented in the dictionary below:

    TRANSITIONS = {
        'idle': ['idle', 'ccw1', 'cw1',  'idle'],
        'ccw1': ['idle', 'ccw1', 'ccw3', 'ccw2'],
        'ccw2': ['idle', 'ccw1', 'ccw3', 'ccw2'],
        'ccw3': ['-1',   'idle', 'ccw3', 'ccw2'],
        'cw1':  ['idle', 'cw3',  'cw1',  'cw2'],
        'cw2':  ['idle', 'cw3',  'cw1',  'cw2'],
        'cw3':  ['+1',   'cw3',  'idle', 'cw2'],
    }

    # The state machine here includes more than just the strictly necessary
    # edges; it also permits "wiggle" between intermediary states so that the
    # overall graph looks like this:
    #
    #                            ┌──────┐
    #                            │      │
    #                      ┌─────┤ idle ├────┐
    #                      │1    │      │   2│
    #                      │     └──────┘    │
    #                      ▾       ▴  ▴      ▾
    #                  ┌────────┐  │  │  ┌───────┐
    #                  │        │ 0│  │0 │       │
    #              ┌───┤  ccw1  ├──┤  ├──┤  cw1  ├───┐
    #              │2  │        │  │  │  │       │  1│
    #              │   └─┬──────┘  │  │  └─────┬─┘   │
    #              │    3│    ▴    │  │    ▴   │3    │
    #              │     ▾    │1   │  │   2│   ▾     │
    #              │   ┌──────┴─┐  │  │  ┌─┴─────┐   │
    #              │   │        │ 0│  │0 │       │   │
    #              │   │  ccw2  ├──┤  ├──┤  cw2  │   │
    #              │   │        │  │  │  │       │   │
    #              │   └─┬──────┘  │  │  └─────┬─┘   │
    #              │    2│    ▴    │  │    ▴   │1    │
    #              │     ▾    │3   │  │   3│   ▾     │
    #              │   ┌──────┴─┐  │  │  ┌─┴─────┐   │
    #              │   │        │  │  │  │       │   │
    #              └──▸│  ccw3  │  │  │  │  cw3  │◂──┘
    #                  │        │  │  │  │       │
    #                  └───┬────┘  │  │  └───┬───┘
    #                     0│       │  │      │0
    #                      ▾       │  │      ▾
    #                  ┌────────┐  │  │  ┌───────┐
    #                  │        │  │  │  │       │
    #                  │   -1   ├──┘  └──┤  +1   │
    #                  │        │        │       │
    #                  └────────┘        └───────┘
    #
    # Note that, once we start down the clockwise (cw) or counter-clockwise
    # (ccw) path, we don't allow the state to pick the alternate direction
    # without passing through the idle state again. This seems to work well in
    # practice with several encoders, even quite jiggly ones with no debounce
    # hardware or software

    def __init__(
            self, a, b, bounce_time=None, max_steps=16, threshold_steps=(0, 0),
            wrap=False, pin_factory=None):
        min_thresh, max_thresh = threshold_steps
        if max_thresh < min_thresh:
            raise ValueError('maximum threshold cannot be less than minimum')
        self._steps = 0
        self._max_steps = int(max_steps)
        self._threshold = (int(min_thresh), int(max_thresh))
        self._wrap = bool(wrap)
        self._state = 'idle'
        self._edge = 0
        self._when_rotated = None
        self._when_rotated_cw = None
        self._when_rotated_ccw = None
        self._rotate_event = Event()
        self._rotate_cw_event = Event()
        self._rotate_ccw_event = Event()
        super(RotaryEncoder, self).__init__(
            a=InputDevice(a, pull_up=True, pin_factory=pin_factory),
            b=InputDevice(b, pull_up=True, pin_factory=pin_factory),
            _order=('a', 'b'), pin_factory=pin_factory)
        self.a.pin.bounce_time = bounce_time
        self.b.pin.bounce_time = bounce_time
        self.a.pin.edges = 'both'
        self.b.pin.edges = 'both'
        self.a.pin.when_changed = self._a_changed
        self.b.pin.when_changed = self._b_changed
        # Call _fire_events once to set initial state of events
        self._fire_events(self.pin_factory.ticks(), self.is_active)

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.%s object on pins %r and %r>" % (
                self.__class__.__name__, self.a.pin, self.b.pin)
        except DeviceClosed:
            return super(RotaryEncoder, self).__repr__()

    def _a_changed(self, ticks, state):
        edge = (self.a._state_to_value(state) << 1) | (self._edge & 0x1)
        self._change_state(ticks, edge)

    def _b_changed(self, ticks, state):
        edge = (self._edge & 0x2) | self.b._state_to_value(state)
        self._change_state(ticks, edge)

    def _change_state(self, ticks, edge):
        self._edge = edge
        new_state = RotaryEncoder.TRANSITIONS[self._state][edge]
        if new_state == '+1':
            self._steps = (
                self._steps + 1
                if not self._max_steps or self._steps < self._max_steps else
                -self._max_steps if self._wrap else self._max_steps
            )
            self._rotate_cw_event.set()
            self._fire_rotated_cw()
            self._rotate_cw_event.clear()
        elif new_state == '-1':
            self._steps = (
                self._steps - 1
                if not self._max_steps or self._steps > -self._max_steps else
                self._max_steps if self._wrap else -self._max_steps
            )
            self._rotate_ccw_event.set()
            self._fire_rotated_ccw()
            self._rotate_ccw_event.clear()
        else:
            self._state = new_state
            return
        self._rotate_event.set()
        self._fire_rotated()
        self._rotate_event.clear()
        self._fire_events(ticks, self.is_active)
        self._state = 'idle'

    def wait_for_rotate(self, timeout=None):
        """
        Pause the script until the encoder is rotated at least one step in
        either direction, or the timeout is reached.

        :type timeout: float or None
        :param timeout:
            Number of seconds to wait before proceeding. If this is
            :data:`None` (the default), then wait indefinitely until the
            encoder is rotated.
        """
        return self._rotate_event.wait(timeout)

    def wait_for_rotate_clockwise(self, timeout=None):
        """
        Pause the script until the encoder is rotated at least one step
        clockwise, or the timeout is reached.

        :type timeout: float or None
        :param timeout:
            Number of seconds to wait before proceeding. If this is
            :data:`None` (the default), then wait indefinitely until the
            encoder is rotated clockwise.
        """
        return self._rotate_cw_event.wait(timeout)

    def wait_for_rotate_counter_clockwise(self, timeout=None):
        """
        Pause the script until the encoder is rotated at least one step
        counter-clockwise, or the timeout is reached.

        :type timeout: float or None
        :param timeout:
            Number of seconds to wait before proceeding. If this is
            :data:`None` (the default), then wait indefinitely until the
            encoder is rotated counter-clockwise.
        """
        return self._rotate_ccw_event.wait(timeout)

    when_rotated = event(
        """
        The function to be run when the encoder is rotated in either direction.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    when_rotated_clockwise = event(
        """
        The function to be run when the encoder is rotated clockwise.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    when_rotated_counter_clockwise = event(
        """
        The function to be run when the encoder is rotated counter-clockwise.

        This can be set to a function which accepts no (mandatory) parameters,
        or a Python function which accepts a single mandatory parameter (with
        as many optional parameters as you like). If the function accepts a
        single mandatory parameter, the device that activated will be passed
        as that parameter.

        Set this property to :data:`None` (the default) to disable the event.
        """)

    @property
    def steps(self):
        """
        The "steps" value of the encoder starts at 0. It increments by one for
        every step the encoder is rotated clockwise, and decrements by one for
        every step it is rotated counter-clockwise. The steps value is
        limited by :attr:`max_steps`. It will not advance beyond positive or
        negative :attr:`max_steps`, unless :attr:`wrap` is :data:`True` in
        which case it will roll around by negation. If :attr:`max_steps` is
        zero then steps are not limited at all, and will increase infinitely
        in either direction, but :attr:`value` will return a constant zero.

        Note that, in contrast to most other input devices, because the rotary
        encoder has no absolute position the :attr:`steps` attribute (and
        :attr:`value` by corollary) is writable.
        """
        return self._steps

    def _fire_rotated(self):
        if self.when_rotated:
            self.when_rotated()

    def _fire_rotated_cw(self):
        if self.when_rotated_clockwise:
            self.when_rotated_clockwise()

    def _fire_rotated_ccw(self):
        if self.when_rotated_counter_clockwise:
            self.when_rotated_counter_clockwise()

    @steps.setter
    def steps(self, value):
        value = int(value)
        if self._max_steps:
            value = max(-self._max_steps, min(self._max_steps, value))
        self._steps = value

    @property
    def value(self):
        """
        Represents the value of the rotary encoder as a value between -1 and 1.
        The value is calculated by dividing the value of :attr:`steps` into the
        range from negative :attr:`max_steps` to positive :attr:`max_steps`.

        Note that, in contrast to most other input devices, because the rotary
        encoder has no absolute position the :attr:`value` attribute is
        writable.
        """
        try:
            return self._steps / self._max_steps
        except ZeroDivisionError:
            return 0

    @value.setter
    def value(self, value):
        self._steps = int(max(-1, min(1, float(value))) * self._max_steps)

    @property
    def is_active(self):
        return self._threshold[0] <= self._steps <= self._threshold[1]

    @property
    def max_steps(self):
        """
        The number of discrete steps the rotary encoder takes to move
        :attr:`value` from 0 to 1 clockwise, or 0 to -1 counter-clockwise. In
        another sense, this is also the total number of discrete states this
        input can represent.
        """
        return self._max_steps

    @property
    def threshold_steps(self):
        """
        The mininum and maximum number of steps between which :attr:`is_active`
        will return :data:`True`. Defaults to (0, 0).
        """
        return self._threshold

    @property
    def wrap(self):
        """
        If :data:`True`, when :attr:`value` reaches its limit (-1 or 1), it
        "wraps around" to the opposite limit. When :data:`False`, the value
        (and the corresponding :attr:`steps` attribute) simply don't advance
        beyond their limits.
        """
        return self._wrap
