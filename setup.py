"""A simple interface to GPIO devices with Raspberry Pi."""

import io
import os
import errno
from setuptools import setup, config


cfg = config.read_configuration(
    os.path.join(os.path.dirname(__file__), 'setup.cfg'))

try:
    # If we're executing on a Raspberry Pi, install all GPIO libraries for
    # testing (except RPIO which doesn't work on the multi-core models yet)
    with io.open('/proc/device-tree/model', 'r') as f:
        if f.read().startswith('Raspberry Pi'):
            cfg['options']['extras_require']['test'].append('RPI.GPIO')
            cfg['options']['extras_require']['test'].append('pigpio')
except IOError as e:
    if e.errno != errno.ENOENT:
        raise

opts = cfg['metadata']
opts.update(cfg['options'])

setup(**opts)
