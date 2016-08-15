from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')


import pytest
from mock import patch, MagicMock

import gpiozero.devices
import gpiozero.pins.data
import gpiozero.pins.native
from gpiozero.pins.data import pi_info
from gpiozero import PinMultiplePins, PinNoPins, PinUnknownPi


def test_pi_revision():
    save_factory = gpiozero.devices.pin_factory
    try:
        # Can't use MockPin for this as we want something that'll actually try
        # and read /proc/cpuinfo (MockPin simply parrots the 2B's data);
        # NativePin is used as we're guaranteed to be able to import it
        gpiozero.devices.pin_factory = gpiozero.pins.native.NativePin
        with patch('io.open') as m:
            m.return_value.__enter__.return_value = ['lots of irrelevant', 'lines', 'followed by', 'Revision: 0002', 'Serial:  xxxxxxxxxxx']
            assert pi_info().revision == '0002'
            # LocalPin caches the revision (because realistically it isn't going to
            # change at runtime); we need to wipe it here though
            gpiozero.pins.native.NativePin._PI_REVISION = None
            m.return_value.__enter__.return_value = ['Revision: a21042']
            assert pi_info().revision == 'a21042'
            # Check over-volting result (some argument over whether this is 7 or
            # 8 character result; make sure both work)
            gpiozero.pins.native.NativePin._PI_REVISION = None
            m.return_value.__enter__.return_value = ['Revision: 1000003']
            assert pi_info().revision == '0003'
            gpiozero.pins.native.NativePin._PI_REVISION = None
            m.return_value.__enter__.return_value = ['Revision: 100003']
            assert pi_info().revision == '0003'
            with pytest.raises(PinUnknownPi):
                m.return_value.__enter__.return_value = ['nothing', 'relevant', 'at all']
                gpiozero.pins.native.NativePin._PI_REVISION = None
                pi_info()
            with pytest.raises(PinUnknownPi):
                pi_info('0fff')
    finally:
        gpiozero.devices.pin_factory = save_factory

def test_pi_info():
    r = pi_info('900011')
    assert r.model == 'B'
    assert r.pcb_revision == '1.0'
    assert r.memory == 512
    assert r.manufacturer == 'Sony'
    assert r.storage == 'SD'
    assert r.usb == 2
    assert not r.wifi
    assert not r.bluetooth
    assert r.csi == 1
    assert r.dsi == 1
    with pytest.raises(PinUnknownPi):
        pi_info('9000f1')

def test_pi_info_other_types():
    with pytest.raises(PinUnknownPi):
        pi_info(b'9000f1')
    with pytest.raises(PinUnknownPi):
        pi_info(0x9000f1)

def test_physical_pins():
    # Assert physical pins for some well-known Pi's; a21041 is a Pi2B
    assert pi_info('a21041').physical_pins('3V3') == {('P1', 1), ('P1', 17)}
    assert pi_info('a21041').physical_pins('GPIO2') == {('P1', 3)}
    assert pi_info('a21041').physical_pins('GPIO47') == set()

def test_physical_pin():
    with pytest.raises(PinMultiplePins):
        assert pi_info('a21041').physical_pin('GND')
    assert pi_info('a21041').physical_pin('GPIO3') == ('P1', 5)
    with pytest.raises(PinNoPins):
        assert pi_info('a21041').physical_pin('GPIO47')

def test_pulled_up():
    assert pi_info('a21041').pulled_up('GPIO2')
    assert not pi_info('a21041').pulled_up('GPIO4')
    assert not pi_info('a21041').pulled_up('GPIO47')

