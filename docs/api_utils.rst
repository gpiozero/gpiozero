=========
Utilities
=========

.. currentmodule:: gpiozero

The GPIO Zero library also contains a database of information about the various
revisions of Raspberry Pi. This is used internally to raise warnings when
non-physical pins are used, or to raise exceptions when pull-downs are
requested on pins with physical pull-up resistors attached. The following
functions and classes can be used to query this database:

.. autofunction:: pi_info

.. autoclass:: PiBoardInfo

.. autoclass:: HeaderInfo

.. autoclass:: PinInfo

