===========
Development
===========

.. currentmodule:: gpiozero

The main GitHub repository for the project can be found at:

    https://github.com/RPi-Distro/python-gpiozero

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

    $ sudo apt install lsb-release build-essential git git-core \
    >   exuberant-ctags virtualenvwrapper python-virtualenv python3-virtualenv \
    >   python-dev python3-dev
    $ cd
    $ mkvirtualenv -p /usr/bin/python3 python-gpiozero
    $ workon python-gpiozero
    (python-gpiozero) $ git clone https://github.com/RPi-Distro/python-gpiozero.git
    (python-gpiozero) $ cd python-gpiozero
    (python-gpiozero) $ make develop

You will likely wish to install one or more pin implementations within the
virtual environment (if you don't, GPIO Zero will use the "native" pin
implementation which is largely experimental at this stage and not very
useful):

.. code-block:: console

    (python-gpiozero) $ pip install rpi.gpio pigpio

If you are working on SPI devices you may also wish to install the ``spidev``
package to provide hardware SPI capabilities (again, GPIO Zero will work
without this, but a big-banging software SPI implementation will be used
instead):

.. code-block:: console

    (python-gpiozero) $ pip install spidev

To pull the latest changes from git into your clone and update your
installation:

.. code-block:: console

    $ workon python-gpiozero
    (python-gpiozero) $ cd ~/python-gpiozero
    (python-gpiozero) $ git pull
    (python-gpiozero) $ make develop

To remove your installation, destroy the sandbox and the clone:

.. code-block:: console

    (python-gpiozero) $ deactivate
    $ rmvirtualenv python-gpiozero
    $ rm -fr ~/python-gpiozero


Building the docs
=================

If you wish to build the docs, you'll need a few more dependencies. Inkscape
is used for conversion of SVGs to other formats, Graphviz is used for rendering
certain charts, and TeX Live is required for building PDF output. The following
command should install all required dependencies:

.. code-block:: console

    $ sudo apt install texlive-latex-recommended texlive-latex-extra \
        texlive-fonts-recommended graphviz inkscape

Once these are installed, you can use the "doc" target to build the
documentation:

.. code-block:: console

    $ workon python-gpiozero
    (python-gpiozero) $ cd ~/python-gpiozero
    (python-gpiozero) $ make doc

The HTML output is written to :file:`docs/_build/html` while the PDF output
goes to :file:`docs/_build/latex`.


Test suite
==========

If you wish to run the GPIO Zero test suite, follow the instructions in
:ref:`dev_install` above and then make the "test" target within the sandbox:

.. code-block:: console

    $ workon python-gpiozero
    (python-gpiozero) $ cd ~/python-gpiozero
    (python-gpiozero) $ make test

The test suite expects pins 22 and 27 (by default) to be wired together in
order to run the "real" pin tests. The pins used by the test suite can be
overridden with the environment variables ``GPIOZERO_TEST_PIN`` (defaults to
22) and ``GPIOZERO_TEST_INPUT_PIN`` (defaults to 27).

.. warning::

    When wiring GPIOs together, ensure a load (like a 330Ω resistor) is placed
    between them. Failure to do so may lead to blown GPIO pins (your humble
    author has a fried GPIO27 as a result of such laziness, although it did
    take *many* runs of the test suite before this occurred!).
