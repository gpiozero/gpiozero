.. GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
..
.. Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
.. Copyright (c) 2016-2021 Ben Nuttall <ben@bennuttall.com>
.. Copyright (c) 2017 rgm <roland@securelink.com>
..
.. SPDX-License-Identifier: BSD-3-Clause

.. _contributing:

============
Contributing
============

Contributions to the library are welcome! Here are some guidelines to follow.


Suggestions
===========

Please make suggestions for additional components or enhancements to the
codebase by opening an `issue`_ explaining your reasoning clearly.


Bugs
====

Please submit bug reports by opening an `issue`_ explaining the problem clearly
using code examples.


Documentation
=============

The documentation source lives in the `docs`_ folder. Contributions to the
documentation are welcome but should be easy to read and understand.


Commit messages and pull requests
=================================

Commit messages should be concise but descriptive, and in the form of a patch
description, i.e. instructional not past tense ("Add LED example" not "Added
LED example").

Commits which close (or intend to close) an issue should include the phrase
"fix #123" or "close #123" where ``#123`` is the issue number, as well as
include a short description, for example: "Add LED example, close #123", and
pull requests should aim to match or closely match the corresponding issue
title.

Copyrights on submissions are owned by their authors (we don't bother with
copyright assignments), and we assume that authors are happy for their code to
be released under the project's :doc:`license <license>`. Do feel free to add
your name to the list of contributors in :file:`README.rst` at the top level of
the project in your pull request! Don't worry about adding your name to the
copyright headers in whatever files you touch; these are updated automatically
from the git metadata before each release.


Backwards compatibility
=======================

Since this library reached v1.0 we aim to maintain backwards-compatibility
thereafter. Changes which break backwards-compatibility will not be accepted.


Python 2/3
==========

The library is 100% compatible with both Python 2.7 and Python 3 from version
3.2 onwards. Since Python 2 is now past its `end-of-life`_, the 1.6.2 release
(2021-03-18) is the last to support Python 2.


.. _docs: https://github.com/gpiozero/gpiozero/tree/master/docs
.. _issue: https://github.com/gpiozero/gpiozero/issues/new
.. _end-of-life: http://legacy.python.org/dev/peps/pep-0373/
