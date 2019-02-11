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
    print_function,
    absolute_import,
    division,
    )
str = type('')


import sys
import pytest
import warnings

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

@pytest.yield_fixture()
def no_default_factory(request):
    save_pin_factory = Device.pin_factory
    Device.pin_factory = None
    yield None
    Device.pin_factory = save_pin_factory

@pytest.yield_fixture(scope='function')
def mock_factory(request):
    save_factory = Device.pin_factory
    Device.pin_factory = MockFactory()
    yield Device.pin_factory
    # This reset() may seem redundant given we're re-constructing the factory
    # for each function that requires it but MockFactory (via LocalFactory)
    # stores some info at the class level which reset() clears.
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    Device.pin_factory = save_factory

@pytest.fixture()
def pwm(request, mock_factory):
    mock_factory.pin_class = MockPWMPin
