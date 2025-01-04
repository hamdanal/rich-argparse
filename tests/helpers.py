from __future__ import annotations

import argparse as ap
import functools
import io
import optparse as op
import sys
import textwrap
from collections.abc import Callable
from typing import Any, Generic, TypeVar
from unittest.mock import patch

import pytest

if sys.version_info >= (3, 10):  # pragma: >=3.10 cover
    from typing import Concatenate, ParamSpec
else:  # pragma: <3.10 cover
    from typing_extensions import Concatenate, ParamSpec

R = TypeVar("R")  # return type
S = TypeVar("S")  # self type
P = ParamSpec("P")  # other parameters type
PT = TypeVar("PT", bound="ap.ArgumentParser | op.OptionParser")  # parser type
GT = TypeVar("GT", bound="ap._ArgumentGroup | op.OptionGroup")  # group type


def get_cmd_output(parser: ap.ArgumentParser | op.OptionParser, cmd: list[str]) -> str:
    __tracebackhide__ = True
    stdout = io.StringIO()
    with pytest.raises(SystemExit), patch.object(sys, "stdout", stdout):
        parser.parse_args(cmd)
    return stdout.getvalue()


def copy_signature(
    func: Callable[Concatenate[Any, P], object],
) -> Callable[[Callable[Concatenate[S, ...], R]], Callable[Concatenate[S, P], R]]:
    """Copy the signature of the given method except self and return types."""
    return functools.wraps(func)(lambda f: f)


class BaseGroups(Generic[GT]):
    """Base class for argument groups and option groups."""

    def __init__(self) -> None:
        self.groups: list[GT] = []

    def append(self, group: GT) -> None:
        self.groups.append(group)


class BaseParsers(Generic[PT]):
    """Base class for argument parsers and option parsers."""

    parsers: list[PT]

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


# argparse
# ========
class ArgumentGroups(BaseGroups[ap._ArgumentGroup]):
    @copy_signature(ap._ArgumentGroup.add_argument)  # type: ignore[arg-type]
    def add_argument(self, /, *args, **kwds) -> None:
        for group in self.groups:
            group.add_argument(*args, **kwds)


class _SubParsersActions:
    def __init__(self) -> None:
        self.parents: list[ap.ArgumentParser] = []
        self.subparsers: list[ap._SubParsersAction[ap.ArgumentParser]] = []

    def append(self, p: ap.ArgumentParser, sp: ap._SubParsersAction[ap.ArgumentParser]) -> None:
        self.parents.append(p)
        self.subparsers.append(sp)

    @copy_signature(ap._SubParsersAction.add_parser)  # type: ignore[arg-type]
    def add_parser(self, /, *args, **kwds) -> ArgumentParsers:
        parsers = ArgumentParsers()
        for parent, subparser in zip(self.parents, self.subparsers):
            sp = subparser.add_parser(*args, **kwds, formatter_class=parent.formatter_class)
            parsers.parsers.append(sp)
        return parsers


class ArgumentParsers(BaseParsers[ap.ArgumentParser]):
    def __init__(
        self,
        *formatter_classes: type[ap.HelpFormatter],
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
    ) -> None:
        assert len(set(formatter_classes)) == len(formatter_classes), "Duplicate formatter_class"
        self.parsers = [
            ap.ArgumentParser(
                prog=prog,
                usage=usage,
                description=description,
                epilog=epilog,
                formatter_class=formatter_class,
            )
            for formatter_class in formatter_classes
        ]

    @copy_signature(ap.ArgumentParser.add_argument)  # type: ignore[arg-type]
    def add_argument(self, /, *args, **kwds) -> None:
        for parser in self.parsers:
            parser.add_argument(*args, **kwds)

    @copy_signature(ap.ArgumentParser.add_argument_group)
    def add_argument_group(self, /, *args, **kwds) -> ArgumentGroups:
        groups = ArgumentGroups()
        for parser in self.parsers:
            groups.append(parser.add_argument_group(*args, **kwds))
        return groups

    @copy_signature(ap.ArgumentParser.add_subparsers)
    def add_subparsers(self, /, *args, **kwds) -> _SubParsersActions:
        subparsers = _SubParsersActions()
        for parser in self.parsers:
            sp = parser.add_subparsers(*args, **kwds)
            subparsers.append(parser, sp)
        return subparsers


def clean_argparse(text: str, dedent: bool = True) -> str:
    """Clean argparse help text."""
    # Can be replaced with textwrap.dedent(text) when Python 3.10 is the minimum version
    if sys.version_info >= (3, 10):  # pragma: >=3.10 cover
        # replace "optional arguments:" with "options:"
        pos = text.lower().index("optional arguments:")
        text = text[: pos + 6] + text[pos + 17 :]
    if dedent:
        text = textwrap.dedent(text)
    return text


# optparse
# ========
class OptionGroups(BaseGroups[op.OptionGroup]):
    @copy_signature(op.OptionGroup.add_option)
    def add_option(self, /, *args, **kwds) -> None:
        for group in self.groups:
            group.add_option(*args, **kwds)


class OptionParsers(BaseParsers[op.OptionParser]):
    def __init__(
        self,
        *formatters: op.HelpFormatter,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
    ) -> None:
        assert len(set(formatters)) == len(formatters), "Duplicate formatter"
        self.parsers = [
            op.OptionParser(
                prog=prog, usage=usage, description=description, epilog=epilog, formatter=formatter
            )
            for formatter in formatters
        ]

    @copy_signature(op.OptionParser.add_option)
    def add_option(self, /, *args, **kwds) -> None:
        for parser in self.parsers:
            parser.add_option(*args, **kwds)

    @copy_signature(op.OptionParser.add_option_group)
    def add_option_group(self, /, *args, **kwds) -> OptionGroups:
        groups = OptionGroups()
        for parser in self.parsers:
            groups.append(parser.add_option_group(*args, **kwds))
        return groups
