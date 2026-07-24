import pytest
from ..devices import Device
from ..pins.mock import MockFactory, MockPWMPin

@pytest.fixture()
def no_default_factory(request):
    """
    pytest fixture which temporarily sets the default pin factory to `None`
    and reverts the change at the end of the test run.
    """
    save_pin_factory = Device.pin_factory
    Device.pin_factory = None
    try:
        yield None
    finally:
        Device.pin_factory = save_pin_factory

@pytest.fixture(scope='function')
def mock_factory(request):
    """
    pytest fixture which provides a mock pin factory for executing tests
    without connected hardware. Ensures that the factory is **correctly
    reset** between tests and in case of test failure.

    Usage example:

    .. code-block:: python

        from gpiozero.testing import mock_factory

        test_mockedpin(mock_factory)
            pin16 = mock_factory.pin(16)
            ...

    """
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
    """
    pytest fixture which extends :func:`mock_factory`. Default
    :attr:`pin_class` is set to `MockPWMPin`
    """
    mock_factory.pin_class = MockPWMPin