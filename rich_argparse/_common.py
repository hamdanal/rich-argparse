# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>

# for internal use only
from __future__ import annotations

import sys

import rich_argparse._lazy_rich as r

# Default highlight patterns:
# - highlight `text in backquotes` as "syntax"
# - --words-with-dashes outside backticks as "args"
_HIGHLIGHTS = [
    r"`(?P<syntax>[^`]*)`|(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",
]

_windows_console_fixed: bool | None = None


def rich_strip(text: r.Text) -> r.Text:
    """Strip leading and trailing whitespace from `rich.text.Text`."""
    lstrip_at = len(text.plain) - len(text.plain.lstrip())
    if lstrip_at:  # rich.Text.lstrip() is not available yet!!
        text = text[lstrip_at:]
    text.rstrip()
    return text


def rich_wrap(console: r.Console, text: r.Text, width: int) -> r.Lines:
    """`textwrap.wrap()` equivalent for `rich.text.Text`."""
    text = text.copy()
    text.expand_tabs(8)  # textwrap expands tabs first
    whitespace_trans = dict.fromkeys(map(ord, "\t\n\x0b\x0c\r "), ord(" "))
    text.plain = text.plain.translate(whitespace_trans)
    return text.wrap(console, width)


def rich_fill(console: r.Console, text: r.Text, width: int, indent: r.Text) -> r.Text:
    """`textwrap.fill()` equivalent for `rich.text.Text`."""
    lines = rich_wrap(console, text, width)
    return r.Text("\n").join(indent + line for line in lines)


def _initialize_win_colors() -> bool:  # pragma: no cover
    global _windows_console_fixed
    assert sys.platform == "win32"
    if _windows_console_fixed is None:
        winver = sys.getwindowsversion()  # type: ignore[attr-defined]
        if winver.major < 10 or winver.build < 10586:
            try:
                import colorama

                _windows_console_fixed = isinstance(sys.stdout, colorama.ansitowin32.StreamWrapper)
            except Exception:
                _windows_console_fixed = False
        else:
            import ctypes

            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            ENABLE_PROCESSED_OUTPUT = 0x1
            ENABLE_WRAP_AT_EOL_OUTPUT = 0x2
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x4
            STD_OUTPUT_HANDLE = -11
            kernel32.SetConsoleMode(
                kernel32.GetStdHandle(STD_OUTPUT_HANDLE),
                ENABLE_PROCESSED_OUTPUT
                | ENABLE_WRAP_AT_EOL_OUTPUT
                | ENABLE_VIRTUAL_TERMINAL_PROCESSING,
            )
            _windows_console_fixed = True
    return _windows_console_fixed


def _fix_legacy_win_text(console: r.Console, text: str) -> str:
    # activate legacy Windows console colors if needed (and available) or strip ANSI escape codes
    if (
        text
        and sys.platform == "win32"
        and console.legacy_windows
        and console.color_system is not None
        and not _initialize_win_colors()
    ):  # pragma: win32 cover
        text = "\n".join(r.re_ansi.sub("", line) for line in text.split("\n"))
    return text
