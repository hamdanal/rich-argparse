# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
from __future__ import annotations

from rich_argparse._optparse import (
    GENERATE_USAGE,
    IndentedRichHelpFormatter,
    RichHelpFormatter,
    TitledRichHelpFormatter,
)

__all__ = [
    "RichHelpFormatter",
    "IndentedRichHelpFormatter",
    "TitledRichHelpFormatter",
    "GENERATE_USAGE",
]


if __name__ == "__main__":
    import optparse

    IndentedRichHelpFormatter.highlights.append(r"(?P<metavar>\bregexes\b)")
    parser = optparse.OptionParser(
        description="I [link https://pypi.org/project/rich]rich[/]ify:trade_mark: optparse help.",
        formatter=IndentedRichHelpFormatter(),
        prog="python -m rich_arparse.optparse",
        epilog=":link: https://github.com/hamdanal/rich-argparse#optparse-support.",
        usage=GENERATE_USAGE,
    )
    parser.add_option("--formatter", metavar="rich", help="A piece of :cake: isn't it? :wink:")
    parser.add_option(
        "--styles", metavar="yours", help="Not your style? No biggie, change it :sunglasses:"
    )
    parser.add_option(
        "--highlights",
        action="store_true",
        help=":clap: --highlight :clap: all :clap: the :clap: regexes :clap:",
    )
    parser.add_option(
        "--syntax", action="store_true", help="`backquotes` may be bold, but they are :muscle:"
    )
    parser.add_option(
        "-s", "--long", metavar="METAVAR", help="That's a lot of metavars for an option!"
    )

    group = parser.add_option_group("Magic", description=":sparkles: :sparkles: :sparkles:")
    group.add_option(
        "--treasure", action="store_false", help="Mmm, did you find the --hidden :gem:?"
    )
    group.add_option("--hidden", action="store_false", dest="treasure", help=optparse.SUPPRESS_HELP)
    parser.print_help()
