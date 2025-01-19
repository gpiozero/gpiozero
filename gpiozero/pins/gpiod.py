# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2024 Kent Gibson <warthog618@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import select
from datetime import timedelta
from threading import Thread, RLock

from gpiod import (
    request_lines,
    Chip,
    LineSettings,
)
from gpiod.line import (
    Bias,
    Direction,
    Edge,
    Value
)
from .local import LocalPiFactory, LocalPiPin
from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    PinInvalidPull,
    PinInvalidBounce,
)

def find_gpiochip():
    """find the gpiochip with the pinctrl driver (that contains the Pi GPIOs)"""
    for chipnum in [0, 4]:
        path = f"/dev/gpiochip{chipnum}"
        with Chip(path) as chip:
            if chip.get_info().label.startswith("pinctrl-"):
                return chipnum
    raise Exception("cannot find gpiochip for Pi GPIOs")

class GpiodFactory(LocalPiFactory):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiFactory`. Uses the `gpiod`_
    library to interface to the local computer's GPIO pins. The gpiod library
    simply talks to Linux gpiochip devices; it is not specific to the Raspberry
    Pi although this class is currently constructed under the assumption that
    it is running on a Raspberry Pi.

    You can construct gpiod pins manually like so::

        from gpiozero.pins.gpiod import GpiodFactory
        from gpiozero import LED

        factory = GpiodFactory(chip=0)
        led = LED(12, pin_factory=factory)

    The *chip* parameter to the factory constructor specifies which gpiochip
    device to attempt to open. It defaults to the gpiochip containing the
    Pi header pins and thus doesn't normally need to be specified (the example
    above only includes it for completeness).

    The gpiod library relies on access to the :file:`/dev/gpiochip*` devices.
    If you run into issues, please check that your user has read/write access
    to the specific gpiochip device you are attempting to open (generally 0
    by default).

    .. _gpiod: https://pypi.org/project/gpiod/
    """

    def __init__(self, chip=None):
        super().__init__()
        if chip is None:
            chip = find_gpiochip()
        self._chip = chip
        self._chip_path = f'/dev/gpiochip{chip}'
        self.pin_class = GpiodPin
        # lazily constructed on first watch
        self._watcher = None

    def close(self):
        super().close()
        if self._watcher is not None:
            self._watcher.close()
            self._watcher = None

    def _watch(self, fd, pin):
        if self._watcher is None:
            self._watcher = GpiodWatcherThread()
        self._watcher.watch(fd, pin)

    def _unwatch(self, fd):
        if self._watcher is not None:
            self._watcher.unwatch(self._req.fd)

    def _get_spi_class(self, shared, hardware):
        # gpiod does not provide support for spidev, so force software.
        return super()._get_spi_class(shared, hardware=False)

    @property
    def chip(self):
        return self._chip


class GpiodPin(LocalPiPin):
    """
    Extends :class:`~gpiozero.pins.local.LocalPiPin`. Pin implementation for
    the `gpiod`_ library. See :class:`GpiodFactory` for more information.

    .. _gpiod: https://pypi.org/project/gpiod/
    """

    def __init__(self, factory, info):
        super().__init__(factory, info)
        self._settings = LineSettings(direction=Direction.INPUT)
        self._req = None
        self._watched_fd = None
        self._edges = 'both'
        # Note: line is lazily requested on first access - not during construction

    def __apply_config(self):
        config = {self._number: self._settings}
        if self._req is not None:
            self._req.reconfigure_lines(config=config)
        else:
            self._req = request_lines(self.factory._chip_path, config=config,
                                      consumer="gpiozero-gpiod")

    def __pull_to_bias(self, pull):
        try:
            return {'up': Bias.PULL_UP,
                    'down': Bias.PULL_DOWN,
                    'floating': Bias.DISABLED}[pull]
        except KeyError:
            raise PinInvalidPull(f'invalid pull "{pull}" for pin {self!r}')

    def __check_fixed_pull(self, pull):
        if self.info.pull not in (pull, ''):
            raise PinFixedPull(
                f'{self!r} has a physical pull-{self.info.pull} resistor')

    def close(self):
        if self._req is not None:
            self._unwatch()
            self._req.release()
            self._req = None
        self._settings = LineSettings(direction=Direction.INPUT)

    def output_with_state(self, state):
        value = Value.ACTIVE if state else Value.INACTIVE
        self._settings = LineSettings(
            direction=Direction.OUTPUT, output_value=value)
        self.__apply_config()

    def input_with_pull(self, pull):
        self.__check_fixed_pull(pull)
        bias = self.__pull_to_bias(pull)
        self._settings = LineSettings(direction=Direction.INPUT, bias=bias)
        self.__apply_config()

    def _get_function(self):
        return 'input' if self._settings.direction == Direction.INPUT else 'output'

    def _set_function(self, value):
        if self.function == value:
            return
        if value == 'output':
            self._settings = LineSettings(direction=Direction.OUTPUT)
            self._unwatch()
        elif value == 'input':
            self._settings = LineSettings(direction=Direction.INPUT)
        else:
            raise PinInvalidFunction(
                f'invalid function "{value}" for pin {self!r}')
        self.__apply_config()

    def _get_state(self):
        if self._req is None:
            self._req = request_lines(self.factory._chip_path,
                                      config={self._number: self._settings})
        return self._req.get_value(self._number) == Value.ACTIVE

    def _set_state(self, value):
        if self.function == 'input':
            raise PinSetInput(f'cannot set state of pin {self!r}')
        else:
            # function has been set to output, so pin must already be requested
            v = Value.ACTIVE if value else Value.INACTIVE
            self._req.set_value(self._number, v)

    def _get_pull(self):
        return {Bias.AS_IS: 'unknown',
                Bias.DISABLED: 'floating',
                Bias.PULL_UP: 'up',
                Bias.PULL_DOWN: 'down'}[self._settings.bias]

    def _set_pull(self, pull):
        # as drive is always push-pull here, biasing an output makes no sense
        if self.function != 'input':
            raise PinFixedPull(f'cannot set pull on non-input pin {self!r}')
        self.__check_fixed_pull(pull)
        bias = self.__pull_to_bias(pull)
        if self._settings.bias == bias:
            return
        self._settings.bias = bias
        self.__apply_config()

    def _get_bounce(self):
        return None if not self._settings.debounce_period else self._settings.debounce_period.total_seconds()

    def _set_bounce(self, value):
        if self.function != 'input':
            raise PinInvalidBounce(f'cannot set debounce on non-input pin {self!r}')
        if value is None:
            value = 0
        elif value < 0:
            raise PinInvalidBounce('bounce must be 0 or greater')
        self._settings.debounce_period = timedelta(seconds=value)
        self.__apply_config()

    def _get_edges(self):
        return self._edges

    def _set_edges(self, value):
        self._edges = value
        if self.when_changed is not None:
            self.__apply_config()

    def _enable_event_detect(self):
        edges = {'both': Edge.BOTH,
                 'rising': Edge.RISING,
                 'falling': Edge.FALLING,
                 'none': Edge.NONE}[self._edges]
        self._settings.edge_detection = edges
        self.__apply_config()
        if edges != Edge.NONE:
            self._watch()

    def _disable_event_detect(self):
        self._unwatch()
        self._settings.edge_detection = Edge.NONE
        self.__apply_config()

    def __read_event(self):
        evt = self._req.read_edge_events(max_events=1)[0]
        level = 1 if evt.event_type == evt.Type.RISING_EDGE else 0
        self._call_when_changed(evt.timestamp_ns / 1000000000, level)

    def _watch(self):
        if self._watched_fd is None:
            self.watched_fd = self._req.fd
            self.factory._watch(self._req.fd, self)

    def _unwatch(self):
        if self._watched_fd is not None:
            self.factory._unwatch(self._watched_fd)
            self._watched_fd = None


class GpiodWatcherThread(Thread):
    EXIT = b'deaddodo'
    WAKE = b'reawaken'

    def __init__(self):
        super().__init__(target=self._run)
        self.daemon = True
        self._watches = {}
        self._lock = RLock()
        # thread started by first watch

    def close(self):
        with self._lock:
            if self._poll is not None:
                os.write(self._evtfd, self.EXIT)
                self.join()
                self._poll.close()
                self._poll = None
                os.close(self._evtfd)
                self._evtfd = None

    def watch(self, fd, pin):
        with self._lock:
            flags = select.POLLIN | select.POLLPRI
            if len(self._watches) == 0:
                self._evtfd = os.eventfd(0)
                self._poll = select.poll()
                self._poll.register(self._evtfd, flags)
            self._watches[fd] = pin
            self._poll.register(fd, flags)
            if len(self._watches) == 1:
                self.start()
            else:
                os.write(self._evtfd, self.WAKE)

    def unwatch(self, fd):
        with self._lock:
            self._watches.pop(fd, None)
            self._poll.unregister(fd)
            if len(self._watches):
                os.write(self._evtfd, self.WAKE)
            else:
                self.close()

    def _run(self):
        while True:
            for fd, event in self._poll.poll():
                if fd == self._evtfd:
                    cmd = os.read(self._evtfd, 8)
                    if cmd == self.EXIT:
                        return
                    # only other command is wake - to update the poll
                    continue
                try:
                    self._watches[fd].__read_event()
                except KeyError:
                    # fd has been unwatched so ignore and move on
                    pass
