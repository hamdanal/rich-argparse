# Contributing to rich-argparse

The best way to contribute to this project is by opening an issue in the issue tracker. Issues for
reporting bugs or requesting new features are all welcome and appreciated. Also, [Discussions] are
open for any discussion related to this project. There you can ask questions, discuss ideas, or
simply show your clever snippets or hacks.

Code contributions are also welcome in the form of Pull Requests. For these you need to open an
issue prior to starting work to discuss it first (with the exception of very clear bug fixes and
typo fixes where an issue may not be needed).

## Prerequisites for code contributions

For local development you'll need the following installed:
* git
* python3 (3.7 or higher)
* tox (or virtualenv or python's venv module)
* pre-commit

### Setting up a development environment
This is needed to the run the test suite. The easiest way to set up a dev env is to use [tox]
(requires tox>=3.13). Simply run `tox --devenv venv` to create a virtual environment with all
the dev dependencies. To activate it run `. venv/bin/activate` if you are on *MacOS/Linux* and
`.\venv\Scripts\activate` if you are on *Windows*.

### Developing and testing
Any change made to code base needs to pass the test suite. If you are fixing a bug, add a test
that shows the fix. If you add a new feature, you have to add tests that cover all added code.

#### Running a specific test
Running a specific test with the environment activated is as easy as:
`pytest -k the_name_of_your_test`

#### Running all the tests
Running all the tests can be done by running `tox -e py39` (or your interpreter version of choice).
This also runs the test coverage to insure 100% of the code is covered by tests. Code that is not
tested with fail the Continuous Integration (CI) workflow on GitHub and will not be merged.

**Note** to run the tests with all supported python versions that are installed on your machine,
simply run `tox` (with no arguments).

### Code quality
This project has code quality standards that are enforced using [pre-commit]. Run
`pre-commit install` to have the checks run automatically on commit. You can also run
`pre-commit run --all-files` to run all the tools on all the files (but make sure you staged you
work with `git add` first). The following sections detail some of the tools used:

#### Type checking
This project uses type annotations throughout, and [mypy] to do the checking. Added code must be
type annotated and must pass mypy checking in *strict mode*.

#### Formatting
The project is formatted using [black] and [isort].

#### Linting
Code changes must not trigger linting errors by [flake8].

## Creating a Pull Request

Once your happy with your change and have ensured that all steps above have been followed (and
checks have passed), you can create a pull request. GitHub offers a guide on how to do this
[here][PR]. Please ensure that you include a good description of what your change does in your
pull request, and link it to any relevant issues or discussions.

When you create your pull request, we'll run the checks described earlier. If they fail, please
attempt to fix them as we're unlikely to be able to review your code until then. If you've
exhausted all options on trying to fix a failing check, feel free to leave a note saying so in the
pull request and someone may be able to offer assistance.

### Code Review
After the checks in your pull request pass, I will review your code. There may be some discussion
and, in most cases, a few iterations will be required to find a solution that works best.

## Afterwards
When the pull request is approved, it will be merged into the `main` branch.
Your change will only be available to users the next time rich-argparse is released.

[Discussions]: https://github.com/hamdanal/rich-argparse/discussions
[tox]: https://tox.wiki/en/latest/
[pre-commit]: https://pre-commit.com/
[mypy]: https://mypy.readthedocs.io/en/stable/
[black]: https://black.readthedocs.io/en/stable/
[isort]: https://pycqa.github.io/isort/
[flake8]: https://flake8.pycqa.org/en/latest/
[PR]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork
