import argparse
import sys

from modelforge import slogging

from sourced.ml.mining.cmd import ArgumentDefaultsHelpFormatterNoNone


def parse_args() -> argparse.Namespace:
    """
    Create the cmdline argument parser.
    """
    parser = argparse.ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatterNoNone
    )
    slogging.add_logging_args(parser, patch=True, erase_args=False)

    # Create and construct subparsers
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    def add_parser(name, help_message):
        return subparsers.add_parser(
            name, help=help_message, formatter_class=ArgumentDefaultsHelpFormatterNoNone
        )

    args = parser.parse_args()
    if not hasattr(args, "handler"):
        args.handler = lambda _: parser.print_usage()  # noqa: E731
    return args


def main():
    """
    Create all the argparse-rs and invokes the function from set_defaults().

    :return: The result of the function from set_defaults().
    """
    args = parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
