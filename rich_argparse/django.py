# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
"""Django-specific utilities for rich help messages."""

from __future__ import annotations

try:
    from django.core.management.base import DjangoHelpFormatter as _DjangoHelpFormatter
except ImportError as e:  # pragma: no cover
    raise ImportError("rich_argparse.django requires django to be installed.") from e

from functools import partial as _partial

from rich_argparse._argparse import RichHelpFormatter as _RichHelpFormatter
from rich_argparse._patching import patch_default_formatter_class as _patch_default_formatter_class

__all__ = [
    "DjangoRichHelpFormatter",
    "patch_django_command",
    "patch_django_base_command",
]


class DjangoRichHelpFormatter(_DjangoHelpFormatter, _RichHelpFormatter):
    """A rich help formatter for django commands."""


def patch_django_base_command(
    formatter_class: type[_RichHelpFormatter] = DjangoRichHelpFormatter,
) -> None:
    """Patch django's ``BaseCommand`` to use a rich help formatter project-wide.

    Calling this function affects all built-in, third-party, and user defined commands.
    """
    from django.core.management.base import BaseCommand

    _patch_default_formatter_class(
        BaseCommand, formatter_class=formatter_class, method_name="create_parser"
    )


patch_django_command = _partial(
    _patch_default_formatter_class,
    formatter_class=DjangoRichHelpFormatter,
    method_name="create_parser",
)
"""Patch a ``BaseCommand`` subclass to use a rich help formatter.

Usage::

    from django.core.management.base import BaseCommand
    from rich_argparse.django import patch_django_command

    @patch_django_command
    class Command(BaseCommand): ...

You can also use a custom help formatter::

    from rich_argparse.django import DjangoRichHelpFormatter

    class MyAwesomeHelpFormatter(DjangoRichHelpFormatter): ...

    @patch_django_command(formatter_class=MyAwesomeHelpFormatter)
    class Command(BaseCommand): ...
"""
