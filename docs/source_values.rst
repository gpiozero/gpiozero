=============
Source/Values
=============

.. currentmodule:: gpiozero

GPIO Zero provides a method of using the declarative programming paradigm to
connect devices together: feeding the values of one device into another, for
example the values of a button into an LED:

.. literalinclude:: examples/led_button.py

which is equivalent to:

.. literalinclude:: examples/led_button_loop.py

Every device has a :attr:`~Device.value` property (the device's current value).
Input devices can only have their values read, but output devices can also have
their value set to alter the state of the device::

    >>> led = PWMLED(17)
    >>> led.value  # LED is initially off
    0.0
    >>> led.on()  # LED is now on
    >>> led.value
    1.0
    >>> led.value = 0  # LED is now off

Every device also has a :attr:`~ValuesMixin.values` property (a generator
continuously yielding the device's current value). All output devices have a
:attr:`~SourceMixin.source` property which can be set to any iterator. The
device will iterate over the values provided, setting the device's value to
each element at a rate specified in the :attr:`~SourceMixin.source_delay`
property.

.. image:: images/source_values.*
    :align: center

The most common use case for this is to set the source of an output device to
the values of an input device, like the example above. A more interesting
example would be a potentiometer controlling the brightness of an LED:

.. literalinclude:: examples/pwmled_pot.py

It is also possible to set an output device's :attr:`~SourceMixin.source` to
the :attr:`~ValuesMixin.values` of another output device, to keep them
matching:

.. literalinclude:: examples/matching_leds.py

The device's values can also be processed before they are passed to the
``source``:

.. image:: images/source_value_processing.*
    :align: center

For example:

.. literalinclude:: examples/source_value_processing.py

Alternatively, a custom generator can be used to provide values from an
artificial source:

.. image:: images/custom_generator.*
    :align: center

For example:

.. literalinclude:: examples/custom_generator.py

If the iterator is infinite (i.e. an infinite generator), the elements will be
processed until the :attr:`~SourceMixin.source` is changed or set to ``None``.

If the iterator is finite (e.g. a list), this will terminate once all elements
are processed (leaving the device's value at the final element):

.. literalinclude:: examples/custom_generator_finite.py

Composite devices
-----------------

Most devices have a :attr:`~Device.value` range between 0 and 1. Some have a
range between -1 and 1 (e.g. :class:`Motor`). The :attr:`~Device.value` of a
composite device is a namedtuple of such values. For example, the
:class:`Robot` class::

    >>> from gpiozero import Robot
    >>> robot = Robot(left=(14, 15), right=(17, 18))
    >>> robot.value
    RobotValue(left_motor=0.0, right_motor=0.0)
    >>> tuple(robot.value)
    (0.0, 0.0)
    >>> robot.forward()
    >>> tuple(robot.value)
    (1.0, 1.0)
    >>> robot.backward()
    >>> tuple(robot.value)
    (-1.0, -1.0)
    >>> robot.value = (1, 1)  # robot is now driven forwards

Source Tools
------------

GPIO Zero provides a set of ready-made functions for dealing with
source/values, called source tools. These are available by importing from
:mod:`gpiozero.tools`.

Some of these source tools are artificial sources which require no input:

.. image:: images/source_tool.*

In this example, random values between 0 and 1 are passed to the LED, giving it
a flickering candle effect:

.. literalinclude:: examples/random_values.py

Some tools take a single source and process its values:

.. image:: images/source_tool_value_processor.*

In this example, the LED is lit only when the button is not pressed:

.. literalinclude:: examples/negated.py

Some tools combine the values of multiple sources:

.. image:: images/combining_sources.*

In this example, the LED is lit only if both buttons are pressed (like an
`AND`_ gate):

.. _AND: https://en.wikipedia.org/wiki/AND_gate

.. literalinclude:: examples/combining_sources.py
