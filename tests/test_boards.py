from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest

from gpiozero.pins.mock import MockPin
from gpiozero import *


def teardown_function(function):
    MockPin.clear_pins()

# TODO boards tests!

