# Change Log

## Unreleased

## 0.3.1 - 2022-10-08

### Fixes
- Fix required options not coloured in the usage
  * Issue #28, PR #30

## 0.3.0 - 2022-10-01

### Features
- A new custom usage lexer that is consistent with the formatter styles
  * Issue #16, PR #17

### Fixes
- Fix inconsistent coloring of args in the top usage panel
  * Issue #16, PR #17
- Fix incorrect line breaks that put metavars on a alone on a new line
  * Issue #12, PR #20
- Do not print help output, return it instead
  * Issue #19, PR #21

### Changes
- The default styles have been changed to be more in line with the new usage coloring
  * PR #17
- The default `max_help_position` is now set to 24 (the default used in argparse) as line breaks
  are no longer an issue
  * PR #20

### Removed
- The `RichHelpFormatter.renderables` property has been removed, it was never documented
  * PR #20

### Tests
- Run windows tests in CI
  * PR #22

## 0.2.1 - 2022-09-25

### Fixes
- Fix compatibility with `argparse.ArgumentDefaultsHelpFormatter`
  * Issue #13, PR #14

## 0.2.0 - 2022-09-17

### Features
- Metavars now have their own style `argparse.metavar` which defaults to `'bold cyan'`
  * Issue #4, PR #9

### Fixes
- Add missing ":" after the group name similar to the default HelpFormatter
  * Issue #4, PR #10
- Fix padding of long options or metavars
  * PR #11
- Fix overflow of text in help that was truncated
  * PR #11
- Escape parameters that get substituted with % such as %(prog)s and %(default)s
  * PR #11
- Fix flaky wrapping of long lines
  * PR #11

## 0.1.1 - 2022-09-10

### Fixes
- Fix `RichHelpFormatter` does not replace `%(prog)s` in text
  * Issue #5, PR #6
- Fix extra newline at the end
  * Issue #7, PR #8

## 0.1.0 - 2022-09-03

Initial release

### Features
- First upload to PyPI, `pip install rich-argparse` now supported
