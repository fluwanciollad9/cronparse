"""Command-line interface for cronparse."""

import argparse
import json
import sys
from typing import List, Optional

from cronparse.parser import ParseError, parse
from cronparse.humanizer import humanize
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.validator import validate
from cronparse.conflicts import detect_conflicts
from cronparse.classifier import classify


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse",
        description="Parse, humanize, validate, and classify cron expressions.",
    )
    p.add_argument("expression", nargs="+", help="One or more cron expressions.")
    p.add_argument(
        "--format",
        choices=["human", "dict", "json", "table", "cron", "classify"],
        default="human",
        help="Output format (default: human).",
    )
    p.add_argument("--validate", action="store_true", help="Validate each expression.")
    p.add_argument("--conflicts", action="store_true", help="Detect conflicts across expressions.")
    return p


def _format_output(expression: str, fmt: str) -> str:
    try:
        expr = parse(expression)
    except ParseError as exc:
        return f"ERROR: {exc}"

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
    if fmt == "classify":
        result = classify(expression)
        return result.category if result.valid else f"ERROR: {result.error}"
    return humanize(expr)


def run(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(args)

    exit_code = 0

    if ns.validate:
        for expr_str in ns.expression:
            result = validate(expr_str)
            status = "OK" if result else "INVALID"
            print(f"{expr_str!r}: {status}")
            if not result:
                print(f"  {result}")
                exit_code = 1
        return exit_code

    if ns.conflicts:
        try:
            exprs = [parse(e) for e in ns.expression]
            report = detect_conflicts(exprs)
            print(str(report))
            if report.has_conflicts():
                exit_code = 1
        except ParseError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            exit_code = 2
        return exit_code

    for expr_str in ns.expression:
        output = _format_output(expr_str, ns.format)
        print(output)

    return exit_code


def main() -> None:
    sys.exit(run())
