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

    def _write(self, value):
        GPIO.output(self.pin, bool(value))

    def on(self):
        """
        Turns the device on.
        """
        self._write(1)

    def off(self):
        """
        Turns the device off.
        """
        self._write(0)


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
        self._write(1)

    def off(self):
        """
        Turns the device off.
        """
        self._stop_blink()
        self._write(0)

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
            self._write(1)
            if self._blink_thread.stopping.wait(on_time):
                break
            self._write(0)
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
    def __init__(self, pin=None, frequency=100):
        super(PWMOutputDevice, self).__init__(pin)
        try:
            self._pwm = GPIO.PWM(self._pin, frequency)
            self._pwm.start(0.0)
            self._frequency = frequency
            self._value = 0.0
        except:
            self.close()
            raise

    def _read(self):
        return self._value

    def _write(self, value):
        if not 0 <= value <= 1:
            raise OutputDeviceError("PWM value must be between 0 and 1")
        self._pwm.ChangeDutyCycle(value * 100)
        self._value = value

    def _get_value(self):
        return self._read()

    def _set_value(self, value):
        self._stop_blink()
        self._write(value)

    value = property(_get_value, _set_value, doc="""\
        The duty cycle of the PWM device. 0.0 is off, 1.0 is fully on. Values
        in between may be specified for varying levels of power in the device.
        """)

    @property
    def is_active(self):
        return self.value > 0.0

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, value):
        self._pwm.ChangeFrequency(value)
        self._frequency = value

    frequency = property(_get_frequency, _set_frequency, doc="""\
        The frequency of the pulses used with the PWM device, in Hz. The
        default is 100.
        """)


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
