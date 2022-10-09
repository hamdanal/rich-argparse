from rich_argparse_plus.rich_help_formatter_plus import RichHelpFormatterPlus


def example():
    from rich_argparse_plus.example_parser import parser
    parser.parse_args(['--help'])
