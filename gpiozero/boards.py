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
from itertools import repeat, cycle, chain

from .exc import InputDeviceError, OutputDeviceError
from .input_devices import Button
from .output_devices import LED, PWMLED, Buzzer, Motor
from .devices import GPIOThread, CompositeDevice, SourceMixin


class LEDBoard(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic LED board or
    collection of LEDs.

    The following example turns on all the LEDs on a board containing 5 LEDs
    attached to GPIO pins 2 through 6::

        from gpiozero import LEDBoard

        leds = LEDBoard(2, 3, 4, 5, 6)
        leds.on()

    :param int \*pins:
        Specify the GPIO pins that the LEDs of the board are attached to. You
        can designate as many pins as necessary.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.
    """
    def __init__(self, *pins, **kwargs):
        self._blink_thread = None
        super(LEDBoard, self).__init__()
        pwm = kwargs.get('pwm', False)
        LEDClass = PWMLED if pwm else LED
        self._leds = tuple(LEDClass(pin) for pin in pins)

    def close(self):
        self._stop_blink()
        for led in self.leds:
            led.close()

    @property
    def closed(self):
        return all(led.closed for led in self.leds)

    @property
    def leds(self):
        """
        A tuple of all the :class:`LED` or :class:`PWMLED` objects contained by
        the instance.
        """
        return self._leds

    @property
    def value(self):
        """
        A tuple containing a value for each LED on the board. This property can
        also be set to update the state of all LEDs on the board.
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
        self._stop_blink()
        for led in self.leds:
            led.on()

    def off(self):
        """
        Turn all the LEDs off.
        """
        self._stop_blink()
        for led in self.leds:
            led.off()

    def toggle(self):
        """
        Toggle all the LEDs. For each LED, if it's on, turn it off; if it's
        off, turn it on.
        """
        for led in self.leds:
            led.toggle()

    def blink(
            self, on_time=1, off_time=1, fade_in_time=0, fade_out_time=0,
            n=None, background=True):
        """
        Make all the LEDs turn on and off repeatedly.

        :param float on_time:
            Number of seconds on. Defaults to 1 second.

        :param float off_time:
            Number of seconds off. Defaults to 1 second.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 0. Must be 0 if
            ``pwm`` was ``False`` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 0. Must be 0 if
            ``pwm`` was ``False`` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True``, start a background thread to continue blinking and
            return immediately. If ``False``, only return when the blink is
            finished (warning: the default value of *n* will result in this
            method never returning).
        """
        if isinstance(self.leds[0], LED):
            if fade_in_time:
                raise ValueError('fade_in_time must be 0 with non-PWM LEDs')
            if fade_out_time:
                raise ValueError('fade_out_time must be 0 with non-PWM LEDs')
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_device,
            args=(on_time, off_time, fade_in_time, fade_out_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _stop_blink(self):
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_device(self, on_time, off_time, fade_in_time, fade_out_time, n, fps=50):
        sequence = []
        if fade_in_time > 0:
            sequence += [
                (i * (1 / fps) / fade_in_time, 1 / fps)
                for i in range(int(fps * fade_in_time))
                ]
        sequence.append((1, on_time))
        if fade_out_time > 0:
            sequence += [
                (1 - (i * (1 / fps) / fade_out_time), 1 / fps)
                for i in range(int(fps * fade_out_time))
                ]
        sequence.append((0, off_time))
        sequence = (
                cycle(sequence) if n is None else
                chain.from_iterable(repeat(sequence, n))
                )
        for value, delay in sequence:
            for led in self.leds:
                led.value = value
            if self._blink_thread.stopping.wait(delay):
                break


class PiLiter(LEDBoard):
    """
    Extends :class:`LEDBoard` for the Ciseco Pi-LITEr: a strip of 8 very bright
    LEDs.

    The Pi-LITEr pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example turns on all the LEDs
    of the Pi-LITEr::

        from gpiozero import PiLiter

        lite = PiLiter()
        lite.on()

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.
    """
    def __init__(self, pwm=False):
        super(PiLiter, self).__init__(4, 17, 27, 18, 22, 23, 24, 25, pwm=pwm)


TrafficLightTuple = namedtuple('TrafficLightTuple', ('red', 'amber', 'green'))


class TrafficLights(LEDBoard):
    """
    Extends :class:`LEDBoard` for devices containing red, amber, and green
    LEDs.

    The following example initializes a device connected to GPIO pins 2, 3,
    and 4, then lights the amber LED attached to GPIO 3::

        from gpiozero import TrafficLights

        traffic = TrafficLights(2, 3, 4)
        traffic.amber.on()

    :param int red:
        The GPIO pin that the red LED is attached to.

    :param int amber:
        The GPIO pin that the amber LED is attached to.

    :param int green:
        The GPIO pin that the green LED is attached to.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.
    """
    def __init__(self, red=None, amber=None, green=None, pwm=False):
        if not all([red, amber, green]):
            raise OutputDeviceError(
                'red, amber and green pins must be provided'
            )
        super(TrafficLights, self).__init__(red, amber, green, pwm=pwm)

    @property
    def value(self):
        """
        A 3-tuple containing values for the red, amber, and green LEDs. This
        property can also be set to alter the state of the LEDs.
        """
        return TrafficLightTuple(*super(TrafficLights, self).value)

    @value.setter
    def value(self, value):
        # Eurgh, this is horrid but necessary (see #90)
        super(TrafficLights, self.__class__).value.fset(self, value)

    @property
    def red(self):
        """
        The :class:`LED` or :class:`PWMLED` object representing the red LED.
        """
        return self.leds[0]

    @property
    def amber(self):
        """
        The :class:`LED` or :class:`PWMLED` object representing the red LED.
        """
        return self.leds[1]

    @property
    def green(self):
        """
        The :class:`LED` or :class:`PWMLED` object representing the green LED.
        """
        return self.leds[2]


class PiTraffic(TrafficLights):
    """
    Extends :class:`TrafficLights` for the Low Voltage Labs PI-TRAFFIC:
    vertical traffic lights board when attached to GPIO pins 9, 10, and 11.

    There's no need to specify the pins if the PI-TRAFFIC is connected to the
    default pins (9, 10, 11). The following example turns on the amber LED on
    the PI-TRAFFIC::

        from gpiozero import PiTraffic

        traffic = PiTraffic()
        traffic.amber.on()

    To use the PI-TRAFFIC board when attached to a non-standard set of pins,
    simply use the parent class, :class:`TrafficLights`.
    """
    def __init__(self):
        super(PiTraffic, self).__init__(9, 10, 11)


TrafficLightsBuzzerTuple = namedtuple('TrafficLightsBuzzerTuple', (
    'red', 'amber', 'green', 'buzzer'))


class TrafficLightsBuzzer(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and is a generic class for HATs with
    traffic lights, a button and a buzzer.

    :param TrafficLights lights:
        An instance of :class:`TrafficLights` representing the traffic lights
        of the HAT.

    :param Buzzer buzzer:
        An instance of :class:`Buzzer` representing the buzzer on the HAT.

    :param Button button:
        An instance of :class:`Button` representing the button on the HAT.
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
        :class:`LED` objects, a :class:`Buzzer`, and a :class:`Button`).
        """
        return self._all

    @property
    def value(self):
        """
        Returns a named-tuple containing values representing the states of
        the LEDs, and the buzzer. This property can also be set to a 4-tuple
        to update the state of all the board's components.
        """
        return TrafficLightsBuzzerTuple(
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

        :param float on_time:
            Number of seconds on

        :param float off_time:
            Number of seconds off

        :param int n:
            Number of times to blink; ``None`` means forever

        :param bool background:
            If ``True``, start a background thread to continue blinking and
            return immediately. If ``False``, only return when the blink is
            finished (warning: the default value of *n* will result in this
            method never returning).
        """
        # XXX This isn't going to work for background=False
        for thing in self._all:
            thing.blink(on_time, off_time, n, background)


class FishDish(TrafficLightsBuzzer):
    """
    Extends :class:`TrafficLightsBuzzer` for the Pi Supply FishDish: traffic
    light LEDs, a button and a buzzer.

    The FishDish pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example waits for the button
    to be pressed on the FishDish, then turns on all the LEDs::

        from gpiozero import FishDish

        fish = FishDish()
        fish.button.wait_for_press()
        fish.lights.on()

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.
    """
    def __init__(self, pwm=False):
        super(FishDish, self).__init__(
            TrafficLights(9, 22, 4, pwm=pwm),
            Buzzer(8),
            Button(7, pull_up=False),
        )


class TrafficHat(TrafficLightsBuzzer):
    """
    Extends :class:`TrafficLightsBuzzer` for the Ryanteck Traffic HAT: traffic
    light LEDs, a button and a buzzer.

    The Traffic HAT pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example waits for the
    button to be pressed on the Traffic HAT, then turns on all the LEDs::

        from gpiozero import TrafficHat

        hat = TrafficHat()
        hat.button.wait_for_press()
        hat.lights.on()

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.
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
    Extends :class:`CompositeDevice` to represent a generic dual-motor robot.

    This class is constructed with two tuples representing the forward and
    backward pins of the left and right controllers respectively. For example,
    if the left motor's controller is connected to GPIOs 4 and 14, while the
    right motor's controller is connected to GPIOs 17 and 18 then the following
    example will turn the robot left::

        from gpiozero import Robot

        robot = Robot(left=(4, 14), right=(17, 18))
        robot.left()

    :param tuple left:
        A tuple of two GPIO pins representing the forward and backward inputs
        of the left motor's controller.

    :param tuple right:
        A tuple of two GPIO pins representing the forward and backward inputs
        of the right motor's controller.
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

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.forward(speed)
        self._right.forward(speed)

    def backward(self, speed=1):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.backward(speed)
        self._right.backward(speed)

    def left(self, speed=1):
        """
        Make the robot turn left by running the right motor forward and left
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._right.forward(speed)
        self._left.backward(speed)

    def right(self, speed=1):
        """
        Make the robot turn right by running the left motor forward and right
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.forward(speed)
        self._right.backward(speed)

    def reverse(self):
        """
        Reverse the robot's current motor directions. If the robot is currently
        running full speed forward, it will run full speed backward. If the
        robot is turning left at half-speed, it will turn right at half-speed.
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
    Extends :class:`Robot` for the Ryanteck MCB robot.

    The Ryanteck MCB pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example turns the robot
    left::

        from gpiozero import RyanteckRobot

        robot = RyanteckRobot()
        robot.left()
    """
    def __init__(self):
        super(RyanteckRobot, self).__init__(left=(17, 18), right=(22, 23))


class CamJamKitRobot(Robot):
    """
    Extends :class:`Robot` for the `CamJam #3 EduKit`_ robot controller.

    The CamJam robot controller pins are fixed and therefore there's no need
    to specify them when constructing this class. The following example turns
    the robot left::

        from gpiozero import CamJamKitRobot

        robot = CamJamKitRobot()
        robot.left()

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    def __init__(self):
        super(CamJamKitRobot, self).__init__(left=(9, 10), right=(7, 8))

