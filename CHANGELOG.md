# Change Log

## Unreleased

### Features
- [PR-149](https://github.com/hamdanal/rich-argparse/pull/149)
  Add support for django commands in the new `rich_argparse.django` module. Read more at
  https://github.com/hamdanal/rich-argparse#django-support
- [GH-140](https://github.com/hamdanal/rich-argparse/issues/140),
  [PR-147](https://github.com/hamdanal/rich-argparse/pull/147)
  Add `ParagraphRichHelpFormatter`, a formatter that preserves paragraph breaks, in the new
  `rich_argparse.contrib` module. Read more at
  https://github.com/hamdanal/rich-argparse#additional-formatters

### Fixes
- [GH-141](https://github.com/hamdanal/rich-argparse/issues/141),
  [PR-142](https://github.com/hamdanal/rich-argparse/pull/142)
  Do not highlight --options inside backticks.

## 1.6.0 - 2024-11-02

### Fixes
- [GH-133](https://github.com/hamdanal/rich-argparse/issues/133),
  [PR-135](https://github.com/hamdanal/rich-argparse/pull/135)
  Fix help preview generation with newer releases of rich.
- [GH-130](https://github.com/hamdanal/rich-argparse/issues/130),
  [PR-131](https://github.com/hamdanal/rich-argparse/pull/131)
  Fix a bug that caused long group titles to wrap.
- [GH-125](https://github.com/hamdanal/rich-argparse/issues/125),
  [GH-127](https://github.com/hamdanal/rich-argparse/pull/127),
  [PR-128](https://github.com/hamdanal/rich-argparse/pull/128)
  Redesign metavar styling to fix broken colors of usage when some metavars are wrapped to multiple
  lines. The brackets and spaces of metavars are no longer colored.

## 1.5.2 - 2024-06-15

### Fixes
- [PR-124](https://github.com/hamdanal/rich-argparse/pull/124)
  Fix a regression in `%(default)s` style that was introduced in #123.

## 1.5.1 - 2024-06-06

### Fixes
- [GH-121](https://github.com/hamdanal/rich-argparse/issues/121),
  [PR-123](https://github.com/hamdanal/rich-argparse/pull/123)
  Fix `%(default)s` style when help markup is deactivated.

## 1.5.0 - 2024-06-01

### Features
- [PR-103](https://github.com/hamdanal/rich-argparse/pull/103)
  Python 3.13 is now officially supported
- [GH-95](https://github.com/hamdanal/rich-argparse/issues/95),
  [PR-103](https://github.com/hamdanal/rich-argparse/pull/103)
  Python 3.7 is no longer supported (EOL since 27/6/2023)
- [GH-120](https://github.com/hamdanal/rich-argparse/issues/120),
  [GH-121](https://github.com/hamdanal/rich-argparse/issues/121),
  [PR-122](https://github.com/hamdanal/rich-argparse/pull/122)
  Add options `help_markup` and `text_markup` to disable console markup in the help text and the
  description text respectively.

### Fixes
- [GH-115](https://github.com/hamdanal/rich-argparse/issues/115),
  [PR-116](https://github.com/hamdanal/rich-argparse/pull/116)
  Do not print group names suppressed with `argparse.SUPPRESS`

## 1.4.0 - 2023-10-21

### Features
- [PR-90](https://github.com/hamdanal/rich-argparse/pull/90)
  Make `RichHelpFormatter` itself a rich renderable with rich console.
- [GH-91](https://github.com/hamdanal/rich-argparse/issues/91),
  [PR-92](https://github.com/hamdanal/rich-argparse/pull/92)
  Allow passing custom console to `RichHelpFormatter`.
- [GH-91](https://github.com/hamdanal/rich-argparse/issues/91),
  [PR-93](https://github.com/hamdanal/rich-argparse/pull/93)
  Add `HelpPreviewAction` to generate a preview of the help output in SVG, HTML, or TXT formats.
- [PR-97](https://github.com/hamdanal/rich-argparse/pull/97)
  Avoid importing `typing` to improve startup time by about 35%.
- [GH-84](https://github.com/hamdanal/rich-argparse/issues/84),
  [PR-98](https://github.com/hamdanal/rich-argparse/pull/98)
  Add a style for default values when using `%(default)s` in the help text.
- [PR-99](https://github.com/hamdanal/rich-argparse/pull/99)
  Allow arbitrary renderables in the descriptions and epilog.

### Fixes
- [GH-100](https://github.com/hamdanal/rich-argparse/issues/100),
  [PR-101](https://github.com/hamdanal/rich-argparse/pull/101)
  Fix color of brackets surrounding positional arguments in the usage.

## 1.3.0 - 2023-08-19

### Features
- [PR-87](https://github.com/hamdanal/rich-argparse/pull/87)
  Add `optparse.GENERATE_USAGE` to auto generate a usage similar to argparse.
- [PR-87](https://github.com/hamdanal/rich-argparse/pull/87)
  Add `rich_format_*` methods to optparse formatters. These return a `rich.text.Text` object.

### Fixes
- [GH-79](https://github.com/hamdanal/rich-argparse/issues/79),
  [PR-80](https://github.com/hamdanal/rich-argparse/pull/80),
  [PR-85](https://github.com/hamdanal/rich-argparse/pull/85)
  Fix ansi escape codes on legacy Windows console

## 1.2.0 - 2023-07-02

### Features
- [PR-73](https://github.com/hamdanal/rich-argparse/pull/73)
  Add experimental support for `optparse`. Import optparse formatters from `rich_argparse.optparse`.

### Changes
- [PR-72](https://github.com/hamdanal/rich-argparse/pull/72)
  The project now uses `ruff` for linting and import sorting.
- [PR-71](https://github.com/hamdanal/rich-argparse/pull/71)
  `rich_argparse` is now a package instead of a module. This should not affect users.

### Fixes
- [PR-74](https://github.com/hamdanal/rich-argparse/pull/74)
  Fix crash when a metavar following a long option contains control codes.

## 1.1.1 - 2023-05-30

### Fixes
- [GH-67](https://github.com/hamdanal/rich-argparse/issues/67),
  [PR-69](https://github.com/hamdanal/rich-argparse/pull/69)
  Fix `%` not being escaped properly
- [PR-68](https://github.com/hamdanal/rich-argparse/pull/68)
  Restore lazy loading of `rich`. Delay its import until it is needed.

## 1.1.0 - 2023-03-11

### Features
- [GH-55](https://github.com/hamdanal/rich-argparse/issues/55),
  [PR-56](https://github.com/hamdanal/rich-argparse/pull/56)
  Add a new style for `%(prog)s` in the usage. The style is applied in argparse-generated usage and
  in user defined usage whether the user usage is plain text or rich markup.

## 1.0.0 - 2023-01-07

### Fixes
- [GH-49](https://github.com/hamdanal/rich-argparse/issues/49),
  [PR-50](https://github.com/hamdanal/rich-argparse/pull/50)
  `RichHelpFormatter` now respects format conversion types in help strings

## 0.7.0 - 2022-12-31

### Features
- [GH-47](https://github.com/hamdanal/rich-argparse/issues/47),
  [PR-48](https://github.com/hamdanal/rich-argparse/pull/48)
  The default `group_name_formatter` has changed from `str.upper` to `str.title`. This renders
  better with long group names and follows the convention of popular CLI tools and programs.
  Please note that if you test the output of your CLI **verbatim** and rely on the default behavior
  of rich_argparse, you will have to either set the formatter explicitly or update the tests.


## 0.6.0 - 2022-12-18

### Features
- [PR-43](https://github.com/hamdanal/rich-argparse/pull/43)
  Support type checking for users. Bundle type information in the wheel and sdist.

### Fixes
- [PR-43](https://github.com/hamdanal/rich-argparse/pull/43)
  Fix annotations of class variables previously typed as instance variables.

## 0.5.0 - 2022-11-05

### Features
- [PR-38](https://github.com/hamdanal/rich-argparse/pull/38)
  Support console markup in **custom** `usage` messages. Note that this feature is not activated by
  default. To enable it, set `RichHelpFormatter.usage_markup = True`.


### Fixes
- [PR-35](https://github.com/hamdanal/rich-argparse/pull/35)
  Use `soft_wrap` in `console.print` instead of a large fixed console width for wrapping
- [GH-36](https://github.com/hamdanal/rich-argparse/issues/36),
  [PR-37](https://github.com/hamdanal/rich-argparse/pull/37)
  Fix a regression in highlight regexes that caused the formatter to crash when using the same
  style multiple times.


## 0.4.0 - 2022-10-15

### Features
- [PR-31](https://github.com/hamdanal/rich-argparse/pull/31)
  Add support for all help formatters of argparse. Now there are five formatter classes defined in
  `rich_argparse`:
  ```
  RichHelpFormatter:                 the equivalent of argparse.HelpFormatter
  RawDescriptionRichHelpFormatter:   the equivalent of argparse.RawDescriptionHelpFormatter
  RawTextRichHelpFormatter:          the equivalent of argparse.RawTextHelpFormatter
  ArgumentDefaultsRichHelpFormatter: the equivalent of argparse.ArgumentDefaultsHelpFormatter
  MetavarTypeRichHelpFormatter:      the equivalent of argparse.MetavarTypeHelpFormatter
  ```
  Note that this changes the default behavior of `RichHelpFormatter` to no longer respect line
  breaks in the description and help text. It now behaves similarly to the original
  `HelpFormatter`. You have now to use the appropriate subclass for this to happen.

## 0.3.1 - 2022-10-08

### Fixes
- [GH-28](https://github.com/hamdanal/rich-argparse/issues/28),
  [PR-30](https://github.com/hamdanal/rich-argparse/pull/30)
  Fix required options not coloured in the usage

## 0.3.0 - 2022-10-01

### Features
- [GH-16](https://github.com/hamdanal/rich-argparse/issues/16),
  [PR-17](https://github.com/hamdanal/rich-argparse/pull/17)
  A new custom usage lexer that is consistent with the formatter styles

### Fixes
- [GH-16](https://github.com/hamdanal/rich-argparse/issues/16),
  [PR-17](https://github.com/hamdanal/rich-argparse/pull/17)
  Fix inconsistent coloring of args in the top usage panel
- [GH-12](https://github.com/hamdanal/rich-argparse/issues/12),
  [PR-20](https://github.com/hamdanal/rich-argparse/pull/20)
  Fix incorrect line breaks that put metavars on a alone on a new line
- [GH-19](https://github.com/hamdanal/rich-argparse/issues/19),
  [PR-21](https://github.com/hamdanal/rich-argparse/pull/21)
  Do not print help output, return it instead

### Changes
- [PR-17](https://github.com/hamdanal/rich-argparse/pull/17)
  The default styles have been changed to be more in line with the new usage coloring
- [PR-20](https://github.com/hamdanal/rich-argparse/pull/20)
  The default `max_help_position` is now set to 24 (the default used in argparse) as line breaks
  are no longer an issue


### Removed
- [PR-20](https://github.com/hamdanal/rich-argparse/pull/20)
  The `RichHelpFormatter.renderables` property has been removed, it was never documented

### Tests
- [PR-22](https://github.com/hamdanal/rich-argparse/pull/22)
  Run windows tests in CI

## 0.2.1 - 2022-09-25

### Fixes
- [GH-13](https://github.com/hamdanal/rich-argparse/issues/13),
  [PR-14](https://github.com/hamdanal/rich-argparse/pull/14)
  Fix compatibility with `argparse.ArgumentDefaultsHelpFormatter`

## 0.2.0 - 2022-09-17

### Features
- [GH-4](https://github.com/hamdanal/rich-argparse/issues/4),
  [PR-9](https://github.com/hamdanal/rich-argparse/pull/9)
  Metavars now have their own style `argparse.metavar` which defaults to `'bold cyan'`

### Fixes
- [GH-4](https://github.com/hamdanal/rich-argparse/issues/4),
  [PR-10](https://github.com/hamdanal/rich-argparse/pull/10)
  Add missing ":" after the group name similar to the default HelpFormatter
- [PR-11](https://github.com/hamdanal/rich-argparse/pull/11)
  Fix padding of long options or metavars
- [PR-11](https://github.com/hamdanal/rich-argparse/pull/11)
  Fix overflow of text in help that was truncated
- [PR-11](https://github.com/hamdanal/rich-argparse/pull/11)
  Escape parameters that get substituted with % such as %(prog)s and %(default)s
- [PR-11](https://github.com/hamdanal/rich-argparse/pull/11)
  Fix flaky wrapping of long lines

## 0.1.1 - 2022-09-10

### Fixes
- [GH-5](https://github.com/hamdanal/rich-argparse/issues/5),
  [PR-6](https://github.com/hamdanal/rich-argparse/pull/6)
  Fix `RichHelpFormatter` does not replace `%(prog)s` in text
- [GH-7](https://github.com/hamdanal/rich-argparse/issues/7),
  [PR-8](https://github.com/hamdanal/rich-argparse/pull/8)
  Fix extra newline at the end

## 0.1.0 - 2022-09-03

Initial release

### Features
- First upload to PyPI, `pip install rich-argparse` now supported
