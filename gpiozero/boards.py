from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
try:
    from itertools import izip as zip
except ImportError:
    pass

from time import sleep
from collections import namedtuple

from .input_devices import InputDeviceError, Button
from .output_devices import OutputDeviceError, LED, PWMLED, Buzzer, Motor
from .devices import CompositeDevice, SourceMixin


class LEDBoard(SourceMixin, CompositeDevice):
    """
    A Generic LED Board or collection of LEDs.
    """
    def __init__(self, *pins, **kwargs):
        super(LEDBoard, self).__init__()
        pwm = kwargs.get('pwm', False)
        LEDClass = PWMLED if pwm else LED
        self._leds = tuple(LEDClass(pin) for pin in pins)

    def close(self):
        for led in self.leds:
            led.close()

    @property
    def closed(self):
        return all(led.closed for led in self.leds)

    @property
    def leds(self):
        """
        A tuple of all the `LED` objects contained by the instance.
        """
        return self._leds

    @property
    def value(self):
        """
        A tuple containing a boolean value for each LED on the board. This
        property can also be set to update the state of all LEDs on the board.
        """
        return tuple(led.value for led in self._leds)

    @value.setter
    def value(self, value):
        for l, v in zip(self.leds, value):
            l.value = v

    def on(self):
        """
        Turn all the LEDs on.
        """
        for led in self.leds:
            led.on()

    def off(self):
        """
        Turn all the LEDs off.
        """
        for led in self.leds:
            led.off()

    def toggle(self):
        """
        Toggle all the LEDs. For each LED, if it's on, turn it off; if it's
        off, turn it on.
        """
        for led in self.leds:
            led.toggle()

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make all the LEDs turn on and off repeatedly.

        on_time: `1`
            Number of seconds to be on

        off_time: `1`
            Number of seconds to be off

        n: `None`
            Number of times to blink; None means forever

        background: `True`
            If `True`, start a background thread to continue blinking and
            return immediately. If `False`, only return when the blink is
            finished (warning: the default value of `n` will result in this
            method never returning).
        """
        # XXX This isn't going to work for background=False
        for led in self.leds:
            led.blink(on_time, off_time, n, background)


class PiLiter(LEDBoard):
    """
    Ciseco Pi-LITEr: strip of 8 very bright LEDs.
    """
    def __init__(self, pwm=False):
        super(PiLiter, self).__init__(4, 17, 27, 18, 22, 23, 24, 25, pwm=pwm)


TrafficLightTuple = namedtuple('TrafficLightTuple', ('red', 'amber', 'green'))


class TrafficLights(LEDBoard):
    """
    Generic Traffic Lights set.

    red: `None`
        Red LED pin

    amber: `None`
        Amber LED pin

    green: `None`
        Green LED pin
    """
    def __init__(self, red=None, amber=None, green=None, pwm=False):
        if not all([red, amber, green]):
            raise OutputDeviceError(
                'red, amber and green pins must be provided'
            )
        super(TrafficLights, self).__init__(red, amber, green, pwm=pwm)

    @property
    def value(self):
        return TrafficLightTuple(*super(TrafficLights, self).value)

    @value.setter
    def value(self, value):
        # Eurgh, this is horrid but necessary (see #90)
        super(TrafficLights, self.__class__).value.fset(self, value)

    @property
    def red(self):
        """
        The `LED` object representing the red LED.
        """
        return self.leds[0]

    @property
    def amber(self):
        """
        The `LED` object representing the red LED.
        """
        return self.leds[1]

    @property
    def green(self):
        """
        The `LED` object representing the green LED.
        """
        return self.leds[2]


class PiTraffic(TrafficLights):
    """
    Low Voltage Labs PI-TRAFFIC: vertical traffic lights board on pins 9, 10
    and 11.
    """
    def __init__(self):
        super(PiTraffic, self).__init__(9, 10, 11)


TrafficLightsBuzzerTuple = namedtuple('TrafficLightsBuzzerTuple', (
    'red', 'amber', 'green', 'buzzer'))


class TrafficLightsBuzzer(SourceMixin, CompositeDevice):
    """
    A generic class for HATs with traffic lights, a button and a buzzer.
    """
    def __init__(self, lights, buzzer, button):
        super(TrafficLightsBuzzer, self).__init__()
        self.lights = lights
        self.buzzer = buzzer
        self.button = button
        self._all = self.lights.leds + (self.buzzer,)

    def close(self):
        self.lights.close()
        self.buzzer.close()
        self.button.close()

    @property
    def closed(self):
        return all(o.closed for o in self.all)

    @property
    def all(self):
        """
        A tuple containing objects for all the items on the board (several
        `LED` objects, a `Buzzer`, and a `Button`).
        """
        return self._all

    @property
    def value(self):
        """
        Returns a named-tuple containing values representing the states of
        the LEDs, and the buzzer. This property can also be set to a 4-tuple
        to update the state of all the board's components.
        """
        return FishDishTuple(
            self.lights.red.value,
            self.lights.amber.value,
            self.lights.green.value,
            self.buzzer.value,
        )

    @value.setter
    def value(self, value):
        for i, v in zip(self.all, value):
            i.value = v

    def on(self):
        """
        Turn all the board's components on.
        """
        for thing in self.all:
            thing.on()

    def off(self):
        """
        Turn all the board's components off.
        """
        for thing in self.all:
            thing.off()

    def toggle(self):
        """
        Toggle all the board's components. For each component, if it's on, turn
        it off; if it's off, turn it on.
        """
        for thing in self.all:
            thing.toggle()

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make all the board's components turn on and off repeatedly.

        on_time: `1`
            Number of seconds to be on

        off_time: `1`
            Number of seconds to be off

        n: `None`
            Number of times to blink; None means forever

        background: `True`
            If `True`, start a background thread to continue blinking and
            return immediately. If `False`, only return when the blink is
            finished (warning: the default value of `n` will result in this
            method never returning).
        """
        # XXX This isn't going to work for background=False
        for thing in self._all:
            thing.blink(on_time, off_time, n, background)


class FishDish(TrafficLightsBuzzer):
    """
    Pi Supply FishDish: traffic light LEDs, a button and a buzzer.
    """
    def __init__(self, pwm=False):
        super(FishDish, self).__init__(
            TrafficLights(9, 22, 4, pwm=pwm),
            Buzzer(8),
            Button(7, pull_up=False),
        )


class TrafficHat(TrafficLightsBuzzer):
    """
    Ryanteck Traffic HAT: traffic light LEDs, a button and a buzzer.
    """
    def __init__(self, pwm=False):
        super(TrafficHat, self).__init__(
            TrafficLights(24, 23, 22, pwm=pwm),
            Buzzer(5),
            Button(25),
        )


RobotTuple = namedtuple('RobotTuple', ('left', 'right'))


class Robot(SourceMixin, CompositeDevice):
    """
    Generic dual-motor Robot.
    """
    def __init__(self, left=None, right=None):
        if not all([left, right]):
            raise OutputDeviceError(
                'left and right motor pins must be provided'
            )
        super(Robot, self).__init__()
        self._left = Motor(*left)
        self._right = Motor(*right)

    def close(self):
        self._left.close()
        self._right.close()

    @property
    def closed(self):
        return self._left.closed and self._right.closed

    @property
    def left_motor(self):
        """
        Returns the `Motor` device representing the robot's left motor.
        """
        return self._left

    @property
    def right_motor(self):
        """
        Returns the `Motor` device representing the robot's right motor.
        """
        return self._right

    @property
    def value(self):
        """
        Returns a tuple of two floating point values (-1 to 1) representing the
        speeds of the robot's two motors (left and right). This property can
        also be set to alter the speed of both motors.
        """
        return RobotTuple(self._left.value, self._right.value)

    @value.setter
    def value(self, value):
        self._left.value, self._right.value = value

    def forward(self, speed=1):
        """
        Drive the robot forward by running both motors forward.

        speed: `1`
            Speed at which to drive the motors, 0 to 1.
        """
        self._left.forward(speed)
        self._right.forward(speed)

    def backward(self, speed=1):
        """
        Drive the robot backward by running both motors backward.

        speed: `1`
            Speed at which to drive the motors, 0 to 1.
        """
        self._left.backward(speed)
        self._right.backward(speed)

    def left(self, speed=1):
        """
        Make the robot turn left by running the right motor forward and left
        motor backward.

        speed: `1`
            Speed at which to drive the motors, 0 to 1.
        """
        self._right.forward(speed)
        self._left.backward(speed)

    def right(self, speed=1):
        """
        Make the robot turn right by running the left motor forward and right
        motor backward.

        speed: `1`
            Speed at which to drive the motors, 0 to 1.
        """
        self._left.forward(speed)
        self._right.backward(speed)

    def reverse(self):
        """
        Reverse the robot's current motor directions. If the robot is currently
        running full speed forward, it will run full speed backward. If the
        roboto is turning left at half-speed, it will turn right at half-speed.
        If the robot is currently stopped it will remain stopped.
        """
        self._left.value = -self._left.value
        self._right.value = -self._right.value

    def stop(self):
        """
        Stop the robot.
        """
        self._left.stop()
        self._right.stop()


class RyanteckRobot(Robot):
    """
    RTK MCB Robot. Generic robot controller with pre-configured pin numbers.
    """
    def __init__(self):
        super(RyanteckRobot, self).__init__((17, 18), (22, 23))
