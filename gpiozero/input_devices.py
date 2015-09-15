from RPi import GPIO
from w1thermsensor import W1ThermSensor


class InputDevice(object):
    def __init__(self, pin=None):
        if pin is None:
            raise InputDeviceError('No GPIO pin number given')

        self.pin = pin
        self._pull = GPIO.PUD_UP
        self._edge = GPIO.FALLING
        self._active_state = 0
        self._inactive_state = 1
        GPIO.setup(pin, GPIO.IN, self._pull)

    @property
    def is_active(self):
        return GPIO.input(self.pin) == self._active_state

    def wait_for_input(self):
        GPIO.wait_for_edge(self.pin, self._edge)

    def add_callback(self, callback=None, bouncetime=1000):
        if callback is None:
            raise InputDeviceError('No callback function given')

        GPIO.add_event_detect(self.pin, self._edge, callback, bouncetime)

    def remove_callback(self):
        GPIO.remove_event_detect(self.pin)


class Button(InputDevice):
    pass


class MotionSensor(InputDevice):
    def _is_active_with_pause(self):
        sleep(0.1)
        return self.is_active

    @property
    def motion_detected(self):
        n = 20
        return sum(self._is_active_with_pause() for i in range(n)) > n/2


class LightSensor(object):
    def __init__(self, pin=None, darkness_level=0.01):
        if pin is None:
            raise InputDeviceError('No GPIO pin number given')

        self.pin = pin
        self.darkness_level = darkness_level

    @property
    def value(self):
        return self._get_average_light_level(5)

    def _get_light_level(self):
        time_taken = self._time_charging_light_capacitor()
        value = 100 * time_taken / self.darkness_level
        return 100 - value

    def _time_charging_light_capacitor(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        sleep(0.1)
        GPIO.setup(self.pin, GPIO.IN)
        start_time = time()
        end_time = time()
        while (
            GPIO.input(self.pin) == GPIO.LOW and
            time() - start_time < self.darkness_level
        ):
            end_time = time()
        time_taken = end_time - start_time
        return min(time_taken, self.darkness_level)

    def _get_average_light_level(self, num):
        values = [self._get_light_level() for n in range(num)]
        average_value = sum(values) / len(values)
        return average_value


class TemperatureSensor(W1ThermSensor):
    @property
    def value(self):
        return self.get_temperature()


class InputDeviceError(Exception):
    pass
