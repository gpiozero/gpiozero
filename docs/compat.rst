.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2021-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2023 Andrew Scheller <lurch@durge.org>
..
.. SPDX-License-Identifier: BSD-3-Clause

=======================
Backwards Compatibility
=======================


.. currentmodule:: gpiozero

GPIO Zero 2.x is a new major version and thus backwards incompatible changes
can be expected. We have attempted to keep these as minimal as reasonably
possible while taking advantage of the opportunity to clean up things. This
chapter documents breaking changes from version 1.x of the library to 2.x, and
all deprecated functionality which will still work in release 2.0 but is
scheduled for removal in a future 2.x release.


Finding and fixing deprecated usage
===================================

As of release 2.0, all deprecated functionality will raise
:exc:`DeprecationWarning` when used. By default, the Python interpreter
suppresses these warnings (as they're only of interest to developers, not
users) but you can easily configure different behaviour.

The following example script uses a number of deprecated functions::

    import gpiozero

    board = gpiozero.pi_info()
    for header in board.headers.values():
        for pin in header.pins.values():
            if pin.pull_up:
                print(pin.function, 'is pulled up')

Despite using deprecated functionality the script runs happily (and silently)
with gpiozero 2.0. To discover what deprecated functions are being used, we add
a couple of lines to tell the warnings module that we want "default" handling
of :exc:`DeprecationWarning`; "default" handling means that the first time an
attempt is made to raise this warning at a particular location, the warning's
details will be printed to the console. All future invocations from the same
location will be ignored. This saves flooding the console with warning details
from tight loops. With this change, the script looks like this::

    import gpiozero

    import warnings
    warnings.filterwarnings('default', category=DeprecationWarning)

    board = gpiozero.pi_info()
    for header in board.headers.values():
        for pin in header.pins.values():
            if pin.pull_up:
                print(pin.function, 'is pulled up')

And produces the following output on the console when run:

.. code-block:: text

    /home/dave/projects/home/gpiozero/gpio-zero/gpiozero/pins/__init__.py:899:
    DeprecationWarning: PinInfo.pull_up is deprecated; please use PinInfo.pull
      warnings.warn(
    /home/dave/projects/home/gpiozero/gpio-zero/gpiozero/pins/__init__.py:889:
    DeprecationWarning: PinInfo.function is deprecated; please use PinInfo.name
      warnings.warn(
    GPIO2 is pulled up
    GPIO3 is pulled up

This tells us which pieces of deprecated functionality are being used in our
script, but it doesn't tell us where in the script they were used. For this,
it is more useful to have warnings converted into full blown exceptions. With
this change, each time a :exc:`DeprecationWarning` would have been printed, it
will instead cause the script to terminate with an unhandled exception and a
full stack trace::

    import gpiozero

    import warnings
    warnings.filterwarnings('error', category=DeprecationWarning)

    board = gpiozero.pi_info()
    for header in board.headers.values():
        for pin in header.pins.values():
            if pin.pull_up:
                print(pin.function, 'is pulled up')

Now when we run the script it produces the following:

.. code-block:: pycon

    Traceback (most recent call last):
      File "/home/dave/projects/home/gpiozero/gpio-zero/foo.py", line 9, in <module>
        if pin.pull_up:
      File "/home/dave/projects/home/gpiozero/gpio-zero/gpiozero/pins/__init__.py", line 899, in pull_up
        warnings.warn(
    DeprecationWarning: PinInfo.pull_up is deprecated; please use PinInfo.pull

This tells us that line 9 of our script is using deprecated functionality, and
provides a hint of how to fix it. We change line 9 to use the "pull" attribute
instead. Now we run again, and this time get the following:

.. code-block:: pycon

    Traceback (most recent call last):
      File "/home/dave/projects/home/gpiozero/gpio-zero/foo.py", line 10, in <module>
        print(pin.function, 'is pulled up')
      File "/home/dave/projects/home/gpiozero/gpio-zero/gpiozero/pins/__init__.py", line 889, in function
        warnings.warn(
    DeprecationWarning: PinInfo.function is deprecated; please use PinInfo.name

Now we can tell line 10 has a problem, and once again the exception tells us
how to fix it. We continue in this fashion until the script looks like this::

    import gpiozero

    import warnings
    warnings.filterwarnings('error', category=DeprecationWarning)

    board = gpiozero.pi_info()
    for header in board.headers.values():
        for pin in header.pins.values():
            if pin.pull == 'up':
                print(pin.name, 'is pulled up')

The script now runs to completion, so we can be confident it's no longer using
any deprecated functionality and will run happily even when this functionality
is removed in a future 2.x release. At this point, you may wish to remove the
``filterwarnings`` line as well (or at least comment it out).


Python 2.x support dropped
==========================

By far the biggest and most important change is that the Python 2.x series is
no longer supported (in practice, this means Python 2.7 is no longer
supported). If your code is not compatible with Python 3, you should follow the
`porting guide`_ in the `Python documentation`_.

As of GPIO Zero 2.0, the lowest supported Python version will be 3.5. This base
version may advance with minor releases, but we will make a reasonable best
effort not to break compatibility with old Python 3.x versions, and to ensure
that GPIO Zero can run on the version of Python in Debian oldstable at the
time of its release.


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

In GPIO Zero 2.0, all such arguments are now *actually* keyword arguments. If
your code complied with the 1.x documentation you shouldn't notice any
difference. In other words, the following is still fine::

    from gpiozero import PiLiter

    l = PiLiter(pwm=True)

However, if you had omitted the keyword you will need to modify your code::

    from gpiozero import PiLiter

    l = PiLiter(True)  # this will no longer work


Robots take Motors, and PhaseEnableRobot is deprecated
======================================================

The GPIO Zero 1.x API specified that a :class:`Robot` was constructed with two
tuples that were in turn used to construct two :class:`Motor` instances. The
2.x API replaces this with simply passing in the :class:`Motor`, or
:func:`PhaseEnableMotor` instances you wish to use as the left and right
wheels.

If your current code uses pins 4 and 14 for the left wheel, and 17 and 18 for
the right wheel, it may look like this::

    from gpiozero import Robot

    r = Robot(left=(4, 14), right=(17, 18))

This should be changed to the following::

    from gpiozero import Robot, Motor

    r = Robot(left=Motor(4, 14), right=Motor(17, 18))

Likewise, if you are currently using :func:`PhaseEnableRobot` your code may
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
which was inconsistent. Furthermore, :func:`PhaseEnableRobot` was more or less
a redundant duplicate of :class:`Robot` but was lacking a couple of features
added to :class:`Robot` later (notable "curved" turning).

Although the new API requires a little more typing, it does mean that phase
enable robot boards now inherit all the functionality of :class:`Robot` because
that's all they use. Theoretically you could also mix and match regular motors
and phase-enable motors although there's little sense in doing so.

The former functionality (passing tuples to the :class:`Robot` constructor)
will remain as deprecated functionality for gpiozero 2.0, but will be removed
in a future 2.x release. :func:`PhaseEnableRobot` remains as a stub function
which simply returns a :class:`Robot` instance, but this will be removed in a
future 2.x release.


PiBoardInfo, HeaderInfo, PinInfo
================================

The :class:`PiBoardInfo` class, and the associated :class:`HeaderInfo` and
:class:`PinInfo` classes have undergone a major re-structuring. This is partly
because some of the prior terminology was confusing (e.g. the meaning of
:attr:`PinInfo.function` and :attr:`Pin.function` clashed), and partly because
with the addition of the "lgpio" factory it's entirely possible to use gpiozero
on non-Pi boards (although at present the :class:`pins.lgpio.LGPIOFactory` is
still written assuming it is only ever used on a Pi).

As a result the following classes, methods, and attributes are deprecated
(not yet removed, but will be in a future release within the 2.x series):

* :attr:`Factory.pi_info` is deprecated in favour of :attr:`Factory.board_info`
  which returns a :class:`BoardInfo` instead of :class:`PiBoardInfo` (which is
  now a subclass of the former).

* :attr:`PinInfo.pull_up` is deprecated in favour of :attr:`PinInfo.pull`.

* :attr:`PinInfo.function` is deprecated in favour of :attr:`PinInfo.name`.

* :meth:`BoardInfo.physical_pins`, :meth:`BoardInfo.physical_pin`, and
  :meth:`BoardInfo.pulled_up`, are all deprecated in favour of a combination of
  the new :meth:`BoardInfo.find_pin` and the attributes mentioned above.

* :attr:`PiPin.number` is deprecated in favour of :attr:`Pin.info.name`.

.. _Python documentation: https://docs.python.org/3/
.. _porting guide: https://docs.python.org/3/howto/pyporting.html
