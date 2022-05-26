# rich_argparse.py
#
#     https://github.com/hamdanal/rich_argparse
#
# Author: Ali Hamdan (ali.hamdan.dev@gmail.com).
#
# Copyright (C) 2022.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.

import argparse
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Optional

# rich is only used to display help. It is imported inside the functions in order
# not to add delays to command line tools that use this formatter.
if TYPE_CHECKING:
    from rich.console import RenderableType
    from rich.style import StyleType
    from rich.syntax import Syntax
    from rich.table import Table

__all__ = ["RichHelpFormatter"]


class RichHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    first_column_min_width: int = 18
    first_column_max_width: int = 38
    second_column_max_width: int = 78
    insert_empty_lines_between_args: bool = False
    highlight_help: bool = False
    styles: Dict[str, "StyleType"] = {
        "argparse.args": "italic cyan",
        "argparse.groups": "bold italic dark_orange",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._width = min(self._width, self.first_column_max_width + self.second_column_max_width)
        self._renderables: list[RenderableType] = []

    def _rich_table_factory(self, heading: Optional[str]) -> "Table":
        from rich.table import Table

        if heading is None or heading is argparse.SUPPRESS:
            title = ""
        else:
            title = heading.upper()
        table = Table(
            title=title,
            box=None,
            title_justify="left",
            title_style="argparse.groups",
            show_header=False,
            show_footer=False,
            show_edge=False,
            show_lines=False,
            highlight=self.highlight_help,
            leading=self.insert_empty_lines_between_args,
        )
        table.add_column(
            "args",
            style="argparse.args",
            min_width=self.first_column_min_width,
            max_width=self.first_column_max_width,
            overflow="fold",
        )
        table.add_column("help", style="none", max_width=self.second_column_max_width)
        self._renderables.append(table)
        return table

    def _create_usage_renderable(self, usage: str) -> "Syntax":
        from rich.syntax import Syntax

        return Syntax(
            usage.strip(),
            lexer="awk",
            theme="one-dark",
            code_width=self._width,
            background_color="default",
        )

    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings or action.nargs == 0:
            action_invocation = super()._format_action_invocation(action)
        else:
            # The default format: `-s ARGS, --long-option ARGS` is very ugly with long
            # option names so I change it to `-s, --long-option ARG` similar to click
            default = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, default)
            action_invocation = f"{', '.join(action.option_strings)} {args_string}"

        # add a row to the current section's table
        if self._current_section != self._root_section:
            self._current_section.table.add_row(action_invocation, self._get_help_string(action))

        return action_invocation

    def _add_item(self, func: Callable[..., str], args: Iterable[Any]) -> None:
        # disable _add_item, self._renderables handles all necessary data
        pass

    def add_text(self, text: Optional[str]) -> None:
        if text is not argparse.SUPPRESS and text is not None:
            self._renderables.append(text)

    def add_usage(
        self,
        usage: Optional[str],
        actions: Iterable[argparse.Action],
        groups: Iterable[argparse._ArgumentGroup],
        prefix: Optional[str] = None,
    ) -> None:
        if usage is not argparse.SUPPRESS:
            usage = self._format_usage(usage, actions, groups, prefix)  # type: ignore[arg-type]
            self._renderables.append(self._create_usage_renderable(usage))

    def start_section(self, heading: Optional[str]) -> None:
        super().start_section(heading)
        # create a table and attach it to the new section (except for the root section)
        if self._current_section != self._root_section:
            self._current_section.table = self._rich_table_factory(heading)

    def format_help(self) -> str:
        from rich.console import Console
        from rich.table import Table
        from rich.theme import Theme

        # call the parent class method, it will create the renderables
        super().format_help()

        # compute a unified width of the first column of all tables
        col1_width = self.first_column_min_width
        for renderable in self._renderables:
            if not isinstance(renderable, Table):
                continue
            col1_width = max(col1_width, len(max(renderable.columns[0].cells, key=len, default="")))
        col1_width = min(col1_width, self.first_column_max_width)

        # print renderables
        console = Console(theme=Theme(self.styles))
        for renderable in self._renderables:
            if isinstance(renderable, Table):
                if not renderable.row_count:
                    continue
                renderable.columns[0].width = col1_width
            console.print(renderable, highlight=True)
            console.print()
        return ""


if __name__ == "__main__":
    import sys

    from rich import get_console

    RichHelpFormatter.highlight_help = True

    parser = argparse.ArgumentParser(
        formatter_class=RichHelpFormatter,
        description=(
            "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
            "[link https://docs.python.org/3/library/argparse.html#formatter-class]argparse[/]'s "
            "help output."
        ),
        epilog="An epilog :sparkles: at the end :hourglass_done:",
    )
    parser.add_argument("-V", "--version", action="version", version="version 0.1.0")
    parser.add_argument(
        "pos-args",
        nargs="*",
        help="This is a positional argument that expects zero or more args",
    )
    if sys.version_info > (3, 9):
        parser.add_argument(
            "--bool",
            action=argparse.BooleanOptionalAction,
            default=True,
            help=(
                "This is a boolean optional action. It automatically adds an option with a "
                "[italic red]--no-[/red italic] prefix to negate the action of this options. "
                "You can see how this really log line is clearly printed even if you resize "
                "your window."
            ),
        )
    parser.add_argument(
        "-l",
        "--long-option",
        metavar="HINT",
        help=(
            "If an option takes a value and has short and long options, it is printed "
            "as [argparse.args]-l, --long-option HINT[/]"
        ),
    )
    parser.add_argument(
        "-s",
        "--syntax",
        help=(
            "Highlighting the help text is off by default. You have to set "
            "RichHelpFormatter.highlight_help=True to see highlighting in the text"
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
        "--poor",
        action="store_false",
        dest="rich",
        help="Does poor mean [argparse.args]--not-rich[/] :wink:?",
    )
    mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)

    console = get_console()
    args = parser.parse_args()
    console.print(vars(args))
