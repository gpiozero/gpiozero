from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')


from gpiozero import Device
from gpiozero.pins.mock import MockFactory

Device.pin_factory = MockFactory()
