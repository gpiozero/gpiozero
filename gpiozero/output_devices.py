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
    """
    def __init__(self, pin=None):
        super(OutputDevice, self).__init__(pin)
        # NOTE: catch_warnings isn't thread-safe but hopefully no-one's messing
        # around with GPIO init within background threads...
        with warnings.catch_warnings(record=True) as w:
            GPIO.setup(pin, GPIO.OUT)
        # The only warning we want to squash is a RuntimeWarning that is thrown
        # when setting pins 2 or 3. Anything else should be replayed
        for warning in w:
            if warning.category != RuntimeWarning or pin not in (2, 3):
                warnings.showwarning(
                    warning.message, warning.category, warning.filename,
                    warning.lineno, warning.file, warning.line
                )

    def on(self):
        """
        Turns the device on.
        """
        GPIO.output(self.pin, True)

    def off(self):
        """
        Turns the device off.
        """
        GPIO.output(self.pin, False)


class DigitalOutputDevice(OutputDevice):
    """
    Represents a generic output device with typical on/off behaviour.

    This class extends `OutputDevice` with a `toggle` method to switch the
    device between its on and off states, and a `blink` method which uses an
    optional background thread to handle toggling the device state without
    further interaction.
    """
    def __init__(self, pin=None):
        super(DigitalOutputDevice, self).__init__(pin)
        self._blink_thread = None
        self._lock = Lock()

    def on(self):
        """
        Turns the device on.
        """
        self._stop_blink()
        super(DigitalOutputDevice, self).on()

    def off(self):
        """
        Turns the device off.
        """
        self._stop_blink()
        super(DigitalOutputDevice, self).off()

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
            super(DigitalOutputDevice, self).on()
            if self._blink_thread.stopping.wait(on_time):
                break
            super(DigitalOutputDevice, self).off()
            if self._blink_thread.stopping.wait(off_time):
                break


class LED(DigitalOutputDevice):
    """
    An LED (Light Emmitting Diode) component.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the LED, and the cathode (short leg) to ground, with
    an optional resistor to prevent the LED from burning out.
    """
    pass


class Buzzer(DigitalOutputDevice):
    """
    A digital Buzzer component.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the buzzer, and the cathode (short leg) to ground.
    """
    pass


class PWMOutputDevice(DigitalOutputDevice):
    """
    Generic Output device configured for PWM (Pulse-Width Modulation).
    """
    def __init__(self, pin=None):
        super(PWMOutputDevice, self).__init__(pin)
        self._frequency = 100
        self._pwm = GPIO.PWM(self._pin, self._frequency)
        self._pwm.start(0)
        self._min_pwm = 0
        self._max_pwm = 1
        self.value = 0

    def on(self):
        """
        Turn the device on
        """
        self.value = self._max_pwm

    def off(self):
        """
        Turn the device off
        """
        self.value = self._min_pwm

    def toggle(self):
        """
        Reverse the state of the device.
        If it's on (a value greater than 0), turn it off; if it's off, turn it
        on.
        """
        _min = self._min_pwm
        _max = self._max_pwm
        self.value = _max if self.value == _min else _min

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, n):
        _min = self._min_pwm
        _max = self._max_pwm
        if _min <= n <= _max:
            n *= 100
        else:
            raise GPIODeviceError(
                "Value must be between %s and %s" % (_min, _max)
            )
        self._pwm.ChangeDutyCycle(n)
        self._value = n


class RGBLED(object):
    """
    Single LED with individually controllable Red, Green and Blue components.
    """
    def __init__(self, red=None, green=None, blue=None):
        if not all([red, green, blue]):
            raise GPIODeviceError('Red, Green and Blue pins must be provided')

        self._red = PWMOutputDevice(red)
        self._green = PWMOutputDevice(green)
        self._blue = PWMOutputDevice(blue)
        self._leds = (self._red, self._green, self._blue)

    def on(self):
        """
        Turn the device on
        """
        for led in self._leds:
            led.on()

    def off(self):
        """
        Turn the device off
        """
        for led in self._leds:
            led.off()

    @property
    def red(self):
        return self._red.value

    @red.setter
    def red(self, value):
        self._red.value = self._validate(value)

    @property
    def green(self):
        return self._green.value

    @green.setter
    def green(self, value):
        self._green.value = self._validate(value)

    @property
    def blue(self):
        return self._blue.value

    @blue.setter
    def blue(self, value):
        self._blue.value = self._validate(value)

    @property
    def rgb(self):
        r = self.red
        g = self.green
        b = self.blue
        return (r, g, b)

    @rgb.setter
    def rgb(self, values):
        r, g, b = values
        self.red = r
        self.green = g
        self.blue = b

    def _validate(self, value):
        _min = self._min_value
        _max = self._max_value
        if _min >= value >= _max:
            return value
        else:
            raise GPIODeviceError(
                "Colour value must be between %s and %s" % (_min, _max)
            )


class Motor(object):
    """
    Generic bi-directional motor.
    """
    def __init__(self, forward=None, back=None):
        if not all([forward, back]):
            raise GPIODeviceError('forward and back pins must be provided')

        self._forward = PWMOutputDevice(forward)
        self._backward = PWMOutputDevice(back)

        self._min_pwm = self._forward._min_pwm
        self._max_pwm = self._forward._max_pwm

    def forward(self, speed=1):
        """
        Drive the motor forwards
        """
        self._backward.value = self._min_pwm
        self._forward.value = self._max_pwm
        if speed < 1:
            sleep(0.1)  # warm up the motor
            self._forward.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards
        """
        self._forward.value = self._min_pwm
        self._backward.value = self._max_pwm
        if speed < 1:
            sleep(0.1)  # warm up the motor
            self._backward.value = speed

    def stop(self):
        """
        Stop the motor
        """
        self._forward.off()
        self._backward.off()
