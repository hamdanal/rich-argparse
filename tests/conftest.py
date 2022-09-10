from __future__ import annotations

import argparse
import io
import os
import sys
import textwrap
from unittest.mock import patch

import pytest

OPTIONS_GROUP_NAME = "OPTIONS" if sys.version_info >= (3, 10) else "OPTIONAL ARGUMENTS"


@pytest.fixture(scope="session", autouse=True)
def set_terminal_columns():
    with patch.dict(os.environ, {"COLUMNS": "100", "TERM": "xterm-256color"}):
        yield


def assert_help_output(
    parser: argparse.ArgumentParser, cmd: list[str], expected_output: str, with_ansi: bool = False
) -> None:
    __tracebackhide__ = True
    stdout = io.StringIO()
    stdout.isatty = lambda: with_ansi  # type: ignore[assignment]
    with pytest.raises(SystemExit), patch.object(sys, "stdout", stdout):
        parser.parse_args(cmd)
    out = stdout.getvalue()

    out_lines = out.splitlines()
    expected_out_lines = textwrap.dedent(expected_output).splitlines()
    assert len(out_lines) == len(expected_out_lines)

    for line, expected_line in zip(out_lines, expected_out_lines):
        assert line.rstrip() == expected_line
