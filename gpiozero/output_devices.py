from RPi import GPIO

from time import sleep
from threading import Thread, Event

from .devices import GPIODevice, GPIODeviceError


class OutputDeviceError(GPIODeviceError):
    pass


class OutputDevice(GPIODevice):
    def __init__(self, pin=None):
        super(OutputDevice, self).__init__(pin)
        GPIO.setup(pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, True)

    def off(self):
        GPIO.output(self.pin, False)


class LED(OutputDevice):
    def __init__(self, pin=None):
        super(LED, self).__init__(pin)
        self._thread = None
        self._terminate = Event()

    def __del__(self):
        self._stop_blink()

    def blink(self, on_time, off_time):
        self._stop_blink()
        self._terminate.clear()
        self._thread = Thread(target=self._blink_led, args=(on_time, off_time))
        self._thread.start()

    def _stop_blink(self):
        if self._thread:
            self._terminate.set()
            self._thread.join()
            self._thread = None

    def _blink_led(self, on_time, off_time):
        while True:
            super(LED, self).on()
            if self._terminate.wait(on_time):
                break
            super(LED, self).off()
            if self._terminate.wait(off_time):
                break

    def on(self):
        self._stop_blink()
        super(LED, self).on()

    def off(self):
        self._stop_blink()
        super(LED, self).off()


class Buzzer(OutputDevice):
    pass


class Motor(OutputDevice):
    pass
