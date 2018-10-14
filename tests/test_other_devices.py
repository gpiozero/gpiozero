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

def test_PingServer_init():
    with PingServer('localhost') as server:
        assert server.host == 'localhost'

def test_PingServer_repr():
    with PingServer('localhost') as server:
        assert repr(server) == '<gpiozero.PingServer host="%s">' % server.host

def test_PingServer_unknown_attr():
    with PingServer('localhost') as server:
        with pytest.raises(AttributeError):
            server.foo = 1

def test_TimeOfDay_init():
    with TimeOfDay(time(7), time(12), utc=False) as morning:
        assert morning.start_time == time(7)
        assert morning.end_time == time(12)
        assert morning.utc == False
        morning.utc = True
        assert morning.utc == True

