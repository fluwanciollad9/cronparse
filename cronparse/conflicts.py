"""Detect logical conflicts and redundancies in cron expressions."""

from dataclasses import dataclass, field
from typing import List
from cronparse.parser import CronExpression


@dataclass
class ConflictReport:
    expression: str
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def __str__(self) -> str:
        lines = [f"Expression: {self.expression}"]
        for e in self.errors:
            lines.append(f"  [ERROR] {e}")
        for w in self.warnings:
            lines.append(f"  [WARN]  {w}")
        if not self.errors and not self.warnings:
            lines.append("  No conflicts detected.")
        return "\n".join(lines)


def _field_values_in_range(f, lo, hi):
    if f.values:
        return all(lo <= v <= hi for v in f.values)
    return True


def detect_conflicts(expression: CronExpression) -> ConflictReport:
    """Analyse a CronExpression and return a ConflictReport."""
    raw = " ".join([
        expression.minute.raw,
        expression.hour.raw,
        expression.day_of_month.raw,
        expression.month.raw,
        expression.day_of_week.raw,
    ])
    report = ConflictReport(expression=raw)

    # Feb 30/31 — impossible date
    dom = expression.day_of_month
    month = expression.month
    if month.values and dom.values:
        feb_only = month.values == {2}
        impossible_days = {d for d in dom.values if d > 28}
        if feb_only and impossible_days:
            report.errors.append(
                f"Day(s) {sorted(impossible_days)} do not exist in February."
            )

    # Day 31 in months with 30 days
    short_months = {4, 6, 9, 11}
    if month.values and dom.values:
        bad = month.values & short_months
        if bad and 31 in dom.values:
            names = ", ".join(str(m) for m in sorted(bad))
            report.errors.append(
                f"Day 31 does not exist in month(s): {names}."
            )

    # Both DOM and DOW restricted — ambiguous semantics
    if not dom.wildcard and not expression.day_of_week.wildcard:
        report.warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "most cron implementations use OR semantics which may be unintended."
        )

    # Step of 0 is invalid
    for fname, f in [
        ("minute", expression.minute), ("hour", expression.hour),
        ("day-of-month", expression.day_of_month),
        ("month", expression.month), ("day-of-week", expression.day_of_week),
    ]:
        if f.step == 0:
            report.errors.append(f"Step value of 0 in {fname} field is invalid.")

    return report
