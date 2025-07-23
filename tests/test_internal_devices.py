#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2019-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Jeevan M R <14.jeevan@gmail.com>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 SteveAmor <steveamor@noreply.users.github.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import errno
import warnings
from posix import statvfs_result
from subprocess import CalledProcessError
from threading import Event
from unittest import mock

import pytest

from gpiozero import *
from datetime import datetime, time

file_not_found = IOError(errno.ENOENT, 'File not found')
bad_ping = CalledProcessError(1, 'returned non-zero exit status 1')


def test_polled_event_delay(mock_factory):
    with TimeOfDay(time(7), time(8)) as tod:
        tod.event_delay = 1.0
        assert tod.event_delay == 1.0

def test_timeofday_bad_init(mock_factory):
    with pytest.raises(TypeError):
        TimeOfDay()
    with pytest.raises(ValueError):
        TimeOfDay(7, 12)
    with pytest.raises(TypeError):
        TimeOfDay(time(7))
    with pytest.raises(ValueError):
        TimeOfDay(time(7), time(7))
    with pytest.raises(ValueError):
        TimeOfDay(time(7), time(7))
    with pytest.raises(ValueError):
        TimeOfDay('7:00', '8:00')
    with pytest.raises(ValueError):
        TimeOfDay(7.00, 8.00)
    with pytest.raises(ValueError):
        TimeOfDay(datetime(2019, 1, 24, 19), time(19))  # lurch edge case

def test_timeofday_init(mock_factory):
    TimeOfDay(time(7), time(8), utc=False)
    TimeOfDay(time(7), time(8), utc=True)
    TimeOfDay(time(0), time(23, 59))
    TimeOfDay(time(0), time(23, 59))
    TimeOfDay(time(12, 30), time(13, 30))
    TimeOfDay(time(23), time(1))
    TimeOfDay(time(6), time(18))
    TimeOfDay(time(18), time(6))
    TimeOfDay(datetime(2019, 1, 24, 19), time(19, 1))  # lurch edge case

def test_timeofday_value(mock_factory):
    with TimeOfDay(time(7), time(8), utc=False) as tod:
        assert repr(tod).startswith('<gpiozero.TimeOfDay object')
        assert tod.start_time == time(7)
        assert tod.end_time == time(8)
        assert not tod.utc
        with mock.patch('gpiozero.internal_devices.datetime') as dt:
            dt.now.return_value = datetime(2018, 1, 1, 6, 59, 0)
            assert not tod.is_active
            dt.now.return_value = datetime(2018, 1, 1, 7, 0, 0)
            assert tod.is_active
            dt.now.return_value = datetime(2018, 1, 2, 8, 0, 0)
            assert tod.is_active
            dt.now.return_value = datetime(2018, 1, 2, 8, 1, 0)
            assert not tod.is_active
    assert repr(tod) == '<gpiozero.TimeOfDay object closed>'

    with TimeOfDay(time(1, 30), time(23, 30)) as tod:
        assert tod.start_time == time(1, 30)
        assert tod.end_time == time(23, 30)
        assert tod.utc
        with mock.patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 1, 29, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 1, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 12, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 31, 0)
            assert not tod.is_active

    with TimeOfDay(time(23), time(1)) as tod:
        with mock.patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 22, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 1, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 1, 1, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 3, 12, 0, 0)
            assert not tod.is_active

    with TimeOfDay(time(6), time(5)) as tod:
        with mock.patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 30, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 6, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 18, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 1, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 30, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 6, 0, 0)
            assert tod.is_active

def test_polled_events(mock_factory):
    with TimeOfDay(time(7), time(8)) as tod:
        tod.event_delay = 0.1
        activated = Event()
        deactivated = Event()
        with mock.patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 0, 0, 0)
            tod._fire_events(tod.pin_factory.ticks(), tod.is_active)
            tod.when_activated = activated.set
            tod.when_deactivated = deactivated.set
            assert not activated.wait(0)
            assert not deactivated.wait(0)
            dt.utcnow.return_value = datetime(2018, 1, 1, 7, 1, 0)
            assert activated.wait(1)
            activated.clear()
            assert not deactivated.wait(0)
            dt.utcnow.return_value = datetime(2018, 1, 1, 8, 1, 0)
            assert deactivated.wait(1)
            assert not activated.wait(0)
            tod.when_activated = None
            tod.when_deactivated = None

def test_polled_event_start_stop(mock_factory):
    with TimeOfDay(time(7), time(8)) as tod:
        assert not tod._event_thread
        tod.when_activated = lambda: True
        assert tod._event_thread
        tod.when_deactivated = lambda: True
        assert tod._event_thread
        tod.when_activated = None
        assert tod._event_thread
        tod.when_deactivated = None
        assert not tod._event_thread

def test_pingserver_bad_init(mock_factory):
    with pytest.raises(TypeError):
         PingServer()

def test_pingserver_init(mock_factory):
    with mock.patch('gpiozero.internal_devices.subprocess') as sp:
        sp.check_call.return_value = True
        with PingServer('example.com') as server:
            assert repr(server).startswith('<gpiozero.PingServer object')
            assert server.host == 'example.com'
        assert repr(server) == '<gpiozero.PingServer object closed>'
        with PingServer('192.168.1.10') as server:
            assert server.host == '192.168.1.10'
        with PingServer('8.8.8.8') as server:
            assert server.host == '8.8.8.8'
        with PingServer('2001:4860:4860::8888') as server:
            assert server.host == '2001:4860:4860::8888'

def test_pingserver_value(mock_factory):
    with mock.patch('gpiozero.internal_devices.subprocess.check_call') as check_call:
        with PingServer('example.com') as server:
            assert server.is_active
            check_call.side_effect = bad_ping
            assert not server.is_active
            check_call.side_effect = None
            assert server.is_active

def test_cputemperature_bad_init(mock_factory):
    with mock.patch('io.open', mock.mock_open()) as m:
        m.side_effect = file_not_found
        with pytest.raises(IOError):
            with CPUTemperature('') as temp:
                temp.value
        with pytest.raises(IOError):
            with CPUTemperature('badfile') as temp:
                temp.value
        m.return_value.__enter__.return_value.readline.return_value = '37000'
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=100)
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=10, max_temp=10)
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=20, max_temp=10)

def test_cputemperature(mock_factory):
    with mock.patch('io.open', mock.mock_open(read_data='37000')) as m:
        with CPUTemperature() as cpu:
            assert repr(cpu).startswith('<gpiozero.CPUTemperature object')
            assert cpu.temperature == 37.0
            assert cpu.value == 0.37
        assert repr(cpu) == '<gpiozero.CPUTemperature object closed>'
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            with CPUTemperature(min_temp=30, max_temp=40) as cpu:
                assert cpu.value == 0.7
                assert not cpu.is_active
            assert len(w) == 1
            assert w[0].category == ThresholdOutOfRange
            assert cpu.temperature == 37.0
        with CPUTemperature(min_temp=30, max_temp=40, threshold=35) as cpu:
            assert cpu.is_active

def test_loadaverage_bad_init(mock_factory):
    with mock.patch('io.open', mock.mock_open()) as m:
        m.side_effect = file_not_found
        with pytest.raises(IOError):
            with LoadAverage('') as load:
                load.value
        with pytest.raises(IOError):
            with LoadAverage('badfile') as load:
                load.value
    with mock.patch('io.open', mock.mock_open(read_data='0.09 0.10 0.09 1/292 20758')):
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=1)
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=0.5, max_load_average=0.5)
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=1, max_load_average=0.5)
        with pytest.raises(ValueError):
            LoadAverage(minutes=0)
        with pytest.raises(ValueError):
            LoadAverage(minutes=10)

def test_loadaverage(mock_factory):
    with mock.patch('io.open', mock.mock_open(read_data='0.09 0.10 0.09 1/292 20758')):
        with LoadAverage() as la:
            assert repr(la).startswith('<gpiozero.LoadAverage object')
            assert la.min_load_average == 0
            assert la.max_load_average == 1
            assert la.threshold == 0.8
            assert la.load_average == 0.1
            assert la.value == 0.1
            assert not la.is_active
        assert repr(la) == '<gpiozero.LoadAverage object closed>'
    with mock.patch('io.open', mock.mock_open(read_data='1.72 1.40 1.31 3/457 23102')):
        with LoadAverage(min_load_average=0.5, max_load_average=2,
                         threshold=1, minutes=5) as la:
            assert la.min_load_average == 0.5
            assert la.max_load_average == 2
            assert la.threshold == 1
            assert la.load_average == 1.4
            assert la.value == 0.6
            assert la.is_active
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            with LoadAverage(min_load_average=1, max_load_average=2,
                         threshold=0.8, minutes=5) as la:
                assert len(w) == 1
                assert w[0].category == ThresholdOutOfRange
                assert la.load_average == 1.4

def test_diskusage_bad_init(mock_factory):
    with pytest.raises(OSError):
        DiskUsage(filesystem='badfilesystem')

def test_diskusage(mock_factory):
    with mock.patch('os.statvfs') as statvfs:
        statvfs.return_value = statvfs_result((
            4096, 4096, 100000, 48000, 48000, 0, 0, 0, 0, 255))
        with DiskUsage() as disk:
            assert repr(disk).startswith('<gpiozero.DiskUsage object')
            assert disk.filesystem == '/'
            assert disk.usage == 52.0
            assert disk.is_active == False
            assert disk.value == 0.52
        assert repr(disk) == '<gpiozero.DiskUsage object closed>'
        with DiskUsage(threshold=50.0) as disk:
            assert disk.is_active == True
        with warnings.catch_warnings(record=True) as w:
            warnings.resetwarnings()
            with DiskUsage(threshold=125) as disk:
                assert disk.threshold == 125
                assert not disk.is_active
            assert len(w) == 1
            assert w[0].category == ThresholdOutOfRange
            assert disk.usage == 52.0
