from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from rich_argparse import RichHelpFormatter
from tests.conftest import OPTIONS_GROUP_NAME, assert_help_output, get_help_output


def test_params_substitution():
    # in text (description, epilog, group description) and version: substitute %(prog)s
    # in help message: substitute %(param)s for all param in vars(action)
    parser = argparse.ArgumentParser(
        "awesome_program",
        description="This is the %(prog)s program.",
        epilog="The epilog of %(prog)s.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("--option", default="value", help="help of option (default: %(default)s)")

    expected_help_output = f"""\
    usage: awesome_program [-h] [--version] [--option OPTION]

    This is the awesome_program program.

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --version        show program's version number and exit
      --option OPTION  help of option (default: value)

    The epilog of awesome_program.
    """
    expected_version_output = """\
    awesome_program 1.0.0
    """
    assert_help_output(parser, cmd=["--version"], expected_output=expected_version_output)
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)


@pytest.mark.parametrize("prog", (None, "PROG"), ids=("no_prog", "prog"))
@pytest.mark.parametrize("usage", (None, "USAGE"), ids=("no_usage", "usage"))
@pytest.mark.parametrize("description", (None, "A description."), ids=("no_desc", "desc"))
@pytest.mark.parametrize("epilog", (None, "An epilog."), ids=("no_epilog", "epilog"))
def test_overall_structure(prog, usage, description, epilog):
    # The output must be consistent with the original HelpFormatter in these cases:
    # 1. all names and help text are short to avoid special wrapping
    # 2. no short and long options with args are used
    # 3. group_name_formatter is disabled
    # 4. colors are disabled
    # 5. no markup/emoji codes are used
    # 6. trailing whitespace is ignored
    parser = argparse.ArgumentParser(prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument("file", default="-", help="A file (default: %(default)s).")

    # all types of empty groups
    parser.add_argument_group("empty group name", description="empty_group description")
    parser.add_argument_group("no description empty group name")
    parser.add_argument_group("", description="empty_name_empty_group description")
    parser.add_argument_group(description="no_name_empty_group description")

    # all types of non-empty groups
    group = parser.add_argument_group("group name", description="group description")
    group.add_argument("arg", help="help inside group")
    no_desc_group = parser.add_argument_group("no description group name")
    no_desc_group.add_argument("arg", help="agr help inside no_desc_group")
    empty_name_group = parser.add_argument_group("", description="empty_name_group description")
    empty_name_group.add_argument("arg", help="arg help inside empty_name_group")
    no_name_group = parser.add_argument_group(description="no_name_group description")
    no_name_group.add_argument("arg", help="arg help inside no_name_group")
    no_name_no_desc_group = parser.add_argument_group()
    no_name_no_desc_group.add_argument("arg", help="arg help inside no_name_no_desc_group")

    orig_out = get_help_output(parser, cmd=["--help"])
    parser.formatter_class = RichHelpFormatter
    with patch.object(RichHelpFormatter, "group_name_formatter", str):
        rich_out = get_help_output(parser, cmd=["--help"])
    rich_out_no_trailing_ws = "\n".join(line.rstrip(" ") for line in rich_out.split("\n"))
    assert rich_out_no_trailing_ws == orig_out


def test_padding_and_wrapping():
    # padding of group descritpion works as expected even when wrapped
    # wrapping of options work as expected
    parser = argparse.ArgumentParser(
        "PROG", description="-" * 120, epilog="%" * 120, formatter_class=RichHelpFormatter
    )
    parser.add_argument("-o", "--very-long-option-name", metavar="LONG_METAVAR", help="." * 120)
    group_with_description = parser.add_argument_group("group", description="*" * 120)
    group_with_description.add_argument("pos-arg", help="#" * 120)

    expected_help_output = f"""\
    usage: PROG [-h] [-o LONG_METAVAR] pos-arg

    --------------------------------------------------------------------------------------------------
    ----------------------

    {OPTIONS_GROUP_NAME}:
      -h, --help                           show this help message and exit
      -o, --very-long-option-name          ...........................................................
    LONG_METAVAR                           ...........................................................
                                           ..

    GROUP:
      ************************************************************************************************
      ************************

      pos-arg                              ###########################################################
                                           ###########################################################
                                           ##

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)


@pytest.mark.parametrize("title", (None, "available commands"), ids=("no_title", "title"))
@pytest.mark.parametrize("description", (None, "subparsers description"), ids=("no_desc", "desc"))
@pytest.mark.parametrize("dest", (None, "command"), ids=("no_dest", "dest"))
@pytest.mark.parametrize("metavar", (None, "<command>"), ids=("no_mv", "mv"))
@pytest.mark.parametrize("help", (None, "The subcommand to execute"), ids=("no_help", "help"))
@pytest.mark.parametrize("required", (False, True), ids=("opt", "req"))
def test_subparsers(title, description, dest, metavar, help, required):
    subparsers_kwargs = {
        "title": title,
        "description": description,
        "dest": dest,
        "metavar": metavar,
        "help": help,
        "required": required,
    }
    subparsers_kwargs = {k: v for k, v in subparsers_kwargs.items() if v is not None}

    def create_parsers_and_generate_help(formatter_class):
        parser = argparse.ArgumentParser(formatter_class=formatter_class)
        subparsers = parser.add_subparsers(**subparsers_kwargs)
        subparsers.add_parser("help", formatter_class=formatter_class, help="help subcommand.")
        base_out = get_help_output(parser, cmd=["--help"])  # base parser
        help_cmd_out = get_help_output(parser, cmd=["help", "--help"])  # help command subparser
        return base_out, help_cmd_out

    orig_base_out, orig_help_cmd_out = create_parsers_and_generate_help(argparse.HelpFormatter)
    with patch.object(RichHelpFormatter, "group_name_formatter", str):
        rich_base_out, rich_help_cmd_out = create_parsers_and_generate_help(RichHelpFormatter)

    # strip trailing whitespace from rich outputs
    rich_base_out = "\n".join(line.rstrip(" ") for line in rich_base_out.split("\n"))
    rich_help_cmd_out = "\n".join(line.rstrip(" ") for line in rich_help_cmd_out.split("\n"))
    assert rich_base_out == orig_base_out
    assert rich_help_cmd_out == orig_help_cmd_out


def test_escape_params():
    # params such as %(prog)s and %(default)s must be escaped when substituted
    parser = argparse.ArgumentParser(
        "[underline]",
        description="%(prog)s description.",
        epilog="%(prog)s epilog.",
        formatter_class=RichHelpFormatter,
    )

    class SpecialType(str):
        ...

    SpecialType.__name__ = "[link]"

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("pos-arg", metavar="[italic]", help="help of pos arg with special metavar")
    parser.add_argument(
        "--default", default="[default]", help="help with special default: %(default)s"
    )
    parser.add_argument("--type", type=SpecialType, help="help with special type: %(type)s")
    parser.add_argument(
        "--metavar", metavar="[bold]", help="help with special metavar: %(metavar)s"
    )

    expected_help_output = f"""\
    usage: [underline] [-h] [--version] [--default DEFAULT] [--type TYPE] [--metavar [bold]] [italic]

    [underline] description.

    POSITIONAL ARGUMENTS:
      [italic]           help of pos arg with special metavar

    {OPTIONS_GROUP_NAME}:
      -h, --help         show this help message and exit
      --version          show program's version number and exit
      --default DEFAULT  help with special default: [default]
      --type TYPE        help with special type: [link]
      --metavar [bold]   help with special metavar: [bold]

    [underline] epilog.
    """
    expected_version_output = "[underline] 1.0.0\n"
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


def test_no_help():
    formatter = RichHelpFormatter("prog")
    formatter.add_usage(usage=argparse.SUPPRESS, actions=[], groups=[])
    out = formatter.format_help()
    assert not out
