# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>

# for internal use only
from __future__ import annotations

from rich import get_console

import rich_argparse._lazy_rich as r
from rich_argparse._argparse import RichHelpFormatter
from rich_argparse._common import rich_strip, rich_wrap


class ParagraphRichHelpFormatter(RichHelpFormatter):
    """Rich help message formatter which retains paragraph separation."""

    def _rich_split_lines(self, text: r.Text, width: int) -> r.Lines:
        text = rich_strip(text)
        lines = r.Lines()
        for paragraph in text.split("\n\n"):
            # Normalize whitespace in the paragraph
            paragraph = self._rich_whitespace_sub(paragraph)
            # Wrap the paragraph to the specified width
            paragraph_lines = rich_wrap(self.console, paragraph, width)
            # Add the wrapped lines to the output
            lines.extend(paragraph_lines)
            # Add a blank line between paragraphs
            lines.append(r.Text("\n"))
        if lines:  # pragma: no cover
            lines.pop()  # Remove trailing newline
        return lines

    def _rich_fill_text(self, text: r.Text, width: int, indent: r.Text) -> r.Text:
        lines = self._rich_split_lines(text, width)
        return r.Text("\n").join(indent + line for line in lines) + "\n"


WRAPPED_MAX_WIDTH = 88
WRAPPED_MIN_WIDTH = 40


class WrappedColorFormatter(ParagraphRichHelpFormatter):
    """
    A colored formatter for argparse that retains paragraphs (unlike default
    argparse formatters) and also wraps text to console width, which is better
    for readability in both wide and narrow consoles.
    """

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 24,
        width: int | None = None,
        console: r.Console | None = None,
    ) -> None:
        if not width:
            width = max(WRAPPED_MIN_WIDTH, min(WRAPPED_MAX_WIDTH, get_console().width))
        super().__init__(prog, indent_increment, max_help_position, width=width, console=console)
