# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016 Stewart <stewart@adcock.org.uk>
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
    absolute_import,
    print_function,
    division,
    )
str = type('')


import os

import pytest

from gpiozerocli.pinout import main


def test_args_incorrect():
    with pytest.raises(SystemExit) as ex:
        main(['pinout', '--nonexistentarg'])

def test_args_color():
    args = main.parser.parse_args([])
    assert args.color is None
    args = main.parser.parse_args(['--color'])
    assert args.color is True
    args = main.parser.parse_args(['--monochrome'])
    assert args.color is False

def test_args_revision():
    args = main.parser.parse_args(['--revision', '000d'])
    assert args.revision == '000d'

def test_help(capsys):
    with pytest.raises(SystemExit) as ex:
        main(['pinout', '--help'])
    out, err = capsys.readouterr()
    assert 'GPIO pin-out' in out

def test_execution(capsys, no_default_factory):
    os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
    assert main([]) == 0
