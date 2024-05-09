from __future__ import annotations

import argparse
import sys

from rich.terminal_theme import DIMMED_MONOKAI

from rich_argparse import HelpPreviewAction, RichHelpFormatter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python -m rich_argparse",
        formatter_class=RichHelpFormatter,
        description=(
            "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
            "[link https://docs.python.org/3/library/argparse.html#formatter-class]"
            "argparse's help output[/].\n\n"
            "It enables you to use the powers of rich like markup and highlights in your CLI help. "
        ),
        epilog=":link: Read more at https://github.com/hamdanal/rich-argparse#usage.",
    )
    parser.add_argument(
        "formatter-class",
        help=(
            "Simply pass `formatter_class=RichHelpFormatter` to the argument parser to get a "
            "colorful help like this."
        ),
    )
    parser.add_argument(
        "styles",
        help="Customize your CLI's help with the `RichHelpFormatter.styles` dictionary.",
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
            "(default: %(default)r)"
        ),
    )
    parser.add_argument(
        "-o",
        "--option",
        metavar="METAVAR",
        help="Text that looks like an --option is highlighted using the `argparse.args` style.",
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
    mutex.add_argument(
        "--poor", action="store_false", dest="rich", help="Does poor mean --not-rich 😉?"
    )
    mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)
    parser.add_argument(
        "--generate-rich-argparse-preview",
        action=HelpPreviewAction,
        path="rich-argparse.svg",
        export_kwds={"theme": DIMMED_MONOKAI},
    )
    # There is no program to run, always print help (except for the hidden --generate option)
    # You probably don't want to do this in your own code.
    if any(arg.startswith("--generate") for arg in sys.argv):
        parser.parse_args()
    else:
        parser.print_help()
