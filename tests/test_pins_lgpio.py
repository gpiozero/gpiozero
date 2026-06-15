import os
import sys
from unittest import mock
import pytest
from pathlib import Path

# Mock lgpio before importing LGPIOFactory
mock_lgpio = mock.MagicMock()
sys.modules['lgpio'] = mock_lgpio

# Mock colorzero as it's a dependency of gpiozero
mock_colorzero = mock.MagicMock()
sys.modules['colorzero'] = mock_colorzero

from gpiozero.pins.lgpio import LGPIOFactory

def test_lgpio_factory_explicit_chip():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    factory = LGPIOFactory(chip=2)
    
    mock_lgpio.gpiochip_open.assert_called_once_with(2)
    assert factory._chip == 2
    assert factory._handle == 123

def test_lgpio_factory_env_var():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    with mock.patch.dict(os.environ, {'LGPIO_CHIP': '3'}):
        factory = LGPIOFactory()
        
    mock_lgpio.gpiochip_open.assert_called_once_with(3)
    assert factory._chip == 3

def test_lgpio_factory_pi5_auto_detect():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    # Mock _get_revision to return Pi 5 revision (0x17 in type bits)
    mock_get_revision = mock.Mock(return_value=0x170)
    
    # Mock /dev/gpiochip* glob
    mock_glob = mock.Mock(return_value=[Path('/dev/gpiochip4')])
    
    # Mock open and ioctl
    mock_open_file = mock.MagicMock()
    mock_open_file.__enter__.return_value = mock_open_file
    mock_open_file.fileno.return_value = 999
    
    def side_effect_ioctl(fd, cmd, buf):
        import struct
        chip_info_struct = struct.Struct("32s32sI")
        packed = chip_info_struct.pack(b'gpiochip4', b'pinctrl-rp1', 28)
        buf[:len(packed)] = packed
        return 0

    with mock.patch('gpiozero.pins.lgpio.LGPIOFactory._get_revision', mock_get_revision), \
         mock.patch('gpiozero.pins.lgpio.Path.glob', mock_glob), \
         mock.patch('gpiozero.pins.lgpio.Path.open', return_value=mock_open_file), \
         mock.patch('fcntl.ioctl', side_effect_ioctl):
        
        factory = LGPIOFactory()
        
    mock_lgpio.gpiochip_open.assert_called_once_with(4)
    assert factory._chip == 4

def test_lgpio_factory_pi5_auto_detect_fallback_to_4():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    mock_get_revision = mock.Mock(return_value=0x170)
    
    # Mock ioctl to fail or raise an error to trigger fallback
    def side_effect_ioctl(fd, cmd, buf):
        raise OSError("ioctl not supported")

    # Mock Path('/dev/gpiochip4').exists() to be True
    def side_effect_exists(self):
        if str(self) == '/dev/gpiochip4':
            return True
        return False

    with mock.patch('gpiozero.pins.lgpio.LGPIOFactory._get_revision', mock_get_revision), \
         mock.patch('gpiozero.pins.lgpio.Path.glob', return_value=[]), \
         mock.patch('gpiozero.pins.lgpio.Path.exists', side_effect_exists), \
         mock.patch('fcntl.ioctl', side_effect_ioctl):
        
        factory = LGPIOFactory()
        
    mock_lgpio.gpiochip_open.assert_called_once_with(4)
    assert factory._chip == 4

def test_lgpio_factory_pi5_auto_detect_fallback_to_0():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    mock_get_revision = mock.Mock(return_value=0x170)
    
    # Mock ioctl to fail
    def side_effect_ioctl(fd, cmd, buf):
        raise OSError("ioctl not supported")

    # Mock Path('/dev/gpiochip0').exists() to be True, and '/dev/gpiochip4' to be False
    def side_effect_exists(self):
        if str(self) == '/dev/gpiochip0':
            return True
        return False

    with mock.patch('gpiozero.pins.lgpio.LGPIOFactory._get_revision', mock_get_revision), \
         mock.patch('gpiozero.pins.lgpio.Path.glob', return_value=[]), \
         mock.patch('gpiozero.pins.lgpio.Path.exists', side_effect_exists), \
         mock.patch('fcntl.ioctl', side_effect_ioctl):
        
        factory = LGPIOFactory()
        
    mock_lgpio.gpiochip_open.assert_called_once_with(0)
    assert factory._chip == 0

def test_lgpio_factory_pi5_auto_detect_not_found():
    mock_lgpio.reset_mock()
    
    mock_get_revision = mock.Mock(return_value=0x170)
    
    # Mock glob to return empty, and exist check to return False
    with mock.patch('gpiozero.pins.lgpio.LGPIOFactory._get_revision', mock_get_revision), \
         mock.patch('gpiozero.pins.lgpio.Path.glob', return_value=[]), \
         mock.patch('gpiozero.pins.lgpio.Path.exists', return_value=False):
        
        with pytest.raises(RuntimeError, match="Cannot find RP1 gpiochip on Pi 5"):
            factory = LGPIOFactory()

def test_lgpio_factory_non_pi5_default():
    mock_lgpio.reset_mock()
    mock_lgpio.gpiochip_open.return_value = 123
    
    # Mock _get_revision to return non-Pi 5 revision (e.g. Pi 4)
    mock_get_revision = mock.Mock(return_value=0x110) # 0x11 is Pi 4
    
    with mock.patch('gpiozero.pins.lgpio.LGPIOFactory._get_revision', mock_get_revision):
        factory = LGPIOFactory()
        
    mock_lgpio.gpiochip_open.assert_called_once_with(0)
    assert factory._chip == 0
