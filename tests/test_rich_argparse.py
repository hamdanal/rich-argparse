from __future__ import annotations

import argparse
import io
import os
import re
import sys
from textwrap import dedent
from unittest.mock import patch

import pytest
from rich.text import Text

from rich_argparse_plus import RichHelpFormatterPlus

# helpers
# =======
OPTIONS_GROUP_NAME = "OPTIONS" if sys.version_info >= (3, 10) else "OPTIONAL ARGUMENTS"


def get_cmd_output(parser: argparse.ArgumentParser, cmd: list[str]) -> str:
    __tracebackhide__ = True
    stdout = io.StringIO()
    with pytest.raises(SystemExit), patch.object(sys, "stdout", stdout):
        parser.parse_args(cmd)
    return stdout.getvalue()


def _assert_same_lines(actual: str, expected: str) -> bool:
    if actual == expected:
        return True

    lines1 = actual.split("\n")
    lines2 = expected.split("\n")

    for i, line in enumerate(lines1):
        if line != lines2[i]:
            print(f"\nACTUAL.{i}: {_insert_spaces_between_chars(line)}")
            print(f"EXPECT.{i}: {_insert_spaces_between_chars(lines2[i])}\n")

    return actual == expected


def _insert_spaces_between_chars(_string: str) -> str:
    return '_'.join([c for c in _string])


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
    with patch.object(RichHelpFormatterPlus, "group_name_formatter", str):
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
        formatter_class=RichHelpFormatterPlus,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("--option", default="value", help="help of option")

    expected_help_output = f"""\
    USAGE: awesome_program [-h] [--version] [--option OPTION]

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
    # 1. all names and help text are short to avoid special wrapping
    # 2. no short and long options with args are used
    # 3. group_name_formatter is disabled
    # 4. colors are disabled
    # 5. no markup/emoji codes are used
    # 6. trailing whitespace is ignored
    parser = argparse.ArgumentParser(prog, usage=usage, description=description, epilog=epilog)
    parser.add_argument("file", default="-", help="A file argument")

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

    orig_out = parser.format_help()
    # Strip out lines that consist just of a colon
    orig_out = '\n'.join([line for line in orig_out.split("\n") if not re.match('^:$', line)])
    orig_out = orig_out.replace('A file argument', 'A file argument (default: -)')
    parser.formatter_class = RichHelpFormatterPlus
    rich_out = parser.format_help()
    assert rich_out == orig_out


def test_padding_and_wrapping():
    # padding of group descritpion works as expected even when wrapped
    # wrapping of options work as expected
    parser = argparse.ArgumentParser(
        "PROG", description="-" * 120, epilog="%" * 120, formatter_class=RichHelpFormatterPlus
    )
    parser.add_argument("-o", "--very-long-option-name", metavar="LONG_METAVAR", help="." * 120)
    group_with_description = parser.add_argument_group("group", description="*" * 120)
    group_with_description.add_argument("pos-arg", help="#" * 120)

    expected_help_output = f"""\
    USAGE: PROG [-h] [-o LONG_METAVAR] pos-arg

    --------------------------------------------------------------------------------------------------
    ----------------------

    {OPTIONS_GROUP_NAME}:
      -h, --help            show this help message and exit
      -o, --very-long-option-name LONG_METAVAR
                            ..........................................................................
                            ..............................................

    GROUP:
      ************************************************************************************************
      ************************

      pos-arg               ##########################################################################
                            ##############################################

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%
    """
    assert parser.format_help() == dedent(expected_help_output)


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
    rich_parser, rich_subparser = create_parsers(fmt_cls=RichHelpFormatterPlus)

    assert rich_parser.format_help() == orig_parser.format_help()
    assert rich_subparser.format_help() == orig_subparser.format_help()


def test_escape_params():
    # params such as %(prog)s and %(default)s must be escaped when substituted
    parser = argparse.ArgumentParser(
        "[underline]",
        description="%(prog)s description.",
        epilog="%(prog)s epilog.",
        formatter_class=RichHelpFormatterPlus,
    )

    class SpecialType(str):
        ...

    SpecialType.__name__ = "[link]"

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    parser.add_argument("pos-arg", metavar="[italic]", help="help of pos arg with special metavar")
    parser.add_argument(
        "--default", default="[default]", help="help with special default"
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
      --default DEFAULT  help with special default (default: [default])
      --type TYPE        help with special type: [link]
      --metavar [bold]   help with special metavar: [bold]

    [underline] epilog.
    """
    #import pdb; pdb.set_trace()
    assert _assert_same_lines(parser.format_help(), dedent(expected_help_output))
    assert get_cmd_output(parser, cmd=["--version"]) == "[underline] 1.0.0\n"


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
@pytest.mark.usefixtures("force_color")
def test_spans(usage, usage_text):
    parser = argparse.ArgumentParser("PROG", usage=usage, formatter_class=RichHelpFormatterPlus)
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
    \x1b[36m  file         \x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m   \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--weird\x1b[0m \x1b[38;5;36my)\x1b[0m
      \x1b[36m--flag\x1b[0m       \x1b[39mIs flag?\x1b[0m
      \x1b[36m--not-flag\x1b[0m   \x1b[39mIs not flag?\x1b[0m
      \x1b[36m--path\x1b[0m \x1b[38;5;36mPATH\x1b[0m  \x1b[39mOption path.\x1b[0m
      \x1b[36m--url\x1b[0m \x1b[38;5;36mURL\x1b[0m    \x1b[39mOption url.\x1b[0m
    """

    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.usefixtures("force_color")
def test_actions_spans_in_usage():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatterPlus)
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
    \x1b[36m  arg                   \x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m            \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--opt\x1b[0m \x1b[38;5;36m[OPT]\x1b[0m
      \x1b[36m--opts\x1b[0m \x1b[38;5;36mOPTS [OPTS ...]\x1b[0m
    """

    assert _assert_same_lines(parser.format_help(), dedent(expected_help_output))


@pytest.mark.skipif(sys.version_info <= (3, 9), reason="not available in 3.8")
@pytest.mark.usefixtures("force_color")
def test_boolean_optional_action_spans():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatterPlus)
    parser.add_argument("--bool", action=argparse.BooleanOptionalAction)
    expected_help_output = f"""\
    \x1b[38;5;208mUSAGE:\x1b[0m PROG [\x1b[36m-h\x1b[0m] [\x1b[36m--bool\x1b[0m | \x1b[36m--no-bool\x1b[0m]

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

    formatter = RichHelpFormatterPlus("PROG")
    with patch.object(RichHelpFormatterPlus, "_usage_spans", side_effect=ValueError):
        formatter.add_usage(usage=None, actions=actions, groups=groups, prefix=None)
    (usage,) = formatter._root_section.rich
    assert isinstance(usage, Text)
    assert str(usage) == "USAGE: PROG [-h]"
    (prefix_span,) = usage.spans
    assert prefix_span.start == 0
    assert prefix_span.end == len("usage:")
    assert prefix_span.style == "argparse.groups"


def test_no_help():
    formatter = RichHelpFormatterPlus("prog")
    formatter.add_usage(usage=argparse.SUPPRESS, actions=[], groups=[])
    out = formatter.format_help()
    assert not formatter._root_section.rich
    assert not out


# def test_with_argument_default_help_formatter():
#     class Fmt(RichHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
#         ...

#     parser = argparse.ArgumentParser("PROG", formatter_class=Fmt)
#     parser.add_argument("--option", default="def", help="help of option")

#     expected_help_output = f"""\
#     USAGE: PROG [-h] [--option OPTION]

#     {OPTIONS_GROUP_NAME}:
#       -h, --help       show this help message and exit
#       --option OPTION  help of option (default: def)
#     """
#     assert _assert_same_lines(parser.format_help(), dedent(expected_help_output))


def test_with_metavar_type_help_formatter():
    class Fmt(RichHelpFormatterPlus, argparse.MetavarTypeHelpFormatter):
        ...

    parser = argparse.ArgumentParser("PROG", formatter_class=Fmt)
    parser.add_argument("--count", type=int, default=0, help="how many?")

    expected_help_output = f"""\
    USAGE: PROG [-h] [--count int]

    {OPTIONS_GROUP_NAME}:
      -h, --help   show this help message and exit
      --count int  how many?
    """
    assert parser.format_help() == dedent(expected_help_output)


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

    class Fmt(DjangoHelpFormatter, RichHelpFormatterPlus):
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
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.parametrize("indent_increment", (1, 3))
@pytest.mark.parametrize("max_help_position", (25, 26, 27))
@pytest.mark.parametrize("width", (None, 70))
@pytest.mark.usefixtures("disable_group_name_formatter")
def test_help_formatter_args(indent_increment, max_help_position, width):
    # Note: the length of the option corresponds with the values of max_help_position
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
        formatter_class=lambda prog: RichHelpFormatterPlus(
            prog, indent_increment, max_help_position, width
        ),
    )
    rich_parser.add_argument(option, help=help_text)
    assert rich_parser.format_help() == orig_parser.format_help()


def test_return_output():
    parser = argparse.ArgumentParser("prog", formatter_class=RichHelpFormatterPlus)
    assert parser.format_help()


@pytest.mark.usefixtures("force_color")
def test_text_highlighter():
    parser = argparse.ArgumentParser("PROG", formatter_class=RichHelpFormatterPlus)
    parser.add_argument("arg", help="Did you try `RichHelpFormatterPlus.highlighter`?")

    expected_help_output = f"""\
    \x1b[38;5;208mUSAGE:\x1b[0m PROG [\x1b[36m-h\x1b[0m] \x1b[36marg\x1b[0m

    \x1b[38;5;208mPOSITIONAL ARGUMENTS:\x1b[0m
    \x1b[36m  arg         \x1b[0m\x1b[39mDid you try `\x1b[0m\x1b[1;39mRichHelpFormatterPlus.highlighter\x1b[0m\x1b[39m`?\x1b[0m

    \x1b[38;5;208m{OPTIONS_GROUP_NAME}:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
    """

    assert _assert_same_lines(parser.format_help(), dedent(expected_help_output))


@pytest.mark.usefixtures("force_color")
def test_default_highlights():
    parser = argparse.ArgumentParser(
        "PROG",
        formatter_class=RichHelpFormatterPlus,
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


def test_escape_params_and_expand_help():
    formatter = RichHelpFormatterPlus('awesomeprog')

    action = argparse._StoreAction(
        dest='metavar',
        help='help with special metavar: %(metavar)s',
        metavar='[bold]',
        option_strings=['--metavar'],
        required=False
    )
    output = formatter._escape_params_and_expand_help(action)
    assert output == Text('help with special metavar: [bold]')

    choice_action = argparse._StoreAction(
        dest='arg_name',
        help='help with a choice',
        metavar='CHOICE',
        choices=range(101),
        option_strings=['--arg-name'],
        required=False
    )
    output = formatter._escape_params_and_expand_help(choice_action)
    assert output == Text('help with a choice (range: 0-100)')

    default_default_action = argparse._StoreAction(
        dest='default',
        default='[default]',
        help='help with special default',
        option_strings=['--default'],
        required=False
    )
    output = formatter._escape_params_and_expand_help(default_default_action)
    print(f"Plains: {output.plain}")
    assert output == Text('help with special default (default: [default])')
