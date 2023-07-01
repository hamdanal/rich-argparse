from __future__ import annotations

import argparse
import sys

from rich_argparse import RichHelpFormatter

RichHelpFormatter.highlights.append(r"(?:^|\s)-{1,2}[\w]+[\w-]* (?P<metavar>METAVAR)\b")
parser = argparse.ArgumentParser(
    prog="python -m rich_argparse",
    formatter_class=RichHelpFormatter,
    description=(
        "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
        "[link https://docs.python.org/3/library/argparse.html#formatter-class]"
        "argparse's help output[/].\n\n"
        "It enables you to use the powers of rich like markup and highlights in your CLI help. "
        "Read below for a glance at available features."
    ),
    epilog=":link: Read more at https://github.com/hamdanal/rich-argparse#usage.",
)
parser.add_argument(
    "formatter-class",
    help=(
        "All you need to make your argparse.ArgumentParser output colorful text like this is to "
        "pass it `formatter_class=RichHelpFormatter` or any of the available variants."
    ),
)
parser.add_argument(
    "styles",
    help=(
        "All the styles used by this formatter are defined in `RichHelpFormatter.styles`. "
        "Modify this dictionary with any rich style to change the look of your CLI's help text."
    ),
)
parser.add_argument(
    "--highlights",
    metavar="REGEXES",
    help=(
        "Highlighting the help text is managed by the list of regular expressions "
        "`RichHelpFormatter.highlights`. Set to empty list to turn off highlighting.\n"
        "See the next two options for default values."
    ),
)
parser.add_argument(
    "--syntax",
    default=RichHelpFormatter.styles["argparse.syntax"],
    help=(
        "Text inside backticks is highlighted using the `argparse.syntax` style "
        "(default: '%(default)s')"
    ),
)
parser.add_argument(
    "-s",
    "--long-option",
    metavar="METAVAR",
    help=(
        "Words that look like --command-line-options are highlighted using the `argparse.args` "
        "style. In addition, this example, adds a highlighter regex for the word 'METAVAR' "
        "following an option for the sake of demonstrating custom highlights.\n"
        "Notice also that if an option takes a value and has short and long options, it is "
        "printed as -s, --long-option METAVAR instead of -s METAVAR, --long-option METAVAR."
    ),
)
group = parser.add_argument_group(
    "more arguments",
    description=(
        "This is a custom group. Group names are [italic]*Title Cased*[/] by default. Use the "
        "`RichHelpFormatter.group_name_formatter` function to change their format."
    ),
)
group.add_argument(
    "--more",
    nargs="*",
    help="This formatter works with subparsers, mutually exclusive groups and hidden arguments.",
)
mutex = group.add_mutually_exclusive_group()
mutex.add_argument(
    "--rich",
    action="store_true",
    help="Rich and poor are mutually exclusive. Choose either one but not both.",
)
mutex.add_argument("--poor", action="store_false", dest="rich", help="Does poor mean --not-rich 😉?")
mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)

if "--generate-rich-argparse-preview" in sys.argv:  # for internal use only
    from rich.console import Console
    from rich.terminal_theme import DIMMED_MONOKAI
    from rich.text import Text

    width = 128
    parser.formatter_class = lambda prog: RichHelpFormatter(prog, width=width)
    text = Text.from_ansi(parser.format_help())
    console = Console(record=True, width=width)
    console.print(text)
    console.save_svg("rich-argparse.svg", title="", theme=DIMMED_MONOKAI)
else:
    parser.print_help()
