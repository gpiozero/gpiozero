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
from collections import OrderedDict, Counter

from .exc import (
    DeviceClosed,
    GPIOPinMissing,
    EnergenieSocketMissing,
    EnergenieBadSocket,
    OutputDeviceBadValue,
    )
from .input_devices import Button
from .output_devices import (
    OutputDevice,
    LED,
    PWMLED,
    RGBLED,
    Buzzer,
    Motor,
    PhaseEnableMotor,
    )
from .threads import GPIOThread
from .devices import Device, CompositeDevice
from .mixins import SharedMixin, SourceMixin, HoldMixin


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

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """

    def on(self):
        """
        Turn all the output devices on.
        """
        for device in self:
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.on()

    def off(self):
        """
        Turn all the output devices off.
        """
        for device in self:
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.off()

    def toggle(self):
        """
        Toggle all the output devices. For each device, if it's on, turn it
        off; if it's off, turn it on.
        """
        for device in self:
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
        for device, v in zip(self, value):
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.value = v
            # Simply ignore values for non-output devices


class ButtonBoard(HoldMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic button board or
    collection of buttons.

    :param int \*pins:
        Specify the GPIO pins that the buttons of the board are attached to.
        You can designate as many pins as necessary.

    :param bool pull_up:
        If ``True`` (the default), the GPIO pins will be pulled high by
        default. In this case, connect the other side of the buttons to
        ground. If ``False``, the GPIO pins will be pulled low by default. In
        this case, connect the other side of the buttons to 3V3. This
        parameter can only be specified as a keyword parameter.

    :param float bounce_time:
        If ``None`` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length of time (in seconds) that the
        buttons will ignore changes in state after an initial change. This
        parameter can only be specified as a keyword parameter.

    :param float hold_time:
        The length of time (in seconds) to wait after any button is pushed,
        until executing the :attr:`when_held` handler. Defaults to ``1``. This
        parameter can only be specified as a keyword parameter.

    :param bool hold_repeat:
        If ``True``, the :attr:`when_held` handler will be repeatedly executed
        as long as any buttons remain held, every *hold_time* seconds. If
        ``False`` (the default) the :attr:`when_held` handler will be only be
        executed once per hold. This parameter can only be specified as a
        keyword parameter.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :param \*\*named_pins:
        Specify GPIO pins that buttons of the board are attached to,
        associating each button with a property name. You can designate as
        many pins as necessary and use any names, provided they're not already
        in use by something else.
    """
    def __init__(self, *args, **kwargs):
        pull_up = kwargs.pop('pull_up', True)
        bounce_time = kwargs.pop('bounce_time', None)
        hold_time = kwargs.pop('hold_time', 1)
        hold_repeat = kwargs.pop('hold_repeat', False)
        pin_factory = kwargs.pop('pin_factory', None)
        order = kwargs.pop('_order', None)
        super(ButtonBoard, self).__init__(
            *(
                Button(pin, pull_up, bounce_time, hold_time, hold_repeat)
                for pin in args
                ),
            _order=order,
            pin_factory=pin_factory,
            **{
                name: Button(pin, pull_up, bounce_time, hold_time, hold_repeat)
                for name, pin in kwargs.items()
                })
        def get_new_handler(device):
            def fire_both_events():
                device._fire_events()
                self._fire_events()
            return fire_both_events
        for button in self:
            button.pin.when_changed = get_new_handler(button)
        self._when_changed = None
        self._last_value = None
        # Call _fire_events once to set initial state of events
        self._fire_events()
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat

    @property
    def pull_up(self):
        """
        If ``True``, the device uses a pull-up resistor to set the GPIO pin
        "high" by default.
        """
        return self[0].pull_up

    @property
    def when_changed(self):
        return self._when_changed

    @when_changed.setter
    def when_changed(self, value):
        self._when_changed = self._wrap_callback(value)

    def _fire_changed(self):
        if self.when_changed:
            self.when_changed()

    def _fire_events(self):
        super(ButtonBoard, self)._fire_events()
        old_value = self._last_value
        new_value = self._last_value = self.value
        if old_value is None:
            # Initial "indeterminate" value; don't do anything
            pass
        elif old_value != new_value:
            self._fire_changed()


ButtonBoard.is_pressed = ButtonBoard.is_active
ButtonBoard.pressed_time = ButtonBoard.active_time
ButtonBoard.when_pressed = ButtonBoard.when_activated
ButtonBoard.when_released = ButtonBoard.when_deactivated
ButtonBoard.wait_for_press = ButtonBoard.wait_for_active
ButtonBoard.wait_for_release = ButtonBoard.wait_for_inactive


class LEDCollection(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice`. Abstract base class for
    :class:`LEDBoard` and :class:`LEDBarGraph`.
    """
    def __init__(self, *args, **kwargs):
        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', False)
        pin_factory = kwargs.pop('pin_factory', None)
        order = kwargs.pop('_order', None)
        LEDClass = PWMLED if pwm else LED
        super(LEDCollection, self).__init__(
            *(
                pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(
                    pin_or_collection, active_high, initial_value,
                    pin_factory=pin_factory
                )
                for pin_or_collection in args
                ),
            _order=order,
            pin_factory=pin_factory,
            **{
                name: pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(
                    pin_or_collection, active_high, initial_value,
                    pin_factory=pin_factory
                )
                for name, pin_or_collection in kwargs.items()
                })
        leds = []
        for item in self:
            if isinstance(item, LEDCollection):
                for subitem in item.leds:
                    leds.append(subitem)
            else:
                leds.append(item)
        self._leds = tuple(leds)

    @property
    def leds(self):
        """
        A flat tuple of all LEDs contained in this collection (and all
        sub-collections).
        """
        return self._leds

    @property
    def active_high(self):
        return self[0].active_high


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
        associated pins to HIGH. If ``False``, the :meth:`on` method will set
        all pins to LOW (the :meth:`off` method always does the opposite). This
        parameter can only be specified as a keyword parameter.

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially. This parameter can only be
        specified as a keyword parameter.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :param \*\*named_pins:
        Specify GPIO pins that LEDs of the board are attached to, associating
        each LED with a property name. You can designate as many pins as
        necessary and use any names, provided they're not already in use by
        something else. You can also specify :class:`LEDBoard` instances to
        create trees of LEDs.
    """
    def __init__(self, *args, **kwargs):
        self._blink_thread = None
        self._blink_leds = []
        self._blink_lock = Lock()
        super(LEDBoard, self).__init__(*args, **kwargs)

    def close(self):
        try:
            self._stop_blink()
        except AttributeError:
            pass
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

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances. This
        parameter can only be specified as a keyword parameter.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If ``False``, the :meth:`on` method will set
        all pins to LOW (the :meth:`off` method always does the opposite). This
        parameter can only be specified as a keyword parameter.

    :param float initial_value:
        The initial :attr:`value` of the graph given as a float between -1 and
        +1.  Defaults to ``0.0``. This parameter can only be specified as a
        keyword parameter.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """

    def __init__(self, *pins, **kwargs):
        # Don't allow graphs to contain collections
        for pin in pins:
            assert not isinstance(pin, LEDCollection)
        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', 0.0)
        pin_factory = kwargs.pop('pin_factory', None)
        if kwargs:
            raise TypeError('unexpected keyword argument: %s' % kwargs.popitem()[0])
        super(LEDBarGraph, self).__init__(
            *pins, pwm=pwm, active_high=active_high, pin_factory=pin_factory
        )
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
        if not -1 <= value <= 1:
            raise OutputDeviceBadValue('LEDBarGraph value must be between -1 and 1')
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

    @property
    def lit_count(self):
        """
        The number of LEDs on the bar graph actually lit up. Note that just
        like ``value``, this can be negative if the LEDs are lit from last to
        first.
        """
        lit_value = self.value * len(self)
        if not isinstance(self[0], PWMLED):
            lit_value = int(lit_value)
        return lit_value

    @lit_count.setter
    def lit_count(self, value):
        self.value = value / len(self)


class LedBorg(RGBLED):
    """
    Extends :class:`RGBLED` for the `PiBorg LedBorg`_: an add-on board
    containing a very bright RGB LED.

    The LedBorg pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example turns the LedBorg
    purple::

        from gpiozero import LedBorg

        led = LedBorg()
        led.color = (1, 0, 1)

    :param tuple initial_value:
        The initial color for the LedBorg. Defaults to black ``(0, 0, 0)``.

    :param bool pwm:
        If ``True`` (the default), construct :class:`PWMLED` instances for
        each component of the LedBorg. If ``False``, construct regular
        :class:`LED` instances, which prevents smooth color graduations.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _PiBorg LedBorg: https://www.piborg.org/ledborg
    """

    def __init__(self, initial_value=(0, 0, 0), pwm=True, pin_factory=None):
        super(LedBorg, self).__init__(red=17, green=27, blue=22,
                                      pwm=pwm, initial_value=initial_value,
                                      pin_factory=pin_factory)


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
        ``False`` (the default), construct regular :class:`LED` instances.

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(PiLiter, self).__init__(4, 17, 27, 18, 22, 23, 24, 25,
                                      pwm=pwm, initial_value=initial_value,
                                      pin_factory=pin_factory)


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

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances for each pin. If
        ``False`` (the default), construct regular :class:`LED` instances.

    :param float initial_value:
        The initial :attr:`value` of the graph given as a float between -1 and
        +1. Defaults to ``0.0``.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, pwm=False, initial_value=0.0, pin_factory=None):
        pins = (4, 17, 27, 18, 22, 23, 24, 25)
        super(PiLiterBarGraph, self).__init__(
            *pins, pwm=pwm, initial_value=initial_value, pin_factory=pin_factory
        )


class TrafficLights(LEDBoard):
    """
    Extends :class:`LEDBoard` for devices containing red, yellow, and green
    LEDs.

    The following example initializes a device connected to GPIO pins 2, 3,
    and 4, then lights the amber (yellow) LED attached to GPIO 3::

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

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param int yellow:
        The GPIO pin that the yellow LED is attached to. This is merely an
        alias for the ``amber`` parameter - you can't specify both ``amber``
        and ``yellow``.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, red=None, amber=None, green=None,
                 pwm=False, initial_value=False, yellow=None,
                 pin_factory=None):
        if amber is not None and yellow is not None:
            raise OutputDeviceBadValue(
                'Only one of amber or yellow can be specified'
            )
        devices = OrderedDict((('red', red), ))
        self._display_yellow = amber is None and yellow is not None
        if self._display_yellow:
            devices['yellow'] = yellow
        else:
            devices['amber'] = amber
        devices['green'] = green
        if not all(p is not None for p in devices.values()):
            raise GPIOPinMissing(
                ', '.join(devices.keys())+' pins must be provided'
            )
        super(TrafficLights, self).__init__(
            pwm=pwm, initial_value=initial_value,
            _order=devices.keys(), pin_factory=pin_factory,
            **devices)

    def __getattr__(self, name):
        if name == 'amber' and self._display_yellow:
            name = 'yellow'
        elif name == 'yellow' and not self._display_yellow:
            name = 'amber'
        return super(TrafficLights, self).__getattr__(name)


class PiTraffic(TrafficLights):
    """
    Extends :class:`TrafficLights` for the `Low Voltage Labs PI-TRAFFIC`_
    vertical traffic lights board when attached to GPIO pins 9, 10, and 11.

    There's no need to specify the pins if the PI-TRAFFIC is connected to the
    default pins (9, 10, 11). The following example turns on the amber LED on
    the PI-TRAFFIC::

        from gpiozero import PiTraffic

        traffic = PiTraffic()
        traffic.amber.on()

    To use the PI-TRAFFIC board when attached to a non-standard set of pins,
    simply use the parent class, :class:`TrafficLights`.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Low Voltage Labs PI-TRAFFIC: http://lowvoltagelabs.com/products/pi-traffic/
    """
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(PiTraffic, self).__init__(9, 10, 11,
                                        pwm=pwm, initial_value=initial_value,
                                        pin_factory=pin_factory)


class PiStop(TrafficLights):
    """
    Extends :class:`TrafficLights` for the `PiHardware Pi-Stop`_: a vertical
    traffic lights board.

    The following example turns on the amber LED on a Pi-Stop
    connected to location ``A+``::

        from gpiozero import PiStop

        traffic = PiStop('A+')
        traffic.amber.on()

    :param str location:
        The `location`_ on the GPIO header to which the Pi-Stop is connected.
        Must be one of: ``A``, ``A+``, ``B``, ``B+``, ``C``, ``D``.

    :param bool pwm:
        If ``True``, construct :class:`PWMLED` instances to represent each
        LED. If ``False`` (the default), construct regular :class:`LED`
        instances.

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _PiHardware Pi-Stop: https://pihw.wordpress.com/meltwaters-pi-hardware-kits/pi-stop/
    .. _location: https://github.com/PiHw/Pi-Stop/blob/master/markdown_source/markdown/Discover-PiStop.md
    """
    LOCATIONS = {
        'A': (7, 8, 25),
        'A+': (21, 20, 16),
        'B': (10, 9, 11),
        'B+': (13, 19, 26),
        'C': (18, 15, 14),
        'D': (2, 3, 4),
    }

    def __init__(
            self, location=None, pwm=False, initial_value=False,
            pin_factory=None):
        gpios = self.LOCATIONS.get(location, None)
        if gpios is None:
            raise ValueError('location must be one of: %s' %
                             ', '.join(sorted(self.LOCATIONS.keys())))
        super(PiStop, self).__init__(
            *gpios, pwm=pwm, initial_value=initial_value,
            pin_factory=pin_factory
        )


class StatusZero(LEDBoard):
    """
    Extends :class:`LEDBoard` for The Pi Hut's `STATUS Zero`_: a Pi Zero sized
    add-on board with three sets of red/green LEDs to provide a status
    indicator.

    The following example designates the first strip the label "wifi" and the
    second "raining", and turns them green and red respectfully::

        from gpiozero import StatusZero

        status = StatusZero('wifi', 'raining')
        status.wifi.green.on()
        status.raining.red.on()

    :param str \*labels:
        Specify the names of the labels you wish to designate the strips to.
        You can list up to three labels. If no labels are given, three strips
        will be initialised with names 'one', 'two', and 'three'. If some, but
        not all strips are given labels, any remaining strips will not be
        initialised.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _STATUS Zero: https://thepihut.com/statuszero
    """
    default_labels = ('one', 'two', 'three')

    def __init__(self, *labels, **kwargs):
        pins = (
            (17, 4),
            (22, 27),
            (9, 10),
        )
        pin_factory = kwargs.pop('pin_factory', None)
        if len(labels) == 0:
            labels = self.default_labels
        elif len(labels) > len(pins):
            raise ValueError("StatusZero doesn't support more than three labels")
        dup, count = Counter(labels).most_common(1)[0]
        if count > 1:
            raise ValueError("Duplicate label %s" % dup)
        super(StatusZero, self).__init__(
            _order=labels, pin_factory=pin_factory, **{
                label: LEDBoard(
                    red=red, green=green, _order=('red', 'green'),
                    pin_factory=pin_factory, **kwargs
                )
                for (green, red), label in zip(pins, labels)
            }
        )


class StatusBoard(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` for The Pi Hut's `STATUS`_ board: a
    HAT sized add-on board with five sets of red/green LEDs and buttons to
    provide a status indicator with additional input.

    The following example designates the first strip the label "wifi" and the
    second "raining", turns the wifi green and then activates the button to
    toggle its lights when pressed::

        from gpiozero import StatusBoard

        status = StatusBoard('wifi', 'raining')
        status.wifi.lights.green.on()
        status.wifi.button.when_pressed = status.wifi.lights.toggle

    :param str \*labels:
        Specify the names of the labels you wish to designate the strips to.
        You can list up to five labels. If no labels are given, five strips
        will be initialised with names 'one' to 'five'. If some, but not all
        strips are given labels, any remaining strips will not be initialised.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _STATUS: https://thepihut.com/status
    """
    default_labels = ('one', 'two', 'three', 'four', 'five')

    def __init__(self, *labels, **kwargs):
        pins = (
            (17, 4, 14),
            (22, 27, 19),
            (9, 10, 15),
            (5, 11, 26),
            (13, 6, 18),
        )
        pin_factory = kwargs.pop('pin_factory', None)
        if len(labels) == 0:
            labels = self.default_labels
        elif len(labels) > len(pins):
            raise ValueError("StatusBoard doesn't support more than five labels")
        dup, count = Counter(labels).most_common(1)[0]
        if count > 1:
            raise ValueError("Duplicate label %s" % dup)
        super(StatusBoard, self).__init__(
            _order=labels, pin_factory=pin_factory, **{
                label: CompositeOutputDevice(
                    button=Button(button, pin_factory=pin_factory),
                    lights=LEDBoard(
                        red=red, green=green, _order=('red', 'green'),
                        pin_factory=pin_factory, **kwargs
                    ), _order=('button', 'lights'), pin_factory=pin_factory
                )
                for (green, red, button), label in zip(pins, labels)
            }
        )


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

    :param bool initial_value:
        If ``False`` (the default), all LEDs will be off initially. If
        ``None``, each device will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If ``True``,
        the device will be switched on initially.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ryanteck SnowPi: https://ryanteck.uk/raspberry-pi/114-snowpi-the-gpio-snowman-for-raspberry-pi-0635648608303.html
    """
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(SnowPi, self).__init__(
            arms=LEDBoard(
                left=LEDBoard(
                    top=17, middle=18, bottom=22,
                    pwm=pwm, initial_value=initial_value,
                    _order=('top', 'middle', 'bottom'),
                    pin_factory=pin_factory),
                right=LEDBoard(
                    top=7, middle=8, bottom=9,
                    pwm=pwm, initial_value=initial_value,
                    _order=('top', 'middle', 'bottom'),
                    pin_factory=pin_factory),
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            eyes=LEDBoard(
                left=23, right=24,
                pwm=pwm, initial_value=initial_value,
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            nose=25,
            pwm=pwm, initial_value=initial_value,
            _order=('eyes', 'nose', 'arms'),
            pin_factory=pin_factory
        )


class TrafficLightsBuzzer(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` and is a generic class for HATs with
    traffic lights, a button and a buzzer.

    :param TrafficLights lights:
        An instance of :class:`TrafficLights` representing the traffic lights
        of the HAT.

    :param Buzzer buzzer:
        An instance of :class:`Buzzer` representing the buzzer on the HAT.

    :param Button button:
        An instance of :class:`Button` representing the button on the HAT.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """

    def __init__(self, lights, buzzer, button, pin_factory=None):
        super(TrafficLightsBuzzer, self).__init__(
            lights=lights, buzzer=buzzer, button=button,
            _order=('lights', 'buzzer', 'button'),
            pin_factory=pin_factory
        )


class FishDish(TrafficLightsBuzzer):
    """
    Extends :class:`TrafficLightsBuzzer` for the `Pi Supply FishDish`_: traffic
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

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pi Supply FishDish: https://www.pi-supply.com/product/fish-dish-raspberry-pi-led-buzzer-board/
    """

    def __init__(self, pwm=False, pin_factory=None):
        super(FishDish, self).__init__(
            TrafficLights(9, 22, 4, pwm=pwm, pin_factory=pin_factory),
            Buzzer(8, pin_factory=pin_factory),
            Button(7, pull_up=False, pin_factory=pin_factory),
            pin_factory=pin_factory
        )


class TrafficHat(TrafficLightsBuzzer):
    """
    Extends :class:`TrafficLightsBuzzer` for the `Ryanteck Traffic HAT`_: traffic
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

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ryanteck Traffic HAT: https://ryanteck.uk/hats/1-traffichat-0635648607122.html
    """

    def __init__(self, pwm=False, pin_factory=None):
        super(TrafficHat, self).__init__(
            TrafficLights(24, 23, 22, pwm=pwm, pin_factory=pin_factory),
            Buzzer(5, pin_factory=pin_factory),
            Button(25, pin_factory=pin_factory),
            pin_factory=pin_factory
        )


class Robot(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` to represent a generic dual-motor robot.

    This class is constructed with two tuples representing the forward and
    backward pins of the left and right controllers respectively. For example,
    if the left motor's controller is connected to GPIOs 4 and 14, while the
    right motor's controller is connected to GPIOs 17 and 18 then the following
    example will drive the robot forward::

        from gpiozero import Robot

        robot = Robot(left=(4, 14), right=(17, 18))
        robot.forward()

    :param tuple left:
        A tuple of two GPIO pins representing the forward and backward inputs
        of the left motor's controller.

    :param tuple right:
        A tuple of two GPIO pins representing the forward and backward inputs
        of the right motor's controller.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """

    def __init__(self, left=None, right=None, pin_factory=None):
        super(Robot, self).__init__(
            left_motor=Motor(*left, pin_factory=pin_factory),
            right_motor=Motor(*right, pin_factory=pin_factory),
            _order=('left_motor', 'right_motor'),
            pin_factory=pin_factory
        )

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return super(Robot, self).value

    @value.setter
    def value(self, value):
        self.left_motor.value, self.right_motor.value = value

    def forward(self, speed=1, **kwargs):
        """
        Drive the robot forward by running both motors forward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving forwards, by driving the
            left motor at a slower speed. Maximum ``curve_left`` is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with ``curve_right``.

        :param float curve_right:
            The amount to curve right while moving forwards, by driving the
            right motor at a slower speed. Maximum ``curve_right`` is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with ``curve_left``.
        """
        curve_left = kwargs.pop('curve_left', 0)
        curve_right = kwargs.pop('curve_right', 0)
        if kwargs:
            raise TypeError('unexpected argument %s' % kwargs.popitem()[0])
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError('curve_left and curve_right can\'t be used at the same time')
        self.left_motor.forward(speed * (1 - curve_left))
        self.right_motor.forward(speed * (1 - curve_right))

    def backward(self, speed=1, **kwargs):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving backwards, by driving the
            left motor at a slower speed. Maximum ``curve_left`` is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with ``curve_right``.

        :param float curve_right:
            The amount to curve right while moving backwards, by driving the
            right motor at a slower speed. Maximum ``curve_right`` is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with ``curve_left``.
        """
        curve_left = kwargs.pop('curve_left', 0)
        curve_right = kwargs.pop('curve_right', 0)
        if kwargs:
            raise TypeError('unexpected argument %s' % kwargs.popitem()[0])
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError('curve_left and curve_right can\'t be used at the same time')
        self.left_motor.backward(speed * (1 - curve_left))
        self.right_motor.backward(speed * (1 - curve_right))

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
    Extends :class:`Robot` for the `Ryanteck motor controller board`_.

    The Ryanteck MCB pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example drives the robot
    forward::

        from gpiozero import RyanteckRobot

        robot = RyanteckRobot()
        robot.forward()

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ryanteck motor controller board: https://ryanteck.uk/add-ons/6-ryanteck-rpi-motor-controller-board-0635648607160.html
    """

    def __init__(self, pin_factory=None):
        super(RyanteckRobot, self).__init__(
            (17, 18), (22, 23), pin_factory=pin_factory
        )


class CamJamKitRobot(Robot):
    """
    Extends :class:`Robot` for the `CamJam #3 EduKit`_ motor controller board.

    The CamJam robot controller pins are fixed and therefore there's no need
    to specify them when constructing this class. The following example drives
    the robot forward::

        from gpiozero import CamJamKitRobot

        robot = CamJamKitRobot()
        robot.forward()

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """

    def __init__(self, pin_factory=None):
        super(CamJamKitRobot, self).__init__(
            (9, 10), (7, 8), pin_factory=pin_factory
        )


class PhaseEnableRobot(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` to represent a dual-motor robot based
    around a Phase/Enable motor board.

    This class is constructed with two tuples representing the phase
    (direction) and enable (speed) pins of the left and right controllers
    respectively. For example, if the left motor's controller is connected to
    GPIOs 12 and 5, while the right motor's controller is connected to GPIOs 13
    and 6 so the following example will drive the robot forward::

        from gpiozero import PhaseEnableRobot

        robot = PhaseEnableRobot(left=(5, 12), right=(6, 13))
        robot.forward()

    :param tuple left:
        A tuple of two GPIO pins representing the phase and enable inputs
        of the left motor's controller.

    :param tuple right:
        A tuple of two GPIO pins representing the phase and enable inputs
        of the right motor's controller.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """

    def __init__(self, left=None, right=None, pin_factory=None):
        super(PhaseEnableRobot, self).__init__(
            left_motor=PhaseEnableMotor(*left, pin_factory=pin_factory),
            right_motor=PhaseEnableMotor(*right, pin_factory=pin_factory),
            _order=('left_motor', 'right_motor'),
            pin_factory=pin_factory
        )

    @property
    def value(self):
        """
        Returns a tuple of two floating point values (-1 to 1) representing the
        speeds of the robot's two motors (left and right). This property can
        also be set to alter the speed of both motors.
        """
        return super(PhaseEnableRobot, self).value

    @value.setter
    def value(self, value):
        self.left_motor.value, self.right_motor.value = value

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
        self.left_motor.value = -self.left_motor.value
        self.right_motor.value = -self.right_motor.value

    def stop(self):
        """
        Stop the robot.
        """
        self.left_motor.stop()
        self.right_motor.stop()


class PololuDRV8835Robot(PhaseEnableRobot):
    """
    Extends :class:`PhaseEnableRobot` for the `Pololu DRV8835 Dual Motor Driver
    Kit`_.

    The Pololu DRV8835 pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example drives the robot
    forward::

        from gpiozero import PololuDRV8835Robot

        robot = PololuDRV8835Robot()
        robot.forward()

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pololu DRV8835 Dual Motor Driver Kit: https://www.pololu.com/product/2753
    """

    def __init__(self, pin_factory=None):
        super(PololuDRV8835Robot, self).__init__(
            (5, 12), (6, 13), pin_factory=pin_factory
        )


class _EnergenieMaster(SharedMixin, CompositeOutputDevice):
    def __init__(self, pin_factory=None):
        self._lock = Lock()
        super(_EnergenieMaster, self).__init__(
            *(
                OutputDevice(pin, pin_factory=pin_factory)
                for pin in (17, 22, 23, 27)
            ),
            mode=OutputDevice(24, pin_factory=pin_factory),
            enable=OutputDevice(25, pin_factory=pin_factory),
            _order=('mode', 'enable'), pin_factory=pin_factory
        )

    def close(self):
        if getattr(self, '_lock', None):
            with self._lock:
                super(_EnergenieMaster, self).close()
        self._lock = None

    @classmethod
    def _shared_key(cls, pin_factory):
        # There's only one Energenie master
        return None

    def transmit(self, socket, enable):
        with self._lock:
            try:
                code = (8 * bool(enable)) + (8 - socket)
                for bit in self[:4]:
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

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Energenie socket: https://energenie4u.co.uk/index.php/catalogue/product/ENER002-2PI
    """

    def __init__(self, socket=None, initial_value=False, pin_factory=None):
        if socket is None:
            raise EnergenieSocketMissing('socket number must be provided')
        if not (1 <= socket <= 4):
            raise EnergenieBadSocket('socket number must be between 1 and 4')
        self._value = None
        super(Energenie, self).__init__(pin_factory=pin_factory)
        self._socket = socket
        self._master = _EnergenieMaster(pin_factory=pin_factory)
        if initial_value:
            self.on()
        else:
            self.off()

    def close(self):
        if getattr(self, '_master', None):
            self._master.close()
        self._master = None

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
        value = bool(value)
        self._master.transmit(self._socket, value)
        self._value = value

    def on(self):
        self.value = True

    def off(self):
        self.value = False
