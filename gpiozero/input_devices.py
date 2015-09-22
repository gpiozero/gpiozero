from __future__ import division

from time import sleep, time
from threading import Event

from RPi import GPIO
from w1thermsensor import W1ThermSensor

from .devices import GPIODeviceError, GPIODevice, GPIOQueue


def _alias(key):
    return property(
        lambda self: getattr(self, key),
        lambda self, val: setattr(self, key, val))


class InputDeviceError(GPIODeviceError):
    pass


class InputDevice(GPIODevice):
    def __init__(self, pin=None, pull_up=False):
        super(InputDevice, self).__init__(pin)
        self._pull_up = pull_up
        self._active_edge = (GPIO.RISING, GPIO.FALLING)[pull_up]
        self._inactive_edge = (GPIO.FALLING, GPIO.RISING)[pull_up]
        if pull_up:
            self._active_state = GPIO.LOW
            self._inactive_state = GPIO.HIGH
        GPIO.setup(pin, GPIO.IN, (GPIO.PUD_DOWN, GPIO.PUD_UP)[pull_up])

    @property
    def pull_up(self):
        return self._pull_up


class WaitableInputDevice(InputDevice):
    def __init__(self, pin=None, pull_up=False):
        super(WaitableInputDevice, self).__init__(pin, pull_up)
        self._active_event = Event()
        self._inactive_event = Event()
        self._when_activated = None
        self._when_deactivated = None
        self._last_state = None

    def wait_for_active(self, timeout=None):
        return self._active_event.wait(timeout)

    def wait_for_inactive(self, timeout=None):
        return self._inactive_event.wait(timeout)

    def _get_when_activated(self):
        return self._when_activated
    def _set_when_activated(self, value):
        if not callable(value) and value is not None:
            raise InputDeviceError('value must be None or a function')
        self._when_activated = value
    when_activated = property(_get_when_activated, _set_when_activated)

    def _get_when_deactivated(self):
        return self._when_deactivated
    def _set_when_deactivated(self, value):
        if not callable(value) and value is not None:
            raise InputDeviceError('value must be None or a function')
        self._when_deactivated = value
    when_deactivated = property(_get_when_deactivated, _set_when_deactivated)

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
    def __init__(self, pin=None, pull_up=False, bouncetime=None):
        super(DigitalInputDevice, self).__init__(pin, pull_up)
        # Yes, that's really the default bouncetime in RPi.GPIO...
        GPIO.add_event_detect(
                self.pin, GPIO.BOTH, callback=self._fire_events,
                bouncetime=-666 if bouncetime is None else bouncetime)
        # Call _fire_events once to set initial state of events
        super(DigitalInputDevice, self)._fire_events()

    def __del__(self):
        GPIO.remove_event_detect(self.pin)

    def _fire_events(self, channel):
        super(DigitalInputDevice, self)._fire_events()


class SmoothedInputDevice(WaitableInputDevice):
    def __init__(
            self, pin=None, pull_up=False, threshold=0.5,
            queue_len=5, sample_wait=0.0, partial=False):
        super(SmoothedInputDevice, self).__init__(pin, pull_up)
        self._queue = GPIOQueue(self, queue_len, sample_wait, partial)
        self.threshold = float(threshold)

    @property
    def queue_len(self):
        return self._queue.queue.maxlen

    @property
    def partial(self):
        return self._queue.partial

    @property
    def value(self):
        return self._queue.value

    def _get_threshold(self):
        return self._threshold

    def _set_threshold(self, value):
        if not (0.0 < value < 1.0):
            raise InputDeviceError('threshold must be between zero and one exclusive')
        self._threshold = float(value)
    threshold = property(_get_threshold, _set_threshold)

    @property
    def is_active(self):
        return self.value > self.threshold


class Button(DigitalInputDevice):
    def __init__(self, pin=None, pull_up=True, bouncetime=None):
        super(Button, self).__init__(pin, pull_up, bouncetime)

    when_pressed = _alias('when_activated')
    when_released = _alias('when_deactivated')

    wait_for_press = _alias('wait_for_active')
    wait_for_release = _alias('wait_for_inactive')


class MotionSensor(SmoothedInputDevice):
    def __init__(
            self, pin=None, queue_len=5, sample_rate=10, threshold=0.5,
            partial=False):
        super(MotionSensor, self).__init__(
                pin, pull_up=False, threshold=threshold,
                queue_len=queue_len, sample_wait=1 / sample_rate, partial=partial)
        self._queue.start()

    motion_detected = _alias('is_active')

    when_motion = _alias('when_activated')
    when_no_motion = _alias('when_deactivated')

    wait_for_motion = _alias('wait_for_active')
    wait_for_no_motion = _alias('wait_for_inactive')


class LightSensor(SmoothedInputDevice):
    def __init__(
            self, pin=None, queue_len=5, charge_time_limit=0.01,
            threshold=0.1, partial=False):
        super(LightSensor, self).__init__(
                pin, pull_up=False, threshold=threshold,
                queue_len=queue_len, sample_wait=0.0, partial=partial)
        self._charge_time_limit = charge_time_limit
        self._charged = Event()
        GPIO.add_event_detect(self.pin, GPIO.RISING, lambda channel: self._charged.set())
        self._queue.start()

    def __del__(self):
        GPIO.remove_event_detect(self.pin)

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
        return 1.0 - min(self.charge_time_limit, time() - start) / self.charge_time_limit

    light_detected = _alias('is_active')

    when_light = _alias('when_activated')
    when_dark = _alias('when_deactivated')

    wait_for_light = _alias('wait_for_active')
    wait_for_dark = _alias('wait_for_inactive')



class TemperatureSensor(W1ThermSensor):
    @property
    def value(self):
        return self.get_temperature()

