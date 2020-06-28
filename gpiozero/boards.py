# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2015-2020 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2020 Ryan Walmsley <ryanteck@gmail.com>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 tuftii <3215045+tuftii@users.noreply.github.com>
# Copyright (c) 2019 ForToffee <ForToffee@users.noreply.github.com>
# Copyright (c) 2018 SteveAmor <steveamor@users.noreply.github.com>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
# Copyright (c) 2016 Ian Harcombe <ian.harcombe@gmail.com>
# Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
from collections import OrderedDict, Counter, namedtuple

from .exc import (
    DeviceClosed,
    GPIOPinMissing,
    EnergenieSocketMissing,
    EnergenieBadSocket,
    EnergenieBadInitialValue,
    OutputDeviceBadValue,
    CompositeDeviceBadDevice,
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
from .mixins import SharedMixin, SourceMixin, HoldMixin


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
    def __init__(self, *args, **kwargs):
        pull_up = kwargs.pop('pull_up', True)
        active_state = kwargs.pop('active_state', None)
        bounce_time = kwargs.pop('bounce_time', None)
        hold_time = kwargs.pop('hold_time', 1)
        hold_repeat = kwargs.pop('hold_repeat', False)
        pin_factory = kwargs.pop('pin_factory', None)
        order = kwargs.pop('_order', None)
        super(ButtonBoard, self).__init__(
            *(
                Button(pin, pull_up=pull_up, active_state=active_state,
                       bounce_time=bounce_time, hold_time=hold_time,
                       hold_repeat=hold_repeat)
                for pin in args
            ),
            _order=order,
            pin_factory=pin_factory,
            **{
                name: Button(pin, pull_up=pull_up, active_state=active_state,
                             bounce_time=bounce_time, hold_time=hold_time,
                             hold_repeat=hold_repeat)
                for name, pin in kwargs.items()
            }
        )
        if len(self) == 0:
            raise GPIOPinMissing('No pins given')
        def get_new_handler(device):
            def fire_both_events(ticks, state):
                device._fire_events(ticks, device._state_to_value(state))
                self._fire_events(ticks, self.value)
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

    @property
    def when_changed(self):
        return self._when_changed

    @when_changed.setter
    def when_changed(self, value):
        self._when_changed = self._wrap_callback(value)

    def _fire_changed(self):
        if self.when_changed:
            self.when_changed()

    def _fire_events(self, ticks, new_value):
        super(ButtonBoard, self)._fire_events(ticks, new_value)
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
            super(LEDBoard, self).on()

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
            super(LEDBoard, self).off()

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
            target=self._blink_device,
            args=(on_time, off_time, fade_in_time, fade_out_time, n))
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
    def __init__(self, *pins, **kwargs):
        # Don't allow graphs to contain collections
        for pin in pins:
            if isinstance(pin, Device):
                raise CompositeDeviceBadDevice(
                    'Only pins may be specified for LEDBarGraph')
        pwm = kwargs.pop('pwm', False)
        active_high = kwargs.pop('active_high', True)
        initial_value = kwargs.pop('initial_value', 0.0)
        pin_factory = kwargs.pop('pin_factory', None)
        if kwargs:
            raise TypeError(
                'unexpected keyword argument: %s' % kwargs.popitem()[0])
        super(LEDBarGraph, self).__init__(
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
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        pins_dict = OrderedDict(star=2)
        pins = (4, 15, 13, 21, 25, 8, 5, 10, 16, 17, 27, 26,
                24, 9, 12, 6, 20, 19, 14, 18, 11, 7, 23, 22)
        for i, pin in enumerate(pins):
            pins_dict['led%d' % (i+1)] = pin
        super(PiHutXmasTree, self).__init__(
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

    def __init__(self, initial_value=(0, 0, 0), pwm=True, pin_factory=None):
        super(LedBorg, self).__init__(red=17, green=27, blue=22,
                                      pwm=pwm, initial_value=initial_value,
                                      pin_factory=pin_factory)


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
    def __init__(self, red=None, amber=None, green=None,
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
            raise GPIOPinMissing('%s pins must be provided' %
                                 ', '.join(devices.keys()))
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
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(PiTraffic, self).__init__(9, 10, 11,
                                        pwm=pwm, initial_value=initial_value,
                                        pin_factory=pin_factory)


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

    Each designated label will contain a "lights" :class:`LEDBoard` containing
    two :class:`LED` objects named "red" and "green", and a :class:`Button`
    object named "button".

    :param str \\*labels:
        Specify the names of the labels you wish to designate the strips to.
        You can list up to five labels. If no labels are given, five strips
        will be initialised with names 'one' to 'five'. If some, but not all
        strips are given labels, any remaining strips will not be initialised.

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
    def __init__(self, lights, buzzer, button, pin_factory=None):
        super(TrafficLightsBuzzer, self).__init__(
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
    def __init__(self, pwm=False, pin_factory=None):
        super(FishDish, self).__init__(
            lights=TrafficLights(9, 22, 4, pwm=pwm, pin_factory=pin_factory),
            buzzer=Buzzer(8, pin_factory=pin_factory),
            button=Button(7, pull_up=False, pin_factory=pin_factory),
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
    def __init__(self, pwm=False, pin_factory=None):
        super(TrafficHat, self).__init__(
            lights=TrafficLights(24, 23, 22, pwm=pwm, pin_factory=pin_factory),
            buzzer=Buzzer(5, pin_factory=pin_factory),
            button=Button(25, pin_factory=pin_factory),
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
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(TrafficpHat, self).__init__(red=25, amber=24, green=23,
                                        pwm=pwm, initial_value=initial_value,
                                        pin_factory=pin_factory)


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
        A tuple of two (or three) GPIO pins representing the forward and
        backward inputs of the left motor's controller. Use three pins if your
        motor controller requires an enable pin.

    :param tuple right:
        A tuple of two (or three) GPIO pins representing the forward and
        backward inputs of the right motor's controller. Use three pins if your
        motor controller requires an enable pin.

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

    .. attribute:: left_motor

        The :class:`Motor` on the left of the robot.

    .. attribute:: right_motor

        The :class:`Motor` on the right of the robot.
    """
    def __init__(self, left=None, right=None, pwm=True, pin_factory=None, *args):
        # *args is a hack to ensure a useful message is shown when pins are
        # supplied as sequential positional arguments e.g. 2, 3, 4, 5
        if not isinstance(left, tuple) or not isinstance(right, tuple):
            raise GPIOPinMissing('left and right motor pins must be given as '
                                 'tuples')
        super(Robot, self).__init__(
            left_motor=Motor(*left, pwm=pwm, pin_factory=pin_factory),
            right_motor=Motor(*right, pwm=pwm, pin_factory=pin_factory),
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
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving forwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
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
            raise ValueError("curve_left and curve_right can't be used at "
                             "the same time")
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
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving backwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
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

    def __init__(self, pwm=True, pin_factory=None):
        super(RyanteckRobot, self).__init__(
            left=(17, 18), right=(22, 23), pwm=pwm, pin_factory=pin_factory
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
    def __init__(self, pwm=True, pin_factory=None):
        super(CamJamKitRobot, self).__init__(
            left=(9, 10), right=(7, 8), pwm=pwm, pin_factory=pin_factory
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

    .. attribute:: left_motor

        The :class:`PhaseEnableMotor` on the left of the robot.

    .. attribute:: right_motor

        The :class:`PhaseEnableMotor` on the right of the robot.
    """
    def __init__(self, left=None, right=None, pwm=True, pin_factory=None, *args):
        # *args is a hack to ensure a useful message is shown when pins are
        # supplied as sequential positional arguments e.g. 2, 3, 4, 5
        if not isinstance(left, tuple) or not isinstance(right, tuple):
            raise GPIOPinMissing('left and right motor pins must be given as '
                                 'tuples')
        super(PhaseEnableRobot, self).__init__(
            left_motor=PhaseEnableMotor(*left, pwm=pwm, pin_factory=pin_factory),
            right_motor=PhaseEnableMotor(*right, pwm=pwm, pin_factory=pin_factory),
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
    def __init__(self, pwm=True, pin_factory=None):
        super(PololuDRV8835Robot, self).__init__(
            left=(5, 12), right=(6, 13), pwm=pwm, pin_factory=pin_factory
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
    state (defaults to :data:`False`, meaning off). Instances of this class can
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
        :data:`False` which will switch the socket off.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _Energenie socket: https://energenie4u.co.uk/index.php/catalogue/product/ENER002-2PI
    """
    def __init__(self, socket=None, initial_value=False, pin_factory=None):
        if socket is None:
            raise EnergenieSocketMissing('socket number must be provided')
        if not (1 <= socket <= 4):
            raise EnergenieBadSocket('socket number must be between 1 and 4')
        if initial_value is None:
            raise EnergenieBadInitialValue("initial value can't be None")
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
        """
        return self._value

    @value.setter
    def value(self, value):
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
    def __init__(self, pwm=False, initial_value=False, pin_factory=None):
        super(PumpkinPi, self).__init__(
            sides=LEDBoard(
                left=LEDBoard(
                    bottom=18, midbottom=17, middle=16, midtop=13, top=24,
                    pwm=pwm, initial_value=initial_value,
                    _order=('bottom', 'midbottom', 'middle', 'midtop', 'top'),
                    pin_factory=pin_factory),
                right=LEDBoard(
                    bottom=19, midbottom=20, middle=21, midtop=22, top=23,
                    pwm=pwm, initial_value=initial_value,
                    _order=('bottom', 'midbottom', 'middle', 'midtop', 'top'),
                    pin_factory=pin_factory),
                pwm=pwm, initial_value=initial_value,
                _order=('left', 'right'),
                pin_factory=pin_factory
                ),
            eyes=LEDBoard(
                left=12, right=6,
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
    def __init__(self, pwm=False, pin_factory=None):
        super(JamHat, self).__init__(
            lights_1=LEDBoard(red=5, yellow=12, green=16,
                              pwm=pwm, _order=('red', 'yellow', 'green'),
                              pin_factory=pin_factory),
            lights_2=LEDBoard(red=6, yellow=13, green=17,
                              pwm=pwm, _order=('red', 'yellow', 'green'),
                              pin_factory=pin_factory),
            button_1=Button(19, pull_up=False, pin_factory=pin_factory),
            button_2=Button(18, pull_up=False, pin_factory=pin_factory),
            buzzer=TonalBuzzer(20, pin_factory=pin_factory),
            _order=('lights_1', 'lights_2', 'button_1', 'button_2', 'buzzer'),
            pin_factory=pin_factory
        )

    def on(self):
        """
        Turns all the LEDs on and makes the buzzer play its mid tone.
        """
        self.buzzer.value = 0
        super(JamHat, self).on()

    def off(self):
        """
        Turns all the LEDs off and stops the buzzer.
        """
        self.buzzer.value = None
        super(JamHat, self).off()

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

    The four input and output channels are not provided by this class. Instead,
    you can create GPIO Zero devices using these pins::

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
    def __init__(self, pwm=False, pin_factory=None):
        super(Pibrella, self).__init__(
            lights=TrafficLights(red=27, amber=17, green=4, pwm=pwm,
                              pin_factory=pin_factory),
            button=Button(11, pull_up=False, pin_factory=pin_factory),
            buzzer=TonalBuzzer(18, pin_factory=pin_factory),
            _order=('lights', 'button', 'buzzer'),
            pin_factory=pin_factory
        )
        InputPins = namedtuple('InputPins', ['a', 'b', 'c', 'd'])
        OutputPins = namedtuple('OutputPins', ['e', 'f', 'g', 'h'])
        self.inputs = InputPins(a=9, b=7, c=8, d=10)
        self.outputs = OutputPins(e=22, f=23, g=24, h=25)

    def on(self):
        """
        Turns all the LEDs on and makes the buzzer play its mid tone.
        """
        self.buzzer.value = 0
        super(Pibrella, self).on()

    def off(self):
        """
        Turns all the LEDs off and stops the buzzer.
        """
        self.buzzer.value = None
        super(Pibrella, self).off()
