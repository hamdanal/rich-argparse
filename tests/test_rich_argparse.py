from __future__ import annotations

import argparse
import io
import os
import string
import sys
from contextlib import nullcontext
from textwrap import dedent
from unittest.mock import patch

import pytest
from rich import get_console
from rich.text import Text

from rich_argparse import (
    ArgumentDefaultsRichHelpFormatter,
    MetavarTypeRichHelpFormatter,
    RawDescriptionRichHelpFormatter,
    RawTextRichHelpFormatter,
    RichHelpFormatter,
)

# helpers
# =======
OPTIONS_GROUP_NAME = "Options" if sys.version_info >= (3, 10) else "Optional Arguments"


def get_cmd_output(parser: argparse.ArgumentParser, cmd: list[str]) -> str:
    __tracebackhide__ = True
    stdout = io.StringIO()
    with pytest.raises(SystemExit), patch.object(sys, "stdout", stdout):
        parser.parse_args(cmd)
    return stdout.getvalue()


# fixtures
# ========
@pytest.fixture(scope="session", autouse=True)
def set_terminal_properties():
    with patch.dict(os.environ, {"COLUMNS": "100", "TERM": "xterm-256color"}):
        yield


@pytest.fixture(scope="session", autouse=True)
def turnoff_legacy_windows():
    with patch("rich.console.detect_legacy_windows", return_value=False):
        yield


@pytest.fixture()
def force_color():
    with patch("rich.console.Console.is_terminal", return_value=True):
        yield


@pytest.fixture()
def disable_group_name_formatter():
    with patch.object(RichHelpFormatter, "group_name_formatter", str):
        yield


# tests
# =====
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
    Usage: awesome_program [-h] [--version] [--option OPTION]

    This is the awesome_program program.

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --version        show program's version number and exit
      --option OPTION  help of option (default: value)

    The epilog of awesome_program.
    """
    assert parser.format_help() == dedent(expected_help_output)
    assert get_cmd_output(parser, cmd=["--version"]) == "awesome_program 1.0.0\n"


@pytest.mark.parametrize("prog", (None, "PROG"), ids=("no_prog", "prog"))
@pytest.mark.parametrize("usage", (None, "USAGE"), ids=("no_usage", "usage"))
@pytest.mark.parametrize("description", (None, "A description."), ids=("no_desc", "desc"))
@pytest.mark.parametrize("epilog", (None, "An epilog."), ids=("no_epilog", "epilog"))
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_overall_structure(prog, usage, description, epilog):
    # The output must be consistent with the original HelpFormatter in these cases:
    # 1. no markup/emoji codes are used
    # 2. no short and long options with args are used
    # 3. group_name_formatter is disabled
    # 4. colors are disabled
    parser = argparse.ArgumentParser(prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument("file", default="-", help="A file (default: %(default)s).")
    parser.add_argument("spaces", help="Arg   with  weird\n\n whitespaces\t\t.")
    parser.add_argument("--very-very-very-very-very-very-very-very-long-option-name", help="help!")

    # all types of empty groups
    parser.add_argument_group("empty group name", description="empty_group description")
    parser.add_argument_group("no description empty group name")
    parser.add_argument_group("", description="empty_name_empty_group description")
    parser.add_argument_group(description="no_name_empty_group description")
    parser.add_argument_group("spaces group", description=" \tspaces_group description  ")

    # all types of non-empty groups
    group = parser.add_argument_group("group name", description="group description")
    group.add_argument("arg", help="help inside group")
    no_desc_group = parser.add_argument_group("no description group name")
    no_desc_group.add_argument("arg", help="arg help inside no_desc_group")
    empty_name_group = parser.add_argument_group("", description="empty_name_group description")
    empty_name_group.add_argument("arg", help="arg help inside empty_name_group")
    no_name_group = parser.add_argument_group(description="no_name_group description")
    no_name_group.add_argument("arg", help="arg help inside no_name_group")
    no_name_no_desc_group = parser.add_argument_group()
    no_name_no_desc_group.add_argument("arg", help="arg help inside no_name_no_desc_group")

    orig_out = parser.format_help()
    parser.formatter_class = RichHelpFormatter
    rich_out = parser.format_help()
    assert rich_out == orig_out


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_padding_and_wrapping():
    parser = argparse.ArgumentParser("PROG", description="-" * 120, epilog="%" * 120)
    parser.add_argument("--very-long-option-name", metavar="LONG_METAVAR", help="." * 120)
    group_with_description = parser.add_argument_group("group", description="*" * 120)
    group_with_description.add_argument("pos-arg", help="#" * 120)

    expected_help_output = f"""\
    usage: PROG [-h] [--very-long-option-name LONG_METAVAR] pos-arg

    --------------------------------------------------------------------------------------------------
    ----------------------

    {OPTIONS_GROUP_NAME.lower()}:
      -h, --help            show this help message and exit
      --very-long-option-name LONG_METAVAR
                            ..........................................................................
                            ..............................................

    group:
      **********************************************************************************************
      **************************

      pos-arg               ##########################################################################
                            ##############################################

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%
    """
    orig_output = parser.format_help()
    parser.formatter_class = RichHelpFormatter
    rich_output = parser.format_help()
    assert rich_output == orig_output
    assert rich_output == dedent(expected_help_output)


@pytest.mark.xfail(reason="rich wraps differently")
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_wrapping_compatible():
    # needs fixing rich wrapping to be compatible with textwrap.wrap
    parser = argparse.ArgumentParser("PROG", description="some text " + "-" * 120)
    orig_output = parser.format_help()
    parser.formatter_class = RichHelpFormatter
    rich_output = parser.format_help()
    assert rich_output == orig_output


@pytest.mark.parametrize("title", (None, "available commands"), ids=("no_title", "title"))
@pytest.mark.parametrize("description", (None, "subparsers description"), ids=("no_desc", "desc"))
@pytest.mark.parametrize("dest", (None, "command"), ids=("no_dest", "dest"))
@pytest.mark.parametrize("metavar", (None, "<command>"), ids=("no_mv", "mv"))
@pytest.mark.parametrize("help", (None, "The subcommand to execute"), ids=("no_help", "help"))
@pytest.mark.parametrize("required", (False, True), ids=("opt", "req"))
@pytest.mark.usefixtures("disable_group_name_formatter")
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

    def create_parsers(fmt_cls):
        p = argparse.ArgumentParser(formatter_class=fmt_cls)
        # `add_subparsers` must be called with `formatter_class` already set to trigger
        # argparse's call to get `prog` with the formatter under test
        subparsers = p.add_subparsers(**subparsers_kwargs)
        sp = subparsers.add_parser("help", help="help subcommand.", formatter_class=fmt_cls)
        return p, sp

    orig_parser, orig_subparser = create_parsers(fmt_cls=argparse.HelpFormatter)
    rich_parser, rich_subparser = create_parsers(fmt_cls=RichHelpFormatter)

    assert rich_parser.format_help() == orig_parser.format_help()
    assert rich_subparser.format_help() == orig_subparser.format_help()


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
    parser.add_argument(
        "--float", type=float, default=1.5, help="help with float conversion: %(default).5f"
    )
    parser.add_argument("--repr", type=str, help="help with repr conversion: %(type)r")

    expected_help_output = f"""\
    Usage: [underline] [-h] [--version] [--default DEFAULT] [--type TYPE] [--metavar [bold]]
                       [--float FLOAT] [--repr REPR]
                       [italic]

    [underline] description.

    Positional Arguments:
      [italic]           help of pos arg with special metavar

    {OPTIONS_GROUP_NAME}:
      -h, --help         show this help message and exit
      --version          show program's version number and exit
      --default DEFAULT  help with special default: [default]
      --type TYPE        help with special type: [link]
      --metavar [bold]   help with special metavar: [bold]
      --float FLOAT      help with float conversion: 1.50000
      --repr REPR        help with repr conversion: 'str'

    [underline] epilog.
    """
    assert parser.format_help() == dedent(expected_help_output)
    assert get_cmd_output(parser, cmd=["--version"]) == "[underline] 1.0.0\n"


@pytest.mark.usefixtures("force_color")
def test_generated_usage():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("hidden", help=argparse.SUPPRESS)
    parser.add_argument("--weird", metavar="y)")
    hidden_group = parser.add_mutually_exclusive_group()
    hidden_group.add_argument("--hidden-group-arg1", help=argparse.SUPPRESS)
    hidden_group.add_argument("--hidden-group-arg2", help=argparse.SUPPRESS)
    parser.add_argument("--required", metavar="REQ", required=True)
    mut_ex = parser.add_mutually_exclusive_group()
    mut_ex.add_argument("--flag", action="store_true", help="Is flag?")
    mut_ex.add_argument("--not-flag", action="store_true", help="Is not flag?")
    req_mut_ex = parser.add_mutually_exclusive_group(required=True)
    req_mut_ex.add_argument("-y", help="Yes.")
    req_mut_ex.add_argument("-n", help="No.")

    usage_text = (
        "\x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] "
        "[\x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m]  "
        "\x1b[36m--required\x1b[0m \x1b[38;5;36mREQ\x1b[0m "
        "[\x1b[36m--flag\x1b[0m | \x1b[36m--not-flag\x1b[0m] "
        "(\x1b[36m-y\x1b[0m \x1b[38;5;36mY\x1b[0m | \x1b[36m-n\x1b[0m \x1b[38;5;36mN\x1b[0m) "
        "\x1b[36mfile\x1b[0m"
    )

    expected_help_output = f"""\
    \x1b[38;5;208mUsage:\x1b[0m {usage_text}

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36mfile\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m      \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m
      \x1b[36m--required\x1b[0m \x1b[38;5;36mREQ\x1b[0m
      \x1b[36m--flag\x1b[0m          \x1b[39mIs flag?\x1b[0m
      \x1b[36m--not-flag\x1b[0m      \x1b[39mIs not flag?\x1b[0m
      \x1b[36m-y\x1b[0m \x1b[38;5;36mY\x1b[0m            \x1b[39mYes.\x1b[0m
      \x1b[36m-n\x1b[0m \x1b[38;5;36mN\x1b[0m            \x1b[39mNo.\x1b[0m
    """
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.parametrize(
    ("usage", "expected", "usage_markup"),
    (
        pytest.param(
            "%(prog)s [bold] PROG_CMD[/]",
            "\x1b[38;5;244mPROG\x1b[0m [bold] PROG_CMD[/]",
            None,
            id="default",
        ),
        pytest.param(
            "%(prog)s [bold] PROG_CMD[/]",
            "\x1b[38;5;244mPROG\x1b[0m [bold] PROG_CMD[/]",
            False,
            id="no_markup",
        ),
        pytest.param(
            "%(prog)s [bold] PROG_CMD[/]",
            "\x1b[38;5;244mPROG\x1b[0m \x1b[1m PROG_CMD\x1b[0m",
            True,
            id="markup",
        ),
        pytest.param(
            "PROG %(prog)s [bold] %(prog)s [/]\n%(prog)r",
            (
                "PROG "
                "\x1b[38;5;244mPROG\x1b[0m "
                "\x1b[1m \x1b[0m\x1b[1;38;5;244mPROG\x1b[0m\x1b[1m \x1b[0m"
                "\n\x1b[38;5;244m'PROG'\x1b[0m"
            ),
            True,
            id="prog_prog",
        ),
    ),
)
@pytest.mark.usefixtures("force_color")
def test_user_usage(usage, expected, usage_markup):
    parser = argparse.ArgumentParser(prog="PROG", usage=usage, formatter_class=RichHelpFormatter)
    if usage_markup is not None:
        ctx = patch.object(RichHelpFormatter, "usage_markup", usage_markup)
    else:
        ctx = nullcontext()
    with ctx:
        assert parser.format_usage() == f"\x1b[38;5;208mUsage:\x1b[0m {expected}\n"


@pytest.mark.usefixtures("force_color")
def test_actions_spans_in_usage():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("arg", nargs="*")
    mut_ex = parser.add_mutually_exclusive_group()
    mut_ex.add_argument("--opt", nargs="?")
    mut_ex.add_argument("--opts", nargs="+")

    # https://github.com/python/cpython/issues/82619
    if sys.version_info < (3, 9):  # pragma: <3.9 cover
        arg_metavar = "[arg [arg ...]]"
    else:  # pragma: >=3.9 cover
        arg_metavar = "[arg ...]"

    usage_text = (
        f"\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] "
        f"[\x1b[36m--opt\x1b[0m \x1b[38;5;36m[OPT]\x1b[0m | "
        f"\x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS [OPTS ...]\x1b[0m] "
        f"\x1b[36m{arg_metavar}\x1b[0m"
    )
    expected_help_output = f"""\
    {usage_text}

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36marg\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m            \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--opt\x1b[0m \x1b[38;5;36m[OPT]\x1b[0m
      \x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS [OPTS ...]\x1b[0m
    """
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="not available in 3.8")
@pytest.mark.usefixtures("force_color")
def test_boolean_optional_action_spans():  # pragma: >=3.9 cover
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("--bool", action=argparse.BooleanOptionalAction)
    expected_help_output = f"""\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--bool\x1b[0m | \x1b[36m--no-bool\x1b[0m]

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m         \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--bool\x1b[0m, \x1b[36m--no-bool\x1b[0m
    """
    assert parser.format_help() == dedent(expected_help_output)


def test_usage_spans_errors():
    parser = argparse.ArgumentParser()
    parser._optionals.required = False
    actions = parser._actions
    groups = [parser._optionals]

    formatter = RichHelpFormatter("PROG")
    with patch.object(RichHelpFormatter, "_rich_usage_spans", side_effect=ValueError):
        formatter.add_usage(usage=None, actions=actions, groups=groups, prefix=None)
    (usage,) = formatter._root_section.rich_items
    assert isinstance(usage, Text)
    assert str(usage).rstrip() == "Usage: PROG [-h]"
    prefix_span, prog_span = usage.spans
    assert prefix_span.start == 0
    assert prefix_span.end == len("usage:")
    assert prefix_span.style == "argparse.groups"
    assert prog_span.start == len("usage: ")
    assert prog_span.end == len("usage: PROG")
    assert prog_span.style == "argparse.prog"


def test_no_help():
    formatter = RichHelpFormatter("prog")
    formatter.add_usage(usage=argparse.SUPPRESS, actions=[], groups=[])
    out = formatter.format_help()
    assert not formatter._root_section.rich_items
    assert not out


def test_raw_description_rich_help_formatter():
    long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 3)
    parser = argparse.ArgumentParser(
        "PROG",
        formatter_class=RawDescriptionRichHelpFormatter,
        description=long_text,
        epilog=long_text,
    )
    group = parser.add_argument_group("group", description=long_text)
    group.add_argument("--long", help=long_text)

    expected_help_output = f"""\
    Usage: PROG [-h] [--long LONG]

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    {OPTIONS_GROUP_NAME}:
      -h, --help   show this help message and exit

    Group:
      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

      --long LONG  The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the
                   lazy dog. The quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.
    """
    assert parser.format_help() == dedent(expected_help_output)


def test_raw_text_rich_help_formatter():
    long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 3)
    parser = argparse.ArgumentParser(
        "PROG", formatter_class=RawTextRichHelpFormatter, description=long_text, epilog=long_text
    )
    group = parser.add_argument_group("group", description=long_text)
    group.add_argument("--long", help=long_text)

    expected_help_output = f"""\
    Usage: PROG [-h] [--long LONG]

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    {OPTIONS_GROUP_NAME}:
      -h, --help   show this help message and exit

    Group:
      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

      --long LONG  The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.
    """
    assert parser.format_help() == dedent(expected_help_output)


def test_argument_default_rich_help_formatter():
    parser = argparse.ArgumentParser("PROG", formatter_class=ArgumentDefaultsRichHelpFormatter)
    parser.add_argument("--option", default="def", help="help of option")

    expected_help_output = f"""\
    Usage: PROG [-h] [--option OPTION]

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --option OPTION  help of option (default: def)
    """
    assert parser.format_help() == dedent(expected_help_output)


def test_metavar_type_help_formatter():
    parser = argparse.ArgumentParser("PROG", formatter_class=MetavarTypeRichHelpFormatter)
    parser.add_argument("--count", type=int, default=0, help="how many?")

    expected_help_output = f"""\
    Usage: PROG [-h] [--count int]

    {OPTIONS_GROUP_NAME}:
      -h, --help   show this help message and exit
      --count int  how many?
    """
    assert parser.format_help() == dedent(expected_help_output)


def test_django_rich_help_formatter():
    # https://github.com/django/django/blob/8eed30aec6/django/core/management/base.py#L105-L131
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

    class DjangoRichHelpFormatter(DjangoHelpFormatter, RichHelpFormatter):
        """Rich help message formatter with django's special ordering of arguments."""

    parser = argparse.ArgumentParser("command", formatter_class=DjangoRichHelpFormatter)
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("--traceback", action="store_true", help="show traceback")
    parser.add_argument("my-arg", help="custom argument.")
    parser.add_argument("--my-option", action="store_true", help="custom option")
    parser.add_argument("--verbosity", action="count", help="verbosity level")
    parser.add_argument("-a", "--an-option", action="store_true", help="another custom option")

    expected_help_output = f"""\
    Usage: command [-h] [--my-option] [-a] [--version] [--traceback] [--verbosity] my-arg

    Positional Arguments:
      my-arg           custom argument.

    {OPTIONS_GROUP_NAME}:
      -h, --help       show this help message and exit
      --my-option      custom option
      -a, --an-option  another custom option
      --version        show program's version number and exit
      --traceback      show traceback
      --verbosity      verbosity level
    """
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.parametrize("indent_increment", (1, 3))
@pytest.mark.parametrize("max_help_position", (25, 26, 27))
@pytest.mark.parametrize("width", (None, 70))
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_help_formatter_args(indent_increment, max_help_position, width):
    # Note: the length of the option string is chosen to test edge cases where it is less than,
    # equal to, and bigger than max_help_position
    option = "option-of-certain-length"
    help_text = "This is the help of the said option"
    orig_parser = argparse.ArgumentParser(
        "program",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, indent_increment, max_help_position, width
        ),
    )
    orig_parser.add_argument(option, help=help_text)
    rich_parser = argparse.ArgumentParser(
        "program",
        formatter_class=lambda prog: RichHelpFormatter(
            prog, indent_increment, max_help_position, width
        ),
    )
    rich_parser.add_argument(option, help=help_text)

    assert rich_parser.format_help() == orig_parser.format_help()


def test_return_output():
    parser = argparse.ArgumentParser("prog", formatter_class=RichHelpFormatter)
    assert parser.format_help()


@pytest.mark.usefixtures("force_color")
def test_text_highlighter():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("arg", help="Did you try `RichHelpFormatter.highlighter`?")

    expected_help_output = f"""\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] \x1b[36marg\x1b[0m

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36marg\x1b[0m         \x1b[39mDid you try `\x1b[0m\x1b[1;39mRichHelpFormatter.highlighter\x1b[0m\x1b[39m`?\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
    """

    # Make sure we can use a style multiple times in regexes
    pattern_with_duplicate_style = r"'(?P<syntax>[^']*)'"
    RichHelpFormatter.highlights.append(pattern_with_duplicate_style)
    assert parser.format_help() == dedent(expected_help_output)
    RichHelpFormatter.highlights.remove(pattern_with_duplicate_style)


@pytest.mark.usefixtures("force_color")
def test_default_highlights():
    parser = argparse.ArgumentParser(
        "PROG",
        formatter_class=RichHelpFormatter,
        description="Descritpion with `syntax` and --options.",
        epilog="Epilog with `syntax` and --options.",
    )
    # syntax highlights
    parser.add_argument("--syntax-normal", action="store_true", help="Start `middle` end")
    parser.add_argument("--syntax-start", action="store_true", help="`Start` middle end")
    parser.add_argument("--syntax-end", action="store_true", help="Start middle `end`")
    # options highlights
    parser.add_argument("--option-normal", action="store_true", help="Start --middle end")
    parser.add_argument("--option-start", action="store_true", help="--Start middle end")
    parser.add_argument("--option-end", action="store_true", help="Start middle --end")
    parser.add_argument("--option-comma", action="store_true", help="Start --middle, end")
    parser.add_argument("--option-multi", action="store_true", help="Start --middle-word end")
    parser.add_argument("--option-not", action="store_true", help="Start middle-word end")
    parser.add_argument("--option-short", action="store_true", help="Start -middle end")

    expected_help_output = f"""
    \x1b[39mDescritpion with `\x1b[0m\x1b[1;39msyntax\x1b[0m\x1b[39m` and \x1b[0m\x1b[36m--options\x1b[0m\x1b[39m.\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m       \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--syntax-normal\x1b[0m  \x1b[39mStart `\x1b[0m\x1b[1;39mmiddle\x1b[0m\x1b[39m` end\x1b[0m
      \x1b[36m--syntax-start\x1b[0m   \x1b[39m`\x1b[0m\x1b[1;39mStart\x1b[0m\x1b[39m` middle end\x1b[0m
      \x1b[36m--syntax-end\x1b[0m     \x1b[39mStart middle `\x1b[0m\x1b[1;39mend\x1b[0m\x1b[39m`\x1b[0m
      \x1b[36m--option-normal\x1b[0m  \x1b[39mStart \x1b[0m\x1b[36m--middle\x1b[0m\x1b[39m end\x1b[0m
      \x1b[36m--option-start\x1b[0m   \x1b[36m--Start\x1b[0m\x1b[39m middle end\x1b[0m
      \x1b[36m--option-end\x1b[0m     \x1b[39mStart middle \x1b[0m\x1b[36m--end\x1b[0m
      \x1b[36m--option-comma\x1b[0m   \x1b[39mStart \x1b[0m\x1b[36m--middle\x1b[0m\x1b[39m, end\x1b[0m
      \x1b[36m--option-multi\x1b[0m   \x1b[39mStart \x1b[0m\x1b[36m--middle-word\x1b[0m\x1b[39m end\x1b[0m
      \x1b[36m--option-not\x1b[0m     \x1b[39mStart middle-word end\x1b[0m
      \x1b[36m--option-short\x1b[0m   \x1b[39mStart \x1b[0m\x1b[36m-middle\x1b[0m\x1b[39m end\x1b[0m

    \x1b[39mEpilog with `\x1b[0m\x1b[1;39msyntax\x1b[0m\x1b[39m` and \x1b[0m\x1b[36m--options\x1b[0m\x1b[39m.\x1b[0m
    """
    assert parser.format_help().endswith(dedent(expected_help_output))


@pytest.mark.usefixtures("force_color")
def test_subparsers_usage():
    # Parent uses RichHelpFormatter
    rich_parent = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    rich_subparsers = rich_parent.add_subparsers()
    rich_child1 = rich_subparsers.add_parser("sp1", formatter_class=RichHelpFormatter)
    rich_child2 = rich_subparsers.add_parser("sp2")
    assert rich_parent.format_usage() == (
        "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] "
        "\x1b[36m{sp1,sp2} ...\x1b[0m\n"
    )
    assert rich_child1.format_usage() == (
        "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG sp1\x1b[0m [\x1b[36m-h\x1b[0m]\n"
    )
    assert rich_child2.format_usage() == "usage: PROG sp2 [-h]\n"

    # Parent uses original formatter
    orig_parent = argparse.ArgumentParser("PROG")
    orig_subparsers = orig_parent.add_subparsers()
    orig_child1 = orig_subparsers.add_parser("sp1", formatter_class=RichHelpFormatter)
    orig_child2 = orig_subparsers.add_parser("sp2")
    assert orig_parent.format_usage() == ("usage: PROG [-h] {sp1,sp2} ...\n")
    assert orig_child1.format_usage() == (
        "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG sp1\x1b[0m [\x1b[36m-h\x1b[0m]\n"
    )
    assert orig_child2.format_usage() == "usage: PROG sp2 [-h]\n"


@pytest.mark.parametrize("ct", string.printable)
def test_expand_help_format_specifier(ct):
    prog = 1 if ct in "cdeEfFgGiouxX*" else "PROG"
    help_formatter = RichHelpFormatter(prog=prog)
    action = argparse.Action(["-t"], dest="test", help=f"%(prog){ct}")
    try:
        expected = help_formatter._expand_help(action)
    except ValueError as e:
        with pytest.raises(ValueError) as exc_info:
            help_formatter._rich_expand_help(action)
        assert exc_info.value.args == e.args
    else:
        assert help_formatter._rich_expand_help(action).plain == expected


def test_rich_lazy_import():
    sys_modules_no_rich = {
        mod_name: mod
        for mod_name, mod in sys.modules.items()
        if mod_name != "rich" and not mod_name.startswith("rich.")
    }
    with patch.dict(sys.modules, sys_modules_no_rich, clear=True):
        parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)
        parser.add_argument("--foo", help="foo help")
        args = parser.parse_args(["--foo", "bar"])
        assert args.foo == "bar"
        assert sys.modules
        assert "rich" not in sys.modules  # no help formatting, do not import rich
        for mod_name in sys.modules:
            assert not mod_name.startswith("rich.")
        parser.format_help()
        assert "rich" in sys.modules  # format help has been called
        formatter = RichHelpFormatter("PROG")
        assert formatter._console is None
        formatter.console = get_console()
        assert formatter._console is not None
