=======================
Backwards Compatibility
=======================


.. currentmodule:: gpiozero

GPIO Zero 2.x is a new major version and thus backwards incompatible changes
can be expected. We have attempted to keep these as minimal as reasonably
possible while taking advantage of the opportunity to clean up things. This
chapter documents breaking changes from version 1.x of the library to 2.x.


Python 2.x support dropped
==========================

By far the biggest and most important change is that the Python 2.x series is
no longer supported (in practice, this means Python 2.7 is no longer
supported). If your code is not compatible with Python 3, you should follow the
`porting guide`_ in the `Python documentation`_.

As of GPIO Zero 2.0, the lowest supported Python version will be 3.5. This base
version may advance with minor releases, but we will make a reasonable best
effort not to break compatibility with old Python 3.x versions.


RPIO pin factory removed
========================

The RPIO pin implementation is unsupported on the Raspberry Pi 2 onwards and
hence of little practical use these days. Anybody still relying on RPIO's
stable PWM implementation is advised to try the pigpio pin implementation
instead (also supported by GPIO Zero).


Deprecated pin-factory aliases removed
======================================

Several deprecated aliases for pin factories, which could be specified by the
:envvar:`GPIOZERO_PIN_FACTORY` environment variable, have been removed:

* "PiGPIOPin" is removed in favour of "pigpio"

* "RPiGPIOPin" is removed in favour of "rpigpio"

* "NativePin" is removed in favour of "native"

In other words, you can no longer use the following when invoking your
script:

.. code-block:: console

    $ GPIOZERO_PIN_FACTORY=PiGPIOPin python3 my_script.py

Instead, you should use the following:

.. code-block:: console

    $ GPIOZERO_PIN_FACTORY=pigpio python3 my_script.py


Keyword arguments
=================

Many classes in GPIO Zero 1.x were documented as having keyword-only arguments
in their constructors and methods. For example, the :class:`PiLiter` was
documented as having the constructor: ``PiLiter(*, pwm=False,
initial_value=False, pin_factory=None)`` implying that all its arguments were
keyword only.

However, despite being documented in this manner, this was rarely enforced as
it was extremely difficult to do so under Python 2.x without complicating the
code-base considerably (Python 2.x lacked the "*" syntax to declare
keyword-only arguments; they could only be implemented via "\*\*kwargs"
arguments and dictionary manipulation).

In GPIO Zero 2.x, all such arguments are now *actually* keyword arguments. If
your code complied with the 1.x documentation you shouldn't notice any
difference. In other words, the following is still fine::

    from gpiozero import PiLiter

    l = PiLiter(pwm=True)

However, if you had omitted the keyword you will need to modify your code::

    from gpiozero import PiLiter

    l = PiLiter(True)  # this will no longer work


Robots take Motors, and PhaseEnableRobot is removed
===================================================

The GPIO Zero 1.x API specified that a :class:`Robot` was constructed with two
tuples that were in turn used to construct two :class:`Motor` instances. The
2.x API replaces this with simply passing in the :class:`Motor`, or
:class:`PhaseEnableMotor` instances you wish to use as the left and right
wheels.

If your current code uses pins 4 and 14 for the left wheel, and 17 and 18 for
the right wheel, it may look like this::

    from gpiozero import Robot

    r = Robot(left=(4, 14), right=(17, 18))

This should be changed to the following::

    from gpiozero import Robot, Motor

    r = Robot(left=Motor(4, 14), right=Motor(17, 18))

Likewise, if you are currently using :class:`PhaseEnableRobot` your code may
look like this::

    from gpiozero import PhaseEnableRobot

    r = PhaseEnableRobot(left=(4, 14), right=(17, 18))

This should be changed to the following::

    from gpiozero import Robot, PhaseEnableMotor

    r = Robot(left=PhaseEnableMotor(4, 14),
              right=PhaseEnableMotor(17, 18))

This change came about because the :class:`Motor` class was also documented as
having two mandatory parameters (*forward* and *backward*) and several
keyword-only parameters, including the *enable* pin. However, *enable* was
treated as a positional argument for the sake of constructing :class:`Robot`
which was inconsistent. Furthermore, :class:`PhaseEnableRobot` was more or less
a redundant duplicate of :class:`Robot` but was lacking a couple of features
added to :class:`Robot` later (notable "curved" turning).

Although the new API requires a little more typing, it does mean that phase
enable robot boards now inherit all the functionality of :class:`Robot` because
that's all they use. Theoretically you could also mix and match regular motors
and phase-enable motors although there's little sense in doing so.

The former functionality (passing tuples to the :class:`Robot` constructor)
will remain as deprecated functionality for gpiozero 2.0, but will be removed
in a future 2.x release.


.. _Python documentation: https://docs.python.org/3/
.. _porting guide: https://docs.python.org/3/howto/pyporting.html
