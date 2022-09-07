from __future__ import annotations

import argparse

from rich_argparse import RichHelpFormatter
from tests.conftest import assert_help_output

_POETRY_CLONE_HELP = """\
usage: poetry [-h] [-q] [-v] [-V] [--ansi] [--no-ansi] [-n] <command> ...

GLOBAL OPTIONS
  -h, --help            Display this help message
  -q, --quiet           Do not output any message
  -v, --verbose         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                        verbose output and "-vvv" for debug
  -V, --version         Display this application version
  --ansi                Force ANSI output
  --no-ansi             Disable ANSI output
  -n, --no-interaction  Do not ask any interactive question

AVAILABLE COMMANDS
  <command>             The command to execute
    about               Shows information about Poetry.
    add                 Adds a new dependency to pyproject.toml.
    build               Builds a package, as a tarball and a wheel by default.
    cache               Interact with Poetry's cache
    check               Checks the validity of the pyproject.toml file.
    config              Manages configuration settings.
    debug               Debug various elements of Poetry.
    env                 Interact with Poetry's project environments.
    export              Exports the lock file to alternative formats.
    help                Display the manual of a command
    init                Creates a basic pyproject.toml file in the current directory.
    install             Installs the project dependencies.
    lock                Locks the project dependencies.
    new                 Creates a new Python project at <path>.
    publish             Publishes a package to a remote repository.
    remove              Removes a package from the project dependencies.
    run                 Runs a command in the appropriate environment.
    search              Searches for packages on remote repositories.
    self                Interact with Poetry directly.
    shell               Spawns a shell within the virtual environment.
    show                Shows information about packages.
    update              Update the dependencies as according to the pyproject.toml file.
    version             Shows the version of the project or bumps it when a valid bump rule is
                        provided.

"""

_POETRY_CLONE_HELP_HELP = """\
usage: poetry help [-h] [-q] [-v] [-V] [--ansi] [--no-ansi] [-n] [<command>]

POSITIONAL ARGUMENTS
  <command>             The command name

GLOBAL OPTIONS
  -h, --help            Display this help message
  -q, --quiet           Do not output any message
  -v, --verbose         Increase the verbosity of messages: "-v" for normal output, "-vv" for more
                        verbose output and "-vvv" for debug
  -V, --version         Display this application version
  --ansi                Force ANSI output
  --no-ansi             Disable ANSI output
  -n, --no-interaction  Do not ask any interactive question

"""


def _poetry_clone_parser() -> argparse.ArgumentParser:
    RichHelpFormatter.styles["argparse.pyproject"] = "green"
    RichHelpFormatter.highlights.append(r"\W(?P<pyproject>pyproject\.toml)\W")

    def add_global_options(parser: argparse.ArgumentParser) -> argparse._ArgumentGroup:
        options_group = parser.add_argument_group(title="global options")
        options_group.add_argument("-h", "--help", action="help", help="Display this help message")
        options_group.add_argument(
            "-q", "--quiet", action="store_true", help="Do not output any message"
        )
        options_group.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help=(
                'Increase the verbosity of messages: "-v" for normal output, "-vv" for more '
                'verbose output and "-vvv" for debug'
            ),
        )
        options_group.add_argument(
            "-V",
            "--version",
            action="version",
            version="1.0.0",
            help="Display this application version",
        )
        options_group.add_argument("--ansi", action="store_true", help="Force ANSI output")
        options_group.add_argument(
            "--no-ansi", action="store_false", dest="ansi", help="Disable ANSI output"
        )
        options_group.add_argument(
            "-n",
            "--no-interaction",
            action="store_true",
            help="Do not ask any interactive question",
        )
        return options_group

    parser = argparse.ArgumentParser(
        prog="poetry", formatter_class=RichHelpFormatter, add_help=False
    )
    add_global_options(parser)

    subparsers = parser.add_subparsers(
        title="available commands",
        dest="command",
        metavar="<command>",
        help="The command to execute",
        required=True,
    )
    commands = []  # store commands for the `help` command options

    def add_subparser(name: str, **kwds) -> argparse.ArgumentParser:
        kwds.setdefault("formatter_class", parser.formatter_class)
        kwds.setdefault("add_help", False)
        sub_parser = subparsers.add_parser(name, **kwds)
        add_global_options(sub_parser)
        commands.append(name)
        return sub_parser

    about_parser = add_subparser("about", help="Shows information about Poetry.")
    add_parser = add_subparser("add", help="Adds a new dependency to pyproject.toml.")
    build_parser = add_subparser(
        "build", help="Builds a package, as a tarball and a wheel by default."
    )
    cache_parser = add_subparser("cache", help="Interact with Poetry's cache")
    check_parser = add_subparser("check", help="Checks the validity of the pyproject.toml file.")
    config_parser = add_subparser("config", help="Manages configuration settings.")
    debug_parser = add_subparser("debug", help="Debug various elements of Poetry.")
    env_parser = add_subparser("env", help="Interact with Poetry's project environments.")
    export_parser = add_subparser("export", help="Exports the lock file to alternative formats.")
    help_parser = add_subparser("help", help="Display the manual of a command")
    help_parser.add_argument(
        "help_command", metavar="<command>", choices=commands, nargs="?", help="The command name"
    )
    init_parser = add_subparser(
        "init", help="Creates a basic pyproject.toml file in the current directory."
    )
    install_parser = add_subparser("install", help="Installs the project dependencies.")
    install_parser.add_argument(
        "--no-dev", action="store_true", help="Do not install the development dependencies."
    )
    lock_parser = add_subparser("lock", help="Locks the project dependencies.")
    new_parser = add_subparser("new", help="Creates a new Python project at <path>.")
    publish_parser = add_subparser("publish", help="Publishes a package to a remote repository.")
    remove_parser = add_subparser("remove", help="Removes a package from the project dependencies.")
    run_parser = add_subparser("run", help="Runs a command in the appropriate environment.")
    search_parser = add_subparser("search", help="Searches for packages on remote repositories.")
    self_parser = add_subparser("self", help="Interact with Poetry directly.")
    shell_parser = add_subparser("shell", help="Spawns a shell within the virtual environment.")
    show_parser = add_subparser("show", help="Shows information about packages.")
    update_parser = add_subparser(
        "update", help="Update the dependencies as according to the pyproject.toml file."
    )
    version_parser = add_subparser(
        "version",
        help="Shows the version of the project or bumps it when a valid bump rule is provided.",
    )
    return parser


def test_poetry_help():
    assert_help_output(
        parser=_poetry_clone_parser(), cmd=["--help"], expected_output=_POETRY_CLONE_HELP
    )


def test_poetry_help_subparser():
    assert_help_output(
        parser=_poetry_clone_parser(),
        cmd=["help", "--help"],
        expected_output=_POETRY_CLONE_HELP_HELP,
    )
