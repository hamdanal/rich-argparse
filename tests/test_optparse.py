from __future__ import annotations

import sys
from optparse import SUPPRESS_HELP, IndentedHelpFormatter, OptionParser, TitledHelpFormatter
from textwrap import dedent
from unittest.mock import Mock, patch

import pytest
from rich import get_console

import rich_argparse._lazy_rich as r
from rich_argparse.optparse import (
    GENERATE_USAGE,
    IndentedRichHelpFormatter,
    RichHelpFormatter,
    TitledRichHelpFormatter,
)
from tests.helpers import OptionParsers


def test_default_substitution():
    parser = OptionParser(prog="PROG", formatter=IndentedRichHelpFormatter())
    parser.add_option("--option", default="[bold]", help="help of option (default: %default)")

    expected_help_output = """\
    Usage: PROG [options]

    Options:
      -h, --help       show this help message and exit
      --option=OPTION  help of option (default: [bold])
    """
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.parametrize("prog", (None, "PROG"), ids=("no_prog", "prog"))
@pytest.mark.parametrize("usage", (None, "USAGE"), ids=("no_usage", "usage"))
@pytest.mark.parametrize("description", (None, "A description."), ids=("no_desc", "desc"))
@pytest.mark.parametrize("epilog", (None, "An epilog."), ids=("no_epilog", "epilog"))
def test_overall_structure(prog, usage, description, epilog):
    # The output must be consistent with the original HelpFormatter in these cases:
    # 1. no markup/emoji codes are used
    # 4. colors are disabled
    parsers = OptionParsers(
        IndentedHelpFormatter(),
        IndentedRichHelpFormatter(),
        prog=prog,
        usage=usage,
        description=description,
        epilog=epilog,
    )
    parsers.add_option("--file", default="-", help="A file (default: %default).")
    parsers.add_option("--spaces", help="Arg   with  weird\n\n whitespaces\t\t.")
    parsers.add_option("--very-very-very-very-very-very-very-very-long-option-name", help="help!")
    parsers.add_option("--very-long-option-that-has-no-help-text")

    # all types of empty groups
    parsers.add_option_group("empty group name", description="empty_group description")
    parsers.add_option_group("no description empty group name")
    parsers.add_option_group("", description="empty_name_empty_group description")
    parsers.add_option_group("spaces group", description=" \tspaces_group description  ")

    # all types of non-empty groups
    groups = parsers.add_option_group("title", description="description")
    groups.add_option("--arg1", help="help inside group")
    no_desc_groups = parsers.add_option_group("title")
    no_desc_groups.add_option("--arg2", help="arg help inside no_desc_group")
    empty_title_group = parsers.add_option_group("", description="description")
    empty_title_group.add_option("--arg3", help="arg help inside empty_title_group")

    parsers.assert_format_help_equal()


def test_padding_and_wrapping():
    parsers = OptionParsers(
        IndentedHelpFormatter(),
        IndentedRichHelpFormatter(),
        prog="PROG",
        description="-" * 120,
        epilog="%" * 120,
    )
    parsers.add_option("--very-long-option-name", metavar="LONG_METAVAR", help="." * 120)
    group_with_descriptions = parsers.add_option_group("Group", description="*" * 120)
    group_with_descriptions.add_option("--arg", help="#" * 120)

    expected_help_output = """\
    Usage: PROG [options]

    --------------------------------------------------------------------------------------------------
    ----------------------

    Options:
      -h, --help            show this help message and exit
      --very-long-option-name=LONG_METAVAR
                            ..........................................................................
                            ..............................................

      Group:
        ******************************************************************************************
        ******************************

        --arg=ARG           ##########################################################################
                            ##############################################

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%
    """

    parsers.assert_format_help_equal(expected=dedent(expected_help_output))


@pytest.mark.xfail(reason="rich wraps differently")
def test_wrapping_compatible():
    # needs fixing rich wrapping to be compatible with textwrap.wrap
    parsers = OptionParsers(
        IndentedHelpFormatter(),
        IndentedRichHelpFormatter(),
        prog="PROG",
        description="some text " + "-" * 120,
    )
    parsers.assert_format_help_equal()


@pytest.mark.usefixtures("force_color")
def test_with_colors():
    parser = OptionParser(prog="PROG", formatter=IndentedRichHelpFormatter())
    parser.add_option("--file")
    parser.add_option("--hidden", help=SUPPRESS_HELP)
    parser.add_option("--flag", action="store_true", help="Is flag?")
    parser.add_option("--not-flag", action="store_true", help="Is not flag?")
    parser.add_option("-y", help="Yes.")
    parser.add_option("-n", help="No.")

    expected_help_output = """\
    \x1b[38;5;208mUsage:\x1b[0m PROG [options]

    \x1b[38;5;208mOptions:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m       \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--file\x1b[0m=\x1b[38;5;36mFILE\x1b[0m
      \x1b[36m--flag\x1b[0m           \x1b[39mIs flag?\x1b[0m
      \x1b[36m--not-flag\x1b[0m       \x1b[39mIs not flag?\x1b[0m
      \x1b[36m-y\x1b[0m \x1b[38;5;36mY\x1b[0m             \x1b[39mYes.\x1b[0m
      \x1b[36m-n\x1b[0m \x1b[38;5;36mN\x1b[0m             \x1b[39mNo.\x1b[0m
    """
    assert parser.format_help() == dedent(expected_help_output)


@pytest.mark.parametrize("indent_increment", (1, 3))
@pytest.mark.parametrize("max_help_position", (25, 26, 27))
@pytest.mark.parametrize("width", (None, 70))
@pytest.mark.parametrize("short_first", (1, 0))
def test_help_formatter_args(indent_increment, max_help_position, width, short_first):
    parsers = OptionParsers(
        IndentedHelpFormatter(indent_increment, max_help_position, width, short_first),
        IndentedRichHelpFormatter(indent_increment, max_help_position, width, short_first),
        prog="PROG",
    )
    # Note: the length of the option string is chosen to test edge cases where it is less than,
    # equal to, and bigger than max_help_position
    parsers.add_option(
        "--option-of-certain-size", action="store_true", help="This is the help of the said option"
    )
    parsers.assert_format_help_equal()


def test_return_output():
    parser = OptionParser(prog="prog", formatter=IndentedRichHelpFormatter())
    assert parser.format_help()


@pytest.mark.usefixtures("force_color")
def test_text_highlighter():
    parser = OptionParser(prog="PROG", formatter=IndentedRichHelpFormatter())
    parser.add_option(
        "--arg", action="store_true", help="Did you try `RichHelpFormatter.highlighter`?"
    )

    expected_help_output = """\
    \x1b[38;5;208mUsage:\x1b[0m PROG [options]

    \x1b[38;5;208mOptions:\x1b[0m
      \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
      \x1b[36m--arg\x1b[0m       \x1b[39mDid you try `\x1b[0m\x1b[1;39mRichHelpFormatter.highlighter\x1b[0m\x1b[39m`?\x1b[0m
    """

    # Make sure we can use a style multiple times in regexes
    pattern_with_duplicate_style = r"'(?P<syntax>[^']*)'"
    RichHelpFormatter.highlights.append(pattern_with_duplicate_style)
    assert parser.format_help() == dedent(expected_help_output)
    RichHelpFormatter.highlights.remove(pattern_with_duplicate_style)


@pytest.mark.usefixtures("force_color")
def test_default_highlights():
    parser = OptionParser(
        "PROG",
        formatter=IndentedRichHelpFormatter(),
        description="Description with `syntax` and --options.",
        epilog="Epilog with `syntax` and --options.",
    )
    # syntax highlights
    parser.add_option("--syntax-normal", action="store_true", help="Start `middle` end")
    parser.add_option("--syntax-start", action="store_true", help="`Start` middle end")
    parser.add_option("--syntax-end", action="store_true", help="Start middle `end`")
    # --options highlights
    parser.add_option("--option-normal", action="store_true", help="Start --middle end")
    parser.add_option("--option-start", action="store_true", help="--Start middle end")
    parser.add_option("--option-end", action="store_true", help="Start middle --end")
    parser.add_option("--option-comma", action="store_true", help="Start --middle, end")
    parser.add_option("--option-multi", action="store_true", help="Start --middle-word end")
    parser.add_option("--option-not", action="store_true", help="Start middle-word end")
    parser.add_option("--option-short", action="store_true", help="Start -middle end")

    expected_help_output = """
    \x1b[39mDescription with `\x1b[0m\x1b[1;39msyntax\x1b[0m\x1b[39m` and \x1b[0m\x1b[36m--options\x1b[0m\x1b[39m.\x1b[0m

    \x1b[38;5;208mOptions:\x1b[0m
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


def test_empty_fields():
    orig_fmt = IndentedRichHelpFormatter()
    rich_fmt = IndentedRichHelpFormatter()
    assert rich_fmt.format_usage("") == orig_fmt.format_usage("")
    assert rich_fmt.format_heading("") == orig_fmt.format_heading("")
    assert rich_fmt.format_description("") == orig_fmt.format_description("")
    assert rich_fmt.format_epilog("") == orig_fmt.format_epilog("")

    parser = OptionParser()
    option = parser.add_option("--option")
    for fmt in (orig_fmt, rich_fmt):
        fmt.store_option_strings(parser)
        fmt.set_parser(parser)
    assert rich_fmt.format_option(option) == orig_fmt.format_option(option)

    option = parser.add_option("--option2", help="help")
    for fmt in (orig_fmt, rich_fmt):
        fmt.store_option_strings(parser)
        fmt.default_tag = None
    assert rich_fmt.format_option(option) == orig_fmt.format_option(option)


def test_titled_help_formatter():
    parsers = OptionParsers(
        TitledHelpFormatter(),
        TitledRichHelpFormatter(),
        prog="PROG",
        description="Description.",
        epilog="Epilog.",
    )
    parsers.add_option("--option", help="help")
    groups = parsers.add_option_group("Group")
    groups.add_option("-s", "--short", help="help")
    groups.add_option("-o", "-O", help="help")
    parsers.assert_format_help_equal()


@pytest.mark.usefixtures("force_color")
def test_titled_help_formatter_colors():
    parser = OptionParser(
        prog="PROG",
        description="Description.",
        epilog="Epilog.",
        formatter=TitledRichHelpFormatter(),
    )
    parser.add_option("--option", help="help")
    expected_help_output = """\
    \x1b[38;5;208mUsage\x1b[0m
    \x1b[38;5;208m=====\x1b[0m
      PROG [options]

    \x1b[39mDescription.\x1b[0m

    \x1b[38;5;208mOptions\x1b[0m
    \x1b[38;5;208m=======\x1b[0m
    \x1b[36m--help\x1b[0m, \x1b[36m-h\x1b[0m       \x1b[39mshow this help message and exit\x1b[0m
    \x1b[36m--option\x1b[0m=\x1b[38;5;36mOPTION\x1b[0m  \x1b[39mhelp\x1b[0m

    \x1b[39mEpilog.\x1b[0m
    """
    assert parser.format_help() == dedent(expected_help_output)


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
        parser = OptionParser(formatter=IndentedRichHelpFormatter())
        parser.add_option("--foo", help="foo help")
        values, args = parser.parse_args(["--foo", "bar"])
        assert values.foo == "bar"
        assert not args
        assert sys.modules
        assert "rich" not in sys.modules  # no help formatting, do not import rich
        for mod_name in sys.modules:
            assert not mod_name.startswith("rich.")
        parser.format_help()
        assert "rich" in sys.modules  # format help has been called

    formatter = IndentedRichHelpFormatter()
    assert formatter._console is None
    formatter.console = get_console()
    assert formatter._console is not None

    with pytest.raises(AttributeError, match="Foo"):
        _ = r.Foo


@pytest.mark.skipif(sys.platform != "win32", reason="windows-only test")
@pytest.mark.usefixtures("force_color")
@pytest.mark.parametrize(
    ("legacy_console", "old_windows", "colors"),
    (
        pytest.param(True, False, True, id="legacy_console-new_windows"),
        pytest.param(True, True, False, id="legacy_console-old_windows"),
        pytest.param(False, None, True, id="new_console"),
    ),
)
def test_legacy_windows(legacy_console, old_windows, colors):  # pragma: win32 cover
    expected_output = {
        False: """\
        Usage: PROG [options]

        Options:
          -h, --help  show this help message and exit
        """,
        True: """\
        \x1b[38;5;208mUsage:\x1b[0m PROG [options]

        \x1b[38;5;208mOptions:\x1b[0m
          \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
        """,
    }[colors]

    init_win_colors = Mock(return_value=not old_windows)
    parser = OptionParser(prog="PROG", formatter=IndentedRichHelpFormatter())
    with patch("rich.console.detect_legacy_windows", return_value=legacy_console), patch(
        "rich_argparse._common._initialize_win_colors", init_win_colors
    ):
        assert parser.format_help() == dedent(expected_output)
    if legacy_console:
        init_win_colors.assert_called_with()
    else:
        init_win_colors.assert_not_called()


@pytest.mark.parametrize(
    ("formatter", "description", "nb_o", "expected"),
    (
        pytest.param(
            IndentedRichHelpFormatter(),
            None,
            2,
            """\
            \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--foo\x1b[0m \x1b[38;5;36mFOO\x1b[0m]

            \x1b[38;5;208mOptions:\x1b[0m
              \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
              \x1b[36m--foo\x1b[0m=\x1b[38;5;36mFOO\x1b[0m   \x1b[39mfoo help\x1b[0m
            """,
            id="indented",
        ),
        pytest.param(
            IndentedRichHelpFormatter(),
            "A description.",
            2,
            """\
            \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--foo\x1b[0m \x1b[38;5;36mFOO\x1b[0m]

            \x1b[39mA description.\x1b[0m

            \x1b[38;5;208mOptions:\x1b[0m
              \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
              \x1b[36m--foo\x1b[0m=\x1b[38;5;36mFOO\x1b[0m   \x1b[39mfoo help\x1b[0m
            """,
            id="indented-desc",
        ),
        pytest.param(
            IndentedRichHelpFormatter(),
            None,
            30,
            """\
            \x1b[38;5;208mUsage:\x1b[0m \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m]
                        [\x1b[36m--foooooooooooooooooooooooooooooo\x1b[0m \x1b[38;5;36mFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\x1b[0m]

            \x1b[38;5;208mOptions:\x1b[0m
              \x1b[36m-h\x1b[0m, \x1b[36m--help\x1b[0m            \x1b[39mshow this help message and exit\x1b[0m
              \x1b[36m--foooooooooooooooooooooooooooooo\x1b[0m=\x1b[38;5;36mFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\x1b[0m
                                    \x1b[39mfoo help\x1b[0m
            """,
            id="indented-long",
        ),
        pytest.param(
            TitledRichHelpFormatter(),
            None,
            2,
            """\
            \x1b[38;5;208mUsage\x1b[0m
            \x1b[38;5;208m=====\x1b[0m
              \x1b[38;5;244mPROG\x1b[0m [\x1b[36m-h\x1b[0m] [\x1b[36m--foo\x1b[0m \x1b[38;5;36mFOO\x1b[0m]

            \x1b[38;5;208mOptions\x1b[0m
            \x1b[38;5;208m=======\x1b[0m
            \x1b[36m--help\x1b[0m, \x1b[36m-h\x1b[0m  \x1b[39mshow this help message and exit\x1b[0m
            \x1b[36m--foo\x1b[0m=\x1b[38;5;36mFOO\x1b[0m   \x1b[39mfoo help\x1b[0m
            """,
            id="titled",
        ),
    ),
)
@pytest.mark.usefixtures("force_color")
def test_generated_usage(formatter, description, nb_o, expected):
    parser = OptionParser(
        prog="PROG", formatter=formatter, usage=GENERATE_USAGE, description=description
    )
    parser.add_option("--f" + "o" * nb_o, help="foo help")
    parser.add_option("--bar", help=SUPPRESS_HELP)
    assert parser.format_help() == dedent(expected)


def test_generated_usage_no_parser():
    formatter = IndentedRichHelpFormatter()
    with pytest.raises(TypeError) as exc_info:
        formatter.format_usage(GENERATE_USAGE)
    assert str(exc_info.value) == "Cannot generate usage if parser is not set"
