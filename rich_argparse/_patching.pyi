# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>

# for internal use only
from argparse import _FormatterClass
from collections.abc import Callable
from typing import TypeVar, overload

from rich_argparse._argparse import RichHelpFormatter

_T = TypeVar("_T", bound=type)

@overload
def patch_default_formatter_class(
    cls: None = None,
    /,
    *,
    formatter_class: _FormatterClass = RichHelpFormatter,
    method_name: str = "__init__",
) -> Callable[[_T], _T]: ...
@overload
def patch_default_formatter_class(
    cls: _T,
    /,
    *,
    formatter_class: _FormatterClass = RichHelpFormatter,
    method_name: str = "__init__",
) -> _T: ...
