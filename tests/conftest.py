# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2019-2023 Dave Jones <dave@waveform.org.uk>
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import warnings
from threading import Event, Thread

# Safe to import * as we are specifically defining __ALL__ in testing/__init__.py
# This makes fixtures defined in testing available as if they were defined here.
from gpiozero.testing import *

# NOTE: Work-around for python versions <3.4: in these versions the
# resetwarnings function in the warnings module doesn't do much (or doesn't do
# what most would expect). Warnings that have already been triggered still
# won't be re-triggered even after the call. To work-around this we set the
# default filter to "always" on these versions before running any tests. Note
# that this does mean you should run resetwarnings() whenever using
# catch_warnings()
if sys.version_info[:2] < (3, 4):
    warnings.simplefilter('always')

class ThreadedTest(Thread):
    def __init__(self, test_fn, *args, **kwargs):
        self._fn = test_fn
        self._args = args
        self._kwargs = kwargs
        self._result = None
        super().__init__(daemon=True)
        self.start()

    def run(self):
        self._result = self._fn(*self._args, **self._kwargs)

    @property
    def result(self):
        self.join(10)
        if not self.is_alive():
            return self._result
        else:
            raise RuntimeError('test thread did not finish')
