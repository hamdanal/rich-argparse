from __future__ import annotations

import argparse
import io
import os
import sys
import textwrap
from unittest import mock

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_terminal_columns():
    with mock.patch.dict(os.environ, {"COLUMNS": "100"}):
        yield


def assert_help_output(
    parser: argparse.ArgumentParser, cmd: list[str], expected_output: str
) -> None:
    __tracebackhide__ = True
    stdout = io.StringIO()
    stderr = io.StringIO()
    with pytest.raises(SystemExit), mock.patch.object(sys, "stdout", stdout), mock.patch.object(
        sys, "stderr", stderr
    ):
        parser.parse_args(cmd)
    out = stdout.getvalue()
    err = stderr.getvalue()

    out_lines = out.splitlines()
    expected_out_lines = textwrap.dedent(expected_output).splitlines()
    assert len(out_lines) == len(expected_out_lines)

    for line, expected_line in zip(out_lines, expected_out_lines):
        assert line.rstrip() == expected_line.rstrip()
    assert err == ""
