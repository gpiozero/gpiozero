from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')
try:
    range = xrange
except NameError:
    pass

import io
import os
from time import sleep

import pytest
import pkg_resources

from gpiozero import (
    PinFixedPull,
    PinInvalidPull,
    PinInvalidFunction,
    PinPWMUnsupported,
    Device,
    )
from gpiozero.pins.mock import MockConnectedPin, MockFactory
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose


# This module assumes you've wired the following GPIO pins together. The pins
# can be re-configured via the listed environment variables (useful for when
# your testing rig requires different pins because the defaults interfere with
# attached hardware).
TEST_PIN = int(os.getenv('GPIOZERO_TEST_PIN', '22'))
INPUT_PIN = int(os.getenv('GPIOZERO_TEST_INPUT_PIN', '27'))


@pytest.fixture(
    scope='module',
    params=[
        name
        for name in pkg_resources.get_distribution('gpiozero').get_entry_map('gpiozero_pin_factories').keys()
        if not name.endswith('Pin') # leave out compatibility names
    ])
def pin_factory(request):
    try:
        factory = pkg_resources.load_entry_point('gpiozero', 'gpiozero_pin_factories', request.param)()
    except Exception as e:
        pytest.skip("skipped factory %s: %s" % (request.param, str(e)))
    else:
        Device.pin_factory = factory
        def fin():
            Device.pin_factory = MockFactory()
        request.addfinalizer(fin)
        return factory


@pytest.fixture(scope='function')
def pins(request, pin_factory):
    # Why return both pins in a single fixture? If we defined one fixture for
    # each pin then pytest will (correctly) test RPiGPIOPin(22) against
    # NativePin(27) and so on. This isn't supported, so we don't test it
    input_pin = pin_factory.pin(INPUT_PIN)
    input_pin.function = 'input'
    input_pin.pull = 'down'
    if pin_factory.__class__.__name__ == 'MockFactory':
        test_pin = pin_factory.pin(TEST_PIN, pin_class=MockConnectedPin, input_pin=input_pin)
    else:
        test_pin = pin_factory.pin(TEST_PIN)
    def fin():
        test_pin.close()
        input_pin.close()
    request.addfinalizer(fin)
    return test_pin, input_pin


def test_pin_numbers(pins):
    test_pin, input_pin = pins
    assert test_pin.number == TEST_PIN
    assert input_pin.number == INPUT_PIN

def test_function_bad(pins):
    test_pin, input_pin = pins
    with pytest.raises(PinInvalidFunction):
        test_pin.function = 'foo'

def test_output(pins):
    test_pin, input_pin = pins
    test_pin.function = 'output'
    test_pin.state = 0
    assert input_pin.state == 0
    test_pin.state = 1
    assert input_pin.state == 1

def test_output_with_state(pins):
    test_pin, input_pin = pins
    test_pin.output_with_state(0)
    assert input_pin.state == 0
    test_pin.output_with_state(1)
    assert input_pin.state == 1

def test_pull(pins):
    test_pin, input_pin = pins
    test_pin.function = 'input'
    test_pin.pull = 'up'
    assert input_pin.state == 1
    test_pin.pull = 'down'
    test_pin, input_pin = pins
    assert input_pin.state == 0

def test_pull_bad(pins):
    test_pin, input_pin = pins
    test_pin.function = 'input'
    with pytest.raises(PinInvalidPull):
        test_pin.pull = 'foo'
    with pytest.raises(PinInvalidPull):
        test_pin.input_with_pull('foo')

def test_pull_down_warning(pin_factory):
    if pin_factory.pi_info.pulled_up('GPIO2'):
        pin = pin_factory.pin(2)
        try:
            with pytest.raises(PinFixedPull):
                pin.pull = 'down'
            with pytest.raises(PinFixedPull):
                pin.input_with_pull('down')
        finally:
            pin.close()
    else:
        pytest.skip("GPIO2 isn't pulled up on this pi")

def test_input_with_pull(pins):
    test_pin, input_pin = pins
    test_pin.input_with_pull('up')
    assert input_pin.state == 1
    test_pin.input_with_pull('down')
    assert input_pin.state == 0

def test_bad_duty_cycle(pins):
    test_pin, input_pin = pins
    test_pin.function = 'output'
    try:
        # NOTE: There's some race in RPi.GPIO that causes a segfault if we
        # don't pause before starting PWM; only seems to happen when stopping
        # and restarting PWM very rapidly (i.e. between test cases).
        if Device.pin_factory.__class__.__name__ == 'RPiGPIOFactory':
            sleep(0.1)
        test_pin.frequency = 100
    except PinPWMUnsupported:
        pytest.skip("%r doesn't support PWM" % test_pin.factory)
    else:
        try:
            with pytest.raises(ValueError):
                test_pin.state = 1.1
        finally:
            test_pin.frequency = None

def test_duty_cycles(pins):
    test_pin, input_pin = pins
    test_pin.function = 'output'
    try:
        # NOTE: see above
        if Device.pin_factory.__class__.__name__ == 'RPiGPIOFactory':
            sleep(0.1)
        test_pin.frequency = 100
    except PinPWMUnsupported:
        pytest.skip("%r doesn't support PWM" % test_pin.factory)
    else:
        try:
            for duty_cycle in (0.0, 0.1, 0.5, 1.0):
                test_pin.state = duty_cycle
                assert test_pin.state == duty_cycle
                total = sum(input_pin.state for i in range(20000))
                assert isclose(total / 20000, duty_cycle, rel_tol=0.1, abs_tol=0.1)
        finally:
            test_pin.frequency = None

