.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017 Ben Nuttall <ben@bennuttall.com>
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

===================
Remote GPIO Recipes
===================

.. currentmodule:: gpiozero

The following recipes demonstrate some of the capabilities of the remote GPIO
feature of the GPIO Zero library. Before you start following these examples,
please read up on preparing your Pi and your host PC to work with
:doc:`remote_gpio`.

Please note that all recipes are written assuming Python 3. Recipes *may* work
under Python 2, but no guarantees!


LED + Button
============

Let a :class:`Button` on one Raspberry Pi control the :class:`LED` of another:

.. literalinclude:: examples/led_button_remote_1.py


LED + 2 Buttons
===============

The :class:`LED` will come on when both buttons are pressed:

.. literalinclude:: examples/led_button_remote_2.py


Multi-room motion alert
=======================

Install a Raspberry Pi with a :class:`MotionSensor` in each room of your house,
and have an class:`LED` indicator showing when there's motion in each room:

.. literalinclude:: examples/multi_room_motion_alert.py


Multi-room doorbell
===================

Install a Raspberry Pi with a :class:`Buzzer` attached in each room you want to
hear the doorbell, and use a push :class:`Button` as the doorbell:

.. literalinclude:: examples/multi_room_doorbell.py

This could also be used as an internal doorbell (tell people it's time for
dinner from the kitchen).


Remote button robot
===================

Similarly to the simple recipe for the button controlled :class:`Robot`, this
example uses four buttons to control the direction of a robot. However, using
remote pins for the robot means the control buttons can be separate from the
robot:

.. literalinclude:: examples/remote_button_robot.py


Light sensor + Sense HAT
=========================

The `Sense HAT`_ (not supported by GPIO Zero) includes temperature, humidity
and pressure sensors, but no light sensor. Remote GPIO allows an external
:class:`LightSensor` to be used as well. The Sense HAT LED display can be used
to show different colours according to the light levels:

.. literalinclude:: examples/sense_hat_remote_2.py

Note that in this case, the Sense HAT code must be run locally, and the GPIO
remotely.


.. _Sense HAT: https://www.raspberrypi.org/products/sense-hat/
