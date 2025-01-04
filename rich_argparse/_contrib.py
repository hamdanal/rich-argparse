# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>

# for internal use only
from __future__ import annotations

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
