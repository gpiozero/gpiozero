# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
# Copyright (c) 2015-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2015-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2019 tuftii <pi@raspberrypi>
# Copyright (c) 2019 tuftii <3215045+tuftii@users.noreply.github.com>
# Copyright (c) 2019 Yisrael Dov Lebow <lebow@lebowtech.com>
# Copyright (c) 2019 Kosovan Sofiia <sofiia.kosovan@gmail.com>
# Copyright (c) 2016 Ian Harcombe <ian.harcombe@gmail.com>
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
    print_function,
    absolute_import,
    division,
)
str = type('')

from threading import Lock
from itertools import repeat, cycle, chain
from colorzero import Color
from collections import OrderedDict
try:
    from math import log2
except ImportError:
    from .compat import log2
import warnings

from .exc import OutputDeviceBadValue, GPIOPinMissing, PWMSoftwareFallback
from .devices import GPIODevice, Device, CompositeDevice
from .mixins import SourceMixin
from .threads import GPIOThread
from .tones import Tone
try:
    from .pins.pigpio import PiGPIOFactory
except ImportError:
    PiGPIOFactory = None

class OutputDevice(SourceMixin, GPIODevice):
    """
    Represents a generic GPIO output device.

    This class extends :class:`GPIODevice` to add facilities common to GPIO
    output devices: an :meth:`on` method to switch the device on, a
    corresponding :meth:`off` method, and a :meth:`toggle` method.

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the device will be off initially.  If
        :data:`None`, the device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on).  If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, active_high=True, initial_value=False,
            pin_factory=None):
        super(OutputDevice, self).__init__(pin, pin_factory=pin_factory)
        self._lock = Lock()
        self.active_high = active_high
        if initial_value is None:
            self.pin.function = 'output'
        else:
            self.pin.output_with_state(self._value_to_state(initial_value))

    def _value_to_state(self, value):
        return bool(self._active_state if value else self._inactive_state)

    def _write(self, value):
        try:
            self.pin.state = self._value_to_state(value)
        except AttributeError:
            self._check_open()
            raise

    def on(self):
        """
        Turns the device on.
        """
        self._write(True)

    def off(self):
        """
        Turns the device off.
        """
        self._write(False)

    def toggle(self):
        """
        Reverse the state of the device. If it's on, turn it off; if it's off,
        turn it on.
        """
        with self._lock:
            if self.is_active:
                self.off()
            else:
                self.on()

    @property
    def value(self):
        """
        Returns 1 if the device is currently active and 0 otherwise. Setting
        this property changes the state of the device.
        """
        return super(OutputDevice, self).value

    @value.setter
    def value(self, value):
        self._write(value)

    @property
    def active_high(self):
        """
        When :data:`True`, the :attr:`value` property is :data:`True` when the
        device's :attr:`~GPIODevice.pin` is high. When :data:`False` the
        :attr:`value` property is :data:`True` when the device's pin is low
        (i.e. the value is inverted).

        This property can be set after construction; be warned that changing it
        will invert :attr:`value` (i.e. changing this property doesn't change
        the device's pin state - it just changes how that state is
        interpreted).
        """
        return self._active_state

    @active_high.setter
    def active_high(self, value):
        self._active_state = True if value else False
        self._inactive_state = False if value else True

    def __repr__(self):
        try:
            return '<gpiozero.%s object on pin %r, active_high=%s, is_active=%s>' % (
                self.__class__.__name__, self.pin, self.active_high, self.is_active)
        except:
            return super(OutputDevice, self).__repr__()


class DigitalOutputDevice(OutputDevice):
    """
    Represents a generic output device with typical on/off behaviour.

    This class extends :class:`OutputDevice` with a :meth:`blink` method which
    uses an optional background thread to handle toggling the device state
    without further interaction.

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the device will be off initially.  If
        :data:`None`, the device will be left in whatever state the pin is
        found in when configured for output (warning: this can be on).  If
        :data:`True`, the device will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, active_high=True, initial_value=False,
            pin_factory=None):
        self._blink_thread = None
        self._controller = None
        super(DigitalOutputDevice, self).__init__(
            pin, active_high, initial_value, pin_factory=pin_factory
        )

    @property
    def value(self):
        return super(DigitalOutputDevice, self).value

    @value.setter
    def value(self, value):
        self._stop_blink()
        self._write(value)

    def close(self):
        self._stop_blink()
        super(DigitalOutputDevice, self).close()

    def on(self):
        self._stop_blink()
        self._write(True)

    def off(self):
        self._stop_blink()
        self._write(False)

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        """
        Make the device turn on and off repeatedly.

        :param float on_time:
            Number of seconds on. Defaults to 1 second.

        :param float off_time:
            Number of seconds off. Defaults to 1 second.

        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_device, args=(on_time, off_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _stop_blink(self):
        if getattr(self, '_controller', None):
            self._controller._stop_blink(self)
        self._controller = None
        if getattr(self, '_blink_thread', None):
            self._blink_thread.stop()
        self._blink_thread = None

    def _blink_device(self, on_time, off_time, n):
        iterable = repeat(0) if n is None else repeat(0, n)
        for _ in iterable:
            self._write(True)
            if self._blink_thread.stopping.wait(on_time):
                break
            self._write(False)
            if self._blink_thread.stopping.wait(off_time):
                break


class LED(DigitalOutputDevice):
    """
    Extends :class:`DigitalOutputDevice` and represents a light emitting diode
    (LED).

    Connect the cathode (short leg, flat side) of the LED to a ground pin;
    connect the anode (longer leg) to a limiting resistor; connect the other
    side of the limiting resistor to a GPIO pin (the limiting resistor can be
    placed either side of the LED).

    The following example will light the LED::

        from gpiozero import LED

        led = LED(17)
        led.on()

    :type pin: int or str
    :param pin:
        The GPIO pin which the LED is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the LED will operate normally with the
        circuit described above. If :data:`False` you should wire the cathode
        to the GPIO pin, and the anode to a 3V3 pin (via a limiting resistor).

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the LED will be off initially.  If
        :data:`None`, the LED will be left in whatever state the pin is found
        in when configured for output (warning: this can be on).  If
        :data:`True`, the LED will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    pass

LED.is_lit = LED.is_active


class Buzzer(DigitalOutputDevice):
    """
    Extends :class:`DigitalOutputDevice` and represents a digital buzzer
    component.

    .. note::

        This interface is only capable of simple on/off commands, and is not
        capable of playing a variety of tones (see :class:`TonalBuzzer`).

    Connect the cathode (negative pin) of the buzzer to a ground pin; connect
    the other side to any GPIO pin.

    The following example will sound the buzzer::

        from gpiozero import Buzzer

        bz = Buzzer(3)
        bz.on()

    :type pin: int or str
    :param pin:
        The GPIO pin which the buzzer is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the buzzer will operate normally with
        the circuit described above. If :data:`False` you should wire the
        cathode to the GPIO pin, and the anode to a 3V3 pin.

    :type initial_value: bool or None
    :param initial_value:
        If :data:`False` (the default), the buzzer will be silent initially. If
        :data:`None`, the buzzer will be left in whatever state the pin is
        found in when configured for output (warning: this can be on). If
        :data:`True`, the buzzer will be switched on initially.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    pass

Buzzer.beep = Buzzer.blink


class PWMOutputDevice(OutputDevice):
    """
    Generic output device configured for pulse-width modulation (PWM).

    :type pin: int or str
    :param pin:
        The GPIO pin that the device is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :param float initial_value:
        If 0 (the default), the device's duty cycle will be 0 initially.
        Other values between 0 and 1 can be specified as an initial duty cycle.
        Note that :data:`None` cannot be specified (unlike the parent class) as
        there is no way to tell PWM not to alter the state of the pin.

    :param int frequency:
        The frequency (in Hz) of pulses emitted to drive the device. Defaults
        to 100Hz.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, active_high=True, initial_value=0, frequency=100,
            pin_factory=None):
        self._blink_thread = None
        self._controller = None
        if not 0 <= initial_value <= 1:
            raise OutputDeviceBadValue("initial_value must be between 0 and 1")
        super(PWMOutputDevice, self).__init__(
            pin, active_high, initial_value=None, pin_factory=pin_factory
        )
        try:
            # XXX need a way of setting these together
            self.pin.frequency = frequency
            self.value = initial_value
        except:
            self.close()
            raise

    def close(self):
        try:
            self._stop_blink()
        except AttributeError:
            pass
        try:
            self.pin.frequency = None
        except AttributeError:
            # If the pin's already None, ignore the exception
            pass
        super(PWMOutputDevice, self).close()

    def _state_to_value(self, state):
        return float(state if self.active_high else 1 - state)

    def _value_to_state(self, value):
        return float(value if self.active_high else 1 - value)

    def _write(self, value):
        if not 0 <= value <= 1:
            raise OutputDeviceBadValue("PWM value must be between 0 and 1")
        super(PWMOutputDevice, self)._write(value)

    @property
    def value(self):
        """
        The duty cycle of the PWM device. 0.0 is off, 1.0 is fully on. Values
        in between may be specified for varying levels of power in the device.
        """
        return super(PWMOutputDevice, self).value

    @value.setter
    def value(self, value):
        self._stop_blink()
        self._write(value)

    def on(self):
        self._stop_blink()
        self._write(1)

    def off(self):
        self._stop_blink()
        self._write(0)

    def toggle(self):
        """
        Toggle the state of the device. If the device is currently off
        (:attr:`value` is 0.0), this changes it to "fully" on (:attr:`value` is
        1.0).  If the device has a duty cycle (:attr:`value`) of 0.1, this will
        toggle it to 0.9, and so on.
        """
        self._stop_blink()
        self.value = 1 - self.value

    @property
    def is_active(self):
        """
        Returns :data:`True` if the device is currently active (:attr:`value`
        is non-zero) and :data:`False` otherwise.
        """
        return self.value != 0

    @property
    def frequency(self):
        """
        The frequency of the pulses used with the PWM device, in Hz. The
        default is 100Hz.
        """
        return self.pin.frequency

    @frequency.setter
    def frequency(self, value):
        self.pin.frequency = value

    def blink(
            self, on_time=1, off_time=1, fade_in_time=0, fade_out_time=0,
            n=None, background=True):
        """
        Make the device turn on and off repeatedly.

        :param float on_time:
            Number of seconds on. Defaults to 1 second.

        :param float off_time:
            Number of seconds off. Defaults to 1 second.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 0.

        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_device,
            args=(on_time, off_time, fade_in_time, fade_out_time, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def pulse(self, fade_in_time=1, fade_out_time=1, n=None, background=True):
        """
        Make the device fade in and out repeatedly.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.

        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue pulsing and return immediately. If :data:`False`, only
            return when the pulse is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        on_time = off_time = 0
        self.blink(
            on_time, off_time, fade_in_time, fade_out_time, n, background
        )

    def _stop_blink(self):
        if self._controller:
            self._controller._stop_blink(self)
            self._controller = None
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_device(
            self, on_time, off_time, fade_in_time, fade_out_time, n, fps=25):
        sequence = []
        if fade_in_time > 0:
            sequence += [
                (i * (1 / fps) / fade_in_time, 1 / fps)
                for i in range(int(fps * fade_in_time))
                ]
        sequence.append((1, on_time))
        if fade_out_time > 0:
            sequence += [
                (1 - (i * (1 / fps) / fade_out_time), 1 / fps)
                for i in range(int(fps * fade_out_time))
                ]
        sequence.append((0, off_time))
        sequence = (
                cycle(sequence) if n is None else
                chain.from_iterable(repeat(sequence, n))
                )
        for value, delay in sequence:
            self._write(value)
            if self._blink_thread.stopping.wait(delay):
                break


class TonalBuzzer(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a tonal buzzer.

    :type pin: int or str
    :param pin:
        The GPIO pin which the buzzer is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param float initial_value:
        If :data:`None` (the default), the buzzer will be off initially. Values
        between -1 and 1 can be specified as an initial value for the buzzer.

    :type mid_tone: int or str
    :param mid_tone:
        The tone which is represented the device's middle value (0). The
        default is "A4" (MIDI note 69).

    :param int octaves:
        The number of octaves to allow away from the base note. The default is
        1, meaning a value of -1 goes one octave below the base note, and one
        above, i.e. from A3 to A5 with the default base note of A4.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. note::

        Note that this class does not currently work with
        :class:`~gpiozero.pins.pigpio.PiGPIOFactory`.
    """

    def __init__(self, pin=None, initial_value=None, mid_tone=Tone("A4"),
                 octaves=1, pin_factory=None):
        self._mid_tone = None
        super(TonalBuzzer, self).__init__(
            pwm_device=PWMOutputDevice(
                pin=pin, pin_factory=pin_factory
            ), pin_factory=pin_factory)
        try:
            self._mid_tone = Tone(mid_tone)
            if not (0 < octaves <= 9):
                raise ValueError('octaves must be between 1 and 9')
            self._octaves = octaves
            try:
                self.min_tone.note
            except ValueError:
                raise ValueError(
                    '%r is too low for %d octaves' %
                    (self._mid_tone, self._octaves))
            try:
                self.max_tone.note
            except ValueError:
                raise ValueError(
                    '%r is too high for %d octaves' %
                    (self._mid_tone, self._octaves))
            self.value = initial_value
        except:
            self.close()
            raise

    def __repr__(self):
        try:
            if self.value is None:
                return '<gpiozero.TonalBuzzer object on pin %r, silent>' % (
                    self.pwm_device.pin,)
            else:
                return '<gpiozero.TonalBuzzer object on pin %r, playing %s>' % (
                    self.pwm_device.pin, self.tone.note)
        except:
            return super(TonalBuzzer, self).__repr__()

    def play(self, tone):
        """
        Play the given *tone*. This can either be an instance of
        :class:`~gpiozero.tones.Tone` or can be anything that could be used to
        construct an instance of :class:`~gpiozero.tones.Tone`.

        For example::

            >>> from gpiozero import TonalBuzzer
            >>> from gpiozero.tones import Tone
            >>> b = TonalBuzzer(17)
            >>> b.play(Tone("A4"))
            >>> b.play(Tone(220.0)) # Hz
            >>> b.play(Tone(60)) # middle C in MIDI notation
            >>> b.play("A4")
            >>> b.play(220.0)
            >>> b.play(60)
        """
        if tone is None:
            self.value = None
        else:
            if not isinstance(tone, Tone):
                tone = Tone(tone)
            freq = tone.frequency
            if self.min_tone.frequency <= tone <= self.max_tone.frequency:
                self.pwm_device.pin.frequency = freq
                self.pwm_device.value = 0.5
            else:
                raise ValueError("tone is out of the device's range")

    def stop(self):
        """
        Turn the buzzer off. This is equivalent to setting :attr:`value` to
        :data:`None`.
        """
        self.value = None

    @property
    def tone(self):
        """
        Returns the :class:`~gpiozero.tones.Tone` that the buzzer is currently
        playing, or :data:`None` if the buzzer is silent. This property can
        also be set to play the specified tone.
        """
        if self.pwm_device.pin.frequency is None:
            return None
        else:
            return Tone.from_frequency(self.pwm_device.pin.frequency)

    @tone.setter
    def tone(self, value):
        self.play(value)

    @property
    def value(self):
        """
        Represents the state of the buzzer as a value between -1 (representing
        the minimum tone) and 1 (representing the maximum tone). This can also
        be the special value :data:`None` indicating that the buzzer is
        currently silent.
        """
        if self.pwm_device.pin.frequency is None:
            return None
        else:
            try:
                return log2(
                    self.pwm_device.pin.frequency / self.mid_tone.frequency
                ) / self.octaves
            except ZeroDivisionError:
                return 0.0

    @value.setter
    def value(self, value):
        if value is None:
            self.pwm_device.pin.frequency = None
        elif -1 <= value <= 1:
            freq = self.mid_tone.frequency * 2 ** (self.octaves * value)
            self.pwm_device.pin.frequency = freq
            self.pwm_device.value = 0.5
        else:
            raise OutputDeviceBadValue(
                'TonalBuzzer value must be between -1 and 1, or None')

    @property
    def is_active(self):
        """
        Returns :data:`True` if the buzzer is currently playing, otherwise
        :data:`False`.
        """
        return self.value is not None

    @property
    def octaves(self):
        """
        The number of octaves available (above and below mid_tone).
        """
        return self._octaves

    @property
    def min_tone(self):
        """
        The lowest tone that the buzzer can play, i.e. the tone played
        when :attr:`value` is -1.
        """
        return self._mid_tone.down(12 * self.octaves)

    @property
    def mid_tone(self):
        """
        The middle tone available, i.e. the tone played when :attr:`value` is
        0.
        """
        return self._mid_tone

    @property
    def max_tone(self):
        """
        The highest tone that the buzzer can play, i.e. the tone played when
        :attr:`value` is 1.
        """
        return self._mid_tone.up(12 * self.octaves)


class PWMLED(PWMOutputDevice):
    """
    Extends :class:`PWMOutputDevice` and represents a light emitting diode
    (LED) with variable brightness.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the LED, and the cathode (short leg) to ground, with
    an optional resistor to prevent the LED from burning out.

    :type pin: int or str
    :param pin:
        The GPIO pin which the LED is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param bool active_high:
        If :data:`True` (the default), the :meth:`on` method will set the GPIO
        to HIGH. If :data:`False`, the :meth:`on` method will set the GPIO to
        LOW (the :meth:`off` method always does the opposite).

    :param float initial_value:
        If ``0`` (the default), the LED will be off initially. Other values
        between 0 and 1 can be specified as an initial brightness for the LED.
        Note that :data:`None` cannot be specified (unlike the parent class) as
        there is no way to tell PWM not to alter the state of the pin.

    :param int frequency:
        The frequency (in Hz) of pulses emitted to drive the LED. Defaults
        to 100Hz.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    pass

PWMLED.is_lit = PWMLED.is_active


class RGBLED(SourceMixin, Device):
    """
    Extends :class:`Device` and represents a full color LED component (composed
    of red, green, and blue LEDs).

    Connect the common cathode (longest leg) to a ground pin; connect each of
    the other legs (representing the red, green, and blue anodes) to any GPIO
    pins.  You should use three limiting resistors (one per anode).

    The following code will make the LED yellow::

        from gpiozero import RGBLED

        led = RGBLED(2, 3, 4)
        led.color = (1, 1, 0)

    The `colorzero`_ library is also supported::

        from gpiozero import RGBLED
        from colorzero import Color

        led = RGBLED(2, 3, 4)
        led.color = Color('yellow')

    :type red: int or str
    :param red:
        The GPIO pin that controls the red component of the RGB LED. See
        :ref:`pin-numbering` for valid pin numbers. If this is :data:`None` a
        :exc:`GPIODeviceError` will be raised.

    :type green: int or str
    :param green:
        The GPIO pin that controls the green component of the RGB LED.

    :type blue: int or str
    :param blue:
        The GPIO pin that controls the blue component of the RGB LED.

    :param bool active_high:
        Set to :data:`True` (the default) for common cathode RGB LEDs. If you
        are using a common anode RGB LED, set this to :data:`False`.

    :type initial_value: ~colorzero.Color or tuple
    :param initial_value:
        The initial color for the RGB LED. Defaults to black ``(0, 0, 0)``.

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMLED` instances for
        each component of the RGBLED. If :data:`False`, construct regular
        :class:`LED` instances, which prevents smooth color graduations.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _colorzero: https://colorzero.readthedocs.io/
    """
    def __init__(
            self, red=None, green=None, blue=None, active_high=True,
            initial_value=(0, 0, 0), pwm=True, pin_factory=None):
        self._leds = ()
        self._blink_thread = None
        if not all(p is not None for p in [red, green, blue]):
            raise GPIOPinMissing('red, green, and blue pins must be provided')
        LEDClass = PWMLED if pwm else LED
        super(RGBLED, self).__init__(pin_factory=pin_factory)
        self._leds = tuple(
            LEDClass(pin, active_high, pin_factory=pin_factory)
            for pin in (red, green, blue)
        )
        self.value = initial_value

    def close(self):
        if getattr(self, '_leds', None):
            self._stop_blink()
            for led in self._leds:
                led.close()
        self._leds = ()
        super(RGBLED, self).close()

    @property
    def closed(self):
        return len(self._leds) == 0

    @property
    def value(self):
        """
        Represents the color of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 1 if *pwm* was :data:`True`
        when the class was constructed (and only 0 or 1 if not).

        For example, red would be ``(1, 0, 0)`` and yellow would be ``(1, 1,
        0)``, while orange would be ``(1, 0.5, 0)``.
        """
        return tuple(led.value for led in self._leds)

    @value.setter
    def value(self, value):
        for component in value:
            if not 0 <= component <= 1:
                raise OutputDeviceBadValue(
                    'each RGB color component must be between 0 and 1')
            if isinstance(self._leds[0], LED):
                if component not in (0, 1):
                    raise OutputDeviceBadValue(
                        'each RGB color component must be 0 or 1 with non-PWM '
                        'RGBLEDs')
        self._stop_blink()
        for led, v in zip(self._leds, value):
            led.value = v

    @property
    def is_active(self):
        """
        Returns :data:`True` if the LED is currently active (not black) and
        :data:`False` otherwise.
        """
        return self.value != (0, 0, 0)

    is_lit = is_active

    @property
    def color(self):
        """
        Represents the color of the LED as a :class:`~colorzero.Color` object.
        """
        return Color(*self.value)

    @color.setter
    def color(self, value):
        self.value = value

    @property
    def red(self):
        """
        Represents the red element of the LED as a :class:`~colorzero.Red`
        object.
        """
        return self.color.red

    @red.setter
    def red(self, value):
        self._stop_blink()
        r, g, b = self.value
        self.value = value, g, b

    @property
    def green(self):
        """
        Represents the green element of the LED as a :class:`~colorzero.Green`
        object.
        """
        return self.color.green

    @green.setter
    def green(self, value):
        self._stop_blink()
        r, g, b = self.value
        self.value = r, value, b

    @property
    def blue(self):
        """
        Represents the blue element of the LED as a :class:`~colorzero.Blue`
        object.
        """
        return self.color.blue

    @blue.setter
    def blue(self, value):
        self._stop_blink()
        r, g, b = self.value
        self.value = r, g, value

    def on(self):
        """
        Turn the LED on. This equivalent to setting the LED color to white
        ``(1, 1, 1)``.
        """
        self.value = (1, 1, 1)

    def off(self):
        """
        Turn the LED off. This is equivalent to setting the LED color to black
        ``(0, 0, 0)``.
        """
        self.value = (0, 0, 0)

    def toggle(self):
        """
        Toggle the state of the device. If the device is currently off
        (:attr:`value` is ``(0, 0, 0)``), this changes it to "fully" on
        (:attr:`value` is ``(1, 1, 1)``).  If the device has a specific color,
        this method inverts the color.
        """
        r, g, b = self.value
        self.value = (1 - r, 1 - g, 1 - b)

    def blink(
            self, on_time=1, off_time=1, fade_in_time=0, fade_out_time=0,
            on_color=(1, 1, 1), off_color=(0, 0, 0), n=None, background=True):
        """
        Make the device turn on and off repeatedly.

        :param float on_time:
            Number of seconds on. Defaults to 1 second.

        :param float off_time:
            Number of seconds off. Defaults to 1 second.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 0. Must be 0 if
            *pwm* was :data:`False` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 0. Must be 0 if
            *pwm* was :data:`False` when the class was constructed
            (:exc:`ValueError` will be raised if not).

        :type on_color: ~colorzero.Color or tuple
        :param on_color:
            The color to use when the LED is "on". Defaults to white.

        :type off_color: ~colorzero.Color or tuple
        :param off_color:
            The color to use when the LED is "off". Defaults to black.

        :type n: int or None
        :param n:
            Number of times to blink; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue blinking and return immediately. If :data:`False`, only
            return when the blink is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        if isinstance(self._leds[0], LED):
            if fade_in_time:
                raise ValueError('fade_in_time must be 0 with non-PWM RGBLEDs')
            if fade_out_time:
                raise ValueError('fade_out_time must be 0 with non-PWM RGBLEDs')
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_device,
            args=(
                on_time, off_time, fade_in_time, fade_out_time,
                on_color, off_color, n
            )
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def pulse(
            self, fade_in_time=1, fade_out_time=1,
            on_color=(1, 1, 1), off_color=(0, 0, 0), n=None, background=True):
        """
        Make the device fade in and out repeatedly.

        :param float fade_in_time:
            Number of seconds to spend fading in. Defaults to 1.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 1.

        :type on_color: ~colorzero.Color or tuple
        :param on_color:
            The color to use when the LED is "on". Defaults to white.

        :type off_color: ~colorzero.Color or tuple
        :param off_color:
            The color to use when the LED is "off". Defaults to black.

        :type n: int or None
        :param n:
            Number of times to pulse; :data:`None` (the default) means forever.

        :param bool background:
            If :data:`True` (the default), start a background thread to
            continue pulsing and return immediately. If :data:`False`, only
            return when the pulse is finished (warning: the default value of
            *n* will result in this method never returning).
        """
        on_time = off_time = 0
        self.blink(
            on_time, off_time, fade_in_time, fade_out_time,
            on_color, off_color, n, background
        )

    def _stop_blink(self, led=None):
        # If this is called with a single led, we stop all blinking anyway
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_device(
            self, on_time, off_time, fade_in_time, fade_out_time, on_color,
            off_color, n, fps=25):
        # Define a simple lambda to perform linear interpolation between
        # off_color and on_color
        lerp = lambda t, fade_in: tuple(
            (1 - t) * off + t * on
            if fade_in else
            (1 - t) * on + t * off
            for off, on in zip(off_color, on_color)
            )
        sequence = []
        if fade_in_time > 0:
            sequence += [
                (lerp(i * (1 / fps) / fade_in_time, True), 1 / fps)
                for i in range(int(fps * fade_in_time))
                ]
        sequence.append((on_color, on_time))
        if fade_out_time > 0:
            sequence += [
                (lerp(i * (1 / fps) / fade_out_time, False), 1 / fps)
                for i in range(int(fps * fade_out_time))
                ]
        sequence.append((off_color, off_time))
        sequence = (
                cycle(sequence) if n is None else
                chain.from_iterable(repeat(sequence, n))
                )
        for l in self._leds:
            l._controller = self
        for value, delay in sequence:
            for l, v in zip(self._leds, value):
                l._write(v)
            if self._blink_thread.stopping.wait(delay):
                break


class Motor(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor
    connected to a bi-directional motor driver circuit (i.e. an `H-bridge`_).

    Attach an `H-bridge`_ motor controller to your Pi; connect a power source
    (e.g. a battery pack or the 5V pin) to the controller; connect the outputs
    of the controller board to the two terminals of the motor; connect the
    inputs of the controller board to two GPIO pins.

    .. _H-bridge: https://en.wikipedia.org/wiki/H_bridge

    The following code will make the motor turn "forwards"::

        from gpiozero import Motor

        motor = Motor(17, 18)
        motor.forward()

    :type forward: int or str
    :param forward:
        The GPIO pin that the forward input of the motor driver chip is
        connected to. See :ref:`pin-numbering` for valid pin numbers. If this
        is :data:`None` a :exc:`GPIODeviceError` will be raised.

    :type backward: int or str
    :param backward:
        The GPIO pin that the backward input of the motor driver chip is
        connected to. See :ref:`pin-numbering` for valid pin numbers. If this
        is :data:`None` a :exc:`GPIODeviceError` will be raised.

    :type enable: int or str or None
    :param enable:
        The GPIO pin that enables the motor. Required for *some* motor
        controller boards. See :ref:`pin-numbering` for valid pin numbers.

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If :data:`False`, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, forward=None, backward=None, enable=None, pwm=True,
                 pin_factory=None):
        if not all(p is not None for p in [forward, backward]):
            raise GPIOPinMissing(
                'forward and backward pins must be provided'
            )
        PinClass = PWMOutputDevice if pwm else DigitalOutputDevice
        devices = OrderedDict((
            ('forward_device', PinClass(forward, pin_factory=pin_factory)),
            ('backward_device', PinClass(backward, pin_factory=pin_factory)),
        ))
        if enable is not None:
            devices['enable_device'] = DigitalOutputDevice(
                enable,
                initial_value=True,
                pin_factory=pin_factory
            )
        super(Motor, self).__init__(_order=devices.keys(), **devices)

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward), with 0 representing
        stopped.
        """
        return self.forward_device.value - self.backward_device.value

    @value.setter
    def value(self, value):
        if not -1 <= value <= 1:
            raise OutputDeviceBadValue("Motor value must be between -1 and 1")
        if value > 0:
            try:
                self.forward(value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        elif value < 0:
            try:
               self.backward(-value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        else:
            self.stop()

    @property
    def is_active(self):
        """
        Returns :data:`True` if the motor is currently running and
        :data:`False` otherwise.
        """
        return self.value != 0

    def forward(self, speed=1):
        """
        Drive the motor forwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if *pwm* was
            :data:`True` when the class was constructed (and only 0 or 1 if
            not).
        """
        if not 0 <= speed <= 1:
            raise ValueError('forward speed must be between 0 and 1')
        if isinstance(self.forward_device, DigitalOutputDevice):
            if speed not in (0, 1):
                raise ValueError(
                    'forward speed must be 0 or 1 with non-PWM Motors')
        self.backward_device.off()
        self.forward_device.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if *pwm* was
            :data:`True` when the class was constructed (and only 0 or 1 if
            not).
        """
        if not 0 <= speed <= 1:
            raise ValueError('backward speed must be between 0 and 1')
        if isinstance(self.backward_device, DigitalOutputDevice):
            if speed not in (0, 1):
                raise ValueError(
                    'backward speed must be 0 or 1 with non-PWM Motors')
        self.forward_device.off()
        self.backward_device.value = speed

    def reverse(self):
        """
        Reverse the current direction of the motor. If the motor is currently
        idle this does nothing. Otherwise, the motor's direction will be
        reversed at the current speed.
        """
        self.value = -self.value

    def stop(self):
        """
        Stop the motor.
        """
        self.forward_device.off()
        self.backward_device.off()


class PhaseEnableMotor(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor connected
    to a Phase/Enable motor driver circuit; the phase of the driver controls
    whether the motor turns forwards or backwards, while enable controls the
    speed with PWM.

    The following code will make the motor turn "forwards"::

        from gpiozero import PhaseEnableMotor
        motor = PhaseEnableMotor(12, 5)
        motor.forward()

    :type phase: int or str
    :param phase:
        The GPIO pin that the phase (direction) input of the motor driver chip
        is connected to. See :ref:`pin-numbering` for valid pin numbers. If
        this is :data:`None` a :exc:`GPIODeviceError` will be raised.

    :type enable: int or str
    :param enable:
        The GPIO pin that the enable (speed) input of the motor driver chip
        is connected to. See :ref:`pin-numbering` for valid pin numbers. If
        this is :data:`None` a :exc:`GPIODeviceError` will be raised.

    :param bool pwm:
        If :data:`True` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If :data:`False`, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(self, phase=None, enable=None, pwm=True, pin_factory=None):
        if not all([phase, enable]):
            raise GPIOPinMissing('phase and enable pins must be provided')
        PinClass = PWMOutputDevice if pwm else DigitalOutputDevice
        super(PhaseEnableMotor, self).__init__(
            phase_device=DigitalOutputDevice(phase, pin_factory=pin_factory),
            enable_device=PinClass(enable, pin_factory=pin_factory),
            _order=('phase_device', 'enable_device'),
            pin_factory=pin_factory
        )

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward).
        """
        return (
            -self.enable_device.value
            if self.phase_device.is_active else
            self.enable_device.value
        )

    @value.setter
    def value(self, value):
        if not -1 <= value <= 1:
            raise OutputDeviceBadValue("Motor value must be between -1 and 1")
        if value > 0:
            self.forward(value)
        elif value < 0:
            self.backward(-value)
        else:
            self.stop()

    @property
    def is_active(self):
        """
        Returns :data:`True` if the motor is currently running and
        :data:`False` otherwise.
        """
        return self.value != 0

    def forward(self, speed=1):
        """
        Drive the motor forwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed).
        """
        if isinstance(self.enable_device, DigitalOutputDevice):
            if speed not in (0, 1):
                raise ValueError(
                    'forward speed must be 0 or 1 with non-PWM Motors')
        self.enable_device.off()
        self.phase_device.off()
        self.enable_device.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed).
        """
        if isinstance(self.enable_device, DigitalOutputDevice):
            if speed not in (0, 1):
                raise ValueError(
                    'backward speed must be 0 or 1 with non-PWM Motors')
        self.enable_device.off()
        self.phase_device.on()
        self.enable_device.value = speed

    def reverse(self):
        """
        Reverse the current direction of the motor. If the motor is currently
        idle this does nothing. Otherwise, the motor's direction will be
        reversed at the current speed.
        """
        self.value = -self.value

    def stop(self):
        """
        Stop the motor.
        """
        self.enable_device.off()


class Servo(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a PWM-controlled servo
    motor connected to a GPIO pin.

    Connect a power source (e.g. a battery pack or the 5V pin) to the power
    cable of the servo (this is typically colored red); connect the ground
    cable of the servo (typically colored black or brown) to the negative of
    your battery pack, or a GND pin; connect the final cable (typically colored
    white or orange) to the GPIO pin you wish to use for controlling the servo.

    The following code will make the servo move between its minimum, maximum,
    and mid-point positions with a pause between each::

        from gpiozero import Servo
        from time import sleep

        servo = Servo(17)

        while True:
            servo.min()
            sleep(1)
            servo.mid()
            sleep(1)
            servo.max()
            sleep(1)

    You can also use the :attr:`value` property to move the servo to a
    particular position, on a scale from -1 (min) to 1 (max) where 0 is the
    mid-point::

        from gpiozero import Servo

        servo = Servo(17)

        servo.value = 0.5

    .. note::

        To reduce servo jitter, use the pigpio pin driver rather than the default
        RPi.GPIO driver (pigpio uses DMA sampling for much more precise edge
        timing). See :ref:`changing-pin-factory` for further information.

    :type pin: int or str
    :param pin:
        The GPIO pin that the servo is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param float initial_value:
        If ``0`` (the default), the device's mid-point will be set initially.
        Other values between -1 and +1 can be specified as an initial position.
        :data:`None` means to start the servo un-controlled (see
        :attr:`value`).

    :param float min_pulse_width:
        The pulse width corresponding to the servo's minimum position. This
        defaults to 1ms.

    :param float max_pulse_width:
        The pulse width corresponding to the servo's maximum position. This
        defaults to 2ms.

    :param float frame_width:
        The length of time between servo control pulses measured in seconds.
        This defaults to 20ms which is a common value for servos.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, initial_value=0.0,
            min_pulse_width=1/1000, max_pulse_width=2/1000,
            frame_width=20/1000, pin_factory=None):
        if min_pulse_width >= max_pulse_width:
            raise ValueError('min_pulse_width must be less than max_pulse_width')
        if max_pulse_width >= frame_width:
            raise ValueError('max_pulse_width must be less than frame_width')
        self._frame_width = frame_width
        self._min_dc = min_pulse_width / frame_width
        self._dc_range = (max_pulse_width - min_pulse_width) / frame_width
        self._min_value = -1
        self._value_range = 2
        super(Servo, self).__init__(
            pwm_device=PWMOutputDevice(
                pin, frequency=int(1 / frame_width), pin_factory=pin_factory
            ),
            pin_factory=pin_factory
        )

        if PiGPIOFactory is None or not isinstance(self.pin_factory, PiGPIOFactory):
            warnings.warn(PWMSoftwareFallback(
                'To reduce servo jitter, use the pigpio pin factory.'
                'See https://gpiozero.readthedocs.io/en/stable/api_output.html#servo for more info'
            ))

        try:
            self.value = initial_value
        except:
            self.close()
            raise

    @property
    def frame_width(self):
        """
        The time between control pulses, measured in seconds.
        """
        return self._frame_width

    @property
    def min_pulse_width(self):
        """
        The control pulse width corresponding to the servo's minimum position,
        measured in seconds.
        """
        return self._min_dc * self.frame_width

    @property
    def max_pulse_width(self):
        """
        The control pulse width corresponding to the servo's maximum position,
        measured in seconds.
        """
        return (self._dc_range * self.frame_width) + self.min_pulse_width

    @property
    def pulse_width(self):
        """
        Returns the current pulse width controlling the servo.
        """
        if self.pwm_device.pin.frequency is None:
            return None
        else:
            return self.pwm_device.pin.state * self.frame_width

    @pulse_width.setter
    def pulse_width(self, value):
        self.pwm_device.pin.state = value / self.frame_width

    def min(self):
        """
        Set the servo to its minimum position.
        """
        self.value = -1

    def mid(self):
        """
        Set the servo to its mid-point position.
        """
        self.value = 0

    def max(self):
        """
        Set the servo to its maximum position.
        """
        self.value = 1

    def detach(self):
        """
        Temporarily disable control of the servo. This is equivalent to
        setting :attr:`value` to :data:`None`.
        """
        self.value = None

    def _get_value(self):
        if self.pwm_device.pin.frequency is None:
            return None
        else:
            return (
                ((self.pwm_device.pin.state - self._min_dc) / self._dc_range) *
                self._value_range + self._min_value)

    @property
    def value(self):
        """
        Represents the position of the servo as a value between -1 (the minimum
        position) and +1 (the maximum position). This can also be the special
        value :data:`None` indicating that the servo is currently
        "uncontrolled", i.e. that no control signal is being sent. Typically
        this means the servo's position remains unchanged, but that it can be
        moved by hand.
        """
        result = self._get_value()
        if result is None:
            return result
        else:
            # NOTE: This round() only exists to ensure we don't confuse people
            # by returning 2.220446049250313e-16 as the default initial value
            # instead of 0. The reason _get_value and _set_value are split
            # out is for descendents that require the un-rounded values for
            # accuracy
            return round(result, 14)

    @value.setter
    def value(self, value):
        if value is None:
            self.pwm_device.pin.frequency = None
        elif -1 <= value <= 1:
            self.pwm_device.pin.frequency = int(1 / self.frame_width)
            self.pwm_device.pin.state = (
                self._min_dc + self._dc_range *
                ((value - self._min_value) / self._value_range)
                )
        else:
            raise OutputDeviceBadValue(
                "Servo value must be between -1 and 1, or None")

    @property
    def is_active(self):
        return self.value is not None


class AngularServo(Servo):
    """
    Extends :class:`Servo` and represents a rotational PWM-controlled servo
    motor which can be set to particular angles (assuming valid minimum and
    maximum angles are provided to the constructor).

    Connect a power source (e.g. a battery pack or the 5V pin) to the power
    cable of the servo (this is typically colored red); connect the ground
    cable of the servo (typically colored black or brown) to the negative of
    your battery pack, or a GND pin; connect the final cable (typically colored
    white or orange) to the GPIO pin you wish to use for controlling the servo.

    Next, calibrate the angles that the servo can rotate to. In an interactive
    Python session, construct a :class:`Servo` instance. The servo should move
    to its mid-point by default. Set the servo to its minimum value, and
    measure the angle from the mid-point. Set the servo to its maximum value,
    and again measure the angle::

        >>> from gpiozero import Servo
        >>> s = Servo(17)
        >>> s.min() # measure the angle
        >>> s.max() # measure the angle

    You should now be able to construct an :class:`AngularServo` instance
    with the correct bounds::

        >>> from gpiozero import AngularServo
        >>> s = AngularServo(17, min_angle=-42, max_angle=44)
        >>> s.angle = 0.0
        >>> s.angle
        0.0
        >>> s.angle = 15
        >>> s.angle
        15.0

    .. note::

        You can set *min_angle* greater than *max_angle* if you wish to reverse
        the sense of the angles (e.g. ``min_angle=45, max_angle=-45``). This
        can be useful with servos that rotate in the opposite direction to your
        expectations of minimum and maximum.

    :type pin: int or str
    :param pin:
        The GPIO pin that the servo is connected to. See :ref:`pin-numbering`
        for valid pin numbers. If this is :data:`None` a :exc:`GPIODeviceError`
        will be raised.

    :param float initial_angle:
        Sets the servo's initial angle to the specified value. The default is
        0. The value specified must be between *min_angle* and *max_angle*
        inclusive. :data:`None` means to start the servo un-controlled (see
        :attr:`value`).

    :param float min_angle:
        Sets the minimum angle that the servo can rotate to. This defaults to
        -90, but should be set to whatever you measure from your servo during
        calibration.

    :param float max_angle:
        Sets the maximum angle that the servo can rotate to. This defaults to
        90, but should be set to whatever you measure from your servo during
        calibration.

    :param float min_pulse_width:
        The pulse width corresponding to the servo's minimum position. This
        defaults to 1ms.

    :param float max_pulse_width:
        The pulse width corresponding to the servo's maximum position. This
        defaults to 2ms.

    :param float frame_width:
        The length of time between servo control pulses measured in seconds.
        This defaults to 20ms which is a common value for servos.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
    """
    def __init__(
            self, pin=None, initial_angle=0.0,
            min_angle=-90, max_angle=90,
            min_pulse_width=1/1000, max_pulse_width=2/1000,
            frame_width=20/1000, pin_factory=None):
        self._min_angle = min_angle
        self._angular_range = max_angle - min_angle
        if initial_angle is None:
            initial_value = None
        elif ((min_angle <= initial_angle <= max_angle) or
            (max_angle <= initial_angle <= min_angle)):
            initial_value = 2 * ((initial_angle - min_angle) / self._angular_range) - 1
        else:
            raise OutputDeviceBadValue(
                "AngularServo angle must be between %s and %s, or None" %
                (min_angle, max_angle))
        super(AngularServo, self).__init__(
            pin, initial_value, min_pulse_width, max_pulse_width, frame_width,
            pin_factory=pin_factory
        )

    @property
    def min_angle(self):
        """
        The minimum angle that the servo will rotate to when :meth:`min` is
        called.
        """
        return self._min_angle

    @property
    def max_angle(self):
        """
        The maximum angle that the servo will rotate to when :meth:`max` is
        called.
        """
        return self._min_angle + self._angular_range

    @property
    def angle(self):
        """
        The position of the servo as an angle measured in degrees. This will
        only be accurate if :attr:`min_angle` and :attr:`max_angle` have been
        set appropriately in the constructor.

        This can also be the special value :data:`None` indicating that the
        servo is currently "uncontrolled", i.e. that no control signal is being
        sent.  Typically this means the servo's position remains unchanged, but
        that it can be moved by hand.
        """
        result = self._get_value()
        if result is None:
            return None
        else:
            # NOTE: Why round(n, 12) here instead of 14? Angle ranges can be
            # much larger than -1..1 so we need a little more rounding to
            # smooth off the rough corners!
            return round(
                self._angular_range *
                ((result - self._min_value) / self._value_range) +
                self._min_angle, 12)

    @angle.setter
    def angle(self, angle):
        if angle is None:
            self.value = None
        elif ((self.min_angle <= angle <= self.max_angle) or
              (self.max_angle <= angle <= self.min_angle)):
            self.value = (
                self._value_range *
                ((angle - self._min_angle) / self._angular_range) +
                self._min_value)
        else:
            raise OutputDeviceBadValue(
                "AngularServo angle must be between %s and %s, or None" %
                (self.min_angle, self.max_angle))
