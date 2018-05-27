import sys

from mock import Mock
import pytest

from gpiozero.i2c import I2C, find_smbus_module


@pytest.mark.skipif(hasattr(sys, 'pypy_version_info'),
                    reason="XXX: Doesn't work on Pypy")
def test_i2c():
    # Ensure instance uniqueness relies on bus number
    assert I2C._shared_key(bus=0) == 0
    assert I2C._shared_key(1) == 1
    # Create a mock of SMBus
    smbus = Mock()
    smbus.read_i2c_block_data = Mock(return_value=[0xda, 0x7a])
    smbus.write_i2c_block_data = Mock()
    SMBus = Mock(return_value=smbus)
    # Create an instance
    lock = Mock(__enter__=Mock(), __exit__=Mock())
    i2c = I2C(1, SMBus, lock)
    # Ensure the interface class was called with the bus number
    SMBus.assert_called_once_with(1)
    # Test __repr__()
    assert repr(i2c) == 'I2C(bus=1)'
    # Test read()
    assert i2c.read(0x13, 0x37, 42) == [0xda, 0x7a]
    i2c.lock.__enter__.assert_called_once_with()
    i2c.lock.__exit__.assert_called_once_with(None, None, None)
    smbus.read_i2c_block_data.assert_called_once_with(0x13, 0x37, 42)
    # Test write()
    i2c.lock = Mock(__enter__=Mock(), __exit__=Mock())
    assert i2c.write(1, 2, [3, 4]) is None
    i2c.lock.__enter__.assert_called_once_with()
    i2c.lock.__exit__.assert_called_once_with(None, None, None)
    smbus.write_i2c_block_data.assert_called_once_with(1, 2, [3, 4])


def test_find_smbus_module():
    import re
    assert find_smbus_module(('foo', 'bar', 're')) is re
    with pytest.raises(ImportError):
        find_smbus_module(('a', 'b'))
