from __future__ import absolute_import

import atexit

from RPi import GPIO


def gpiozero_shutdown():
    GPIO.cleanup()

atexit.register(gpiozero_shutdown)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

from .input_devices import (
    InputDeviceError,
    InputDevice,
    Button,
    MotionSensor,
    LightSensor,
    TemperatureSensor,
)
from .output_devices import (
    OutputDevice,
    LED,
    Buzzer,
    Motor,
)
