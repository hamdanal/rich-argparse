from __future__ import annotations

import argparse
import sys
from unittest.mock import patch

import pytest
from rich.text import Text

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
    USAGE: awesome_program [-h] [--version] [--option OPTION]

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
    USAGE: PROG [-h] [-o LONG_METAVAR] pos-arg

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
    USAGE: [underline] [-h] [--version] [--default DEFAULT] [--type TYPE] [--metavar [bold]] [italic]

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


@pytest.mark.parametrize(
    ("usage", "usage_text"),
    (
        pytest.param(
            None,
            "\x1b[38;5;208mUSAGE:\x1b[0m PROG [\x1b[36m-h\x1b[0m] "
            "[\x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m] [\x1b[36m--flag\x1b[0m "
            "| \x1b[36m--not-flag\x1b[0m] (\x1b[36m--path\x1b[0m \x1b[38;5;36mPATH\x1b[0m "
            "| \x1b[36m--url\x1b[0m \x1b[38;5;36mURL\x1b[0m)  \x1b[36mfile\x1b[0m",
            id="auto_usage",
        ),
        pytest.param(
            "%(prog)s [-h] [--flag | --not-flag] (--path PATH | --url URL]) file",
            "\x1b[38;5;208mUSAGE:\x1b[0m PROG [-h] [--flag | --not-flag] (--path PATH | --url URL]) file",
            id="user_usage",
        ),
    ),
)
def test_spans(usage, usage_text):
    parser = argparse.ArgumentParser("PROG", usage=usage, formatter_class=RichHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("hidden", help=argparse.SUPPRESS)
    parser.add_argument("--weird", metavar="y)")
    mut_ex = parser.add_mutually_exclusive_group()
    mut_ex.add_argument("--flag", action="store_true", help="Is flag?")
    mut_ex.add_argument("--not-flag", action="store_true", help="Is not flag?")
    req_mut_ex = parser.add_mutually_exclusive_group(required=True)
    req_mut_ex.add_argument("--path", help="Option path.")
    req_mut_ex.add_argument("--url", help="Option url.")
    hidden_group = parser.add_mutually_exclusive_group()
    hidden_group.add_argument("--hidden-group-arg1", help=argparse.SUPPRESS)
    hidden_group.add_argument("--hidden-group-arg2", help=argparse.SUPPRESS)

    expected_help_output = f"""\
    {usage_text}

    \x1b[38;5;208mPOSITIONAL ARGUMENTS:\x1b[0m
      \x1b[36mfile\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m   \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m
      \x1b[36m--flag\x1b[0m       \x1b[39mIs flag?\x1b[0m
      \x1b[36m--not-flag\x1b[0m   \x1b[39mIs not flag?\x1b[0m
      \x1b[36m--path\x1b[0m \x1b[38;5;36mPATH\x1b[0m  \x1b[39mOption path.\x1b[0m
      \x1b[36m--url\x1b[0m \x1b[38;5;36mURL\x1b[0m    \x1b[39mOption url.\x1b[0m
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output, with_ansi=True)


def test_actions_spans_in_usage():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("arg", nargs="*")
    mut_ex = parser.add_mutually_exclusive_group()
    mut_ex.add_argument("--opt", nargs="?")
    mut_ex.add_argument("--opts", nargs="+")

    # https://github.com/python/cpython/issues/82619
    if sys.version_info < (3, 9):
        arg_metavar = "[arg [arg ...]]"
    else:
        arg_metavar = "[arg ...]"

    usage_text = (
        f"\x1b[38;5;208mUSAGE:\x1b[0m PROG [\x1b[36m-h\x1b[0m] [\x1b[36m--opt\x1b[0m \x1b[38;5;36m"
        f"[OPT]\x1b[0m | \x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS [OPTS ...]\x1b[0m] "
        f"\x1b[36m{arg_metavar}\x1b[0m"
    )
    expected_help_output = f"""\
    {usage_text}

    \x1b[38;5;208mPOSITIONAL ARGUMENTS:\x1b[0m
      \x1b[36marg\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m              \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--opt\x1b[0m \x1b[38;5;36m[OPT]\x1b[0m
      \x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS [OPTS ...]\x1b[0m
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output, with_ansi=True)


def test_usage_spans_errors():
    parser = argparse.ArgumentParser()
    parser._optionals.required = False
    actions = parser._actions
    groups = [parser._optionals]

    formatter = RichHelpFormatter("PROG")
    with pytest.raises(
        ValueError, match=r"usage error: encountered extraneous '\]' at pos 2: '\]'"
    ):
        list(formatter._usage_spans("xx]", start=0, actions=actions, groups=groups))

    with pytest.raises(
        ValueError, match=r"usage error: expecting '\]' to match '\[' starting at: '\[xx'"
    ):
        list(formatter._usage_spans("[xx", start=0, actions=actions, groups=groups))

    with patch.object(RichHelpFormatter, "_usage_spans", side_effect=ValueError):
        formatter.add_usage(usage=None, actions=actions, groups=groups, prefix=None)
    (usage,) = formatter.renderables
    assert isinstance(usage, Text)
    assert str(usage) == "USAGE: PROG [-h]"
    (prefix_span,) = usage.spans
    assert prefix_span.start == 0
    assert prefix_span.end == len("usage:")
    assert prefix_span.style == "argparse.groups"


def test_no_help():
    formatter = RichHelpFormatter("prog")
    formatter.add_usage(usage=argparse.SUPPRESS, actions=[], groups=[])
    out = formatter.format_help()
    assert not formatter.renderables
    assert not out


def test_with_argument_default_help_formatter():
    class Fmt(RichHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
        ...

    parser = argparse.ArgumentParser("PROG", formatter_class=Fmt)
    parser.add_argument("--option", default="def", help="help of option")

    expected_help_output = f"""\
    USAGE: PROG [-h] [--option OPTION]

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --option OPTION  help of option (default: def)
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)


def test_with_metavar_type_help_formatter():
    class Fmt(RichHelpFormatter, argparse.MetavarTypeHelpFormatter):
        ...

    parser = argparse.ArgumentParser("PROG", formatter_class=Fmt)
    parser.add_argument("--count", type=int, default=0, help="how many?")

    expected_help_output = f"""\
    USAGE: PROG [-h] [--count int]

    {OPTIONS_GROUP_NAME}:
      -h, --help   show this help message and exit
      --count int  how many?
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)


def test_with_django_help_formatter():
    # https://github.com/django/django/blob/8eed30aec606ff70eee920af84e880ea19da481b/django/core/management/base.py#L105-L131
    class DjangoHelpFormatter(argparse.HelpFormatter):
        """
        Customized formatter so that command-specific arguments appear in the
        --help output before arguments common to all commands.
        """

        show_last = {
            "--version",
            "--verbosity",
            "--traceback",
            "--settings",
            "--pythonpath",
            "--no-color",
            "--force-color",
            "--skip-checks",
        }

        def _reordered_actions(self, actions):
            return sorted(actions, key=lambda a: set(a.option_strings) & self.show_last != set())

        def add_usage(self, usage, actions, *args, **kwargs):
            super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

        def add_arguments(self, actions):
            super().add_arguments(self._reordered_actions(actions))

    class Fmt(DjangoHelpFormatter, RichHelpFormatter):
        ...

    parser = argparse.ArgumentParser("command", formatter_class=Fmt)
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("--traceback", action="store_true", help="show traceback")
    parser.add_argument("my-arg", help="custom argument.")
    parser.add_argument("--my-option", action="store_true", help="custom option")
    parser.add_argument("--verbosity", action="count", help="verbosity level")
    parser.add_argument("-a", "--an-option", action="store_true", help="another custom option")

    expected_help_output = f"""\
    USAGE: command [-h] [--my-option] [-a] [--version] [--traceback] [--verbosity] my-arg

    POSITIONAL ARGUMENTS:
      my-arg           custom argument.

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --my-option      custom option
      -a, --an-option  another custom option
      --version        show program's version number and exit
      --traceback      show traceback
      --verbosity      verbosity level
    """
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)
