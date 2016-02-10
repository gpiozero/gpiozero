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
from itertools import repeat, cycle, chain
from threading import Lock

from .exc import (
    DeviceClosed,
    GPIOPinMissing,
    EnergenieSocketMissing,
    EnergenieBadSocket,
    )
from .input_devices import Button
from .output_devices import OutputDevice, LED, PWMLED, Buzzer, Motor
from .threads import GPIOThread
from .devices import Device, CompositeDevice
from .mixins import SharedMixin, SourceMixin


class CompositeOutputDevice(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` with :meth:`on`, :meth:`off`, and
    :meth:`toggle` methods for controlling subordinate output devices.  Also
    extends :attr:`value` to be writeable.

    :param list _order:
        If specified, this is the order of named items specified by keyword
        arguments (to ensure that the :attr:`value` tuple is constructed with a
        specific order). All keyword arguments *must* be included in the
        collection. If omitted, an alphabetically sorted order will be selected
        for keyword arguments.
    """

    def on(self):
        """
        Turn all the output devices on.
        """
        for device in self.all:
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.on()

    def off(self):
        """
        Turn all the output devices off.
        """
        for device in self.all:
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.off()

    def toggle(self):
        """
        Toggle all the output devices. For each device, if it's on, turn it
        off; if it's off, turn it on.
        """
        for device in self.all:
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.toggle()

    @property
    def value(self):
        """
        A tuple containing a value for each subordinate device. This property
        can also be set to update the state of all subordinate output devices.
        """
        return super(CompositeOutputDevice, self).value

    @value.setter
    def value(self, value):
        for device, v in zip(self.all, value):
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.value = v
            # Simply ignore values for non-output devices


class LEDCollection(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice`. Abstract base class for
    :class:`LEDBoard` and :class:`LEDBarGraph`.
    """

    def __init__(self, *args, **kwargs):
        self._blink_thread = None
        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', False)
        order = kwargs.pop('_order', None)
        LEDClass = PWMLED if pwm else LED
        super(LEDCollection, self).__init__(
            *(
                pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(pin_or_collection, active_high, initial_value)
                for pin_or_collection in args
                ),
            _order=order,
            **{
                name: pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(pin_or_collection, active_high, initial_value)
                for name, pin_or_collection in kwargs.items()
                })

    @property
    def leds(self):
        """
        A flat iterator over all LEDs contained in this collection (and all
        sub-collections).
        """
        for item in self:
            if isinstance(item, LEDCollection):
                for subitem in item.leds:
                    yield subitem
            else:
                yield item


class LEDBoard(LEDCollection):
    """
    Extends :class:`LEDCollection` and represents a generic LED board or
    collection of LEDs.

    The following example turns on all the LEDs on a board containing 5 LEDs
    attached to GPIO pins 2 through 6::

        from gpiozero import LEDBoard

        leds = LEDBoard(2, 3, 4, 5, 6)
        leds.on()

    :param int \*pins:
        Specify the GPIO pins that the LEDs of the board are attached to. You
        can designate as many pins as necessary. You can also specify
        :class:`LEDBoard` instances to create trees of LEDs.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set all the
        associates pins to HIGH. If ``False``, the :meth:`on` method will set
        all pins to LOW (the :meth:`off` method always does the opposite).

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param \*\*named_pins:
        Sepcify GPIO pins that LEDs of the board are attached to, associated
        each LED with a property name. You can designate as many pins as
        necessary and any name provided it's not already in use by something
        else. You can also specify :class:`LEDBoard` instances to create
        trees of LEDs.
    """
    def __init__(self, *args, **kwargs):
        self._blink_leds = []
        self._blink_lock = Lock()
        super(LEDBoard, self).__init__(*args, **kwargs)

    def close(self):
        self._stop_blink()
        super(LEDBoard, self).close()

    def on(self, *args):
        self._stop_blink()
        if args:
            for index in args:
                self[index].on()
        else:
            super(LEDBoard, self).on()

    def off(self, *args):
        self._stop_blink()
        if args:
            for index in args:
                self[index].off()
        else:
            super(LEDBoard, self).off()

    def toggle(self, *args):
        self._stop_blink()
        if args:
            for index in args:
                self[index].toggle()
        else:
            super(LEDBoard, self).toggle()

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
        for led in self.leds:
            if isinstance(led, LED):
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

    def _stop_blink(self, led=None):
        if led is None:
            if self._blink_thread:
                self._blink_thread.stop()
                self._blink_thread = None
        else:
            with self._blink_lock:
                self._blink_leds.remove(led)

    def pulse(self, fade_in_time=1, fade_out_time=1, n=None, background=True):
        """
        Make the device fade in and out repeatedly.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True`` (the default), start a background thread to continue
            blinking and return immediately. If ``False``, only return when the
            blink is finished (warning: the default value of *n* will result in
            this method never returning).
        """
        on_time = off_time = 0
        self.blink(
            on_time, off_time, fade_in_time, fade_out_time, n, background
        )

    def _blink_device(self, on_time, off_time, fade_in_time, fade_out_time, n, fps=25):
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
        with self._blink_lock:
            self._blink_leds = list(self.leds)
            for led in self._blink_leds:
                if led._controller not in (None, self):
                    led._controller._stop_blink(led)
                led._controller = self
        for value, delay in sequence:
            with self._blink_lock:
                if not self._blink_leds:
                    break
                for led in self._blink_leds:
                    led._write(value)
            if self._blink_thread.stopping.wait(delay):
                break


class LEDBarGraph(LEDCollection):
    """
    Extends :class:`LEDCollection` to control a line of LEDs representing a
    bar graph. Positive values (0 to 1) light the LEDs from first to last.
    Negative values (-1 to 0) light the LEDs from last to first.

    The following example demonstrates turning on the first two and last two
    LEDs in a board containing five LEDs attached to GPIOs 2 through 6::

        from gpiozero import LEDBarGraph
        from time import sleep

        graph = LEDBarGraph(2, 3, 4, 5, 6)
        graph.value = 2/5  # Light the first two LEDs only
        sleep(1)
        graph.value = -2/5 # Light the last two LEDs only
        sleep(1)
        graph.off()

    As with other output devices, :attr:`source` and :attr:`values` are
    supported::

        from gpiozero import LEDBarGraph, MCP3008
        from signal import pause

        graph = LEDBarGraph(2, 3, 4, 5, 6, pwm=True)
        pot = MCP3008(channel=0)
        graph.source = pot.values
        pause()

    :param int \*pins:
        Specify the GPIO pins that the LEDs of the bar graph are attached to.
        You can designate as many pins as necessary.

    :param float initial_value:
        The initial :attr:`value` of the graph given as a float between -1 and
        +1.  Defaults to 0.0. This parameter can only be specified as a keyword
        parameter.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.
    """

    def __init__(self, *pins, **kwargs):
        # Don't allow graphs to contain collections
        for pin in pins:
            assert not isinstance(pin, LEDCollection)
        pwm = kwargs.pop('pwm', False)
        initial_value = kwargs.pop('initial_value', 0)
        if kwargs:
            raise TypeError('unexpected keyword argument: %s' % kwargs.popitem()[0])
        super(LEDBarGraph, self).__init__(*pins, pwm=pwm)
        try:
            self.value = initial_value
        except:
            self.close()
            raise

    @property
    def value(self):
        """
        The value of the LED bar graph. When no LEDs are lit, the value is 0.
        When all LEDs are lit, the value is 1. Values between 0 and 1
        light LEDs linearly from first to last. Values between 0 and -1
        light LEDs linearly from last to first.

        To light a particular number of LEDs, simply divide that number by
        the number of LEDs. For example, if your graph contains 3 LEDs, the
        following will light the first::

            from gpiozero import LEDBarGraph

            graph = LEDBarGraph(12, 16, 19)
            graph.value = 1/3

        .. note::

            Setting value to -1 will light all LEDs. However, querying it
            subsequently will return 1 as both representations are the same in
            hardware. The readable range of :attr:`value` is effectively
            -1 < value <= 1.
        """
        result = sum(led.value for led in self)
        if self[0].value < self[-1].value:
            result = -result
        return result / len(self)

    @value.setter
    def value(self, value):
        count = len(self)
        leds = self
        if value < 0:
            leds = reversed(leds)
            value = -value
        if isinstance(self[0], PWMLED):
            calc_value = lambda index: min(1, max(0, count * value - index))
        else:
            calc_value = lambda index: value >= ((index + 1) / count)
        for index, led in enumerate(leds):
            led.value = calc_value(index)


class PiLiter(LEDBoard):
    """
    Extends :class:`LEDBoard` for the `Ciseco Pi-LITEr`_: a strip of 8 very bright
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

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, pwm=False):
        super(PiLiter, self).__init__(4, 17, 27, 18, 22, 23, 24, 25, pwm=pwm)


class PiLiterBarGraph(LEDBarGraph):
    """
    Extends :class:`LEDBarGraph` to treat the `Ciseco Pi-LITEr`_ as an
    8-segment bar graph.

    The Pi-LITEr pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example sets the graph value
    to 0.5::

        from gpiozero import PiLiterBarGraph

        graph = PiLiterBarGraph()
        graph.value = 0.5

    :param bool initial_value:
        The initial value of the graph given as a float between -1 and +1.
        Defaults to 0.0.

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, initial_value=0):
        super(PiLiterBarGraph, self).__init__(
                4, 17, 27, 18, 22, 23, 24, 25, initial_value=initial_value)


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
            raise GPIOPinMissing(
                'red, amber and green pins must be provided'
            )
        super(TrafficLights, self).__init__(
            red=red, amber=amber, green=green, pwm=pwm,
            _order=('red', 'amber', 'green'))


class PiTraffic(TrafficLights):
    """
    Extends :class:`TrafficLights` for the `Low Voltage Labs PI-TRAFFIC`_:
    vertical traffic lights board when attached to GPIO pins 9, 10, and 11.

    There's no need to specify the pins if the PI-TRAFFIC is connected to the
    default pins (9, 10, 11). The following example turns on the amber LED on
    the PI-TRAFFIC::

        from gpiozero import PiTraffic

        traffic = PiTraffic()
        traffic.amber.on()

    To use the PI-TRAFFIC board when attached to a non-standard set of pins,
    simply use the parent class, :class:`TrafficLights`.

    .. _Low Voltage Labs PI-TRAFFIC: http://lowvoltagelabs.com/products/pi-traffic/
    """

    def __init__(self):
        super(PiTraffic, self).__init__(9, 10, 11)


class SnowPi(LEDBoard):
    """
    Extends :class:`LEDBoard` for the `Ryanteck SnowPi`_ board.

    The SnowPi pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example turns on the eyes, sets
    the nose pulsing, and the arms blinking::

        from gpiozero import SnowPi

        snowman = SnowPi(pwm=True)
        snowman.eyes.on()
        snowman.nose.pulse()
        snowman.arms.blink()

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.

    .. _Ryanteck SnowPi: https://ryanteck.uk/raspberry-pi/114-snowpi-the-gpio-snowman-for-raspberry-pi-0635648608303.html
    """
    def __init__(self, pwm=False):
        super(SnowPi, self).__init__(
            arms=LEDBoard(
                left=LEDBoard(
                    top=17, middle=18, bottom=22, pwm=pwm,
                    _order=('top', 'middle', 'bottom')),
                right=LEDBoard(
                    top=7, middle=8, bottom=9, pwm=pwm,
                    _order=('top', 'middle', 'bottom')),
                _order=('left', 'right')
                ),
            eyes=LEDBoard(
                left=23, right=24, pwm=pwm,
                _order=('left', 'right')
                ),
            nose=25, pwm=pwm,
            _order=('eyes', 'nose', 'arms')
            )


class TrafficLightsBuzzer(CompositeOutputDevice):
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
        super(TrafficLightsBuzzer, self).__init__(
            lights=lights, buzzer=buzzer, button=button,
            _order=('lights', 'buzzer', 'button'))


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
        super(Robot, self).__init__(
                left_motor=Motor(*left),
                right_motor=Motor(*right),
                _order=('left_motor', 'right_motor'))

    def forward(self, speed=1):
        """
        Drive the robot forward by running both motors forward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)

    def backward(self, speed=1):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.left_motor.backward(speed)
        self.right_motor.backward(speed)

    def left(self, speed=1):
        """
        Make the robot turn left by running the right motor forward and left
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.right_motor.forward(speed)
        self.left_motor.backward(speed)

    def right(self, speed=1):
        """
        Make the robot turn right by running the left motor forward and right
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.left_motor.forward(speed)
        self.right_motor.backward(speed)

    def reverse(self):
        """
        Reverse the robot's current motor directions. If the robot is currently
        running full speed forward, it will run full speed backward. If the
        robot is turning left at half-speed, it will turn right at half-speed.
        If the robot is currently stopped it will remain stopped.
        """
        self.left_motor.reverse()
        self.right_motor.reverse()

    def stop(self):
        """
        Stop the robot.
        """
        self.left_motor.stop()
        self.right_motor.stop()


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
        super(RyanteckRobot, self).__init__((17, 18), (22, 23))


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
        super(CamJamKitRobot, self).__init__((9, 10), (7, 8))


class _EnergenieMaster(SharedMixin, CompositeOutputDevice):
    def __init__(self):
        self._lock = Lock()
        super(_EnergenieMaster, self).__init__(
                *(OutputDevice(pin) for pin in (17, 22, 23, 27)),
                mode=OutputDevice(24), enable=OutputDevice(25),
                _order=('mode', 'enable'))

    def close(self):
        if self._lock:
            with self._lock:
                super(_EnergenieMaster, self).close()
            self._lock = None

    @classmethod
    def _shared_key(cls):
        # There's only one Energenie master
        return None

    def transmit(self, socket, enable):
        with self._lock:
            try:
                code = (8 * bool(enable)) + (8 - socket)
                for bit in self.all[:4]:
                    bit.value = (code & 1)
                    code >>= 1
                sleep(0.1)
                self.enable.on()
                sleep(0.25)
            finally:
                self.enable.off()


class Energenie(SourceMixin, Device):
    """
    Extends :class:`Device` to represent an `Energenie socket`_ controller.

    This class is constructed with a socket number and an optional initial
    state (defaults to ``False``, meaning off). Instances of this class can
    be used to switch peripherals on and off. For example::

        from gpiozero import Energenie

        lamp = Energenie(1)
        lamp.on()

    :param int socket:
        Which socket this instance should control. This is an integer number
        between 1 and 4.

    :param bool initial_value:
        The initial state of the socket. As Energenie sockets provide no
        means of reading their state, you must provide an initial state for
        the socket, which will be set upon construction. This defaults to
        ``False`` which will switch the socket off.

    .. _Energenie socket: https://energenie4u.co.uk/index.php/catalogue/product/ENER002-2PI
    """

    def __init__(self, socket=None, initial_value=False):
        if socket is None:
            raise EnergenieSocketMissing('socket number must be provided')
        if not (1 <= socket <= 4):
            raise EnergenieBadSocket('socket number must be between 1 and 4')
        super(Energenie, self).__init__()
        self._socket = socket
        self._master = _EnergenieMaster()
        if initial_value:
            self.on()
        else:
            self.off()

    def close(self):
        if self._master:
            m = self._master
            self._master = None
            m.close()

    @property
    def closed(self):
        return self._master is None

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.Energenie object on socket %d>" % self._socket
        except DeviceClosed:
            return "<gpiozero.Energenie object closed>"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._master.transmit(self._socket, bool(value))
        self._value = bool(value)

    def on(self):
        self.value = True

    def off(self):
        self.value = False

