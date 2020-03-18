# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2015-2020 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 tuftii <3215045+tuftii@users.noreply.github.com>
# Copyright (c) 2019 Jeevan M R <14.jeevan@gmail.com>
# Copyright (c) 2019 ForToffee <ForToffee@users.noreply.github.com>
# Copyright (c) 2018 Claire Pollard <claire.r.pollard@gmail.com>
# Copyright (c) 2016 pcopa <scheltovandoorn@gmail.com>
# Copyright (c) 2016 Ian Harcombe <ian.harcombe@gmail.com>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2016 Andrew Scheller <lurch@durge.org>
# Copyright (c) 2015 Philip Howard <phil@gadgetoid.com>
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

from .pins import (
    Factory,
    Pin,
    SPI,
)
from .pins.data import (
    PiBoardInfo,
    HeaderInfo,
    PinInfo,
    pi_info,
)
# Yes, import * is naughty, but exc imports nothing else so there's no cross
# contamination here ... and besides, have you *seen* the list lately?!
from .exc import *
from .devices import (
    Device,
    GPIODevice,
    CompositeDevice,
)
from .mixins import (
    SharedMixin,
    SourceMixin,
    ValuesMixin,
    EventsMixin,
    HoldMixin,
)
from .input_devices import (
    InputDevice,
    DigitalInputDevice,
    SmoothedInputDevice,
    Button,
    LineSensor,
    MotionSensor,
    LightSensor,
    DistanceSensor,
)
from .spi_devices import (
    SPIDevice,
    AnalogInputDevice,
    MCP3001,
    MCP3002,
    MCP3004,
    MCP3008,
    MCP3201,
    MCP3202,
    MCP3204,
    MCP3208,
    MCP3301,
    MCP3302,
    MCP3304,
)
from .output_devices import (
    OutputDevice,
    DigitalOutputDevice,
    PWMOutputDevice,
    PWMLED,
    LED,
    Buzzer,
    Motor,
    PhaseEnableMotor,
    Servo,
    AngularServo,
    RGBLED,
    TonalBuzzer,
)
from .boards import (
    CompositeOutputDevice,
    ButtonBoard,
    LEDCollection,
    LEDBoard,
    LEDBarGraph,
    LedBorg,
    PiHutXmasTree,
    PiLiter,
    PiLiterBarGraph,
    TrafficLights,
    PiTraffic,
    PiStop,
    StatusZero,
    StatusBoard,
    SnowPi,
    TrafficLightsBuzzer,
    FishDish,
    TrafficHat,
    TrafficpHat,
    Robot,
    RyanteckRobot,
    CamJamKitRobot,
    PhaseEnableRobot,
    PololuDRV8835Robot,
    Energenie,
    PumpkinPi,
    JamHat,
    Pibrella,
)
from .internal_devices import (
    InternalDevice,
    PingServer,
    CPUTemperature,
    LoadAverage,
    TimeOfDay,
    DiskUsage,
)
