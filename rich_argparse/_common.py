# for internal use only
from __future__ import annotations

import sys

import rich_argparse._lazy_rich as r

_HIGHLIGHTS = [
    r"(?:^|\s)(?P<args>-{1,2}[\w]+[\w-]*)",  # highlight --words-with-dashes as args
    r"`(?P<syntax>[^`]*)`",  # highlight `text in backquotes` as syntax
]

_windows_console_fixed = None


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
