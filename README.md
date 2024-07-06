# rich-argparse

![python -m rich_argparse](
https://github.com/hamdanal/rich-argparse/assets/93259987/5eb719ce-9865-4654-a5c6-04950a86d40d)

[![tests](https://github.com/hamdanal/rich-argparse/actions/workflows/tests.yml/badge.svg)
](https://github.com/hamdanal/rich-argparse/actions/workflows/tests.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/hamdanal/rich-argparse/main.svg)
](https://results.pre-commit.ci/latest/github/hamdanal/rich-argparse/main)
[![Downloads](https://img.shields.io/pypi/dm/rich-argparse)](https://pypistats.org/packages/rich-argparse)
[![Python Version](https://img.shields.io/pypi/pyversions/rich-argparse)
![Release](https://img.shields.io/pypi/v/rich-argparse)
](https://pypi.org/project/rich-argparse/)

Format argparse and optparse help using [rich](https://pypi.org/project/rich).

*rich-argparse* improves the look and readability of argparse's help while requiring minimal
changes to the code.

## Table of contents

* [Installation](#installation)
* [Usage](#usage)
* [Output styles](#output-styles)
  * [Colors](#customize-the-colors)
  * [Group names](#customize-the-group-name-format)
  * [Highlighting patterns](#special-text-highlighting)
  * ["usage"](#colors-in-the-usage)
  * [Console markup](#disable-console-markup)
  * [--version](#colors-in---version)
  * [Rich renderables](#rich-descriptions-and-epilog)
* [Subparsers](#working-with-subparsers)
* [Documenting your CLI](#generate-help-preview)
* [Third party formatters](#working-with-third-party-formatters) (ft. django)
* [Optparse](#optparse-support) (experimental)
* [Legacy Windows](#legacy-windows-support)

## Installation

Install from PyPI with pip or your favorite tool.

```sh
pip install rich-argparse
```

## Usage

Simply pass `formatter_class` to the argument parser
```python
import argparse
from rich_argparse import RichHelpFormatter

parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
```

*rich-argparse* defines equivalents to all argparse's [built-in formatters](
https://docs.python.org/3/library/argparse.html#formatter-class):

| `rich_argparse` formatter | equivalent in `argparse` |
|---------------------------|--------------------------|
| `RichHelpFormatter` | `HelpFormatter` |
| `RawDescriptionRichHelpFormatter` | `RawDescriptionHelpFormatter` |
| `RawTextRichHelpFormatter` | `RawTextHelpFormatter` |
| `ArgumentDefaultsRichHelpFormatter` | `ArgumentDefaultsHelpFormatter` |
| `MetavarTypeRichHelpFormatter` | `MetavarTypeHelpFormatter` |

## Output styles

The default styles used by *rich-argparse* are carefully chosen to work in different light and dark
themes.

### Customize the colors

You can customize the colors of the output by modifying the `styles` dictionary on the formatter
class. You can use any rich style as defined [here](https://rich.readthedocs.io/en/latest/style.html).
*rich-argparse* defines and uses the following styles:

```python
{
    'argparse.args': 'cyan',  # for positional-arguments and --options (e.g "--help")
    'argparse.groups': 'dark_orange',  # for group names (e.g. "positional arguments")
    'argparse.help': 'default',  # for argument's help text (e.g. "show this help message and exit")
    'argparse.metavar': 'dark_cyan',  # for metavariables (e.g. "FILE" in "--file FILE")
    'argparse.prog': 'grey50',  # for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
    'argparse.syntax': 'bold',  # for highlights of back-tick quoted text (e.g. "`some text`")
    'argparse.text': 'default',  # for descriptions, epilog, and --version (e.g. "A program to foo")
    'argparse.default': 'italic',  # for %(default)s in the help (e.g. "Value" in "(default: Value)")
}
```

For example, to make the description and epilog *italic*, change the `argparse.text` style:

```python
RichHelpFormatter.styles["argparse.text"] = "italic"
```

### Customize the group name format

You can change how the names of the groups (like `'positional arguments'` and `'options'`) are
formatted by setting the `RichHelpFormatter.group_name_formatter` which is set to `str.title` by
default. Any callable that takes the group name as an input and returns a str works:

```python
RichHelpFormatter.group_name_formatter = str.upper  # Make group names UPPERCASE
```

### Special text highlighting

You can [highlight patterns](https://rich.readthedocs.io/en/stable/highlighting.html) in the
arguments help and the description and epilog using regular expressions. By default,
*rich-argparse* highlights patterns of `--options-with-hyphens` using the `argparse.args` style
and patterns of `` `back tick quoted text` `` using the `argparse.syntax` style. You can control
what patterns are highlighted by modifying the `RichHelpFormatter.highlights` list. To disable all
highlights, you can clear this list using `RichHelpFormatter.highlights.clear()`.

You can also add custom highlight patterns and styles. The following example highlights all
occurrences of `pyproject.toml` in green:

```python
# Add a style called `pyproject` which applies a green style (any rich style works)
RichHelpFormatter.styles["argparse.pyproject"] = "green"
# Add the highlight regex (the regex group name must match an existing style name)
RichHelpFormatter.highlights.append(r"\b(?P<pyproject>pyproject\.toml)\b")
# Pass the formatter class to argparse
parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
```

### Colors in the `usage`

The usage **generated by the formatter** is colored using the `argparse.args` and `argparse.metavar`
styles. If you use a custom `usage` message in the parser, it will be treated as "plain text" and
will **not** be colored by default. You can enable colors in user defined usage message through
[console markup](https://rich.readthedocs.io/en/stable/markup.html) by setting
`RichHelpFormatter.usage_markup = True`. If you enable this option, make sure to [escape](
https://rich.readthedocs.io/en/stable/markup.html#escaping) any square brackets in the usage text.

### Disable console markup

The text of the descriptions and epilog is interpreted as
[console markup](https://rich.readthedocs.io/en/stable/markup.html) by default. If this conflicts
with your usage of square brackets, make sure to [escape](
https://rich.readthedocs.io/en/stable/markup.html#escaping) the square brackets or to disable
markup globally with `RichHelpFormatter.text_markup = False`.

Similarly the help text of arguments is interpreted as markup by default. It can be disabled using
`RichHelpFormatter.help_markup = False`.

### Colors in `--version`

If you use the `"version"` action from argparse, you can use console markup in the `version` string:

```python
parser.add_argument(
    "--version", action="version", version="[argparse.prog]%(prog)s[/] version [i]1.0.0[/]"
)
```

Note that the `argparse.text` style is applied to the `version` string similar to the description
and epilog.

### Rich descriptions and epilog

You can use any rich renderable in the descriptions and epilog. This includes all built-in rich
renderables like `Table` and `Markdown` and any custom renderables defined using the
[Console Protocol](https://rich.readthedocs.io/en/stable/protocol.html#console-protocol).

```python
import argparse
from rich.markdown import Markdown
from rich_argparse import RichHelpFormatter

description = """
# My program

This is a markdown description of my program.

* It has a list
* And a table

| Column 1 | Column 2 |
| -------- | -------- |
| Value 1  | Value 2  |
"""
parser = argparse.ArgumentParser(
    description=Markdown(description, style="argparse.text"),
    formatter_class=RichHelpFormatter,
)
...
```
Certain features are **disabled** for arbitrary renderables other than strings, including:

* Syntax highlighting with `RichHelpFormatter.highlights`
* Styling with the `"argparse.text"` style defined in `RichHelpFormatter.styles`
* Replacement of `%(prog)s` with the program name

## Working with subparsers

Subparsers do not inherit the formatter class from the parent parser by default. You have to pass
the formatter class explicitly:

```python
subparsers = parser.add_subparsers(...)
p1 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
p2 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
```

## Generate help preview

You can generate a preview of the help message for your CLI in SVG, HTML, or TXT formats using the
`HelpPreviewAction` action. This is useful for including the help message in the documentation of
your app. The action uses the
[rich exporting API](https://rich.readthedocs.io/en/stable/console.html#exporting) internally.

```python
import argparse
from rich.terminal_theme import DIMMED_MONOKAI
from rich_argparse import HelpPreviewAction, RichHelpFormatter

parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
parser.add_argument(
    "--generate-help-preview",
    action=HelpPreviewAction,
    path="help-preview.svg",  # (optional) or "help-preview.html" or "help-preview.txt"
    export_kwds={"theme": DIMMED_MONOKAI},  # (optional) keywords passed to console.save_... methods
)
```
This action is hidden, it won't show up in the help message or in the parsed arguments namespace.

Use it like this:

```sh
python my_cli.py --generate-help-preview  # generates help-preview.svg (default path specified above)
# or
python my_cli.py --generate-help-preview my-help.svg  # generates my-help.svg
# or
COLUMNS=120 python my_cli.py --generate-help-preview  # force the width of the output to 120 columns
```

## Working with third party formatters

*rich-argparse* can be used with other custom formatters through multiple inheritance. For example,
[django](https://pypi.org/project/django) defines a custom help formatter for its built in commands
as well as extension libraries and user defined commands. To use *rich-argparse* in your django
project, change your `manage.py` file as follows:

```diff
diff --git a/my_project/manage.py b/my_project/manage.py
index 7fb6855..5e5d48a 100755
--- a/my_project/manage.py
+++ b/my_project/manage.py
@@ -1,22 +1,38 @@
 #!/usr/bin/env python
 """Django's command-line utility for administrative tasks."""
 import os
 import sys


 def main():
     """Run administrative tasks."""
     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
     try:
         from django.core.management import execute_from_command_line
     except ImportError as exc:
         raise ImportError(
             "Couldn't import Django. Are you sure it's installed and "
             "available on your PYTHONPATH environment variable? Did you "
             "forget to activate a virtual environment?"
         ) from exc
+
+    from django.core.management.base import BaseCommand, DjangoHelpFormatter
+    from rich_argparse import RichHelpFormatter
+
+    class DjangoRichHelpFormatter(DjangoHelpFormatter, RichHelpFormatter):  # django first
+        """A rich-based help formatter for django commands."""
+
+    original_create_parser = BaseCommand.create_parser
+
+    def create_parser(*args, **kwargs):
+        parser = original_create_parser(*args, **kwargs)
+        parser.formatter_class = DjangoRichHelpFormatter  # set the formatter_class
+        return parser
+
+    BaseCommand.create_parser = create_parser
+
     execute_from_command_line(sys.argv)


 if __name__ == '__main__':
     main()
```

Now the output of all `python manage.py <COMMAND> --help` will be colored.

## Optparse support

*rich-argparse* now ships with experimental support for [optparse](
https://docs.python.org/3/library/optparse.html).

Import optparse help formatters from `rich_argparse.optparse`:

```python
import optparse
from rich_argparse.optparse import IndentedRichHelpFormatter  # or TitledRichHelpFormatter

parser = optparse.OptionParser(formatter=IndentedRichHelpFormatter())
...
```

You can also generate a more helpful usage message by passing `usage=GENERATE_USAGE` to the
parser. This is similar to the default behavior of `argparse`.

```python
from rich_argparse.optparse import GENERATE_USAGE, IndentedRichHelpFormatter

parser = optparse.OptionParser(usage=GENERATE_USAGE, formatter=IndentedRichHelpFormatter())
```

Similar to `argparse`, you can customize the styles used by the formatter by modifying the
`RichHelpFormatter.styles` dictionary. These are the same styles used by `argparse` but with
the `optparse.` prefix instead:

```python
RichHelpFormatter.styles["optparse.metavar"] = "bold magenta"
```

Syntax highlighting works the same as with `argparse`.

Colors in the `usage` are only supported when using `GENERATE_USAGE`.

## Legacy Windows support

When used on legacy Windows versions like *Windows 7*, colors are disabled unless
[colorama](https://pypi.org/project/colorama/) is used:

```python
import argparse
import colorama
from rich_argparse import RichHelpFormatter

colorama.init()
parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
```
