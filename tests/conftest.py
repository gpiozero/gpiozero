from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')


import pytest

from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPWMPin


@pytest.yield_fixture(scope='function')
def mock_factory(request):
    save_factory = Device.pin_factory
    Device.pin_factory = MockFactory()
    yield Device.pin_factory
    # This reset() may seem redundant given we're re-constructing the factory
    # for each function that requires is but MockFactory (via LocalFactory)
    # stores some info at the class level which reset() clears.
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    Device.pin_factory = save_factory

@pytest.fixture()
def pwm(request, mock_factory):
    mock_factory.pin_class = MockPWMPin
