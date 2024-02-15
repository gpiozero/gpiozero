.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2017-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2018 Steveis <SteveAmor@users.noreply.github.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

===========
Development
===========

.. currentmodule:: gpiozero

The main GitHub repository for the project can be found at:

    https://github.com/gpiozero/gpiozero

For anybody wishing to hack on the project, we recommend starting off by
getting to grips with some simple device classes. Pick something like
:class:`LED` and follow its heritage backward to :class:`DigitalOutputDevice`.
Follow that back to :class:`OutputDevice` and you should have a good
understanding of simple output devices along with a grasp of how GPIO Zero
relies fairly heavily upon inheritance to refine the functionality of devices.
The same can be done for input devices, and eventually more complex devices
(composites and SPI based).


.. _dev_install:

Development installation
========================

If you wish to develop GPIO Zero itself, we recommend obtaining the source by
cloning the GitHub repository and then use the "develop" target of the Makefile
which will install the package as a link to the cloned repository allowing
in-place development (it also builds a tags file for use with vim/emacs with
Exuberant’s ctags utility). The following example demonstrates this method
within a virtual Python environment:

.. code-block:: console

    $ sudo apt install lsb-release build-essential git exuberant-ctags \
        virtualenvwrapper python-virtualenv python3-virtualenv \
        python-dev python3-dev

After installing ``virtualenvwrapper`` you'll need to restart your shell before
commands like :command:`mkvirtualenv` will operate correctly. Once you've
restarted your shell, continue:

.. code-block:: console

    $ cd
    $ mkvirtualenv -p /usr/bin/python3 gpiozero
    $ workon gpiozero
    (gpiozero) $ git clone https://github.com/gpiozero/gpiozero.git
    (gpiozero) $ cd gpiozero
    (gpiozero) $ make develop

You will likely wish to install one or more pin implementations within the
virtual environment (if you don't, GPIO Zero will use the "native" pin
implementation which is usable at this stage, but doesn't support facilities
like PWM):

.. code-block:: console

    (gpiozero) $ pip install rpi.gpio pigpio

If you are working on SPI devices you may also wish to install the ``spidev``
package to provide hardware SPI capabilities (again, GPIO Zero will work
without this, but a big-banging software SPI implementation will be used
instead which limits bandwidth):

.. code-block:: console

    (gpiozero) $ pip install spidev

To pull the latest changes from git into your clone and update your
installation:

.. code-block:: console

    $ workon gpiozero
    (gpiozero) $ cd ~/gpiozero
    (gpiozero) $ git pull
    (gpiozero) $ make develop

To remove your installation, destroy the sandbox and the clone:

.. code-block:: console

    (gpiozero) $ deactivate
    $ rmvirtualenv gpiozero
    $ rm -rf ~/gpiozero


Building the docs
=================

If you wish to build the docs, you'll need a few more dependencies. Inkscape
is used for conversion of SVGs to other formats, Graphviz is used for rendering
certain charts, and TeX Live is required for building PDF output. The following
command should install all required dependencies:

.. code-block:: console

    $ sudo apt install texlive-latex-recommended texlive-latex-extra \
        texlive-fonts-recommended texlive-xetex graphviz inkscape \
        python3-sphinx python3-sphinx-rtd-theme latexmk xindy

Once these are installed, you can use the "doc" target to build the
documentation:

.. code-block:: console

    $ workon gpiozero
    (gpiozero) $ cd ~/gpiozero
    (gpiozero) $ make doc

The HTML output is written to :file:`build/html` while the PDF output
goes to :file:`build/latex`.


Test suite
==========

If you wish to run the GPIO Zero test suite, follow the instructions in
:ref:`dev_install` above and then make the "test" target within the sandbox.
You'll also need to install some pip packages:

.. code-block:: console

    $ workon gpiozero
    (gpiozero) $ pip install coverage mock pytest
    (gpiozero) $ cd ~/gpiozero
    (gpiozero) $ make test

The test suite expects pins 22 and 27 (by default) to be wired together in
order to run the "real" pin tests. The pins used by the test suite can be
overridden with the environment variables :envvar:`GPIOZERO_TEST_PIN` (defaults
to 22) and :envvar:`GPIOZERO_TEST_INPUT_PIN` (defaults to 27).

.. warning::

    When wiring GPIOs together, ensure a load (like a 1KΩ resistor) is placed
    between them. Failure to do so may lead to blown GPIO pins (your humble
    author has a fried GPIO27 as a result of such laziness, although it did
    take *many* runs of the test suite before this occurred!).

The test suite is also setup for usage with the :command:`tox` utility, in
which case it will attempt to execute the test suite with all supported
versions of Python. If you are developing under Ubuntu you may wish to look
into the `Dead Snakes PPA`_ in order to install old/new versions of Python; the
tox setup *should* work with the version of tox shipped with Ubuntu Xenial, but
more features (like parallel test execution) are available with later versions.

On the subject of parallel test execution, this is also supported in the tox
setup, including the "real" pin tests (a file-system level lock is used to
ensure different interpreters don't try to access the physical pins
simultaneously).

For example, to execute the test suite under tox, skipping interpreter versions
which are not installed:

.. code-block:: console

    $ tox -s

To execute the test suite under all installed interpreter versions in parallel,
using as many parallel tasks as there are CPUs, then displaying a combined
report of coverage from all environments:

.. code-block:: console

    $ tox -p auto -s
    $ coverage combine --rcfile coverage.cfg
    $ coverage report --rcfile coverage.cfg


.. _Dead Snakes PPA: https://launchpad.net/~deadsnakes/%2Barchive/ubuntu/ppa


Mock pins
=========

The test suite largely depends on the existence of the mock pin factory
:class:`~gpiozero.pins.mock.MockFactory`, which is also useful for manual
testing, for example in the Python shell or another REPL. See the section on
:ref:`mock-pins` in the :doc:`api_pins` chapter for more information.
