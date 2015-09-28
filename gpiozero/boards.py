from .input_devices import Button
from .output_devices import LED, Buzzer
from .devices import GPIODeviceError

from time import sleep


class LEDBoard(object):
    """
    A Generic LED Board or collection of LEDs.
    """
    def __init__(self, leds):
        self._leds = tuple(LED(led) for led in leds)

    @property
    def leds(self):
        return self._leds

    def on(self):
        """
        Turn all the LEDs on.
        """
        for led in self._leds:
            led.on()

    def off(self):
        """
        Turn all the LEDs off.
        """
        for led in self._leds:
            led.off()

    def toggle(self):
        """
        Toggle all the LEDs. For each LED, if it's on, turn it off; if it's
        off, turn it on.
        """
        for led in self._leds:
            led.toggle()

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make all the LEDs turn on and off repeatedly.

        on_time: 1
            Number of seconds to be on

        off_time: 1
            Number of seconds to be off

        n: None
            Number of times to blink; None means forever

        background: True
            If True, start a background thread to continue blinking and return
            immediately. If False, only return when the blink is finished
            (warning: the default value of n will result in this method never
            returning).
        """
        for led in self._leds:
            led.blink(on_time, off_time, n, background)


class PiLiter(LEDBoard):
    """
    Ciseco Pi-LITEr: strip of 8 very bright LEDs.
    """
    def __init__(self):
        leds = (4, 17, 27, 18, 22, 23, 24, 25)
        super(PiLiter, self).__init__(leds)


class TrafficLights(LEDBoard):
    """
    Generic Traffic Lights set.

    red: None
        Red LED pin

    amber: None
        Amber LED pin

    green: None
        Green LED pin
    """
    def __init__(self, red=None, amber=None, green=None):
        if not all([red, amber, green]):
            raise GPIODeviceError('Red, Amber and Green pins must be provided')

        self.red = LED(red)
        self.amber = LED(amber)
        self.green = LED(green)
        self._leds = (self.red, self.amber, self.green)


class PiTraffic(TrafficLights):
    """
    Low Voltage Labs PI-TRAFFIC: vertical traffic lights board on pins 9, 10
    and 11.
    """
    def __init__(self):
        red, amber, green = (9, 10, 11)
        super(PiTraffic, self).__init__(red, amber, green)


class FishDish(TrafficLights):
    """
    Pi Supply FishDish: traffic light LEDs, a button and a buzzer.
    """
    def __init__(self):
        red, amber, green = (9, 22, 4)
        super(FishDish, self).__init__(red, amber, green)
        self.buzzer = Buzzer(8)
        self.button = Button(pin=7, pull_up=False)
        self._all = self._leds + (self.buzzer,)

    @property
    def all(self):
        return self._all

    def on(self):
        """
        Turn all the board's components on.
        """
        for thing in self._all:
            thing.on()

    def off(self):
        """
        Turn all the board's components off.
        """
        for thing in self._all:
            thing.off()

    def toggle(self):
        """
        Toggle all the board's components. For each component, if it's on, turn
        it off; if it's off, turn it on.
        """
        for thing in self._all:
            thing.toggle()

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make all the board's components turn on and off repeatedly.

        on_time: 1
            Number of seconds to be on

        off_time: 1
            Number of seconds to be off

        n: None
            Number of times to blink; None means forever

        background: True
            If True, start a background thread to continue blinking and return
            immediately. If False, only return when the blink is finished
            (warning: the default value of n will result in this method never
            returning).
        """
        for thing in self._all:
            led.blink(on_time, off_time, n, background)

    def lights_on(self):
        """
        Turn all the board's LEDs on.
        """
        super(FishDish, self).on()

    def lights_off(self):
        """
        Turn all the board's LEDs off.
        """
        super(FishDish, self).off()

    def toggle_lights(self):
        """
        Toggle all the board's LEDs. For each LED, if it's on, turn
        it off; if it's off, turn it on.
        """
        super(FishDish, self).toggle()

    def blink_lights(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make all the board's LEDs turn on and off repeatedly.

        on_time: 1
            Number of seconds to be on

        off_time: 1
            Number of seconds to be off

        n: None
            Number of times to blink; None means forever

        background: True
            If True, start a background thread to continue blinking and return
            immediately. If False, only return when the blink is finished
            (warning: the default value of n will result in this method never
            returning).
        """
        super(FishDish, self).blink(on_time, off_time, n, background)


class TrafficHat(FishDish):
    """
    Ryanteck Traffic HAT: traffic light LEDs, a button and a buzzer.
    """
    def __init__(self):
        red, amber, green = (22, 23, 24)
        super(FishDish, self).__init__(red, amber, green)
        self.buzzer = Buzzer(5)
        self.button = Button(25)
        self._all = self._leds + (self.buzzer,)
