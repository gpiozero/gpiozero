from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

from threading import Lock
from itertools import repeat, cycle, chain

from .exc import OutputDeviceBadValue, GPIOPinMissing
from .devices import GPIODevice, Device, CompositeDevice
from .mixins import SourceMixin
from .threads import GPIOThread


class OutputDevice(SourceMixin, GPIODevice):
    """
    Represents a generic GPIO output device.

    This class extends :class:`GPIODevice` to add facilities common to GPIO
    output devices: an :meth:`on` method to switch the device on, a
    corresponding :meth:`off` method, and a :meth:`toggle` method.

    :param int pin:
        The GPIO pin (in BCM numbering) that the device is connected to. If
        this is ``None`` a :exc:`GPIOPinMissing` will be raised.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set the GPIO to
        HIGH. If ``False``, the :meth:`on` method will set the GPIO to LOW (the
        :meth:`off` method always does the opposite).

    :param bool initial_value:
        If ``False`` (the default), the device will be off initially.  If
        ``None``, the device will be left in whatever state the pin is found in
        when configured for output (warning: this can be on).  If ``True``, the
        device will be switched on initially.
    """
    def __init__(self, pin=None, active_high=True, initial_value=False):
        super(OutputDevice, self).__init__(pin)
        self._lock = Lock()
        self.active_high = active_high
        if initial_value is None:
            self.pin.function = 'output'
        elif initial_value:
            self.pin.output_with_state(self._active_state)
        else:
            self.pin.output_with_state(self._inactive_state)

    def _write(self, value):
        if not self.active_high:
            value = not value
        try:
            self.pin.state = bool(value)
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
        Returns ``True`` if the device is currently active and ``False``
        otherwise. Setting this property changes the state of the device.
        """
        return super(OutputDevice, self).value

    @value.setter
    def value(self, value):
        self._write(value)

    @property
    def active_high(self):
        """
        When ``True``, the :attr:`value` property is ``True`` when the device's
        :attr:`pin` is high. When ``False`` the :attr:`value` property is
        ``True`` when the device's pin is low (i.e. the value is inverted).

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
    """
    def __init__(self, pin=None, active_high=True, initial_value=False):
        self._blink_thread = None
        super(DigitalOutputDevice, self).__init__(pin, active_high, initial_value)
        self._controller = None

    @property
    def value(self):
        return self._read()

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

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True`` (the default), start a background thread to continue
            blinking and return immediately. If ``False``, only return when the
            blink is finished (warning: the default value of *n* will result in
            this method never returning).
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
        if self._controller:
            self._controller._stop_blink(self)
            self._controller = None
        if self._blink_thread:
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

    :param int pin:
        The GPIO pin which the LED is attached to. See :doc:`notes` for valid
        pin numbers.

    :param bool active_high:
        If ``True`` (the default), the LED will operate normally with the
        circuit described above. If ``False`` you should wire the cathode to
        the GPIO pin, and the anode to a 3V3 pin (via a limiting resistor).

    :param bool initial_value:
        If ``False`` (the default), the LED will be off initially.  If
        ``None``, the LED will be left in whatever state the pin is found in
        when configured for output (warning: this can be on).  If ``True``, the
        LED will be switched on initially.
    """
    pass

LED.is_lit = LED.is_active


class Buzzer(DigitalOutputDevice):
    """
    Extends :class:`DigitalOutputDevice` and represents a digital buzzer
    component.

    Connect the cathode (negative pin) of the buzzer to a ground pin; connect
    the other side to any GPIO pin.

    The following example will sound the buzzer::

        from gpiozero import Buzzer

        bz = Buzzer(3)
        bz.on()

    :param int pin:
        The GPIO pin which the buzzer is attached to. See :doc:`notes` for
        valid pin numbers.

    :param bool active_high:
        If ``True`` (the default), the buzzer will operate normally with the
        circuit described above. If ``False`` you should wire the cathode to
        the GPIO pin, and the anode to a 3V3 pin.

    :param bool initial_value:
        If ``False`` (the default), the buzzer will be silent initially.  If
        ``None``, the buzzer will be left in whatever state the pin is found in
        when configured for output (warning: this can be on).  If ``True``, the
        buzzer will be switched on initially.
    """
    pass

Buzzer.beep = Buzzer.blink


class PWMOutputDevice(OutputDevice):
    """
    Generic output device configured for pulse-width modulation (PWM).

    :param int pin:
        The GPIO pin which the device is attached to. See :doc:`notes` for
        valid pin numbers.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set the GPIO to
        HIGH. If ``False``, the :meth:`on` method will set the GPIO to LOW (the
        :meth:`off` method always does the opposite).

    :param bool initial_value:
        If ``0`` (the default), the device's duty cycle will be 0 initially.
        Other values between 0 and 1 can be specified as an initial duty cycle.
        Note that ``None`` cannot be specified (unlike the parent class) as
        there is no way to tell PWM not to alter the state of the pin.

    :param int frequency:
        The frequency (in Hz) of pulses emitted to drive the device. Defaults
        to 100Hz.
    """
    def __init__(self, pin=None, active_high=True, initial_value=0, frequency=100):
        self._blink_thread = None
        self._controller = None
        if not 0 <= initial_value <= 1:
            raise OutputDeviceBadValue("initial_value must be between 0 and 1")
        super(PWMOutputDevice, self).__init__(pin, active_high)
        try:
            # XXX need a way of setting these together
            self.pin.frequency = frequency
            self.value = initial_value
        except:
            self.close()
            raise

    def close(self):
        self._stop_blink()
        try:
            self.pin.frequency = None
        except AttributeError:
            # If the pin's already None, ignore the exception
            pass
        super(PWMOutputDevice, self).close()

    def _read(self):
        self._check_open()
        if self.active_high:
            return self.pin.state
        else:
            return 1 - self.pin.state

    def _write(self, value):
        if not self.active_high:
            value = 1 - value
        if not 0 <= value <= 1:
            raise OutputDeviceBadValue("PWM value must be between 0 and 1")
        try:
            self.pin.state = value
        except AttributeError:
            self._check_open()
            raise

    @property
    def value(self):
        """
        The duty cycle of the PWM device. 0.0 is off, 1.0 is fully on. Values
        in between may be specified for varying levels of power in the device.
        """
        return self._read()

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
        Returns ``True`` if the device is currently active (:attr:`value` is
        non-zero) and ``False`` otherwise.
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

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True`` (the default), start a background thread to continue
            blinking and return immediately. If ``False``, only return when the
            blink is finished (warning: the default value of *n* will result in
            this method never returning).
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

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True`` (the default), start a background thread to continue
            blinking and return immediately. If ``False``, only return when the
            blink is finished (warning: the default value of *n* will result in
            this method never returning).
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


class PWMLED(PWMOutputDevice):
    """
    Extends :class:`PWMOutputDevice` and represents a light emitting diode
    (LED) with variable brightness.

    A typical configuration of such a device is to connect a GPIO pin to the
    anode (long leg) of the LED, and the cathode (short leg) to ground, with
    an optional resistor to prevent the LED from burning out.

    :param int pin:
        The GPIO pin which the LED is attached to. See :doc:`notes` for
        valid pin numbers.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set the GPIO to
        HIGH. If ``False``, the :meth:`on` method will set the GPIO to LOW (the
        :meth:`off` method always does the opposite).

    :param bool initial_value:
        If ``0`` (the default), the LED will be off initially. Other values
        between 0 and 1 can be specified as an initial brightness for the LED.
        Note that ``None`` cannot be specified (unlike the parent class) as
        there is no way to tell PWM not to alter the state of the pin.

    :param int frequency:
        The frequency (in Hz) of pulses emitted to drive the LED. Defaults
        to 100Hz.
    """
    pass

PWMLED.is_lit = PWMLED.is_active


def _led_property(index, doc=None):
    def getter(self):
        return self._leds[index].value
    def setter(self, value):
        self._stop_blink()
        self._leds[index].value = value
    return property(getter, setter, doc=doc)


class RGBLED(SourceMixin, Device):
    """
    Extends :class:`Device` and represents a full color LED component (composed
    of red, green, and blue LEDs).

    Connect the common cathode (longest leg) to a ground pin; connect each of
    the other legs (representing the red, green, and blue anodes) to any GPIO
    pins.  You can either use three limiting resistors (one per anode) or a
    single limiting resistor on the cathode.

    The following code will make the LED purple::

        from gpiozero import RGBLED

        led = RGBLED(2, 3, 4)
        led.color = (1, 0, 1)

    :param int red:
        The GPIO pin that controls the red component of the RGB LED.

    :param int green:
        The GPIO pin that controls the green component of the RGB LED.

    :param int blue:
        The GPIO pin that controls the blue component of the RGB LED.

    :param bool active_high:
        Set to ``True`` (the default) for common cathode RGB LEDs. If you are
        using a common anode RGB LED, set this to ``False``.

    :param bool initial_value:
        The initial color for the LED. Defaults to black ``(0, 0, 0)``.
    """
    def __init__(
            self, red=None, green=None, blue=None, active_high=True,
            initial_value=(0, 0, 0)):
        self._leds = ()
        self._blink_thread = None
        if not all([red, green, blue]):
            raise GPIOPinMissing('red, green, and blue pins must be provided')
        super(RGBLED, self).__init__()
        self._leds = tuple(PWMLED(pin, active_high) for pin in (red, green, blue))
        self.value = initial_value

    red = _led_property(0)
    green = _led_property(1)
    blue = _led_property(2)

    def close(self):
        if self._leds:
            self._stop_blink()
            for led in self._leds:
                led.close()
            self._leds = ()
        super(RGBLED, self).close()

    @property
    def closed(self):
        return bool(self._leds)

    @property
    def value(self):
        """
        Represents the color of the LED as an RGB 3-tuple of ``(red, green,
        blue)`` where each value is between 0 and 1.

        For example, purple would be ``(1, 0, 1)`` and yellow would be ``(1, 1,
        0)``, while orange would be ``(1, 0.5, 0)``.
        """
        return (self.red, self.green, self.blue)

    @value.setter
    def value(self, value):
        self._stop_blink()
        self.red, self.green, self.blue = value

    @property
    def is_active(self):
        """
        Returns ``True`` if the LED is currently active (not black) and
        ``False`` otherwise.
        """
        return self.value != (0, 0, 0)

    is_lit = is_active
    color = value

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
            Number of seconds to spend fading in. Defaults to 0.

        :param float fade_out_time:
            Number of seconds to spend fading out. Defaults to 0.

        :param tuple on_color:
            The color to use when the LED is "on". Defaults to white.

        :param tuple off_color:
            The color to use when the LED is "off". Defaults to black.

        :param int n:
            Number of times to blink; ``None`` (the default) means forever.

        :param bool background:
            If ``True`` (the default), start a background thread to continue
            blinking and return immediately. If ``False``, only return when the
            blink is finished (warning: the default value of *n* will result in
            this method never returning).
        """
        self._stop_blink()
        self._blink_thread = GPIOThread(
            target=self._blink_device,
            args=(on_time, off_time, fade_in_time, fade_out_time, on_color, off_color, n)
        )
        self._blink_thread.start()
        if not background:
            self._blink_thread.join()
            self._blink_thread = None

    def _stop_blink(self, led=None):
        # If this is called with a single led, we stop all blinking anyway
        if self._blink_thread:
            self._blink_thread.stop()
            self._blink_thread = None

    def _blink_device(
            self, on_time, off_time, fade_in_time, fade_out_time, on_color,
            off_color, n, fps=25):
        # Define some simple lambdas to perform linear interpolation between
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
    connected to a bi-directional motor driver circuit (i.e.  an `H-bridge`_).

    Attach an `H-bridge`_ motor controller to your Pi; connect a power source
    (e.g. a battery pack or the 5V pin) to the controller; connect the outputs
    of the controller board to the two terminals of the motor; connect the
    inputs of the controller board to two GPIO pins.

    .. _H-bridge: https://en.wikipedia.org/wiki/H_bridge

    The following code will make the motor turn "forwards"::

        from gpiozero import Motor

        motor = Motor(17, 18)
        motor.forward()

    :param int forward:
        The GPIO pin that the forward input of the motor driver chip is
        connected to.

    :param int backward:
        The GPIO pin that the backward input of the motor driver chip is
        connected to.
    """
    def __init__(self, forward=None, backward=None):
        if not all([forward, backward]):
            raise GPIOPinMissing(
                'forward and backward pins must be provided'
            )
        super(Motor, self).__init__(
                forward_device=PWMOutputDevice(forward),
                backward_device=PWMOutputDevice(backward),
                _order=('forward_device', 'backward_device'))

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward).
        """
        return self.forward_device.value - self.backward_device.value

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
        Returns ``True`` if the motor is currently running and ``False``
        otherwise.
        """
        return self.value != 0

    def forward(self, speed=1):
        """
        Drive the motor forwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed).
        """
        self.backward_device.off()
        self.forward_device.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed).
        """
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
