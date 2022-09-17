# Change Log

## Unreleased

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
