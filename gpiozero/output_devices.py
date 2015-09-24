from time import sleep
from threading import Lock

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
        GPIO.setup(pin, GPIO.OUT)

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
    Generic Digital GPIO Output Device (on/off/blink/toggle/flash).
    """
    def __init__(self, pin=None):
        super(DigitalOutputDevice, self).__init__(pin)
        self._blink_thread = None
        self._lock = Lock()

    def on(self):
        """
        Turn the device on.
        """
        self._stop_blink()
        super(DigitalOutputDevice, self).on()

    def off(self):
        """
        Turn the device off.
        """
        self._stop_blink()
        super(DigitalOutputDevice, self).off()

    def blink(self, on_time=1, off_time=1):
        """
        Make the device turn on and off repeatedly in the background.

        on_time: 1
            Number of seconds on

        off_time: 1
            Number of seconds off
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_led, args=(on_time, off_time)
        )
        self._blink_thread.start()

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

    def flash(self, on_time=1, off_time=1, n=1):
        """
        Turn the device on and off a given number of times.

        on_time: 1
            Number of seconds on

        off_time: 1
            Number of seconds off

        n: 1
            Number of iterations
        """
        for i in range(n):
            self.on()
            sleep(on_time)
            self.off()
            if i+1 < n:  # don't sleep on final iteration
                sleep(off_time)

    def _stop_blink(self):
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_led(self, on_time, off_time):
        while True:
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
    def on(self):
        """
        Turn the LED on.
        """
        super(LED, self).on()

    def off(self):
        """
        Turn the LED off.
        """
        super(LED, self).off()

    def blink(self, on_time=1, off_time=1):
        """
        Make the LED turn on and off repeatedly in the background.

        on_time: 1
            Number of seconds on

        off_time: 1
            Number of seconds off
        """
        super(LED, self).blink()

    def toggle(self):
        """
        Reverse the state of the LED.
        If it's on, turn it off; if it's off, turn it on.
        """
        super(LED, self).toggle()

class Buzzer(DigitalOutputDevice):
    """
    A Buzzer component.
    """
    def on(self):
        """
        Turn the Buzzer on.
        """
        super(Buzzer, self).on()

    def off(self):
        """
        Turn the Buzzer off.
        """
        super(Buzzer, self).off()

    def blink(self, on_time=1, off_time=1):
        """
        Make the Buzzer turn on and off repeatedly in the background.

        on_time: 1
            Number of seconds on

        off_time: 1
            Number of seconds off
        """
        super(Buzzer, self).blink()

    def toggle(self):
        """
        Reverse the state of the Buzzer.
        If it's on, turn it off; if it's off, turn it on.
        """
        super(Buzzer, self).toggle()


class Motor(OutputDevice):
    def on(self):
        """
        Turns the Motor on.
        """
        super(Motor, self).toggle()

    def off(self):
        """
        Turns the Motor off.
        """
        super(Motor, self).toggle()


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
