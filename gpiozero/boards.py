# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2015-2024 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2022 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2015-2021 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2020 Ryan Walmsley <ryanteck@gmail.com>
# Copyright (c) 2020 Jack Wearden <jack@jackwearden.co.uk>
# Copyright (c) 2019 tuftii <3215045+tuftii@users.noreply.github.com>
# Copyright (c) 2019 ForToffee <ForToffee@users.noreply.github.com>
# Copyright (c) 2018 SteveAmor <steveamor@users.noreply.github.com>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
# Copyright (c) 2016 Ian Harcombe <ian.harcombe@gmail.com>
# Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import warnings
from time import sleep
from itertools import repeat, cycle, chain, tee
from threading import Lock
from collections import OrderedDict, Counter, namedtuple
from collections.abc import MutableMapping
from pprint import pformat

# Remove the try clause when 3.7 support is no longer trivial
try:
    import importlib_resources as resources
except ImportError:
    from importlib import resources

from .exc import (
    DeviceClosed,
    PinInvalidPin,
    GPIOPinMissing,
    EnergenieSocketMissing,
    EnergenieBadSocket,
    OutputDeviceBadValue,
    CompositeDeviceBadDevice,
    BadWaitTime,
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
    TonalBuzzer,
    )
from .threads import GPIOThread
from .devices import Device, CompositeDevice
from .mixins import SharedMixin, SourceMixin, HoldMixin, event
from .fonts import load_font_7seg, load_font_14seg


def pairwise(it):
    a, b = tee(it)
    next(b, None)
    return zip(a, b)


class CompositeOutputDevice(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` with :meth:`on`, :meth:`off`, and
    :meth:`toggle` methods for controlling subordinate output devices.  Also
    extends :attr:`value` to be writeable.

    :param Device \\*args:
        The un-named devices that belong to the composite device. The
        :attr:`~Device.value` attributes of these devices will be represented
        within the composite device's tuple :attr:`value` in the order
        specified here.

    :type _order: list or None
    :param _order:
        If specified, this is the order of named items specified by keyword
        arguments (to ensure that the :attr:`value` tuple is constructed with a
        specific order). All keyword arguments *must* be included in the
        collection. If omitted, an alphabetically sorted order will be selected
        for keyword arguments.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :param Device \\*\\*kwargs:
        The named devices that belong to the composite device. These devices
        will be accessible as named attributes on the resulting device, and
        their :attr:`value` attributes will be accessible as named elements of
        the composite device's tuple :attr:`value`.
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
        return super().value

    @value.setter
    def value(self, value):
        for device, v in zip(self, value):
            if isinstance(device, (OutputDevice, CompositeOutputDevice)):
                device.value = v
            # Simply ignore values for non-output devices


class ButtonBoard(HoldMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic button board or
    collection of buttons. The :attr:`value` of the button board is a tuple
    of all the buttons states. This can be used to control all the LEDs in a
    :class:`LEDBoard` with a :class:`ButtonBoard`::

        from gpiozero import LEDBoard, ButtonBoard
        from signal import pause

        leds = LEDBoard(2, 3, 4, 5)
        btns = ButtonBoard(6, 7, 8, 9)
        leds.source = btns

        pause()

    Alternatively you could represent the number of pressed buttons with an
    :class:`LEDBarGraph`::

        from gpiozero import LEDBarGraph, ButtonBoard
        from statistics import mean
        from signal import pause

        graph = LEDBarGraph(2, 3, 4, 5)
        bb = ButtonBoard(6, 7, 8, 9)
        graph.source = (mean(values) for values in bb.values)

        pause()

    :type pins: int or str
    :param \\*pins:
        Specify the GPIO pins that the buttons of the board are attached to.
        See :ref:`pin-numbering` for valid pin numbers. You can designate as
        many pins as necessary.

    :type pull_up: bool or None
    :param pull_up:
        If :data:`True` (the default), the GPIO pins will be pulled high by
        default.  In this case, connect the other side of the buttons to
        ground.  If :data:`False`, the GPIO pins will be pulled low by default.
        In this case, connect the other side of the buttons to 3V3. If
        :data:`None`, the pin will be floating, so it must be externally pulled
        up or down and the ``active_state`` parameter must be set accordingly.

    :type active_state: bool or None
    :param active_state:
        See description under :class:`InputDevice` for more information.

    :param float bounce_time:
        If :data:`None` (the default), no software bounce compensation will be
        performed. Otherwise, this is the length of time (in seconds) that the
        buttons will ignore changes in state after an initial change.

    :param float hold_time:
        The length of time (in seconds) to wait after any button is pushed,
        until executing the :attr:`when_held` handler. Defaults to ``1``.

    :param bool hold_repeat:
        If :data:`True`, the :attr:`when_held` handler will be repeatedly
        executed as long as any buttons remain held, every *hold_time* seconds.
        If :data:`False` (the default) the :attr:`when_held` handler will be
        only be executed once per hold.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :type named_pins: int or str
    :param \\*\\*named_pins:
        Specify GPIO pins that buttons of the board are attached to,
        associating each button with a property name. You can designate as
        many pins as necessary and use any names, provided they're not already
        in use by something else.
    """
    def __init__(self, *pins, pull_up=True, active_state=None,
                 bounce_time=None, hold_time=1, hold_repeat=False,
                 _order=None, pin_factory=None, **named_pins):
        super().__init__(
            *(
                Button(pin, pull_up=pull_up, active_state=active_state,
                       bounce_time=bounce_time, hold_time=hold_time,
                       hold_repeat=hold_repeat, pin_factory=pin_factory)
                for pin in pins
            ),
            _order=_order,
            pin_factory=pin_factory,
            **{
                name: Button(pin, pull_up=pull_up, active_state=active_state,
                             bounce_time=bounce_time, hold_time=hold_time,
                             hold_repeat=hold_repeat, pin_factory=pin_factory)
                for name, pin in named_pins.items()
            }
        )
        if len(self) == 0:
            raise GPIOPinMissing('No pins given')
        def get_new_handler(device):
            def fire_both_events(ticks, state):
                device._fire_events(ticks, device._state_to_value(state))
                self._fire_events(ticks, self.is_active)
            return fire_both_events
        # _handlers only exists to ensure that we keep a reference to the
        # generated fire_both_events handler for each Button (remember that
        # pin.when_changed only keeps a weak reference to handlers)
        self._handlers = tuple(get_new_handler(device) for device in self)
        for button, handler in zip(self, self._handlers):
            button.pin.when_changed = handler
        self._when_changed = None
        self._last_value = None
        # Call _fire_events once to set initial state of events
        self._fire_events(self.pin_factory.ticks(), self.is_active)
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat

    @property
    def pull_up(self):
        """
        If :data:`True`, the device uses a pull-up resistor to set the GPIO pin
        "high" by default.
        """
        return self[0].pull_up

    when_changed = event()

    def _fire_changed(self):
        if self.when_changed:
            self.when_changed()

    def _fire_events(self, ticks, new_value):
        super()._fire_events(ticks, new_value)
        old_value, self._last_value = self._last_value, new_value
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
    def __init__(self, *pins, pwm=False, active_high=True, initial_value=False,
                 _order=None, pin_factory=None, **named_pins):
        LEDClass = PWMLED if pwm else LED
        super().__init__(
            *(
                pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(
                    pin_or_collection, active_high=active_high,
                    initial_value=initial_value, pin_factory=pin_factory
                )
                for pin_or_collection in pins
            ),
            _order=_order,
            pin_factory=pin_factory,
            **{
                name: pin_or_collection
                if isinstance(pin_or_collection, LEDCollection) else
                LEDClass(
                    pin_or_collection, active_high=active_high,
                    initial_value=initial_value, pin_factory=pin_factory
                )
                for name, pin_or_collection in named_pins.items()
            }
        )
        if len(self) == 0:
            raise GPIOPinMissing('No pins given')
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


LEDCollection.is_lit = LEDCollection.is_active


class LEDBoard(LEDCollection):
    """
    Extends :class:`LEDCollection` and represents a generic LED board or
    collection of LEDs.

    The following example turns on all the LEDs on a board containing 5 LEDs
    attached to GPIO pins 2 through 6::

        from gpiozero import LEDBoard

        leds = LEDBoard(2, 3, 4, 5, 6)
        leds.on()

    :type pins: int or str or LEDCollection
    :param \\*pins:
        Specify the GPIO pins that the LEDs of the board are attached to. See
        :ref:`pin-numbering` for valid pin numbers. You can designate as many
        pins as necessary. You can also specify :class:`LEDBoard` instances to
        create trees of LEDs.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If :data:`False`, the :meth:`on` method will
        set all pins to LOW (the :meth:`off` method always does the opposite).

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type _order: list or None
    :param _order:
        If specified, this is the order of named items specified by keyword
        arguments (to ensure that the :attr:`value` tuple is constructed with a
        specific order). All keyword arguments *must* be included in the
        collection. If omitted, an alphabetically sorted order will be selected
        for keyword arguments.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    :type named_pins: int or str
    :param \\*\\*named_pins:
        Specify GPIO pins that LEDs of the board are attached to, associating
        each LED with a property name. You can designate as many pins as
        necessary and use any names, provided they're not already in use by
        something else. You can also specify :class:`LEDBoard` instances to
        create trees of LEDs.
    """
    def __init__(self, *pins, pwm=False, active_high=True, initial_value=False,
                 _order=None, pin_factory=None, **named_pins):
        self._blink_thread = None
        self._blink_leds = []
        self._blink_lock = Lock()
        super().__init__(*pins, pwm=pwm, active_high=active_high,
                         initial_value=initial_value, _order=_order,
                         pin_factory=pin_factory, **named_pins)

    def close(self):
        try:
            self._stop_blink()
        except AttributeError:
            pass
        super().close()

    def on(self, *args):
        """
        If no arguments are specified, turn all the LEDs on. If arguments are
        specified, they must be the indexes of the LEDs you wish to turn on.
        For example::

            from gpiozero import LEDBoard

            leds = LEDBoard(2, 3, 4, 5)
            leds.on(0)    # turn on the first LED (pin 2)
            leds.on(-1)   # turn on the last LED (pin 5)
            leds.on(1, 2) # turn on the middle LEDs (pins 3 and 4)
            leds.off()    # turn off all LEDs
            leds.on()     # turn on all LEDs

        If :meth:`blink` is currently active, it will be stopped first.

        :param int args:
            The index(es) of the LED(s) to turn on. If no indexes are specified
            turn on all LEDs.
        """
        self._stop_blink()
        if args:
            for index in args:
                self[index].on()
        else:
            super().on()

    def off(self, *args):
        """
        If no arguments are specified, turn all the LEDs off. If arguments are
        specified, they must be the indexes of the LEDs you wish to turn off.
        For example::

            from gpiozero import LEDBoard

            leds = LEDBoard(2, 3, 4, 5)
            leds.on()      # turn on all LEDs
            leds.off(0)    # turn off the first LED (pin 2)
            leds.off(-1)   # turn off the last LED (pin 5)
            leds.off(1, 2) # turn off the middle LEDs (pins 3 and 4)
            leds.on()      # turn on all LEDs

        If :meth:`blink` is currently active, it will be stopped first.

        :param int args:
            The index(es) of the LED(s) to turn off. If no indexes are
            specified turn off all LEDs.
        """
        self._stop_blink()
        if args:
            for index in args:
                self[index].off()
        else:
            super().off()

    def toggle(self, *args):
        """
        If no arguments are specified, toggle the state of all LEDs. If
        arguments are specified, they must be the indexes of the LEDs you wish
        to toggle. For example::

            from gpiozero import LEDBoard

            leds = LEDBoard(2, 3, 4, 5)
            leds.toggle(0)   # turn on the first LED (pin 2)
            leds.toggle(-1)  # turn on the last LED (pin 5)
            leds.toggle()    # turn the first and last LED off, and the
                             # middle pair on

        If :meth:`blink` is currently active, it will be stopped first.

        :param int args:
            The index(es) of the LED(s) to toggle. If no indexes are specified
            toggle the state of all LEDs.
        """
        self._stop_blink()
        if args:
            for index in args:
                self[index].toggle()
        else:
            super().toggle()

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
            ``pwm`` was :data:`False` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 0. Must be 0 if
            ``pwm`` was :data:`False` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True`, start a background thread to continue blinking and
            return immediately. If :data:`False`, only return when the blink is
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
            self._blink_device,
            (on_time, off_time, fade_in_time, fade_out_time, n))
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
        Make all LEDs fade in and out repeatedly. Note that this method will
        only work if the *pwm* parameter was :data:`True` at construction time.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.

        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        on_time = off_time = 0
        self.blink(
            on_time, off_time, fade_in_time, fade_out_time, n, background)

    def _blink_device(
            self, on_time, off_time, fade_in_time, fade_out_time, n, fps=25):
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
        if n is None:
            sequence = cycle(sequence)
        else:
            sequence = chain.from_iterable(repeat(sequence, n))
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

    As with all other output devices, :attr:`source` and :attr:`values` are
    supported::

        from gpiozero import LEDBarGraph, MCP3008
        from signal import pause

        graph = LEDBarGraph(2, 3, 4, 5, 6, pwm=True)
        pot = MCP3008(channel=0)

        graph.source = pot

        pause()

    :type pins: int or str
    :param \\*pins:
        Specify the GPIO pins that the LEDs of the bar graph are attached to.
        See :ref:`pin-numbering` for valid pin numbers. You can designate as
        many pins as necessary.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.
        This parameter can only be specified as a keyword parameter.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If :data:`False`, the :meth:`on` method will
        set all pins to LOW (the :meth:`off` method always does the opposite).
        This parameter can only be specified as a keyword parameter.

    :param float initial_value:
        The initial :attr:`value` of the graph given as a float between -1 and
        +1. Defaults to 0.0. This parameter can only be specified as a
        keyword parameter.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, *pins, pwm=False, active_high=True, initial_value=0.0,
                 pin_factory=None):
        # Don't allow graphs to contain collections
        for pin in pins:
            if isinstance(pin, Device):
                raise CompositeDeviceBadDevice(
                    'Only pins may be specified for LEDBarGraph')
        super().__init__(
            *pins, pwm=pwm, active_high=active_high, pin_factory=pin_factory)
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
            raise OutputDeviceBadValue(
                'LEDBarGraph value must be between -1 and 1')
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
        like :attr:`value`, this can be negative if the LEDs are lit from last
        to first.
        """
        lit_value = self.value * len(self)
        if not isinstance(self[0], PWMLED):
            lit_value = int(lit_value)
        return lit_value

    @lit_count.setter
    def lit_count(self, value):
        self.value = value / len(self)


class LEDCharFont(MutableMapping):
    """
    Contains a mapping of values to tuples of LED states.

    This effectively acts as a "font" for :class:`LEDCharDisplay`, and two
    default fonts (for 7-segment and 14-segment displays) are shipped with GPIO
    Zero by default. You can construct your own font instance from a
    :class:`dict` which maps values (usually single-character strings) to
    a tuple of LED states::

        from gpiozero import LEDCharDisplay, LEDCharFont

        my_font = LEDCharFont({
            ' ': (0, 0, 0, 0, 0, 0, 0),
            'D': (1, 1, 1, 1, 1, 1, 0),
            'A': (1, 1, 1, 0, 1, 1, 1),
            'd': (0, 1, 1, 1, 1, 0, 1),
            'a': (1, 1, 1, 1, 1, 0, 1),
        })
        display = LEDCharDisplay(26, 13, 12, 22, 17, 19, 6, dp=5, font=my_font)
        display.value = 'D'

    Font instances are mutable and can be changed while actively in use by
    an instance of :class:`LEDCharDisplay`. However, changing the font will
    *not* change the state of the LEDs in the display (though it may change
    the :attr:`~LEDCharDisplay.value` of the display when next queried).

    .. note::

        Your custom mapping should always include a value (typically space)
        which represents all the LEDs off. This will usually be the default
        value for an instance of :class:`LEDCharDisplay`.

    You may also wish to load fonts from a friendly text-based format. A simple
    parser for such formats (supporting an arbitrary number of segments) is
    provided by :func:`gpiozero.fonts.load_segment_font`.
    """
    def __init__(self, font):
        super().__init__()
        self._map = {
            char: tuple(int(bool(pin)) for pin in pins)
            for char, pins in font.items()
        }
        self._refresh_rmap()

    def __repr__(self):
        return f'{self.__class__.__name__}({pformat(self._map, indent=4)})'

    def _refresh_rmap(self):
        # The reverse mapping is pre-calculated for speed of lookup. Given that
        # the font mapping can be 1:n, we cannot guarantee the reverse is
        # unique. In case the provided font is an ordered dictionary, we
        # explicitly take only the first definition of each non-unique pin
        # definition so that value lookups are predictable
        rmap = {}
        for char, pins in self._map.items():
            rmap.setdefault(pins, char)
        self._rmap = rmap

    def __len__(self):
        return len(self._map)

    def __iter__(self):
        return iter(self._map)

    def __getitem__(self, char):
        return self._map[char]

    def __setitem__(self, char, pins):
        try:
            # This is necessary to ensure that _rmap is correct in the case
            # that we're overwriting an existing char->pins mapping
            del self[char]
        except KeyError:
            pass
        pins = tuple(int(bool(pin)) for pin in pins)
        self._map[char] = pins
        self._rmap.setdefault(pins, char)

    def __delitem__(self, char):
        pins = self._map[char]
        del self._map[char]
        # If the reverse mapping of the char's pins maps to the char we need
        # to find if it now maps to another char (given the n:1 mapping)
        if self._rmap[pins] == char:
            del self._rmap[pins]
            for char, char_pins in self._map.items():
                if pins == char_pins:
                    self._rmap[pins] = char
                    break


class LEDCharDisplay(LEDCollection):
    """
    Extends :class:`LEDCollection` for a multi-segment LED display.

    `Multi-segment LED displays`_ typically have 7 pins (labelled "a" through
    "g") representing 7 LEDs layed out in a figure-of-8 fashion. Frequently, an
    eigth pin labelled "dp" is included for a trailing decimal-point:

    .. code-block:: text

             a
           ━━━━━
        f ┃     ┃ b
          ┃  g  ┃
           ━━━━━
        e ┃     ┃ c
          ┃     ┃
           ━━━━━ • dp
             d

    Other common layouts are 9, 14, and 16 segment displays which include
    additional segments permitting more accurate renditions of alphanumerics.
    For example:

    .. code-block:: text

             a
           ━━━━━
        f ┃╲i┃j╱┃ b
          ┃ ╲┃╱k┃
          g━━ ━━h
        e ┃ ╱┃╲n┃ c
          ┃╱l┃m╲┃
           ━━━━━ • dp
             d

    Such displays have either a common anode, or common cathode pin. This class
    defaults to the latter; when using a common anode display *active_high*
    should be set to :data:`False`.

    Instances of this class can be used to display characters or control
    individual LEDs on the display. For example::

        from gpiozero import LEDCharDisplay

        char = LEDCharDisplay(4, 5, 6, 7, 8, 9, 10, active_high=False)
        char.value = 'C'

    If the class is constructed with 7 or 14 segments, a default :attr:`font`
    will be loaded, mapping some ASCII characters to typical layouts. In other
    cases, the default mapping will simply assign " " (space) to all LEDs off.
    You can assign your own mapping at construction time or after
    instantiation.

    While the example above shows the display with a :class:`str` value,
    theoretically the *font* can map any value that can be the key in a
    :class:`dict`, so the value of the display can be likewise be any valid
    key value (e.g. you could map integer digits to LED patterns). That said,
    there is one exception to this: when *dp* is specified to enable the
    decimal-point, the :attr:`value` must be a :class:`str` as the presence
    or absence of a "." suffix indicates whether the *dp* LED is lit.

    :type pins: int or str
    :param \\*pins:
        Specify the GPIO pins that the multi-segment display is attached to.
        Pins should be in the LED segment order A, B, C, D, E, F, G, and will
        be named automatically by the class. If a decimal-point pin is
        present, specify it separately as the *dp* parameter.

    :type dp: int or str
    :param dp:
        If a decimal-point segment is present, specify it as this named
        parameter.

    :type font: dict or None
    :param font:
        A mapping of values (typically characters, but may also be numbers) to
        tuples of LED states. A default mapping for ASCII characters is
        provided for 7 and 14 segment displays.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set all the
        associated pins to HIGH. If :data:`False`, the :meth:`on` method will
        set all pins to LOW (the :meth:`off` method always does the opposite).

    :param initial_value:
        The initial value to display. Defaults to space (" ") which typically
        maps to all LEDs being inactive. If :data:`None`, each device will be
        left in whatever state the pin is found in when configured for output
        (warning: this can be on).

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Multi-segment LED displays: https://en.wikipedia.org/wiki/Seven-segment_display
    """
    def __init__(self, *pins, dp=None, font=None, pwm=False, active_high=True,
                 initial_value=" ", pin_factory=None):
        if not 1 < len(pins) <= 26:
            raise PinInvalidPin(
                'Must have between 2 and 26 LEDs in LEDCharDisplay')
        for pin in pins:
            if isinstance(pin, LEDCollection):
                raise PinInvalidPin(
                    'Cannot use LEDCollection in LEDCharDisplay')

        if font is None:
            if len(pins) == 7:
                with resources.files('gpiozero.fonts').joinpath('7seg.txt').open() as f:
                    font = load_font_7seg(f)
            elif len(pins) == 14:
                with resources.files('gpiozero.fonts').joinpath('14seg.txt').open() as f:
                    font = load_font_14seg(f)
            else:
                # Construct a default dict containing a definition for " "
                font = {" ": (0,) * len(pins)}
        self._font = LEDCharFont(font)

        pins = {chr(ord('a') + i): pin for i, pin in enumerate(pins)}
        order = sorted(pins.keys())
        if dp is not None:
            pins['dp'] = dp
            order.append('dp')
        super().__init__(
            pwm=pwm, active_high=active_high, initial_value=None,
            _order=order, pin_factory=pin_factory, **pins)
        if initial_value is not None:
            self.value = initial_value

    @property
    def font(self):
        """
        An :class:`LEDCharFont` mapping characters to tuples of LED states.
        The font is mutable after construction. You can assign a tuple of LED
        states to a character to modify the font, delete an existing character
        in the font, or assign a mapping of characters to tuples to replace the
        entire font.

        Note that modifying the :attr:`font` never alters the underlying LED
        states. Only assignment to :attr:`value`, or calling the inherited
        :class:`LEDCollection` methods (:meth:`on`, :meth:`off`, etc.) modifies
        LED states. However, modifying the font may alter the character
        returned by querying :attr:`value`.
        """
        return self._font

    @font.setter
    def font(self, value):
        self._font = LEDCharFont(value)

    @property
    def value(self):
        """
        The character the display should show. This is mapped by the current
        :attr:`font` to a tuple of LED states which is applied to the
        underlying LED objects when this attribute is set.

        When queried, the current LED states are looked up in the font to
        determine the character shown. If the current LED states do not
        correspond to any character in the :attr:`font`, the value is
        :data:`None`.

        It is possible for multiple characters in the font to map to the same
        LED states (e.g. S and 5). In this case, if the font was constructed
        from an ordered mapping (which is the default), then the first matching
        mapping will always be returned. This also implies that the value
        queried need not match the value set.
        """
        state = super().value
        if hasattr(self, 'dp'):
            state, dp = state[:-1], state[-1]
        else:
            dp = False
        try:
            result = self._font._rmap[state]
        except KeyError:
            # Raising exceptions on lookup is problematic; in case the LED
            # state is not representable we simply return None (although
            # technically that is a valid item we can map :)
            return None
        else:
            if dp:
                return result + '.'
            else:
                return result

    @value.setter
    def value(self, value):
        for led, v in zip(self, self._parse_state(value)):
            led.value = v

    def _parse_state(self, value):
        if hasattr(self, 'dp'):
            if len(value) > 1 and value.endswith('.'):
                value = value[:-1]
                dp = 1
            else:
                dp = 0
            return self._font[value] + (dp,)
        else:
            return self._font[value]


class LEDMultiCharDisplay(CompositeOutputDevice):
    """
    Wraps :class:`LEDCharDisplay` for multi-character `multiplexed`_ LED
    character displays.

    The class is constructed with a *char* which is an instance of the
    :class:`LEDCharDisplay` class, capable of controlling the LEDs in one
    character of the display, and an additional set of *pins* that represent
    the common cathode (or anode) of each character.

    .. warning::

        You should not attempt to connect the common cathode (or anode) off
        each character directly to a GPIO. Rather, use a set of transistors (or
        some other suitable component capable of handling the current of all
        the segment LEDs simultaneously) to connect the common cathode to
        ground (or the common anode to the supply) and control those
        transistors from the GPIOs specified under *pins*.

    The *active_high* parameter defaults to :data:`True`. Note that it only
    applies to the specified *pins*, which are assumed to be controlling a set
    of transistors (hence the default). The specified *char* will use its own
    *active_high* parameter. Finally, *initial_value* defaults to a tuple of
    :attr:`~LEDCharDisplay.value` attribute of the specified display multiplied
    by the number of *pins* provided.

    When the :attr:`value` is set such that one or more characters in the
    display differ in value, a background thread is implicitly started to
    rotate the active character, relying on `persistence of vision`_ to display
    the complete value.

    .. _multiplexed: https://en.wikipedia.org/wiki/Multiplexed_display
    .. _persistence of vision: https://en.wikipedia.org/wiki/Persistence_of_vision
    """
    def __init__(self, char, *pins, active_high=True, initial_value=None,
                 pin_factory=None):
        if not isinstance(char, LEDCharDisplay):
            raise ValueError('char must be an LEDCharDisplay')
        if initial_value is None:
            initial_value = (char.value,) * len(pins)
        if pin_factory is None:
            pin_factory = char.pin_factory
        self._plex_thread = None
        self._plex_delay = 0.005
        plex = CompositeOutputDevice(*(
            OutputDevice(
                pin, active_high=active_high, initial_value=None,
                pin_factory=pin_factory)
            for pin in pins
        ))
        super().__init__(
            plex=plex, char=char, pin_factory=pin_factory)
        self.value = initial_value

    def close(self):
        try:
            self._stop_plex()
        except AttributeError:
            pass
        super().close()

    def _stop_plex(self):
        if self._plex_thread:
            self._plex_thread.stop()
        self._plex_thread = None

    @property
    def plex_delay(self):
        """
        The delay (measured in seconds) in the loop used to switch each
        character in the multiplexed display on. Defaults to 0.005 seconds
        which is generally sufficient to provide a "stable" (non-flickery)
        display.
        """
        return self._plex_delay

    @plex_delay.setter
    def plex_delay(self, value):
        if value < 0:
            raise BadWaitTime('plex_delay must be 0 or greater')
        self._plex_delay = float(value)

    @property
    def value(self):
        """
        The sequence of values to display.

        This can be any sequence containing keys from the
        :attr:`~LEDCharDisplay.font` of the associated character display. For
        example, if the value consists only of single-character strings, it's
        valid to assign a string to this property (as a string is simply a
        sequence of individual character keys)::

            from gpiozero import LEDCharDisplay, LEDMultiCharDisplay

            c = LEDCharDisplay(4, 5, 6, 7, 8, 9, 10)
            d = LEDMultiCharDisplay(c, 19, 20, 21, 22)
            d.value = 'LEDS'

        However, things get more complicated if a decimal point is in use as
        then this class needs to know explicitly where to break the value for
        use on each character of the display. This can be handled by simply
        assigning a sequence of strings thus::

            from gpiozero import LEDCharDisplay, LEDMultiCharDisplay

            c = LEDCharDisplay(4, 5, 6, 7, 8, 9, 10)
            d = LEDMultiCharDisplay(c, 19, 20, 21, 22)
            d.value = ('L.', 'E', 'D', 'S')

        This is how the value will always be represented when queried (as a
        tuple of individual values) as it neatly handles dealing with
        heterogeneous types and the aforementioned decimal point issue.

        .. note::

            The value also controls whether a background thread is in use to
            multiplex the display. When all positions in the value are equal
            the background thread is disabled and all characters are
            simultaneously enabled.
        """
        return self._value

    @value.setter
    def value(self, value):
        if len(value) > len(self.plex):
            raise ValueError(
                'length of value must not exceed the number of characters in '
                'the display')
        elif len(value) < len(self.plex):
            # Right-align the short value on the display
            value = (' ',) * (len(self.plex) - len(value)) + tuple(value)
        else:
            value = tuple(value)

        # Get the list of tuples of states that the character LEDs will pass
        # through. Prune any entirely blank state (which we can skip by never
        # activating the plex for them) but remember which plex index each
        # (non-blank) state is associated with
        states = {}
        for index, char in enumerate(value):
            state = self.char._parse_state(char)
            if any(state):
                states.setdefault(state, set()).add(index)
        # Calculate the transitions between states for an ordering of chars
        # based on activated LEDs. This a vague attempt at minimizing the
        # number of LEDs that need flipping between chars; to do this
        # "properly" is O(n!) which gets silly quickly so ... fudge it
        order = sorted(states)
        if len(order) > 1:
            transitions = [
                [(self.plex[index], 0) for index in states[old]] +
                [
                    (led, new_value)
                    for led, old_value, new_value in zip(self.char, old, new)
                    if old_value ^ new_value
                ] +
                [(self.plex[index], 1) for index in states[new]]
                for old, new in pairwise(order + [order[0]])
            ]
        else:
            transitions = []

        # Stop any current display thread and disable the display
        self._stop_plex()
        self.plex.off()

        # If there's any characters to display, set the character LEDs to the
        # state of the first character in the display order. If there's
        # transitions to display, activate the plex thread; otherwise, just
        # switch on each plex with a char to display
        if order:
            for led, state in zip(self.char, order[0]):
                led.value = state
            if transitions:
                self._plex_thread = GPIOThread(self._show_chars, (transitions,))
                self._plex_thread.start()
            else:
                for index in states[order[0]]:
                    self.plex[index].on()
        self._value = value

    def _show_chars(self, transitions):
        for transition in cycle(transitions):
            for device, value in transition:
                device.value = value
            if self._plex_thread.stopping.wait(self._plex_delay):
                break


class PiHutXmasTree(LEDBoard):
    """
    Extends :class:`LEDBoard` for `The Pi Hut's Xmas board`_: a 3D Christmas
    tree board with 24 red LEDs and a white LED as a star on top.

    The 24 red LEDs can be accessed through the attributes led0, led1, led2,
    and so on. The white star LED is accessed through the :attr:`star`
    attribute. Alternatively, as with all descendents of :class:`LEDBoard`,
    you can treat the instance as a sequence of LEDs (the first element is the
    :attr:`star`).

    The Xmas Tree board pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example turns all the LEDs
    on one at a time::

        from gpiozero import PiHutXmasTree
        from time import sleep

        tree = PiHutXmasTree()

        for light in tree:
            light.on()
            sleep(1)

    The following example turns the star LED on and sets all the red LEDs to
    flicker randomly::

        from gpiozero import PiHutXmasTree
        from gpiozero.tools import random_values
        from signal import pause

        tree = PiHutXmasTree(pwm=True)

        tree.star.on()

        for led in tree[1:]:
            led.source_delay = 0.1
            led.source = random_values()

        pause()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _The Pi Hut's Xmas board: https://thepihut.com/xmas

    .. attribute:: star

        Returns the :class:`LED` or :class:`PWMLED` representing the white
        star on top of the tree.

    .. attribute:: led0, led1, led2, ...

        Returns the :class:`LED` or :class:`PWMLED` representing one of the red
        LEDs. There are actually 24 of these properties named led0, led1, and
        so on but for the sake of brevity we represent all 24 under this
        section.
    """
    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        pins_dict = OrderedDict(star=2)
        pins = (4, 15, 13, 21, 25, 8, 5, 10, 16, 17, 27, 26,
                24, 9, 12, 6, 20, 19, 14, 18, 11, 7, 23, 22)
        for i, pin in enumerate(pins):
            pins_dict[f'led{i + 1:d}'] = pin
        super().__init__(
            pwm=pwm, initial_value=initial_value,
            _order=pins_dict.keys(),
            pin_factory=pin_factory,
            **pins_dict
        )


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

    :type initial_value: ~colorzero.Color or tuple
    :param initial_value:
        The initial color for the LedBorg. Defaults to black ``(0, 0, 0)``.

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMLED` instances for
        each component of the LedBorg. If :data:`False`, construct regular
        :class:`LED` instances, which prevents smooth color graduations.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _PiBorg LedBorg: https://www.piborg.org/ledborg
    """

    def __init__(self, *, initial_value=(0, 0, 0), pwm=True, pin_factory=None):
        super().__init__(
            red='BOARD11', green='BOARD13', blue='BOARD15',
            pwm=pwm, initial_value=initial_value, pin_factory=pin_factory
        )


class PiLiter(LEDBoard):
    """
    Extends :class:`LEDBoard` for the `Ciseco Pi-LITEr`_: a strip of 8 very
    bright LEDs.

    The Pi-LITEr pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example turns on all the LEDs
    of the Pi-LITEr::

        from gpiozero import PiLiter

        lite = PiLiter()
        lite.on()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each LED will be left in whatever state the pin is found
        in when configured for output (warning: this can be on). If
        :data:`True`, the each LED will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        pins = ('BOARD7', 'BOARD11', 'BOARD13', 'BOARD12',
                'BOARD15', 'BOARD16', 'BOARD18', 'BOARD22')
        super().__init__(
            *pins, pwm=pwm, initial_value=initial_value, pin_factory=pin_factory
        )


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
        If :data:`True`, construct :class:`PWMLED` instances for each pin. If
        :data:`False` (the default), construct regular :class:`LED` instances.

    :param float initial_value:
        The initial :attr:`value` of the graph given as a float between -1 and
        +1. Defaults to ``0.0``.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ciseco Pi-LITEr: http://shop.ciseco.co.uk/pi-liter-8-led-strip-for-the-raspberry-pi/
    """

    def __init__(self, *, pwm=False, initial_value=0.0, pin_factory=None):
        pins = ('BOARD7', 'BOARD11', 'BOARD13', 'BOARD12',
                'BOARD15', 'BOARD16', 'BOARD18', 'BOARD22')
        super().__init__(
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

    :type red: int or str
    :param red:
        The GPIO pin that the red LED is attached to. See :ref:`pin-numbering`
        for valid pin numbers.

    :type amber: int or str or None
    :param amber:
        The GPIO pin that the amber LED is attached to. See
        :ref:`pin-numbering` for valid pin numbers.

    :type yellow: int or str or None
    :param yellow:
        The GPIO pin that the yellow LED is attached to. This is merely an
        alias for the ``amber`` parameter; you can't specify both ``amber`` and
        ``yellow``. See :ref:`pin-numbering` for valid pin numbers.

    :type green: int or str
    :param green:
        The GPIO pin that the green LED is attached to. See
        :ref:`pin-numbering` for valid pin numbers.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. attribute:: red

        The red :class:`LED` or :class:`PWMLED`.

    .. attribute:: amber

        The amber :class:`LED` or :class:`PWMLED`. Note that this attribute
        will not be present when the instance is constructed with the
        *yellow* keyword parameter.

    .. attribute:: yellow

        The yellow :class:`LED` or :class:`PWMLED`. Note that this attribute
        will only be present when the instance is constructed with the
        *yellow* keyword parameter.

    .. attribute:: green

        The green :class:`LED` or :class:`PWMLED`.
    """
    def __init__(self, red=None, amber=None, green=None, *,
                 pwm=False, initial_value=False, yellow=None,
                 pin_factory=None):
        if amber is not None and yellow is not None:
            raise OutputDeviceBadValue(
                'Only one of amber or yellow can be specified')
        devices = OrderedDict((('red', red), ))
        self._display_yellow = amber is None and yellow is not None
        if self._display_yellow:
            devices['yellow'] = yellow
        else:
            devices['amber'] = amber
        devices['green'] = green
        if not all(p is not None for p in devices.values()):
            raise GPIOPinMissing(
                f'{", ".join(devices.keys())} pins must be provided')
        super().__init__(
            pwm=pwm, initial_value=initial_value,
            _order=devices.keys(), pin_factory=pin_factory,
            **devices)

    def __getattr__(self, name):
        if name == 'amber' and self._display_yellow:
            name = 'yellow'
        elif name == 'yellow' and not self._display_yellow:
            name = 'amber'
        return super().__getattr__(name)


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
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param bool initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Low Voltage Labs PI-TRAFFIC: http://lowvoltagelabs.com/products/pi-traffic/
    """
    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        super().__init__(
            'BOARD21', 'BOARD19', 'BOARD23',
            pwm=pwm, initial_value=initial_value, pin_factory=pin_factory
        )


class PiStop(TrafficLights):
    """
    Extends :class:`TrafficLights` for the `PiHardware Pi-Stop`_: a vertical
    traffic lights board.

    The following example turns on the amber LED on a Pi-Stop connected to
    location ``A+``::

        from gpiozero import PiStop

        traffic = PiStop('A+')
        traffic.amber.on()

    :param str location:
        The `location`_ on the GPIO header to which the Pi-Stop is connected.
        Must be one of: ``A``, ``A+``, ``B``, ``B+``, ``C``, ``D``.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param bool initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _PiHardware Pi-Stop: https://pihw.wordpress.com/meltwaters-pi-hardware-kits/pi-stop/
    .. _location: https://github.com/PiHw/Pi-Stop/blob/master/markdown_source/markdown/Discover-PiStop.md
    """
    LOCATIONS = {
        'A': ('BOARD26', 'BOARD24', 'BOARD22'),
        'A+': ('BOARD40', 'BOARD38', 'BOARD36'),
        'B': ('BOARD19', 'BOARD21', 'BOARD23'),
        'B+': ('BOARD33', 'BOARD35', 'BOARD37'),
        'C': ('BOARD12', 'BOARD10', 'BOARD8'),
        'D': ('BOARD3', 'BOARD5', 'BOARD7'),
    }

    def __init__(
            self, location=None, *, pwm=False, initial_value=False,
            pin_factory=None):
        gpios = self.LOCATIONS.get(location, None)
        if gpios is None:
            locations = ', '.join(sorted(self.LOCATIONS.keys()))
            raise ValueError(f'location must be one of: {locations}')
        super().__init__(
            *gpios, pwm=pwm, initial_value=initial_value,
            pin_factory=pin_factory)


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

    Each designated label will contain two :class:`LED` objects named "red"
    and "green".

    :param str \\*labels:
        Specify the names of the labels you wish to designate the strips to.
        You can list up to three labels. If no labels are given, three strips
        will be initialised with names 'one', 'two', and 'three'. If some, but
        not all strips are given labels, any remaining strips will not be
        initialised.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param bool initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _STATUS Zero: https://thepihut.com/statuszero

    .. attribute:: your-label-here, your-label-here, ...

        This entry represents one of the three labelled attributes supported on
        the STATUS Zero board. It is an :class:`LEDBoard` which contains:

        .. attribute:: red

            The :class:`LED` or :class:`PWMLED` representing the red LED
            next to the label.

        .. attribute:: green

            The :class:`LED` or :class:`PWMLED` representing the green LED
            next to the label.
    """
    default_labels = ('one', 'two', 'three')

    def __init__(self, *labels, pwm=False, initial_value=False,
                 pin_factory=None):
        pins = (
            ('BOARD11', 'BOARD7'),
            ('BOARD15', 'BOARD13'),
            ('BOARD21', 'BOARD19'),
        )
        if len(labels) == 0:
            labels = self.default_labels
        elif len(labels) > len(pins):
            raise ValueError(
                f"StatusZero doesn't support more than {len(pins)} labels")
        dup, count = Counter(labels).most_common(1)[0]
        if count > 1:
            raise ValueError(f"Duplicate label {dup}")
        super().__init__(
            _order=labels, pin_factory=pin_factory, **{
                label: LEDBoard(
                    red=red, green=green, _order=('red', 'green'),
                    pwm=pwm, initial_value=initial_value,
                    pin_factory=pin_factory)
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

    Each designated label will contain a "lights" :class:`LEDBoard` containing
    two :class:`LED` objects named "red" and "green", and a :class:`Button`
    object named "button".

    :param str \\*labels:
        Specify the names of the labels you wish to designate the strips to.
        You can list up to five labels. If no labels are given, five strips
        will be initialised with names 'one' to 'five'. If some, but not all
        strips are given labels, any remaining strips will not be initialised.

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param bool initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _STATUS: https://thepihut.com/status

    .. attribute:: your-label-here, your-label-here, ...

        This entry represents one of the five labelled attributes supported on
        the STATUS board. It is an :class:`CompositeOutputDevice` which
        contains:

        .. attribute:: lights

            A :class:`LEDBoard` representing the lights next to the label. It
            contains:

            .. attribute:: red

                The :class:`LED` or :class:`PWMLED` representing the red LED
                next to the label.

            .. attribute:: green

                The :class:`LED` or :class:`PWMLED` representing the green LED
                next to the label.

        .. attribute:: button

            A :class:`Button` representing the button next to the label.
    """
    default_labels = ('one', 'two', 'three', 'four', 'five')

    def __init__(self, *labels, pwm=False, initial_value=False,
                 pin_factory=None):
        pins = (
            ('BOARD11', 'BOARD7', 'BOARD8'),
            ('BOARD15', 'BOARD13', 'BOARD35'),
            ('BOARD21', 'BOARD19', 'BOARD10'),
            ('BOARD29', 'BOARD23', 'BOARD37'),
            ('BOARD33', 'BOARD31', 'BOARD12'),
        )
        if len(labels) == 0:
            labels = self.default_labels
        elif len(labels) > len(pins):
            raise ValueError("StatusBoard doesn't support more than five labels")
        dup, count = Counter(labels).most_common(1)[0]
        if count > 1:
            raise ValueError(f"Duplicate label {dup}")
        super().__init__(
            _order=labels, pin_factory=pin_factory, **{
                label: CompositeOutputDevice(
                    button=Button(button, pin_factory=pin_factory),
                    lights=LEDBoard(
                        red=red, green=green, _order=('red', 'green'),
                        pwm=pwm, initial_value=initial_value,
                        pin_factory=pin_factory),
                    _order=('button', 'lights'), pin_factory=pin_factory
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
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param bool initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ryanteck SnowPi: https://ryanteck.uk/raspberry-pi/114-snowpi-the-gpio-snowman-for-raspberry-pi-0635648608303.html

    .. attribute:: arms

        A :class:`LEDBoard` representing the arms of the snow man. It contains
        the following attributes:

        .. attribute:: left, right

            Two :class:`LEDBoard` objects representing the left and right arms
            of the snow-man. They contain:

            .. attribute:: top, middle, bottom

                The :class:`LED` or :class:`PWMLED` down the snow-man's arms.

    .. attribute:: eyes

        A :class:`LEDBoard` representing the eyes of the snow-man. It contains:

        .. attribute:: left, right

            The :class:`LED` or :class:`PWMLED` for the snow-man's eyes.

    .. attribute:: nose

        The :class:`LED` or :class:`PWMLED` for the snow-man's nose.
    """
    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        super().__init__(
            arms=LEDBoard(
                left=LEDBoard(
                    top='BOARD11', middle='BOARD12', bottom='BOARD15',
                    pwm=pwm, initial_value=initial_value,
                    _order=('top', 'middle', 'bottom'),
                    pin_factory=pin_factory),
                right=LEDBoard(
                    top='BOARD26', middle='BOARD24', bottom='BOARD21',
                    pwm=pwm, initial_value=initial_value,
                    _order=('top', 'middle', 'bottom'),
                    pin_factory=pin_factory),
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            eyes=LEDBoard(
                left='BOARD16', right='BOARD18',
                pwm=pwm, initial_value=initial_value,
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            nose='BOARD22',
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

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. attribute:: lights

        The :class:`TrafficLights` instance passed as the *lights* parameter.

    .. attribute:: buzzer

        The :class:`Buzzer` instance passed as the *buzzer* parameter.

    .. attribute:: button

        The :class:`Button` instance passed as the *button* parameter.
    """
    def __init__(self, lights, buzzer, button, *, pin_factory=None):
        super().__init__(
            lights=lights, buzzer=buzzer, button=button,
            _order=('lights', 'buzzer', 'button'),
            pin_factory=pin_factory
        )


class FishDish(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` for the `Pi Supply FishDish`_: traffic
    light LEDs, a button and a buzzer.

    The FishDish pins are fixed and therefore there's no need to specify them
    when constructing this class. The following example waits for the button
    to be pressed on the FishDish, then turns on all the LEDs::

        from gpiozero import FishDish

        fish = FishDish()
        fish.button.wait_for_press()
        fish.lights.on()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pi Supply FishDish: https://www.pi-supply.com/product/fish-dish-raspberry-pi-led-buzzer-board/
    """
    def __init__(self, *, pwm=False, pin_factory=None):
        super().__init__(
            lights=TrafficLights(
                'BOARD21', 'BOARD15', 'BOARD7', pwm=pwm, pin_factory=pin_factory
            ),
            buzzer=Buzzer('BOARD24', pin_factory=pin_factory),
            button=Button('BOARD26', pull_up=False, pin_factory=pin_factory),
            _order=('lights', 'buzzer', 'button'),
            pin_factory=pin_factory
        )


class TrafficHat(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` for the `Pi Supply Traffic HAT`_: a
    board with traffic light LEDs, a button and a buzzer.

    The Traffic HAT pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example waits for the
    button to be pressed on the Traffic HAT, then turns on all the LEDs::

        from gpiozero import TrafficHat

        hat = TrafficHat()
        hat.button.wait_for_press()
        hat.lights.on()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pi Supply Traffic HAT: https://uk.pi-supply.com/products/traffic-hat-for-raspberry-pi
    """
    def __init__(self, *, pwm=False, pin_factory=None):
        super().__init__(
            lights=TrafficLights(
                'BOARD18', 'BOARD16', 'BOARD15',
                pwm=pwm, pin_factory=pin_factory
            ),
            buzzer=Buzzer('BOARD29', pin_factory=pin_factory),
            button=Button('BOARD22', pin_factory=pin_factory),
            _order=('lights', 'buzzer', 'button'),
            pin_factory=pin_factory
        )


class TrafficpHat(TrafficLights):
    """
    Extends :class:`TrafficLights` for the `Pi Supply Traffic pHAT`_: a small
    board with traffic light LEDs.

    The Traffic pHAT pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example then turns on all
    the LEDs::

        from gpiozero import TrafficpHat
        phat = TrafficpHat()
        phat.red.on()
        phat.blink()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pi Supply Traffic pHAT: http://pisupp.ly/trafficphat
    """
    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        super().__init__(
            red='BOARD22', amber='BOARD18', green='BOARD16',
            pwm=pwm, initial_value=initial_value, pin_factory=pin_factory
        )


def PhaseEnableRobot(left=None, right=None, pwm=True, pin_factory=None, *args):
    """
    Deprecated alias of :class:`Robot`. The :class:`Robot` class can now be
    constructed directly with :class:`Motor` or :class:`PhaseEnableMotor`
    classes.
    """
    warnings.warn(
        DeprecationWarning(
            "PhaseEnableRobot is deprecated; please construct Robot directly "
            "with PhaseEnableMotor instances"))
    return Robot(
        PhaseEnableMotor(*left),
        PhaseEnableMotor(*right),
        pwm=pwm, pin_factory=pin_factory,
        *args)


class Robot(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` to represent a generic dual-motor robot.

    This class is constructed with two motor instances representing the left
    and right wheels of the robot respectively. For example, if the left
    motor's controller is connected to GPIOs 4 and 14, while the right motor's
    controller is connected to GPIOs 17 and 18 then the following example will
    drive the robot forward::

        from gpiozero import Robot

        robot = Robot(left=Motor(4, 14), right=Motor(17, 18))
        robot.forward()

    :type left: Motor or PhaseEnableMotor
    :param left:
        A :class:`~gpiozero.Motor` or a :class:`~gpiozero.PhaseEnableMotor`
        for the left wheel of the robot.

    :type right: Motor or PhaseEnableMotor
    :param right:
        A :class:`~gpiozero.Motor` or a :class:`~gpiozero.PhaseEnableMotor`
        for the right wheel of the robot.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. attribute:: left_motor

        The :class:`Motor` on the left of the robot.

    .. attribute:: right_motor

        The :class:`Motor` on the right of the robot.
    """
    def __init__(self, left, right, *, pin_factory=None):
        if not isinstance(left, (Motor, PhaseEnableMotor)):
            if isinstance(left, tuple):
                warnings.warn(
                    DeprecationWarning(
                        "Passing a tuple as the left parameter of the Robot "
                        "constructor is deprecated; please pass a Motor or "
                        "PhaseEnableMotor instance instead"))
                left = Motor(*left, pin_factory=pin_factory)
            else:
                raise GPIOPinMissing('left must be a Motor or PhaseEnableMotor')
        if not isinstance(right, (Motor, PhaseEnableMotor)):
            if isinstance(right, tuple):
                warnings.warn(
                    DeprecationWarning(
                        "Passing a tuple as the right parameter of the Robot "
                        "constructor is deprecated; please pass a Motor or "
                        "PhaseEnableMotor instance instead"))
                right = Motor(*right, pin_factory=pin_factory)
            else:
                raise GPIOPinMissing('right must be a Motor or PhaseEnableMotor')
        super().__init__(left_motor=left, right_motor=right,
                         _order=('left_motor', 'right_motor'),
                         pin_factory=pin_factory)

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return super().value

    @value.setter
    def value(self, value):
        self.left_motor.value, self.right_motor.value = value

    def forward(self, speed=1, *, curve_left=0, curve_right=0):
        """
        Drive the robot forward by running both motors forward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving forwards, by driving the
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving forwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
        """
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError("curve_left and curve_right can't be used at "
                             "the same time")
        self.left_motor.forward(speed * (1 - curve_left))
        self.right_motor.forward(speed * (1 - curve_right))

    def backward(self, speed=1, *, curve_left=0, curve_right=0):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving backwards, by driving the
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving backwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
        """
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError("curve_left and curve_right can't be used at "
                             "the same time")
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

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If :data:`False`, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Ryanteck motor controller board: https://uk.pi-supply.com/products/ryanteck-rtk-000-001-motor-controller-board-kit-raspberry-pi
    """

    def __init__(self, *, pwm=True, pin_factory=None):
        super().__init__(
            left=Motor('BOARD11', 'BOARD12', pwm=pwm, pin_factory=pin_factory),
            right=Motor('BOARD15', 'BOARD16', pwm=pwm, pin_factory=pin_factory),
            pin_factory=pin_factory)


class CamJamKitRobot(Robot):
    """
    Extends :class:`Robot` for the `CamJam #3 EduKit`_ motor controller board.

    The CamJam robot controller pins are fixed and therefore there's no need
    to specify them when constructing this class. The following example drives
    the robot forward::

        from gpiozero import CamJamKitRobot

        robot = CamJamKitRobot()
        robot.forward()

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If :data:`False`, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """
    def __init__(self, *, pwm=True, pin_factory=None):
        super().__init__(
            left=Motor('BOARD21', 'BOARD19', pwm=pwm, pin_factory=pin_factory),
            right=Motor('BOARD26', 'BOARD24', pwm=pwm, pin_factory=pin_factory),
            pin_factory=pin_factory)


class PololuDRV8835Robot(Robot):
    """
    Extends :class:`Robot` for the `Pololu DRV8835 Dual Motor Driver Kit`_.

    The Pololu DRV8835 pins are fixed and therefore there's no need to specify
    them when constructing this class. The following example drives the robot
    forward::

        from gpiozero import PololuDRV8835Robot

        robot = PololuDRV8835Robot()
        robot.forward()

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller's enable pins, allowing both
        direction and variable speed control. If :data:`False`, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pololu DRV8835 Dual Motor Driver Kit: https://www.pololu.com/product/2753
    """
    def __init__(self, *, pwm=True, pin_factory=None):
        super().__init__(
            left=PhaseEnableMotor('BOARD29', 'BOARD32', pwm=pwm, pin_factory=pin_factory),
            right=PhaseEnableMotor('BOARD31', 'BOARD33', pwm=pwm, pin_factory=pin_factory),
            pin_factory=pin_factory)


class _EnergenieMaster(SharedMixin, CompositeOutputDevice):
    def __init__(self, *, pin_factory=None):
        self._lock = Lock()
        super().__init__(
            *(
                OutputDevice(pin, pin_factory=pin_factory)
                for pin in ('BOARD11', 'BOARD15', 'BOARD16', 'BOARD13')
            ),
            mode=OutputDevice('BOARD18', pin_factory=pin_factory),
            enable=OutputDevice('BOARD22', pin_factory=pin_factory),
            _order=('mode', 'enable'), pin_factory=pin_factory
        )

    def close(self):
        if getattr(self, '_lock', None):
            with self._lock:
                super().close()
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
    state (defaults to :data:`False`, meaning off). Instances of this class can
    be used to switch peripherals on and off. For example::

        from gpiozero import Energenie

        lamp = Energenie(1)
        lamp.on()

    :param int socket:
        Which socket this instance should control. This is an integer number
        between 1 and 4.

    :type initial_value: bool or None
    :param initial_value:
        The initial state of the socket. As Energenie sockets provide no
        means of reading their state, you may provide an initial state for
        the socket, which will be set upon construction. This defaults to
        :data:`False` which will switch the socket off.
        Specifying :data:`None` will not set any initial state nor transmit any
        control signal to the device.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Energenie socket: https://energenie4u.co.uk/index.php/catalogue/product/ENER002-2PI
    """
    def __init__(self, socket=None, *, initial_value=False, pin_factory=None):
        if socket is None:
            raise EnergenieSocketMissing('socket number must be provided')
        if not (1 <= socket <= 4):
            raise EnergenieBadSocket('socket number must be between 1 and 4')
        self._value = None
        super().__init__(pin_factory=pin_factory)
        self._socket = socket
        self._master = _EnergenieMaster(pin_factory=pin_factory)
        if initial_value:
            self.on()
        elif initial_value is not None:
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
            return f"<gpiozero.Energenie object on socket {self._socket}>"
        except DeviceClosed:
            return "<gpiozero.Energenie object closed>"

    @property
    def socket(self):
        """
        Returns the socket number.
        """
        return self._socket

    @property
    def value(self):
        """
        Returns :data:`True` if the socket is on and :data:`False` if the
        socket is off.  Setting this property changes the state of the socket.
        Returns :data:`None` only when constructed with :data:`initial_value`
        set to :data:`None` and neither :data:`on()` nor :data:`off()` have
        been called since construction.
        """
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            raise TypeError('value cannot be None')
        value = bool(value)
        self._master.transmit(self._socket, value)
        self._value = value

    def on(self):
        """
        Turns the socket on.
        """
        self.value = True

    def off(self):
        """
        Turns the socket off.
        """
        self.value = False


class PumpkinPi(LEDBoard):
    """
    Extends :class:`LEDBoard` for the `ModMyPi PumpkinPi`_ board.

    There are twelve LEDs connected up to individual pins, so for the PumpkinPi
    the pins are fixed. For example::

        from gpiozero import PumpkinPi

        pumpkin = PumpkinPi(pwm=True)
        pumpkin.sides.pulse()
        pumpkin.off()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED. If :data:`False` (the default), construct regular :class:`LED`
        instances

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), all LEDs will be off initially. If
        :data:`None`, each device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _ModMyPi PumpkinPi: https://www.modmypi.com/halloween-pumpkin-programmable-kit

    .. attribute:: sides

        A :class:`LEDBoard` representing the LEDs around the edge of the
        pumpkin. It contains:

        .. attribute:: left, right

            Two :class:`LEDBoard` instances representing the LEDs on the left
            and right sides of the pumpkin. They each contain:

            .. attribute:: top, midtop, middle, midbottom, bottom

                Each :class:`LED` or :class:`PWMLED` around the specified side
                of the pumpkin.

    .. attribute:: eyes

        A :class:`LEDBoard` representing the eyes of the pumpkin. It contains:

        .. attribute:: left, right

            The :class:`LED` or :class:`PWMLED` for each of the pumpkin's eyes.
    """
    def __init__(self, *, pwm=False, initial_value=False, pin_factory=None):
        super().__init__(
            sides=LEDBoard(
                left=LEDBoard(
                    bottom='BOARD12', midbottom='BOARD11', middle='BOARD36',
                    midtop='BOARD33', top='BOARD18',
                    pwm=pwm, initial_value=initial_value,
                    _order=('bottom', 'midbottom', 'middle', 'midtop', 'top'),
                    pin_factory=pin_factory),
                right=LEDBoard(
                    bottom='BOARD35', midbottom='BOARD38', middle='BOARD40',
                    midtop='BOARD15', top='BOARD16',
                    pwm=pwm, initial_value=initial_value,
                    _order=('bottom', 'midbottom', 'middle', 'midtop', 'top'),
                    pin_factory=pin_factory),
                pwm=pwm, initial_value=initial_value,
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            eyes=LEDBoard(
                left='BOARD32', right='BOARD31',
                pwm=pwm, initial_value=initial_value,
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            pwm=pwm, initial_value=initial_value,
            _order=('eyes', 'sides'),
            pin_factory=pin_factory
        )


class JamHat(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` for the `ModMyPi JamHat`_ board.

    There are 6 LEDs, two buttons and a tonal buzzer. The pins are fixed.
    Usage::

        from gpiozero import JamHat

        hat = JamHat()

        hat.button_1.wait_for_press()
        hat.lights_1.on()
        hat.buzzer.play('C4')
        hat.button_2.wait_for_press()
        hat.off()

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED on the board. If :data:`False` (the default), construct regular
        :class:`LED` instances.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _ModMyPi JamHat: https://thepihut.com/products/jam-hat

    .. attribute:: lights_1, lights_2

        Two :class:`LEDBoard` instances representing the top (lights_1) and
        bottom (lights_2) rows of LEDs on the JamHat.

        .. attribute:: red, yellow, green

            :class:`LED` or :class:`PWMLED` instances representing the red,
            yellow, and green LEDs along the top row.

    .. attribute:: button_1, button_2

        The left (button_1) and right (button_2) :class:`Button` objects on the
        JamHat.

    .. attribute:: buzzer

        The :class:`TonalBuzzer` at the bottom right of the JamHat.
    """
    def __init__(self, *, pwm=False, pin_factory=None):
        super().__init__(
            lights_1=LEDBoard(
                red='BOARD29', yellow='BOARD32', green='BOARD36',
                pwm=pwm, _order=('red', 'yellow', 'green'),
                pin_factory=pin_factory
            ),
            lights_2=LEDBoard(
                red='BOARD31', yellow='BOARD33', green='BOARD11',
                pwm=pwm, _order=('red', 'yellow', 'green'),
                pin_factory=pin_factory),
            button_1=Button('BOARD35', pull_up=False, pin_factory=pin_factory),
            button_2=Button('BOARD12', pull_up=False, pin_factory=pin_factory),
            buzzer=TonalBuzzer('BOARD38', pin_factory=pin_factory),
            _order=('lights_1', 'lights_2', 'button_1', 'button_2', 'buzzer'),
            pin_factory=pin_factory
        )

    def on(self):
        """
        Turns all the LEDs on and makes the buzzer play its mid tone.
        """
        self.buzzer.value = 0
        super().on()

    def off(self):
        """
        Turns all the LEDs off and stops the buzzer.
        """
        self.buzzer.value = None
        super().off()


class Pibrella(CompositeOutputDevice):
    """
    Extends :class:`CompositeOutputDevice` for the Cyntech/Pimoroni `Pibrella`_
    board.

    The Pibrella board comprises 3 LEDs, a button, a tonal buzzer, four general
    purpose input channels, and four general purpose output channels (with LEDs).

    This class exposes the LEDs, button and buzzer.

    Usage::

        from gpiozero import Pibrella

        pb = Pibrella()

        pb.button.wait_for_press()
        pb.lights.on()
        pb.buzzer.play('A4')
        pb.off()

    The four input and output channels are exposed so you can create GPIO Zero
    devices using these pins without looking up their respective pin numbers::

        from gpiozero import Pibrella, LED, Button

        pb = Pibrella()
        btn = Button(pb.inputs.a, pull_up=False)
        led = LED(pb.outputs.e)

        btn.when_pressed = led.on

    :param bool pwm:
        If :data:`True`, construct :class:`PWMLED` instances to represent each
        LED on the board, otherwise if :data:`False` (the default), construct
        regular :class:`LED` instances.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Pibrella: http://www.pibrella.com/

    .. attribute:: lights

        :class:`TrafficLights` instance representing the three LEDs

        .. attribute:: red, amber, green

            :class:`LED` or :class:`PWMLED` instances representing the red,
            amber, and green LEDs

    .. attribute:: button

        The red :class:`Button` object on the Pibrella

    .. attribute:: buzzer

        A :class:`TonalBuzzer` object representing the buzzer

    .. attribute:: inputs

        A :func:`~collections.namedtuple` of the input pin numbers

        .. attribute:: a, b, c, d

    .. attribute:: outputs

        A :func:`~collections.namedtuple` of the output pin numbers

        .. attribute:: e, f, g, h
    """
    def __init__(self, *, pwm=False, pin_factory=None):
        super().__init__(
            lights=TrafficLights(
                red='BOARD13', amber='BOARD11', green='BOARD7',
                pwm=pwm, pin_factory=pin_factory
            ),
            button=Button('BOARD23', pull_up=False, pin_factory=pin_factory),
            buzzer=TonalBuzzer('BOARD12', pin_factory=pin_factory),
            _order=('lights', 'button', 'buzzer'),
            pin_factory=pin_factory
        )
        InputPins = namedtuple('InputPins', ['a', 'b', 'c', 'd'])
        OutputPins = namedtuple('OutputPins', ['e', 'f', 'g', 'h'])
        self.inputs = InputPins(
            a='BOARD21', b='BOARD26', c='BOARD24', d='BOARD19'
        )
        self.outputs = OutputPins(
            e='BOARD15', f='BOARD16', g='BOARD18', h='BOARD22'
        )

    def on(self):
        """
        Turns all the LEDs on and makes the buzzer play its mid tone.
        """
        self.buzzer.value = 0
        super().on()

    def off(self):
        """
        Turns all the LEDs off and stops the buzzer.
        """
        self.buzzer.value = None
        super().off()
