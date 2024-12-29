from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from rich_argparse import RichHelpFormatter


# Common fixtures
# ===============
@pytest.fixture(scope="session", autouse=True)
def set_terminal_properties():
    with patch.dict(os.environ, {"COLUMNS": "100", "TERM": "xterm-256color"}):
        yield


@pytest.fixture(scope="session", autouse=True)
def turnoff_legacy_windows():
    with patch("rich.console.detect_legacy_windows", return_value=False):
        yield


@pytest.fixture()
def force_color():
    with patch("rich.console.Console.is_terminal", return_value=True):
        yield


# argparse fixtures
# =================
@pytest.fixture()
def disable_group_name_formatter():
    with patch.object(RichHelpFormatter, "group_name_formatter", str):
        yield
