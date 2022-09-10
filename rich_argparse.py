# rich_argparse.py
#
#     https://github.com/hamdanal/rich-argparse
#
# Author: Ali Hamdan (ali.hamdan.dev@gmail.com).
#
# Copyright (C) 2022.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Callable, Generator, Iterable

# rich is only used to display help. It is imported inside the functions in order
# not to add delays to command line tools that use this formatter.
if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.padding import Padding
    from rich.style import StyleType
    from rich.table import Table

__all__ = ["RichHelpFormatter"]


class RichHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    group_name_formatter: Callable[[str], str] = str.upper
    styles: dict[str, StyleType] = {
        "argparse.args": "italic cyan",
        "argparse.groups": "bold italic dark_orange",
        "argparse.help": "default",
        "argparse.text": "italic",
        "argparse.syntax": "#E06C75",  # Light Red color used by the one-dark theme
    }
    highlights: list[str] = [
        r"\W(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
        r"`(?P<syntax>[^`]*)`",  # highlight text in backquotes as syntax
    ]

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 38,
        width: int | None = None,
    ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self._root_section.renderables = []

    @property
    def renderables(self) -> list[RenderableType]:
        return self._current_section.renderables  # type: ignore[no-any-return]

    @property
    def _table(self) -> Table:
        return self._current_section.table  # type: ignore[no-any-return]

    def _pad(self, renderable: RenderableType) -> Padding:
        from rich.padding import Padding

        return Padding(renderable, pad=(0, 0, 0, self._current_indent))

    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings or action.nargs == 0:
            action_invocation = super()._format_action_invocation(action)
        else:
            # The default format: `-s ARGS, --long-option ARGS` is very ugly with long
            # option names so I change it to `-s, --long-option ARG` similar to click
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            action_invocation = f"{', '.join(action.option_strings)} {args_string}"

        if self._current_section != self._root_section:
            col1 = self._pad(action_invocation)
            col2 = self._expand_help(action) if action.help else ""
            self._table.add_row(col1, col2)

        return action_invocation

    def add_text(self, text: str | None) -> None:
        from rich.text import Text

        super().add_text(text)

        if text is not argparse.SUPPRESS and text is not None:
            if "%(prog)" in text:
                text = text % {"prog": self._prog}
            self.renderables.append(self._pad(Text.from_markup(text, style="argparse.text")))

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[argparse.Action],
        groups: Iterable[argparse._ArgumentGroup],
        prefix: str | None = None,
    ) -> None:
        from rich.syntax import Syntax

        super().add_usage(usage, actions, groups, prefix)

        if usage is not argparse.SUPPRESS:
            usage_text = self._format_usage(usage, actions, groups, prefix)
            self.renderables.append(
                Syntax(
                    usage_text.strip(),
                    lexer="awk",
                    theme="one-dark",
                    code_width=self._width,
                    background_color="default",
                    word_wrap=True,
                )
            )

    def start_section(self, heading: str | None) -> None:
        from rich.table import Table

        super().start_section(heading)  # sets self._current_section to child section

        self._current_section.renderables = []
        self._current_section.table = Table(
            box=None, pad_edge=False, show_header=False, show_edge=False, highlight=True
        )
        self._table.add_column(
            style="argparse.args", max_width=self._max_help_position, overflow="fold"
        )
        self._table.add_column(
            style="argparse.help", min_width=self._width - self._max_help_position
        )

    def end_section(self) -> None:
        from rich.console import Group

        if self.renderables or self._table.row_count:
            title = type(self).group_name_formatter(self._current_section.heading or "")
            self.renderables.insert(0, f"[argparse.groups]{title}")
            if self._table.row_count:
                self.renderables.append(self._table)
        renderables = self.renderables

        super().end_section()  # sets self._current_section to parent section
        if renderables:
            # append the group to the parent section
            self.renderables.append(Group(*renderables))

    def format_help(self) -> str:
        from rich.console import Console, Group
        from rich.highlighter import RegexHighlighter
        from rich.measure import measure_renderables
        from rich.table import Table
        from rich.theme import Theme

        out = super().format_help()

        # Handle ArgumentParser.add_subparsers() call to get the program name
        all_items = self._root_section.items
        if len(all_items) == 1:
            func, args = all_items[0]
            if func == self._format_usage and args[-1] == "":
                return out  # return the program name instead of printing it

        class ArgparseHighlighter(RegexHighlighter):
            base_style = "argparse."
            highlights = self.highlights

        console = Console(highlighter=ArgparseHighlighter(), theme=Theme(self.styles))
        renderables_list = []
        for r in self.renderables:
            renderables_list.append(r)
            renderables_list.append("")
        if renderables_list:
            renderables_list.pop()
        renderables = Group(*renderables_list)

        def iter_tables(group: Group) -> Generator[Table, None, None]:
            for renderable in group.renderables:
                if isinstance(renderable, Table):
                    yield renderable
                elif isinstance(renderable, Group):
                    yield from iter_tables(renderable)

        col1_width = 0
        for table in iter_tables(renderables):  # compute a unified width of all tables
            cells = table.columns[0].cells
            table_col1_width = measure_renderables(console, console.options, tuple(cells)).maximum
            col1_width = max(col1_width, table_col1_width)
        col1_width = min(col1_width, self._max_help_position)
        col2_width = self._width - col1_width
        for table in iter_tables(renderables):  # apply the unified width
            table.columns[0].width = col1_width
            table.columns[1].width = col2_width

        console.print(renderables, highlight=True)
        return ""


if __name__ == "__main__":
    import sys

    from rich import get_console

    RichHelpFormatter.highlights.append(r"'(?P<help>[^']*)'")  # disable colors inside single quotes
    parser = argparse.ArgumentParser(
        prog="python -m rich_argparse",
        formatter_class=RichHelpFormatter,
        description=(
            "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
            "[link https://docs.python.org/3/library/argparse.html#formatter-class]"
            "argparse's help output[/]."
        ),
        epilog="An epilog :sparkles: at the end ⌛",
    )
    parser.add_argument("-V", "--version", action="version", version="version 0.1.0")
    parser.add_argument(
        "pos-args", nargs="*", help="This is a positional argument that expects zero or more args"
    )
    if sys.version_info[:2] >= (3, 9):
        parser.add_argument(
            "--bool",
            action=argparse.BooleanOptionalAction,
            default=True,
            help=(
                "Starting with python 3.9, you can use `action=argparse.BooleanOptionalAction`. "
                "This action automatically adds an option with a --no- prefix to negate the "
                "action of this flag."
                " This is a very long help text in one line. The formatter takes care of wrapping "
                "the text based on the size of the terminal window."
            ),
        )
    else:
        bool_mutex = parser.add_mutually_exclusive_group()
        bool_mutex.add_argument(
            "--bool, --no-bool",
            action="store_true",
            dest="bool",
            default=True,
            help=(
                "Before python 3.9, you had to implement your own version of a boolean optional "
                "action. The --no- prefix that negates the action of this flag must be added "
                "manually."
                " This is a very long help text in one line. The formatter takes care of wrapping "
                "the text based on the size of the terminal window."
            ),
        )
        bool_mutex.add_argument(
            "--no-bool", action="store_false", dest="bool", help=argparse.SUPPRESS
        )
    parser.add_argument(
        "-s",
        "--long-option",
        metavar="METAVAR",
        help=(
            "If an option takes a value and has short and long options, it is printed as "
            "'-s, --long-option METAVAR' instead of '-s METAVAR, --long-option METAVAR'"
        ),
    )
    parser.add_argument(
        "--syntax",
        help=(
            "Highlighting the help text is managed by the list of regular expressions "
            "`RichHelpFormatter.highlights`. Set to empty list to turn off highlighting."
        ),
    )
    group = parser.add_argument_group("my group")
    group.add_argument("--args", nargs="*", help="Arguments in a custom group")
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

    console = get_console()
    args = parser.parse_args()
    console.print("Got the following arguments on the command line:")
    console.print(vars(args))
