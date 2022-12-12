from __future__ import annotations

import argparse

from rich import print

from . import RichHelpFormatter

RichHelpFormatter.highlights.append(r"(?:^|\s)-{1,2}[\w]+[\w-]* (?P<metavar>METAVAR)\b")
parser = argparse.ArgumentParser(
    prog="python -m rich_argparse",
    formatter_class=RichHelpFormatter,
    description=(
        "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
        "[link https://docs.python.org/3/library/argparse.html#formatter-class]"
        "argparse's help output[/].\n\n"
        "It makes it easy to use the powers of rich like markup and highlights in your CLI "
        "help. For example, the first sentence contains clickable hyperlinks thanks to rich's "
        "\\[link] markup. Read below for a peek at available features."
    ),
    epilog=":link: Read more at https://github.com/hamdanal/rich-argparse#usage.",
)
parser.add_argument(
    "formatter-class",
    help=(
        "All you need to make you argparse ArgumentParser output colorful text like this is to "
        "pass it `formatter_class=RichHelpFormatter` or any of the available variants."
    ),
)
parser.add_argument(
    "styles",
    nargs="*",
    help=(
        "All the styles used by this formatter are defined in the `RichHelpFormatter.styles` "
        "dictionary and customizable. Any rich style can be used."
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
    help="Text inside backtics is highlighted using the `argparse.syntax` style (default: '%(default)s')",
)
parser.add_argument(
    "-s",
    "--long-option",
    metavar="METAVAR",
    help=(
        "If an option takes a value and has short and long options, it is printed as "
        "-s, --long-option METAVAR instead of -s METAVAR, --long-option METAVAR.\n"
        "You can see also that words that look like command line options are highlighted by "
        "deafult. This example, adds a highlighter regex for the word 'METAVAR' following an "
        "option for the sake of demonsting custom highlights."
    ),
)
group = parser.add_argument_group(
    "more options",
    description=(
        "This is a custom group. Group names are upper-cased by default but it can be changed "
        "by setting the `RichHelpFormatter.group_name_formatter` function."
    ),
)
group.add_argument(
    "--others",
    nargs="*",
    help=(
        "This formatter works with subparsers, mutually exclusive groups and hidden arguments. "
        "It also works with other help formatters such as `ArgumentDefaultsHelpFormatter` and "
        "`MetavarTypeHelpFormatter`."
    ),
)
mutex = group.add_mutually_exclusive_group()
mutex.add_argument(
    "--rich",
    action="store_true",
    help="Rich and poor are mutually exclusive. Choose either one but not both.",
)
mutex.add_argument("--poor", action="store_false", dest="rich", help="Does poor mean --not-rich 😉?")
mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)

args = parser.parse_args()
print("Got the following arguments on the command line:")
print(vars(args))
