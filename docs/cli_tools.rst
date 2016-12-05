==================
Command-line Tools
==================

Pinout
======

The gpiozero package contains a database of information about the various
revisions of Raspberry Pi. This is queried by the ``pinout`` command-line
tool to write details of the GPIO pins available.

Unless specified, the revision of the current device will be detected. A
particular revision may be selected with the --revision command-line
option. e.g::

    pinout --revision 000d

By default, the output will include ANSI color codes if run in a color-capable
terminal. This behaviour may be overridden by the --color or --monochrome
options to force colored or non-colored output, respectively. e.g::

    pinout --monochrome

Full usage details are available with::

    pinout --help
