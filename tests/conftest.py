from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
    )
str = type('')

import os
os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
