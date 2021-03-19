# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2016 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

import operator
from functools import reduce
from collections.abc import Mapping


# Copied from the MIT-licensed https://github.com/slezica/python-frozendict
class frozendict(Mapping):
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def copy(self, **add_or_replace):
        return frozendict(self, **add_or_replace)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<frozendict {self._dict!r}>'.format(self=self)

    def __hash__(self):
        if self._hash is None:
            hashes = map(hash, self.items())
            self._hash = reduce(operator.xor, hashes, 0)
        return self._hash
