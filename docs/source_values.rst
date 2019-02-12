.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016-2019 Ben Nuttall <ben@bennuttall.com>
..
.. Redistribution and use in source and binary forms, with or without
.. modification, are permitted provided that the following conditions are met:
..
.. * Redistributions of source code must retain the above copyright notice,
..   this list of conditions and the following disclaimer.
..
.. * Redistributions in binary form must reproduce the above copyright notice,
..   this list of conditions and the following disclaimer in the documentation
..   and/or other materials provided with the distribution.
..
.. * Neither the name of the copyright holder nor the names of its contributors
..   may be used to endorse or promote products derived from this software
..   without specific prior written permission.
..
.. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
.. AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
.. IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
.. ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
.. LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
.. CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
.. SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
.. INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
.. CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
.. ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
.. POSSIBILITY OF SUCH DAMAGE.

=============
Source/Values
=============

.. currentmodule:: gpiozero

GPIO Zero provides a method of using the declarative programming paradigm to
connect devices together: feeding the values of one device into another, for
example the values of a button into an LED:

.. image:: images/source_values/led_button.*
    :align: center

.. literalinclude:: examples/led_button.py

which is equivalent to:

.. literalinclude:: examples/led_button_loop.py

except that the former is updated in a background thread, which enables you to
do other things at the same time.

Every device has a :attr:`~Device.value` property (the device's current value).
Input devices (like buttons) can only have their values read, but output devices
(like LEDs) can also have their value set to alter the state of the device:

.. code-block:: pycon

    >>> led = PWMLED(17)
    >>> led.value  # LED is initially off
    0.0
    >>> led.on()  # LED is now on
    >>> led.value
    1.0
    >>> led.value = 0  # LED is now off

Every device also has a :attr:`~ValuesMixin.values` property (a `generator`_
continuously yielding the device's current value). All output devices have a
:attr:`~SourceMixin.source` property which can be set to any `iterator`_. The
device will iterate over the values of the device provided, setting the device's
value to each element at a rate specified in the
:attr:`~SourceMixin.source_delay` property (the default is 0.01 seconds).

.. _generator: https://wiki.python.org/moin/Generators
.. _iterator: https://wiki.python.org/moin/Iterator

.. image:: images/source_values/source_values.*
    :align: center

The most common use case for this is to set the source of an output device to
match the values of an input device, like the example above. A more interesting
example would be a potentiometer controlling the brightness of an LED:

.. image:: images/source_values/pwmled_pot.*
    :align: center

.. literalinclude:: examples/pwmled_pot.py

The way this works is that the input device's :attr:`~ValuesMixin.values`
property is used to feed values into the output device. Prior to v1.5, the
:attr:`~SourceMixin.source` had to be set directly to a device's
:attr:`~ValuesMixin.values` property:

.. literalinclude:: examples/pwmled_pot_values.py

.. note::

    Although this method is still supported, the recommended way is now to set
    the :attr:`~SourceMixin.source` to a device object.

It is also possible to set an output device's :attr:`~SourceMixin.source` to
another output device, to keep them matching. In this example, the red LED is
set to match the button, and the green LED is set to match the red LED, so both
LEDs will be on when the button is pressed:

.. image:: images/source_values/matching_leds.*
    :align: center

.. literalinclude:: examples/matching_leds.py

Processing values
-----------------

The device's values can also be processed before they are passed to the
:attr:`~SourceMixin.source`:

.. image:: images/source_values/value_processing.*
    :align: center

For example, writing a generator function to pass the opposite of the Button
value into the LED:

.. image:: images/source_values/led_button_opposite.*
    :align: center

.. literalinclude:: examples/source_value_processing.py

Alternatively, a custom generator can be used to provide values from an
artificial source:

.. image:: images/source_values/custom_generator.*
    :align: center

For example, writing a generator function to randomly yield 0 or 1:

.. image:: images/source_values/random_led.*
    :align: center

.. literalinclude:: examples/custom_generator.py

If the iterator is infinite (i.e. an infinite generator), the elements will be
processed until the :attr:`~SourceMixin.source` is changed or set to
:data:`None`.

If the iterator is finite (e.g. a list), this will terminate once all elements
are processed (leaving the device's value at the final element):

.. literalinclude:: examples/custom_generator_finite.py

Source Tools
------------

GPIO Zero provides a set of ready-made functions for dealing with
source/values, called source tools. These are available by importing from
:mod:`gpiozero.tools`.

Some of these source tools are artificial sources which require no input:

.. image:: images/source_values/source_tool.*
    :align: center

In this example, random values between 0 and 1 are passed to the LED, giving it
a flickering candle effect:

.. image:: images/source_values/source_tool_candle.*
    :align: center

.. literalinclude:: examples/random_values.py

Note that in the above example, :attr:`~SourceMixin.source_delay` is used to
make the LED iterate over the random values slightly slower.
:attr:`~SourceMixin.source_delay` can be set to a larger number (e.g. 1 for a
one second delay) or set to 0 to disable any delay.

Some tools take a single source and process its values:

.. image:: images/source_values/source_tool_value_processor.*
    :align: center

In this example, the LED is lit only when the button is not pressed:

.. image:: images/source_values/led_button_negated.*
    :align: center

.. literalinclude:: examples/negated.py

.. note::

    Note that source tools which take one or more ``value`` parameters support
    passing either :class:`~ValuesMixin` derivatives, or iterators, including a
    device's :attr:`~ValuesMixin.values` property.

Some tools combine the values of multiple sources:

.. image:: images/source_values/combining_sources.*
    :align: center

In this example, the LED is lit only if both buttons are pressed (like an
`AND`_ gate):

.. image:: images/source_values/combining_sources_led_buttons.*
    :align: center

.. literalinclude:: examples/combining_sources.py

Similarly, :func:`~tools.any_values` with two buttons would simulate an `OR`_
gate.

.. _AND: https://en.wikipedia.org/wiki/AND_gate
.. _OR: https://en.wikipedia.org/wiki/OR_gate

While most devices have a :attr:`~Device.value` range between 0 and 1, some have
a range between -1 and 1 (e.g. :class:`Motor`, :class:`Servo` and
:class:`TonalBuzzer`). Some source tools output values between -1 and 1, which
are ideal for these devices, for example passing :func:`~tools.sin_values` in:

.. image:: images/source_values/sin_values.*
    :align: center

.. literalinclude:: examples/sin_values.py

In this example, all three devices are following the `sine wave`_. The motor
value ramps up from 0 (stopped) to 1 (full speed forwards), then back down to 0
and on to -1 (full speed backwards) in a cycle. Similarly, the servo moves from
its mid point to the right, then towards the left; and the buzzer starts with
its mid tone, gradually raises its frequency, to its highest tone, then down
towards its lowest tone. Note that setting :attr:`~SourceMixin.source_delay`
will alter the speed at which the device iterates through the values.
Alternatively, the tool :func:`~tools.cos_values` could be used to start from -1
and go up to 1, and so on.

.. _sine wave: https://en.wikipedia.org/wiki/Sine_wave

Internal devices
----------------

GPIO Zero also provides several :doc:`internal devices <api_internal>` which
represent facilities provided by the operating system itself. These can be used
to react to things like the time of day, or whether a server is available on the
network. These classes include a :attr:`~ValuesMixin.values` property which can
be used to feed values into a device's :attr:`~SourceMixin.source`. For example,
a lamp connected to an :class:`Energenie` socket can be controlled by a
:class:`TimeOfDay` object so that it is on between the hours of 8am and 8pm:

.. image:: images/source_values/timed_heat_lamp.*
    :align: center

.. literalinclude:: examples/timed_heat_lamp.py

Using the :class:`DiskUsage` class with :class:`LEDBarGraph` can show your Pi's
disk usage percentage on a bar graph:

.. image:: images/source_values/disk_usage_bar_graph.*
    :align: center

.. literalinclude:: examples/disk_usage_bar_graph.py

Demonstrating a garden light system whereby the light comes on if it's dark and
there's motion is simple enough, but it requires using the
:func:`~tools.booleanized` source tool to convert the light sensor from a float
value into a boolean:

.. image:: images/source_values/garden_light.*
    :align: center

.. literalinclude:: examples/garden_light.py

Composite devices
-----------------

The :attr:`~Device.value` of a composite device made up of the nested values of
its devices. For example, the value of a :class:`Robot` object is a 2-tuple
containing its left and right motor values:

.. code-block:: pycon

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

Use two potentiometers to control the left and right motor speed of a robot:

.. image:: images/source_values/robot_pots_1.*
    :align: center

.. literalinclude:: examples/robot_pots_1.py

To include reverse direction, scale the potentiometer values from 0->1 to -1->1:

.. image:: images/source_values/robot_pots_2.*
    :align: center

.. literalinclude:: examples/robot_pots_2.py

Note that this example uses the built-in :func:`zip` rather than the tool
:func:`~tools.zip_values` as the :func:`~tools.scaled` tool yields values which
do not need converting, just zipping. Also note that this use of :func:`zip`
will not work in Python 2, instead use `izip`_.

.. _izip: https://docs.python.org/2/library/itertools.html#itertools.izip
