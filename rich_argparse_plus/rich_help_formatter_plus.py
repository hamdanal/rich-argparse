from __future__ import annotations

import argparse
import logging
import sys
from os import environ
from pprint import PrettyPrinter
from typing import Callable, Generator, Iterable, List, Tuple

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.style import StyleType
from rich.table import Column, Table
from rich.text import Span, Text
from rich.theme import Theme

from rich_argparse_plus.help_renderer import RENDER_HELP_FORMAT, render_help
from rich_argparse_plus.themes import *

_Actions = Iterable[argparse.Action]
_Groups = Iterable[argparse._ArgumentGroup]


# Formatting constants
DEFAULT_INDENT_INCREMENT = 2
DEFAULT_MAX_HELP_INDENT = 24

# Debug logging
log = logging.getLogger("rich_argparse")
pp = PrettyPrinter(indent=4, sort_dicts=True)

if environ.get("RICH_ARGPARSE_DEBUG"):
    log.addHandler(logging.StreamHandler())
    log.setLevel('DEBUG')



class RichHelpFormatterPlus(argparse.RawTextHelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    theme_name: str = 'default'
    group_name_formatter: Callable[[str], str] = str.upper
    styles: dict[str, StyleType] = ARGPARSE_COLOR_THEMES[theme_name].copy()

    highlights: list[str] = [
        r"(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
        r"`(?P<syntax>[^`]*)`",  # highlight text in backquotes as syntax
    ]

    @classmethod
    def choose_theme(cls, theme_name: str) -> None:
        if theme_name not in ARGPARSE_COLOR_THEMES:
            raise ValueError(f"{theme_name} is not a theme. (Themes: {list(ARGPARSE_COLOR_THEMES.keys())})")

        cls.theme_name = theme_name
        cls.styles = ARGPARSE_COLOR_THEMES[theme_name]

    def __init__(
            self,
            prog: str,
            indent_increment: int = DEFAULT_INDENT_INCREMENT,
            max_help_position: int = DEFAULT_MAX_HELP_INDENT,
            width: int | None = None,
        ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self._root_section.rich = []

    # TODO: separate file
    class _RichSection:
        def __init__(self, formatter: RichHelpFormatterPlus, heading: str | None) -> None:
            self.formatter = formatter
            self.heading = f"{RichHelpFormatterPlus.group_name_formatter(heading)}:" if heading else None
            self.description: Text | None = None
            self.actions: List[Tuple[Text, Text]] = []

        def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
            help_position = min(
                self.formatter._action_max_length + DEFAULT_INDENT_INCREMENT,
                self.formatter._max_help_position
            )

            if self.heading:
                yield Text(self.heading, style=ARGPARSE_GROUPS)

            if self.description:
                yield self.description

                # add empty line between the description and the arguments
                if self.actions:
                    yield ""

            table = Table.grid(Column(width=help_position), Column(overflow="fold"))

            for action_header, action_help in self.actions:
                # Split args that are two long into two cells
                if len(action_header) >= help_position - 1:
                    table.add_row(*action_header.divide([help_position]))

                    if action_help:
                        table.add_row(None, action_help)
                else:
                    table.add_row(action_header, action_help)

            log.debug(f"Help pos: {help_position}, action max len: {self.formatter._action_max_length}, " \
                "max help position: {self.formatter._max_help_position}")
            yield table


    def _is_root(self) -> bool:
        return self._current_section == self._root_section  # type: ignore[no-any-return]

    def _rich_append(self, renderable: RenderableType) -> None:
        assert self._is_root(), "can only append in root"

        if isinstance(renderable, type(self)._RichSection) and not (renderable.description or renderable.actions):
            return

        if self._root_section.rich:
            self._root_section.rich.append("")

        self._root_section.rich.append(renderable)

    def _escape_params_and_expand_help(self, action: argparse.Action) -> Text:
        """Handle %(prog)s etc. substitutions, add defaults, add choices to help text"""
        if not action.help:
            return Text()

        action_vars = vars(action)
        action_vars['prog'] = escape(str(self._prog))
        choices = action_vars.get('choices')
        default_value = action_vars.get('default')

        format_specifiers = {
            k: escape(str(v.__name__ if hasattr(v, "__name__") else v))
            for k, v in action_vars.items()
            if v != argparse.SUPPRESS
        }

        help_string = (self._get_help_string(action) or '') % format_specifiers

        if default_value and default_value != argparse.SUPPRESS:
            help_string += escape(f" (default: {default_value})")
        if choices and isinstance(choices, range):
            help_string += f" (range: {min(choices)}-{max(choices)})"

        return Text.from_markup(help_string)

    def _format_action_invocation(self, action: argparse.Action) -> str:
        orig_str = super()._format_action_invocation(action)
        log.debug(f"orig_str: {orig_str}")
        if self._is_root():
            return orig_str

        if not action.option_strings:
            action_invocation = Text(orig_str, style=ARGPARSE_ARGS)
        else:
            log.debug(f"    OPTION STRINGS: {action.option_strings}")
            styled_options = (Text(opt, style=ARGPARSE_ARGS) for opt in action.option_strings)
            action_invocation = Text(", ").join(styled_options)

            # The default format: `-s ARGS, --long-option ARGS` is very ugly with long
            # option names so I change it to `-s, --long-option ARG` similar to click
            if action.nargs != 0:
                action_invocation.append(" ")
                long_arg_no_prefix = self._get_default_metavar_for_optional(action)
                metavar = self._format_args(action, long_arg_no_prefix)
                action_invocation.append(metavar, style=ARGPARSE_METAVAR)
                log.debug(f"    long_arg: {long_arg_no_prefix}, formatted metavar: {metavar}")

        action_invocation.pad_left(self._current_indent)
        help_text = self._escape_params_and_expand_help(action)
        help_text.spans.insert(0, Span(0, len(help_text), style=ARGPARSE_HELP))
        self._highlight_text(help_text)
        log.debug(f"Help text: {help_text.markup}\n\n")
        self._current_section.rich.actions.append((action_invocation, help_text))
        return orig_str

    def _usage_spans(self, text: str, start: int, actions: _Actions) -> Generator[Span, None, None]:
        options, positionals = [], []
        pos = start

        for action in actions:  # split into options and positionals
            if action.help is argparse.SUPPRESS:
                continue
            if action.option_strings:
                options.append(action)
            else:
                positionals.append(action)

        for action in options:  # start with the options
            if sys.version_info >= (3, 9):  # pragma: >=3.9 cover
                usage = action.format_usage()
                if isinstance(action, argparse.BooleanOptionalAction):
                    for option_string in action.option_strings:
                        start = text.index(option_string, pos)
                        end = start + len(option_string)
                        yield Span(start, end, ARGPARSE_ARGS)
                        pos = end + 1
                    continue
            else:  # pragma: <3.9 cover
                usage = action.option_strings[0]
            start = text.index(usage, pos)
            end = start + len(usage)
            yield Span(start, end, ARGPARSE_ARGS)
            if action.nargs != 0:
                metavar = self._format_args(action, self._get_default_metavar_for_optional(action))
                start = text.index(metavar, end)
                end = start + len(metavar)
                yield Span(start, end, ARGPARSE_METAVAR)
            pos = end + 1
        for action in positionals:  # positionals come at the end
            usage = self._format_args(action, self._get_default_metavar_for_positional(action))
            start = text.index(usage, pos)
            end = start + len(usage)
            yield Span(start, end, ARGPARSE_ARGS)
            pos = end + 1

    def add_usage(
            self,
            usage: str | None,
            actions: _Actions,
            groups: _Groups,
            prefix: str | None = None
        ) -> None:
        super().add_usage(usage, actions, groups, prefix)

        if usage is argparse.SUPPRESS:
            return

        if prefix is None:
            prefix = self._format_usage(usage="", actions=(), groups=(), prefix=None).rstrip("\n")

        prefix_end = ": " if prefix.endswith(": ") else ""
        prefix = prefix[: len(prefix) - len(prefix_end)]
        prefix = type(self).group_name_formatter(prefix) + prefix_end

        spans = [Span(0, len(prefix.rstrip()), ARGPARSE_GROUPS)]
        usage_text = self._format_usage(usage, actions, groups, prefix=prefix).rstrip()
        log.debug(f"usage_text: {usage_text}")

        if usage is None:  # only auto generated usage is coloured
            actions_start = len(prefix) + len(self._prog) + 1
            try:
                spans.extend(list(self._usage_spans(usage_text, actions_start, actions=actions)))
            except ValueError:
                spans.extend([])

        self._rich_append(Text(usage_text, spans=spans))

    def add_text(self, text: str | None) -> None:
        """Add description text."""
        super().add_text(text)

        if text is argparse.SUPPRESS or text is None:
            return
        if "%(prog)" in text:
            text = text % {"prog": escape(self._prog)}

        rich_text = Text.from_markup(text, style=ARGPARSE_DESCRIPTION)
        self._highlight_text(rich_text)
        padded_text = Padding.indent(rich_text, self._current_indent)

        if self._is_root():
            self._rich_append(padded_text)
        else:
            self._current_section.rich.description = padded_text

    def start_section(self, heading: str | None) -> None:
        super().start_section(heading)  # sets self._current_section to child section
        self._current_section.rich = type(self)._RichSection(self, heading)

    def end_section(self) -> None:
        section_renderable = self._current_section.rich
        super().end_section()  # sets self._current_section to parent section
        self._rich_append(section_renderable)

    def format_help(self) -> str:
        super().format_help()
        console_kwargs = {"theme": Theme(self.styles), "width": self._width}
        console = Console(**console_kwargs)

        with console.capture() as capture:
            for renderable in self._root_section.rich:
                console.print(renderable)

        if RENDER_HELP_FORMAT:
            render_help(self)

        return "\n".join(line.rstrip() for line in capture.get().split("\n"))

    def _highlight_text(self, text: Text) -> None:
        for regex in self.highlights:
            text.highlight_regex(regex, style_prefix=STYLE_PREFIX)
