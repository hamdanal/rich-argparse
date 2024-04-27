from __future__ import annotations

import io
import os
import sys
from typing import Any, Generic, Protocol, TypeVar
from unittest.mock import patch

import pytest


class Parser(Protocol):
    def format_help(self) -> str: ...

    def parse_args(self, *args, **kwds) -> Any: ...


PT = TypeVar("PT", bound=Parser)  # parser type
GT = TypeVar("GT")  # group type
FT = TypeVar("FT")  # formatter type


# helpers
# =======
class Groups(Generic[GT]):
    def __init__(self) -> None:
        self.groups: list[GT] = []

    def append(self, group: GT) -> None:
        self.groups.append(group)

    def add_argument(self, *args, **kwds) -> None:
        for group in self.groups:
            assert hasattr(group, "add_argument"), "Group has no add_argument method"
            group.add_argument(*args, **kwds)

    def add_option(self, *args, **kwds) -> None:
        for group in self.groups:
            assert hasattr(group, "add_option"), "Group has no add_option method"
            group.add_option(*args, **kwds)


class Parsers(Generic[PT, GT, FT]):
    parser_class: type[PT]
    formatter_param_name: str

    def __init__(self, *formatters: FT, **kwds) -> None:
        self.parsers: list[PT] = []
        assert len(set(formatters)) == len(formatters), "Duplicate formatters"
        for fmt in formatters:
            kwds[self.formatter_param_name] = fmt
            parser = self.parser_class(**kwds)
            assert hasattr(parser, "format_help"), "Parser has no format_help method"
            self.parsers.append(parser)

    def __init_subclass__(cls) -> None:
        for name in ("parser_class", "formatter_param_name"):
            assert hasattr(cls, name), f"Parsers subclass must define {name} attribute"
        return super().__init_subclass__()

    def add_argument(self, *args, **kwds) -> None:
        for parser in self.parsers:
            assert hasattr(parser, "add_argument"), "Parser has no add_argument method"
            parser.add_argument(*args, **kwds)

    def add_argument_group(self, *args, **kwds) -> Groups[GT]:
        groups = Groups[GT]()
        for parser in self.parsers:
            assert hasattr(parser, "add_argument_group"), "Parser has no add_argument_group method"
            groups.append(parser.add_argument_group(*args, **kwds))
        return groups

    def add_option(self, *args, **kwds) -> None:
        for parser in self.parsers:
            assert hasattr(parser, "add_option"), "Parser has no add_option method"
            parser.add_option(*args, **kwds)

    def add_option_group(self, *args, **kwds) -> Groups[GT]:
        groups = Groups[GT]()
        for parser in self.parsers:
            assert hasattr(parser, "add_option_group"), "Parser has no add_option_group method"
            groups.append(parser.add_option_group(*args, **kwds))
        return groups

    def assert_format_help_equal(self, expected: str | None = None) -> None:
        assert self.parsers, "No parsers to compare."
        outputs = [parser.format_help() for parser in self.parsers]
        if expected is None:  # pragma: no cover
            expected = outputs.pop()
        assert outputs, "No outputs to compare."
        for output in outputs:
            assert output == expected

    def assert_cmd_output_equal(self, cmd: list[str], expected: str | None = None) -> None:
        assert self.parsers, "No parsers to compare."
        outputs = [get_cmd_output(parser, cmd) for parser in self.parsers]
        if expected is None:  # pragma: no cover
            expected = outputs.pop()
        assert outputs, "No outputs to compare."
        for output in outputs:
            assert output == expected


def get_cmd_output(parser: Parser, cmd: list[str]) -> str:
    __tracebackhide__ = True
    stdout = io.StringIO()
    with pytest.raises(SystemExit), patch.object(sys, "stdout", stdout):
        parser.parse_args(cmd)
    return stdout.getvalue()


# fixtures
# ========
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
