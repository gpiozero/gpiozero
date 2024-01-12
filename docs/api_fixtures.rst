.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. SPDX-License-Identifier: BSD-3-Clause

=====================
API - pytest Fixtures
=====================

.. module:: gpiozero.testing.fixtures

GPIO Zero includes fixtures for use with pytest which ensure that changes to
:attr:`Device.pin_factory` are correctly reset after and between tests.

These fixtures are the preferred method of using
:class:`~gpiozero.pins.mock.MockFactory` and its descendents.

They can be imported directly in your test or via your conftest.py either 
individually or all together using:

.. code-block:: python

    from gpiozero.testing import *

.. automodule:: gpiozero.testing.fixtures
    :members:

See :doc:`api_pins` for more details on the behaviour of
:class:`~gpiozero.pins.mock.MockFactory` 