from __future__ import annotations

from argparse import ArgumentParser

from rich_argparse.contrib import ParagraphRichHelpFormatter
from tests.helpers import clean_argparse


def test_paragraph_rich_help_formatter():
    long_sentence = "The quick brown fox jumps over the lazy dog. " * 3
    long_paragraphs = [long_sentence] * 2
    long_text = "\n\n\r\n\t " + "\n\n".join(long_paragraphs) + "\n\n\r\n\t "
    parser = ArgumentParser(
        prog="PROG",
        description=long_text,
        epilog=long_text,
        formatter_class=ParagraphRichHelpFormatter,
    )
    group = parser.add_argument_group("group", description=long_text)
    group.add_argument("--long", help=long_text)

    expected_help_output = """\
    Usage: PROG [-h] [--long LONG]

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
    quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
    quick brown fox jumps over the lazy dog.

    Optional Arguments:
      -h, --help   show this help message and exit

    Group:
      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
      quick brown fox jumps over the lazy dog.

      The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
      quick brown fox jumps over the lazy dog.

      --long LONG  The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the
                   lazy dog. The quick brown fox jumps over the lazy dog.

                   The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the
                   lazy dog. The quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
    quick brown fox jumps over the lazy dog.

    The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The
    quick brown fox jumps over the lazy dog.
    """
    assert parser.format_help() == clean_argparse(expected_help_output)
