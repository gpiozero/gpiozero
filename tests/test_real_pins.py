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
import subprocess

import pytest

from gpiozero import PinFixedPull, PinInvalidPull, PinInvalidFunction
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose


# This module assumes you've wired the following GPIO pins together
TEST_PIN = 22
INPUT_PIN = 27


# Skip the entire module if we're not on a Pi
def is_a_pi():
    with io.open('/proc/cpuinfo', 'r') as cpuinfo:
        for line in cpuinfo:
            if line.startswith('Hardware'):
                hardware, colon, soc = line.strip().split(None, 2)
                return soc in ('BCM2708', 'BCM2709', 'BCM2835', 'BCM2836')
        else:
            return False
pytestmark = pytest.mark.skipif(not is_a_pi(), reason='tests cannot run on non-Pi platforms')
del is_a_pi


# Try and import as many pin libraries as possible
PIN_CLASSES = []
try:
    from gpiozero.pins.rpigpio import RPiGPIOPin
    PIN_CLASSES.append(RPiGPIOPin)
except ImportError:
    RPiGPIOPin = None
try:
    from gpiozero.pins.rpio import RPIOPin
    PIN_CLASSES.append(RPIOPin)
except ImportError:
    RPIOPin = None
try:
    from gpiozero.pins.pigpiod import PiGPIOPin
    PIN_CLASSES.append(PiGPIOPin)
except ImportError:
    PiGPIOPin = None
try:
    from gpiozero.pins.native import NativePin
    PIN_CLASSES.append(NativePin)
except ImportError:
    NativePin = None

@pytest.fixture(scope='module', params=PIN_CLASSES)
def pin_class(request):
    # pigpiod needs to be running for PiGPIOPin
    if request.param.__name__ == 'PiGPIOPin':
        subprocess.check_call(['sudo', 'pigpiod'])
        # Unfortunately, pigpiod provides no option for running in the
        # foreground, so we have to use the sledgehammer of killall to get shot
        # of it
        def kill_pigpiod():
            subprocess.check_call(['sudo', 'killall', 'pigpiod'])
        request.addfinalizer(kill_pigpiod)
    return request.param

@pytest.fixture(scope='function')
def pins(request, pin_class):
    # Why return both pins in a single fixture? If we defined one fixture for
    # each pin then pytest will (correctly) test RPiGPIOPin(22) against
    # NativePin(27) and so on. This isn't supported, so we don't test it
    test_pin = pin_class(TEST_PIN)
    input_pin = pin_class(INPUT_PIN)
    input_pin.function = 'input'
    input_pin.pull = 'down'
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

def test_pull_down_warning(pin_class):
    # XXX This assumes we're on a vaguely modern Pi and not a compute module
    # Might want to refine this with the pi-info database
    pin = pin_class(2)
    try:
        with pytest.raises(PinFixedPull):
            pin.pull = 'down'
        with pytest.raises(PinFixedPull):
            pin.input_with_pull('down')
    finally:
        pin.close()

def test_input_with_pull(pins):
    test_pin, input_pin = pins
    test_pin.input_with_pull('up')
    assert input_pin.state == 1
    test_pin.input_with_pull('down')
    assert input_pin.state == 0

@pytest.mark.skipif(True, reason='causes segfaults')
def test_bad_duty_cycle(pins):
    test_pin, input_pin = pins
    if test_pin.__class__.__name__ == 'NativePin':
        pytest.skip("native pin doesn't support PWM")
    test_pin.function = 'output'
    test_pin.frequency = 100
    with pytest.raises(ValueError):
        test_pin.state = 1.1

def test_duty_cycles(pins):
    test_pin, input_pin = pins
    if test_pin.__class__.__name__ == 'NativePin':
        pytest.skip("native pin doesn't support PWM")
    test_pin.function = 'output'
    test_pin.frequency = 100
    for duty_cycle in (0.0, 0.1, 0.5, 1.0):
        test_pin.state = duty_cycle
        assert test_pin.state == duty_cycle
        total = sum(input_pin.state for i in range(20000))
        assert isclose(total / 20000, duty_cycle, rel_tol=0.1, abs_tol=0.1)

