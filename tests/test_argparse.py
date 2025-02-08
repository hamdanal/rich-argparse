from __future__ import annotations

import argparse
import re
import string
import sys
import textwrap
from argparse import (
    SUPPRESS,
    Action,
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    HelpFormatter,
    MetavarTypeHelpFormatter,
    RawDescriptionHelpFormatter,
    RawTextHelpFormatter,
)
from contextlib import nullcontext
from unittest.mock import Mock, patch

import pytest
from rich import get_console
from rich.console import Group
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

import rich_argparse._lazy_rich as r
from rich_argparse import (
    ArgumentDefaultsRichHelpFormatter,
    HelpPreviewAction,
    MetavarTypeRichHelpFormatter,
    RawDescriptionRichHelpFormatter,
    RawTextRichHelpFormatter,
    RichHelpFormatter,
)
from rich_argparse._common import _fix_legacy_win_text
from rich_argparse._patching import patch_default_formatter_class
from tests.helpers import ArgumentParsers, clean_argparse, get_cmd_output


def test_params_substitution():
    # in text (description, epilog, group description) and version: substitute %(prog)s
    # in help message: substitute %(param)s for all param in vars(action)
    parser = ArgumentParser(
        "awesome_program",
        description="This is the %(prog)s program.",
        epilog="The epilog of %(prog)s.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("--option", default="value", help="help of option (default: %(default)s)")

    expected_help_output = """\
    Usage: awesome_program [-h] [--version] [--option OPTION]

    This is the awesome_program program.

    Optional Arguments:
      -h, --help       show this help message and exit
      --version        show program's version number and exit
      --option OPTION  help of option (default: value)

    The epilog of awesome_program.
    """
    assert parser.format_help() == clean_argparse(expected_help_output)
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
    parsers = ArgumentParsers(
        HelpFormatter,
        RichHelpFormatter,
        prog=prog,
        usage=usage,
        description=description,
        epilog=epilog,
    )
    parsers.add_argument("file", default="-", help="A file (default: %(default)s).")
    parsers.add_argument("spaces", help="Arg   with  weird\n\n whitespaces\t\t.")
    parsers.add_argument("--very-very-very-very-very-very-very-very-long-option-name", help="help!")

    # all types of empty groups
    parsers.add_argument_group("empty group name", description="empty_group description")
    parsers.add_argument_group("no description empty group name")
    parsers.add_argument_group("", description="empty_name_empty_group description")
    parsers.add_argument_group(description="no_name_empty_group description")
    parsers.add_argument_group("spaces group", description=" \tspaces_group description  ")
    parsers.add_argument_group(SUPPRESS, description="suppressed_name_group description")
    parsers.add_argument_group(SUPPRESS, description=SUPPRESS)

    # all types of non-empty groups
    groups = parsers.add_argument_group("group name", description="group description")
    groups.add_argument("arg", help="help inside group")
    no_desc_groups = parsers.add_argument_group("no description group name")
    no_desc_groups.add_argument("arg", help="arg help inside no_desc_group")
    empty_name_groups = parsers.add_argument_group("", description="empty_name_group description")
    empty_name_groups.add_argument("arg", help="arg help inside empty_name_group")
    no_name_groups = parsers.add_argument_group(description="no_name_group description")
    no_name_groups.add_argument("arg", help="arg help inside no_name_group")
    no_name_no_desc_groups = parsers.add_argument_group()
    no_name_no_desc_groups.add_argument("arg", help="arg help inside no_name_no_desc_group")
    suppressed_name_groups = parsers.add_argument_group(
        SUPPRESS, description="suppressed_name_group description"
    )
    suppressed_name_groups.add_argument("arg", help="arg help inside suppressed_name_group")
    suppressed_name_desc_groups = parsers.add_argument_group(SUPPRESS, description=SUPPRESS)
    suppressed_name_desc_groups.add_argument(
        "arg", help="arg help inside suppressed_name_desc_group"
    )

    parsers.assert_format_help_equal()


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_padding_and_wrapping():
    parsers = ArgumentParsers(
        HelpFormatter, RichHelpFormatter, prog="PROG", description="-" * 120, epilog="%" * 120
    )
    parsers.add_argument("--very-long-option-name", metavar="LONG_METAVAR", help="." * 120)
    groups_with_description = parsers.add_argument_group("group", description="*" * 120)
    groups_with_description.add_argument("pos-arg", help="#" * 120)

    parsers.add_argument_group(
        "= =" * 40, description="group with a very long name that should not wrap"
    )

    expected_help_output = """\
    usage: PROG [-h] [--very-long-option-name LONG_METAVAR] pos-arg

    --------------------------------------------------------------------------------------------------
    ----------------------

    optional arguments:
      -h, --help            show this help message and exit
      --very-long-option-name LONG_METAVAR
                            ..........................................................................
                            ..............................................

    group:
      **********************************************************************************************
      **************************

      pos-arg               ##########################################################################
                            ##############################################

    = == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == =:
      group with a very long name that should not wrap

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))


@pytest.mark.xfail(reason="rich wraps differently")
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_wrapping_compatible():
    # needs fixing rich wrapping to be compatible with textwrap.wrap
    parsers = ArgumentParsers(
        HelpFormatter, RichHelpFormatter, prog="PROG", description="some text " + "-" * 120
    )
    parsers.assert_format_help_equal()


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

    parsers = ArgumentParsers(HelpFormatter, RichHelpFormatter)
    subparsers_actions = parsers.add_subparsers(**subparsers_kwargs)
    subparsers = subparsers_actions.add_parser("help", help="help subcommand.")
    parsers.assert_format_help_equal()
    subparsers.assert_format_help_equal()


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_escape_params():
    # params such as %(prog)s and %(default)s must be escaped when substituted
    parsers = ArgumentParsers(
        HelpFormatter,
        RichHelpFormatter,
        prog="[underline]",
        usage="%(prog)s [%%options] %% [args]\n%%%(prog)s %%(prog)s [%%%%options] %%%% [args]",
        description="%(prog)s description.",
        epilog="%(prog)s epilog.",
    )

    class SpecialType(str): ...

    SpecialType.__name__ = "[link]"

    parsers.add_argument("--version", action="version", version="%(prog)s %%1.0.0")
    parsers.add_argument("pos-arg", metavar="[italic]", help="help of pos arg with special metavar")
    parsers.add_argument(
        "--default", default="[default]", help="help with special default: %(default)s"
    )
    parsers.add_argument("--type", type=SpecialType, help="help with special type: %(type)s")
    parsers.add_argument(
        "--metavar", metavar="[bold]", help="help with special metavar: %(metavar)s"
    )
    parsers.add_argument(
        "--float", type=float, default=1.5, help="help with float conversion: %(default).5f"
    )
    parsers.add_argument("--repr", type=str, help="help with repr conversion: %(type)r")
    parsers.add_argument(
        "--percent", help="help with percent escaping: %%(prog)s %%%(prog)s %% %%%% %%%%prog"
    )

    expected_help_output = """\
    usage: [underline] [%options] % [args]
    %[underline] %(prog)s [%%options] %% [args]

    [underline] description.

    positional arguments:
      [italic]           help of pos arg with special metavar

    optional arguments:
      -h, --help         show this help message and exit
      --version          show program's version number and exit
      --default DEFAULT  help with special default: [default]
      --type TYPE        help with special type: [link]
      --metavar [bold]   help with special metavar: [bold]
      --float FLOAT      help with float conversion: 1.50000
      --repr REPR        help with repr conversion: 'str'
      --percent PERCENT  help with percent escaping: %(prog)s %[underline] % %% %%prog

    [underline] epilog.
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))
    parsers.assert_cmd_output_equal(cmd=["--version"], expected="[underline] %1.0.0\n")


@pytest.mark.usefixtures("force_color")
def test_generated_usage():
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("file")
    parser.add_argument("hidden", help=SUPPRESS)
    parser.add_argument("--weird", metavar="y)")
    hidden_group = parser.add_mutually_exclusive_group()
    hidden_group.add_argument("--hidden-group-arg1", help=SUPPRESS)
    hidden_group.add_argument("--hidden-group-arg2", help=SUPPRESS)
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
    if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
        usage_text = usage_text.replace("  ", " ")

    expected_help_output = f"""\
    \x1b[38;5;208mUsage:\x1b[0m {usage_text}

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36mfile\x1b[0m

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m      \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m
      \x1b[36m--required\x1b[0m \x1b[38;5;36mREQ\x1b[0m
      \x1b[36m--flag\x1b[0m          \x1b[39mIs flag?\x1b[0m
      \x1b[36m--not-flag\x1b[0m      \x1b[39mIs not flag?\x1b[0m
      \x1b[36m-y\x1b[0m \x1b[38;5;36mY\x1b[0m            \x1b[39mYes.\x1b[0m
      \x1b[36m-n\x1b[0m \x1b[38;5;36mN\x1b[0m            \x1b[39mNo.\x1b[0m
    """
    assert parser.format_help() == clean_argparse(expected_help_output)


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
                "\x1b[1m \x1b[0m\x1b[1;38;5;244mPROG\x1b[0m"  # "\x1b[1m \x1b[0m"
                "\n\x1b[38;5;244m'PROG'\x1b[0m"
            ),
            True,
            id="prog_prog",
        ),
    ),
)
@pytest.mark.usefixtures("force_color")
def test_user_usage(usage, expected, usage_markup):
    parser = ArgumentParser(prog="PROG", usage=usage, formatter_class=RichHelpFormatter)
    if usage_markup is not None:
        ctx = patch.object(RichHelpFormatter, "usage_markup", usage_markup)
    else:
        ctx = nullcontext()
    with ctx:
        assert parser.format_usage() == f"\x1b[38;5;208mUsage:\x1b[0m {expected}\n"


@pytest.mark.usefixtures("force_color")
def test_actions_spans_in_usage():
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("required")
    parser.add_argument("int", nargs=2)
    parser.add_argument("optional", nargs=argparse.OPTIONAL)
    parser.add_argument("zom", nargs=argparse.ZERO_OR_MORE)
    parser.add_argument("oom", nargs=argparse.ONE_OR_MORE)
    parser.add_argument("remainder", nargs=argparse.REMAINDER)
    parser.add_argument("parser", nargs=argparse.PARSER)
    parser.add_argument("suppress", nargs=argparse.SUPPRESS)
    mut_ex = parser.add_mutually_exclusive_group()
    mut_ex.add_argument("--opt", nargs="?")
    mut_ex.add_argument("--opts", nargs="+")

    # https://github.com/python/cpython/issues/82619
    if sys.version_info < (3, 9):  # pragma: <3.9 cover
        zom_metavar = "[\x1b[36mzom\x1b[0m [\x1b[36mzom\x1b[0m \x1b[36m...\x1b[0m]]"
    else:  # pragma: >=3.9 cover
        zom_metavar = "[\x1b[36mzom\x1b[0m \x1b[36m...\x1b[0m]"

    usage_text = (
        f"\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] "
        f"[\x1b[36m--opt\x1b[0m [\x1b[38;5;36mOPT\x1b[0m] | "
        f"\x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS\x1b[0m [\x1b[38;5;36mOPTS\x1b[0m \x1b[38;5;36m...\x1b[0m]]\n                "
        f"\x1b[36mrequired\x1b[0m \x1b[36mint\x1b[0m \x1b[36mint\x1b[0m [\x1b[36moptional\x1b[0m] "
        f"{zom_metavar} \x1b[36moom\x1b[0m [\x1b[36moom\x1b[0m \x1b[36m...\x1b[0m] \x1b[36m...\x1b[0m \x1b[36mparser\x1b[0m \x1b[36m...\x1b[0m"
    )
    expected_help_output = f"""\
    {usage_text}

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36mrequired\x1b[0m
      \x1b[36mint\x1b[0m
      \x1b[36moptional\x1b[0m
      \x1b[36mzom\x1b[0m
      \x1b[36moom\x1b[0m
      \x1b[36mremainder\x1b[0m
      \x1b[36mparser\x1b[0m
      \x1b[36msuppress\x1b[0m

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m            \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--opt\x1b[0m [\x1b[38;5;36mOPT\x1b[0m]
      \x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS\x1b[0m [\x1b[38;5;36mOPTS\x1b[0m \x1b[38;5;36m...\x1b[0m]
    """
    assert parser.format_help() == clean_argparse(expected_help_output)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="not available in 3.8")
@pytest.mark.usefixtures("force_color")
def test_boolean_optional_action_spans():  # pragma: >=3.9 cover
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("--bool", action=argparse.BooleanOptionalAction)
    expected_help_output = """\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--bool\x1b[0m | \x1b[36m--no-bool\x1b[0m]

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m         \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--bool\x1b[0m, \x1b[36m--no-bool\x1b[0m
    """
    assert parser.format_help() == clean_argparse(expected_help_output)


def test_usage_spans_errors():
    parser = ArgumentParser()
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
    formatter.add_usage(usage=SUPPRESS, actions=[], groups=[])
    out = formatter.format_help()
    assert not formatter._root_section.rich_items
    assert not out


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_raw_description_rich_help_formatter():
    long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 3)
    parsers = ArgumentParsers(
        RawDescriptionHelpFormatter,
        RawDescriptionRichHelpFormatter,
        prog="PROG",
        description=long_text,
        epilog=long_text,
    )
    groups = parsers.add_argument_group("group", description=long_text)
    groups.add_argument("--long", help=long_text)

    expected_help_output = """\
    usage: PROG [-h] [--long LONG]

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    optional arguments:
      -h, --help   show this help message and exit

    group:
      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

      --long LONG  The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the
                   lazy dog. The quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_raw_text_rich_help_formatter():
    long_text = " ".join(["The quick brown fox jumps over the lazy dog."] * 3)
    parsers = ArgumentParsers(
        RawTextHelpFormatter,
        RawTextRichHelpFormatter,
        prog="PROG",
        description=long_text,
        epilog=long_text,
    )
    groups = parsers.add_argument_group("group", description=long_text)
    groups.add_argument("--long", help=long_text)

    expected_help_output = """\
    usage: PROG [-h] [--long LONG]

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    optional arguments:
      -h, --help   show this help message and exit

    group:
      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

      --long LONG  The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog.
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_argument_default_rich_help_formatter():
    parsers = ArgumentParsers(
        ArgumentDefaultsHelpFormatter, ArgumentDefaultsRichHelpFormatter, prog="PROG"
    )
    parsers.add_argument("--option", default="def", help="help of option")

    expected_help_output = """\
    usage: PROG [-h] [--option OPTION]

    optional arguments:
      -h, --help       show this help message and exit
      --option OPTION  help of option (default: def)
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))


@pytest.mark.usefixtures("disable_group_name_formatter")
def test_metavar_type_help_formatter():
    parsers = ArgumentParsers(MetavarTypeHelpFormatter, MetavarTypeRichHelpFormatter, prog="PROG")
    parsers.add_argument("--count", type=int, default=0, help="how many?")

    expected_help_output = """\
    usage: PROG [-h] [--count int]

    optional arguments:
      -h, --help   show this help message and exit
      --count int  how many?
    """
    parsers.assert_format_help_equal(expected=clean_argparse(expected_help_output))


def test_django_rich_help_formatter():
    # https://github.com/django/django/blob/8eed30aec6/django/core/management/base.py#L105-L131
    class DjangoHelpFormatter(HelpFormatter):
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

    parser = ArgumentParser("command", formatter_class=DjangoRichHelpFormatter)
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("--traceback", action="store_true", help="show traceback")
    parser.add_argument("my-arg", help="custom argument.")
    parser.add_argument("--my-option", action="store_true", help="custom option")
    parser.add_argument("--verbosity", action="count", help="verbosity level")
    parser.add_argument("-a", "--an-option", action="store_true", help="another custom option")

    expected_help_output = """\
    Usage: command [-h] [--my-option] [-a] [--version] [--traceback] [--verbosity] my-arg

    Positional Arguments:
      my-arg           custom argument.

    Optional Arguments:
      -h, --help       show this help message and exit
      --my-option      custom option
      -a, --an-option  another custom option
      --version        show program's version number and exit
      --traceback      show traceback
      --verbosity      verbosity level
    """
    assert parser.format_help() == clean_argparse(expected_help_output)


@pytest.mark.parametrize("indent_increment", (1, 3))
@pytest.mark.parametrize("max_help_position", (25, 26, 27))
@pytest.mark.parametrize("width", (None, 70))
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_help_formatter_args(indent_increment, max_help_position, width):
    # Note: the length of the option string is chosen to test edge cases where it is less than,
    # equal to, and bigger than max_help_position
    parsers = ArgumentParsers(
        lambda prog: HelpFormatter(prog, indent_increment, max_help_position, width),
        lambda prog: RichHelpFormatter(prog, indent_increment, max_help_position, width),
        prog="program",
    )
    parsers.add_argument("option-of-certain-length", help="This is the help of the said option")
    parsers.assert_format_help_equal()


def test_return_output():
    parser = ArgumentParser("prog", formatter_class=RichHelpFormatter)
    assert parser.format_help()


@pytest.mark.usefixtures("force_color")
def test_text_highlighter():
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("arg", help="Did you try `RichHelpFormatter.highlighter`?")

    expected_help_output = """\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] \x1b[36marg\x1b[0m

    \x1b[38;5;208mPositional Arguments:\x1b[0m
      \x1b[36marg\x1b[0m         \x1b[39mDid you try `\x1b[0m\x1b[1;39mRichHelpFormatter.highlighter\x1b[0m\x1b[39m`?\x1b[0m

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
    """

    # Make sure we can use a style multiple times in regexes
    pattern_with_duplicate_style = r"'(?P<syntax>[^']*)'"
    RichHelpFormatter.highlights.append(pattern_with_duplicate_style)
    assert parser.format_help() == clean_argparse(expected_help_output)
    RichHelpFormatter.highlights.remove(pattern_with_duplicate_style)


@pytest.mark.usefixtures("force_color")
def test_default_highlights():
    parser = ArgumentParser(
        "PROG",
        formatter_class=RichHelpFormatter,
        description="Description with `syntax` and --options.",
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
    # options inside backticks should not be highlighted
    parser.add_argument("--not-option", action="store_true", help="Start `not --option` end")
    # %(default)s highlights
    parser.add_argument("--default", default=10, help="The default value is %(default)s.")

    expected_help_output = """
    \x1b[39mDescription with `\x1b[0m\x1b[1;39msyntax\x1b[0m\x1b[39m` and \x1b[0m\x1b[36m--options\x1b[0m\x1b[39m.\x1b[0m

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m         \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--syntax-normal\x1b[0m    \x1b[39mStart `\x1b[0m\x1b[1;39mmiddle\x1b[0m\x1b[39m` end\x1b[0m
      \x1b[36m--syntax-start\x1b[0m     \x1b[39m`\x1b[0m\x1b[1;39mStart\x1b[0m\x1b[39m` middle end\x1b[0m
      \x1b[36m--syntax-end\x1b[0m       \x1b[39mStart middle `\x1b[0m\x1b[1;39mend\x1b[0m\x1b[39m`\x1b[0m
      \x1b[36m--option-normal\x1b[0m    \x1b[39mStart \x1b[0m\x1b[36m--middle\x1b[0m\x1b[39m end\x1b[0m
      \x1b[36m--option-start\x1b[0m     \x1b[36m--Start\x1b[0m\x1b[39m middle end\x1b[0m
      \x1b[36m--option-end\x1b[0m       \x1b[39mStart middle \x1b[0m\x1b[36m--end\x1b[0m
      \x1b[36m--option-comma\x1b[0m     \x1b[39mStart \x1b[0m\x1b[36m--middle\x1b[0m\x1b[39m, end\x1b[0m
      \x1b[36m--option-multi\x1b[0m     \x1b[39mStart \x1b[0m\x1b[36m--middle-word\x1b[0m\x1b[39m end\x1b[0m
      \x1b[36m--option-not\x1b[0m       \x1b[39mStart middle-word end\x1b[0m
      \x1b[36m--option-short\x1b[0m     \x1b[39mStart \x1b[0m\x1b[36m-middle\x1b[0m\x1b[39m end\x1b[0m
      \x1b[36m--not-option\x1b[0m       \x1b[39mStart `\x1b[0m\x1b[1;39mnot --option\x1b[0m\x1b[39m` end\x1b[0m
      \x1b[36m--default\x1b[0m \x1b[38;5;36mDEFAULT\x1b[0m  \x1b[39mThe default value is \x1b[0m\x1b[3;39m10\x1b[0m\x1b[39m.\x1b[0m

    \x1b[39mEpilog with `\x1b[0m\x1b[1;39msyntax\x1b[0m\x1b[39m` and \x1b[0m\x1b[36m--options\x1b[0m\x1b[39m.\x1b[0m
    """
    assert parser.format_help().endswith(clean_argparse(expected_help_output))


@pytest.mark.usefixtures("force_color")
def test_subparsers_usage():
    # Parent uses RichHelpFormatter
    rich_parent = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    rich_subparsers = rich_parent.add_subparsers()
    rich_child1 = rich_subparsers.add_parser("sp1", formatter_class=RichHelpFormatter)
    rich_child2 = rich_subparsers.add_parser("sp2")
    assert rich_parent.format_usage() == (
        "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] "
        "\x1b[36m{sp1,sp2}\x1b[0m \x1b[36m...\x1b[0m\n"
    )
    assert rich_child1.format_usage() == (
        "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG sp1\x1b[0m [\x1b[36m-h\x1b[0m]\n"
    )
    assert rich_child2.format_usage() == "usage: PROG sp2 [-h]\n"

    # Parent uses original formatter
    orig_parent = ArgumentParser("PROG")
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
    action = Action(["-t"], dest="test", help=f"%(prog){ct}")
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
    lazy_rich = {k: v for k, v in r.__dict__.items() if k not in r.__all__}
    with patch.dict(sys.modules, sys_modules_no_rich, clear=True), patch.dict(
        r.__dict__, lazy_rich, clear=True
    ):
        parser = ArgumentParser(formatter_class=RichHelpFormatter)
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

    with pytest.raises(AttributeError, match="Foo"):
        _ = r.Foo


def test_help_with_control_codes():
    parsers = ArgumentParsers(HelpFormatter, RichHelpFormatter, prog="PROG\r\nRAM")
    parsers.add_argument(
        "--long-option-with-control-codes-in-metavar", metavar="META\r\nVAR", help="%(metavar)s"
    )
    orig_parser, rich_parser = parsers.parsers
    orig_help = orig_parser.format_help().lower()
    rich_help = rich_parser.format_help().lower()
    assert rich_help == orig_help.replace("\r", "")  # rich strips \r and other control codes

    expected_help_text = """\
\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m
\x1b[38;5;244mRAM\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--long-option-with-control-codes-in-metavar\x1b[0m \x1b[38;5;36mMETA\x1b[0m
\x1b[38;5;36mVAR\x1b[0m]

\x1b[38;5;208mOptional Arguments:\x1b[0m
  \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m            \x1b[39mshow this help message and exit\x1b[0m
  \x1b[36m--long-option-with-control-codes-in-metavar\x1b[0m \x1b[38;5;36mMETA\x1b[0m
\x1b[38;5;36mVAR\x1b[0m
                        \x1b[39mMETA VAR\x1b[0m
"""
    with patch("rich.console.Console.is_terminal", return_value=True):
        colored_help_text = rich_parser.format_help()
    # cannot use textwrap.dedent because of the control codes
    assert colored_help_text == clean_argparse(expected_help_text, dedent=False)


@pytest.mark.skipif(sys.platform != "win32", reason="windows-only test")
@pytest.mark.usefixtures("force_color")
def test_legacy_windows():  # pragma: win32 cover
    expected_output = """\
    Usage: PROG [-h]

    Optional Arguments:
      -h, --help  show this help message and exit
    """
    expected_colored_output = """\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m]

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
    """

    # New windows console => colors: YES, initialization: NO
    init_win_colors = Mock(return_value=True)
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    with patch("rich_argparse._common._initialize_win_colors", init_win_colors):
        help = parser.format_help()
    assert help == clean_argparse(expected_colored_output)
    init_win_colors.assert_not_called()

    # Legacy windows console on new windows => colors: YES, initialization: YES
    init_win_colors = Mock(return_value=True)
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    with patch("rich.console.detect_legacy_windows", return_value=True), patch(
        "rich_argparse._common._initialize_win_colors", init_win_colors
    ):
        help = parser.format_help()
    assert help == clean_argparse(expected_colored_output)
    init_win_colors.assert_called_once_with()

    # Legacy windows console on old windows => colors: NO, initialization: YES
    init_win_colors = Mock(return_value=False)
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    with patch("rich.console.detect_legacy_windows", return_value=True), patch(
        "rich_argparse._common._initialize_win_colors", init_win_colors
    ):
        help = parser.format_help()
    assert help == clean_argparse(expected_output)
    init_win_colors.assert_called_once_with()

    # Legacy windows, but colors disabled in formatter => colors: NO, initialization: NO
    def fmt_no_color(prog):
        fmt = RichHelpFormatter(prog)
        fmt.console = r.Console(theme=r.Theme(fmt.styles), color_system=None)
        return fmt

    init_win_colors = Mock(return_value=True)
    no_colors_parser = ArgumentParser("PROG", formatter_class=fmt_no_color)
    with patch("rich.console.detect_legacy_windows", return_value=True), patch(
        "rich_argparse._common._initialize_win_colors", init_win_colors
    ):
        help = no_colors_parser.format_help()
    assert help == clean_argparse(expected_output)
    init_win_colors.assert_not_called()


@pytest.mark.skipif(sys.platform == "win32", reason="non-windows test")
def test_no_win_console_init_on_unix():  # pragma: win32 no cover
    text = "\x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m]"
    console = r.Console(legacy_windows=True, force_terminal=True)
    init_win_colors = Mock(return_value=True)
    with patch("rich_argparse._common._initialize_win_colors", init_win_colors):
        out = _fix_legacy_win_text(console, text)
    assert out == text
    init_win_colors.assert_not_called()


@pytest.mark.usefixtures("force_color")
def test_rich_renderables():
    table = Table("foo", "bar")
    table.add_row("1", "2")
    parser = ArgumentParser(
        "PROG",
        formatter_class=RichHelpFormatter,
        description=Markdown(
            textwrap.dedent(
                """\
                This is a **description**
                _________________________

                | foo | bar |
                | --- | --- |
                | 1   | 2   |
                """
            )
        ),
        epilog=Group(Markdown("This is an *epilog*"), table, Text("The end.", style="red")),
    )
    expected_help = """\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m]

    This is a \x1b[1mdescription\x1b[0m

    \x1b[33m──────────────────────────────────────────────────────────────────────────────────────────────────\x1b[0m

     \x1b[1m \x1b[0m\x1b[1mfoo\x1b[0m\x1b[1m \x1b[0m \x1b[1m \x1b[0m\x1b[1mbar\x1b[0m
     ━━━━━━━━━━━
      1     2

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m

    This is an \x1b[3mepilog\x1b[0m
    ┏━━━━━┳━━━━━┓
    ┃\x1b[1m \x1b[0m\x1b[1mfoo\x1b[0m\x1b[1m \x1b[0m┃\x1b[1m \x1b[0m\x1b[1mbar\x1b[0m\x1b[1m \x1b[0m┃
    ┡━━━━━╇━━━━━┩
    │ 1   │ 2   │
    └─────┴─────┘
    \x1b[31mThe end.\x1b[0m
    """
    assert parser.format_help() == clean_argparse(expected_help)


def test_help_preview_generation(tmp_path):
    parser = ArgumentParser("PROG", formatter_class=RichHelpFormatter)
    parser.add_argument("--foo", help="foo help")
    preview_action = parser.add_argument("--generate", action=HelpPreviewAction)
    default_path = tmp_path / "default-preview.svg"
    parser.add_argument("--generate-with-default", action=HelpPreviewAction, path=str(default_path))

    # No namespace pollution
    args = parser.parse_args(["--foo", "FOO"])
    assert vars(args) == {"foo": "FOO"}

    # No help pollution
    assert "--generate" not in parser.format_help()

    # No file, error
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate"])
    assert exc_info.value.code == 1

    # Default file, ok
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate-with-default"])
    assert exc_info.value.code == 0
    assert default_path.exists()

    # SVG file
    svg_file = tmp_path / "preview.svg"
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate", str(svg_file)])
    assert exc_info.value.code == 0
    assert svg_file.exists()
    svg_out = svg_file.read_text()
    assert svg_out.startswith("<svg")
    assert "Usage" in svg_out

    # HTML file
    preview_action.export_kwds = {}
    html_file = tmp_path / "preview.html"
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate", str(html_file)])
    assert exc_info.value.code == 0
    assert html_file.exists()
    html_out = html_file.read_text()
    assert html_out.startswith("<!DOCTYPE html>")
    assert "Usage" in html_out

    # TXT file
    preview_action.export_kwds = {}
    txt_file = tmp_path / "preview.txt"
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate", str(txt_file)])
    assert exc_info.value.code == 0
    assert txt_file.exists()
    assert txt_file.read_text().startswith("Usage:")

    # Wrong file extension
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate", str(tmp_path / "preview.png")])
    assert exc_info.value.code == 1

    # Wrong type
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--generate", ("",)])
    assert exc_info.value.code == 1


def test_disable_help_markup():
    parser = ArgumentParser(
        prog="PROG", formatter_class=RichHelpFormatter, description="[red]Description text.[/]"
    )
    parser.add_argument("--foo", default="def", help="[red]Help text (default: %(default)s).[/]")
    with patch.object(RichHelpFormatter, "help_markup", False):
        help_text = parser.format_help()
    expected_help_text = """\
    Usage: PROG [-h] [--foo FOO]

    Description text.

    Optional Arguments:
      -h, --help  show this help message and exit
      --foo FOO   [red]Help text (default: def).[/]
    """
    assert help_text == clean_argparse(expected_help_text)


def test_disable_text_markup():
    parser = ArgumentParser(
        prog="PROG", formatter_class=RichHelpFormatter, description="[red]Description text.[/]"
    )
    parser.add_argument("--foo", help="[red]Help text.[/]")
    with patch.object(RichHelpFormatter, "text_markup", False):
        help_text = parser.format_help()
    expected_help_text = """\
    Usage: PROG [-h] [--foo FOO]

    [red]Description text.[/]

    Optional Arguments:
      -h, --help  show this help message and exit
      --foo FOO   Help text.
    """
    assert help_text == clean_argparse(expected_help_text)


@pytest.mark.usefixtures("force_color")
def test_arg_default_spans():
    parser = ArgumentParser(prog="PROG", formatter_class=RichHelpFormatter)
    parser.add_argument(
        "--foo",
        default="def",
        help="(default: %(default)r) [red](default: %(default)s)[/] (default: %(default)s)",
    )
    expected_help_text = """\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--foo\x1b[0m \x1b[38;5;36mFOO\x1b[0m]

    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--foo\x1b[0m \x1b[38;5;36mFOO\x1b[0m   \x1b[39m(default: \x1b[0m\x1b[3;39m'def'\x1b[0m\x1b[39m) \x1b[0m\x1b[31m(default: \x1b[0m\x1b[3;39mdef\x1b[0m\x1b[31m)\x1b[0m\x1b[39m (default: \x1b[0m\x1b[3;39mdef\x1b[0m\x1b[39m)\x1b[0m
    """
    help_text = parser.format_help()
    assert help_text == clean_argparse(expected_help_text)


def test_arg_default_in_markup():
    parser = ArgumentParser(prog="PROG", formatter_class=RichHelpFormatter)
    parser.add_argument(
        "--foo",
        default="def",
        help=(
            "[%(type)r type](good: %(default)r)[bad: %(default)r] text [bad: %(default)s]"
            "(good: %(default)s) [link bad %(default)s] %(default)s"
        ),
    )
    expected_help_text = """\
    Usage: PROG [-h] [--foo FOO]

    Optional Arguments:
      -h, --help  show this help message and exit
      --foo FOO   [None type](good: 'def') text (good: def) def
    """
    with pytest.warns(
        UserWarning,
        match=re.escape(
            "Failed to process default value in help string of argument '--foo'.\n"
            "Hint: try disabling rich markup: `RichHelpFormatter.help_markup = False`\n"
            "      or replace brackets by parenthesis: `[bad: %(default)r]` -> `(bad: %(default)r)`"
        ),
    ):
        help_text = parser.format_help()
    assert help_text == clean_argparse(expected_help_text)


@pytest.mark.usefixtures("force_color")
def test_metavar_spans():
    # tests exotic metavars (tuples, wrapped, different nargs, etc.) in usage and help text
    parser = argparse.ArgumentParser(
        prog="PROG", formatter_class=lambda prog: RichHelpFormatter(prog, width=20)
    )
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument("--op1", metavar="MET", nargs="?")
    meg.add_argument("--op2", metavar=("MET1", "MET2"), nargs="*")
    meg.add_argument("--op3", nargs="*")
    meg.add_argument("--op4", metavar=("MET1", "MET2"), nargs="+")
    meg.add_argument("--op5", nargs="+")
    meg.add_argument("--op6", nargs=3)
    meg.add_argument("--op7", metavar=("MET1", "MET2", "MET3"), nargs=3)
    help_text = parser.format_help()

    op3_metavar = "[\x1b[38;5;36mOP3\x1b[0m \x1b[38;5;36m...\x1b[0m]"
    if sys.version_info < (3, 9):  # pragma: <3.9 cover
        op3_metavar = f"[\x1b[38;5;36mOP3\x1b[0m {op3_metavar}]"

    if sys.version_info >= (3, 13):  # pragma: >=3.13 cover
        usage_tail = """ |
                \x1b[36m--op2\x1b[0m [\x1b[38;5;36mMET1\x1b[0m [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m]] |
                \x1b[36m--op3\x1b[0m [\x1b[38;5;36mOP3\x1b[0m \x1b[38;5;36m...\x1b[0m] |
                \x1b[36m--op4\x1b[0m \x1b[38;5;36mMET1\x1b[0m [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m] |
                \x1b[36m--op5\x1b[0m \x1b[38;5;36mOP5\x1b[0m [\x1b[38;5;36mOP5\x1b[0m \x1b[38;5;36m...\x1b[0m] |
                \x1b[36m--op6\x1b[0m \x1b[38;5;36mOP6\x1b[0m \x1b[38;5;36mOP6\x1b[0m \x1b[38;5;36mOP6\x1b[0m |
                \x1b[36m--op7\x1b[0m \x1b[38;5;36mMET1\x1b[0m \x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36mMET3\x1b[0m]
        """
    else:  # pragma: <3.13 cover
        usage_tail = f"""
                | \x1b[36m--op2\x1b[0m
                [\x1b[38;5;36mMET1\x1b[0m [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m]]
                | \x1b[36m--op3\x1b[0m
                {op3_metavar}
                | \x1b[36m--op4\x1b[0m
                \x1b[38;5;36mMET1\x1b[0m
                [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m]
                | \x1b[36m--op5\x1b[0m
                \x1b[38;5;36mOP5\x1b[0m
                [\x1b[38;5;36mOP5\x1b[0m \x1b[38;5;36m...\x1b[0m]
                | \x1b[36m--op6\x1b[0m
                \x1b[38;5;36mOP6\x1b[0m \x1b[38;5;36mOP6\x1b[0m
                \x1b[38;5;36mOP6\x1b[0m |
                \x1b[36m--op7\x1b[0m
                \x1b[38;5;36mMET1\x1b[0m
                \x1b[38;5;36mMET2\x1b[0m
                \x1b[38;5;36mMET3\x1b[0m]
        """
    expected_help_text = f"""\
    \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m]
                [\x1b[36m--op1\x1b[0m [\x1b[38;5;36mMET\x1b[0m]{usage_tail}
    \x1b[38;5;208mOptional Arguments:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m
        \x1b[39mshow this help\x1b[0m
        \x1b[39mmessage and exit\x1b[0m
      \x1b[36m--op1\x1b[0m [\x1b[38;5;36mMET\x1b[0m]
      \x1b[36m--op2\x1b[0m [\x1b[38;5;36mMET1\x1b[0m [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m]]
      \x1b[36m--op3\x1b[0m {op3_metavar}
      \x1b[36m--op4\x1b[0m \x1b[38;5;36mMET1\x1b[0m [\x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36m...\x1b[0m]
      \x1b[36m--op5\x1b[0m \x1b[38;5;36mOP5\x1b[0m [\x1b[38;5;36mOP5\x1b[0m \x1b[38;5;36m...\x1b[0m]
      \x1b[36m--op6\x1b[0m \x1b[38;5;36mOP6\x1b[0m \x1b[38;5;36mOP6\x1b[0m \x1b[38;5;36mOP6\x1b[0m
      \x1b[36m--op7\x1b[0m \x1b[38;5;36mMET1\x1b[0m \x1b[38;5;36mMET2\x1b[0m \x1b[38;5;36mMET3\x1b[0m
    """
    assert help_text == clean_argparse(expected_help_text)


def test_patching():
    class MyArgumentParser(ArgumentParser):
        not_callable = None

    # Patch existing class
    patch_default_formatter_class(MyArgumentParser)
    assert MyArgumentParser().formatter_class is RichHelpFormatter

    # Override previous patch
    patch_default_formatter_class(MyArgumentParser, formatter_class=MetavarTypeRichHelpFormatter)
    assert MyArgumentParser().formatter_class is MetavarTypeRichHelpFormatter

    # Patch new class
    @patch_default_formatter_class(formatter_class=ArgumentDefaultsRichHelpFormatter)
    class MyArgumentParser2(ArgumentParser):
        pass

    assert MyArgumentParser2().formatter_class is ArgumentDefaultsRichHelpFormatter

    # Errors
    with pytest.raises(AttributeError, match=r"'MyArgumentParser' has no attribute 'missing'"):
        patch_default_formatter_class(MyArgumentParser, method_name="missing")

    with pytest.raises(TypeError, match=r"'MyArgumentParser\.not_callable' is not callable"):
        patch_default_formatter_class(MyArgumentParser, method_name="not_callable")
