# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
"""Django-specific utilities for rich command line help."""

from __future__ import annotations

try:
    from django.core.management.base import DjangoHelpFormatter as _DjangoHelpFormatter
except ImportError as e:  # pragma: no cover
    raise ImportError("rich_argparse.django requires django to be installed.") from e

from rich_argparse._argparse import RichHelpFormatter as _RichHelpFormatter
from rich_argparse._patching import patch_default_formatter_class as _patch_default_formatter_class

__all__ = [
    "DjangoRichHelpFormatter",
    "richify_command_line_help",
]


class DjangoRichHelpFormatter(_DjangoHelpFormatter, _RichHelpFormatter):
    """A rich help formatter for django commands."""


def richify_command_line_help(
    formatter_class: type[_RichHelpFormatter] = DjangoRichHelpFormatter,
) -> None:
    """Set a rich default formatter class for ``BaseCommand`` project-wide.

    Calling this function affects all built-in, third-party, and user defined django commands.

    Note that this function only changes the **default** formatter class of commands. User commands
    can still override the default by explicitly setting a formatter class.
    """
    from django.core.management.base import BaseCommand

    _patch_default_formatter_class(
        BaseCommand, formatter_class=formatter_class, method_name="create_parser"
    )
