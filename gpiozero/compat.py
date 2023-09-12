# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Fangchen Li <fangchen.li@outlook.com>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import operator
from functools import reduce
from collections.abc import Mapping


# Derived from the MIT-licensed https://github.com/slezica/python-frozendict
class frozendict(Mapping):
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def copy(self, **add_or_replace):
        return frozendict(self, **add_or_replace)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._dict!r}>'

    def __hash__(self):
        if self._hash is None:
            self._hash = reduce(operator.xor, map(hash, self.items()), 0)
        return self._hash
