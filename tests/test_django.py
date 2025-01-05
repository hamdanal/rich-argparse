from __future__ import annotations

from argparse import ArgumentParser, HelpFormatter
from types import ModuleType
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def patch_django_import():
    class DjangoHelpFormatter(HelpFormatter): ...

    class BaseCommand:
        def create_parser(self, *args, **kwargs):
            kwargs.setdefault("formatter_class", DjangoHelpFormatter)
            return ArgumentParser(*args, **kwargs)

    module = ModuleType("django.core.management.base")
    module.DjangoHelpFormatter = DjangoHelpFormatter
    module.BaseCommand = BaseCommand
    with patch.dict("sys.modules", {"django.core.management.base": module}, clear=False):
        yield


def test_patch_django_base_command():
    from django.core.management.base import BaseCommand, DjangoHelpFormatter

    from rich_argparse.django import DjangoRichHelpFormatter, patch_django_base_command

    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoHelpFormatter

    patch_django_base_command()
    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoRichHelpFormatter


def test_patch_django_command():
    from django.core.management.base import BaseCommand, DjangoHelpFormatter

    from rich_argparse.django import DjangoRichHelpFormatter, patch_django_command

    @patch_django_command
    class Command(BaseCommand): ...

    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoHelpFormatter

    parser = Command().create_parser("", "")
    assert parser.formatter_class is DjangoRichHelpFormatter
