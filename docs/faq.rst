.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
.. Copyright (c) 2017-2019 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2017-2019 Ben Nuttall <ben@bennuttall.com>
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

.. _faq:

==========================
Frequently Asked Questions
==========================

.. currentmodule:: gpiozero


.. _keep-your-script-running:

How do I keep my script running?
================================

The following script looks like it should turn an :class:`LED` on::

    from gpiozero import LED

    led = LED(17)
    led.on()

And it does, if you're using the Python or IPython shell, or the IDLE, Thonny or
Mu editors. However, if you saved this script as a Python file and ran it, it
would flash on briefly, then the script would end and it would turn off.

The following file includes an intentional :func:`~signal.pause` to keep the
script alive::

    from gpiozero import LED
    from signal import pause

    led = LED(17)
    led.on()

    pause()

Now the script will stay running, leaving the LED on, until it is terminated
manually (e.g. by pressing Ctrl+C). Similarly, when setting up callbacks on
button presses or other input devices, the script needs to be running for the
events to be detected::

    from gpiozero import Button
    from signal import pause

    def hello():
        print("Hello")

    button = Button(2)
    button.when_pressed = hello

    pause()


My event handler isn't being called
===================================

When assigning event handlers, don't call the function you're assigning. For
example::

    from gpiozero import Button

    def pushed():
        print("Don't push the button!")

    b = Button(17)
    b.when_pressed = pushed()

In the case above, when assigning to :attr:`~Button.when_pressed`, the thing
that is assigned is the *result of calling* the ``pushed`` function. Because
``pushed`` doesn't explicitly return anything, the result is :data:`None`.
Hence this is equivalent to doing::

    b.when_pressed = None

This doesn't raise an error because it's perfectly valid: it's what you assign
when you don't want the event handler to do anything. Instead, you want to
do the following::

    b.when_pressed = pushed

This will assign the function to the event handler *without calling it*. This
is the crucial difference between ``my_function`` (a reference to a function)
and ``my_function()`` (the result of calling a function).

.. note::

    Note that as of v1.5, setting a callback to :data:`None` when it was
    previously :data:`None` will raise a :class:`CallbackSetToNone` warning,
    with the intention of alerting users when callbacks are set to :data:`None`
    accidentally. However, if this is intentional, the warning can be
    suppressed. See the :mod:`warnings` module for reference.

.. _pinfactoryfallback-warnings:

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

1. Explicitly specify what pin driver you want via the
   :envvar:`GPIOZERO_PIN_FACTORY` environment variable. For example:

   .. code-block:: console

       $ GPIOZERO_PIN_FACTORY=pigpio python3

   In this case no warning is issued because there's no fallback; either the
   specified factory loads or it fails in which case an :exc:`ImportError` will
   be raised.

2. Suppress the warnings and let the fallback mechanism work:

   .. code-block:: pycon

        >>> import warnings
        >>> warnings.simplefilter('ignore')
        >>> import gpiozero

   Refer to the :mod:`warnings` module documentation for more refined ways to
   filter out specific warning classes.


How can I tell what version of gpiozero I have installed?
=========================================================

The gpiozero library relies on the setuptools package for installation
services.  You can use the setuptools :mod:`pkg_resources` API to query which
version of gpiozero is available in your Python environment like so:

.. code-block:: pycon

    >>> from pkg_resources import require
    >>> require('gpiozero')
    [gpiozero 1.5.1 (/usr/lib/python3/dist-packages)]
    >>> require('gpiozero')[0].version
    '1.5.1'

If you have multiple versions installed (e.g. from :command:`pip` and
:command:`apt`) they will not show up in the list returned by the
:meth:`pkg_resources.require` method. However, the first entry in the list will
be the version that ``import gpiozero`` will import.

If you receive the error "No module named pkg_resources", you need to install
:command:`pip`. This can be done with the following command in Raspbian:

.. code-block:: console

    $ sudo apt install python3-pip

Alternatively, install pip with `get-pip`_.


Why do I get "command not found" when running pinout?
=====================================================

The gpiozero library is available as a Debian package for Python 2 and Python
3, but the :doc:`cli_pinout` tool cannot be made available by both packages, so
it's only included with the Python 3 version of the package. To make sure the
:doc:`cli_pinout` tool is available, the "python3-gpiozero" package must be
installed:

.. code-block:: console

    $ sudo apt install python3-gpiozero

Alternatively, installing gpiozero using :command:`pip` will install the
command line tool, regardless of Python version:

.. code-block:: console

    $ sudo pip3 install gpiozero

or:

.. code-block:: console

    $ sudo pip install gpiozero


The pinout command line tool incorrectly identifies my Raspberry Pi model
=========================================================================

If your Raspberry Pi model is new, it's possible it wasn't known about at the
time of the gpiozero release you are using. Ensure you have the latest version
installed (remember, the :doc:`cli_pinout` tool usually comes from the Python 3
version of the package as noted in the previous FAQ).

If the Pi model you are using isn't known to gpiozero, it may have been added
since the last release. You can check the `GitHub issues`_ to see if it's been
reported before, or check the `commits`_ on GitHub since the last release to
see if it's been added. The model determination can be found in
:file:`gpiozero/pins/data.py`.


.. _gpio-cleanup:

What's the gpiozero equivalent of GPIO.cleanup()?
=================================================

Many people ask how to do the equivalent of the ``cleanup`` function from
``RPi.GPIO``. In gpiozero, at the end of your script, cleanup is run
automatically, restoring your GPIO pins to the state they were found.

To explicitly close a connection to a pin, you can manually call the
:meth:`~Device.close` method on a device object:

.. code-block:: pycon

    >>> led = LED(2)
    >>> led.on()
    >>> led
    <gpiozero.LED object on pin GPIO2, active_high=True, is_active=True>
    >>> led.close()
    >>> led
    <gpiozero.LED object closed>

This means that you can reuse the pin for another device, and that despite
turning the LED on (and hence, the pin high), after calling
:meth:`~Device.close` it is restored to its previous state (LED off, pin low).


How do I use button.when_pressed and button.when_held together?
===============================================================

The :class:`Button` class provides a :attr:`~Button.when_held` property which
is used to set a callback for when the button is held down for a set amount of
time (as determined by the :attr:`~Button.hold_time` property). If you want to
set :attr:`~Button.when_held` as well as :attr:`~Button.when_pressed`, you'll
notice that both callbacks will fire. Sometimes, this is acceptable, but often
you'll want to only fire the :attr:`~Button.when_pressed` callback when the
button has not been held, only pressed.

The way to achieve this is to *not* set a callback on
:attr:`~Button.when_pressed`, and instead use :attr:`~Button.when_released` to
work out whether it had been held or just pressed::

    from gpiozero import Button

    Button.was_held = False

    def held(btn):
        btn.was_held = True
        print("button was held not just pressed")

    def released(btn):
        if not btn.was_held:
            pressed()
        btn.was_held = False

    def pressed():
        print("button was pressed not held")

    btn = Button(2)

    btn.when_held = held
    btn.when_released = released


Why do I get "ImportError: cannot import name" when trying to import from gpiozero?
===================================================================================

It's common to see people name their first gpiozero script ``gpiozero.py``.
Unfortunately, this will cause your script to try to import itself, rather than
the gpiozero library from the libraries path. You'll see an error like this::

    Traceback (most recent call last):
      File "gpiozero.py", line 1, in <module>
        from gpiozero import LED
      File "/home/pi/gpiozero.py", line 1, in <module>
        from gpiozero import LED
    ImportError: cannot import name 'LED'

Simply rename your script to something else, and run it again. Be sure not to
name any of your scripts the same name as a Python module you may be importing,
such as :file:`picamera.py`.


Why do I get an AttributeError trying to set attributes on a device object?
===========================================================================

If you try to add an attribute to a gpiozero device object after its
initialization, you'll find you can't:

.. code-block:: pycon

    >>> from gpiozero import Button
    >>> btn = Button(2)
    >>> btn.label = 'alarm'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/lib/python3/dist-packages/gpiozero/devices.py", line 118, in __setattr__
        self.__class__.__name__, name))
    AttributeError: 'Button' object has no attribute 'label'

This is in order to prevent users accidentally setting new attributes by
mistake. Because gpiozero provides functionality through setting attributes via
properties, such as callbacks on buttons (and often there is no immediate
feedback when setting a property), this could lead to bugs very difficult to
find. Consider the following example::

    from gpiozero import Button

    def hello():
        print("hello")

    btn = Button(2)

    btn.pressed = hello

This is perfectly valid Python code, and no errors would occur, but the program
would not behave as expected: pressing the button would do nothing, because the
property for setting a callback is ``when_pressed`` not ``pressed``. But
without gpiozero preventing this non-existent attribute from being set, the
user would likely struggle to see the mistake.

If you really want to set a new attribute on a device object, you need to
create it in the class before initializing your object:

.. code-block:: pycon

    >>> from gpiozero import Button
    >>> Button.label = ''
    >>> btn = Button(2)
    >>> btn.label = 'alarm'
    >>> def press(btn):
    ...:    print(btn.label, "was pressed")
    >>> btn.when_pressed = press


Why is it called GPIO Zero? Does it only work on Pi Zero?
=========================================================

gpiozero works on all Raspberry Pi models, not just the Pi Zero.

The "zero" is part of a naming convention for "zero-boilerplate" education
friendly libraries, which started with `Pygame Zero`_, and has been followed by
`NetworkZero`_, `guizero`_ and more.

These libraries aim to remove barrier to entry and provide a smooth learning
curve for beginners by making it easy to get started and easy to build up to
more advanced projects.


.. _get-pip: https://pip.pypa.io/en/stable/installing/
.. _GitHub issues: https://github.com/gpiozero/gpiozero/issues
.. _commits: https://github.com/gpiozero/gpiozero/commits/master
.. _Pygame Zero: https://pygame-zero.readthedocs.io/en/stable/
.. _NetworkZero: https://networkzero.readthedocs.io/en/latest/
.. _guizero: https://lawsie.github.io/guizero/
