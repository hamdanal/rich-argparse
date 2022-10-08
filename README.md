# rich-argparse
![Tests](https://img.shields.io/github/workflow/status/hamdanal/rich-argparse/tests?label=tests)
![pre-commit](https://img.shields.io/github/workflow/status/hamdanal/rich-argparse/pre-commit?label=pre-commit)
![Python Version](https://img.shields.io/pypi/pyversions/rich-argparse)
![Release](https://img.shields.io/github/v/release/hamdanal/rich-argparse?sort=semver)
![Status](https://img.shields.io/pypi/status/rich-argparse)
![Downloads](https://img.shields.io/pypi/dm/rich-argparse)

Format **argparse** help output with [**rich**](https://pypi.org/project/rich).

![python -m rich_argparse --help](
https://user-images.githubusercontent.com/93259987/194706255-caf3e987-9853-41f5-85d9-1150c7c8ac31.png)

## Installation

Install from PyPI with pip or your favorite tool.

```sh
pip install rich-argparse
```

Or copy the file `rich_argparse.py` to your project provided you have `rich` already installed.

## Usage

Pass the `formatter_class` to the argument parser
```python
import argparse
from rich_argparse import RichHelpFormatter

parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
```

## Recipes

### argparse's subparsers
`argparse` subparsers do not inherit the formatter class from the parent parser. To have the help
text of subparsers formatted with rich, you have to explicitly pass `formatter_class` to the
subparsers:

1. you can pass it to all subparsers at once:
   ```python
    subparsers = parser.add_subparsers(
        ..., parser_class=lambda **k: type(parser)(**k, formatter_class=parser.formatter_class),
    )
    p1 = subparsers.add_parser(...)
    p2 = subparsers.add_parser(...)
   ```
1. or to each subparser individually:
   ```python
    subparsers = parser.add_subparsers(...)
    p1 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
    p2 = subparsers.add_parser(..., formatter_class=parser.formatter_class)
   ```

### django's commands
`django` uses argparse for its built in commands as well as for extension libraries and user
defined commands. To use rich_argparse with these commands, change your `manage.py` file as
follows:

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
+    class RichDjangoHelpFormatter(DjangoHelpFormatter, RichHelpFormatter):  # django first
+        """A rich-based help formatter for django commands."""
+
+    original_create_parser = BaseCommand.create_parser
+
+    def create_parser(*args, **kwargs):
+        parser = original_create_parser(*args, **kwargs)
+        parser.formatter_class = RichDjangoHelpFormatter  # set the formatter_class
+        return parser
+
+    BaseCommand.create_parser = create_parser
+
     execute_from_command_line(sys.argv)


 if __name__ == '__main__':
     main()
```

Now try out some command like: `python manage.py runserver --help`

### Special text highlighting

You can highlight patterns in the help text of your CLI. By default, `RichHelpFormatter` defines
the following styles:
```pycon
>>> pprint(RichHelpFormatter.styles)
{'argparse.args': 'cyan',
 'argparse.groups': 'dark_orange',
 'argparse.help': 'default',
 'argparse.metavar': 'dark_cyan',
 'argparse.syntax': 'bold',
 'argparse.text': 'default'}
```
The following example highlights all occurrences of `pyproject.toml` in green.

```python
# add a style called `pyproject` which applies a green style (any rich style works)
RichHelpFormatter.styles["argparse.pyproject"] = "green"
# add the highlight regex (the regex group name must match an existing style name)
RichHelpFormatter.highlights.append(r"\b(?P<pyproject>pyproject\.toml)\b")
# pass the formatter class to argparse
parser = argparse.ArgumentParser(..., formatter_class=RichHelpFormatter)
...
```

### Custom group name formatting

You can change the formatting of the group name (like `'positional arguments'` and `'options'`) by
setting the `RichHelpFormatter.group_name_formatter` to any function that takes the group name as
an input and returns a str. By default, `RichHelpFormatter` sets the function to `str.upper`.

```python
RichHelpFormatter.group_name_formatter = str.title
```
