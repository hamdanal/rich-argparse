from rich.style import StyleType
from rich.terminal_theme import TerminalTheme

STYLE_PREFIX = "argparse."
build_style_name = lambda _type: f"{STYLE_PREFIX}{_type}"

ARGPARSE_ARGS = build_style_name("args")
ARGPARSE_DEFAULT = build_style_name("default")
ARGPARSE_DEFAULT_NUMBER = build_style_name("default_number")
ARGPARSE_DEFAULT_STRING = build_style_name("default_string")
ARGPARSE_DESCRIPTION = build_style_name("text")
ARGPARSE_GROUPS = build_style_name("groups")
ARGPARSE_HELP = build_style_name("help")
ARGPARSE_METAVAR = build_style_name("metavar")
ARGPARSE_SYNTAX = build_style_name("syntax")
ARGPARSE_TEXT = build_style_name("text")  # TODO: Unused?

ARGPARSE_COLOR_THEMES: dict[str, dict[str, StyleType]] = {
    'default': {
        ARGPARSE_ARGS: "cyan",
        ARGPARSE_DEFAULT: "dark_cyan",
        ARGPARSE_DEFAULT_NUMBER: "bright_cyan",
        ARGPARSE_DEFAULT_STRING: "color(106)",
        ARGPARSE_DESCRIPTION: "default",
        ARGPARSE_GROUPS: "dark_orange",
        ARGPARSE_HELP: "default",
        ARGPARSE_METAVAR: "dark_cyan",
        ARGPARSE_SYNTAX: "bold",
    },

    'prince': {
        ARGPARSE_ARGS: "italic color(147)",
        ARGPARSE_DEFAULT: "dark_cyan",
        ARGPARSE_DEFAULT_NUMBER: "bright_cyan",
        ARGPARSE_DEFAULT_STRING: "color(128)",
        ARGPARSE_DESCRIPTION: "color(255)",
        ARGPARSE_GROUPS: "blue bold",
        ARGPARSE_HELP: "color(252)",
        ARGPARSE_METAVAR: "color(96)",
        ARGPARSE_SYNTAX: "#E06C75",  # Light Red color used by the one-dark theme
    },

    'night_prince': {
        ARGPARSE_ARGS: 'color(219)',
        ARGPARSE_TEXT: 'color(93) dim',
        ARGPARSE_GROUPS: 'color(174)',
        ARGPARSE_HELP: 'color(88) dim italic',
        ARGPARSE_METAVAR: 'color(132) bold italic',
        ARGPARSE_SYNTAX: 'color(251)'
    },

    'black_and_white': {
       ARGPARSE_ARGS: 'color(248)',
       ARGPARSE_TEXT: 'color(255) bold',
       ARGPARSE_GROUPS: 'white reverse bold',
       ARGPARSE_HELP: 'color(240) italic',
       ARGPARSE_METAVAR: 'color(250) dim',
       ARGPARSE_SYNTAX: 'color(247) italic'
    },

    'darkness': {
       ARGPARSE_ARGS: 'color(236) dim',
       ARGPARSE_TEXT: 'color(240) italic',
       ARGPARSE_GROUPS: 'color(238) italic',
       ARGPARSE_HELP: 'color(237) italic',
       ARGPARSE_METAVAR: 'color(232) bold',
       ARGPARSE_SYNTAX: 'color(239) bold dim italic'
    },

    'the_matrix': {
        ARGPARSE_ARGS: "color(106) dim",
        ARGPARSE_DESCRIPTION: "bright_green",
        ARGPARSE_GROUPS: "bold color(220)",
        ARGPARSE_HELP: "color(156)",
        ARGPARSE_METAVAR: "color(148)",
        ARGPARSE_SYNTAX: "color(116) bold",  # Light Red color used by the one-dark theme
    },

    'the_lawn': {
        ARGPARSE_ARGS: 'color(136) bold italic',
        ARGPARSE_TEXT: 'color(35) bold dim',
        ARGPARSE_GROUPS: 'color(151) bold dim',
        ARGPARSE_HELP: 'color(217) bold dim',
        ARGPARSE_METAVAR: 'color(246) bold',
        ARGPARSE_SYNTAX: 'color(242) bold dim'
    },

    'forest': {
        ARGPARSE_ARGS: 'color(242)',
        ARGPARSE_TEXT: 'color(65) dim',
        ARGPARSE_GROUPS: 'color(234) bold dim',
        ARGPARSE_HELP: 'color(193)',
        ARGPARSE_METAVAR: 'color(28) dim italic',
        ARGPARSE_SYNTAX: 'color(179)'
    },

    'lilac': {
        ARGPARSE_ARGS: 'color(125)',
        ARGPARSE_GROUPS: 'color(96)',
        ARGPARSE_HELP: 'color(126) dim italic',
        ARGPARSE_METAVAR: 'color(252) bold',
        ARGPARSE_SYNTAX: 'color(108) bold dim',
        ARGPARSE_TEXT: 'color(168) dim'
    },

    'morning_glory': {
        ARGPARSE_ARGS: 'color(230) bold dim',
        ARGPARSE_TEXT: 'color(231) dim',
        ARGPARSE_GROUPS: 'color(231)',
        ARGPARSE_HELP: 'color(230) italic',
        ARGPARSE_METAVAR: 'color(184)',
        ARGPARSE_SYNTAX: 'color(190) bold'
    },

    'roses': {
       ARGPARSE_ARGS: 'color(198) italic',
       ARGPARSE_TEXT: 'color(235)',
       ARGPARSE_GROUPS: 'color(60) bold',
       ARGPARSE_HELP: 'color(8)',
       ARGPARSE_METAVAR: 'color(242) bold dim italic',
       ARGPARSE_SYNTAX: 'color(168)',
    },

    'dracula': {
       ARGPARSE_ARGS: 'color(239) bold dim italic',
       ARGPARSE_TEXT: 'color(160) italic',
       ARGPARSE_GROUPS: 'color(167) dim italic',
       ARGPARSE_HELP: 'color(9) dim italic',
       ARGPARSE_METAVAR: 'color(59)',
       ARGPARSE_SYNTAX: 'color(94) italic'
    }
}

ANTI_THEMES: dict[str, dict[str, StyleType]] = {}

for theme_name, style_dict in ARGPARSE_COLOR_THEMES.items():
    anti_theme = ANTI_THEMES[f"anti_{theme_name}"] = {}

    for element, style in style_dict.items():
        anti_theme[element] = f"{style} reverse"


# The TerminalThemes that come with Rich all have the black and white offset from actual black and white.
# This is a plain black, totally standard ANSI color theme.
ARGPARSE_TERMINAL_THEME = TerminalTheme(
    (0, 0, 0),
    (255, 255, 255),
    [
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 128),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ],
)
