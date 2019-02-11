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
