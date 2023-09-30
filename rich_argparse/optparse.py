from __future__ import annotations

import optparse

import rich_argparse._lazy_rich as r
from rich_argparse._common import _HIGHLIGHTS, _fix_legacy_win_text, _rich_fill, _rich_wrap

__all__ = [
    "RichHelpFormatter",
    "IndentedRichHelpFormatter",
    "TitledRichHelpFormatter",
    "GENERATE_USAGE",
]

GENERATE_USAGE = "==GENERATE_USAGE=="


class RichHelpFormatter(optparse.HelpFormatter):
    """An optparse HelpFormatter class that renders using rich."""

    styles: dict[str, r.StyleType] = {
        "optparse.args": "cyan",
        "optparse.groups": "dark_orange",
        "optparse.help": "default",
        "optparse.metavar": "dark_cyan",
        "optparse.syntax": "bold",
        "optparse.text": "default",
        "optparse.prog": "grey50",
    }
    """A dict of rich styles to control the formatter styles.

    The following styles are used:

    - ``optparse.args``: for --options (e.g "--help")
    - ``optparse.groups``: for group names (e.g. "Options")
    - ``optparse.help``: for options's help text (e.g. "show this help message and exit")
    - ``optparse.metavar``: for meta variables (e.g. "FILE" in "--file=FILE")
    - ``argparse.prog``: for %prog in generated usage (e.g. "foo" in "Usage: foo [options]")
    - ``optparse.syntax``: for highlights of back-tick quoted text (e.g. "``` `some text` ```"),
    - ``optparse.text``: for the descriptions and epilog (e.g. "A foo program")
    """
    highlights: list[str] = _HIGHLIGHTS[:]
    """A list of regex patterns to highlight in the help text.

    It is used in the description, epilog, groups descriptions, and arguments' help. By default,
    it highlights ``--words-with-dashes`` with the `optparse.args` style and
    ``` `text in backquotes` ``` with the `optparse.syntax` style.

    To disable highlighting, clear this list (``RichHelpFormatter.highlights.clear()``).
    """

    def __init__(
        self,
        indent_increment: int,
        max_help_position: int,
        width: int | None,
        short_first: int,
    ) -> None:
        super().__init__(indent_increment, max_help_position, width, short_first)
        self._console: r.Console | None = None
        self.rich_option_strings: dict[optparse.Option, r.Text] = {}

    @property
    def console(self) -> r.Console:  # deprecate?
        if self._console is None:
            self._console = r.Console(theme=r.Theme(self.styles))
        return self._console

    @console.setter
    def console(self, console: r.Console) -> None:  # is this needed?
        self._console = console

    def _stringify(self, text: r.RenderableType) -> str:
        # Render a rich object to a string
        with self.console.capture() as capture:
            self.console.print(text, highlight=False, soft_wrap=True, end="")
        help = capture.get()
        help = "\n".join(line.rstrip() for line in help.split("\n"))
        return _fix_legacy_win_text(self.console, help)

    def rich_format_usage(self, usage: str) -> r.Text:
        raise NotImplementedError("subclasses must implement")

    def rich_format_heading(self, heading: str) -> r.Text:
        raise NotImplementedError("subclasses must implement")

    def _rich_format_text(self, text: str) -> r.Text:
        # HelpFormatter._format_text() equivalent that produces rich.text.Text
        text_width = max(self.width - 2 * self.current_indent, 11)
        indent = r.Text(" " * self.current_indent)
        rich_text = r.Text.from_markup(text, style="optparse.text")
        for highlight in self.highlights:
            rich_text.highlight_regex(highlight, style_prefix="optparse.")
        return _rich_fill(self.console, rich_text, text_width, indent)

    def rich_format_description(self, description: str) -> r.Text:
        if not description:
            return r.Text()
        return self._rich_format_text(description) + r.Text("\n")

    def rich_format_epilog(self, epilog: str) -> r.Text:
        if not epilog:
            return r.Text()
        return r.Text("\n") + self._rich_format_text(epilog) + r.Text("\n")

    def format_usage(self, usage: str) -> str:
        if usage is GENERATE_USAGE:
            rich_usage = self._generate_usage()
        else:
            rich_usage = self.rich_format_usage(usage)
        return self._stringify(rich_usage)

    def format_heading(self, heading: str) -> str:
        return self._stringify(self.rich_format_heading(heading))

    def format_description(self, description: str) -> str:
        return self._stringify(self.rich_format_description(description))

    def format_epilog(self, epilog: str) -> str:
        return self._stringify(self.rich_format_epilog(epilog))

    def rich_expand_default(self, option: optparse.Option) -> r.Text:
        assert option.help is not None
        if self.parser is None or not self.default_tag:
            help = option.help
        else:
            default_value = self.parser.defaults.get(option.dest)  # type: ignore[arg-type]
            if default_value is optparse.NO_DEFAULT or default_value is None:
                default_value = self.NO_DEFAULT_VALUE
            help = option.help.replace(self.default_tag, r.escape(str(default_value)))
        rich_help = r.Text.from_markup(help, style="optparse.help")
        for highlight in self.highlights:
            rich_help.highlight_regex(highlight, style_prefix="optparse.")
        return rich_help

    def rich_format_option(self, option: optparse.Option) -> r.Text:
        result: list[r.Text] = []
        opts = self.rich_option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts.append("\n")
            indent_first = self.help_position
        else:  # start help on same line as opts
            opts.set_length(opt_width + 2)
            indent_first = 0
        opts.pad_left(self.current_indent)
        result.append(opts)
        if option.help:
            help_text = self.rich_expand_default(option)
            help_lines = _rich_wrap(self.console, help_text, self.help_width)
            result.append(r.Text(" " * indent_first) + help_lines[0] + "\n")
            indent = r.Text(" " * self.help_position)
            for line in help_lines[1:]:
                result.append(indent + line + "\n")
        elif opts.plain[-1] != "\n":
            result.append(r.Text("\n"))
        else:
            pass  # pragma: no cover
        return r.Text().join(result)

    def format_option(self, option: optparse.Option) -> str:
        return self._stringify(self.rich_format_option(option))

    def store_option_strings(self, parser: optparse.OptionParser) -> None:
        self.indent()
        max_len = 0
        for opt in parser.option_list:
            strings = self.rich_format_option_strings(opt)
            self.option_strings[opt] = strings.plain
            self.rich_option_strings[opt] = strings
            max_len = max(max_len, len(strings) + self.current_indent)
        self.indent()
        for group in parser.option_groups:
            for opt in group.option_list:
                strings = self.rich_format_option_strings(opt)
                self.option_strings[opt] = strings.plain
                self.rich_option_strings[opt] = strings
                max_len = max(max_len, len(strings) + self.current_indent)
        self.dedent()
        self.dedent()
        self.help_position = min(max_len + 2, self.max_help_position)
        self.help_width = max(self.width - self.help_position, 11)

    def rich_format_option_strings(self, option: optparse.Option) -> r.Text:
        if option.takes_value():
            if option.metavar:
                metavar = option.metavar
            else:
                assert option.dest is not None
                metavar = option.dest.upper()
            s_delim = self._short_opt_fmt.replace("%s", "")
            short_opts = [
                r.Text(s_delim).join(
                    [r.Text(o, "optparse.args"), r.Text(metavar, "optparse.metavar")]
                )
                for o in option._short_opts
            ]
            l_delim = self._long_opt_fmt.replace("%s", "")
            long_opts = [
                r.Text(l_delim).join(
                    [r.Text(o, "optparse.args"), r.Text(metavar, "optparse.metavar")]
                )
                for o in option._long_opts
            ]
        else:
            short_opts = [r.Text(o, style="optparse.args") for o in option._short_opts]
            long_opts = [r.Text(o, style="optparse.args") for o in option._long_opts]

        if self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts

        return r.Text(", ").join(opts)

    def _generate_usage(self) -> r.Text:
        """Generate usage string from the parser's actions."""
        if self.parser is None:
            raise TypeError("Cannot generate usage if parser is not set")
        mark = "==GENERATED_USAGE_MARKER=="
        usage_lines: list[r.Text] = []
        prefix = self.rich_format_usage(mark).split(mark)[0]
        usage_lines.extend(prefix.split("\n"))
        usage_lines[-1].append(self.parser.get_prog_name(), "optparse.prog")
        indent = len(usage_lines[-1]) + 1
        for option in self.parser.option_list:
            if option.help == optparse.SUPPRESS_HELP:
                continue
            opt_str = option._short_opts[0] if option._short_opts else option.get_opt_string()
            option_usage = r.Text("[").append(opt_str, "optparse.args")
            if option.takes_value():
                metavar = option.metavar or option.dest.upper()  # type: ignore[union-attr]
                option_usage.append(" ").append(metavar, "optparse.metavar")
            option_usage.append("]")
            if len(usage_lines[-1]) + len(option_usage) + 1 > self.width:
                usage_lines.append(r.Text(" " * indent) + option_usage)
            else:
                usage_lines[-1].append(" ").append(option_usage)
        usage_lines.append(r.Text())
        return r.Text("\n").join(usage_lines)


class IndentedRichHelpFormatter(RichHelpFormatter):
    """Format help with indented section bodies."""

    def __init__(
        self,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
        short_first: int = 1,
    ) -> None:
        super().__init__(indent_increment, max_help_position, width, short_first)

    def rich_format_usage(self, usage: str) -> r.Text:
        usage_template = optparse._("Usage: %s\n")  # type: ignore[attr-defined]
        usage = usage_template % usage
        prefix = (usage_template % "").rstrip()
        spans = [r.Span(0, len(prefix), "optparse.groups")]
        return r.Text(usage, spans=spans)

    def rich_format_heading(self, heading: str) -> r.Text:
        text = r.Text(" " * self.current_indent).append(f"{heading}:", "optparse.groups")
        return text + r.Text("\n")


class TitledRichHelpFormatter(RichHelpFormatter):
    """Format help with underlined section headers."""

    def __init__(
        self,
        indent_increment: int = 0,
        max_help_position: int = 24,
        width: int | None = None,
        short_first: int = 0,
    ) -> None:
        super().__init__(indent_increment, max_help_position, width, short_first)

    def rich_format_usage(self, usage: str) -> r.Text:
        heading = self.rich_format_heading(optparse._("Usage"))  # type: ignore[attr-defined]
        return r.Text.assemble(heading, "  ", usage, "\n")

    def rich_format_heading(self, heading: str) -> r.Text:
        underline = "=-"[self.level] * len(heading)
        return r.Text.assemble(
            (heading, "optparse.groups"), "\n", (underline, "optparse.groups"), "\n"
        )


if __name__ == "__main__":
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
