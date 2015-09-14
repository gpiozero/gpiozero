from RPi import GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class InputDevice(object):
    def __init__(self, pin=None):
        if pin is None:
            raise InputDeviceError('No GPIO pin number given')

        self.pin = pin
        self.pull = GPIO.PUD_UP
        self.edge = GPIO.FALLING
        self.active = 0
        self.inactive = 1
        GPIO.setup(pin, GPIO.IN, self.pull)

    def is_active(self):
        return GPIO.input(self.pin) == self.active

    def wait_for_input(self):
        GPIO.wait_for_edge(self.pin, self.edge)

    def add_callback(self, callback=None, bouncetime=1000):
        if callback is None:
            raise InputDeviceError('No callback function given')

        GPIO.add_event_detect(self.pin, self.edge, callback, bouncetime)

    def remove_callback(self):
        GPIO.remove_event_detect(self.pin)


class Button(InputDevice):
    pass


class MotionSensor(InputDevice):
    def _is_active_with_pause(self):
        sleep(0.1)
        return self.is_active()

    def motion_detected(self):
        n = 20
        return sum(self._is_active_with_pause() for i in range(n)) > n/2


class InputDeviceError(Exception):
    pass
