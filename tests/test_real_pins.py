# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2024 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2020 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import errno
import warnings
from time import time, sleep
from math import isclose
from unittest import mock

# NOTE: Remove try when compatibility moves beyond Python 3.10
try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points

import pytest

from gpiozero import *
from gpiozero.pins.mock import MockConnectedPin, MockFactory, MockSPIDevice
from gpiozero.pins.native import NativeFactory
from gpiozero.pins.local import LocalPiFactory, LocalPiHardwareSPI


# This module assumes you've wired the following GPIO pins together. The pins
# can be re-configured via the listed environment variables (useful for when
# your testing rig requires different pins because the defaults interfere with
# attached hardware). Please note that the name specified *must* be the primary
# name of the pin, e.g. GPIO22 rather than an alias like BCM22 or 22 (several
# tests rely upon this).
TEST_PIN = os.environ.get('GPIOZERO_TEST_PIN', 'GPIO22')
INPUT_PIN = os.environ.get('GPIOZERO_TEST_INPUT_PIN', 'GPIO27')

# The lock path is intended to prevent parallel runs of the "real pins" test
# suite. For example, if you are testing multiple Python versions under tox,
# the mocked devices will all happily test in parallel. However, the real pins
# test must not or you risk one run trying to set a pin to an output while
# another simultaneously demands it's an input. The path specified here must be
# visible and accessible to all simultaneous runs.
TEST_LOCK = os.environ.get('GPIOZERO_TEST_LOCK', '/tmp/real_pins_lock')


def local_only():
    if not isinstance(Device.pin_factory, LocalPiFactory):
        pytest.skip("Test cannot run with non-local pin factories")

def local_hardware_spi_only(intf):
    if not isinstance(intf, LocalPiHardwareSPI):
        pytest.skip("Test assumes LocalPiHardwareSPI descendant")


with warnings.catch_warnings():
    @pytest.fixture(
        scope='module',
        params=[ep.name for ep in entry_points(group='gpiozero_pin_factories')])
    def pin_factory_name(request):
        return request.param


@pytest.fixture()
def pin_factory(request, pin_factory_name):
    try:
        with warnings.catch_warnings():
            eps = entry_points(group='gpiozero_pin_factories')
        for ep in eps:
            if ep.name == pin_factory_name:
                factory = ep.load()()
                break
        else:
            assert False, 'internal error'
    except Exception as e:
        pytest.skip("skipped factory {pin_factory_name}: {e!s}".format(
            pin_factory_name=pin_factory_name, e=e))
    else:
        yield factory
        factory.close()


@pytest.fixture()
def default_factory(request, pin_factory):
    save_pin_factory = Device.pin_factory
    Device.pin_factory = pin_factory
    yield pin_factory
    Device.pin_factory = save_pin_factory


@pytest.fixture(scope='function')
def pins(request, pin_factory):
    # Why return both pins in a single fixture? If we defined one fixture for
    # each pin then pytest will (correctly) test RPiGPIOPin(22) against
    # NativePin(27) and so on. This isn't supported, so we don't test it
    assert not (
        {INPUT_PIN, TEST_PIN} & {
            'GPIO2',
            'GPIO3',
            'GPIO7',
            'GPIO8',
            'GPIO9',
            'GPIO10',
            'GPIO11',
        }), 'Cannot use SPI (7-11) or I2C (2-3) pins for tests'
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
    start = time()
    while True:
        if time() - start > 300:  # 5 minute timeout
            raise RuntimeError('timed out waiting for real pins lock')
        try:
            with open(TEST_LOCK, 'x') as f:
                f.write('Lock file for gpiozero real-pin tests; delete '
                        'this if the test suite is not currently running\n')
        except FileExistsError:
            print('Waiting for lock before testing real-pins')
            sleep(1)
        else:
            break


def teardown_module(module):
    os.unlink(TEST_LOCK)


def test_pin_names(pins):
    test_pin, input_pin = pins
    assert test_pin.info.name == TEST_PIN
    assert input_pin.info.name == INPUT_PIN


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
    input_pin.pull = 'floating'
    test_pin.function = 'input'
    test_pin.pull = 'up'
    assert test_pin.state == 1
    assert input_pin.state == 1
    test_pin.pull = 'down'
    assert test_pin.state == 0
    assert input_pin.state == 0


def test_pull_bad(pins):
    test_pin, input_pin = pins
    test_pin.function = 'input'
    with pytest.raises(PinInvalidPull):
        test_pin.pull = 'foo'
    with pytest.raises(PinInvalidPull):
        test_pin.input_with_pull('foo')


def test_pull_down_warning(pin_factory):
    with pin_factory.pin('GPIO2') as pin:
        if pin.info.pull != 'up':
            pytest.skip("GPIO2 isn't pulled up on this pi")
        with pytest.raises(PinFixedPull):
            pin.pull = 'down'
        with pytest.raises(PinFixedPull):
            pin.input_with_pull('down')


def test_input_with_pull(pins):
    test_pin, input_pin = pins
    input_pin.pull = 'floating'
    test_pin.input_with_pull('up')
    assert test_pin.state == 1
    assert input_pin.state == 1
    test_pin.input_with_pull('down')
    assert test_pin.state == 0
    assert input_pin.state == 0


def test_pulls_are_weak(pins):
    test_pin, input_pin = pins
    test_pin.function = 'output'
    for pull in ('floating', 'down', 'up'):
        input_pin.pull = pull
        test_pin.state = 0
        assert input_pin.state == 0
        test_pin.state = 1
        assert input_pin.state == 1


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
        pytest.skip("{test_pin.factory!r} doesn't support PWM".format(
            test_pin=test_pin))
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
        pytest.skip("{test_pin.factory!r} doesn't support PWM".format(
            test_pin=test_pin))
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
        assert device.pin.info.name == TEST_PIN


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_envvar_factory(no_default_factory, pin_factory_name):
    os.environ['GPIOZERO_PIN_FACTORY'] = pin_factory_name
    assert Device.pin_factory is None
    try:
        device = GPIODevice(TEST_PIN)
    except Exception as e:
        pytest.skip("skipped factory {pin_factory_name}: {e!s}".format(
            pin_factory_name=pin_factory_name, e=e))
    else:
        try:
            group = entry_points(group='gpiozero_pin_factories')
            for ep in group:
                if ep.name == pin_factory_name:
                    factory_class = ep.load()
                    break
            else:
                assert False, 'internal error'
            assert isinstance(Device.pin_factory, factory_class)
            assert device.pin_factory is Device.pin_factory
            assert device.pin.info.name == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()


def test_compatibility_names(no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'NATIVE'
    try:
        device = GPIODevice(TEST_PIN)
    except Exception as e:
        pytest.skip("skipped factory {pin_factory_name}: {e!s}".format(
            pin_factory_name=pin_factory_name, e=e))
    else:
        try:
            assert isinstance(Device.pin_factory, NativeFactory)
            assert device.pin_factory is Device.pin_factory
            assert device.pin.info.name == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()


def test_bad_factory(no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'foobarbaz'
    # Waits for someone to implement the foobarbaz pin factory just to
    # mess with our tests ...
    with pytest.raises(BadPinFactory):
        GPIODevice(TEST_PIN)


@pytest.mark.filterwarnings('ignore::gpiozero.exc.PinFactoryFallback')
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
            assert device.pin.info.name == TEST_PIN
        finally:
            device.close()
            Device.pin_factory.close()


def test_spi_init(pin_factory):
    with pin_factory.spi() as intf:
        assert isinstance(intf, SPI)
        assert repr(intf) in (
            "SPI(clock_pin='GPIO11', mosi_pin='GPIO10', miso_pin='GPIO9', "
            "select_pin='GPIO8')",
            "SPI(port=0, device=0)"
        )
        intf.close()
        assert intf.closed
        assert repr(intf) == 'SPI(closed)'
    with pin_factory.spi(port=0, device=1) as intf:
        assert repr(intf) in (
            "SPI(clock_pin='GPIO11', mosi_pin='GPIO10', miso_pin='GPIO9', "
            "select_pin='GPIO7')",
            "SPI(port=0, device=1)"
        )
    with pin_factory.spi(clock_pin=11, mosi_pin=10, select_pin=8) as intf:
        assert repr(intf) in (
            "SPI(clock_pin='GPIO11', mosi_pin='GPIO10', miso_pin='GPIO9', "
            "select_pin='GPIO8')",
            "SPI(port=0, device=0)"
        )
    # Ensure we support "partial" SPI where we don't reserve a pin because
    # the device wants it for general IO (see SPI screens which use a pin
    # for data/commands)
    with pin_factory.spi(clock_pin=11, mosi_pin=10, miso_pin=None, select_pin=7) as intf:
        assert isinstance(intf, SPI)
    with pin_factory.spi(clock_pin=11, mosi_pin=None, miso_pin=9, select_pin=7) as intf:
        assert isinstance(intf, SPI)
    with pin_factory.spi(shared=True) as intf:
        assert isinstance(intf, SPI)
    with pytest.raises(ValueError):
        pin_factory.spi(port=1)
    with pytest.raises(ValueError):
        pin_factory.spi(device=2)
    with pytest.raises(ValueError):
        pin_factory.spi(port=0, clock_pin=12)
    with pytest.raises(ValueError):
        pin_factory.spi(foo='bar')


def test_spi_hardware_conflict(default_factory):
    with LED(11) as led:
        with pytest.raises(GPIOPinInUse):
            Device.pin_factory.spi(port=0, device=0)
    with Device.pin_factory.spi(port=0, device=0) as spi:
        with pytest.raises(GPIOPinInUse):
            LED(11)


def test_spi_hardware_same_port(default_factory):
    with Device.pin_factory.spi(device=0) as intf:
        local_hardware_spi_only(intf)
        with pytest.raises(GPIOPinInUse):
            Device.pin_factory.spi(device=0)
        with Device.pin_factory.spi(device=1) as another_intf:
            assert intf._port == another_intf._port


def test_spi_hardware_shared_bus(default_factory):
    with Device.pin_factory.spi(device=0, shared=True) as intf:
        with Device.pin_factory.spi(device=0, shared=True) as another_intf:
            assert intf is another_intf


def test_spi_hardware_read(default_factory):
    local_only()
    with mock.patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with Device.pin_factory.spi() as intf:
            local_hardware_spi_only(intf)
            assert intf.read(3) == [0, 1, 2]
            assert intf.read(6) == list(range(6))


def test_spi_hardware_write(default_factory):
    local_only()
    with mock.patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.xfer2.side_effect = lambda data: list(range(10))[:len(data)]
        with Device.pin_factory.spi() as intf:
            local_hardware_spi_only(intf)
            assert intf.write([0, 1, 2]) == 3
            assert spidev.return_value.xfer2.called_with([0, 1, 2])
            assert intf.write(list(range(6))) == 6
            assert spidev.return_value.xfer2.called_with(list(range(6)))


def test_spi_hardware_modes(default_factory):
    local_only()
    with mock.patch('gpiozero.pins.local.SpiDev') as spidev:
        spidev.return_value.mode = 0
        spidev.return_value.lsbfirst = False
        spidev.return_value.cshigh = True
        spidev.return_value.bits_per_word = 8
        with Device.pin_factory.spi() as intf:
            local_hardware_spi_only(intf)
            assert intf.clock_mode == 0
            assert not intf.clock_polarity
            assert not intf.clock_phase
            intf.clock_polarity = False
            assert intf.clock_mode == 0
            intf.clock_polarity = True
            assert intf.clock_mode == 2
            intf.clock_phase = True
            assert intf.clock_mode == 3
            assert not intf.lsb_first
            assert intf.select_high
            assert intf.bits_per_word == 8
            intf.select_high = False
            intf.lsb_first = True
            intf.bits_per_word = 12
            assert not spidev.return_value.cshigh
            assert spidev.return_value.lsbfirst
            assert spidev.return_value.bits_per_word == 12
            intf.rate = 1000000
            assert intf.rate == 1000000
            intf.rate = 500000
            assert intf.rate == 500000


# XXX Test two simultaneous SPI devices sharing clock, MOSI, and MISO, with
# separate select pins (including threaded tests which attempt simultaneous
# reading/writing)
