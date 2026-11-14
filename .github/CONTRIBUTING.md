# Contributing

Contributions to the library are welcome! Here are some guidelines to follow.

## State of the project

It should be noted that gpiozero is in a mature state and has not been developed
much in recent years. This is partly due to its state of completion in the
essentials, and partly due to the maintainers working on other projects. We aim
to continue to maintain the library to ensure it remains useful for Raspberry Pi
users, but we are not actively developing it further. It is unlikely support for
additional GPIO devices will be added, but we encourage people to publish
complementary libraries - see the section below.

## AI contributions

If you are not a gpiozero user and your intention is to throw our issues at an
AI agent and produce PRs for the sake of it, this is not helpful and we ask you
not to do this.

If you are a gpiozero user and you experience a problem yourself, we welcome
your contributions and will not forbid the use of AI. However, all PRs take time
and effort for the maintainers to review, so please follow the usual guidelines.
Note that your use of AI may make it more difficult for you to answer questions
without help during the review and you may find yourself becoming a [meat
proxy](https://meatproxy.me/).

If you have an idea or any thoughts to contribute, these could be helpful so
please add them to the conversation on the relevant GitHub issue. This may be
more useful than asking an AI agent to solve the problem and asking us to review
it.

## Suggestions

Please make suggestions for additional components or enhancements to the
codebase by opening an [issue](https://github.com/gpiozero/gpiozero/issues)
explaining your reasoning clearly.

## Bugs

Please submit bug reports by opening an [issue](https://github.com/gpiozero/gpiozero/issues)
explaining the problem clearly using code examples.

## Duplicates

Before opening a new issue, look to see if the issue has been opened already,
and add any relevant information to the discussion in the existing issue.

## Documentation

The documentation source lives in the
[docs](https://github.com/gpiozero/gpiozero/tree/main/docs) folder. If your code
changes require an update to the documentation, please make sure to do so in
your pull request.

Please also build the docs locally, check for errors and 

## Commit messages and pull requests

Commit messages should be concise but descriptive, and in the form of a patch
description, i.e. instructional not past tense ("Add LED example" not "Added
LED example").

Pull requests which intend to close an issue should include a link to the issue
it closes. See [Linking a pull request to an issue using a
keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)

## Backwards compatibility

Since this library reached v1.0 we aim to maintain backwards-compatibility
thereafter. Changes which break backwards-compatibility will not be accepted.

## Separate libraries

Some additions would to better suited to being published as a separate library,
especially if they are for bespoke hardware or require additional dependencies.
Publishing libraries prefixed with `gpiozero-` is encouraged, for example
[gpiozero-sequent-microsystems](https://pypi.org/project/gpiozero-sequent-microsystems).