# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
from __future__ import annotations

import argparse
import re
import sys

import rich_argparse._lazy_rich as r
from rich_argparse._common import _HIGHLIGHTS, _fix_legacy_win_text, _rich_fill, _rich_wrap

TYPE_CHECKING = False
if TYPE_CHECKING:
    from argparse import Action, ArgumentParser, Namespace, _MutuallyExclusiveGroup
    from collections.abc import Callable, Iterable, Iterator, MutableMapping, Sequence
    from typing import Any, ClassVar
    from typing_extensions import Self
del TYPE_CHECKING

__all__ = [
    "RichHelpFormatter",
    "RawDescriptionRichHelpFormatter",
    "RawTextRichHelpFormatter",
    "ArgumentDefaultsRichHelpFormatter",
    "MetavarTypeRichHelpFormatter",
    "HelpPreviewAction",
]


class RichHelpFormatter(argparse.HelpFormatter):
    """An argparse HelpFormatter class that renders using rich."""

    group_name_formatter: ClassVar[Callable[[str], str]] = str.title
    """A function that formats group names. Defaults to ``str.title``."""
    styles: ClassVar[dict[str, r.StyleType]] = {
        "argparse.args": "cyan",
        "argparse.groups": "dark_orange",
        "argparse.help": "default",
        "argparse.metavar": "dark_cyan",
        "argparse.syntax": "bold",
        "argparse.text": "default",
        "argparse.prog": "grey50",
        "argparse.default": "italic",
    }
    """A dict of rich styles to control the formatter styles.

    The following styles are used:

    - ``argparse.args``: for positional-arguments and --options (e.g "--help")
    - ``argparse.groups``: for group names (e.g. "positional arguments")
    - ``argparse.help``: for argument's help text (e.g. "show this help message and exit")
    - ``argparse.metavar``: for meta variables (e.g. "FILE" in "--file FILE")
    - ``argparse.prog``: for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
    - ``argparse.syntax``: for highlights of back-tick quoted text (e.g. "``` `some text` ```")
    - ``argparse.text``: for the descriptions and epilog (e.g. "A foo program")
    - ``argparse.default``: for %(default)s in the help (e.g. "Value" in "(default: Value)")
    """
    highlights: ClassVar[list[str]] = _HIGHLIGHTS[:]
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
    help_markup: ClassVar[bool] = True
    """If True (default), render the help message of arguments as console markup."""
    text_markup: ClassVar[bool] = True
    """If True (default), render the descriptions and epilog as console markup."""

    _root_section: _Section
    _current_section: _Section

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
        console: r.Console | None = None,
    ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self._console = console

        # https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
        self._printf_style_pattern = re.compile(
            r"""
            %                               # Percent character
            (?:\((?P<mapping>[^)]*)\))?     # Mapping key
            (?P<flag>[#0\-+ ])?             # Conversion Flags
            (?P<width>\*|\d+)?              # Minimum field width
            (?P<precision>\.(?:\*?|\d*))?   # Precision
            [hlL]?                          # Length modifier (ignored)
            (?P<format>[diouxXeEfFgGcrsa%]) # Conversion type
            """,
            re.VERBOSE,
        )

    @property
    def console(self) -> r.Console:
        if self._console is None:
            self._console = r.Console()
        return self._console

    @console.setter
    def console(self, console: r.Console) -> None:
        self._console = console

    class _Section(argparse.HelpFormatter._Section):
        def __init__(
            self, formatter: RichHelpFormatter, parent: Self | None, heading: str | None = None
        ) -> None:
            if heading is not argparse.SUPPRESS and heading is not None:
                heading = f"{type(formatter).group_name_formatter(heading)}:"
            super().__init__(formatter, parent, heading)
            self.formatter: RichHelpFormatter
            self.rich_items: list[r.RenderableType] = []
            self.rich_actions: list[tuple[r.Text, r.Text | None]] = []
            if parent is not None:
                parent.rich_items.append(self)

        def _render_items(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
            if not self.rich_items:
                return
            generated_options = options.update(no_wrap=True, overflow="ignore")
            new_line = r.Segment.line()
            for item in self.rich_items:
                if isinstance(item, RichHelpFormatter._Section):
                    yield from console.render(item, options)
                elif isinstance(item, r.Padding):  # user added rich renderable
                    yield from console.render(item, options)
                    yield new_line
                else:  # argparse generated rich renderable
                    yield from console.render(item, generated_options)

        def _render_actions(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
            if not self.rich_actions:
                return
            options = options.update(no_wrap=True, overflow="ignore")
            help_pos = min(self.formatter._action_max_length + 2, self.formatter._max_help_position)
            help_width = max(self.formatter._width - help_pos, 11)
            indent = r.Text(" " * help_pos)
            for action_header, action_help in self.rich_actions:
                if not action_help:
                    # no help, yield the header and finish
                    yield from console.render(action_header, options)
                    continue
                action_help_lines = self.formatter._rich_split_lines(action_help, help_width)
                if len(action_header) > help_pos - 2:
                    # the header is too long, put it on its own line
                    yield from console.render(action_header, options)
                    action_header = indent
                action_header.set_length(help_pos)
                action_help_lines[0].rstrip()
                yield from console.render(action_header + action_help_lines[0], options)
                for line in action_help_lines[1:]:
                    line.rstrip()
                    yield from console.render(indent + line, options)
            yield ""

        def __rich_console__(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
            if not self.rich_items and not self.rich_actions:
                return  # empty section
            if self.heading is not argparse.SUPPRESS and self.heading is not None:
                yield r.Text(self.heading, style="argparse.groups")
            yield from self._render_items(console, options)
            yield from self._render_actions(console, options)

    def __rich_console__(self, console: r.Console, options: r.ConsoleOptions) -> r.RenderResult:
        with console.use_theme(r.Theme(self.styles)):
            root = console.render(self._root_section, options.update_width(self._width))
            new_line = r.Segment.line()
            add_empty_line = False
            for line_segments in r.Segment.split_lines(root):
                for i, segment in enumerate(reversed(line_segments), start=1):
                    stripped = segment.text.rstrip()
                    if stripped:
                        if add_empty_line:
                            yield new_line
                        add_empty_line = False
                        yield from line_segments[:-i]
                        yield r.Segment(stripped, style=segment.style, control=segment.control)
                        yield new_line
                        break
                else:  # empty line
                    add_empty_line = True

    def add_text(self, text: str | None) -> None:
        if text is argparse.SUPPRESS or text is None:
            return
        elif isinstance(text, str):
            self._current_section.rich_items.append(self._rich_format_text(text))
        else:
            self.add_renderable(text)

    def add_renderable(self, renderable: r.RenderableType) -> None:
        padded = r.Padding.indent(renderable, self._current_indent)
        self._current_section.rich_items.append(padded)

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[Action],
        groups: Iterable[_MutuallyExclusiveGroup],
        prefix: str | None = None,
    ) -> None:
        if usage is argparse.SUPPRESS:
            return
        if prefix is None:
            prefix = self._format_usage(usage="", actions=(), groups=(), prefix=None).rstrip("\n")
        prefix_end = ": " if prefix.endswith(": ") else ""
        prefix = prefix[: len(prefix) - len(prefix_end)]
        prefix = r.strip_control_codes(type(self).group_name_formatter(prefix)) + prefix_end

        usage_spans = [r.Span(0, len(prefix.rstrip()), "argparse.groups")]
        usage_text = r.strip_control_codes(
            self._format_usage(usage, actions, groups, prefix=prefix)
        )
        if usage is None:  # get colour spans for generated usage
            prog = r.strip_control_codes(f"{self._prog}")
            if actions:
                prog_start = usage_text.index(prog, len(prefix))
                usage_spans.append(r.Span(prog_start, prog_start + len(prog), "argparse.prog"))
            actions_start = len(prefix) + len(prog) + 1
            try:
                spans = list(self._rich_usage_spans(usage_text, actions_start, actions=actions))
            except ValueError:
                spans = []
            usage_spans.extend(spans)
            rich_usage = r.Text(usage_text)
        elif self.usage_markup:  # treat user provided usage as markup
            usage_spans.extend(self._rich_prog_spans(prefix + r.Text.from_markup(usage).plain))
            rich_usage = r.Text.from_markup(usage_text)
            usage_spans.extend(rich_usage.spans)
            rich_usage.spans.clear()
        else:  # treat user provided usage as plain text
            usage_spans.extend(self._rich_prog_spans(prefix + usage))
            rich_usage = r.Text(usage_text)
        rich_usage.spans.extend(usage_spans)
        self._root_section.rich_items.append(rich_usage)

    def add_argument(self, action: Action) -> None:
        super().add_argument(action)
        if action.help is not argparse.SUPPRESS:
            self._current_section.rich_actions.extend(self._rich_format_action(action))

    def format_help(self) -> str:
        with self.console.capture() as capture:
            self.console.print(self, crop=False)
        return _fix_legacy_win_text(self.console, capture.get())

    # ===============
    # Utility methods
    # ===============
    def _rich_prog_spans(self, usage: str) -> Iterator[r.Span]:
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
            yield r.Span(prog_start, prog_end, "argparse.prog")

    def _rich_usage_spans(
        self, text: str, start: int, actions: Iterable[Action]
    ) -> Iterator[r.Span]:
        options: list[Action] = []
        positionals: list[Action] = []
        for action in actions:
            if action.help is not argparse.SUPPRESS:
                options.append(action) if action.option_strings else positionals.append(action)
        pos = start

        def find_span(_string: str) -> tuple[int, int]:
            stripped = r.strip_control_codes(_string)
            _start = text.index(stripped, pos)
            _end = _start + len(stripped)
            return _start, _end

        for action in options:  # start with the options
            if sys.version_info >= (3, 9):  # pragma: >=3.9 cover
                usage = action.format_usage()
                if isinstance(action, argparse.BooleanOptionalAction):
                    for option_string in action.option_strings:
                        start, end = find_span(option_string)
                        yield r.Span(start, end, "argparse.args")
                        pos = end + 1
                    continue
            else:  # pragma: <3.9 cover
                usage = action.option_strings[0]
            start, end = find_span(usage)
            yield r.Span(start, end, "argparse.args")
            if action.nargs != 0:
                metavar = self._format_args(action, self._get_default_metavar_for_optional(action))
                start, end = find_span(metavar)
                yield r.Span(start, end, "argparse.metavar")
            pos = end + 1
        for action in positionals:  # positionals come at the end
            metavar = self._get_default_metavar_for_positional(action)
            metavar_tuple = self._metavar_formatter(action, metavar)(1)
            usage = metavar_tuple[0]
            if isinstance(action.nargs, int):
                nargs = action.nargs
            elif action.nargs in (argparse.REMAINDER, argparse.SUPPRESS):
                nargs = 0
            elif action.nargs in (None, argparse.OPTIONAL, argparse.PARSER):
                nargs = 1
            elif action.nargs == argparse.ZERO_OR_MORE:
                if sys.version_info >= (3, 9):  # pragma: >=3.9 cover
                    nargs = 2 if len(metavar_tuple) == 2 else 1
                else:  # pragma: <3.9 cover
                    nargs = 2
            elif action.nargs == argparse.ONE_OR_MORE:
                nargs = 2
            else:  # pragma: no cover
                # unknown nargs, fallback to coloring the whole thing
                usage = self._format_args(action, metavar)
                nargs = 1
            for _ in range(nargs):
                start, end = find_span(usage)
                yield r.Span(start, end, "argparse.args")
                pos = end + 1

    def _rich_whitespace_sub(self, text: r.Text) -> r.Text:
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
    def _rich_expand_help(self, action: Action) -> r.Text:
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
        # raise ValueError if needed
        help_string % params  # pyright: ignore[reportUnusedExpression]
        parts = []
        last = 0
        for m in self._printf_style_pattern.finditer(help_string):
            start, end = m.span()
            parts.append(help_string[last:start])
            sub = r.escape(help_string[start:end] % params)
            if m.group("mapping") == "default":
                sub = f"[argparse.default]{sub}[/argparse.default]"
            parts.append(sub)
            last = end
        parts.append(help_string[last:])
        rich_help = (
            r.Text.from_markup("".join(parts), style="argparse.help")
            if self.help_markup
            else r.Text("".join(parts), style="argparse.help")
        )
        for highlight in self.highlights:
            rich_help.highlight_regex(highlight, style_prefix="argparse.")
        return rich_help

    def _rich_format_text(self, text: str) -> r.Text:
        if "%(prog)" in text:
            text = text % {"prog": r.escape(self._prog)}
        rich_text = (
            r.Text.from_markup(text, style="argparse.text")
            if self.text_markup
            else r.Text(text, style="argparse.text")
        )
        for highlight in self.highlights:
            rich_text.highlight_regex(highlight, style_prefix="argparse.")
        text_width = max(self._width - self._current_indent * 2, 11)
        indent = r.Text(" " * self._current_indent)
        return self._rich_fill_text(rich_text, text_width, indent)

    def _rich_format_action(self, action: Action) -> Iterator[tuple[r.Text, r.Text | None]]:
        header = self._rich_format_action_invocation(action)
        header.pad_left(self._current_indent)
        help = self._rich_expand_help(action) if action.help and action.help.strip() else None
        yield header, help
        for subaction in self._iter_indented_subactions(action):
            yield from self._rich_format_action(subaction)

    def _rich_format_action_invocation(self, action: Action) -> r.Text:
        if not action.option_strings:
            return r.Text().append(self._format_action_invocation(action), style="argparse.args")
        else:
            action_header = r.Text(", ").join(
                r.Text(o, "argparse.args") for o in action.option_strings
            )
            if action.nargs != 0:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                action_header.append(" ").append(args_string, style="argparse.metavar")
            return action_header

    def _rich_split_lines(self, text: r.Text, width: int) -> r.Lines:
        return _rich_wrap(self.console, self._rich_whitespace_sub(text), width)

    def _rich_fill_text(self, text: r.Text, width: int, indent: r.Text) -> r.Text:
        return _rich_fill(self.console, self._rich_whitespace_sub(text), width, indent) + "\n\n"


class RawDescriptionRichHelpFormatter(RichHelpFormatter):
    """Rich help message formatter which retains any formatting in descriptions."""

    def _rich_fill_text(self, text: r.Text, width: int, indent: r.Text) -> r.Text:
        return r.Text("\n").join(indent + line for line in text.split()) + "\n\n"


class RawTextRichHelpFormatter(RawDescriptionRichHelpFormatter):
    """Rich help message formatter which retains formatting of all help text."""

    def _rich_split_lines(self, text: r.Text, width: int) -> r.Lines:
        return text.split()


class ArgumentDefaultsRichHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, RichHelpFormatter):
    """Rich help message formatter which adds default values to argument help."""


class MetavarTypeRichHelpFormatter(argparse.MetavarTypeHelpFormatter, RichHelpFormatter):
    """Rich help message formatter which uses the argument 'type' as the default
    metavar value (instead of the argument 'dest').
    """


class HelpPreviewAction(argparse.Action):
    """Action that renders the help to SVG, HTML, or text file and exits."""

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str = argparse.SUPPRESS,
        default: str = argparse.SUPPRESS,
        help: str = argparse.SUPPRESS,
        *,
        path: str | None = None,
        export_kwds: MutableMapping[str, Any] | None = None,
    ) -> None:
        super().__init__(option_strings, dest, nargs="?", const=path, default=default, help=help)
        self.export_kwds = export_kwds or {}

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        path = values
        if path is None:
            parser.exit(1, "error: help preview path is not provided\n")
        if not isinstance(path, str):
            parser.exit(1, "error: help preview path must be a string\n")
        if not path.endswith((".svg", ".html", ".txt")):
            parser.exit(1, "error: help preview path must end with .svg, .html, or .txt\n")

        text = r.Text.from_ansi(parser.format_help())
        console = r.Console(record=True)
        with console.capture():
            console.print(text, crop=False)

        if path.endswith(".svg"):
            self.export_kwds.setdefault("title", "")
            console.save_svg(path, **self.export_kwds)
        elif path.endswith(".html"):
            console.save_html(path, **self.export_kwds)
        elif path.endswith(".txt"):
            console.save_text(path, **self.export_kwds)
        else:
            raise AssertionError("unreachable")
        parser.exit(0, f"Help preview saved to {path}\n")
