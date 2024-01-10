# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from gpiozero.compat import frozendict


def test_frozendict():
    d = {1: 'a', 2: 'b'}
    e = {1: 'a', 2: 'b', 'foo': 'bar'}
    f = frozendict(d)
    assert f[1] == 'a'
    assert f[2] == 'b'
    with pytest.raises(KeyError):
        f[3]
    with pytest.raises(TypeError):
        f[3] = 'c'
    assert d == f
    assert d == f.copy()
    assert e == f.copy(foo='bar')
    assert len(f) == 2
    assert {k: v for k, v in f.items()} == d
    h = hash(f)
    assert h is not None
    assert hash(f) == h
    assert repr(f) == f"<frozendict {d!r}>"
