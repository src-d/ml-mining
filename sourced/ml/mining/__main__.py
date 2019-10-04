import argparse
from pathlib import Path
import sys

from modelforge import slogging

from sourced.ml.mining.cmd import (
    ArgumentDefaultsHelpFormatterNoNone,
    clickhouse2deps,
    CLICKHOUSE_LANGS,
)


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

    # --------------------------------------------------------------------------------------------

    clickhouse2deps_parser = add_parser(
        "clickhouse2deps", "Extract dependencies from a ClickHouse DB."
    )
    clickhouse2deps_parser.set_defaults(handler=clickhouse2deps)
    clickhouse2deps_parser.add_argument(
        "-o",
        "--output-path",
        type=Path,
        help="Output path to the resulting ASDF model with the extracted dependencies.",
    )
    clickhouse2deps_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Boolean indicating whether to overwrite the existing ASDF model specified by "
        "-o/--output-path.",
    )
    clickhouse2deps_parser.add_argument(
        "--user", default="default", help="Username for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--password", default="", help="Password for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--host", default="0.0.0.0", help="Host for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--port", default=9000, type=int, help="Port for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--database", default="default", help="Database name for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--table", default="uasts", help="Table name for the DB."
    )
    clickhouse2deps_parser.add_argument(
        "--langs",
        nargs="+",
        default=CLICKHOUSE_LANGS,
        choices=CLICKHOUSE_LANGS,
        help="Languages to consider while extracting dependencies.",
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
