from __future__ import annotations

import argparse
import sys

from rich_argparse import RichHelpFormatter
from tests.conftest import assert_help_output


def test_text_replaces_prog():
    # https://github.com/hamdanal/rich-argparse/issues/5
    parser = argparse.ArgumentParser(
        "awesome_program",
        description="This is the %(prog)s program.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    expected_help_output = f"""\
    usage: awesome_program [-h] [--version]

    This is the awesome_program program.

    {"OPTIONS" if sys.version_info >= (3, 10) else "OPTIONAL ARGUMENTS"}
      -h, --help  show this help message and exit
      --version   show program's version number and exit
    """
    expected_version_output = """\
    awesome_program 1.0.0
    """
    assert_help_output(parser, cmd=["--version"], expected_output=expected_version_output)
    assert_help_output(parser, cmd=["--help"], expected_output=expected_help_output)
