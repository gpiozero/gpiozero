# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2020 Grzegorz Szymaszek <gszymaszek@short.pl>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2016-2018 Ben Nuttall <ben@bennuttall.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from .devices import Device
from .exc import DeviceClosed, GPIOZeroError


class I2CDevice(Device):
    """
    Extends :class:`Device`. Represents a device that communicates via the I2C
    protocol.

    See :ref:`i2c_args` for information on the keyword arguments that can be
    specified with the constructor.
    """

    def __init__(self, **i2c_args):
        self._i2c = None
        super().__init__(pin_factory=i2c_args.pop("pin_factory", None))
        self._i2c = self.pin_factory.i2c(**i2c_args)

    def close(self):
        if getattr(self, "_i2c", None):
            self._i2c.close()
            self._i2c = None
        super().close()

    @property
    def closed(self):
        return self._i2c is None

    def __repr__(self):
        try:
            self._check_open()
            return "<gpiozero.{self.__class__.__name__} object using " "{self._i2c!r}>".format(
                self=self
            )
        except DeviceClosed:
            return "<gpiozero.{self.__class__.__name__} object " "closed>".format(self=self)