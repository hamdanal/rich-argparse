# Change Log

## Unreleased

### Features
- Make `RichHelpFormatter` itself a rich renderable.
  * PR [#90](https://github.com/hamdanal/rich-argparse/pull/90)
- Allow passing custom console to `RichHelpFormatter`.
  * Issue [#91](https://github.com/hamdanal/rich-argparse/issues/91),
    PR [#92](https://github.com/hamdanal/rich-argparse/pull/92)
- Add `HelpPreviewAction` to generate a preview of the help output in SVG, HTML, or TXT formats.
  * Issue [#91](https://github.com/hamdanal/rich-argparse/issues/91),
    PR [#93](https://github.com/hamdanal/rich-argparse/pull/93)
- Avoid importing `typing` to improve startup time by about 35%.
  * PR [#97](https://github.com/hamdanal/rich-argparse/pull/97)

## 1.3.0 - 2023-08-19

### Features
- Add `optparse.GENERATE_USAGE` to auto generate a usage similar to argparse.
  * PR [#87](https://github.com/hamdanal/rich-argparse/pull/87)
- Add `rich_format_*` methods to optparse formatters. These return a `rich.text.Text` object.
  * PR [#87](https://github.com/hamdanal/rich-argparse/pull/87)

### Fixes
- Fix ansi escape codes on legacy Windows console
  * Issue [#79](https://github.com/hamdanal/rich-argparse/issues/79),
    PR [#80](https://github.com/hamdanal/rich-argparse/pull/80),
    PR [#85](https://github.com/hamdanal/rich-argparse/pull/85)

## 1.2.0 - 2023-07-02

### Features
- Add experimental support for `optparse`. Import optparse formatters from `rich_argparse.optparse`.
  * PR [#73](https://github.com/hamdanal/rich-argparse/pull/73)

### Changes
- The project now uses `ruff` for linting and import sorting.
  * PR [#72](https://github.com/hamdanal/rich-argparse/pull/72)
- `rich_argparse` is now a package instead of a module. This should not affect users.
  * PR [#71](https://github.com/hamdanal/rich-argparse/pull/71)

### Fixes
- Fix crash when a metavar following a long option contains control codes.
  * PR [#74](https://github.com/hamdanal/rich-argparse/pull/74)

## 1.1.1 - 2023-05-30

### Fixes
- Fix `%` not being escaped properly.
  * Issue [#67](https://github.com/hamdanal/rich-argparse/issues/67),
    PR [#69](https://github.com/hamdanal/rich-argparse/pull/69)
- Restore lazy loading of `rich`. Delay its import until it is needed.
  * PR [#68](https://github.com/hamdanal/rich-argparse/pull/68)

## 1.1.0 - 2023-03-11

### Features
- Add a new style for `%(prog)s` in the usage. The style is applied in argparse-generated usage and
  in user defined usage whether the user usage is plain text or rich markup.
  * Issue [#55](https://github.com/hamdanal/rich-argparse/issues/55),
    PR [#56](https://github.com/hamdanal/rich-argparse/pull/56)

## 1.0.0 - 2023-01-07

### Fixes
- `RichHelpFormatter` now respects format conversion types in help strings
  * Issue [#49](https://github.com/hamdanal/rich-argparse/issues/49),
    PR [#50](https://github.com/hamdanal/rich-argparse/pull/50)

## 0.7.0 - 2022-12-31

### Features
- The default `group_name_formatter` has changed from `str.upper` to `str.title`. This renders
  better with long group names and follows the convention of popular CLI tools and programs.
  Please note that if you test the output of your CLI **verbatim** and rely on the default behavior
  of rich_argparse, you will have to either set the formatter explicitly or update the tests.
  * Issue [#47](https://github.com/hamdanal/rich-argparse/issues/47),
    PR [#48](https://github.com/hamdanal/rich-argparse/pull/48)

## 0.6.0 - 2022-12-18

### Features
- Support type checking for users. Bundle type information in the wheel and sdist.
  * PR [#43](https://github.com/hamdanal/rich-argparse/pull/43)

### Fixes
- Fix annotations of class variables previously typed as instance variables.
  * PR [#43](https://github.com/hamdanal/rich-argparse/pull/43)

## 0.5.0 - 2022-11-05

### Features
- Support console markup in **custom** `usage` messages. Note that this feature is not activated by
  default. To enable it, set `RichHelpFormatter.usage_markup = True`.
  * PR [#38](https://github.com/hamdanal/rich-argparse/pull/38)

### Fixes
- Use `soft_wrap` in `console.print` instead of a large fixed console width for wrapping
  * PR [#35](https://github.com/hamdanal/rich-argparse/pull/35)
- Fix a regression in highlight regexes that caused the formatter to crash when using the same
  style multiple times.
  * Issue [#36](https://github.com/hamdanal/rich-argparse/issues/36),
    PR [#37](https://github.com/hamdanal/rich-argparse/pull/37)

## 0.4.0 - 2022-10-15

### Features
- Add support for all help formatters of argparse. Now there are five formatter classes defined in
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
  * PR [#31](https://github.com/hamdanal/rich-argparse/pull/31)

## 0.3.1 - 2022-10-08

### Fixes
- Fix required options not coloured in the usage
  * Issue [#28](https://github.com/hamdanal/rich-argparse/issues/28),
    PR [#30](https://github.com/hamdanal/rich-argparse/pull/30)

## 0.3.0 - 2022-10-01

### Features
- A new custom usage lexer that is consistent with the formatter styles
  * Issue [#16](https://github.com/hamdanal/rich-argparse/issues/16),
    PR [#17](https://github.com/hamdanal/rich-argparse/pull/17)

### Fixes
- Fix inconsistent coloring of args in the top usage panel
  * Issue [#16](https://github.com/hamdanal/rich-argparse/issues/16),
    PR [#17](https://github.com/hamdanal/rich-argparse/pull/17)
- Fix incorrect line breaks that put metavars on a alone on a new line
  * Issue [#12](https://github.com/hamdanal/rich-argparse/issues/12),
    PR [#20](https://github.com/hamdanal/rich-argparse/pull/20)
- Do not print help output, return it instead
  * Issue [#19](https://github.com/hamdanal/rich-argparse/issues/19),
    PR [#21](https://github.com/hamdanal/rich-argparse/pull/21)

### Changes
- The default styles have been changed to be more in line with the new usage coloring
  * PR [#17](https://github.com/hamdanal/rich-argparse/pull/17)
- The default `max_help_position` is now set to 24 (the default used in argparse) as line breaks
  are no longer an issue
  * PR [#20](https://github.com/hamdanal/rich-argparse/pull/20)

### Removed
- The `RichHelpFormatter.renderables` property has been removed, it was never documented
  * PR [#20](https://github.com/hamdanal/rich-argparse/pull/20)

### Tests
- Run windows tests in CI
  * PR [#22](https://github.com/hamdanal/rich-argparse/pull/22)

## 0.2.1 - 2022-09-25

### Fixes
- Fix compatibility with `argparse.ArgumentDefaultsHelpFormatter`
  * Issue [#13](https://github.com/hamdanal/rich-argparse/issues/13),
    PR [#14](https://github.com/hamdanal/rich-argparse/pull/14)

## 0.2.0 - 2022-09-17

### Features
- Metavars now have their own style `argparse.metavar` which defaults to `'bold cyan'`
  * Issue [#4](https://github.com/hamdanal/rich-argparse/issues/4),
    PR [#9](https://github.com/hamdanal/rich-argparse/pull/9)

### Fixes
- Add missing ":" after the group name similar to the default HelpFormatter
  * Issue [#4](https://github.com/hamdanal/rich-argparse/issues/4),
    PR [#10](https://github.com/hamdanal/rich-argparse/pull/10)
- Fix padding of long options or metavars
  * PR [#11](https://github.com/hamdanal/rich-argparse/pull/11)
- Fix overflow of text in help that was truncated
  * PR [#11](https://github.com/hamdanal/rich-argparse/pull/11)
- Escape parameters that get substituted with % such as %(prog)s and %(default)s
  * PR [#11](https://github.com/hamdanal/rich-argparse/pull/11)
- Fix flaky wrapping of long lines
  * PR [#11](https://github.com/hamdanal/rich-argparse/pull/11)

## 0.1.1 - 2022-09-10

### Fixes
- Fix `RichHelpFormatter` does not replace `%(prog)s` in text
  * Issue [#5](https://github.com/hamdanal/rich-argparse/issues/5),
    PR [#6](https://github.com/hamdanal/rich-argparse/pull/6)
- Fix extra newline at the end
  * Issue [#7](https://github.com/hamdanal/rich-argparse/issues/7),
    PR [#8](https://github.com/hamdanal/rich-argparse/pull/8)

## 0.1.0 - 2022-09-03

Initial release

### Features
- First upload to PyPI, `pip install rich-argparse` now supported
