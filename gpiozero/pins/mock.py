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
from collections import namedtuple
from time import time, sleep, monotonic
from threading import Thread, Event
from math import isclose

# NOTE: Remove try when compatibility moves beyond Python 3.10
try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points

from ..exc import (
    PinPWMUnsupported,
    PinSetInput,
    PinFixedPull,
    PinInvalidPin,
    PinInvalidFunction,
    PinInvalidPull,
    PinInvalidBounce,
    )
from ..devices import Device
from ..mixins import SharedMixin
from . import SPI
from .pi import PiPin, PiFactory
from .spi import SPISoftware


PinState = namedtuple('PinState', ('timestamp', 'state'))


class MockPin(PiPin):
    """
    A mock pin used primarily for testing. This class does *not* support PWM.
    """
    def __init__(self, factory, info):
        super().__init__(factory, info)
        self._function = 'input'
        self._pull = info.pull or 'floating'
        self._state = self._pull == 'up'
        self._bounce = None
        self._edges = 'both'
        self._when_changed = None
        self.clear_states()

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


class MockConnectedPin(MockPin):
    """
    This derivative of :class:`MockPin` emulates a pin connected to another
    mock pin. This is used in the "real pins" portion of the test suite to
    check that one pin can influence another.
    """
    def __init__(self, factory, info, input_pin=None):
        super().__init__(factory, info)
        self.input_pin = input_pin

    def _change_state(self, value):
        if self.input_pin:
            if value:
                self.input_pin.drive_high()
            else:
                self.input_pin.drive_low()
        return super()._change_state(value)


class MockChargingPin(MockPin):
    """
    This derivative of :class:`MockPin` emulates a pin which, when set to
    input, waits a predetermined length of time and then drives itself high
    (as if attached to, e.g. a typical circuit using an LDR and a capacitor
    to time the charging rate).
    """
    def __init__(self, factory, info, charge_time=0.01):
        super().__init__(factory, info)
        self.charge_time = charge_time # dark charging time
        self._charge_stop = Event()
        self._charge_thread = None

    def _set_function(self, value):
        super()._set_function(value)
        if value == 'input':
            if self._charge_thread:
                self._charge_stop.set()
                self._charge_thread.join()
            self._charge_stop.clear()
            self._charge_thread = Thread(target=self._charge)
            self._charge_thread.start()
        elif value == 'output':
            if self._charge_thread:
                self._charge_stop.set()
                self._charge_thread.join()
        else:
            assert False

    def _charge(self):
        if not self._charge_stop.wait(self.charge_time):
            try:
                self.drive_high()
            except AssertionError:  # pragma: no cover
                # Charging pins are typically flipped between input and output
                # repeatedly; if another thread has already flipped us to
                # output ignore the assertion-error resulting from attempting
                # to drive the pin high
                pass


class MockTriggerPin(MockPin):
    """
    This derivative of :class:`MockPin` is intended to be used with another
    :class:`MockPin` to emulate a distance sensor. Set *echo_pin* to the
    corresponding pin instance. When this pin is driven high it will trigger
    the echo pin to drive high for the echo time.
    """
    def __init__(self, factory, info, echo_pin=None, echo_time=0.04):
        super().__init__(factory, info)
        self.echo_pin = echo_pin
        self.echo_time = echo_time # longest echo time
        self._echo_thread = None

    def _set_state(self, value):
        super()._set_state(value)
        if value:
            if self._echo_thread:
                self._echo_thread.join()
            self._echo_thread = Thread(target=self._echo)
            self._echo_thread.start()

    def _echo(self):
        sleep(0.001)
        self.echo_pin.drive_high()
        sleep(self.echo_time)
        self.echo_pin.drive_low()


class MockPWMPin(MockPin):
    """
    This derivative of :class:`MockPin` adds PWM support.
    """
    def __init__(self, factory, info):
        super().__init__(factory, info)
        self._frequency = None

    def close(self):
        self.frequency = None
        super().close()

    def _set_state(self, value):
        if self._function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        assert self._function == 'output'
        assert 0 <= value <= 1
        self._change_state(float(value))

    def _get_frequency(self):
        return self._frequency

    def _set_frequency(self, value):
        if value is not None:
            assert self._function == 'output'
        self._frequency = value
        if value is None:
            self._change_state(0.0)


class MockSPIClockPin(MockPin):
    """
    This derivative of :class:`MockPin` is intended to be used as the clock pin
    of a mock SPI device. It is not intended for direct construction in tests;
    rather, construct a :class:`MockSPIDevice` with various pin numbers, and
    this class will be used for the clock pin.
    """
    def __init__(self, factory, info):
        super().__init__(factory, info)
        self.spi_devices = getattr(self, 'spi_devices', [])

    def _set_state(self, value):
        super()._set_state(value)
        for dev in self.spi_devices:
            dev.on_clock()


class MockSPISelectPin(MockPin):
    """
    This derivative of :class:`MockPin` is intended to be used as the select
    pin of a mock SPI device. It is not intended for direct construction in
    tests; rather, construct a :class:`MockSPIDevice` with various pin numbers,
    and this class will be used for the select pin.
    """
    def __init__(self, factory, info):
        super().__init__(factory, info)
        self.spi_device = getattr(self, 'spi_device', None)

    def _set_state(self, value):
        super()._set_state(value)
        if self.spi_device:
            self.spi_device.on_select()


class MockSPIDevice:
    """
    This class is used to test :class:`SPIDevice` implementations. It can be
    used to mock up the slave side of simple SPI devices, e.g. the MCP3xxx
    series of ADCs.

    Descendants should override the :meth:`on_start` and/or :meth:`on_bit`
    methods to respond to SPI interface events. The :meth:`rx_word` and
    :meth:`tx_word` methods can be used facilitate communications within these
    methods. Such descendents can then be passed as the *spi_class* parameter
    of the :class:`MockFactory` constructor to have instances attached to any
    SPI interface requested by an :class:`SPIDevice`.
    """
    def __init__(self, clock_pin, mosi_pin=None, miso_pin=None,
                 select_pin=None, *, clock_polarity=False, clock_phase=False,
                 lsb_first=False, bits_per_word=8, select_high=False,
                 pin_factory=None):
        if pin_factory is None:
            pin_factory = Device.pin_factory
            assert isinstance(pin_factory, MockFactory)
        self.clock_pin = pin_factory.pin(clock_pin, pin_class=MockSPIClockPin)
        self.mosi_pin = None if mosi_pin is None else pin_factory.pin(mosi_pin)
        self.miso_pin = None if miso_pin is None else pin_factory.pin(miso_pin)
        self.select_pin = None if select_pin is None else pin_factory.pin(select_pin, pin_class=MockSPISelectPin)
        self.clock_polarity = clock_polarity
        self.clock_phase = clock_phase
        self.lsb_first = lsb_first
        self.bits_per_word = bits_per_word
        self.select_high = select_high
        self.rx_bit = 0
        self.rx_buf = []
        self.tx_buf = []
        self.clock_pin.spi_devices.append(self)
        self.select_pin.spi_device = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        if self in self.clock_pin.spi_devices:
            self.clock_pin.spi_devices.remove(self)
        if self.select_pin is not None:
            self.select_pin.spi_device = None

    def on_select(self):
        if self.select_pin.state == self.select_high:
            self.on_start()

    def on_clock(self):
        # Don't do anything if this SPI device isn't currently selected
        if self.select_pin is None or self.select_pin.state == self.select_high:
            # The XOR of the clock pin's values, polarity and phase indicates
            # whether we're meant to be acting on this edge
            if self.clock_pin.state ^ self.clock_polarity ^ self.clock_phase:
                self.rx_bit += 1
                if self.mosi_pin is not None:
                    self.rx_buf.append(self.mosi_pin.state)
                if self.miso_pin is not None:
                    try:
                        tx_value = self.tx_buf.pop(0)
                    except IndexError:
                        tx_value = 0
                    if tx_value:
                        self.miso_pin.drive_high()
                    else:
                        self.miso_pin.drive_low()
                self.on_bit()

    def on_start(self):
        """
        Override this in descendents to detect when the mock SPI device's
        select line is activated.
        """
        self.rx_bit = 0
        self.rx_buf = []
        self.tx_buf = []

    def on_bit(self):
        """
        Override this in descendents to react to receiving a bit.

        The :attr:`rx_bit` attribute gives the index of the bit received (this
        is reset to 0 by default by :meth:`on_select`). The :attr:`rx_buf`
        sequence gives the sequence of 1s and 0s that have been recevied so
        far. The :attr:`tx_buf` sequence gives the sequence of 1s and 0s to
        transmit on the next clock pulses. All these attributes can be modified
        within this method.

        The :meth:`rx_word` and :meth:`tx_word` methods can also be used to
        read and append to the buffers using integers instead of bool bits.
        """
        pass

    def rx_word(self):
        result = 0
        bits = reversed(self.rx_buf) if self.lsb_first else self.rx_buf
        for bit in bits:
            result <<= 1
            result |= bit
        return result

    def tx_word(self, value, bits_per_word=None):
        if bits_per_word is None:
            bits_per_word = self.bits_per_word
        bits = [0] * bits_per_word
        for bit in range(bits_per_word):
            bits[bit] = value & 1
            value >>= 1
        assert not value
        if not self.lsb_first:
            bits = reversed(bits)
        self.tx_buf.extend(bits)


class MockFactory(PiFactory):
    """
    Factory for generating mock pins.

    The *revision* parameter specifies what revision of Pi the mock factory
    pretends to be (this affects the result of the :attr:`Factory.board_info`
    attribute as well as where pull-ups are assumed to be).

    The *pin_class* attribute specifies which mock pin class will be generated
    by the :meth:`pin` method by default. This can be changed after
    construction by modifying the :attr:`pin_class` attribute.

    .. attribute:: pin_class

        This attribute stores the :class:`MockPin` class (or descendant) that
        will be used when constructing pins with the :meth:`pin` method (if
        no *pin_class* parameter is used to override it). It defaults on
        construction to the value of the *pin_class* parameter in the
        constructor, or :class:`MockPin` if that is unspecified.
    """
    def __init__(self, revision=None, pin_class=None):
        super().__init__()
        if revision is None:
            revision = os.environ.get('GPIOZERO_MOCK_REVISION', 'a02082')
        if pin_class is None:
            pin_class = os.environ.get('GPIOZERO_MOCK_PIN_CLASS', MockPin)
        self._revision = int(revision, base=16)
        if isinstance(pin_class, bytes):
            pin_class = pin_class.decode('ascii')
        if isinstance(pin_class, str):
            group = entry_points(group='gpiozero_mock_pin_classes')
            pin_class = group[pin_class.lower()].load()
        if not issubclass(pin_class, MockPin):
            raise ValueError(f'invalid mock pin_class: {pin_class!r}')
        self.pin_class = pin_class

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
        The pin method for :class:`MockFactory` additionally takes a
        *pin_class* attribute which can be used to override the class'
        :attr:`pin_class` attribute. Any additional keyword arguments will be
        passed along to the pin constructor (useful with things like
        :class:`MockConnectedPin` which expect to be constructed with another
        pin).
        """
        if pin_class is None:
            pin_class = self.pin_class
        for header, info in self.board_info.find_pin(name):
            try:
                pin = self.pins[info]
            except KeyError:
                pin = pin_class(self, info, **kwargs)
                self.pins[info] = pin
            else:
                # Ensure the pin class expected supports PWM (or not)
                if issubclass(pin_class, MockPWMPin) != isinstance(pin, MockPWMPin):
                    raise ValueError(
                        f'pin {info.name} is already in use as a '
                        f'{pin.__class__.__name__}')
            return pin
        raise PinInvalidPin(f'{name} is not a valid pin name')

    def _get_spi_class(self, shared, hardware):
        return MockSPIInterfaceShared if shared else MockSPIInterface

    @staticmethod
    def ticks():
        return monotonic()

    @staticmethod
    def ticks_diff(later, earlier):
        return later - earlier


class MockSPIInterface(SPISoftware):
    pass


class MockSPIInterfaceShared(SharedMixin, MockSPIInterface):
    @classmethod
    def _shared_key(cls, clock_pin, mosi_pin, miso_pin, select_pin,
                    pin_factory):
        return (clock_pin, select_pin)
