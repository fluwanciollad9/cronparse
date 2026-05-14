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


# Mapping of month number to (name, max_days) for conflict messages
_MONTH_MAX_DAYS = {
    1: ("January", 31), 2: ("February", 28), 3: ("March", 31),
    4: ("April", 30), 5: ("May", 31), 6: ("June", 30),
    7: ("July", 31), 8: ("August", 31), 9: ("September", 30),
    10: ("October", 31), 11: ("November", 30), 12: ("December", 31),
}


def _check_dom_month_conflicts(dom, month, report: ConflictReport) -> None:
    """Append errors for day-of-month values that cannot exist in the given months."""
    if not month.values or not dom.values:
        return
    for m in sorted(month.values):
        if m not in _MONTH_MAX_DAYS:
            continue
        month_name, max_days = _MONTH_MAX_DAYS[m]
        impossible = {d for d in dom.values if d > max_days}
        if impossible:
            report.errors.append(
                f"Day(s) {sorted(impossible)} do not exist in {month_name} (month {m})."
            )


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

    # Check all month/day-of-month combinations for impossible dates
    _check_dom_month_conflicts(expression.day_of_month, expression.month, report)

    # Both DOM and DOW restricted — ambiguous semantics
    if not expression.day_of_month.wildcard and not expression.day_of_week.wildcard:
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
