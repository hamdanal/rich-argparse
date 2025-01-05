from __future__ import annotations

from argparse import ArgumentParser, HelpFormatter
from unittest.mock import patch


class DjangoHelpFormatter(HelpFormatter): ...


def create_base_command():
    class BaseCommand:
        def create_parser(self, *args, **kwargs):
            kwargs.setdefault("formatter_class", DjangoHelpFormatter)
            return ArgumentParser(*args, **kwargs)

    return BaseCommand


@patch("django.core.management.base.DjangoHelpFormatter", new=DjangoHelpFormatter)
@patch("django.core.management.base.BaseCommand", new=create_base_command())
def test_patch_django_base_command():
    from django.core.management.base import BaseCommand

    from rich_argparse.django import DjangoRichHelpFormatter, patch_django_base_command

    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoHelpFormatter

    patch_django_base_command()
    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoRichHelpFormatter


@patch("django.core.management.base.DjangoHelpFormatter", new=DjangoHelpFormatter)
@patch("django.core.management.base.BaseCommand", new=create_base_command())
def test_patch_django_command():
    from django.core.management.base import BaseCommand

    from rich_argparse.django import DjangoRichHelpFormatter, patch_django_command

    @patch_django_command
    class Command(BaseCommand): ...

    parser = BaseCommand().create_parser("", "")
    assert parser.formatter_class is DjangoHelpFormatter

    parser = Command().create_parser("", "")
    assert parser.formatter_class is DjangoRichHelpFormatter
