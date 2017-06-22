=====
Notes
=====

.. currentmodule:: gpiozero


.. _keep-your-script-running:

Keep your script running
========================

The following script looks like it should turn an LED on::

    from gpiozero import LED

    led = LED(17)
    led.on()

And it does, if you're using the Python (or IPython or IDLE) shell. However,
if you saved this script as a Python file and ran it, it would flash on
briefly, then the script would end and it would turn off.

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


Importing from GPIO Zero
========================

In Python, libraries and functions used in a script must be imported by name
at the top of the file, with the exception of the functions built into Python
by default.

For example, to use the :class:`Button` interface from GPIO Zero, it
should be explicitly imported::

    from gpiozero import Button

Now :class:`~gpiozero.Button` is available directly in your script::

    button = Button(2)

Alternatively, the whole GPIO Zero library can be imported::

    import gpiozero

In this case, all references to items within GPIO Zero must be prefixed::

    button = gpiozero.Button(2)


How can I tell what version of gpiozero I have installed?
=========================================================

The gpiozero library relies on the setuptools package for installation
services.  You can use the setuptools ``pkg_resources`` API to query which
version of gpiozero is available in your Python environment like so:

.. code-block:: pycon

    >>> from pkg_resources import require
    >>> require('gpiozero')
    [gpiozero 1.3.2 (/usr/lib/python3/dist-packages)]
    >>> require('gpiozero')[0].version
    '1.3.2'

If you have multiple versions installed (e.g. from ``pip`` and ``apt``) they
will not show up in the list returned by the ``require`` method. However, the
first entry in the list will be the version that ``import gpiozero`` will
import.

If you receive the error "No module named pkg_resources", you need to install
the ``pip`` utility. This can be done with the following command in Raspbian:

.. code-block:: console

    sudo apt install python-pip

Alternatively, install pip with `get-pip`_.


.. _get_pip: https://pip.pypa.io/en/stable/installing/
