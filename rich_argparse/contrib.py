# Source code: https://github.com/hamdanal/rich-argparse
# MIT license: Copyright (c) Ali Hamdan <ali.hamdan.dev@gmail.com>
"""Extra formatters for rich help messages.

The rich_argparse.contrib module contains optional, standard implementations of common patterns of
rich help message formatting. These formatters are not included in the main rich_argparse module
because they do not translate directly to argparse formatters.
"""

from __future__ import annotations

from rich_argparse._contrib import ParagraphRichHelpFormatter

__all__ = [
    "ParagraphRichHelpFormatter",
]
