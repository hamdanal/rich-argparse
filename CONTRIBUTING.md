# Contributing to rich-argparse

The best way to contribute to this project is by opening an issue in the issue tracker. Issues for
reporting bugs or requesting new features are all welcome and appreciated. Also, [Discussions] are
open for any discussion related to this project. There you can ask questions, discuss ideas, or
simply show your clever snippets or hacks.

Code contributions are also welcome in the form of Pull Requests. For these you need to open an
issue prior to starting work to discuss it first (with the exception of very clear bug fixes and
typo fixes where an issue may not be needed).

## Getting started

*python* version 3.8 or higher is required for development.

1. Fork the repository on GitHub.

2. Clone the repository:

   ```sh
   git clone git@github.com:<YOUR_USERNAME>/rich-argparse.git
   cd rich_argparse
   ```
3. Create and activate a virtual environment:

   ```sh
   python3 -m venv venv
   . venv/bin/activate  # Linux and macOS
   ```
   > **Note**
   > Windows users follow [this guide][venv-guide] to create and activate a virtual environment.

4. Install the project and its dependencies:

   ```sh
   python3 -m pip install -r requirements-dev.txt
   ```

## Testing

Running all the tests can be done with `tox run -e py310` (or any other interpreter version). This
also runs the test coverage to insure 100% of the code is covered by tests.

Alternatively, you can run `coverage run -m pytest && coverage report` with the virtual environment
activated. You can also run a individual tests with `pytest -k the_name_of_your_test`.

### Code quality

After staging your work with `git add`, you can run `pre-commit run --all-files` to run all the
code quality tools. These include [black] and [ruff] for formatting and linting, and [mypy] for
type checking. You can also run each tool individually with `pre-commit run <tool> --all-files`.

## Creating a Pull Request

Once you are happy with your change you can create a pull request. GitHub offers a guide on how to
do this [here][PR]. Please ensure that you include a good description of what your change does in
your pull request, and link it to any relevant issues or discussions.

[Discussions]: https://github.com/hamdanal/rich-argparse/discussions
[mypy]: https://mypy.readthedocs.io/en/stable/
[black]: https://black.readthedocs.io/en/stable/
[ruff]: https://beta.ruff.rs/docs/
[PR]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork
[venv-guide]: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
