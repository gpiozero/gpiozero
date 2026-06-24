# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2026 Marie Sauzay <marie.c.sauzay@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
from time import sleep

import megaind
import pytest
from multiio import SMmultiio

from gpiozero.pins.sequent_microsystems import MegaindFactory, MultiIOFactory


# This module assumes a real Sequent Microsystems Megaind HAT and Multi-IO
# HAT are attached to the I2C bus, both at the stack address below (their
# address jumpers/switches set to 0, the factory default). Unlike
# test_real_pins.py this isn't a loopback between two pins: each test writes
# a real output channel and reads the same channel back through the vendor
# library directly, independently of gpiozero's own cached pin state.
STACK = int(os.environ.get('GPIOZERO_SEQUENT_STACK', '0'))
OD_CHANNEL = int(os.environ.get('GPIOZERO_SEQUENT_OD_CHANNEL', '1'))
RELAY_CHANNEL = int(os.environ.get('GPIOZERO_SEQUENT_RELAY_CHANNEL', '1'))

# Prevents two real-hardware runs from fighting over the same I2C bus, same
# idea as TEST_LOCK in test_real_pins.py
TEST_LOCK = os.environ.get('GPIOZERO_SEQUENT_TEST_LOCK', '/tmp/real_sequent_pins_lock')


def setup_module(module):
    from time import time
    start = time()
    while True:
        if time() - start > 60:
            raise RuntimeError('timed out waiting for real sequent pins lock')
        try:
            with open(TEST_LOCK, 'x') as f:
                f.write('Lock file for gpiozero real Sequent hardware tests; '
                        'delete this if the test suite is not currently running\n')
        except FileExistsError:
            print('Waiting for lock before testing real Sequent hardware')
            sleep(1)
        else:
            break


def teardown_module(module):
    os.unlink(TEST_LOCK)


def test_megaind_pin_od_matches_hardware_readback():
    factory = MegaindFactory(stack=STACK, pin_type='od')
    try:
        pin = factory.pin(OD_CHANNEL)
        pin.function = 'output'
        try:
            pin.state = 1
            sleep(0.1)
            assert megaind.getOd(STACK, OD_CHANNEL) == 1
            pin.state = 0
            sleep(0.1)
            assert megaind.getOd(STACK, OD_CHANNEL) == 0
        finally:
            pin.state = 0
    finally:
        factory.close()


def test_multiio_pin_relay_matches_hardware_readback():
    factory = MultiIOFactory(stack=STACK, pin_type='relay')
    card = SMmultiio(stack=STACK)
    try:
        pin = factory.pin(RELAY_CHANNEL)
        pin.function = 'output'
        try:
            pin.state = 1
            sleep(0.1)
            assert card.get_relay(RELAY_CHANNEL) == 1
            pin.state = 0
            sleep(0.1)
            assert card.get_relay(RELAY_CHANNEL) == 0
        finally:
            pin.state = 0
    finally:
        factory.close()
