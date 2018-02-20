from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import sys
import pytest
from time import sleep

from gpiozero import *
from gpiozero.pins.mock import MockPWMPin, MockPin


def setup_function(function):
    # dirty, but it does the job
    Device.pin_factory.pin_class = MockPWMPin if function.__name__ in (
        'test_robot',
        'test_phaseenable_robot',
        'test_ryanteck_robot',
        'test_camjam_kit_robot',
        'test_pololudrv8835_robot',
        'test_led_borg',
        'test_led_board_pwm_value',
        'test_led_board_pwm_bad_value',
        'test_snow_pi_initial_value_pwm',
        'test_led_board_pwm_initial_value',
        'test_led_board_pwm_bad_initial_value',
        'test_led_board_fade_background',
        'test_led_bar_graph_pwm_value',
        'test_led_bar_graph_pwm_initial_value',
        'test_statusboard_kwargs',
        'test_statuszero_kwargs',
        ) else MockPin

def teardown_function(function):
    Device.pin_factory.reset()

def teardown_module(module):
    # make sure we reset the default
    Device.pin_factory.pwm = False


def test_composite_output_on_off():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3), foo=OutputDevice(4)) as device:
        device.on()
        assert all((pin1.state, pin2.state, pin3.state))
        device.off()
        assert not any((pin1.state, pin2.state, pin3.state))

def test_composite_output_toggle():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3), foo=OutputDevice(4)) as device:
        device.toggle()
        assert all((pin1.state, pin2.state, pin3.state))
        device[0].off()
        device.toggle()
        assert pin1.state
        assert not pin2.state
        assert not pin3.state

def test_composite_output_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3), foo=OutputDevice(4)) as device:
        assert device.value == (0, 0, 0)
        device.toggle()
        assert device.value == (1, 1, 1)
        device.value = (1, 0, 1)
        assert device[0].is_active
        assert not device[1].is_active
        assert device[2].is_active

def test_led_board_on_off():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4) as board:
        assert isinstance(board[0], LED)
        assert isinstance(board[1], LED)
        assert isinstance(board[2], LED)
        assert board.active_high
        assert board[0].active_high
        assert board[1].active_high
        assert board[2].active_high
        board.on()
        assert all((pin1.state, pin2.state, pin3.state))
        board.off()
        assert not any((pin1.state, pin2.state, pin3.state))
        board[0].on()
        assert board.value == (1, 0, 0)
        assert pin1.state
        assert not pin2.state
        assert not pin3.state
        board.toggle()
        assert board.value == (0, 1, 1)
        assert not pin1.state
        assert pin2.state
        assert pin3.state
        board.toggle(0,1)
        assert board.value == (1, 0, 1)
        assert pin1.state
        assert not pin2.state
        assert pin3.state
        board.off(2)
        assert board.value == (1, 0, 0)
        assert pin1.state
        assert not pin2.state
        assert not pin3.state
        board.on(1)
        assert board.value == (1, 1, 0)
        assert pin1.state
        assert pin2.state
        assert not pin3.state
        board.off(0,1)
        assert board.value == (0, 0, 0)
        assert not pin1.state
        assert not pin2.state
        assert not pin3.state
        board.on(1,2)
        assert board.value == (0, 1, 1)
        assert not pin1.state
        assert pin2.state
        assert pin3.state
        board.toggle(0)
        assert board.value == (1, 1, 1)
        assert pin1.state
        assert pin2.state
        assert pin3.state

def test_led_board_active_low():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4, active_high=False) as board:
        assert not board.active_high
        assert not board[0].active_high
        assert not board[1].active_high
        assert not board[2].active_high
        board.on()
        assert not any ((pin1.state, pin2.state, pin3.state))
        board.off()
        assert all((pin1.state, pin2.state, pin3.state))
        board[0].on()
        assert board.value == (1, 0, 0)
        assert not pin1.state
        assert pin2.state
        assert pin3.state
        board.toggle()
        assert board.value == (0, 1, 1)
        assert pin1.state
        assert not pin2.state
        assert not pin3.state

def test_led_board_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4) as board:
        assert board.value == (0, 0, 0)
        board.value = (0, 1, 0)
        assert board.value == (0, 1, 0)
        board.value = (1, 0, 1)
        assert board.value == (1, 0, 1)

def test_led_board_pwm_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True) as board:
        assert board.value == (0, 0, 0)
        board.value = (0, 1, 0)
        assert board.value == (0, 1, 0)
        board.value = (0.5, 0, 0.75)
        assert board.value == (0.5, 0, 0.75)

def test_led_board_pwm_bad_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True) as board:
        with pytest.raises(ValueError):
            board.value = (-1, 0, 0)
        with pytest.raises(ValueError):
            board.value = (0, 2, 0)

def test_led_board_initial_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4, initial_value=0) as board:
        assert board.value == (0, 0, 0)
    with LEDBoard(2, 3, foo=4, initial_value=1) as board:
        assert board.value == (1, 1, 1)

def test_led_board_pwm_initial_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=0) as board:
        assert board.value == (0, 0, 0)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=1) as board:
        assert board.value == (1, 1, 1)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=0.5) as board:
        assert board.value == (0.5, 0.5, 0.5)

def test_led_board_pwm_bad_initial_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with pytest.raises(ValueError):
        LEDBoard(2, 3, foo=4, pwm=True, initial_value=-1)
    with pytest.raises(ValueError):
        LEDBoard(2, 3, foo=4, pwm=True, initial_value=2)

def test_led_board_nested():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, LEDBoard(3, 4)) as board:
        assert list(led.pin for led in board.leds) == [pin1, pin2, pin3]
        assert board.value == (0, (0, 0))
        board.value = (1, (0, 1))
        assert pin1.state
        assert not pin2.state
        assert pin3.state

def test_led_board_bad_blink():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBoard(2, LEDBoard(3, 4)) as board:
        with pytest.raises(ValueError):
            board.blink(fade_in_time=1, fade_out_time=1)
        with pytest.raises(ValueError):
            board.blink(fade_out_time=1)
        with pytest.raises(ValueError):
            board.pulse()

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_background():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        # Instantiation takes a long enough time that it throws off our timing
        # here!
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0.1, 0.1, n=2)
        board._blink_thread.join() # naughty, but ensures no arbitrary waits in the test
        test = [
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ]
        pin1.assert_states_and_times(test)
        pin2.assert_states_and_times(test)
        pin3.assert_states_and_times(test)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_foreground():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0.1, 0.1, n=2, background=False)
        test = [
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ]
        pin1.assert_states_and_times(test)
        pin2.assert_states_and_times(test)
        pin3.assert_states_and_times(test)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_control():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0.1, 0.1, n=2)
        # make sure the blink thread's started
        while not board._blink_leds:
            sleep(0.00001) # pragma: no cover
        board[1][0].off() # immediately take over the second LED
        board._blink_thread.join() # naughty, but ensures no arbitrary waits in the test
        test = [
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ]
        pin1.assert_states_and_times(test)
        pin3.assert_states_and_times(test)
        print(pin2.states)
        pin2.assert_states_and_times([(0.0, False), (0.0, True), (0.0, False)])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_take_over():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board[1].blink(0.1, 0.1, n=2)
        board.blink(0.1, 0.1, n=2) # immediately take over blinking
        board[1]._blink_thread.join()
        board._blink_thread.join()
        test = [
            (0.0, False),
            (0.0, True),
            (0.1, False),
            (0.1, True),
            (0.1, False)
            ]
        pin1.assert_states_and_times(test)
        pin2.assert_states_and_times(test)
        pin3.assert_states_and_times(test)

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_control_all():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0.1, 0.1, n=2)
        # make sure the blink thread's started
        while not board._blink_leds:
            sleep(0.00001) # pragma: no cover
        board[0].off() # immediately take over all LEDs
        board[1][0].off()
        board[1][1].off()
        board._blink_thread.join() # blink should terminate here anyway
        test = [
            (0.0, False),
            (0.0, True),
            (0.0, False),
            ]
        pin1.assert_states_and_times(test)
        pin2.assert_states_and_times(test)
        pin3.assert_states_and_times(test)

def test_led_board_blink_interrupt_on():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        board.blink(1, 0.1)
        sleep(0.2)
        board.off() # should interrupt while on
        pin1.assert_states([False, True, False])
        pin2.assert_states([False, True, False])
        pin3.assert_states([False, True, False])

def test_led_board_blink_interrupt_off():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0.1, 1)
        sleep(0.2)
        board.off() # should interrupt while off
        pin1.assert_states([False, True, False])
        pin2.assert_states([False, True, False])
        pin3.assert_states([False, True, False])

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_fade_background():
    pin1 = Device.pin_factory.pin(4)
    pin2 = Device.pin_factory.pin(5)
    pin3 = Device.pin_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6, pwm=True), pwm=True) as board:
        pin1.clear_states()
        pin2.clear_states()
        pin3.clear_states()
        board.blink(0, 0, 0.2, 0.2, n=2)
        board._blink_thread.join()
        test = [
            (0.0, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            (0.04, 0.2),
            (0.04, 0.4),
            (0.04, 0.6),
            (0.04, 0.8),
            (0.04, 1),
            (0.04, 0.8),
            (0.04, 0.6),
            (0.04, 0.4),
            (0.04, 0.2),
            (0.04, 0),
            ]
        pin1.assert_states_and_times(test)
        pin2.assert_states_and_times(test)
        pin3.assert_states_and_times(test)

def test_led_bar_graph_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4) as graph:
        assert isinstance(graph[0], LED)
        assert isinstance(graph[1], LED)
        assert isinstance(graph[2], LED)
        assert graph.active_high
        assert graph[0].active_high
        assert graph[1].active_high
        assert graph[2].active_high
        graph.value = 0
        assert graph.value == 0
        assert graph.lit_count == 0
        assert not any((pin1.state, pin2.state, pin3.state))
        graph.value = 1
        assert graph.value == 1
        assert graph.lit_count == 3
        assert all((pin1.state, pin2.state, pin3.state))
        graph.value = 1/3
        assert graph.value == 1/3
        assert graph.lit_count == 1
        assert pin1.state and not (pin2.state or pin3.state)
        graph.value = -1/3
        assert graph.value == -1/3
        assert graph.lit_count == -1
        assert pin3.state and not (pin1.state or pin2.state)
        pin1.state = True
        pin2.state = True
        assert graph.value == 1
        assert graph.lit_count == 3
        pin3.state = False
        assert graph.value == 2/3
        assert graph.lit_count == 2
        pin3.state = True
        pin1.state = False
        assert graph.value == -2/3
        graph.lit_count = 2
        assert graph.value == 2/3
        graph.lit_count = -1
        assert graph.value == -1/3
        graph.lit_count = -3
        assert graph.value == 1

def test_led_bar_graph_active_low():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4, active_high=False) as graph:
        assert not graph.active_high
        assert not graph[0].active_high
        assert not graph[1].active_high
        assert not graph[2].active_high
        graph.value = 0
        assert graph.value == 0
        assert all((pin1.state, pin2.state, pin3.state))
        graph.value = 1
        assert graph.value == 1
        assert not any((pin1.state, pin2.state, pin3.state))
        graph.value = 1/3
        assert graph.value == 1/3
        assert not pin1.state and pin2.state and pin3.state
        graph.value = -1/3
        assert graph.value == -1/3
        assert not pin3.state and pin1.state and pin2.state

def test_led_bar_graph_pwm_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4, pwm=True) as graph:
        assert isinstance(graph[0], PWMLED)
        assert isinstance(graph[1], PWMLED)
        assert isinstance(graph[2], PWMLED)
        graph.value = 0
        assert graph.value == 0
        assert graph.lit_count == 0
        assert not any((pin1.state, pin2.state, pin3.state))
        graph.value = 1
        assert graph.value == 1
        assert graph.lit_count == 3
        assert all((pin1.state, pin2.state, pin3.state))
        graph.value = 1/3
        assert graph.value == 1/3
        assert graph.lit_count == 1
        assert pin1.state and not (pin2.state or pin3.state)
        graph.value = -1/3
        assert graph.value == -1/3
        assert graph.lit_count == -1
        assert pin3.state and not (pin1.state or pin2.state)
        graph.value = 1/2
        assert graph.value == 1/2
        assert graph.lit_count == 1.5
        assert (pin1.state, pin2.state, pin3.state) == (1, 0.5, 0)
        pin1.state = 0
        pin3.state = 1
        assert graph.value == -1/2
        assert graph.lit_count == -1.5
        graph.lit_count = 1.5
        assert graph.value == 0.5

def test_led_bar_graph_bad_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4) as graph:
        with pytest.raises(ValueError):
            graph.value = -2
        with pytest.raises(ValueError):
            graph.value = 2
        with pytest.raises(ValueError):
            graph.lit_count = -4
        with pytest.raises(ValueError):
            graph.lit_count = 4

def test_led_bar_graph_bad_init():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with pytest.raises(TypeError):
        LEDBarGraph(2, 3, foo=4)
    with pytest.raises(ValueError):
        LEDBarGraph(2, 3, 4, initial_value=-2)
    with pytest.raises(ValueError):
        LEDBarGraph(2, 3, 4, initial_value=2)

def test_led_bar_graph_initial_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4, initial_value=1/3) as graph:
        assert graph.value == 1/3
        assert pin1.state and not (pin2.state or pin3.state)
    with LEDBarGraph(2, 3, 4, initial_value=-1/3) as graph:
        assert graph.value == -1/3
        assert pin3.state and not (pin1.state or pin2.state)

def test_led_bar_graph_pwm_initial_value():
    pin1 = Device.pin_factory.pin(2)
    pin2 = Device.pin_factory.pin(3)
    pin3 = Device.pin_factory.pin(4)
    with LEDBarGraph(2, 3, 4, pwm=True, initial_value=0.5) as graph:
        assert graph.value == 0.5
        assert (pin1.state, pin2.state, pin3.state) == (1, 0.5, 0)
    with LEDBarGraph(2, 3, 4, pwm=True, initial_value=-0.5) as graph:
        assert graph.value == -0.5
        assert (pin1.state, pin2.state, pin3.state) == (0, 0.5, 1)

def test_led_borg():
    pins = [Device.pin_factory.pin(n) for n in (17, 27, 22)]
    with LedBorg() as board:
        assert [device.pin for device in board._leds] == pins

def test_pi_liter():
    pins = [Device.pin_factory.pin(n) for n in (4, 17, 27, 18, 22, 23, 24, 25)]
    with PiLiter() as board:
        assert [device.pin for device in board] == pins

def test_pi_liter_graph():
    pins = [Device.pin_factory.pin(n) for n in (4, 17, 27, 18, 22, 23, 24, 25)]
    with PiLiterBarGraph() as board:
        board.value = 0.5
        assert [pin.state for pin in pins] == [1, 1, 1, 1, 0, 0, 0, 0]
        pins[4].state = 1
        assert board.value == 5/8

def test_traffic_lights():
    red_pin = Device.pin_factory.pin(2)
    amber_pin = Device.pin_factory.pin(3)
    green_pin = Device.pin_factory.pin(4)
    with TrafficLights(2, 3, 4) as board:
        board.red.on()
        assert board.red.value
        assert not board.amber.value
        assert not board.yellow.value
        assert not board.green.value
        assert red_pin.state
        assert not amber_pin.state
        assert not green_pin.state
        board.amber.on()
        assert amber_pin.state
        board.yellow.off()
        assert not amber_pin.state
    with TrafficLights(red=2, yellow=3, green=4) as board:
        board.yellow.on()
        assert not board.red.value
        assert board.amber.value
        assert board.yellow.value
        assert not board.green.value
        assert not red_pin.state
        assert amber_pin.state
        assert not green_pin.state
        board.amber.off()
        assert not amber_pin.state

def test_traffic_lights_bad_init():
    with pytest.raises(ValueError):
        TrafficLights()
    red_pin = Device.pin_factory.pin(2)
    amber_pin = Device.pin_factory.pin(3)
    green_pin = Device.pin_factory.pin(4)
    yellow_pin = Device.pin_factory.pin(5)
    with pytest.raises(ValueError):
        TrafficLights(red=2, amber=3, yellow=5, green=4)

def test_pi_traffic():
    pins = [Device.pin_factory.pin(n) for n in (9, 10, 11)]
    with PiTraffic() as board:
        assert [device.pin for device in board] == pins

def test_pi_stop():
    with pytest.raises(ValueError):
        PiStop()
    with pytest.raises(ValueError):
        PiStop('E')
    pins_a = [Device.pin_factory.pin(n) for n in (7, 8, 25)]
    with PiStop('A') as board:
        assert [device.pin for device in board] == pins_a
    pins_aplus = [Device.pin_factory.pin(n) for n in (21, 20, 16)]
    with PiStop('A+') as board:
        assert [device.pin for device in board] == pins_aplus
    pins_b = [Device.pin_factory.pin(n) for n in (10, 9, 11)]
    with PiStop('B') as board:
        assert [device.pin for device in board] == pins_b
    pins_bplus = [Device.pin_factory.pin(n) for n in (13, 19, 26)]
    with PiStop('B+') as board:
        assert [device.pin for device in board] == pins_bplus
    pins_c = [Device.pin_factory.pin(n) for n in (18, 15, 14)]
    with PiStop('C') as board:
        assert [device.pin for device in board] == pins_c
    pins_d = [Device.pin_factory.pin(n) for n in (2, 3, 4)]
    with PiStop('D') as board:
        assert [device.pin for device in board] == pins_d

def test_snow_pi():
    pins = [Device.pin_factory.pin(n) for n in (23, 24, 25, 17, 18, 22, 7, 8, 9)]
    with SnowPi() as board:
        assert [device.pin for device in board.leds] == pins

def test_snow_pi_initial_value():
    with SnowPi() as board:
        assert all(device.pin.state == False for device in board.leds)
    with SnowPi(initial_value=False) as board:
        assert all(device.pin.state == False for device in board.leds)
    with SnowPi(initial_value=True) as board:
        assert all(device.pin.state == True for device in board.leds)
    with SnowPi(initial_value=0.5) as board:
        assert all(device.pin.state == True for device in board.leds)

def test_snow_pi_initial_value_pwm():
    pins = [Device.pin_factory.pin(n) for n in (23, 24, 25, 17, 18, 22, 7, 8, 9)]
    with SnowPi(pwm=True, initial_value=0.5) as board:
        assert [device.pin for device in board.leds] == pins
        assert all(device.pin.state == 0.5 for device in board.leds)

def test_traffic_lights_buzzer():
    red_pin = Device.pin_factory.pin(2)
    amber_pin = Device.pin_factory.pin(3)
    green_pin = Device.pin_factory.pin(4)
    buzzer_pin = Device.pin_factory.pin(5)
    button_pin = Device.pin_factory.pin(6)
    with TrafficLightsBuzzer(
            TrafficLights(2, 3, 4),
            Buzzer(5),
            Button(6)) as board:
        board.lights.red.on()
        board.buzzer.on()
        assert red_pin.state
        assert not amber_pin.state
        assert not green_pin.state
        assert buzzer_pin.state
        button_pin.drive_low()
        assert board.button.is_active

def test_fish_dish():
    pins = [Device.pin_factory.pin(n) for n in (9, 22, 4, 8, 7)]
    with FishDish() as board:
        assert [led.pin for led in board.lights] + [board.buzzer.pin, board.button.pin] == pins

def test_traffic_hat():
    pins = [Device.pin_factory.pin(n) for n in (24, 23, 22, 5, 25)]
    with TrafficHat() as board:
        assert [led.pin for led in board.lights] + [board.buzzer.pin, board.button.pin] == pins

def test_robot():
    pins = [Device.pin_factory.pin(n) for n in (2, 3, 4, 5)]
    def check_pins_and_value(robot, expected_value):
        # Ensure both forward and back pins aren't both driven simultaneously
        assert pins[0].state == 0 or pins[1].state == 0
        assert pins[2].state == 0 or pins[3].state == 0
        assert robot.value == (pins[0].state - pins[1].state, pins[2].state - pins[3].state) == expected_value
    with Robot((2, 3), (4, 5)) as robot:
        assert (
            [device.pin for device in robot.left_motor] +
            [device.pin for device in robot.right_motor]) == pins
        check_pins_and_value(robot, (0, 0))
        robot.forward()
        check_pins_and_value(robot, (1, 1))
        robot.backward()
        check_pins_and_value(robot, (-1, -1))
        robot.forward(0)
        check_pins_and_value(robot, (0, 0))
        robot.forward(0.5)
        check_pins_and_value(robot, (0.5, 0.5))
        robot.forward(1)
        check_pins_and_value(robot, (1, 1))
        robot.forward(curve_right=0)
        check_pins_and_value(robot, (1, 1))
        robot.forward(curve_left=0)
        check_pins_and_value(robot, (1, 1))
        robot.forward(curve_left=0, curve_right=0)
        check_pins_and_value(robot, (1, 1))
        robot.forward(curve_right=1)
        check_pins_and_value(robot, (1, 0))
        robot.forward(curve_left=1)
        check_pins_and_value(robot, (0, 1))
        robot.forward(0.5, curve_right=1)
        check_pins_and_value(robot, (0.5, 0))
        robot.forward(0.5, curve_left=1)
        check_pins_and_value(robot, (0, 0.5))
        robot.forward(curve_right=0.5)
        check_pins_and_value(robot, (1, 0.5))
        robot.forward(curve_left=0.5)
        check_pins_and_value(robot, (0.5, 1))
        robot.forward(0.5, curve_right=0.5)
        check_pins_and_value(robot, (0.5, 0.25))
        robot.forward(0.5, curve_left=0.5)
        check_pins_and_value(robot, (0.25, 0.5))
        with pytest.raises(ValueError):
            robot.forward(-1)
        with pytest.raises(ValueError):
            robot.forward(2)
        with pytest.raises(ValueError):
            robot.forward(curve_left=-1)
        with pytest.raises(ValueError):
            robot.forward(curve_left=2)
        with pytest.raises(ValueError):
            robot.forward(curve_right=-1)
        with pytest.raises(ValueError):
            robot.forward(curve_right=2)
        with pytest.raises(ValueError):
            robot.forward(curve_left=1, curve_right=1)
        robot.backward()
        check_pins_and_value(robot, (-1, -1))
        robot.reverse()
        check_pins_and_value(robot, (1, 1))
        robot.backward(0)
        check_pins_and_value(robot, (0, 0))
        robot.backward(0.5)
        check_pins_and_value(robot, (-0.5, -0.5))
        robot.backward(1)
        check_pins_and_value(robot, (-1, -1))
        robot.backward(curve_right=0)
        check_pins_and_value(robot, (-1, -1))
        robot.backward(curve_left=0)
        check_pins_and_value(robot, (-1, -1))
        robot.backward(curve_left=0, curve_right=0)
        check_pins_and_value(robot, (-1, -1))
        robot.backward(curve_right=1)
        check_pins_and_value(robot, (-1, 0))
        robot.backward(curve_left=1)
        check_pins_and_value(robot, (0, -1))
        robot.backward(0.5, curve_right=1)
        check_pins_and_value(robot, (-0.5, 0))
        robot.backward(0.5, curve_left=1)
        check_pins_and_value(robot, (0, -0.5))
        robot.backward(curve_right=0.5)
        check_pins_and_value(robot, (-1, -0.5))
        robot.backward(curve_left=0.5)
        check_pins_and_value(robot, (-0.5, -1))
        robot.backward(0.5, curve_right=0.5)
        check_pins_and_value(robot, (-0.5, -0.25))
        robot.backward(0.5, curve_left=0.5)
        check_pins_and_value(robot, (-0.25, -0.5))
        with pytest.raises(ValueError):
            robot.backward(-1)
        with pytest.raises(ValueError):
            robot.backward(2)
        with pytest.raises(ValueError):
            robot.backward(curve_left=-1)
        with pytest.raises(ValueError):
            robot.backward(curve_left=2)
        with pytest.raises(ValueError):
            robot.backward(curve_right=-1)
        with pytest.raises(ValueError):
            robot.backward(curve_right=2)
        with pytest.raises(ValueError):
            robot.backward(curve_left=1, curve_right=1)
        with pytest.raises(TypeError):
            robot.forward(curveleft=1)
        with pytest.raises(TypeError):
            robot.forward(curveright=1)
        robot.left()
        check_pins_and_value(robot, (-1, 1))
        robot.left(0)
        check_pins_and_value(robot, (0, 0))
        robot.left(0.5)
        check_pins_and_value(robot, (-0.5, 0.5))
        robot.left(1)
        check_pins_and_value(robot, (-1, 1))
        with pytest.raises(ValueError):
            robot.left(-1)
        with pytest.raises(ValueError):
            robot.left(2)
        robot.right()
        check_pins_and_value(robot, (1, -1))
        robot.right(0)
        check_pins_and_value(robot, (0, 0))
        robot.right(0.5)
        check_pins_and_value(robot, (0.5, -0.5))
        robot.right(1)
        check_pins_and_value(robot, (1, -1))
        with pytest.raises(ValueError):
            robot.right(-1)
        with pytest.raises(ValueError):
            robot.right(2)
        robot.reverse()
        check_pins_and_value(robot, (-1, 1))
        robot.stop()
        check_pins_and_value(robot, (0, 0))
        robot.stop()
        check_pins_and_value(robot, (0, 0))
        robot.value = (-1, -1)
        check_pins_and_value(robot, (-1, -1))
        robot.value = (0.5, 1)
        check_pins_and_value(robot, (0.5, 1))
        robot.value = (0, -0.5)
        check_pins_and_value(robot, (0, -0.5))

def test_phaseenable_robot():
    pins = [Device.pin_factory.pin(n) for n in (5, 12, 6, 13)]
    with PhaseEnableRobot((5, 12), (6, 13)) as robot:
        assert (
            [device.pin for device in robot.left_motor] +
            [device.pin for device in robot.right_motor]) == pins
        assert robot.value == (0, 0)
        robot.forward()
        assert [pin.state for pin in pins] == [0, 1, 0, 1]
        assert robot.value == (1, 1)
        robot.backward()
        assert [pin.state for pin in pins] == [1, 1, 1, 1]
        assert robot.value == (-1, -1)
        robot.forward(0.5)
        assert [pin.state for pin in pins] == [0, 0.5, 0, 0.5]
        assert robot.value == (0.5, 0.5)
        robot.left()
        assert [pin.state for pin in pins] == [1, 1, 0, 1]
        assert robot.value == (-1, 1)
        robot.right()
        assert [pin.state for pin in pins] == [0, 1, 1, 1]
        assert robot.value == (1, -1)
        robot.reverse()
        assert [pin.state for pin in pins] == [1, 1, 0, 1]
        assert robot.value == (-1, 1)
        robot.stop()
        assert [pin.state for pin in pins][1::2] == [0, 0]
        assert robot.value == (0, 0)
        robot.value = (-1, -1)
        assert robot.value == (-1, -1)
        robot.value = (0.5, 1)
        assert robot.value == (0.5, 1)
        robot.value = (0, -0.5)
        assert robot.value == (0, -0.5)

def test_ryanteck_robot():
    pins = [Device.pin_factory.pin(n) for n in (17, 18, 22, 23)]
    with RyanteckRobot() as board:
        assert [device.pin for motor in board for device in motor] == pins

def test_camjam_kit_robot():
    pins = [Device.pin_factory.pin(n) for n in (9, 10, 7, 8)]
    with CamJamKitRobot() as board:
        assert [device.pin for motor in board for device in motor] == pins

def test_pololudrv8835_robot():
    pins = [Device.pin_factory.pin(n) for n in (5, 12, 6, 13)]
    with PololuDRV8835Robot() as board:
        assert [device.pin for motor in board for device in motor] == pins

def test_energenie_bad_init():
    with pytest.raises(ValueError):
        Energenie()
    with pytest.raises(ValueError):
        Energenie(0)
    with pytest.raises(ValueError):
        Energenie(5)

def test_energenie():
    pins = [Device.pin_factory.pin(n) for n in (17, 22, 23, 27, 24, 25)]
    with Energenie(1, initial_value=True) as device1, \
            Energenie(2, initial_value=False) as device2:
        assert repr(device1) == '<gpiozero.Energenie object on socket 1>'
        assert repr(device2) == '<gpiozero.Energenie object on socket 2>'
        assert device1.value
        assert not device2.value
        [pin.clear_states() for pin in pins]
        device1.on()
        assert device1.value
        pins[0].assert_states_and_times([(0.0, False), (0.0, True)])
        pins[1].assert_states_and_times([(0.0, True), (0.0, True)])
        pins[2].assert_states_and_times([(0.0, True), (0.0, True)])
        pins[3].assert_states_and_times([(0.0, False), (0.0, True)])
        pins[4].assert_states_and_times([(0.0, False)])
        pins[5].assert_states_and_times([(0.0, False), (0.1, True), (0.25, False)])
        [pin.clear_states() for pin in pins]
        device2.on()
        assert device2.value
        pins[0].assert_states_and_times([(0.0, True), (0.0, False)])
        pins[1].assert_states_and_times([(0.0, True), (0.0, True)])
        pins[2].assert_states_and_times([(0.0, True), (0.0, True)])
        pins[3].assert_states_and_times([(0.0, True), (0.0, True)])
        pins[4].assert_states_and_times([(0.0, False)])
        pins[5].assert_states_and_times([(0.0, False), (0.1, True), (0.25, False)])
        device1.close()
        assert repr(device1) == '<gpiozero.Energenie object closed>'

def test_statuszero_init():
    with StatusZero() as sz:
        assert sz.namedtuple._fields == ('one', 'two', 'three')
    with StatusZero('a') as sz:
        assert sz.namedtuple._fields == ('a',)
    with StatusZero('a', 'b') as sz:
        assert sz.namedtuple._fields == ('a', 'b')
    with StatusZero('a', 'b', 'c') as sz:
        assert sz.namedtuple._fields == ('a', 'b', 'c')
    with pytest.raises(ValueError):
        StatusZero('a', 'b', 'c', 'd')
    with pytest.raises(ValueError):
        StatusZero('0')
    with pytest.raises(ValueError):
        StatusZero('foo', 'hello world')
    with pytest.raises(ValueError):
        StatusZero('foo', 'foo')

def test_statuszero():
    with StatusZero() as sz:
        assert isinstance(sz.one, LEDBoard)
        assert isinstance(sz.two, LEDBoard)
        assert isinstance(sz.three, LEDBoard)
        assert isinstance(sz.one.red, LED)
        assert isinstance(sz.one.green, LED)
        assert sz.value == ((False, False), (False, False), (False, False))
        sz.on()
        assert sz.value == ((True, True), (True, True), (True, True))
        sz.one.green.off()
        assert sz.one.value == (True, False)

def test_statuszero_kwargs():
    with StatusZero(pwm=True, initial_value=True) as sz:
        assert isinstance(sz.one, LEDBoard)
        assert isinstance(sz.two, LEDBoard)
        assert isinstance(sz.three, LEDBoard)
        assert isinstance(sz.one.red, PWMLED)
        assert isinstance(sz.one.green, PWMLED)
        assert sz.value == ((1, 1), (1, 1), (1, 1))
        sz.off()
        assert sz.value == ((0, 0), (0, 0), (0, 0))

def test_statuszero_named():
    with StatusZero('a') as sz:
        assert isinstance(sz.a, LEDBoard)
        assert isinstance(sz.a.red, LED)
        with pytest.raises(AttributeError):
            sz.one

def test_statusboard_init():
    with StatusBoard() as sb:
        assert sb.namedtuple._fields == ('one', 'two', 'three', 'four', 'five')
    with StatusBoard('a') as sb:
        assert sb.namedtuple._fields == ('a',)
    with StatusBoard('a', 'b') as sb:
        assert sb.namedtuple._fields == ('a', 'b',)
    with StatusBoard('a', 'b', 'c', 'd', 'e') as sb:
        assert sb.namedtuple._fields == ('a', 'b', 'c', 'd', 'e')
    with pytest.raises(ValueError):
        StatusBoard('a', 'b', 'c', 'd', 'e', 'f')
    with pytest.raises(ValueError):
        StatusBoard('0')
    with pytest.raises(ValueError):
        StatusBoard('foo', 'hello world')
    with pytest.raises(ValueError):
        StatusBoard('foo', 'foo')

def test_statusboard():
    with StatusBoard() as sb:
        assert isinstance(sb.one, CompositeOutputDevice)
        assert isinstance(sb.two, CompositeOutputDevice)
        assert isinstance(sb.five, CompositeOutputDevice)
        assert isinstance(sb.one.button, Button)
        assert isinstance(sb.one.lights, LEDBoard)
        assert isinstance(sb.one.lights.red, LED)
        assert isinstance(sb.one.lights.green, LED)
        assert sb.value == ((False, (False, False)), (False, (False, False)),
                            (False, (False, False)), (False, (False, False)),
                            (False, (False, False)))
        sb.on()
        assert sb.value == ((False, (True, True)), (False, (True, True)),
                            (False, (True, True)), (False, (True, True)),
                            (False, (True, True)))
        sb.one.lights.green.off()
        assert sb.one.value == (False, (True, False))

def test_statusboard_kwargs():
    with StatusBoard(pwm=True, initial_value=True) as sb:
        assert isinstance(sb.one, CompositeOutputDevice)
        assert isinstance(sb.two, CompositeOutputDevice)
        assert isinstance(sb.five, CompositeOutputDevice)
        assert isinstance(sb.one.button, Button)
        assert isinstance(sb.one.lights, LEDBoard)
        assert isinstance(sb.one.lights.red, PWMLED)
        assert isinstance(sb.one.lights.green, PWMLED)
        assert sb.value == ((False, (1, 1)), (False, (1, 1)), (False, (1, 1)),
                           (False, (1, 1)), (False, (1, 1)))
        sb.off()
        assert sb.value == ((False, (0, 0)), (False, (0, 0)), (False, (0, 0)),
                            (False, (0, 0)), (False, (0, 0)))

def test_statusboard_named():
    with StatusBoard('a') as sb:
        assert isinstance(sb.a, CompositeOutputDevice)
        assert isinstance(sb.a.button, Button)
        assert isinstance(sb.a.lights, LEDBoard)
        assert isinstance(sb.a.lights.red, LED)
        with pytest.raises(AttributeError):
            sb.one
