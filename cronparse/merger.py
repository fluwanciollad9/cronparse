"""Merge two cron expressions into a single unified expression."""

from dataclasses import dataclass
from typing import Optional
from cronparse.parser import CronExpression, ParseError


@dataclass
class MergeResult:
    """Result of merging two cron expressions."""
    expression: CronExpression
    conflicts: list
    merged_string: str

    def __str__(self) -> str:
        parts = [self.merged_string]
        if self.conflicts:
            parts.append("Conflicts: " + "; ".join(self.conflicts))
        return "\n".join(parts)

    @property
    def has_conflicts(self) -> bool:
        """Return True if there are any merge conflicts."""
        return bool(self.conflicts)


def _merge_field(field_a: str, field_b: str) -> tuple[str, Optional[str]]:
    """Merge two field expressions. Returns (merged, conflict_message).

    Merging rules:
    - If both fields are identical, return as-is.
    - If either field is '*' (wildcard), prefer the more specific field.
    - If both fields are simple comma-separated values, union them.
    - If either field contains a range ('-') or step ('/'), report a conflict.
    """
    if field_a == field_b:
        return field_a, None
    if field_a == "*":
        return field_b, None
    if field_b == "*":
        return field_a, None

    tokens_a = set(field_a.split(","))
    tokens_b = set(field_b.split(","))

    # Check for step or range conflicts — keep both as list if simple values
    has_complex = any(
        "/" in t or "-" in t for t in tokens_a | tokens_b
    )

    if has_complex:
        conflict = f"Cannot auto-merge complex tokens '{field_a}' and '{field_b}'"
        return field_a, conflict

    merged_tokens = sorted(tokens_a | tokens_b, key=lambda x: int(x) if x.isdigit() else x)
    return ",".join(merged_tokens), None


def merge(expr_a: CronExpression, expr_b: CronExpression) -> MergeResult:
    """Merge two CronExpression objects into a unified expression."""
    fields_a = [expr_a.minute, expr_a.hour, expr_a.day, expr_a.month, expr_a.dow]
    fields_b = [expr_b.minute, expr_b.hour, expr_b.day, expr_b.month, expr_b.dow]

    merged_parts = []
    conflicts = []
    field_names = ["minute", "hour", "day", "month", "dow"]

    for name, fa, fb in zip(field_names, fields_a, fields_b):
        merged, conflict = _merge_field(fa, fb)
        merged_parts.append(merged)
        if conflict:
            conflicts.append(f"[{name}] {conflict}")

    merged_string = " ".join(merged_parts)
    try:
        merged_expr = CronExpression.parse(merged_string)
    except ParseError as exc:
        raise ParseError(f"Merged expression is invalid: {exc}") from exc

    return MergeResult(
        expression=merged_expr,
        conflicts=conflicts,
        merged_string=merged_string,
    )


def merge_strings(cron_a: str, cron_b: str) -> MergeResult:
    """Parse and merge two cron expression strings."""
    expr_a = CronExpression.parse(cron_a)
    expr_b = CronExpression.parse(cron_b)
    return merge(expr_a, expr_b)
