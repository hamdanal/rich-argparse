# rich-argparse

![python -m rich_argparse](
https://user-images.githubusercontent.com/93259987/224482407-ea1de764-09f7-415e-acaa-259466ba9c18.svg)

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
  * [--version](#colors-in---version)
* [Subparsers](#working-with-subparsers)
* [Third party formatters](#working-with-third-party-formatters) (ft. django)
* [Optparse](#optparse-support) (experimental)

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

*rich-argparse* defines equivalents to argparse's [built-in formatters](
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

You can customize the colors in the output by modifying the `styles` dictionary on the formatter
class. *rich-argparse* defines the following styles:

```python
{
    'argparse.args': 'cyan',  # for positional-arguments and --options (e.g "--help")
    'argparse.groups': 'dark_orange',  # for group names (e.g. "positional arguments")
    'argparse.help': 'default',  # for argument's help text (e.g. "show this help message and exit")
    'argparse.metavar': 'dark_cyan',  # for metavariables (e.g. "FILE" in "--file FILE")
    'argparse.prog': 'grey50',  # for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
    'argparse.syntax': 'bold',  # for highlights of back-tick quoted text (e.g. "`some text`")
    'argparse.text': 'default',  # for descriptions, epilog, and --version (e.g. "A program to foo")
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
styles. If you use a custom `usage` message in the parser, it will treated as "plain text" and will
**not** be colored by default. You can enable colors in user defined usage message through
[console markup](https://rich.readthedocs.io/en/stable/markup.html) by setting
`RichHelpFormatter.usage_markup = True`. If you enable this option, make sure to [escape](
https://rich.readthedocs.io/en/stable/markup.html#escaping) any square brackets in the usage text.

### Colors in `--version`

If you use the `"version"` action from argparse, you can use console markup in the `version` string:

```python
parser.add_argument(
    "--version", action="version", version="[argparse.prog]%(prog)s[/] version [i]1.0.0[/]"
)
```

Note that the `argparse.text` style is applied to the `version` string similar to the description
and epilog.

## Working with subparsers

Subparsers do not inherit the formatter class from the parent parser by default. You have to pass
the formatter class explicitly:

```python
subparsers = parser.add_subparsers(...)
p1 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
p2 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
```

## Working with third party formatters

*rich-argparse* can be used with other formatters that **do not rely on the private internals**
of `argparse.HelpFormatter`. A popular example is [django](https://pypi.org/project/django) that
defines a custom help formatter that is used with its built in commands as well as with extension
libraries and user defined commands. To use *rich-argparse* in your django project, change your
`manage.py` file as follows:

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

Now try out some command like `python manage.py runserver --help` and notice how the special
ordering of the arguments applied by django is respected by the new help formatter.

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

Similar to `argparse`, you can customize the styles used by the formatter by modifying the
`RichHelpFormatter.styles` dictionary. These are the same styles used by `argparse` but with
the `optparse.` prefix instead:

```python
RichHelpFormatter.styles["optparse.metavar"] = "bold magenta"
```

Syntax highlighting works the same as `argparse`.

Colors in the `usage` are not supported yet.

Customizing the group name format is not supported. optparse uses Title Case format by default.
