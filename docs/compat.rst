=======================
Backwards Compatibility
=======================


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
keyword-only arguments; they could only be implemented via "!*!*kwargs"
arguments and dictionary manipulation).

In GPIO Zero 2.x, all such arguments are now *actually* keyword arguments. If
your code complied with the 1.x documentation you shouldn't notice any
difference. In other words, the following is still fine::

    from gpiozero import PiLiter

    l = PiLiter(pwm=True)

However, if you had omitted the keyword you will need to modify your code::

    from gpiozero import PiLiter

    l = PiLiter(True)  # this will no longer work


.. _Python documentation: https://docs.python.org/3/
.. _porting guide: https://docs.python.org/3/howto/pyporting.html
