from __future__ import annotations

import argparse

from rich_argparse import RichHelpFormatter
from tests.conftest import OPTIONS_GROUP_NAME, assert_help_output


def test_text_replaces_prog():
    # https://github.com/hamdanal/rich-argparse/issues/5
    parser = argparse.ArgumentParser(
        "awesome_program",
        description="This is the %(prog)s program.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    expected_help_output = f"""\
    usage: awesome_program [-h] [--version]

    This is the awesome_program program.

    {OPTIONS_GROUP_NAME}:
      -h, --help  show this help message and exit
      --version   show program's version number and exit
    """
    expected_version_output = """\
    awesome_program 1.0.0
    """
    assert_help_output(parser, cmd=["--version"], expected_output=expected_version_output)
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)


def test_spans():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("--flag", action="store_true", help="Is flag?")

    expected_help_output = (
        "    \x1b[38;5;174;49musage\x1b[0m\x1b[38;5;146;49m:\x1b[0m\x1b[38;5;146;49m \x1b[0m"
        "\x1b[38;5;174;49mPROG\x1b[0m\x1b[38;5;146;49m \x1b[0m\x1b[38;5;146;49m[\x1b[0m"
        "\x1b[38;5;116;49m-\x1b[0m\x1b[38;5;174;49mh\x1b[0m\x1b[38;5;146;49m]\x1b[0m"
        "\x1b[38;5;146;49m \x1b[0m\x1b[38;5;146;49m[\x1b[0m\x1b[38;5;116;49m--\x1b[0m"
        "\x1b[38;5;174;49mflag\x1b[0m\x1b[38;5;146;49m]\x1b[0m\x1b[38;5;146;49m \x1b[0m"
        "\x1b[38;5;174;49mfile\x1b[0m"
    )  # usage as syntax
    expected_help_output += f"""\


    \x1b[1;3;38;5;208mPOSITIONAL ARGUMENTS:\x1b[0m
      \x1b[3;36mfile\x1b[0m

    \x1b[1;3;38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[3;36m-h\x1b[0m, \x1b[3;36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
      \x1b[3;36m--flag\x1b[0m      \x1b[39mIs flag?\x1b[0m
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output, with_ansi=True)
