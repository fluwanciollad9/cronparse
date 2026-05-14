"""CLI entry point for cronparse."""

import argparse
import json
import sys
from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.validator import ValidationResult
from cronparse.conflicts import has_conflicts
from cronparse.profiler import profile as do_profile


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse",
        description="Parse, humanize, validate, and profile cron expressions.",
    )
    p.add_argument("expression", nargs="+", help="Cron expression(s) to process")
    p.add_argument(
        "--format",
        choices=["human", "dict", "json", "table", "cron", "profile"],
        default="human",
        help="Output format (default: human)",
    )
    p.add_argument(
        "--validate", action="store_true", help="Validate expression before processing"
    )
    p.add_argument(
        "--conflicts", action="store_true", help="Check for scheduling conflicts"
    )
    return p


def _format_output(expr: CronExpression, raw: str, fmt: str) -> str:
    if fmt == "human":
        return humanize(expr)
    if fmt == "dict":
        return str(to_dict(expr))
    if fmt == "json":
        return to_json(expr)
    if fmt == "table":
        return to_table(expr)
    if fmt == "cron":
        return to_cron_string(expr)
    return humanize(expr)


def run(args: argparse.Namespace) -> int:
    if args.format == "profile":
        result = do_profile(args.expression)
        print(str(result))
        return 0 if result.error_count == 0 else 1

    exit_code = 0
    for raw in args.expression:
        try:
            expr = CronExpression.parse(raw)
        except ParseError as exc:
            print(f"[error] {raw}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        if args.validate:
            from cronparse.validator import validate_expression
            vr = validate_expression(expr)
            if not vr:
                print(f"[invalid] {raw}: {vr}", file=sys.stderr)
                exit_code = 1
                continue

        if args.conflicts:
            report = has_conflicts(expr)
            if report.has_conflicts():
                print(f"[conflict] {raw}: {report}", file=sys.stderr)

        output = _format_output(expr, raw, args.format)
        print(output)

    return exit_code


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
