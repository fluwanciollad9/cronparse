"""Command-line interface for cronparse."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .parser import ParseError
from .humanizer import humanize
from .validator import validate
from .formatter import to_dict, to_json, to_table, to_cron_string
from .comparator import compare_many


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronparse",
        description="Parse, humanize, and analyse cron expressions.",
    )
    sub = p.add_subparsers(dest="command")

    # ---- humanize -----------------------------------------------------------
    h = sub.add_parser("humanize", help="Convert a cron expression to plain English.")
    h.add_argument("expression", help="Cron expression (quoted).")

    # ---- validate -----------------------------------------------------------
    v = sub.add_parser("validate", help="Validate a cron expression.")
    v.add_argument("expression")

    # ---- format -------------------------------------------------------------
    f = sub.add_parser("format", help="Format a cron expression.")
    f.add_argument("expression")
    f.add_argument(
        "--output",
        choices=["dict", "json", "table", "cron"],
        default="table",
    )

    # ---- compare ------------------------------------------------------------
    c = sub.add_parser(
        "compare",
        help="Compare expressions against a reference and rank by similarity.",
    )
    c.add_argument("reference", help="Reference cron expression.")
    c.add_argument("expressions", nargs="+", help="Expressions to compare.")
    c.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        metavar="T",
        help="Only show entries with similarity >= T (0–1).",
    )
    c.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output as JSON.",
    )

    return p


def _format_output(expression: str, fmt: str) -> str:
    from .parser import CronExpression

    expr = CronExpression.parse(expression)
    if fmt == "dict":
        return str(to_dict(expr))
    if fmt == "json":
        return to_json(expr)
    if fmt == "cron":
        return to_cron_string(expr)
    return to_table(expr)


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "humanize":
        try:
            print(humanize(args.expression))
        except (ParseError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    elif args.command == "validate":
        result = validate(args.expression)
        print(str(result))
        return 0 if bool(result) else 1

    elif args.command == "format":
        try:
            print(_format_output(args.expression, args.output))
        except (ParseError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    elif args.command == "compare":
        result = compare_many(args.reference, args.expressions)
        entries = (
            result.above_threshold(args.threshold)
            if args.threshold > 0.0
            else result.entries
        )
        if args.as_json:
            payload = [
                {
                    "expression": e.expression,
                    "score": round(e.score, 4),
                    "valid": e.valid,
                    "error": e.error,
                }
                for e in entries
            ]
            print(json.dumps(payload, indent=2))
        else:
            print(f"Reference: {result.reference}")
            for entry in entries:
                print(f"  {entry}")

    else:
        parser.print_help()

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
