from __future__ import (
    unicode_literals,
    print_function,
    absolute_import,
    division,
)

import warnings
from time import sleep
from threading import Lock
from itertools import repeat, cycle, chain

from .exc import OutputDeviceBadValue, GPIOPinMissing, GPIODeviceClosed
from .devices import GPIODevice, GPIOThread, CompositeDevice, SourceMixin


class PololuMotor(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor connected
    to a Pololu motor driver circuit.

    The following code will make the motor turn "forwards"::

        from gpiozero import PololuMotor

        motor = PololuMotor(17, 18)
        motor.forward()

    :param int forward:
        The GPIO pin that the forward input of the motor driver chip is
        connected to.

    :param int backward:
        The GPIO pin that the backward input of the motor driver chip is
        connected to.
    """
    def __init__(self, power=None, direction=None):
        if not all([power, direction]):
            raise GPIOPinMissing(
                'forward and backward pins must be provided'
            )
        super(PololuMotor, self).__init__()
        self._power = PWMOutputDevice(power)
        self._direction = OutputDevice(direction)

    def close(self):
        self._power.close()
        self._direction.close()

    @property
    def closed(self):
        return self._power.closed and self._direction.closed

    @property
    def power_device(self):
        """
        Returns the `PWMOutputDevice` representing the power pin of the
        motor controller.
        """
        return self._power

    @property
    def direction_device(self):
        """
        Returns the `OutputDevice` representing the direction pin of the motor
        controller.
        """
        return self._direction

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward).
        """
        return self._power.value if self._direction.is_active() else -self._power.value

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
        self._direction.on()
        self._power.value = speed

    def backward(self, speed=1):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed).
        """
        self._direction.off()
        self._power.value = speed

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
        self._power.off()
        self._direction.off()


class PololuRobot(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` to represent a generic dual-motor robot.

    This class is constructed with two tuples representing the forward and
    backward pins of the left and right controllers respectively. For example,
    if the left motor's controller is connected to GPIOs 4 and 14, while the
    right motor's controller is connected to GPIOs 17 and 18 then the following
    example will turn the robot left::

        from gpiozero import PololuRobot

        robot = PololuRobot(left=(4, 14), right=(17, 18))
        robot.left()

    :param tuple left:
        A tuple of two GPIO pins representing the power and direction inputs
        of the left motor's controller.

    :param tuple right:
        A tuple of two GPIO pins representing the power and direction inputs
        of the right motor's controller.
    """
    def __init__(self, left=None, right=None):
        if not all([left, right]):
            raise OutputDeviceError(
                'left and right motor pins must be provided'
            )
        super(Robot, self).__init__()
        self._left = PololuMotor(*left)
        self._right = PololuMotor(*right)

    def close(self):
        self._left.close()
        self._right.close()

    @property
    def closed(self):
        return self._left.closed and self._right.closed

    @property
    def left_motor(self):
        """
        Returns the `Motor` device representing the robot's left motor.
        """
        return self._left

    @property
    def right_motor(self):
        """
        Returns the `Motor` device representing the robot's right motor.
        """
        return self._right

    @property
    def value(self):
        """
        Returns a tuple of two floating point values (-1 to 1) representing the
        speeds of the robot's two motors (left and right). This property can
        also be set to alter the speed of both motors.
        """
        return RobotTuple(self._left.value, self._right.value)

    @value.setter
    def value(self, value):
        self._left.value, self._right.value = value

    def forward(self, speed=1):
        """
        Drive the robot forward by running both motors forward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.forward(speed)
        self._right.forward(speed)

    def backward(self, speed=1):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.backward(speed)
        self._right.backward(speed)

    def left(self, speed=1):
        """
        Make the robot turn left by running the right motor forward and left
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._right.forward(speed)
        self._left.backward(speed)

    def right(self, speed=1):
        """
        Make the robot turn right by running the left motor forward and right
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self._left.forward(speed)
        self._right.backward(speed)

    def reverse(self):
        """
        Reverse the robot's current motor directions. If the robot is currently
        running full speed forward, it will run full speed backward. If the
        robot is turning left at half-speed, it will turn right at half-speed.
        If the robot is currently stopped it will remain stopped.
        """
        self._left.value = -self._left.value
        self._right.value = -self._right.value

    def stop(self):
        """
        Stop the robot.
        """
        self._left.stop()
        self._right.stop()
