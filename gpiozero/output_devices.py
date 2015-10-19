import warnings
from time import sleep
from threading import Lock
from itertools import repeat

from RPi import GPIO

from .devices import GPIODeviceError, GPIODevice, GPIOThread


class OutputDeviceError(GPIODeviceError):
    pass


class OutputDevice(GPIODevice):
    """
    Represents a generic GPIO output device.

    This class extends `GPIODevice` to add facilities common to GPIO output
    devices: an `on` method to switch the device on, and a corresponding `off`
    method.

    active_high: `True`
        If `True` (the default), the `on` method will set the GPIO to HIGH. If
        `False`, the `on` method will set the GPIO to LOW (the `off` method
        always does the opposite).
    """

    __slots__ = ('_active_high', '_source', '_source_thread')

    def __init__(self, pin=None, active_high=True):
        self._active_high = active_high
        self._source = None
        self._source_thread = None
        super(OutputDevice, self).__init__(pin)
        self._active_state = GPIO.HIGH if active_high else GPIO.LOW
        self._inactive_state = GPIO.LOW if active_high else GPIO.HIGH
        try:
            # NOTE: catch_warnings isn't thread-safe but hopefully no-one's
            # messing around with GPIO init within background threads...
            with warnings.catch_warnings(record=True) as w:
                GPIO.setup(pin, GPIO.OUT)
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

    def close(self):
        self.source = None
        super(OutputDevice, self).close()

    def _write(self, value):
        GPIO.output(self.pin, bool(value))

    def on(self):
        """
        Turns the device on.
        """
        self._write(self._active_state)

    def off(self):
        """
        Turns the device off.
        """
        self._write(self._inactive_state)

    @property
    def value(self):
        return super(OutputDevice, self).value

    @value.setter
    def value(self, value):
        self._write(value)

    def _copy_values(self, source):
        for v in source:
            self.value = v
            if self._source_thread.stopping.wait(0):
                break

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if self._source_thread is not None:
            self._source_thread.stop()
            self._source_thread = None
        self._source = value
        if value is not None:
            self._source_thread = GPIOThread(target=self._copy_values, args=(value,))
            self._source_thread.start()

    @property
    def active_high(self):
        return self._active_high

    def __repr__(self):
        try:
            return '<gpiozero.%s object on pin=%d, active_high=%s, is_active=%s>' % (
                self.__class__.__name__, self.pin, self.active_high, self.is_active)
        except:
            return super(OutputDevice, self).__repr__()


class DigitalOutputDevice(OutputDevice):
    """
    Represents a generic output device with typical on/off behaviour.

    This class extends `OutputDevice` with a `toggle` method to switch the
    device between its on and off states, and a `blink` method which uses an
    optional background thread to handle toggling the device state without
    further interaction.
    """

    __slots__ = ('_blink_thread', '_lock')

    def __init__(self, pin=None, active_high=True):
        super(DigitalOutputDevice, self).__init__(pin, active_high)
        self._blink_thread = None
        self._lock = Lock()

    def close(self):
        self._stop_blink()
        super(DigitalOutputDevice, self).close()

    def on(self):
        """
        Turns the device on.
        """
        self._stop_blink()
        self._write(self._active_state)

    def off(self):
        """
        Turns the device off.
        """
        self._stop_blink()
        self._write(self._inactive_state)

    def toggle(self):
        """
        Reverse the state of the device.
        If it's on, turn it off; if it's off, turn it on.
        """
        with self._lock:
            if self.is_active:
                self.off()
            else:
                self.on()

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make the device turn on and off repeatedly.

        on_time: 1
            Number of seconds on

        off_time: 1
            Number of seconds off

        n: None
            Number of times to blink; None means forever

        background: True
            If True, start a background thread to continue blinking and return
            immediately. If False, only return when the blink is finished
            (warning: the default value of n will result in this method never
            returning).
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_led, args=(on_time, off_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _stop_blink(self):
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_led(self, on_time, off_time, n):
        iterable = repeat(0) if n is None else repeat(0, n)
        for i in iterable:
            self._write(self._active_state)
            if self._blink_thread.stopping.wait(on_time):
                break
            self._write(self._inactive_state)
            if self._blink_thread.stopping.wait(off_time):
                break


class LED(DigitalOutputDevice):
    """
    An LED (Light Emmitting Diode) component.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the LED, and the cathode (short leg) to ground, with
    an optional resistor to prevent the LED from burning out.
    """
    __slots__ = ()

LED.is_lit = LED.is_active


class Buzzer(DigitalOutputDevice):
    """
    A digital Buzzer component.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the buzzer, and the cathode (short leg) to ground.
    """
    __slots__ = ()


class PWMOutputDevice(DigitalOutputDevice):
    """
    Generic Output device configured for PWM (Pulse-Width Modulation).
    """

    __slots__ = ('_pwm', '_frequency', '_value')

    def __init__(self, pin=None, frequency=100):
        self._pwm = None
        super(PWMOutputDevice, self).__init__(pin)
        try:
            self._pwm = GPIO.PWM(self.pin, frequency)
            self._pwm.start(0.0)
            self._frequency = frequency
            self._value = 0.0
        except:
            self.close()
            raise

    def close(self):
        if self._pwm:
            # Ensure we wipe out the PWM object so that re-runs don't attempt
            # to re-stop the PWM thread (otherwise, the fact that close is
            # called from __del__ can easily result in us stopping the PWM
            # on *another* instance on the same pin)
            p = self._pwm
            self._pwm = None
            p.stop()
        super(PWMOutputDevice, self).close()

    def _read(self):
        return self._value

    def _write(self, value):
        if not 0 <= value <= 1:
            raise OutputDeviceError("PWM value must be between 0 and 1")
        self._pwm.ChangeDutyCycle(value * 100)
        self._value = value

    @property
    def value(self):
        """
        The duty cycle of the PWM device. 0.0 is off, 1.0 is fully on. Values
        in between may be specified for varying levels of power in the device.
        """
        return self._read()

    @value.setter
    def value(self, value):
        self._stop_blink()
        self._write(value)

    @property
    def is_active(self):
        return self.value > 0.0

    @property
    def frequency(self):
        """
        The frequency of the pulses used with the PWM device, in Hz. The
        default is 100.
        """
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._pwm.ChangeFrequency(value)
        self._frequency = value


class PWMLED(PWMOutputDevice):
    pass


def _led_property(index, doc=None):
    return property(
        lambda self: getattr(self._leds[index], 'value'),
        lambda self, value: setattr(self._leds[index], 'value', value),
        doc
    )


class RGBLED(object):
    """
    Single LED with individually controllable red, green and blue components.

    red: `None`
        The GPIO pin that controls the red component of the RGB LED.

    green: `None`
        The GPIO pin that controls the green component of the RGB LED.

    blue: `None`
        The GPIO pin that controls the blue component of the RGB LED.
    """

    __slots__ = ('_leds')

    def __init__(self, red=None, green=None, blue=None):
        self._leds = tuple(PWMOutputDevice(pin) for pin in (red, green, blue))

    red = _led_property(0)
    green = _led_property(1)
    blue = _led_property(2)

    @property
    def color(self):
        """
        Set the color of the LED from an RGB 3-tuple of `(red, green, blue)`
        where each value between 0 and 1.

        For example, purple would be `(1, 0, 1)` and yellow would be `(1, 1,
        0)`, while orange would be `(1, 0.5, 0)`.
        """
        return (self.red, self.green, self.blue)

    @color.setter
    def color(self, value):
        self.red, self.green, self.blue = value

    def on(self):
        """
        Turn the device on. This equivalent to setting the device color to
        white `(1, 1, 1)`.
        """
        self.color = (1, 1, 1)

    def off(self):
        """
        Turn the device off. This is equivalent to setting the device color
        to black `(0, 0, 0)`.
        """
        self.color = (0, 0, 0)

    def close(self):
        for led in self._leds:
            led.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class Motor(object):
    """
    Generic bi-directional motor.
    """

    __slots__ = ('_forward', '_backward')

    def __init__(self, forward=None, back=None):
        if not all([forward, back]):
            raise GPIODeviceError('forward and back pins must be provided')

        self._forward = PWMOutputDevice(forward)
        self._backward = PWMOutputDevice(back)

    def forward(self, speed=1):
        """
        Drive the motor forwards
        """
        self._backward.off()
        self._forward.on()
        if speed < 1:
            sleep(0.1)  # warm up the motor
            self._forward.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards
        """
        self._forward.off()
        self._backward.on()
        if speed < 1:
            sleep(0.1)  # warm up the motor
            self._backward.value = speed

    def stop(self):
        """
        Stop the motor
        """
        self._forward.off()
        self._backward.off()
