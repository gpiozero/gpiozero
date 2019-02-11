# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2018 Rick Ansell <rick@nbinvincible.org.uk>
# Copyright (c) 2018 Mike Kazantsev <mk.fraggod@gmail.com>
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

from weakref import ref
from collections import defaultdict
from threading import Lock

from ..exc import (
    PinInvalidFunction,
    PinSetInput,
    PinFixedPull,
    PinUnsupported,
    PinSPIUnsupported,
    PinPWMUnsupported,
    PinEdgeDetectUnsupported,
    SPIFixedClockMode,
    SPIFixedBitOrder,
    SPIFixedSelect,
    SPIFixedWordSize,
    GPIOPinInUse,
    )


class Factory(object):
    """
    Generates pins and SPI interfaces for devices. This is an abstract
    base class for pin factories. Descendents *must* override the following
    methods:

    * :meth:`ticks`
    * :meth:`ticks_diff`

    Descendents *may* override the following methods, if applicable:

    * :meth:`close`
    * :meth:`reserve_pins`
    * :meth:`release_pins`
    * :meth:`release_all`
    * :meth:`pin`
    * :meth:`spi`
    * :meth:`_get_pi_info`
    """
    def __init__(self):
        self._reservations = defaultdict(list)
        self._res_lock = Lock()

    def reserve_pins(self, requester, *pins):
        """
        Called to indicate that the device reserves the right to use the
        specified *pins*. This should be done during device construction.  If
        pins are reserved, you must ensure that the reservation is released by
        eventually called :meth:`release_pins`.
        """
        with self._res_lock:
            for pin in pins:
                for reserver_ref in self._reservations[pin]:
                    reserver = reserver_ref()
                    if reserver is not None and requester._conflicts_with(reserver):
                        raise GPIOPinInUse('pin %s is already in use by %r' %
                                           (pin, reserver))
                self._reservations[pin].append(ref(requester))

    def release_pins(self, reserver, *pins):
        """
        Releases the reservation of *reserver* against *pins*.  This is
        typically called during :meth:`~gpiozero.Device.close` to clean up
        reservations taken during construction. Releasing a reservation that is
        not currently held will be silently ignored (to permit clean-up after
        failed / partial construction).
        """
        with self._res_lock:
            for pin in pins:
                self._reservations[pin] = [
                    ref for ref in self._reservations[pin]
                    if ref() not in (reserver, None) # may as well clean up dead refs
                    ]

    def release_all(self, reserver):
        """
        Releases all pin reservations taken out by *reserver*. See
        :meth:`release_pins` for further information).
        """
        # Yes, this would be more efficient if it simply regenerated the
        # reservations list without any references to reserver instead of
        # (in release_pins) looping over each pin individually. However, this
        # then causes a subtle bug in LocalPiFactory which does something
        # horribly naughty (with good reason) and makes its _reservations
        # dictionary equivalent to a class-level one.
        self.release_pins(reserver, *self._reservations)

    def close(self):
        """
        Closes the pin factory. This is expected to clean up all resources
        manipulated by the factory. It it typically called at script
        termination.
        """
        pass

    def pin(self, spec):
        """
        Creates an instance of a :class:`Pin` descendent representing the
        specified pin.

        .. warning::

            Descendents must ensure that pin instances representing the same
            hardware are identical; i.e. two separate invocations of
            :meth:`pin` for the same pin specification must return the same
            object.
        """
        raise PinUnsupported(
            "Individual pins are not supported by this pin factory")

    def spi(self, **spi_args):
        """
        Returns an instance of an :class:`SPI` interface, for the specified SPI
        *port* and *device*, or for the specified pins (*clock_pin*,
        *mosi_pin*, *miso_pin*, and *select_pin*).  Only one of the schemes can
        be used; attempting to mix *port* and *device* with pin numbers will
        raise :exc:`SPIBadArgs`.
        """
        raise PinSPIUnsupported('SPI not supported by this pin factory')

    def ticks(self):
        """
        Return the current ticks, according to the factory. The reference point
        is undefined and thus the result of this method is only meaningful when
        compared to another value returned by this method.

        The format of the time is also arbitrary, as is whether the time wraps
        after a certain duration. Ticks should only be compared using the
        :meth:`ticks_diff` method.
        """
        raise NotImplementedError

    def ticks_diff(self, later, earlier):
        """
        Return the time in seconds between two :meth:`ticks` results. The
        arguments are specified in the same order as they would be in the
        formula *later* - *earlier* but the result is guaranteed to be in
        seconds, and to be positive even if the ticks "wrapped" between calls
        to :meth:`ticks`.
        """
        raise NotImplementedError

    def _get_pi_info(self):
        return None

    pi_info = property(
        lambda self: self._get_pi_info(),
        doc="""\
        Returns a :class:`PiBoardInfo` instance representing the Pi that
        instances generated by this factory will be attached to.

        If the pins represented by this class are not *directly* attached to a
        Pi (e.g. the pin is attached to a board attached to the Pi, or the pins
        are not on a Pi at all), this may return :data:`None`.
        """)


class Pin(object):
    """
    Abstract base class representing a pin attached to some form of controller,
    be it GPIO, SPI, ADC, etc.

    Descendents should override property getters and setters to accurately
    represent the capabilities of pins. Descendents *must* override the
    following methods:

    * :meth:`_get_function`
    * :meth:`_set_function`
    * :meth:`_get_state`

    Descendents *may* additionally override the following methods, if
    applicable:

    * :meth:`close`
    * :meth:`output_with_state`
    * :meth:`input_with_pull`
    * :meth:`_set_state`
    * :meth:`_get_frequency`
    * :meth:`_set_frequency`
    * :meth:`_get_pull`
    * :meth:`_set_pull`
    * :meth:`_get_bounce`
    * :meth:`_set_bounce`
    * :meth:`_get_edges`
    * :meth:`_set_edges`
    * :meth:`_get_when_changed`
    * :meth:`_set_when_changed`
    """

    def __repr__(self):
        return "<Pin>"

    def close(self):
        """
        Cleans up the resources allocated to the pin. After this method is
        called, this :class:`Pin` instance may no longer be used to query or
        control the pin's state.
        """
        pass

    def output_with_state(self, state):
        """
        Sets the pin's function to "output" and specifies an initial state
        for the pin. By default this is equivalent to performing::

            pin.function = 'output'
            pin.state = state

        However, descendents may override this in order to provide the smallest
        possible delay between configuring the pin for output and specifying an
        initial value (which can be important for avoiding "blips" in
        active-low configurations).
        """
        self.function = 'output'
        self.state = state

    def input_with_pull(self, pull):
        """
        Sets the pin's function to "input" and specifies an initial pull-up
        for the pin. By default this is equivalent to performing::

            pin.function = 'input'
            pin.pull = pull

        However, descendents may override this order to provide the smallest
        possible delay between configuring the pin for input and pulling the
        pin up/down (which can be important for avoiding "blips" in some
        configurations).
        """
        self.function = 'input'
        self.pull = pull

    def _get_function(self):
        return "input"

    def _set_function(self, value):
        if value != "input":
            raise PinInvalidFunction(
                "Cannot set the function of pin %r to %s" % (self, value))

    function = property(
        lambda self: self._get_function(),
        lambda self, value: self._set_function(value),
        doc="""\
        The function of the pin. This property is a string indicating the
        current function or purpose of the pin. Typically this is the string
        "input" or "output". However, in some circumstances it can be other
        strings indicating non-GPIO related functionality.

        With certain pin types (e.g. GPIO pins), this attribute can be changed
        to configure the function of a pin. If an invalid function is
        specified, for this attribute, :exc:`PinInvalidFunction` will be
        raised.
        """)

    def _get_state(self):
        return 0

    def _set_state(self, value):
        raise PinSetInput("Cannot set the state of input pin %r" % self)

    state = property(
        lambda self: self._get_state(),
        lambda self, value: self._set_state(value),
        doc="""\
        The state of the pin. This is 0 for low, and 1 for high. As a low level
        view of the pin, no swapping is performed in the case of pull ups (see
        :attr:`pull` for more information):

        .. code-block:: text

            HIGH - - - - >       ,----------------------
                                 |
                                 |
            LOW  ----------------'

        Descendents which implement analog, or analog-like capabilities can
        return values between 0 and 1. For example, pins implementing PWM
        (where :attr:`frequency` is not :data:`None`) return a value between
        0.0 and 1.0 representing the current PWM duty cycle.

        If a pin is currently configured for input, and an attempt is made to
        set this attribute, :exc:`PinSetInput` will be raised. If an invalid
        value is specified for this attribute, :exc:`PinInvalidState` will be
        raised.
        """)

    def _get_pull(self):
        return 'floating'

    def _set_pull(self, value):
        raise PinFixedPull("Cannot change pull-up on pin %r" % self)

    pull = property(
        lambda self: self._get_pull(),
        lambda self, value: self._set_pull(value),
        doc="""\
        The pull-up state of the pin represented as a string. This is typically
        one of the strings "up", "down", or "floating" but additional values
        may be supported by the underlying hardware.

        If the pin does not support changing pull-up state (for example because
        of a fixed pull-up resistor), attempts to set this property will raise
        :exc:`PinFixedPull`. If the specified value is not supported by the
        underlying hardware, :exc:`PinInvalidPull` is raised.
        """)

    def _get_frequency(self):
        return None

    def _set_frequency(self, value):
        if value is not None:
            raise PinPWMUnsupported("PWM is not supported on pin %r" % self)

    frequency = property(
        lambda self: self._get_frequency(),
        lambda self, value: self._set_frequency(value),
        doc="""\
        The frequency (in Hz) for the pin's PWM implementation, or :data:`None`
        if PWM is not currently in use. This value always defaults to
        :data:`None` and may be changed with certain pin types to activate or
        deactivate PWM.

        If the pin does not support PWM, :exc:`PinPWMUnsupported` will be
        raised when attempting to set this to a value other than :data:`None`.
        """)

    def _get_bounce(self):
        return None

    def _set_bounce(self, value):
        if value is not None:
            raise PinEdgeDetectUnsupported(
                "Edge detection is not supported on pin %r" % self)

    bounce = property(
        lambda self: self._get_bounce(),
        lambda self, value: self._set_bounce(value),
        doc="""\
        The amount of bounce detection (elimination) currently in use by edge
        detection, measured in seconds. If bounce detection is not currently in
        use, this is :data:`None`.

        For example, if :attr:`edges` is currently "rising", :attr:`bounce` is
        currently 5/1000 (5ms), then the waveform below will only fire
        :attr:`when_changed` on two occasions despite there being three rising
        edges:

        .. code-block:: text

            TIME 0...1...2...3...4...5...6...7...8...9...10..11..12 ms

            bounce elimination   |===================| |==============

            HIGH - - - - >       ,--. ,--------------. ,--.
                                 |  | |              | |  |
                                 |  | |              | |  |
            LOW  ----------------'  `-'              `-'  `-----------
                                 :                     :
                                 :                     :
                           when_changed          when_changed
                               fires                 fires

        If the pin does not support edge detection, attempts to set this
        property will raise :exc:`PinEdgeDetectUnsupported`. If the pin
        supports edge detection, the class must implement bounce detection,
        even if only in software.
        """)

    def _get_edges(self):
        return 'none'

    def _set_edges(self, value):
        raise PinEdgeDetectUnsupported(
            "Edge detection is not supported on pin %r" % self)

    edges = property(
        lambda self: self._get_edges(),
        lambda self, value: self._set_edges(value),
        doc="""\
        The edge that will trigger execution of the function or bound method
        assigned to :attr:`when_changed`. This can be one of the strings
        "both" (the default), "rising", "falling", or "none":

        .. code-block:: text

            HIGH - - - - >           ,--------------.
                                     |              |
                                     |              |
            LOW  --------------------'              `--------------
                                     :              :
                                     :              :
            Fires when_changed     "both"         "both"
            when edges is ...     "rising"       "falling"

        If the pin does not support edge detection, attempts to set this
        property will raise :exc:`PinEdgeDetectUnsupported`.
        """)

    def _get_when_changed(self):
        return None

    def _set_when_changed(self, value):
        raise PinEdgeDetectUnsupported(
            "Edge detection is not supported on pin %r" % self)

    when_changed = property(
        lambda self: self._get_when_changed(),
        lambda self, value: self._set_when_changed(value),
        doc="""\
        A function or bound method to be called when the pin's state changes
        (more specifically when the edge specified by :attr:`edges` is detected
        on the pin). The function or bound method must accept two parameters:
        the first will report the ticks (from :meth:`Factory.ticks`) when
        the pin's state changed, and the second will report the pin's current
        state.

        .. warning::

            Depending on hardware support, the state is *not guaranteed to be
            accurate*. For instance, many GPIO implementations will provide
            an interrupt indicating when a pin's state changed but not what it
            changed to. In this case the pin driver simply reads the pin's
            current state to supply this parameter, but the pin's state may
            have changed *since* the interrupt. Exercise appropriate caution
            when relying upon this parameter.

        If the pin does not support edge detection, attempts to set this
        property will raise :exc:`PinEdgeDetectUnsupported`.
        """)


class SPI(object):
    """
    Abstract interface for `Serial Peripheral Interface`_ (SPI)
    implementations. Descendents *must* override the following methods:

    * :meth:`transfer`
    * :meth:`_get_clock_mode`

    Descendents *may* override the following methods, if applicable:

    * :meth:`read`
    * :meth:`write`
    * :meth:`_set_clock_mode`
    * :meth:`_get_lsb_first`
    * :meth:`_set_lsb_first`
    * :meth:`_get_select_high`
    * :meth:`_set_select_high`
    * :meth:`_get_bits_per_word`
    * :meth:`_set_bits_per_word`

    .. _Serial Peripheral Interface: https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
    """

    def read(self, n):
        """
        Read *n* words of data from the SPI interface, returning them as a
        sequence of unsigned ints, each no larger than the configured
        :attr:`bits_per_word` of the interface.

        This method is typically used with read-only devices that feature
        half-duplex communication. See :meth:`transfer` for full duplex
        communication.
        """
        return self.transfer([0] * n)

    def write(self, data):
        """
        Write *data* to the SPI interface. *data* must be a sequence of
        unsigned integer words each of which will fit within the configured
        :attr:`bits_per_word` of the interface. The method returns the number
        of words written to the interface (which may be less than or equal to
        the length of *data*).

        This method is typically used with write-only devices that feature
        half-duplex communication. See :meth:`transfer` for full duplex
        communication.
        """
        return len(self.transfer(data))

    def transfer(self, data):
        """
        Write *data* to the SPI interface. *data* must be a sequence of
        unsigned integer words each of which will fit within the configured
        :attr:`bits_per_word` of the interface. The method returns the sequence
        of words read from the interface while writing occurred (full duplex
        communication).

        The length of the sequence returned dictates the number of words of
        *data* written to the interface. Each word in the returned sequence
        will be an unsigned integer no larger than the configured
        :attr:`bits_per_word` of the interface.
        """
        raise NotImplementedError

    @property
    def clock_polarity(self):
        """
        The polarity of the SPI clock pin. If this is :data:`False` (the
        default), the clock pin will idle low, and pulse high. Setting this to
        :data:`True` will cause the clock pin to idle high, and pulse low. On
        many data sheets this is documented as the CPOL value.

        The following diagram illustrates the waveform when
        :attr:`clock_polarity` is :data:`False` (the default), equivalent to
        CPOL 0:

        .. code-block:: text

                   on      on      on      on      on      on      on
                  ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
            CLK   |   |   |   |   |   |   |   |   |   |   |   |   |   |
                  |   |   |   |   |   |   |   |   |   |   |   |   |   |
            ------'   `---'   `---'   `---'   `---'   `---'   `---'   `------
            idle       off     off     off     off     off     off       idle

        The following diagram illustrates the waveform when
        :attr:`clock_polarity` is :data:`True`, equivalent to CPOL 1:

        .. code-block:: text

            idle       off     off     off     off     off     off       idle
            ------.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,------
                  |   |   |   |   |   |   |   |   |   |   |   |   |   |
            CLK   |   |   |   |   |   |   |   |   |   |   |   |   |   |
                  `---'   `---'   `---'   `---'   `---'   `---'   `---'
                   on      on      on      on      on      on      on
        """
        return bool(self.clock_mode & 2)

    @clock_polarity.setter
    def clock_polarity(self, value):
        self.clock_mode = self.clock_mode & (~2) | (bool(value) << 1)

    @property
    def clock_phase(self):
        """
        The phase of the SPI clock pin. If this is :data:`False` (the default),
        data will be read from the MISO pin when the clock pin activates.
        Setting this to :data:`True` will cause data to be read from the MISO
        pin when the clock pin deactivates. On many data sheets this is
        documented as the CPHA value. Whether the clock edge is rising or
        falling when the clock is considered activated is controlled by the
        :attr:`clock_polarity` attribute (corresponding to CPOL).

        The following diagram indicates when data is read when
        :attr:`clock_polarity` is :data:`False`, and :attr:`clock_phase` is
        :data:`False` (the default), equivalent to CPHA 0:

        .. code-block:: text

                ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `---'   `---'   `---'   `-------
                :       :       :       :       :       :       :
            MISO---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
              /     \\ /     \\ /     \\ /     \\ /     \\ /     \\ /     \\
            -{  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  }------
              \\     / \\     / \\     / \\     / \\     / \\     / \\     /
               `---'   `---'   `---'   `---'   `---'   `---'   `---'

        The following diagram indicates when data is read when
        :attr:`clock_polarity` is :data:`False`, but :attr:`clock_phase` is
        :data:`True`, equivalent to CPHA 1:

        .. code-block:: text

                ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `---'   `---'   `---'   `-------
                    :       :       :       :       :       :       :
            MISO   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
                  /     \\ /     \\ /     \\ /     \\ /     \\ /     \\ /     \\
            -----{  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  X  Bit  }--
                  \\     / \\     / \\     / \\     / \\     / \\     / \\     /
                   `---'   `---'   `---'   `---'   `---'   `---'   `---'
        """
        return bool(self.clock_mode & 1)

    @clock_phase.setter
    def clock_phase(self, value):
        self.clock_mode = self.clock_mode & (~1) | bool(value)

    def _get_clock_mode(self):
        raise NotImplementedError

    def _set_clock_mode(self, value):
        raise SPIFixedClockMode("clock_mode cannot be changed on %r" % self)

    clock_mode = property(
        lambda self: self._get_clock_mode(),
        lambda self, value: self._set_clock_mode(value),
        doc="""\
        Presents a value representing the :attr:`clock_polarity` and
        :attr:`clock_phase` attributes combined according to the following
        table:

        +------+-----------------+--------------+
        | mode | polarity (CPOL) | phase (CPHA) |
        +======+=================+==============+
        | 0    | False           | False        |
        +------+-----------------+--------------+
        | 1    | False           | True         |
        +------+-----------------+--------------+
        | 2    | True            | False        |
        +------+-----------------+--------------+
        | 3    | True            | True         |
        +------+-----------------+--------------+

        Adjusting this value adjusts both the :attr:`clock_polarity` and
        :attr:`clock_phase` attributes simultaneously.
        """)

    def _get_lsb_first(self):
        return False

    def _set_lsb_first(self, value):
        raise SPIFixedBitOrder("lsb_first cannot be changed on %r" % self)

    lsb_first = property(
        lambda self: self._get_lsb_first(),
        lambda self, value: self._set_lsb_first(value),
        doc="""\
        Controls whether words are read and written LSB in (Least Significant
        Bit first) order. The default is :data:`False` indicating that words
        are read and written in MSB (Most Significant Bit first) order.
        Effectively, this controls the `Bit endianness`_ of the connection.

        The following diagram shows the a word containing the number 5 (binary
        0101) transmitted on MISO with :attr:`bits_per_word` set to 4, and
        :attr:`clock_mode` set to 0, when :attr:`lsb_first` is :data:`False`
        (the default):

        .. code-block:: text

                ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `-----
                :     ,-------. :     ,-------.
            MISO:     | :     | :     | :     |
                :     | :     | :     | :     |
            ----------' :     `-------' :     `----
                :       :       :       :
               MSB                     LSB

        And now with :attr:`lsb_first` set to :data:`True` (and all other
        parameters the same):

        .. code-block:: text

                ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `-----
              ,-------. :     ,-------. :
            MISO:     | :     | :     | :
              | :     | :     | :     | :
            --' :     `-------' :     `-----------
                :       :       :       :
               LSB                     MSB

        .. _Bit endianness: https://en.wikipedia.org/wiki/Endianness#Bit_endianness
        """)

    def _get_select_high(self):
        return False

    def _set_select_high(self, value):
        raise SPIFixedSelect("select_high cannot be changed on %r" % self)

    select_high = property(
        lambda self: self._get_select_high(),
        lambda self, value: self._set_select_high(value),
        doc="""\
        If :data:`False` (the default), the chip select line is considered
        active when it is pulled low. When set to :data:`True`, the chip select
        line is considered active when it is driven high.

        The following diagram shows the waveform of the chip select line, and
        the clock when :attr:`clock_polarity` is :data:`False`, and
        :attr:`select_high` is :data:`False` (the default):

        .. code-block:: text

            ---.                                                     ,------
            __ |                                                     |
            CS |      chip is selected, and will react to clock      |  idle
               `-----------------------------------------------------'

                ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `---'   `---'   `---'   `-------

        And when :attr:`select_high` is :data:`True`:

        .. code-block:: text

               ,-----------------------------------------------------.
            CS |      chip is selected, and will react to clock      |  idle
               |                                                     |
            ---'                                                     `------

                ,---.   ,---.   ,---.   ,---.   ,---.   ,---.   ,---.
            CLK |   |   |   |   |   |   |   |   |   |   |   |   |   |
                |   |   |   |   |   |   |   |   |   |   |   |   |   |
            ----'   `---'   `---'   `---'   `---'   `---'   `---'   `-------
        """)

    def _get_bits_per_word(self):
        return 8

    def _set_bits_per_word(self, value):
        raise SPIFixedWordSize("bits_per_word cannot be changed on %r" % self)

    bits_per_word = property(
        lambda self: self._get_bits_per_word(),
        lambda self, value: self._set_bits_per_word(value),
        doc="""\
        Controls the number of bits that make up a word, and thus where the
        word boundaries appear in the data stream, and the maximum value of a
        word. Defaults to 8 meaning that words are effectively bytes.

        Several implementations do not support non-byte-sized words.
        """)
