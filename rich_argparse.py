from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING, Callable, Generator, Iterable

# rich is only used to display help. It is imported inside the functions in order
# not to add delays to command line tools that use this formatter.
if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
    from rich.style import StyleType
    from rich.text import Span, Text

__all__ = ["RichHelpFormatter"]
_Actions = Iterable[argparse.Action]
_Groups = Iterable[argparse._ArgumentGroup]


class RichHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    group_name_formatter: Callable[[str], str] = str.upper
    styles: dict[str, StyleType] = {
        "argparse.args": "cyan",
        "argparse.groups": "dark_orange",
        "argparse.help": "default",
        "argparse.metavar": "dark_cyan",
        "argparse.syntax": "bold",
        "argparse.text": "default",
    }
    highlights: list[str] = [
        r"(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
        r"`(?P<syntax>[^`]*)`",  # highlight text in backquotes as syntax
    ]

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
    ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self._root_section.rich = []

    class _RichSection:
        def __init__(self, formatter: RichHelpFormatter, heading: str | None) -> None:
            self.formatter = formatter
            if heading is not None:
                heading = f"{type(formatter).group_name_formatter(heading)}:"
            self.heading = heading
            self.description: Text | None = None
            self.actions: list[tuple[Text, Text]] = []

        def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
            from rich.table import Column, Table
            from rich.text import Text

            # assert the empty sections are never rendered
            assert self.description or self.actions
            help_position = min(
                self.formatter._action_max_length + 2, self.formatter._max_help_position
            )
            if self.heading:
                yield Text(self.heading, style="argparse.groups")
            if self.description:
                yield self.description
                if self.actions:
                    yield ""  # add empty line between the description and the arguments
            table = Table.grid(Column(width=help_position), Column(overflow="fold"))
            for action_header, action_help in self.actions:
                if len(action_header) >= help_position - 1:
                    table.add_row(*action_header.divide([help_position]))
                    if action_help:
                        table.add_row(None, action_help)
                else:
                    table.add_row(action_header, action_help)
            yield table

    def _is_root(self) -> bool:
        return self._current_section == self._root_section  # type: ignore[no-any-return]

    def _rich_append(self, r: RenderableType) -> None:
        assert self._is_root(), "can only append in root"
        if isinstance(r, RichHelpFormatter._RichSection) and not r.description and not r.actions:
            return
        if self._root_section.rich:
            self._root_section.rich.append("")
        self._root_section.rich.append(r)

    def _escape_params_and_expand_help(self, action: argparse.Action) -> str:
        from rich.markup import escape

        if not action.help:
            return ""
        params = dict(vars(action), prog=self._prog)
        for name in list(params):  # iterate over a copy because del
            param = params[name]
            if param is argparse.SUPPRESS:
                del params[name]
            elif hasattr(param, "__name__"):
                params[name] = param.__name__
            elif name == "choices" and param is not None:
                params[name] = ", ".join([str(c) for c in param])
        params = {k: escape(str(v)) for k, v in params.items()}
        return self._get_help_string(action) % params  # type: ignore[operator]

    def _format_action_invocation(self, action: argparse.Action) -> str:
        orig_str = super()._format_action_invocation(action)

        if not self._is_root():
            from rich.text import Span, Text

            if not action.option_strings:
                action_invocation = Text(orig_str, spans=[Span(0, len(orig_str), "argparse.args")])
            else:
                styled_options = (Text(opt, style="argparse.args") for opt in action.option_strings)
                action_invocation = Text(", ").join(styled_options)
                if action.nargs != 0:
                    # The default format: `-s ARGS, --long-option ARGS` is very ugly with long
                    # option names so I change it to `-s, --long-option ARG` similar to click
                    default = self._get_default_metavar_for_optional(action)
                    args_string = self._format_args(action, default)
                    action_invocation.append(" ")
                    action_invocation.append(args_string, style="argparse.metavar")

            action_invocation.pad_left(self._current_indent)
            help_text = Text.from_markup(self._escape_params_and_expand_help(action))
            help_text.spans.insert(0, Span(0, len(help_text), style="argparse.help"))
            for regex in self.highlights:
                help_text.highlight_regex(regex, style_prefix="argparse.")
            self._current_section.rich.actions.append((action_invocation, help_text))

        return orig_str

    def _usage_spans(self, text: str, start: int, actions: _Actions) -> Generator[Span, None, None]:
        from rich.text import Span

        options, positionals = [], []
        for action in actions:  # split into options and positionals
            if action.help is argparse.SUPPRESS:
                continue
            if action.option_strings:
                options.append(action)
            else:
                positionals.append(action)
        pos = start
        for action in options:  # start with the options
            if sys.version_info >= (3, 9):  # pragma: >=3.9 cover
                usage = action.format_usage()
                if isinstance(action, argparse.BooleanOptionalAction):
                    for option_string in action.option_strings:
                        start = text.index(option_string, pos)
                        end = start + len(option_string)
                        yield Span(start, end, "argparse.args")
                        pos = end + 1
                    continue
            else:  # pragma: <3.9 cover
                usage = action.option_strings[0]
            start = text.index(usage, pos)
            end = start + len(usage)
            yield Span(start, end, "argparse.args")
            if action.nargs != 0:
                metavar = self._format_args(action, self._get_default_metavar_for_optional(action))
                start = text.index(metavar, end)
                end = start + len(metavar)
                yield Span(start, end, "argparse.metavar")
            pos = end + 1
        for action in positionals:  # positionals come at the end
            usage = self._format_args(action, self._get_default_metavar_for_positional(action))
            start = text.index(usage, pos)
            end = start + len(usage)
            yield Span(start, end, "argparse.args")
            pos = end + 1

    def add_usage(
        self, usage: str | None, actions: _Actions, groups: _Groups, prefix: str | None = None
    ) -> None:
        super().add_usage(usage, actions, groups, prefix)
        if usage is argparse.SUPPRESS:
            return
        from rich.text import Span, Text

        if prefix is None:
            prefix = self._format_usage(usage="", actions=(), groups=(), prefix=None).rstrip("\n")
        prefix_end = ": " if prefix.endswith(": ") else ""
        prefix = prefix[: len(prefix) - len(prefix_end)]
        prefix = type(self).group_name_formatter(prefix) + prefix_end

        spans = [Span(0, len(prefix.rstrip()), "argparse.groups")]
        usage_text = self._format_usage(usage, actions, groups, prefix=prefix).rstrip()
        if usage is None:  # only auto generated usage is coloured
            actions_start = len(prefix) + len(self._prog) + 1
            try:
                actions_spans = list(self._usage_spans(usage_text, actions_start, actions=actions))
            except ValueError:
                actions_spans = []
            spans.extend(actions_spans)
        self._rich_append(Text(usage_text, spans=spans))

    def add_text(self, text: str | None) -> None:
        super().add_text(text)
        if text is not argparse.SUPPRESS and text is not None:
            from rich.markup import escape
            from rich.padding import Padding
            from rich.text import Text

            if "%(prog)" in text:
                text = text % {"prog": escape(self._prog)}
            rich_text = Text.from_markup(text, style="argparse.text")
            for regex in self.highlights:
                rich_text.highlight_regex(regex, style_prefix="argparse.")
            padded_text = Padding.indent(rich_text, self._current_indent)
            if self._is_root():
                self._rich_append(padded_text)
            else:
                self._current_section.rich.description = padded_text

    def start_section(self, heading: str | None) -> None:
        super().start_section(heading)  # sets self._current_section to child section
        self._current_section.rich = self._RichSection(self, heading)

    def end_section(self) -> None:
        section_renderable = self._current_section.rich
        super().end_section()  # sets self._current_section to parent section
        self._rich_append(section_renderable)

    def format_help(self) -> str:
        from rich.console import Console
        from rich.theme import Theme

        super().format_help()
        console = Console(theme=Theme(self.styles), width=self._width)
        with console.capture() as capture:
            for renderable in self._root_section.rich:
                console.print(renderable)
        return "\n".join(line.rstrip() for line in capture.get().split("\n"))


if __name__ == "__main__":
    from rich import print

    RichHelpFormatter.highlights.append(r"(?:^|\s)-{1,2}[\w]+[\w-]* (?P<metavar>METAVAR)\b")
    parser = argparse.ArgumentParser(
        prog="python -m rich_argparse",
        formatter_class=RichHelpFormatter,
        description=(
            "This is a [link https://pypi.org/project/rich]rich[/]-based formatter for "
            "[link https://docs.python.org/3/library/argparse.html#formatter-class]"
            "argparse's help output[/].\n\n"
            "It makes it easy to use the powers of rich like markup and highlights in your CLI "
            "help. For example, the line above contains clickable hyperlinks thanks to rich "
            "\\[link] markup. Read below for a peek at available features."
        ),
        epilog=":link: Read more at https://github.com/hamdanal/rich-argparse#usage.",
    )
    parser.add_argument(
        "formatter-class",
        help=(
            "All you need to make you argparse ArgumentParser output colorful text like this is to "
            "pass it `formatter_class=RichHelpFormatter`."
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
    mutex.add_argument(
        "--poor", action="store_false", dest="rich", help="Does poor mean --not-rich 😉?"
    )
    mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)

    args = parser.parse_args()
    print("Got the following arguments on the command line:")
    print(vars(args))
