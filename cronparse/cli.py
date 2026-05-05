"""Command-line interface for cronparse."""

import argparse
import sys

from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize
from cronparse.conflicts import has_conflicts, has_warnings, ConflictReport
from cronparse.formatter import to_json, to_table, to_cron_string


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse",
        description="Parse, humanize, and validate cron expressions.",
    )
    parser.add_argument("expression", help="Cron expression to process (5 fields)")
    parser.add_argument(
        "--format",
        choices=["human", "json", "table", "cron"],
        default="human",
        help="Output format (default: human)",
    )
    parser.add_argument(
        "--check-conflicts",
        action="store_true",
        help="Report any conflicts or warnings in the expression",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        expr = CronExpression(args.expression)
    except ParseError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    fmt = args.format
    if fmt == "human":
        print(humanize(expr))
    elif fmt == "json":
        print(to_json(expr))
    elif fmt == "table":
        print(to_table(expr))
    elif fmt == "cron":
        print(to_cron_string(expr))

    if args.check_conflicts:
        report: ConflictReport = has_conflicts(expr)
        if has_warnings(report):
            print("\nWarnings / Conflicts detected:", file=sys.stderr)
            print(str(report), file=sys.stderr)
            return 2

    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
