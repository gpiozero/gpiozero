from __future__ import absolute_import

import atexit

from RPi import GPIO

from .devices import (
    _gpio_threads_shutdown,
    GPIODeviceError,
    GPIODevice,
)
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
    Robot,
)
from .boards import (
    LEDBoard,
    PiLiter,
    TrafficLights,
    PiTraffic,
    FishDish,
    TrafficHat,
)


def gpiozero_shutdown():
    _gpio_threads_shutdown()
    GPIO.cleanup()

atexit.register(gpiozero_shutdown)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
