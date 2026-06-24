# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2024 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import time
from collections import namedtuple
from time import monotonic
from threading import Thread, Event
from math import isclose

from multiio import SMmultiio
import megaind

from ..exc import (
    PinPWMUnsupported,
    PinSetInput,
    PinFixedPull,
    PinInvalidPin,
    PinInvalidFunction,
    PinInvalidPull,
    PinInvalidBounce,
    )
from .pi import PiPin, PiFactory

PinState = namedtuple('PinState', ('timestamp', 'state'))


class MultiIOAnalogPin(PiPin):
    """
    Input pin that reads a 0-10V analog input on the Multi-IO HAT via I2C.
    """
    def __init__(self, factory, info, stack=0, channel=1):
        super().__init__(factory, info)
        self._stack = stack
        self._channel = channel
        self._function = 'input'
        self._pull = info.pull or 'floating'
        self._state = 0.0
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self.card = SMmultiio(stack=stack)
        self.clear_states()

    def clear_states(self):
        self._last_change = monotonic()
        self.states = [PinState(0.0, self._state)]

    def _get_function(self):
        return self._function

    def _set_function(self, value):
        if value != 'input':
            raise PinInvalidFunction('MultiIOAnalogPin is input-only')
        self._function = value

    def _get_state(self):
        return self.card.get_u_in(self._channel) / 10.0

    def _set_state(self, value):
        raise PinSetInput(f'MultiIOAnalogPin is read-only: {self!r}')

    def _get_frequency(self):
        return None

    def _set_frequency(self, value):
        if value is not None:
            raise PinPWMUnsupported()

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if value not in ('floating', 'up', 'down'):
            raise PinInvalidPull('pull must be floating, up, or down')
        self._pull = value

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        self._bounce = value

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        self._edges = value


class MultiIOPin(PiPin):
    """
    Output pin that drives a relay channel on the Multi-IO HAT via I2C.
    This class does *not* support PWM.
    """
    def __init__(self, factory, info, stack=0, channel=1):
        super().__init__(factory, info)
        self._function = 'input'
        self._pull = info.pull or 'floating'
        self._state = self._pull == 'up'
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self.clear_states()
        self.card = SMmultiio(stack=stack)
        self._channel = channel

    def close(self):
        self.when_changed = None
        self.function = 'input'

    def _get_function(self):
        return self._function

    def _set_function(self, value):
        if value not in ('input', 'output'):
            raise PinInvalidFunction('function must be input or output')
        self._function = value
        if value == 'input':
            # Drive the input to the pull
            self._set_pull(self._get_pull())

    def _get_state(self):
        return self._state

    def _set_state(self, value):
        if self._function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        assert self._function == 'output'
        assert 0 <= value <= 1
        self._change_state(bool(value))
        self.card.set_relay(self._channel, 1 if value else 0)
        time.sleep(0.05)  # let the I2C write settle on the card

    def _change_state(self, value):
        if self._state != value:
            t = monotonic()
            self._state = value
            self.states.append(PinState(t - self._last_change, value))
            self._last_change = t
            return True
        return False

    def _get_frequency(self):
        return None

    def _set_frequency(self, value):
        if value is not None:
            raise PinPWMUnsupported()

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull(f'cannot set pull on non-input pin {self!r}')
        if self.info.pull and value != self.info.pull:
            raise PinFixedPull(f'{self!r} has a fixed pull resistor')
        if value not in ('floating', 'up', 'down'):
            raise PinInvalidPull('pull must be floating, up, or down')
        self._pull = value
        if value == 'up':
            self.drive_high()
        elif value == 'down':
            self.drive_low()

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        # XXX Need to implement this
        if value is not None:
            try:
                value = float(value)
            except ValueError:
                raise PinInvalidBounce('bounce must be None or a float')
        self._bounce = value

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        assert value in ('none', 'falling', 'rising', 'both')
        self._edges = value

    def _disable_event_detect(self):
        pass

    def _enable_event_detect(self):
        pass

    def _call_when_changed(self):
        super()._call_when_changed(self._last_change, self._state)

    def drive_high(self):
        assert self._function == 'input'
        if self._change_state(True):
            if self._edges in ('both', 'rising') and self._when_changed is not None:
                self._call_when_changed()

    def drive_low(self):
        assert self._function == 'input'
        if self._change_state(False):
            if self._edges in ('both', 'falling') and self._when_changed is not None:
                self._call_when_changed()

    def clear_states(self):
        self._last_change = monotonic()
        self.states = [PinState(0.0, self._state)]

    def assert_states(self, expected_states):
        # Tests that the pin went through the expected states (a list of values)
        for actual, expected in zip(self.states, expected_states):
            assert actual.state == expected

    def assert_states_and_times(self, expected_states):
        # Tests that the pin went through the expected states at the expected
        # times (times are compared with a tolerance of tens-of-milliseconds as
        # that's about all we can reasonably expect in a non-realtime
        # environment on a Pi 1)
        for actual, expected in zip(self.states, expected_states):
            assert isclose(actual.timestamp, expected[0], rel_tol=0.05, abs_tol=0.05)
            assert isclose(actual.state, expected[1])


class MegaindPin(PiPin):
    """
    Output pin that drives a digital output (OD) on the Megaind HAT via I2C.
    """
    def __init__(self, factory, info, stack=0, channel=1):
        super().__init__(factory, info)
        self._stack = stack
        self._channel = channel
        self._function = 'input'
        self._pull = info.pull or 'floating'
        self._state = False
        self._frequency = None
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self.clear_states()

    def close(self):
        self.when_changed = None
        self.function = 'input'

    def clear_states(self):
        self._last_change = monotonic()
        self.states = [PinState(0.0, self._state)]

    def _get_function(self):
        return self._function

    def _set_function(self, value):
        if value not in ('input', 'output'):
            raise PinInvalidFunction('function must be input or output')
        self._function = value
        if value == 'input':
            # Drive the input to the pull
            self._set_pull(self._get_pull())

    def _get_state(self):
        return self._state

    def _set_state(self, value):
        if self._function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        assert self._function == 'output'
        assert 0 <= value <= 1
        if self._frequency is None:
            self._change_state(bool(value))
            megaind.setOd(self._stack, self._channel, 1 if value else 0)
        else:
            self._change_state(float(value))
            megaind.setOdPWM(self._stack, self._channel, float(value) * 100)
        time.sleep(0.05)

    def _change_state(self, value):
        if self._state != value:
            t = monotonic()
            self._state = value
            self.states.append(PinState(t - self._last_change, value))
            self._last_change = t
            return True
        return False

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, value):
        # The Megaind OD channels have a fixed-frequency hardware PWM
        # generator; the requested Hz value can't be applied, it's only
        # used here as an on/off switch between digital and PWM output.
        self._frequency = value
        if value is None:
            self._change_state(False)
            megaind.setOd(self._stack, self._channel, 0)

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if self.function != 'input':
            raise PinFixedPull(f'cannot set pull on non-input pin {self!r}')
        if value not in ('floating', 'up', 'down'):
            raise PinInvalidPull('pull must be floating, up, or down')
        self._pull = value

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        if value is not None:
            try:
                value = float(value)
            except ValueError:
                raise PinInvalidBounce('bounce must be None or a float')
        self._bounce = value

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        assert value in ('none', 'falling', 'rising', 'both')
        self._edges = value

    def _disable_event_detect(self):
        pass

    def _enable_event_detect(self):
        pass

    def _call_when_changed(self):
        super()._call_when_changed(self._last_change, self._state)


class MegaindOptoPin(PiPin):
    """
    Input pin that reads an optocoupled input on the Megaind HAT via I2C.

    I2C reads are not interrupt-driven, so change detection (used by
    :attr:`when_changed`, e.g. :class:`~gpiozero.Button`) is implemented with
    a background poll thread that is only running while a callback is
    actually attached.
    """
    POLL_INTERVAL = 0.02

    def __init__(self, factory, info, stack=0, channel=1):
        super().__init__(factory, info)
        self._stack = stack
        self._channel = channel
        self._function = 'input'
        self._pull = info.pull or 'floating'
        self._state = self._read_hw_state()
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self._poll_thread = None
        self._poll_stop = Event()
        self.clear_states()

    def close(self):
        self.when_changed = None

    def clear_states(self):
        self._last_change = monotonic()
        self.states = [PinState(0.0, self._state)]

    def _get_function(self):
        return self._function

    def _set_function(self, value):
        if value != 'input':
            raise PinInvalidFunction('MegaindOptoPin is input-only')
        self._function = value

    def _read_hw_state(self):
        val = megaind.getOpto(self._stack)
        return (val >> (self._channel - 1)) & 1

    def _get_state(self):
        self._change_state(self._read_hw_state())
        return self._state

    def _set_state(self, value):
        raise PinSetInput(f'MegaindOptoPin is read-only: {self!r}')

    def _change_state(self, value):
        value = bool(value)
        if self._state != value:
            t = monotonic()
            self._state = value
            self.states.append(PinState(t - self._last_change, value))
            self._last_change = t
            return True
        return False

    def _get_frequency(self):
        return None

    def _set_frequency(self, value):
        if value is not None:
            raise PinPWMUnsupported()

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        if value not in ('floating', 'up', 'down'):
            raise PinInvalidPull('pull must be floating, up, or down')
        self._pull = value

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        self._bounce = value

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        self._edges = value

    def _call_when_changed(self):
        super()._call_when_changed(self._last_change, self._state)

    def _enable_event_detect(self):
        if self._poll_thread is None:
            self._poll_stop.clear()
            self._poll_thread = Thread(target=self._poll_loop, daemon=True)
            self._poll_thread.start()

    def _disable_event_detect(self):
        if self._poll_thread is not None:
            self._poll_stop.set()
            self._poll_thread.join()
            self._poll_thread = None

    def _poll_loop(self):
        while not self._poll_stop.wait(self.POLL_INTERVAL):
            value = bool(self._read_hw_state())
            if self._change_state(value):
                if self._edges in ('both', 'rising' if value else 'falling'):
                    self._call_when_changed()


class MultiIOFactory(PiFactory):
    """
    Factory for generating pins connected to a Sequent Microsystems Multi-IO
    HAT over I2C.

    The *stack* parameter identifies which physical board to talk to (the
    hardware address set via the board's jumpers, 0-7). The *pin_type*
    parameter selects which channel family the factory produces by default:
    ``'relay'`` for :class:`MultiIOPin` or ``'analog_in'`` for
    :class:`MultiIOAnalogPin`. This can be overridden per-call via the
    *pin_class* argument to :meth:`pin`.

    .. attribute:: pin_class

        This attribute stores the pin class that will be used when
        constructing pins with the :meth:`pin` method (if no *pin_class*
        parameter is used to override it). It defaults on construction to
        ``PIN_TYPES[pin_type]``.
    """

    PIN_TYPES = {
        'relay':     MultiIOPin,
        'analog_in': MultiIOAnalogPin,
    }

    def __init__(self, revision=None, stack=0, pin_type='relay'):
        super().__init__()
        if revision is None:
            revision = os.environ.get('GPIOZERO_MOCK_REVISION', 'a02082')
        self._revision = int(revision, base=16)
        self.stack = stack
        if pin_type not in self.PIN_TYPES:
            raise ValueError(f'pin_type inconnu: {pin_type}')
        self.pin_class = self.PIN_TYPES[pin_type]

    def _get_revision(self):
        return self._revision

    def reset(self):
        """
        Clears the pins and reservations sets. This is primarily useful in
        test suites to ensure the pin factory is back in a "clean" state before
        the next set of tests are run.
        """
        self.pins.clear()
        self._reservations.clear()

    def pin(self, name, pin_class=None, **kwargs):
        """
        The pin method for :class:`MultiIOFactory` additionally takes a
        *pin_class* attribute which can be used to override the class'
        :attr:`pin_class` attribute. Any additional keyword arguments will be
        passed along to the pin constructor.
        """
        if pin_class is None:
            pin_class = self.pin_class
        for header, info in self.board_info.find_pin(name):
            try:
                pin = self.pins[info]
            except KeyError:
                pin = pin_class(self, info, stack=self.stack, channel=name, **kwargs)
                self.pins[info] = pin
            else:
                # Ensure the cached pin is compatible with what was requested
                if not isinstance(pin, pin_class):
                    raise ValueError(
                        f'pin {info.name} is already in use as a '
                        f'{pin.__class__.__name__}')
            return pin
        raise PinInvalidPin(f'{name} is not a valid pin name')

    def relay(self, channel=1):
        """
        Return a :class:`MultiIORelay` wrapper for the given relay channel,
        bypassing the :class:`~gpiozero.Pin`/:class:`LED` machinery.
        """
        return MultiIORelay(stack=self.stack, channel=channel)

    def analog_in(self, channel=1):
        """
        Return a :class:`MultiIOAnalogInput` wrapper for the given analog
        input channel, bypassing the :class:`~gpiozero.Pin`/
        :class:`~gpiozero.Potentiometer` machinery.
        """
        return MultiIOAnalogInput(stack=self.stack, channel=channel)

    @staticmethod
    def ticks():
        return monotonic()

    @staticmethod
    def ticks_diff(later, earlier):
        return later - earlier


class MegaindFactory(PiFactory):
    """
    Factory for generating pins connected to a Sequent Microsystems Megaind
    HAT over I2C. Structurally identical to :class:`MultiIOFactory`, but
    targets the Megaind board/library instead.

    The *stack* parameter identifies which physical board to talk to (the
    hardware address set via the board's jumpers, 0-7). The *pin_type*
    parameter selects which channel family the factory produces by default:
    ``'od'`` for :class:`MegaindPin` or ``'opto'`` for
    :class:`MegaindOptoPin`.
    """
    PIN_TYPES = {
        'od':   MegaindPin,
        'opto': MegaindOptoPin,
    }

    def __init__(self, revision=None, stack=0, pin_type='od'):
        super().__init__()
        if revision is None:
            revision = os.environ.get('GPIOZERO_MOCK_REVISION', 'a02082')
        self._revision = int(revision, base=16)
        self.stack = stack
        if pin_type not in self.PIN_TYPES:
            raise ValueError(f'pin_type inconnu: {pin_type}')
        self.pin_class = self.PIN_TYPES[pin_type]

    def _get_revision(self):
        return self._revision

    def reset(self):
        """
        Clears the pins and reservations sets. This is primarily useful in
        test suites to ensure the pin factory is back in a "clean" state before
        the next set of tests are run.
        """
        self.pins.clear()
        self._reservations.clear()

    def pin(self, name, pin_class=None, **kwargs):
        """
        The pin method for :class:`MegaindFactory` additionally takes a
        *pin_class* attribute which can be used to override the class'
        :attr:`pin_class` attribute. Any additional keyword arguments will be
        passed along to the pin constructor.
        """
        if pin_class is None:
            pin_class = self.pin_class
        for header, info in self.board_info.find_pin(name):
            try:
                pin = self.pins[info]
            except KeyError:
                pin = pin_class(self, info, stack=self.stack, channel=name, **kwargs)
                self.pins[info] = pin
            else:
                # Ensure the cached pin is compatible with what was requested
                if not isinstance(pin, pin_class):
                    raise ValueError(
                        f'pin {info.name} is already in use as a '
                        f'{pin.__class__.__name__}')
            return pin
        raise PinInvalidPin(f'{name} is not a valid pin name')

    @staticmethod
    def ticks():
        return monotonic()

    @staticmethod
    def ticks_diff(later, earlier):
        return later - earlier


class MultiIOAnalogInput:
    """
    Reads a 0-10V analog input from a Sequent Multi-IO HAT
    """
    def __init__(self, stack=0, channel=1):
        self._card = SMmultiio(stack=stack)
        self._channel = channel

    @property
    def value(self):
        """The reading normalized to 0.0-1.0 (0-10V)."""
        return self._card.get_u_in(self._channel) / 10.0

    @property
    def volts(self):
        """The raw reading in volts (0-10V)."""
        return self._card.get_u_in(self._channel)


class MultiIORelay:
    """
    Controls a relay output on a Sequent Multi-IO HAT
    """
    def __init__(self, stack=0, channel=1):
        self._card = SMmultiio(stack=stack)
        self._channel = channel

    def on(self):
        """Closes the relay."""
        self._card.set_relay(self._channel, 1)

    def off(self):
        """Opens the relay."""
        self._card.set_relay(self._channel, 0)
