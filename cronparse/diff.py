"""Diff two cron expressions and report field-level differences."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, ParseError


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldDiff:
    name: str
    old_value: str
    new_value: str

    def __str__(self) -> str:
        return f"{self.name}: '{self.old_value}' -> '{self.new_value}'"


@dataclass
class CronDiff:
    old_expression: str
    new_expression: str
    changes: List[FieldDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def changed_fields(self) -> List[str]:
        return [c.name for c in self.changes]

    def __str__(self) -> str:
        if not self.has_changes:
            return "No differences found."
        lines = [f"Diff: '{self.old_expression}' vs '{self.new_expression}'"] + [
            f"  {c}" for c in self.changes
        ]
        return "\n".join(lines)


def diff(old: str, new: str) -> CronDiff:
    """Compare two cron expression strings and return a CronDiff.

    Args:
        old: The original cron expression string.
        new: The new cron expression string.

    Returns:
        A CronDiff describing which fields changed.

    Raises:
        ParseError: If either expression cannot be parsed.
    """
    old_expr = CronExpression.parse(old)
    new_expr = CronExpression.parse(new)

    old_fields = [
        old_expr.minute,
        old_expr.hour,
        old_expr.day_of_month,
        old_expr.month,
        old_expr.day_of_week,
    ]
    new_fields = [
        new_expr.minute,
        new_expr.hour,
        new_expr.day_of_month,
        new_expr.month,
        new_expr.day_of_week,
    ]

    changes: List[FieldDiff] = []
    for name, old_val, new_val in zip(FIELD_NAMES, old_fields, new_fields):
        old_raw = old_val.raw
        new_raw = new_val.raw
        if old_raw != new_raw:
            changes.append(FieldDiff(name=name, old_value=old_raw, new_value=new_raw))

    return CronDiff(old_expression=old, new_expression=new, changes=changes)
