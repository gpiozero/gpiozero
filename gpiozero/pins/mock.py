from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


from collections import namedtuple
from time import time
try:
    from math import isclose
except ImportError:
    from ..compat import isclose

from . import Pin, PINS_CLEANUP
from ..exc import PinSetInput, PinPWMUnsupported


PinState = namedtuple('PinState', ('timestamp', 'state'))

class MockPin(Pin):
    """
    A mock pin used primarily for testing. This class does *not* support PWM.
    """

    def __init__(self, number):
        if not (0 <= number < 54):
            raise ValueError('invalid pin %d specified (must be 0..53)' % number)
        self._number = number
        self._function = 'input'
        self._state = False
        self._pull = 'floating'
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self._last_change = time()
        self.states = [PinState(0.0, False)]

    def __repr__(self):
        return 'MOCK%d' % self._number

    @property
    def number(self):
        return self._number

    def close(self):
        self.when_changed = None
        self.function = 'input'

    def _get_function(self):
        return self._function

    def _set_function(self, value):
        assert value in ('input', 'output')
        self._function = value
        if value == 'input':
            # Drive the input to the pull
            self._set_pull(self._get_pull())

    def _get_state(self):
        return self._state

    def _set_state(self, value):
        if self._function == 'input':
            raise PinSetInput()
        assert self._function == 'output'
        assert 0 <= value <= 1
        if self._state != value:
            t = time()
            self._state = value
            self.states.append(PinState(t - self._last_change, value))
            self._last_change = t

    def _get_frequency(self):
        return None

    def _set_frequency(self, value):
        raise PinPWMUnsupported()

    def _get_pull(self):
        return self._pull

    def _set_pull(self, value):
        assert self._function == 'input'
        assert value in ('floating', 'up', 'down')
        self._pull = value
        if value == 'up':
            self.drive_high()
        elif value == 'down':
            self.drive_low()

    def _get_bounce(self):
        return self._bounce

    def _set_bounce(self, value):
        # XXX Need to implement this
        self._bounce = value

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        assert value in ('none', 'falling', 'rising', 'both')
        self._edges = value

    def _get_when_changed(self):
        return self._when_changed

    def _set_when_changed(self, value):
        self._when_changed = value

    def drive_high(self):
        assert self._function == 'input'
        if not self._state:
            t = time()
            self._state = True
            self.states.append(PinState(t - self._last_change, True))
            self._last_change = t
            if self._edges in ('both', 'rising') and self._when_changed is not None:
                self._when_changed()

    def drive_low(self):
        assert self._function == 'input'
        if self._state:
            t = time()
            self._state = False
            self.states.append(PinState(t - self._last_change, False))
            self._last_change = t
            if self._edges in ('both', 'falling') and self._when_changed is not None:
                self._when_changed()

    def clear_states(self):
        self._last_change = time()
        self.states = [PinState(0.0, self.state)]

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
            assert isclose(actual.timestamp, expected[0], rel_tol=0.01, abs_tol=0.01)
            assert isclose(actual.state, expected[1])


class MockPWMPin(MockPin):
    """
    This derivative of :class:`MockPin` adds PWM support.
    """

    def __init__(self, number):
        super(MockPWMPin, self).__init__(number)
        self._frequency = None

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, value):
        if value is not None:
            assert self._function == 'output'
        self._frequency = value
        if value is None:
            self.state = False

