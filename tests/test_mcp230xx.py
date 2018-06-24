from threading import Lock
from time import sleep
import sys

from mock import Mock
import pytest

from gpiozero import MCP23017Factory
from gpiozero.exc import PinInvalidPin, PinError, PinInvalidPull, \
    PinInvalidFunction, PinInvalidPolarity, PinInvalidBounce, PinInvalidEdges
from gpiozero.pins.mcp230xx import get_bit_state, Debouncer, \
    EdgeDetector, EDGE_FALL, EDGE_RISE, Register, MCP230xxPin, MCP230xxPoller


def test_get_bit_state():
    assert bool(get_bit_state([0b10000000], 7))
    assert bool(get_bit_state([0b11111111], 7))
    assert not bool(get_bit_state([0b01111111], 7))
    assert not bool(get_bit_state([0b00000000], 3))
    assert bool(get_bit_state([0b00001000], 3))
    assert not bool(get_bit_state([0], 4))
    assert not bool(get_bit_state([0, 0], 15))
    assert bool(get_bit_state([0, 0b10000000], 15))


@pytest.mark.parametrize(
    'debouncing_delay, reading_interval, input_values, output_values',
    (
        # Read new values every 1ms, and debounce them over 20ms (defaults)
        (
            0.02, 0.001,
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        ),
        # Read new values every 10ms, and debounce over 100ms
        (
            0.1, 0.01,
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ),
    ),
)
def test_debouncer(debouncing_delay, reading_interval,
                   input_values, output_values):
    debouncer = Debouncer(debouncing_delay)
    result = []
    now = 0
    for index, value in enumerate(input_values):
        result.append(debouncer(value, now))
        now += reading_interval
    assert result == output_values


def test_edge_detector():
    detector = EdgeDetector()
    assert detector(0) is None
    assert detector(0) is None
    assert detector(1) is EDGE_RISE
    assert detector(1) is None
    assert detector(0) is EDGE_FALL


def test_register():
    class Foo(object):
        bar = Register(0x42)
        baz = Register(0x43)
    foo = Foo()
    # Test descriptor instances caching (_from_cache & __get__)
    assert Register.CACHE == {}
    assert foo.bar.address == 0x42
    assert foo.bar.factory == foo
    assert Register.CACHE == {(0x42, foo): foo.bar}
    assert foo.baz.address == 0x43
    assert foo.baz.factory == foo
    assert Register.CACHE == {(0x42, foo): foo.bar, (0x43, foo): foo.baz}
    # __repr__
    assert repr(foo.bar) == 'Register(address=0x42, factory=%r)' % foo
    # Test writing (write)
    foo.write = Mock()
    foo.bar.write([0, 1])
    foo.write.assert_called_once_with(0x42, [0, 1])
    # Alternative write API (__set__)
    foo.write = Mock()
    foo.bar = [2, 3]
    foo.write.assert_called_once_with(0x42, [2, 3])
    # Test reading (read)
    foo.read = Mock(return_value=[4, 5])
    assert foo.bar.read() == [4, 5]
    foo.read.assert_called_once_with(0x42)
    # Test accessing a specific bit using indexing (__getitem__)
    foo.read = Mock(return_value=[0b10101010, 0b01010101])
    assert foo.bar[0] is False
    assert foo.bar[1] is True
    assert foo.bar[8] is True
    assert foo.bar[15] is False
    assert foo.read.call_count == 4
    # Test changing a bit value using indexing (__setitem__)
    foo.read = Mock(return_value=[0, 0])
    foo.write = Mock()
    foo.bar[0] = 1
    foo.bar[15] = True
    assert foo.read() == [1, 0b10000000]
    assert foo.read.call_count == 3
    assert foo.write.call_count == 2


def test_MCP23017Factory():
    i2c = Mock()
    pin = Mock(spec_set=['number', 'pull'], number=0)
    pin_class = Mock(side_effect=lambda factory, number, **parameters: pin)
    poller = Mock()
    poller_class = Mock(side_effect=lambda factory: poller)
    factory = MCP23017Factory(
        i2c=i2c, pin_class=pin_class, poller_class=poller_class)

    # __init__
    assert factory.address == 0x20
    assert factory.i2c == i2c
    assert factory.pin_class == pin_class
    assert factory.poller_class == poller_class
    assert factory.register_size == 2
    assert factory.poller is None
    assert factory._pins == {}

    # __repr__
    assert repr(factory) == 'MCP23017Factory(address=0x20, i2c=%r)' % i2c

    # read
    i2c.read = Mock(return_value=[1, 4])
    assert factory.read(0x42) == [1, 4]
    i2c.read.assert_called_once_with(0x20, 0x42, 2)

    # write
    i2c.write = Mock()
    assert factory.write(0x42, [2, 5]) is None
    i2c.write.assert_called_once_with(0x20, 0x42, [2, 5])

    # pin
    #  1st call - create it with given parameters
    assert factory.pin(0, pull='up') is pin
    assert factory._pins == {0: pin}
    pin_class.assert_called_once_with(factory, 0, pull='up')
    #  2nd call - get it from cache and update parameters
    assert factory.pin(0, pull='floating') is pin
    assert pin.pull == 'floating'
    assert factory._pins == {0: pin}
    #  Invalid pin number raises an exception
    with pytest.raises(PinInvalidPin):
        factory.pin(42)
    #  Invalid pin parameter raises an exception
    with pytest.raises(PinError):
        factory.pin(0, foo=42)

    # subscribe
    callback = lambda: 42
    factory.subscribe(5, EDGE_FALL, callback)
    poller_class.assert_called_once_with(factory)
    assert factory.poller is poller
    poller.start.assert_called_once_with()
    poller.subscribe.assert_called_once_with(5, EDGE_FALL, callback)

    # unsubscribe
    #  poller still have subscribers after unsubscription
    factory.unsubscribe(5, EDGE_FALL, callback)
    poller.unsubscribe.assert_called_once_with(5, EDGE_FALL, callback)
    assert poller.stop.call_count == 0
    #  no more subscribers, automatic poller shutdown
    poller.subscribers = set()
    factory.unsubscribe(5, EDGE_FALL, callback)
    poller.stop.assert_called_once_with()
    assert factory.poller is None


def test_MCP230xxPin():
    factory = MCP23017Factory(i2c=Mock())
    factory.iodir.read = Mock(
        side_effect=[[0, 0], [1, 0], [1, 0], [0, 0], [0, 0], [0, 0]])
    factory.iodir.write = Mock()
    factory.gppu.read = Mock(
        side_effect=[[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [1, 0]])
    factory.gppu.write = Mock()
    factory.ipol.read = Mock(
        side_effect=[[0, 0], [0, 0], [0, 0], [1, 0], [1, 0], [1, 0]])
    factory.ipol.write = Mock()
    pin = MCP230xxPin(factory, 0)

    # __init__
    assert pin.factory is factory
    assert pin.number == 0
    assert pin.function == 'input'
    factory.iodir.write.assert_called_once_with([1, 0])
    assert pin.pull == 'floating'
    factory.gppu.write.assert_called_once_with([0, 0])
    assert pin.edges == 'both'
    assert pin.bounce == 0
    assert pin.polarity == 'normal'
    factory.ipol.write.assert_called_once_with([0, 0])

    # Ensure changing the pin function results in a write to the IODIR register
    pin.function = 'output'
    assert pin.function == 'output'
    factory.iodir.write.assert_called_with([0, 0])
    # Exceptions
    with pytest.raises(PinInvalidFunction):
        pin.function = 'foo'

    # Ensure changing the pull resistor status results in a write to the
    # GPPU register
    pin.pull = 'up'
    assert pin.pull == 'up'
    factory.gppu.write.assert_called_with([1, 0])
    # Exceptions
    with pytest.raises(PinInvalidPull):
        pin.pull = 'down'

    # Ensure attaching a callback to the pin results in subscribing to events
    # on the factory side
    factory.subscribe = Mock()
    factory.unsubscribe = Mock()
    pin.edges = 'falling'
    assert pin.edges == 'falling'
    assert factory.subscribe.call_count == 0
    pin.when_changed = lambda: 42
    factory.subscribe.assert_called_once_with(
        0, EDGE_FALL, pin._call_when_changed)
    # Ensure changing the expected edges results in un-subscribing then
    # re-subscribing with the new edges
    factory.subscribe.reset_mock()
    factory.unsubscribe.reset_mock()
    pin.edges = 'rising'
    factory.unsubscribe.assert_called_once_with(
        0, EDGE_FALL, pin._call_when_changed)
    factory.subscribe.assert_called_once_with(
        0, EDGE_RISE, pin._call_when_changed)
    # Exceptions
    with pytest.raises(PinInvalidEdges):
        pin.edges = 'foo'

    # Check bounce property read/write
    pin.bounce = 100
    assert pin.bounce == 100
    pin.bounce = 200
    assert pin.bounce == 200
    # Exceptions
    with pytest.raises(PinInvalidBounce):
        pin.bounce = -1

    # Ensure changing the pin input polarity results in a write to the IPOL
    # register
    pin.polarity = 'reversed'
    assert pin.polarity == 'reversed'
    factory.ipol.write.assert_called_with([1, 0])
    # Exceptions
    with pytest.raises(PinInvalidPolarity):
        pin.polarity = 'foo'

    # Ensure changing the pin state results in a write to the OLAT register
    factory.olat.read = Mock(side_effect=[[0, 0]])
    factory.olat.write = Mock()
    pin.state = 1
    factory.olat.write.assert_called_once_with([1, 0])

    # Ensure pin states are read by default by querying the GPIO register
    factory.gpio.read = Mock(side_effect=[[1, 0], [0, 0]])
    pin.bounce = None
    assert pin.state is True
    assert factory.gpio.read.call_count == 1
    # Ensure they use the cached value instead when provided
    pin._state = False
    assert pin.state is False
    assert factory.gpio.read.call_count == 1
    # Ensure they fall back to the GPIO register when unset
    pin._state = None
    assert pin.state is False
    assert factory.gpio.read.call_count == 2


@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_MCP230xxPoller():
    factory = MCP23017Factory(i2c=Mock())
    poller = MCP230xxPoller(factory)
    # __init__
    assert poller.factory is factory
    assert poller.interval == 0.001
    assert poller.subscribers == {}
    assert hasattr(poller, 'lock')
    # subscribe
    poller.lock = Mock(__enter__=Mock(), __exit__=Mock())
    callback = lambda: None
    poller.subscribe(0, EDGE_RISE, callback)
    poller.lock.__enter__.assert_called_once_with()
    poller.lock.__exit__.assert_called_once_with(None, None, None)
    assert poller.subscribers == {(0, EDGE_RISE): set([callback])}
    # unsubscribe
    poller.lock.reset_mock()
    poller.unsubscribe(0, EDGE_RISE, callback)
    poller.lock.__enter__.assert_called_once_with()
    poller.lock.__exit__.assert_called_once_with(None, None, None)
    assert poller.subscribers == {}
    # run - Ensure callbacks are approprietely invoked
    factory.iodir.read = Mock(side_effect=[[0xff, 0xff]] * 16)
    factory.gppu.read = Mock(side_effect=[[0, 0]] * 16)
    factory.ipol.read = Mock(side_effect=[[0, 0]] * 16)
    states = [[0, 0]] * 20 + [[1, 0]] * 40 + [[0, 0]] * 40
    rise_callback = Mock()
    fall_callback = Mock()
    poller.subscribe(0, EDGE_RISE, rise_callback)
    poller.subscribe(0, EDGE_FALL, fall_callback)
    pin = factory.pin(0, bounce=15)
    # (fake) run the poller
    assert pin._state is None  # Ensure pin state is not managed by poller
    now = 0
    for index, state in enumerate(states):
        poller._run_for_pin(0, state, now + index / 1000.)
    assert pin._state is not None  # Ensure pin state is managed by poller
    # Ensure pin states are boolean when managed by the poller
    assert pin.state is False
    rise_callback.assert_called_once_with()
    fall_callback.assert_called_once_with()
    # Ensure pin management by poller ends when poller is shut down
    poller.stop()
    assert pin._state is None
