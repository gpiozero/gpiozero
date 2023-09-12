# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2019-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import pytest
import warnings
from threading import Event, Thread

from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPWMPin


# NOTE: Work-around for python versions <3.4: in these versions the
# resetwarnings function in the warnings module doesn't do much (or doesn't do
# what most would expect). Warnings that have already been triggered still
# won't be re-triggered even after the call. To work-around this we set the
# default filter to "always" on these versions before running any tests. Note
# that this does mean you should run resetwarnings() whenever using
# catch_warnings()
if sys.version_info[:2] < (3, 4):
    warnings.simplefilter('always')

@pytest.fixture()
def no_default_factory(request):
    save_pin_factory = Device.pin_factory
    Device.pin_factory = None
    try:
        yield None
    finally:
        Device.pin_factory = save_pin_factory

@pytest.fixture(scope='function')
def mock_factory(request):
    save_factory = Device.pin_factory
    Device.pin_factory = MockFactory()
    try:
        yield Device.pin_factory
        # This reset() may seem redundant given we're re-constructing the
        # factory for each function that requires it but MockFactory (via
        # LocalFactory) stores some info at the class level which reset()
        # clears.
    finally:
        if Device.pin_factory is not None:
            Device.pin_factory.reset()
        Device.pin_factory = save_factory

@pytest.fixture()
def pwm(request, mock_factory):
    mock_factory.pin_class = MockPWMPin

class ThreadedTest(Thread):
    def __init__(self, test_fn, *args, **kwargs):
        self._fn = test_fn
        self._args = args
        self._kwargs = kwargs
        self._result = None
        super().__init__(daemon=True)
        self.start()

    def run(self):
        self._result = self._fn(*self._args, **self._kwargs)

    @property
    def result(self):
        self.join(10)
        if not self.is_alive():
            return self._result
        else:
            raise RuntimeError('test thread did not finish')
