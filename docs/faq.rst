.. _faq:

==========================
Frequently Asked Questions
==========================

.. currentmodule:: gpiozero


My event handler isn't being called?
====================================

When assigning event handlers, don't call the function you're assigning. For
example::

    from gpiozero import Button

    def pushed():
        print("Don't push the button!")

    b = Button(17)
    b.when_pressed = pushed()

In the case above, when assigning to the ``when_pressed``, the thing that is
assigned is the *result of calling* the ``pushed`` function. Because ``pushed``
doesn't explicitly return anything, the result is ``None``. Hence this is
equivalent to doing::

    b.when_pressed = None

This doesn't raise an error because it's perfectly valid: it's what you assign
when you don't want the event handler to do anything. Instead, you want to
do the following::

    b.when_pressed = pushed

This will assign the function to the event handler *without calling it*. This
is the crucial difference between ``my_function`` (a reference to a function)
and ``my_function()`` (the result of calling a function).


Why do I get PinFactoryFallback warnings when I import gpiozero?
================================================================

You are most likely working in a virtual Python environment and have forgotten
to install a pin driver library like ``RPi.GPIO``. GPIO Zero relies upon lower
level pin drivers to handle interfacing to the GPIO pins on the Raspberry Pi,
so you can eliminate the warning simply by installing GPIO Zero's first
preference:

.. code-block:: console

    $ pip install rpi.gpio

When GPIO Zero is imported it attempts to find a pin driver by importing them
in a preferred order (detailed in :doc:`api_pins`). If it fails to load its
first preference (``RPi.GPIO``) it notifies you with a warning, then falls back
to trying its second preference and so on. Eventually it will fall back all the
way to the ``native`` implementation. This is a pure Python implementation
built into GPIO Zero itself. While this will work for most things it's almost
certainly not what you want (it doesn't support PWM, and it's quite slow at
certain things).

If you want to use a pin driver other than the default, and you want to
suppress the warnings you've got a couple of options:

1. Explicitly specify what pin driver you want via an environment variable. For
   example:

   .. code-block:: console

       $ GPIOZERO_PIN_FACTORY=pigpio python

   In this case no warning is issued because there's no fallback; either the
   specified factory loads or it fails in which case an :exc:`ImportError` will
   be raised.

2. Suppress the warnings and let the fallback mechanism work::

    >>> import warnings
    >>> warnings.simplefilter('ignore')
    >>> import gpiozero

   Refer to the :mod:`warnings` module documentation for more refined ways to
   filter out specific warning classes.

