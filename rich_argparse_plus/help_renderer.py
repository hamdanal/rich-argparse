import logging
import sys
from os import environ, getcwd, path, remove

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

from rich_argparse_plus.themes import *

log = logging.getLogger("rich_argparse")

# Rendering constants
CAIRO_FORMATS = ['eps', 'pdf', 'png', 'ps']
RENDER_HELP_FORMAT = environ.get("RENDER_HELP_FORMAT")
RENDER_OUTPUT_DIR = environ.get("RENDER_HELP_OUTPUT_DIR", getcwd())
THEME_IN_RENDERED_FILENAME = environ.get('THEME_IN_RENDERED_FILENAME') # Include theme in filename


def render_help(formatter: 'RichHelpFormatterPlus') -> None:
    """Render the contents of the help screen to an HTML, SVG, or colored text file"""
    console = Console(record=True, theme=Theme(formatter.styles), width=formatter._width)

    for renderable in formatter._root_section.rich:
        console.print(renderable)

    export_format = 'svg' if RENDER_HELP_FORMAT in CAIRO_FORMATS else RENDER_HELP_FORMAT
    export_method_name = f"save_{export_format}"
    export_method = getattr(console, export_method_name)
    extension = 'txt' if export_format == 'text' else export_format
    output_file_no_extension = f"{formatter._prog}_help".replace(" ", "_")

    if THEME_IN_RENDERED_FILENAME:
        output_file_no_extension += f"_{formatter.theme_name}_theme"

    output_basepath = path.join(RENDER_OUTPUT_DIR, output_file_no_extension + ".")
    output_file = f"{output_basepath}{extension}"

    export_kwargs = {
        "save_html": {"theme": ARGPARSE_TERMINAL_THEME, "inline_styles": True},
        "save_svg": {"theme": ARGPARSE_TERMINAL_THEME, "title": f"{formatter._prog} --help"},
        "save_text": {"styles": True},
    }

    export_method(output_file, **export_kwargs[export_method_name])
    log.info(f"\n\nInvoked Rich.console.{export_method_name}('{output_file}')")
    log.info(f"   * kwargs: '{export_kwargs[export_method_name]}'...\n")

    if RENDER_HELP_FORMAT in CAIRO_FORMATS:
        try:
            import cairosvg
        except ModuleNotFoundError:
            msg = Text(f"ERROR: Exporting a .{RENDER_HELP_FORMAT} requires cairosvg.\n", 'bright_red')
            msg.append("Run 'pip install cairosvg' or 'pip install rich_argparse_plus[optional]' ", 'white')
            msg.append("and try again.", "white")
            console.print(msg, style='bright_red', justify='center')
            sys.exit()

        render_file = f"{output_basepath}{RENDER_HELP_FORMAT}"
        renderer = getattr(cairosvg, f"svg2{RENDER_HELP_FORMAT}")
        renderer(url=output_file, write_to=render_file)
        remove(output_file)
        console.print(f"Help rendered to '{render_file}'...", style='cyan')
    else:
        console.print(f"Help rendered to '{output_file}'...", style='cyan')
