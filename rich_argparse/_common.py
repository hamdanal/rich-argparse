# for private use only
from __future__ import annotations

import rich_argparse._lazy_rich as r

_HIGHLIGHTS = [
    r"(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
    r"`(?P<syntax>[^`]*)`",  # highlight `text in backquotes` as syntax
]


def _rich_wrap(console: r.Console, text: r.Text, width: int) -> r.Lines:
    # textwrap.wrap() equivalent for rich.text.Text
    text = text.copy()
    text.expand_tabs(8)  # textwrap expands tabs first
    whitespace_trans = dict.fromkeys(map(ord, "\t\n\x0b\x0c\r "), ord(" "))
    text.plain = text.plain.translate(whitespace_trans)
    return text.wrap(console, width)


def _rich_fill(console: r.Console, text: r.Text, width: int, indent: r.Text) -> r.Text:
    # textwrap.fill() equivalent for rich.text.Text
    lines = _rich_wrap(console, text, width)
    return r.Text("\n").join(indent + line for line in lines)
