# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2017-2020 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2018 SteveAmor <steveamor@users.noreply.github.com>
# Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
# Copyright (c) 2016 Ian Harcombe <ian.harcombe@gmail.com>
# Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
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


import sys
import pytest
from time import sleep
from threading import Event

from gpiozero import *


def test_composite_output_on_off(mock_factory):
    pins = [mock_factory.pin(n) for n in (2, 3, 4)]
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3),
                               foo=OutputDevice(4)) as device:
        assert repr(device).startswith('<gpiozero.CompositeOutputDevice object')
        device.on()
        assert all(pin.state for pin in pins)
        device.off()
        assert not any(pin.state for pin in pins)

def test_composite_output_toggle(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3),
                               foo=OutputDevice(4)) as device:
        device.toggle()
        assert all((pin1.state, pin2.state, pin3.state))
        device[0].off()
        device.toggle()
        assert pin1.state
        assert not pin2.state
        assert not pin3.state

def test_composite_output_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with CompositeOutputDevice(OutputDevice(2), OutputDevice(3),
                               foo=OutputDevice(4)) as device:
        assert device.value == (0, 0, 0)
        device.toggle()
        assert device.value == (1, 1, 1)
        device.value = (1, 0, 1)
        assert device[0].is_active
        assert not device[1].is_active
        assert device[2].is_active

def test_button_board_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        ButtonBoard()
    with pytest.raises(GPIOPinMissing):
        ButtonBoard(hold_repeat=True)

def test_button_board_init(mock_factory):
    pins = [mock_factory.pin(n) for n in (2, 3, 4)]
    with ButtonBoard(2, 3, 4) as board:
        assert repr(board).startswith('<gpiozero.ButtonBoard object')
        assert len(board) == 3
        assert isinstance(board[0], Button)
        assert isinstance(board[1], Button)
        assert isinstance(board[2], Button)
        assert [b.pin for b in board] == pins

def test_button_board_pressed_released(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
    with ButtonBoard(4, 5, foo=6) as board:
        assert isinstance(board[0], Button)
        assert isinstance(board[1], Button)
        assert isinstance(board[2], Button)
        assert board.pull_up
        assert board[0].pull_up
        assert board[1].pull_up
        assert board[2].pull_up
        assert board.value == (False, False, False)
        assert board.wait_for_release(1)
        assert not board.is_active
        pin1.drive_low()
        pin3.drive_low()
        assert board.value == (True, False, True)
        assert board.wait_for_press(1)
        assert board.is_active
        pin3.drive_high()
        assert board.value == (True, False, False)
        assert board.is_active

def test_button_board_when_pressed(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
    evt = Event()
    evt1 = Event()
    evt2 = Event()
    evt3 = Event()
    with ButtonBoard(4, 5, foo=6) as board:
        board.when_changed = evt.set
        board[0].when_pressed = evt1.set
        board[1].when_pressed = evt2.set
        board[2].when_pressed = evt3.set
        pin1.drive_low()
        assert evt.wait(1)
        assert evt1.wait(1)
        assert not evt2.wait(0)
        assert not evt3.wait(0)
        evt.clear()
        evt1.clear()
        pin1.drive_high()
        assert evt.wait(1)
        evt.clear()
        pin2.drive_low()
        assert evt.wait(1)
        assert evt2.wait(1)
        assert not evt1.wait(0)
        assert not evt3.wait(0)

def test_led_collection_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        LEDCollection()
    with pytest.raises(GPIOPinMissing):
        LEDCollection(pwm=True)

def test_led_collection_init(mock_factory):
    pins = [mock_factory.pin(n) for n in (2, 3, 4)]
    with LEDCollection(2, 3, 4) as board:
        assert repr(board).startswith('<gpiozero.LEDCollection object')
        assert len(board) == 3
        assert isinstance(board[0], LED)
        assert isinstance(board[1], LED)
        assert isinstance(board[2], LED)
        assert [b.pin for b in board] == pins

def test_led_board_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        LEDBoard()
    with pytest.raises(GPIOPinMissing):
        LEDBoard(pwm=True)

def test_led_board_pwm_init(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (2, 3, 4)]
    with LEDBoard(2, 3, 4, pwm=True) as board:
        assert repr(board).startswith('<gpiozero.LEDBoard object')
        assert len(board) == 3
        assert isinstance(board[0], PWMLED)
        assert isinstance(board[1], PWMLED)
        assert isinstance(board[2], PWMLED)
        assert [b.pin for b in board] == pins

def test_led_board_on_off(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4) as board:
        assert repr(board).startswith('<gpiozero.LEDBoard object')
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

def test_led_board_active_low(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
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

def test_led_board_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4) as board:
        assert board.value == (0, 0, 0)
        board.value = (0, 1, 0)
        assert board.value == (0, 1, 0)
        board.value = (1, 0, 1)
        assert board.value == (1, 0, 1)

def test_led_board_pwm_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True) as board:
        assert board.value == (0, 0, 0)
        board.value = (0, 1, 0)
        assert board.value == (0, 1, 0)
        board.value = (0.5, 0, 0.75)
        assert board.value == (0.5, 0, 0.75)

def test_led_board_pwm_bad_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True) as board:
        with pytest.raises(ValueError):
            board.value = (-1, 0, 0)
        with pytest.raises(ValueError):
            board.value = (0, 2, 0)

def test_led_board_initial_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4, initial_value=0) as board:
        assert board.value == (0, 0, 0)
    with LEDBoard(2, 3, foo=4, initial_value=1) as board:
        assert board.value == (1, 1, 1)

def test_led_board_pwm_initial_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=0) as board:
        assert board.value == (0, 0, 0)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=1) as board:
        assert board.value == (1, 1, 1)
    with LEDBoard(2, 3, foo=4, pwm=True, initial_value=0.5) as board:
        assert board.value == (0.5, 0.5, 0.5)

def test_led_board_pwm_bad_initial_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with pytest.raises(ValueError):
        LEDBoard(2, 3, foo=4, pwm=True, initial_value=-1)
    with pytest.raises(ValueError):
        LEDBoard(2, 3, foo=4, pwm=True, initial_value=2)

def test_led_board_nested(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, LEDBoard(3, 4)) as board:
        assert list(led.pin for led in board.leds) == [pin1, pin2, pin3]
        assert board.value == (0, (0, 0))
        board.value = (1, (0, 1))
        assert pin1.state
        assert not pin2.state
        assert pin3.state

def test_led_board_bad_blink(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBoard(2, LEDBoard(3, 4)) as board:
        with pytest.raises(ValueError):
            board.blink(fade_in_time=1, fade_out_time=1)
        with pytest.raises(ValueError):
            board.blink(fade_out_time=1)
        with pytest.raises(ValueError):
            board.pulse()

@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason='timing is too random on pypy')
def test_led_board_blink_background(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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
def test_led_board_blink_foreground(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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
def test_led_board_blink_control(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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
def test_led_board_blink_take_over(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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
def test_led_board_blink_control_all(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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

def test_led_board_blink_interrupt_on(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
    with LEDBoard(4, LEDBoard(5, 6)) as board:
        board.blink(1, 0.1)
        sleep(0.2)
        board.off() # should interrupt while on
        pin1.assert_states([False, True, False])
        pin2.assert_states([False, True, False])
        pin3.assert_states([False, True, False])

def test_led_board_blink_interrupt_off(mock_factory):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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
def test_led_board_fade_background(mock_factory, pwm):
    pin1 = mock_factory.pin(4)
    pin2 = mock_factory.pin(5)
    pin3 = mock_factory.pin(6)
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

def test_led_bar_graph_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBarGraph(2, 3, 4) as graph:
        assert repr(graph).startswith('<gpiozero.LEDBarGraph object')
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

def test_led_bar_graph_active_low(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
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

def test_led_bar_graph_pwm_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    pins = (pin1, pin2, pin3)
    with LEDBarGraph(2, 3, 4, pwm=True) as graph:
        assert repr(graph).startswith('<gpiozero.LEDBarGraph object')
        assert isinstance(graph[0], PWMLED)
        assert isinstance(graph[1], PWMLED)
        assert isinstance(graph[2], PWMLED)
        graph.value = 0
        assert graph.value == 0
        assert graph.lit_count == 0
        assert not any(pin.state for pin in pins)
        graph.value = 1
        assert graph.value == 1
        assert graph.lit_count == 3
        assert all(pin.state for pin in pins)
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

def test_led_bar_graph_bad_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBarGraph(2, 3, 4) as graph:
        with pytest.raises(ValueError):
            graph.value = -2
        with pytest.raises(ValueError):
            graph.value = 2
        with pytest.raises(ValueError):
            graph.lit_count = -4
        with pytest.raises(ValueError):
            graph.lit_count = 4

def test_led_bar_graph_bad_init(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with pytest.raises(GPIOPinMissing):
        LEDBarGraph()
    with pytest.raises(GPIOPinMissing):
        LEDBarGraph(pwm=True)
    with pytest.raises(TypeError):
        LEDBarGraph(2, 3, foo=4)
    with pytest.raises(ValueError):
        LEDBarGraph(2, 3, 4, initial_value=-2)
    with pytest.raises(ValueError):
        LEDBarGraph(2, 3, 4, initial_value=2)
    with pytest.raises(ValueError):
        LEDBarGraph(2, LEDBoard(3, 4))

def test_led_bar_graph_initial_value(mock_factory):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBarGraph(2, 3, 4, initial_value=1/3) as graph:
        assert graph.value == 1/3
        assert pin1.state and not (pin2.state or pin3.state)
    with LEDBarGraph(2, 3, 4, initial_value=-1/3) as graph:
        assert graph.value == -1/3
        assert pin3.state and not (pin1.state or pin2.state)

def test_led_bar_graph_pwm_initial_value(mock_factory, pwm):
    pin1 = mock_factory.pin(2)
    pin2 = mock_factory.pin(3)
    pin3 = mock_factory.pin(4)
    with LEDBarGraph(2, 3, 4, pwm=True, initial_value=0.5) as graph:
        assert graph.value == 0.5
        assert (pin1.state, pin2.state, pin3.state) == (1, 0.5, 0)
    with LEDBarGraph(2, 3, 4, pwm=True, initial_value=-0.5) as graph:
        assert graph.value == -0.5
        assert (pin1.state, pin2.state, pin3.state) == (0, 0.5, 1)

def test_led_borg(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (17, 27, 22)]
    with LedBorg() as board:
        assert repr(board).startswith('<gpiozero.LedBorg object')
        assert [device.pin for device in board._leds] == pins

def test_pi_liter(mock_factory):
    pins = [mock_factory.pin(n) for n in (4, 17, 27, 18, 22, 23, 24, 25)]
    with PiLiter() as board:
        assert repr(board).startswith('<gpiozero.PiLiter object')
        assert [device.pin for device in board] == pins

def test_pi_liter_graph(mock_factory):
    pins = [mock_factory.pin(n) for n in (4, 17, 27, 18, 22, 23, 24, 25)]
    with PiLiterBarGraph() as board:
        assert repr(board).startswith('<gpiozero.PiLiterBarGraph object')
        board.value = 0.5
        assert [pin.state for pin in pins] == [1, 1, 1, 1, 0, 0, 0, 0]
        pins[4].state = 1
        assert board.value == 5/8

def test_traffic_lights(mock_factory):
    red_pin = mock_factory.pin(2)
    amber_pin = mock_factory.pin(3)
    green_pin = mock_factory.pin(4)
    with TrafficLights(2, 3, 4) as board:
        assert repr(board).startswith('<gpiozero.TrafficLights object')
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

def test_traffic_lights_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        TrafficLights()
    with pytest.raises(GPIOPinMissing):
        TrafficLights(2)
    with pytest.raises(GPIOPinMissing):
        TrafficLights(2, 3)
    red_pin = mock_factory.pin(2)
    amber_pin = mock_factory.pin(3)
    green_pin = mock_factory.pin(4)
    yellow_pin = mock_factory.pin(5)
    with pytest.raises(ValueError):
        TrafficLights(red=2, amber=3, yellow=5, green=4)

def test_pi_traffic(mock_factory):
    pins = [mock_factory.pin(n) for n in (9, 10, 11)]
    with PiTraffic() as board:
        assert repr(board).startswith('<gpiozero.PiTraffic object')
        assert [device.pin for device in board] == pins

def test_pi_stop_bad_init(mock_factory):
    with pytest.raises(ValueError):
        PiStop()
    with pytest.raises(ValueError):
        PiStop('E')

def test_pi_stop(mock_factory):
    pins_a = [mock_factory.pin(n) for n in (7, 8, 25)]
    with PiStop('A') as board:
        assert repr(board).startswith('<gpiozero.PiStop object')
        assert [device.pin for device in board] == pins_a
    pins_aplus = [mock_factory.pin(n) for n in (21, 20, 16)]
    with PiStop('A+') as board:
        assert [device.pin for device in board] == pins_aplus
    pins_b = [mock_factory.pin(n) for n in (10, 9, 11)]
    with PiStop('B') as board:
        assert [device.pin for device in board] == pins_b
    pins_bplus = [mock_factory.pin(n) for n in (13, 19, 26)]
    with PiStop('B+') as board:
        assert [device.pin for device in board] == pins_bplus
    pins_c = [mock_factory.pin(n) for n in (18, 15, 14)]
    with PiStop('C') as board:
        assert [device.pin for device in board] == pins_c
    pins_d = [mock_factory.pin(n) for n in (2, 3, 4)]
    with PiStop('D') as board:
        assert [device.pin for device in board] == pins_d

def test_snow_pi(mock_factory):
    pins = [mock_factory.pin(n) for n in (23, 24, 25, 17, 18, 22, 7, 8, 9)]
    with SnowPi() as board:
        assert repr(board).startswith('<gpiozero.SnowPi object')
        assert [device.pin for device in board.leds] == pins

def test_snow_pi_initial_value(mock_factory):
    with SnowPi() as board:
        assert all(device.pin.state == False for device in board.leds)
    with SnowPi(initial_value=False) as board:
        assert all(device.pin.state == False for device in board.leds)
    with SnowPi(initial_value=True) as board:
        assert all(device.pin.state == True for device in board.leds)
    with SnowPi(initial_value=0.5) as board:
        assert all(device.pin.state == True for device in board.leds)

def test_snow_pi_initial_value_pwm(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (23, 24, 25, 17, 18, 22, 7, 8, 9)]
    with SnowPi(pwm=True, initial_value=0.5) as board:
        assert [device.pin for device in board.leds] == pins
        assert all(device.pin.state == 0.5 for device in board.leds)

def test_pihut_xmas_tree(mock_factory):
    led_pins = (2, 4, 15, 13, 21, 25, 8, 5, 10, 16, 17, 27, 26,
                24, 9, 12, 6, 20, 19, 14, 18, 11, 7, 23, 22)
    pins = [mock_factory.pin(n) for n in led_pins]
    with PiHutXmasTree() as tree:
        assert repr(tree).startswith('<gpiozero.PiHutXmasTree object')
        assert [led.pin for led in tree.leds] == pins
        assert len(tree) == 25
        assert isinstance(tree.star, LED)
        assert isinstance(tree.led1, LED)
        assert isinstance(tree.led24, LED)

def test_pihut_xmas_tree_init(mock_factory):
    with PiHutXmasTree(pwm=False) as tree:
        assert isinstance(tree.star, LED)
        assert isinstance(tree.led1, LED)
        assert isinstance(tree.led24, LED)
    with PiHutXmasTree(initial_value=True) as tree:
        assert all(led.value for led in tree)

def test_pihut_xmas_tree_pwm(mock_factory, pwm):
    with PiHutXmasTree(pwm=True) as tree:
        assert isinstance(tree.star, PWMLED)
        assert isinstance(tree.led1, PWMLED)
        assert isinstance(tree.led24, PWMLED)
    with PiHutXmasTree(pwm=True, initial_value=0.5) as tree:
        assert all(led.value == 0.5 for led in tree)

def test_pihut_xmas_tree_leds(mock_factory):
    with PiHutXmasTree() as tree:
        tree.star.on()
        assert sum(tree.value) == 1
        tree.led1.on()
        assert sum(tree.value) == 2
        tree.on()
        assert sum(tree.value) == 25
        tree.off()
        assert sum(tree.value) == 0
        tree.toggle()
        assert sum(tree.value) == 25

def test_traffic_lights_buzzer(mock_factory):
    red_pin = mock_factory.pin(2)
    amber_pin = mock_factory.pin(3)
    green_pin = mock_factory.pin(4)
    buzzer_pin = mock_factory.pin(5)
    button_pin = mock_factory.pin(6)
    with TrafficLightsBuzzer(
            TrafficLights(2, 3, 4),
            Buzzer(5),
            Button(6)) as board:
        assert repr(board).startswith('<gpiozero.TrafficLightsBuzzer object')
        board.lights.red.on()
        board.buzzer.on()
        assert red_pin.state
        assert not amber_pin.state
        assert not green_pin.state
        assert buzzer_pin.state
        button_pin.drive_low()
        assert board.button.is_active
        board.toggle()
        assert not red_pin.state
        assert amber_pin.state
        assert green_pin.state
        assert not buzzer_pin.state
        assert board.value == ((0, 1, 1), 0, 1)
        board.value = ((0, 0, 0), 1, 0)
        assert not red_pin.state
        assert not amber_pin.state
        assert not green_pin.state
        assert buzzer_pin.state

def test_fish_dish(mock_factory):
    pins = [mock_factory.pin(n) for n in (9, 22, 4, 8, 7)]
    with FishDish() as board:
        assert repr(board).startswith('<gpiozero.FishDish object')
        assert ([led.pin for led in board.lights] +
                [board.buzzer.pin, board.button.pin]) == pins

def test_traffic_hat(mock_factory):
    pins = [mock_factory.pin(n) for n in (24, 23, 22, 5, 25)]
    with TrafficHat() as board:
        assert repr(board).startswith('<gpiozero.TrafficHat object')
        assert ([led.pin for led in board.lights] +
                [board.buzzer.pin, board.button.pin]) == pins

def test_traffic_phat(mock_factory):
    pins = [mock_factory.pin(n) for n in (25, 24, 23)]
    with TrafficpHat() as board:
        assert repr(board).startswith('<gpiozero.TrafficpHat object')
        assert ([led.pin for led in board]) == pins

def test_robot_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        Robot()
    with pytest.raises(GPIOPinMissing):
        Robot(2)
    with pytest.raises(GPIOPinMissing):
        Robot(2, 3)
    with pytest.raises(GPIOPinMissing):
        Robot(2, 3, 4)
    with pytest.raises(GPIOPinMissing):
        Robot(2, 3, 4, 5)
    with pytest.raises(GPIOPinMissing):
        Robot(2, 3, 4, 5, 6, 7)
    with pytest.raises(GPIOPinMissing):
        Robot((2, 3))
    with pytest.raises(GPIOPinMissing):
        Robot((2, 3), 4)

def test_robot(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (2, 3, 4, 5)]
    def check_pins_and_value(robot, expected_value):
        # Ensure both forward and back pins aren't both driven simultaneously
        assert pins[0].state == 0 or pins[1].state == 0
        assert pins[2].state == 0 or pins[3].state == 0
        assert robot.value == (
            pins[0].state - pins[1].state, pins[2].state - pins[3].state
        ) == expected_value
    with Robot((2, 3), (4, 5)) as robot:
        assert repr(robot).startswith('<gpiozero.Robot object')
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
            robot.backward(curveleft=1)
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

def test_robots(mock_factory, pwm):
    with RyanteckRobot() as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert isinstance(left_motor.forward_device, PWMOutputDevice)
        assert isinstance(left_motor.backward_device, PWMOutputDevice)
        assert isinstance(right_motor, Motor)
        assert isinstance(right_motor.forward_device, PWMOutputDevice)
        assert isinstance(right_motor.backward_device, PWMOutputDevice)

    with CamJamKitRobot() as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert isinstance(left_motor.forward_device, PWMOutputDevice)
        assert isinstance(left_motor.backward_device, PWMOutputDevice)
        assert isinstance(right_motor, Motor)
        assert isinstance(right_motor.forward_device, PWMOutputDevice)
        assert isinstance(right_motor.backward_device, PWMOutputDevice)

    with PololuDRV8835Robot() as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, PhaseEnableMotor)
        assert isinstance(left_motor.phase_device, DigitalOutputDevice)
        assert isinstance(left_motor.enable_device, PWMOutputDevice)
        assert isinstance(right_motor, PhaseEnableMotor)
        assert isinstance(right_motor.phase_device, DigitalOutputDevice)
        assert isinstance(right_motor.enable_device, PWMOutputDevice)

def test_robot_nopwm(mock_factory):
    pins = [mock_factory.pin(n) for n in (2, 3, 4, 5)]
    with Robot((2, 3), (4, 5), pwm=False) as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert left_motor.forward_device.pin is pins[0]
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert left_motor.backward_device.pin is pins[1]
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert isinstance(right_motor, Motor)
        assert right_motor.forward_device.pin is pins[2]
        assert isinstance(right_motor.forward_device, DigitalOutputDevice)
        assert right_motor.backward_device.pin is pins[3]
        assert isinstance(right_motor.backward_device, DigitalOutputDevice)

def test_robots_nopwm(mock_factory):
    pins = [mock_factory.pin(n) for n in (17, 18, 22, 23)]
    with RyanteckRobot(pwm=False) as robot:
        assert repr(robot).startswith('<gpiozero.RyanteckRobot object')
        assert [device.pin for motor in robot for device in motor] == pins
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert isinstance(left_motor.backward_device, DigitalOutputDevice)
        assert isinstance(right_motor, Motor)
        assert isinstance(right_motor.forward_device, DigitalOutputDevice)
        assert isinstance(right_motor.backward_device, DigitalOutputDevice)

    pins = [mock_factory.pin(n) for n in (9, 10, 7, 8)]
    with CamJamKitRobot(pwm=False) as robot:
        assert repr(robot).startswith('<gpiozero.CamJamKitRobot object')
        assert [device.pin for motor in robot for device in motor] == pins
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert isinstance(left_motor.backward_device, DigitalOutputDevice)
        assert isinstance(right_motor, Motor)
        assert isinstance(right_motor.forward_device, DigitalOutputDevice)
        assert isinstance(right_motor.backward_device, DigitalOutputDevice)

    pins = [mock_factory.pin(n) for n in (5, 12, 6, 13)]
    with PololuDRV8835Robot(pwm=False) as robot:
        assert repr(robot).startswith('<gpiozero.PololuDRV8835Robot object')
        assert [device.pin for motor in robot for device in motor] == pins
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, PhaseEnableMotor)
        assert isinstance(left_motor.phase_device, DigitalOutputDevice)
        assert isinstance(left_motor.enable_device, DigitalOutputDevice)
        assert isinstance(right_motor, PhaseEnableMotor)
        assert isinstance(right_motor.phase_device, DigitalOutputDevice)
        assert isinstance(right_motor.enable_device, DigitalOutputDevice)

def test_enable_pin_motor_robot(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (2, 3, 4, 5, 6, 7)]
    with Robot((2, 3, 4), (5, 6, 7)) as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert left_motor.forward_device.pin is pins[0]
        assert isinstance(left_motor.forward_device, PWMOutputDevice)
        assert left_motor.backward_device.pin is pins[1]
        assert isinstance(left_motor.forward_device, PWMOutputDevice)
        assert left_motor.enable_device.pin is pins[2]
        assert isinstance(left_motor.enable_device, DigitalOutputDevice)
        assert isinstance(right_motor, Motor)
        assert right_motor.forward_device.pin is pins[3]
        assert isinstance(right_motor.forward_device, PWMOutputDevice)
        assert right_motor.backward_device.pin is pins[4]
        assert isinstance(right_motor.backward_device, PWMOutputDevice)
        assert right_motor.enable_device.pin is pins[5]
        assert isinstance(right_motor.enable_device, DigitalOutputDevice)

def test_enable_pin_motor_robot_nopwm(mock_factory):
    pins = [mock_factory.pin(n) for n in (2, 3, 4, 5, 6, 7)]
    with Robot((2, 3, 4), (5, 6, 7), pwm=False) as robot:
        left_motor, right_motor = robot.all
        assert isinstance(left_motor, Motor)
        assert left_motor.forward_device.pin is pins[0]
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert left_motor.backward_device.pin is pins[1]
        assert isinstance(left_motor.forward_device, DigitalOutputDevice)
        assert left_motor.enable_device.pin is pins[2]
        assert isinstance(left_motor.enable_device, OutputDevice)
        assert isinstance(right_motor, Motor)
        assert right_motor.forward_device.pin is pins[3]
        assert isinstance(right_motor.forward_device, DigitalOutputDevice)
        assert right_motor.backward_device.pin is pins[4]
        assert isinstance(right_motor.backward_device, DigitalOutputDevice)
        assert right_motor.enable_device.pin is pins[5]
        assert isinstance(right_motor.enable_device, DigitalOutputDevice)

def test_phaseenable_robot_bad_init(mock_factory):
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot()
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot(2)
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot(2, 3)
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot(2, 3, 4)
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot(2, 3, 4, 5)
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot(2, 3, 4, 5, 6, 7)
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot((2, 3))
    with pytest.raises(GPIOPinMissing):
        PhaseEnableRobot((2, 3), 4)

def test_phaseenable_robot(mock_factory, pwm):
    pins = [mock_factory.pin(n) for n in (5, 12, 6, 13)]
    with PhaseEnableRobot((5, 12), (6, 13)) as robot:
        assert repr(robot).startswith('<gpiozero.PhaseEnableRobot object')
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

def test_energenie_bad_init(mock_factory):
    with pytest.raises(ValueError):
        Energenie()
    with pytest.raises(ValueError):
        Energenie(0)
    with pytest.raises(ValueError):
        Energenie(5)
    with pytest.raises(ValueError):
        Energenie(1, initial_value=None)

def test_energenie(mock_factory):
    pins = [mock_factory.pin(n) for n in (17, 22, 23, 27, 24, 25)]
    with Energenie(1, initial_value=True) as device1, \
         Energenie(2, initial_value=False) as device2:
        assert repr(device1) == '<gpiozero.Energenie object on socket 1>'
        assert repr(device2) == '<gpiozero.Energenie object on socket 2>'
        assert device1.value
        assert not device2.value
        assert device1.socket == 1
        assert device2.socket == 2
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

def test_statuszero_init(mock_factory):
    with StatusZero() as sz:
        assert repr(sz).startswith('<gpiozero.StatusZero object')
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

def test_statuszero(mock_factory):
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

def test_statuszero_kwargs(mock_factory, pwm):
    with StatusZero(pwm=True, initial_value=True) as sz:
        assert isinstance(sz.one, LEDBoard)
        assert isinstance(sz.two, LEDBoard)
        assert isinstance(sz.three, LEDBoard)
        assert isinstance(sz.one.red, PWMLED)
        assert isinstance(sz.one.green, PWMLED)
        assert sz.value == ((1, 1), (1, 1), (1, 1))
        sz.off()
        assert sz.value == ((0, 0), (0, 0), (0, 0))

def test_statuszero_named(mock_factory):
    with StatusZero('a') as sz:
        assert isinstance(sz.a, LEDBoard)
        assert isinstance(sz.a.red, LED)
        with pytest.raises(AttributeError):
            sz.one

def test_statusboard_init(mock_factory):
    with StatusBoard() as sb:
        assert repr(sb).startswith('<gpiozero.StatusBoard object')
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

def test_statusboard(mock_factory):
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

def test_statusboard_kwargs(mock_factory, pwm):
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

def test_statusboard_named(mock_factory):
    with StatusBoard('a') as sb:
        assert isinstance(sb.a, CompositeOutputDevice)
        assert isinstance(sb.a.button, Button)
        assert isinstance(sb.a.lights, LEDBoard)
        assert isinstance(sb.a.lights.red, LED)
        with pytest.raises(AttributeError):
            sb.one

def test_pumpkin_pi(mock_factory):
    pins = [mock_factory.pin(n)
            for n in (12, 6, 18, 17, 16, 13, 24, 19, 20, 21, 22, 23)]
    with PumpkinPi() as board:
        assert repr(board).startswith('<gpiozero.PumpkinPi object')
        assert [device.pin for device in board.leds] == pins
        assert isinstance(board.sides.left, LEDBoard)
        assert isinstance(board.sides.right, LEDBoard)
        assert isinstance(board.sides, LEDBoard)
        assert isinstance(board.eyes, LEDBoard)
        board.off()
        assert board.value == (
            (False, False), (
                (False, False, False, False, False),
                (False, False, False, False, False)
            )
        )
        board.eyes.on()
        assert board.value == (
            (True, True), (
                (False, False, False, False, False),
                (False, False, False, False, False)
            )
        )
        board.sides.left.middle.on()
        assert board.value == (
            (True, True), (
                (False, False, True, False, False),
                (False, False, False, False, False)
            )
        )
        board.sides.right.midtop.on()
        assert board.value == (
            (True, True), (
                (False, False, True, False, False),
                (False, False, False, True, False)
            )
        )
        board.toggle()
        assert board.value == (
            (False, False), (
                (True, True, False, True, True),
                (True, True, True, False, True)
            )
        )

def test_pumpkin_pi_initial_value(mock_factory):
    with PumpkinPi() as board:
        assert not any(device.pin.state for device in board.leds)
    with PumpkinPi(initial_value=False) as board:
        assert not any(device.pin.state for device in board.leds)
    with PumpkinPi(initial_value=True) as board:
        assert all(device.pin.state for device in board.leds)
    with PumpkinPi(initial_value=0.5) as board:
        assert all(device.pin.state for device in board.leds)

def test_pumpkin_pi_initial_value_pwm(mock_factory, pwm):
    with PumpkinPi(pwm=True, initial_value=0.5) as board:
        assert all(device.pin.state == 0.5 for device in board.leds)

def test_jamhat(mock_factory, pwm):
    with JamHat() as jh:
        assert repr(jh).startswith('<gpiozero.JamHat object')
        assert isinstance(jh.lights_1, LEDBoard)
        assert isinstance(jh.lights_2, LEDBoard)
        assert isinstance(jh.button_1, Button)
        assert isinstance(jh.button_2, Button)
        assert isinstance(jh.buzzer, TonalBuzzer)
        assert isinstance(jh.lights_1.red, LED)
        assert jh.value == (
            (False, False, False),  # lights_1
            (False, False, False),  # lights_2
            False, False,           # buttons
            None                    # buzzer
        )
        jh.on()
        assert jh.value == (
            (True, True, True),  # lights_1
            (True, True, True),  # lights_2
            False, False,        # buttons
            0                    # buzzer
        )
        jh.buzzer.play('A5')
        jh.button_1.pin.drive_high()
        jh.button_2.pin.drive_high()
        assert jh.value == (
            (True, True, True),  # lights_1
            (True, True, True),  # lights_2
            True, True,          # buttons
            1                    # buzzer
        )
        jh.off()
        assert jh.value == (
            (False, False, False),  # lights_1
            (False, False, False),  # lights_2
            True, True,             # buttons
            None                    # buzzer
        )

def test_jamhat_pwm(mock_factory, pwm):
    with JamHat(pwm=True) as jh:
        assert isinstance(jh.lights_1, LEDBoard)
        assert isinstance(jh.lights_1.red, PWMLED)
        assert isinstance(jh.lights_2, LEDBoard)
        assert isinstance(jh.button_1, Button)
        assert isinstance(jh.button_2, Button)
        assert isinstance(jh.buzzer, TonalBuzzer)
        assert jh.value == (
            (0, 0, 0),              # lights_1
            (0, 0, 0),              # lights_2
            False, False,           # buttons
            None                    # buzzer
        )
        jh.on()
        assert jh.value == (
            (1, 1, 1),           # lights_1
            (1, 1, 1),           # lights_2
            False, False,        # buttons
            0                    # buzzer
        )
        jh.off()
        assert jh.value == (
            (0, 0, 0),              # lights_1
            (0, 0, 0),              # lights_2
            False, False,           # buttons
            None                    # buzzer
        )

def test_pibrella(mock_factory, pwm):
    with Pibrella() as pb:
        assert repr(pb).startswith('<gpiozero.Pibrella object')
        assert isinstance(pb.lights, TrafficLights)
        assert isinstance(pb.lights.red, LED)
        assert isinstance(pb.button, Button)
        assert isinstance(pb.buzzer, TonalBuzzer)
        assert pb.inputs == (9, 7, 8, 10)
        assert pb.outputs == (22, 23, 24, 25)
        assert pb.value == (
            (0, 0, 0),  # lights
            0,          # button
            None        # buzzer
        )
        pb.on()
        assert pb.value == (
            (1, 1, 1),  # lights
            0,          # button
            0           # buzzer
        )
        pb.buzzer.play('A5')
        pb.button.pin.drive_high()
        assert pb.value == (
            (1, 1, 1),  # lights
            1,          # button
            1           # buzzer
        )
        pb.off()
        assert pb.value == (
            (0, 0, 0),  # lights
            1,          # button
            None        # buzzer
        )

def test_pibrella_pwm(mock_factory, pwm):
    with Pibrella(pwm=True) as pb:
        assert isinstance(pb.lights, TrafficLights)
        assert isinstance(pb.lights.red, PWMLED)
        assert isinstance(pb.button, Button)
        assert isinstance(pb.buzzer, TonalBuzzer)
        assert pb.inputs == (9, 7, 8, 10)
        assert pb.outputs == (22, 23, 24, 25)
        assert pb.value == (
            (0, 0, 0),  # lights
            0,          # button
            None        # buzzer
        )
        pb.on()
        assert pb.value == (
            (1, 1, 1),  # lights
            0,          # button
            0           # buzzer
        )
        pb.off()
        assert pb.value == (
            (0, 0, 0),  # lights
            0,          # button
            None        # buzzer
        )

def test_pibrella_pins(mock_factory, pwm):
    with Pibrella() as pb:
        with LED(pb.outputs.e) as led:
            assert isinstance(led, LED)
            assert led.pin.number == 22
        with Button(pb.inputs.a) as btn:
            assert btn.pin.number == 9
