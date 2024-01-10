# Contributing

Contributions to the library are welcome! Here are some guidelines to follow.

## Suggestions

Please make suggestions for additional components or enhancements to the
codebase by opening an [issue](https://github.com/gpiozero/gpiozero/issues)
explaining your reasoning clearly.

## Bugs

Please submit bug reports by opening an [issue](https://github.com/gpiozero/gpiozero/issues)
explaining the problem clearly using code examples.

## Documentation

The documentation source lives in the [docs](https://github.com/gpiozero/gpiozero/tree/master/docs)
folder. Contributions to the documentation are welcome but should be easy to
read and understand.

## Commit messages and pull requests

Commit messages should be concise but descriptive, and in the form of a patch
description, i.e. instructional not past tense ("Add LED example" not "Added
LED example").

Commits which close (or intend to close) an issue should include the phrase
"fix #123" or "close #123" where `#123` is the issue number, as well as
include a short description, for example: "Add LED example, close #123", and
pull requests should aim to match or closely match the corresponding issue
title.

## Backwards compatibility

Since this library reached v1.0 we aim to maintain backwards-compatibility
thereafter. Changes which break backwards-compatibility will not be accepted.

## Python 2/3

The library is 100% compatible with both Python 2 and 3. We intend to drop
Python 2 support in 2020 when Python 2 reaches [end-of-life](http://legacy.python.org/dev/peps/pep-0373/).
