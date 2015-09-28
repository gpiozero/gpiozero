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
    Generic GPIO Output Device (on/off).
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
                        warning.lineno, warning.file, warning.line)

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
    Generic Digital GPIO Output Device (on/off/toggle/blink).
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
    """
    pass


class Buzzer(DigitalOutputDevice):
    """
    A digital Buzzer component.
    """
    pass


class Motor(OutputDevice):
    """
    Generic single-direction motor.
    """
    pass


class Robot(object):
    """
    Generic single-direction dual-motor Robot.
    """
    def __init__(self, left=None, right=None):
        if not all([left, right]):
            raise GPIODeviceError('left and right pins must be provided')

        self._left = Motor(left)
        self._right = Motor(right)

    def left(self, seconds=None):
        """
        Turns left for a given number of seconds.

        seconds: None
            Number of seconds to turn left for
        """
        self._left.on()
        if seconds is not None:
            sleep(seconds)
            self._left.off()

    def right(self, seconds=None):
        """
        Turns right for a given number of seconds.

        seconds: None
            Number of seconds to turn right for
        """
        self._right.on()
        if seconds is not None:
            sleep(seconds)
            self._right.off()

    def forwards(self, seconds=None):
        """
        Drives forward for a given number of seconds.

        seconds: None
            Number of seconds to drive forward for
        """
        self.left()
        self.right()
        if seconds is not None:
            sleep(seconds)
            self.stop()

    def stop(self):
        """
        Stops both motors.
        """
        self._left.off()
        self._right.off()
