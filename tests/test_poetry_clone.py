import argparse
import os
import sys
from unittest import mock

import pytest

from rich_argparse import RichHelpFormatter

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
if sys.version_info[:2] >= (3, 10):
    _POETRY_CLONE_HELP_HELP = _POETRY_CLONE_HELP_HELP.replace(
        "\nOPTIONAL ARGUMENTS\n", "\nOPTIONS\n"
    )


def _poetry_clone_parser():
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
        parser_class=lambda **k: type(parser)(
            **k, formatter_class=parser.formatter_class, add_help=False
        ),
    )
    original_add_parser = subparsers.add_parser

    def add_parser(*a, **k):
        sp = original_add_parser(*a, **k)
        add_global_options(sp)
        return sp

    subparsers.add_parser = add_parser

    about_parser = subparsers.add_parser("about", help="Shows information about Poetry.")
    add_parser = subparsers.add_parser("add", help="Adds a new dependency to pyproject.toml.")
    build_parser = subparsers.add_parser(
        "build", help="Builds a package, as a tarball and a wheel by default."
    )
    cache_parser = subparsers.add_parser("cache", help="Interact with Poetry's cache")
    check_parser = subparsers.add_parser(
        "check", help="Checks the validity of the pyproject.toml file."
    )
    config_parser = subparsers.add_parser("config", help="Manages configuration settings.")
    debug_parser = subparsers.add_parser("debug", help="Debug various elements of Poetry.")
    env_parser = subparsers.add_parser("env", help="Interact with Poetry's project environments.")
    export_parser = subparsers.add_parser(
        "export", help="Exports the lock file to alternative formats."
    )
    help_parser = subparsers.add_parser("help", help="Display the manual of a command")
    help_parser.add_argument(
        "help_command",
        metavar="<command>",
        choices=subparsers._name_parser_map,
        nargs="?",
        help="The command name",
    )
    init_parser = subparsers.add_parser(
        "init", help="Creates a basic pyproject.toml file in the current directory."
    )
    install_parser = subparsers.add_parser("install", help="Installs the project dependencies.")
    install_parser.add_argument(
        "--no-dev", action="store_true", help="Do not install the development dependencies."
    )
    lock_parser = subparsers.add_parser("lock", help="Locks the project dependencies.")
    new_parser = subparsers.add_parser("new", help="Creates a new Python project at <path>.")
    publish_parser = subparsers.add_parser(
        "publish", help="Publishes a package to a remote repository."
    )
    remove_parser = subparsers.add_parser(
        "remove", help="Removes a package from the project dependencies."
    )
    run_parser = subparsers.add_parser("run", help="Runs a command in the appropriate environment.")
    search_parser = subparsers.add_parser(
        "search", help="Searches for packages on remote repositories."
    )
    self_parser = subparsers.add_parser("self", help="Interact with Poetry directly.")
    shell_parser = subparsers.add_parser(
        "shell", help="Spawns a shell within the virtual environment."
    )
    show_parser = subparsers.add_parser("show", help="Shows information about packages.")
    update_parser = subparsers.add_parser(
        "update",
        help="Update the dependencies as according to the pyproject.toml file.",
    )
    version_parser = subparsers.add_parser(
        "version",
        help="Shows the version of the project or bumps it when a valid bump rule is provided.",
    )
    return parser


def test_poetry_help(capsys):
    parser = _poetry_clone_parser()
    with mock.patch.dict(os.environ, {"COLUMNS": "100"}), pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    out, err = capsys.readouterr()

    out_lines = out.splitlines()
    expected_out_lines = _POETRY_CLONE_HELP.splitlines()
    assert len(out_lines) == len(expected_out_lines)

    for line, expected_line in zip(out_lines, expected_out_lines):
        assert line.rstrip() == expected_line.rstrip()
    assert err == ""


def test_poetry_help_subparser(capsys):
    parser = _poetry_clone_parser()
    with mock.patch.dict(os.environ, {"COLUMNS": "100"}), pytest.raises(SystemExit):
        parser.parse_args(["help", "--help"])
    out, err = capsys.readouterr()

    out_lines = out.splitlines()
    expected_out_lines = _POETRY_CLONE_HELP_HELP.splitlines()
    assert len(out_lines) == len(expected_out_lines)

    for line, expected_line in zip(out_lines, expected_out_lines):
        assert line.rstrip() == expected_line.rstrip()
    assert err == ""
