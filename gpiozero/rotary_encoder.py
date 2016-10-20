# -*- coding: utf-8 -*-
from gpiozero import Device, DigitalInputDevice, Button, CompositeDevice


class RotaryEncoder(Device):
    """
    Decode mechanical rotary encoder pulses.

    Connect the extrems pins of the rotary encoder (left and right pins) to any GPIO
    and the middle pin to a ground pin. Alternatively, connect the middle pin to the
    3V3 pin, then set *pull_up* to ``False`` in the :class:`RotaryEncoder` constructor.

    The following example will print a Rotary Encoder change direction::

        from gpiozero import RotaryEncoder

        def change(value):
            if value > 0:
                print("clockwise")
            else:
                print("counterclockwise")

        rotary = RotaryEncoder(13, 19)
        rotary.when_rotated = change

    Based in Pigpio implementation `Pigpio implementation <http://abyz.co.uk/rpi/pigpio/examples.html#Python_rotary_encoder_py>`_
    and `Paul Stoffregen implementation <https://github.com/PaulStoffregen/Encoder>`_

    :param int pin_a:
        An extreme GPIO pin which the RotaryEncoder is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param int pin_b:
        The another extreme GPIO pin which the RotaryEncoder is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param bool pull_up:
        If ``True`` (the default), the GPIO pins will be pulled high by default.
        In this case, connect the middle GPIO pin to ground. If ``False``, 
        the GPIO pins will be pulled low by default. In this case,
        connect the middle pin of the RotaryEncoder to 3V3.
    """

    def __init__(self, pin_a, pin_b, pull_up=True):
        self.when_rotated = lambda *args: None

        self.pin_a = DigitalInputDevice(pin=pin_a, pull_up=pull_up)
        self.pin_b = DigitalInputDevice(pin=pin_b, pull_up=pull_up)

        self.pin_a.when_activated = self._pulse
        self.pin_a.when_deactivated = self._pulse

        self.pin_b.when_activated = self._pulse
        self.pin_b.when_deactivated = self._pulse

        self._old_a_value = self.pin_a.is_active
        self._old_b_value = self.pin_b.is_active

    def _pulse(self):
        """
        Calls when_rotated callback if detected changes
        """
        new_b_value = self.pin_b.is_active
        new_a_value = self.pin_a.is_active

        value = TableValues.value(new_b_value, new_a_value, self._old_b_value, self._old_a_value)

        self._old_b_value = new_b_value
        self._old_a_value = new_a_value

        if value != 0:
            self.when_rotated(value)

    def close(self):
        self.pin_a.close()
        self.pin_b.close()

    @property
    def closed(self):
        return self.pin_a.closed and self.pin_b.closed

    @property
    def is_active(self):
        return not self.closed

    @property
    def value(self):
        return None

    def __repr__(self):
        return "<gpiozero.%s object on pin_a %r, pin_b %r, pull_up=%s, is_active=%s>" % (
                self.__class__.__name__, self.pin_a.pin, self.pin_b.pin, self.pin_a.pull_up, self.is_active)


class TableValues:
    """
    Decodes a :class:`RotaryEncoder` pulse.

               +---------+         +---------+      1
               |         |         |         |
     A         |         |         |         |
               |         |         |         |
     +---------+         +---------+         +----- 0

         +---------+         +---------+            1
         |         |         |         |
     B   |         |         |         |
         |         |         |         |
     ----+         +---------+         +---------+  0

    Addapted for `Paul Stoffregen table <https://github.com/PaulStoffregen/Encoder/blob/dd19b612b8050687563323777c946888f450d73c/Encoder.h#L137-L160>`_.
    """

    # The commented values are middle changes
    _values = {
        0: +0,
        1: +1,
        2: -1,
        3: +2,
        # 4: -1,
        5: +0,
        6: -2,
        # 7: +1,
        # 8: +1,
        9: -2,
        10: +0,
        # 11: -1,
        12: +2,
        13: -1,
        14: +1,
        15: +0
    }

    @staticmethod
    def value(new_b_value, new_a_value, old_b_value, old_a_value):
        index = TableValues.calculate_index(new_b_value, new_a_value, old_b_value, old_a_value)
        try:
            return TableValues._values[index]
        except KeyError:
            return 0

    @staticmethod
    def calculate_index(new_b_value, new_a_value, old_b_value, old_a_value):
        value = 0
        if new_b_value:
            value += 8
        if new_a_value:
            value += 4
        if old_b_value:
            value += 2
        if old_a_value:
            value += 1

        return value


class RotaryEncoderClickable(CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a :class:`RotaryEncoder` with a
    :class:`Button`.

    The following example will print a Rotary Encoder change direction and Button pressed::

        from gpiozero import RotaryEncoderClickable

        def change(value):
            if value > 0:
                print("clockwise")
            else:
                print("counterclockwise")

        def pressed():
            print("pressed")

        rotary = RotaryEncoderClickable(pin_a=13, pin_b=19, button_pin=15)
        rotary.when_rotated = change


    :param int pin_a:
        An extreme GPIO pin which the RotaryEncoder is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param int pin_b:
        The another extreme GPIO pin which the RotaryEncoder is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param int button_pin:
        The GPIO pin which the button is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param bool encoder_pull_up:
        If ``True`` (the default), the GPIO pins will be pulled high by default.
        In this case, connect the middle GPIO pin to ground. If ``False``, 
        the GPIO pins will be pulled low by default. In this case,
        connect the middle pin of the RotaryEncoder to 3V3.

    :param bool button_pull_up:
        If ``True`` (the default), the GPIO pin will be pulled high by default.
        In this case, connect the other side of the button to ground. If
        ``False``, the GPIO pin will be pulled low by default. In this case,
        connect the other side of the button to 3V3.

    """
    def __init__(self, pin_a, pin_b, button_pin, encoder_pull_up=True, button_pull_up=True):
        self.rotary_encoder = RotaryEncoder(pin_a, pin_b, encoder_pull_up)
        self.button = Button(button_pin, button_pull_up)

    @property
    def when_rotated(self):
        return self.rotary_encoder.when_rotated

    @when_rotated.setter
    def when_rotated(self, action):
        self.rotary_encoder.when_rotated = action

    @property
    def when_pressed(self):
        return self.button.when_pressed

    @when_pressed.setter
    def when_pressed(self, action):
        self.button.when_pressed = action

    def close(self):
        self.rotary_encoder.close()
        self.button.close()

    @property
    def closed(self):
        return self.rotary_encoder.closed and self.button.closed

    @property
    def is_active(self):
        return not self.closed

    @property
    def value(self):
        self.button.value

    def __repr__(self):
        return "<gpiozero.%s object on pin_a %r, pin_b %r, button_pin %r, encoder_pull_up=%s, button_pull_up=%s, is_active=%s>" % (
                self.__class__.__name__,
                self.rotary_encoder.pin_a.pin,
                self.rotary_encoder.pin_b.pin,
                self.button.pin,
                self.rotary_encoder.pin_a.pull_up,
                self.button.pull_up,
                self.is_active
        )

