import argparse
from collections.abc import Callable
from typing import ClassVar

from rich.console import Console
from rich.style import StyleType

# flake8: noqa

class RichHelpFormatter(argparse.HelpFormatter):
    group_name_formatter: ClassVar[Callable[[str], str]]
    styles: ClassVar[dict[str, StyleType]]
    highlights: ClassVar[list[str]]
    usage_markup: ClassVar[bool]
    console: Console

class RawDescriptionRichHelpFormatter(RichHelpFormatter): ...
class RawTextRichHelpFormatter(RawDescriptionRichHelpFormatter): ...
class ArgumentDefaultsRichHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, RichHelpFormatter
): ...
class MetavarTypeRichHelpFormatter(argparse.MetavarTypeHelpFormatter, RichHelpFormatter): ...
