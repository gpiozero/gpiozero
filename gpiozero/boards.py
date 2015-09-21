from .input_devices import Button
from .output_devices import LED, Buzzer
from .devices import GPIODeviceError


class TrafficLights(object):
    def __init__(self, red=None, amber=None, green=None):
        if not all([red, amber, green]):
            raise GPIODeviceError('Red, Amber and Green pins must be provided')

        self.red = LED(red)
        self.amber = LED(amber)
        self.green = LED(green)
        self._lights = (self.red, self.amber, self.green)

    def on(self):
        for led in self._lights:
            led.on()

    def off(self):
        for led in self._lights:
            led.off()


class PiTraffic(TrafficLights):
    def __init__(self):
        red, amber, green = (9, 10, 11)
        super(FishDish, self).__init__(red, amber, green)


class FishDish(TrafficLights):
    def __init__(self):
        red, amber, green = (9, 22, 4)
        super(FishDish, self).__init__(red, amber, green)
        self.buzzer = Buzzer(8)
        self.button = Button(pin=7, pull_up=False)
        self._all = tuple(list(self._lights) + [self.buzzer])

    def on(self):
        for thing in self._all:
            thing.on()

    def off(self):
        for thing in self._all:
            thing.off()

    def lights_on(self):
        super.on()

    def lights_off(self):
        super.off()


class PiLiter(object):
    def __init__(self):
        leds = [4, 17, 27, 18, 22, 23, 24, 25]
        self.leds = tuple([LED(led) for led in leds])

    def on(self):
        for led in self.leds:
            led.on()

    def off(self):
        for led in self.leds:
            led.off()
