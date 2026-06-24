# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2024 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

from time import sleep
from unittest import mock

import pytest

from gpiozero.exc import (
    PinFixedPull,
    PinInvalidBounce,
    PinInvalidFunction,
    PinInvalidPin,
    PinInvalidPull,
    PinPWMUnsupported,
    PinSetInput,
)
from gpiozero.pins.sequent_microsystems import (
    MegaindFactory,
    MegaindOptoPin,
    MegaindPin,
    MultiIOAnalogInput,
    MultiIOAnalogPin,
    MultiIOFactory,
    MultiIOPin,
    MultiIORelay,
)

# test can be exercised without an actual I2C bus or board attached

@pytest.fixture()
def megaind_mod():
    with mock.patch('gpiozero.pins.sequent_microsystems.megaind') as m:
        m.getOpto.return_value = 0
        yield m

@pytest.fixture()
def multiio_mod():
    with mock.patch('gpiozero.pins.sequent_microsystems.SMmultiio') as cls:
        yield cls.return_value

@pytest.fixture()
def megaind_od(megaind_mod):
    factory = MegaindFactory(stack=0, pin_type='od')
    yield factory
    factory.close()

@pytest.fixture()
def megaind_opto(megaind_mod):
    factory = MegaindFactory(stack=0, pin_type='opto')
    yield factory
    factory.close()

@pytest.fixture()
def multiio_relay(multiio_mod):
    factory = MultiIOFactory(stack=0, pin_type='relay')
    yield factory
    factory.close()

@pytest.fixture()
def multiio_analog(multiio_mod):
    factory = MultiIOFactory(stack=0, pin_type='analog_in')
    yield factory
    factory.close()

# MegaindPin 

def test_megaind_pin_defaults(megaind_od):
    pin = megaind_od.pin(1)
    assert isinstance(pin, MegaindPin)
    assert pin.function == 'input'
    assert pin.frequency is None
    assert pin.state is False

def test_megaind_pin_digital_on_calls_setOd(megaind_od, megaind_mod):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    pin.state = 1
    megaind_mod.setOd.assert_called_with(0, 1, 1)
    pin.state = 0
    megaind_mod.setOd.assert_called_with(0, 1, 0)

def test_megaind_pin_input_raises_on_set_state(megaind_od):
    pin = megaind_od.pin(1)
    with pytest.raises(PinSetInput):
        pin.state = 1

def test_megaind_pin_pwm_calls_setOdPWM(megaind_od, megaind_mod):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    pin.frequency = 100
    pin.state = 0.5
    megaind_mod.setOdPWM.assert_called_with(0, 1, 50.0)


def test_megaind_pin_clearing_frequency_returns_to_digital(megaind_od, megaind_mod):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    pin.frequency = 100
    pin.state = 0.5
    pin.frequency = None
    megaind_mod.setOd.assert_called_with(0, 1, 0)
    assert pin.state is False


def test_megaind_pin_invalid_function(megaind_od):
    pin = megaind_od.pin(1)
    with pytest.raises(PinInvalidFunction):
        pin.function = 'bogus'


# MegaindOptoPin

def test_megaind_opto_pin_is_input_only(megaind_opto):
    pin = megaind_opto.pin(1)
    assert isinstance(pin, MegaindOptoPin)
    assert pin.function == 'input'
    with pytest.raises(PinInvalidFunction):
        pin.function = 'output'


def test_megaind_opto_pin_read_only(megaind_opto):
    pin = megaind_opto.pin(1)
    with pytest.raises(PinSetInput):
        pin.state = 1


def test_megaind_opto_pin_reads_bit_for_channel(megaind_opto, megaind_mod):
    megaind_mod.getOpto.return_value = 0b0101
    pin1 = megaind_opto.pin(1)
    pin2 = megaind_opto.pin(2)
    pin3 = megaind_opto.pin(3)
    assert pin1.state == 1
    assert pin2.state == 0
    assert pin3.state == 1


def test_megaind_opto_pin_fires_when_changed(megaind_opto, megaind_mod):
    pin = megaind_opto.pin(1)
    seen = []

    # when_changed is stored as a weak reference (see PiPin._set_when_changed)
    # so the callback must be kept alive by a local variable here, exactly as
    # gpiozero's own tests do (see test_mock_pin.py's "changed" function) --
    # an inline lambda would be garbage collected before the poll thread
    # ever gets to call it.
    def changed(ticks, state):
        seen.append(state)

    pin.when_changed = changed
    megaind_mod.getOpto.return_value = 1
    # The poll thread checks every POLL_INTERVAL (20ms); give it a few
    # cycles to notice the change and fire the callback.
    for _ in range(20):
        if seen:
            break
        sleep(0.02)
    assert seen == [True]
    pin.close()

# MultiIOPin

def test_multiio_pin_defaults(multiio_relay):
    pin = multiio_relay.pin(1)
    assert isinstance(pin, MultiIOPin)
    assert pin.function == 'input'
    assert pin.frequency is None

def test_multiio_pin_output_calls_set_relay(multiio_relay, multiio_mod):
    pin = multiio_relay.pin(1)
    pin.function = 'output'
    pin.state = 1
    multiio_mod.set_relay.assert_called_with(1, 1)
    pin.state = 0
    multiio_mod.set_relay.assert_called_with(1, 0)

def test_multiio_pin_input_raises_on_set_state(multiio_relay):
    pin = multiio_relay.pin(1)
    with pytest.raises(PinSetInput):
        pin.state = 1

def test_multiio_pin_no_pwm(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'output'
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100

# MultiIOAnalogPin

def test_multiio_analog_pin_is_input_only(multiio_analog):
    pin = multiio_analog.pin(1)
    assert isinstance(pin, MultiIOAnalogPin)
    assert pin.function == 'input'
    with pytest.raises(PinInvalidFunction):
        pin.function = 'output'

def test_multiio_analog_pin_reads_normalized_voltage(multiio_analog, multiio_mod):
    multiio_mod.get_u_in.return_value = 5.0
    pin = multiio_analog.pin(1)
    assert pin.state == 0.5

def test_multiio_analog_pin_read_only(multiio_analog):
    pin = multiio_analog.pin(1)
    with pytest.raises(PinSetInput):
        pin.state = 0.5

# Factories

def test_factory_invalid_pin_type(megaind_mod, multiio_mod):
    with pytest.raises(ValueError):
        MegaindFactory(stack=0, pin_type='bogus')
    with pytest.raises(ValueError):
        MultiIOFactory(stack=0, pin_type='bogus')


def test_factory_pin_is_cached(megaind_od):
    pin1 = megaind_od.pin(1)
    pin2 = megaind_od.pin(1)
    assert pin1 is pin2


def test_factory_pin_class_mismatch_raises(megaind_od):
    megaind_od.pin(1)
    with pytest.raises(ValueError):
        megaind_od.pin(1, pin_class=MegaindOptoPin)


def test_factory_default_pin_types(megaind_mod, multiio_mod):
    assert MegaindFactory(stack=0).pin_class is MegaindPin
    assert MegaindFactory(stack=0, pin_type='opto').pin_class is MegaindOptoPin
    assert MultiIOFactory(stack=0).pin_class is MultiIOPin
    assert MultiIOFactory(stack=0, pin_type='analog_in').pin_class is MultiIOAnalogPin


# MultiIOAnalogPin

def test_multiio_analog_pin_function_input_ok(multiio_analog):
    pin = multiio_analog.pin(1)
    pin.function = 'input'
    assert pin.function == 'input'


def test_multiio_analog_pin_no_pwm(multiio_analog):
    pin = multiio_analog.pin(1)
    assert pin.frequency is None
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100


def test_multiio_analog_pin_pull(multiio_analog):
    pin = multiio_analog.pin(1)
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.pull == 'up'
    with pytest.raises(PinInvalidPull):
        pin.pull = 'bogus'


def test_multiio_analog_pin_bounce_and_edges(multiio_analog):
    pin = multiio_analog.pin(1)
    assert pin.bounce is None
    pin.bounce = 0.1
    assert pin.bounce == 0.1
    assert pin.edges == 'both'
    pin.edges = 'rising'
    assert pin.edges == 'rising'


# MultiIOPin

def test_multiio_pin_function_roundtrip(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'output'
    assert pin.function == 'output'
    pin.function = 'input'
    assert pin.function == 'input'


def test_multiio_pin_state_getter(multiio_relay):
    pin = multiio_relay.pin(1)
    assert pin.state in (0, False)


def test_multiio_pin_no_pwm(multiio_relay):
    pin = multiio_relay.pin(1)
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100


def test_multiio_pin_pull_requires_input_function(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'output'
    with pytest.raises(PinFixedPull):
        pin.pull = 'up'


def test_multiio_pin_pull_invalid(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'input'
    with pytest.raises(PinInvalidPull):
        pin.pull = 'bogus'


def test_multiio_pin_pull_up_down_drives_state(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'input'
    pin.pull = 'up'
    assert pin.state is True
    pin.pull = 'down'
    assert pin.state is False


def test_multiio_pin_fixed_pull_resistor(multiio_relay):
    pin = multiio_relay.pin(2)
    pin.function = 'input'
    with pytest.raises(PinFixedPull):
        pin.pull = 'down'


def test_multiio_pin_bounce(multiio_relay):
    pin = multiio_relay.pin(1)
    assert pin.bounce is None
    pin.bounce = 0.1
    assert pin.bounce == 0.1
    with pytest.raises(PinInvalidBounce):
        pin.bounce = 'not-a-number'


def test_multiio_pin_edges(multiio_relay):
    pin = multiio_relay.pin(1)
    assert pin.edges == 'both'
    pin.edges = 'falling'
    assert pin.edges == 'falling'


def test_multiio_pin_drive_high_low_fire_when_changed(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'input'
    seen = []

    def changed(ticks, state):
        seen.append(state)

    pin.when_changed = changed
    pin.drive_high()
    assert pin.state is True
    assert seen == [True]
    # Driving the same state again must not re-fire (_change_state no-op).
    pin.drive_high()
    assert seen == [True]
    pin.drive_low()
    assert pin.state is False
    assert seen == [True, False]
    pin.close()


def test_multiio_pin_assert_states_helpers(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'input'
    pin.clear_states()
    pin.drive_high()
    pin.drive_low()
    pin.assert_states([False, True, False])
    pin.assert_states_and_times([(0.0, False), (0.0, True), (0.0, False)])


def test_multiio_pin_close(multiio_relay):
    pin = multiio_relay.pin(1)
    pin.function = 'output'
    pin.close()
    assert pin.function == 'input'


# MegaindPin

def test_megaind_pin_no_change_state_noop(megaind_od):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    assert pin._change_state(False) is False


def test_megaind_pin_pull_requires_input_function(megaind_od):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    with pytest.raises(PinFixedPull):
        pin.pull = 'up'


def test_megaind_pin_pull(megaind_od):
    pin = megaind_od.pin(1)
    pin.pull = 'up'
    assert pin.pull == 'up'
    with pytest.raises(PinInvalidPull):
        pin.pull = 'bogus'


def test_megaind_pin_bounce(megaind_od):
    pin = megaind_od.pin(1)
    assert pin.bounce is None
    pin.bounce = 0.1
    assert pin.bounce == 0.1
    with pytest.raises(PinInvalidBounce):
        pin.bounce = 'not-a-number'


def test_megaind_pin_edges(megaind_od):
    pin = megaind_od.pin(1)
    assert pin.edges == 'both'
    pin.edges = 'rising'
    assert pin.edges == 'rising'


def test_megaind_pin_event_detect_are_noops(megaind_od):
    pin = megaind_od.pin(1)
    pin.function = 'input'
    seen = []

    def changed(ticks, state):
        seen.append(state)

    # No hardware interrupt exists for a plain digital OD input, so these
    # are no-ops; assigning when_changed must not raise.
    pin.when_changed = changed
    pin.when_changed = None


def test_megaind_pin_close(megaind_od):
    pin = megaind_od.pin(1)
    pin.function = 'output'
    pin.close()
    assert pin.function == 'input'


# MegaindOptoPin

def test_megaind_opto_pin_function_input_ok(megaind_opto):
    pin = megaind_opto.pin(1)
    pin.function = 'input'
    assert pin.function == 'input'


def test_megaind_opto_pin_no_pwm(megaind_opto):
    pin = megaind_opto.pin(1)
    assert pin.frequency is None
    with pytest.raises(PinPWMUnsupported):
        pin.frequency = 100


def test_megaind_opto_pin_pull(megaind_opto):
    pin = megaind_opto.pin(1)
    assert pin.pull == 'floating'
    pin.pull = 'up'
    assert pin.pull == 'up'
    with pytest.raises(PinInvalidPull):
        pin.pull = 'bogus'


def test_megaind_opto_pin_bounce_and_edges(megaind_opto):
    pin = megaind_opto.pin(1)
    assert pin.bounce is None
    pin.bounce = 0.1
    assert pin.bounce == 0.1
    assert pin.edges == 'both'
    pin.edges = 'rising'
    assert pin.edges == 'rising'


def test_megaind_opto_pin_enable_event_detect_twice_is_noop(megaind_opto):
    pin = megaind_opto.pin(1)
    pin._enable_event_detect()
    thread = pin._poll_thread
    pin._enable_event_detect()  # already running: must not replace the thread
    assert pin._poll_thread is thread
    pin._disable_event_detect()


def test_megaind_opto_pin_disable_event_detect_without_enable_is_noop(megaind_opto):
    pin = megaind_opto.pin(1)
    assert pin._poll_thread is None
    pin._disable_event_detect()  # must not raise
    assert pin._poll_thread is None


def test_megaind_opto_pin_edges_none_suppresses_callback(megaind_opto, megaind_mod):
    pin = megaind_opto.pin(1)
    pin.edges = 'none'
    seen = []

    def changed(ticks, state):
        seen.append(state)

    pin.when_changed = changed
    megaind_mod.getOpto.return_value = 1
    sleep(0.1)  # several poll cycles: state changes internally but never fires
    assert seen == []
    assert pin.state == 1
    pin.close()


def test_megaind_opto_pin_no_change_keeps_polling(megaind_opto, megaind_mod):
    pin = megaind_opto.pin(1)
    seen = []

    def changed(ticks, state):
        seen.append(state)

    pin.when_changed = changed
    # Value never changes from the fixture default (0): the poll loop should
    # keep running (change_state() returning False each time) without firing.
    sleep(0.1)
    assert seen == []
    pin.close()


# Factories

def test_multiio_factory_reset(multiio_relay):
    multiio_relay.pin(1)
    assert len(multiio_relay.pins) == 1
    multiio_relay.reset()
    assert len(multiio_relay.pins) == 0


def test_multiio_factory_pin_explicit_class_match(multiio_relay):
    pin1 = multiio_relay.pin(1, pin_class=MultiIOPin)
    pin2 = multiio_relay.pin(1, pin_class=MultiIOPin)
    assert pin1 is pin2


def test_multiio_factory_pin_class_mismatch_raises(multiio_relay):
    multiio_relay.pin(1)
    with pytest.raises(ValueError):
        multiio_relay.pin(1, pin_class=MultiIOAnalogPin)


def test_multiio_factory_pin_invalid_name(multiio_relay):
    with pytest.raises(PinInvalidPin):
        multiio_relay.pin('not-a-real-pin-name')


def test_multiio_factory_relay_and_analog_in_wrappers(multiio_mod):
    factory = MultiIOFactory(stack=0)
    relay = factory.relay(channel=1)
    assert isinstance(relay, MultiIORelay)
    analog = factory.analog_in(channel=1)
    assert isinstance(analog, MultiIOAnalogInput)


def test_multiio_factory_ticks(multiio_relay):
    t1 = MultiIOFactory.ticks()
    t2 = MultiIOFactory.ticks()
    assert t2 >= t1
    assert MultiIOFactory.ticks_diff(t2, t1) >= 0


def test_megaind_factory_reset(megaind_od):
    megaind_od.pin(1)
    assert len(megaind_od.pins) == 1
    megaind_od.reset()
    assert len(megaind_od.pins) == 0


def test_megaind_factory_pin_invalid_name(megaind_od):
    with pytest.raises(PinInvalidPin):
        megaind_od.pin('not-a-real-pin-name')


def test_megaind_factory_ticks(megaind_od):
    t1 = MegaindFactory.ticks()
    t2 = MegaindFactory.ticks()
    assert t2 >= t1
    assert MegaindFactory.ticks_diff(t2, t1) >= 0


# MultiIOAnalogInput / MultiIORelay

def test_multiio_analog_input_wrapper(multiio_mod):
    multiio_mod.get_u_in.return_value = 7.5
    analog = MultiIOAnalogInput(stack=0, channel=1)
    assert analog.value == 0.75
    assert analog.volts == 7.5


def test_multiio_relay_wrapper(multiio_mod):
    relay = MultiIORelay(stack=0, channel=1)
    relay.on()
    multiio_mod.set_relay.assert_called_with(1, 1)
    relay.off()
    multiio_mod.set_relay.assert_called_with(1, 0)
