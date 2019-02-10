# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
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
import errno
from time import time, sleep

import pytest
import pkg_resources

from gpiozero import *
from gpiozero.pins.mock import MockConnectedPin, MockFactory
from gpiozero.pins.native import NativeFactory
try:
    from math import isclose
except ImportError:
    from gpiozero.compat import isclose


# This module assumes you've wired the following GPIO pins together. The pins
# can be re-configured via the listed environment variables (useful for when
# your testing rig requires different pins because the defaults interfere with
# attached hardware).
TEST_PIN = int(os.environ.get('GPIOZERO_TEST_PIN', '22'))
INPUT_PIN = int(os.environ.get('GPIOZERO_TEST_INPUT_PIN', '27'))
TEST_LOCK = os.environ.get('GPIOZERO_TEST_LOCK', '/tmp/real_pins_lock')


@pytest.fixture(
    scope='module',
    params=[
        name
        for name in pkg_resources.\
            get_distribution('gpiozero').\
            get_entry_map('gpiozero_pin_factories').keys()
        if not name.endswith('Pin') # leave out compatibility names
    ])
def pin_factory_name(request):
    return request.param

@pytest.yield_fixture()
def pin_factory(request, pin_factory_name):
    try:
        factory = pkg_resources.load_entry_point(
            'gpiozero', 'gpiozero_pin_factories', pin_factory_name)()
    except Exception as e:
        pytest.skip("skipped factory %s: %s" % (pin_factory_name, str(e)))
    else:
        yield factory
        factory.close()

@pytest.yield_fixture()
def default_factory(request, pin_factory):
    save_pin_factory = Device.pin_factory
    Device.pin_factory = pin_factory
    yield pin_factory
    Device.pin_factory = save_pin_factory

@pytest.yield_fixture(scope='function')
def pins(request, pin_factory):
    # Why return both pins in a single fixture? If we defined one fixture for
    # each pin then pytest will (correctly) test RPiGPIOPin(22) against
    # NativePin(27) and so on. This isn't supported, so we don't test it
    input_pin = pin_factory.pin(INPUT_PIN)
    input_pin.function = 'input'
    input_pin.pull = 'down'
    if isinstance(pin_factory, MockFactory):
        test_pin = pin_factory.pin(TEST_PIN, pin_class=MockConnectedPin, input_pin=input_pin)
    else:
        test_pin = pin_factory.pin(TEST_PIN)
    yield test_pin, input_pin
    test_pin.close()
    input_pin.close()


def setup_module(module):
    # Python 2.7 compatible method of exclusive-open
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    start = time()
    while True:
        if time() - start > 300:  # 5 minute timeout
            raise RuntimeError('timed out waiting for real pins lock')
        try:
            fd = os.open(TEST_LOCK, flags)
        except OSError as e:
            if e.errno == errno.EEXIST:
                print('Waiting for lock before testing real-pins')
                sleep(0.1)
            else:
                raise
        else:
            with os.fdopen(fd, 'w') as f:
                f.write('Lock file for gpiozero real-pin tests; delete '
                        'this if the test suite is not currently running\n')
            break

def teardown_module(module):
    os.unlink(TEST_LOCK)


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

def test_explicit_factory(no_default_factory, pin_factory):
    with GPIODevice(TEST_PIN, pin_factory=pin_factory) as device:
        assert Device.pin_factory is None
        assert device.pin_factory is pin_factory
        assert device.pin.number == TEST_PIN

def test_envvar_factory(no_default_factory, pin_factory_name):
    os.environ['GPIOZERO_PIN_FACTORY'] = pin_factory_name
    assert Device.pin_factory is None
    try:
        device = GPIODevice(TEST_PIN)
    except Exception as e:
        pytest.skip("skipped factory %s: %s" % (pin_factory_name, str(e)))
    else:
        try:
            group = 'gpiozero_pin_factories'
            for factory in pkg_resources.iter_entry_points(group, pin_factory_name):
                factory_class = factory.load()
            assert isinstance(Device.pin_factory, factory_class)
            assert device.pin_factory is Device.pin_factory
            assert device.pin.number == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()

def test_compatibility_names(no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'NATIVE'
    try:
        device = GPIODevice(TEST_PIN)
    except Exception as e:
        pytest.skip("skipped factory %s: %s" % (pin_factory_name, str(e)))
    else:
        try:
            assert isinstance(Device.pin_factory, NativeFactory)
            assert device.pin_factory is Device.pin_factory
            assert device.pin.number == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()

def test_bad_factory(no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'foobarbaz'
    # Waits for someone to implement the foobarbaz pin factory just to
    # mess with our tests ...
    with pytest.raises(BadPinFactory):
        GPIODevice(TEST_PIN)

def test_default_factory(no_default_factory):
    assert Device.pin_factory is None
    os.environ.pop('GPIOZERO_PIN_FACTORY', None)
    try:
        device = GPIODevice(TEST_PIN)
    except Exception as e:
        pytest.skip("no default factories")
    else:
        try:
            assert device.pin_factory is Device.pin_factory
            assert device.pin.number == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()
