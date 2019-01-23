from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import warnings

import pytest

from gpiozero import *
from datetime import time

def test_pingserver_init():
    with PingServer('localhost') as server:
        assert server.host == 'localhost'

def test_pingserver_repr():
    with PingServer('localhost') as server:
        assert repr(server) == '<gpiozero.PingServer host="%s">' % server.host

def test_pingserver_unknown_attr():
    with PingServer('localhost') as server:
        with pytest.raises(AttributeError):
            server.foo = 1

def test_timeofday_init():
    with TimeOfDay(time(7), time(12), utc=False) as morning:
        assert morning.start_time == time(7)
        assert morning.end_time == time(12)
        assert morning.utc == False
        morning.utc = True
        assert morning.utc == True
        
def test_cputemperature_invalid_val():
    with pytest.raises(ValueError):
        CPUTemperature(min_temp=100.00)
