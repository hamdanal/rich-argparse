from os.path import dirname, join, pardir, realpath
from random import randint
from time import sleep

from rich.color import ANSI_COLOR_NAMES
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from rich_argparse_plus import RichHelpFormatterPlus
from rich_argparse_plus.example_parser import parser as example_parser
from rich_argparse_plus.themes import *

RENDERED_THEME_DIR = realpath(join(dirname(__file__), pardir, 'doc', 'themes'))

console = Console()


def show_themes() -> None:
    for theme_name in ARGPARSE_COLOR_THEMES.keys():
        RichHelpFormatterPlus.choose_theme(theme_name)
        console.line(3)
        title_panel = Panel(f" {theme_name}    ", width=50, expand=False, style='bright_white')
        console.print(title_panel, justify='center')
        console.line()
        _print_help_text()


def random_theme_stream() -> None:
    """Print a random theme every few seconds"""
    while True:
        theme = random_theme()
        _print_theme_styles(theme)
        RichHelpFormatterPlus.styles = random_theme()
        _print_help_text()
        sleep(2)


def render_all_themes() -> None:
    """Render all the themes to .png files in the repo"""
    pass


def random_theme() -> dict:
    return {
        ARGPARSE_ARGS: _random_style(),
        ARGPARSE_DESCRIPTION: _random_style(),
        ARGPARSE_GROUPS: _random_style(),
        ARGPARSE_HELP: _random_style(),
        ARGPARSE_METAVAR: _random_style(),
        ARGPARSE_SYNTAX: _random_style(),
    }


def _print_theme_styles(theme: dict) -> None:
    """Print settings in a way that can be copy/pasted"""
    console.line(3)
    printable_theme = {k.upper().replace('.', '_'): v for k, v in theme.items()}

    for element in sorted(list(printable_theme.keys())):
        print(f"{element}: '{printable_theme[element]}',")

    console.line(2)


def _random_style(low: int = 1, high: int = 255) -> str:
    number = randint(1, 255)
    color_name = _get_color_name(number)

    # Limit to red and grey for Dracula style theme randomization
    # while color_name is None or not re.search('red|grey', color_name):
    #     number = randint(1, 255)
    #     color_name = _get_color_name(number)

    style = f"color({number})"

    if randint(0, 10) > 5:
        style += ' bold'
    if randint(0, 10) > 6:
        style += ' dim'
    if randint(0, 10) > 7:
        style += ' italic'
    if randint(0, 10) > 9:
        style += ' underline'

    return style


def _get_color_name(n: int):
    if n not in ANSI_COLOR_NAMES.values():
        return None
    return list(ANSI_COLOR_NAMES.keys())[list(ANSI_COLOR_NAMES.values()).index(n)]


def _print_help_text() -> None:
    console.print(Text.from_ansi(example_parser.format_help()))
