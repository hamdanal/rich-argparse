# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
from __future__ import annotations

import argparse
import re
import sys
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Iterator

# rich is only used to display help. It is imported inside the functions in order
# not to add delays to command line tools that use this formatter.
if TYPE_CHECKING:
    from argparse import Action, _ArgumentGroup
    from typing_extensions import Self

    from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
    from rich.containers import Lines
    from rich.style import StyleType
    from rich.text import Span, Text

__all__ = [
    "RichHelpFormatter",
    "RawDescriptionRichHelpFormatter",
    "RawTextRichHelpFormatter",
    "ArgumentDefaultsRichHelpFormatter",
    "MetavarTypeRichHelpFormatter",
]


class RichHelpFormatter(argparse.HelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    group_name_formatter: ClassVar[Callable[[str], str]] = str.title
    """A function that formats group names. Defaults to ``str.title``."""
    styles: ClassVar[dict[str, StyleType]] = {
        "argparse.args": "cyan",
        "argparse.groups": "dark_orange",
        "argparse.help": "default",
        "argparse.metavar": "dark_cyan",
        "argparse.syntax": "bold",
        "argparse.text": "default",
        "argparse.prog": "grey50",
    }
    """A dict of rich styles to control the formatter styles.

    The following styles are used:

    - ``argparse.args``: for positional-arguments and --options (e.g "--help")
    - ``argparse.groups``: for group names (e.g. "positional arguments")
    - ``argparse.help``: for argument's help text (e.g. "show this help message and exit")
    - ``argparse.metavar``: for meta variables (e.g. "FILE" in "--file FILE")
    - ``argparse.prog``: for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
    - ``argparse.syntax``: for highlights of back-tick quoted text (e.g. "``` `some text` ```"),
    - ``argparse.text``: for the descriptions and epilog (e.g. "A foo program")
    """
    highlights: ClassVar[list[str]] = [
        r"(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
        r"`(?P<syntax>[^`]*)`",  # highlight `text in backquotes` as syntax
    ]
    """A list of regex patterns to highlight in the help text.

    It is used in the description, epilog, groups descriptions, and arguments' help. By default,
    it highlights ``--words-with-dashes`` with the `argparse.args` style and
    ``` `text in backquotes` ``` with the `argparse.syntax` style.

    To disable highlighting, clear this list (``RichHelpFormatter.highlights.clear()``).
    """
    usage_markup: ClassVar[bool] = False
    """If True, render the usage string passed to ``ArgumentParser(usage=...)`` as markup.

    Defaults to ``False`` meaning the text of the usage will be printed verbatim.

    Note that the auto-generated usage string is always colored.
    """

    _root_section: _Section
    _current_section: _Section

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
    ) -> None:
        from rich.console import Console
        from rich.theme import Theme

        super().__init__(prog, indent_increment, max_help_position, width)
        self.console = Console(theme=Theme(self.styles))

        # https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
        self._printf_style_pattern = re.compile(
            r"""
            %                               # Percent character
            (?:\((?P<mapping>[^)]*)\))      # Mapping key (not optional for argparse)
            (?P<flag>[#0\-+ ])?             # Conversion Flags
            (?P<width>\*|\d+)?              # Minimum field width
            (?P<precision>\.(?:\*?|\d*))?   # Precision
            [hlL]?                          # Length modifier (ignored)
            (?P<format>[diouxXeEfFgGcrsa%]) # Conversion type
            """,
            re.VERBOSE,
        )

    class _Section(argparse.HelpFormatter._Section):  # type: ignore[misc]
        def __init__(
            self, formatter: RichHelpFormatter, parent: Self | None, heading: str | None = None
        ) -> None:
            if heading is not None:
                heading = f"{type(formatter).group_name_formatter(heading)}:"
            super().__init__(formatter, parent, heading)
            self.rich_items: list[RenderableType] = []
            self.rich_actions: list[tuple[Text, Text | None]] = []
            if parent is not None:
                parent.rich_items.append(self)
            if TYPE_CHECKING:  # already assigned in super().__init__ but not present in typeshed
                self.formatter = formatter
                self.heading = heading
                self.parent = parent

        def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
            from rich.text import Text

            # empty section
            if not self.rich_items and not self.rich_actions:
                return
            # root section
            if self is self.formatter._root_section:
                yield from self.rich_items
                return
            # group section
            help_pos = min(self.formatter._action_max_length + 2, self.formatter._max_help_position)
            help_width = max(self.formatter._width - help_pos, 11)
            if self.heading:
                yield Text(self.heading, style="argparse.groups")
            yield from self.rich_items  # (optional) group description
            indent = Text(" " * help_pos)
            for action_header, action_help in self.rich_actions:
                if not action_help:
                    yield action_header  # no help, yield the header and finish
                    continue
                action_help_lines = self.formatter._rich_split_lines(action_help, help_width)
                if len(action_header) > help_pos - 2:
                    yield action_header  # the header is too long, put it on its own line
                    action_header = indent
                action_header.set_length(help_pos)
                action_help_lines[0].rstrip()
                yield action_header + action_help_lines[0]
                for line in action_help_lines[1:]:
                    line.rstrip()
                    yield indent + line
            yield "\n"

    def add_text(self, text: str | None) -> None:
        if text is not argparse.SUPPRESS and text is not None:
            self._current_section.rich_items.append(self._rich_format_text(text))

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[Action],
        groups: Iterable[_ArgumentGroup],
        prefix: str | None = None,
    ) -> None:
        if usage is argparse.SUPPRESS:
            return
        from rich.text import Span, Text

        if prefix is None:
            prefix = self._format_usage(usage="", actions=(), groups=(), prefix=None).rstrip("\n")
        prefix_end = ": " if prefix.endswith(": ") else ""
        prefix = prefix[: len(prefix) - len(prefix_end)]
        prefix = type(self).group_name_formatter(prefix) + prefix_end

        usage_spans = [Span(0, len(prefix.rstrip()), "argparse.groups")]
        usage_text = self._format_usage(usage, actions, groups, prefix=prefix)
        if usage is None:  # get colour spans for generated usage
            prog = f"{self._prog}"
            if actions:
                prog_start = usage_text.index(prog, len(prefix))
                usage_spans.append(Span(prog_start, prog_start + len(prog), "argparse.prog"))
            actions_start = len(prefix) + len(prog) + 1
            try:
                spans = list(self._rich_usage_spans(usage_text, actions_start, actions=actions))
            except ValueError:
                spans = []
            usage_spans.extend(spans)
            rich_usage = Text(usage_text)
        elif self.usage_markup:  # treat user provided usage as markup
            usage_spans.extend(self._rich_prog_spans(prefix + Text.from_markup(usage).plain))
            rich_usage = Text.from_markup(usage_text)
            usage_spans.extend(rich_usage.spans)
            rich_usage.spans.clear()
        else:  # treat user provided usage as plain text
            usage_spans.extend(self._rich_prog_spans(prefix + usage))
            rich_usage = Text(usage_text)
        rich_usage.spans.extend(usage_spans)
        self._root_section.rich_items.append(rich_usage)

    def add_argument(self, action: Action) -> None:
        super().add_argument(action)
        if action.help is not argparse.SUPPRESS:
            self._current_section.rich_actions.extend(self._rich_format_action(action))

    def format_help(self) -> str:
        with self.console.capture() as capture:
            self.console.print(self._root_section, highlight=False, soft_wrap=True)
        help = capture.get()
        if help:
            help = self._long_break_matcher.sub("\n\n", help).rstrip() + "\n"
        return help

    # ===============
    # Utility methods
    # ===============
    def _rich_prog_spans(self, usage: str) -> Iterator[Span]:
        from rich.text import Span

        if "%(prog)" not in usage:
            return
        params = {"prog": self._prog}
        formatted_usage = ""
        last = 0
        for m in self._printf_style_pattern.finditer(usage):
            start, end = m.span()
            formatted_usage += usage[last:start]
            sub = usage[start:end] % params
            prog_start = len(formatted_usage)
            prog_end = prog_start + len(sub)
            formatted_usage += sub
            last = end
            yield Span(prog_start, prog_end, "argparse.prog")

    def _rich_usage_spans(self, text: str, start: int, actions: Iterable[Action]) -> Iterator[Span]:
        from rich.text import Span

        options: list[Action] = []
        positionals: list[Action] = []
        for action in actions:
            if action.help is not argparse.SUPPRESS:
                options.append(action) if action.option_strings else positionals.append(action)
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

    def _rich_whitespace_sub(self, text: Text) -> Text:
        # do this `self._whitespace_matcher.sub(' ', text).strip()` but text is Text
        spans = [m.span() for m in self._whitespace_matcher.finditer(text.plain)]
        for start, end in reversed(spans):
            if end - start > 1:  # slow path
                space = text[start : start + 1]
                space.plain = " "
                text = text[:start] + space + text[end:]
            else:  # performance shortcut
                text.plain = text.plain[:start] + " " + text.plain[end:]
        # Text has no strip method yet
        lstrip_at = len(text.plain) - len(text.plain.lstrip())
        if lstrip_at:
            text = text[lstrip_at:]
        text.rstrip()
        return text

    # =====================================
    # Rich version of HelpFormatter methods
    # =====================================
    def _rich_expand_help(self, action: Action) -> Text:
        from rich.markup import escape
        from rich.text import Text

        params = dict(vars(action), prog=self._prog)
        for name in list(params):
            if params[name] is argparse.SUPPRESS:
                del params[name]
            elif hasattr(params[name], "__name__"):
                params[name] = params[name].__name__
        if params.get("choices") is not None:
            params["choices"] = ", ".join([str(c) for c in params["choices"]])
        help_string = self._get_help_string(action)
        assert help_string is not None
        help_string % params  # pyright: ignore[reportUnusedExpression] # raise ValueError if needed
        parts = []
        last = 0
        for m in self._printf_style_pattern.finditer(help_string):
            start, end = m.span()
            parts.append(help_string[last:start])
            parts.append(escape(help_string[start:end] % params))
            last = end
        parts.append(help_string[last:])
        rich_help = Text.from_markup("".join(parts), style="argparse.help")
        for highlight in self.highlights:
            rich_help.highlight_regex(highlight, style_prefix="argparse.")
        return rich_help

    def _rich_format_text(self, text: str) -> Text:
        from rich.markup import escape
        from rich.text import Text

        if "%(prog)" in text:
            text = text % {"prog": escape(self._prog)}
        rich_text = Text.from_markup(text, style="argparse.text")
        for highlight in self.highlights:
            rich_text.highlight_regex(highlight, style_prefix="argparse.")
        text_width = max(self._width - self._current_indent * 2, 11)
        indent = Text(" " * self._current_indent)
        return self._rich_fill_text(rich_text, text_width, indent)

    def _rich_format_action(self, action: Action) -> Iterator[tuple[Text, Text | None]]:
        header = self._rich_format_action_invocation(action)
        header.pad_left(self._current_indent)
        help = self._rich_expand_help(action) if action.help and action.help.strip() else None
        yield header, help
        for subaction in self._iter_indented_subactions(action):
            yield from self._rich_format_action(subaction)

    def _rich_format_action_invocation(self, action: Action) -> Text:
        from rich.text import Text

        if not action.option_strings:
            return Text().append(self._format_action_invocation(action), style="argparse.args")
        else:
            action_header = Text(", ").join(Text(o, "argparse.args") for o in action.option_strings)
            if action.nargs != 0:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                action_header.append_tokens(((" ", None), (args_string, "argparse.metavar")))
            return action_header

    def _rich_split_lines(self, text: Text, width: int) -> Lines:
        return self._rich_whitespace_sub(text).wrap(self.console, width)

    def _rich_fill_text(self, text: Text, width: int, indent: Text) -> Text:
        lines = self._rich_whitespace_sub(text).wrap(self.console, width)
        return type(text)("\n").join(indent + line for line in lines) + "\n\n"


class RawDescriptionRichHelpFormatter(RichHelpFormatter):
    """Rich help message formatter which retains any formatting in descriptions."""

    def _rich_fill_text(self, text: Text, width: int, indent: Text) -> Text:
        return type(text)("\n").join(indent + line for line in text.split()) + "\n\n"


class RawTextRichHelpFormatter(RawDescriptionRichHelpFormatter):
    """Rich help message formatter which retains formatting of all help text."""

    def _rich_split_lines(self, text: Text, width: int) -> Lines:
        return text.split()


class ArgumentDefaultsRichHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, RichHelpFormatter):
    """Rich help message formatter which adds default values to argument help."""


class MetavarTypeRichHelpFormatter(argparse.MetavarTypeHelpFormatter, RichHelpFormatter):
    """Rich help message formatter which uses the argument 'type' as the default
    metavar value (instead of the argument 'dest').
    """


if __name__ == "__main__":
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
    mutex.add_argument(
        "--poor", action="store_false", dest="rich", help="Does poor mean --not-rich 😉?"
    )
    mutex.add_argument("--not-rich", action="store_false", dest="rich", help=argparse.SUPPRESS)

    if "--generate-rich-argparse-preview" in sys.argv:  # for internal use only
        from rich.console import Console  # noqa: F811
        from rich.terminal_theme import DIMMED_MONOKAI
        from rich.text import Text  # noqa: F811

        width = 128
        parser.formatter_class = lambda prog: RichHelpFormatter(prog, width=width)
        text = Text.from_ansi(parser.format_help())
        console = Console(record=True, width=width)
        console.print(text)
        console.save_svg("rich-argparse.svg", title="", theme=DIMMED_MONOKAI)
    else:
        parser.print_help()
