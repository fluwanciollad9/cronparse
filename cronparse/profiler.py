"""Profiler module: compute execution frequency statistics for cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional
from cronparse.parser import CronExpression, ParseError
from cronparse.schedule import _expand_field


@dataclass
class ExpressionProfile:
    expression: str
    valid: bool
    runs_per_hour: Optional[float] = None
    runs_per_day: Optional[float] = None
    runs_per_week: Optional[float] = None
    runs_per_month: Optional[float] = None
    error: Optional[str] = None

    def __str__(self) -> str:
        if not self.valid:
            return f"[invalid] {self.expression}: {self.error}"
        return (
            f"{self.expression}: "
            f"{self.runs_per_hour:.2f}/hr, "
            f"{self.runs_per_day:.2f}/day, "
            f"{self.runs_per_week:.2f}/week, "
            f"{self.runs_per_month:.2f}/month"
        )


@dataclass
class ProfileResult:
    profiles: List[ExpressionProfile] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return sum(1 for p in self.profiles if p.valid)

    @property
    def error_count(self) -> int:
        return sum(1 for p in self.profiles if not p.valid)

    def __str__(self) -> str:
        lines = [str(p) for p in self.profiles]
        return "\n".join(lines)


def _compute_profile(expr: CronExpression) -> ExpressionProfile:
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)
    doms = _expand_field(expr.dom, 1, 31)
    months = _expand_field(expr.month, 1, 12)

    runs_per_hour = float(len(minutes))
    runs_per_day = runs_per_hour * len(hours)
    # approximate: average days per week in a month
    days_per_week = min(len(doms), 7)
    runs_per_week = runs_per_day * days_per_week
    runs_per_month = runs_per_day * len(doms) * (len(months) / 12.0)

    return ExpressionProfile(
        expression=str(expr),
        valid=True,
        runs_per_hour=runs_per_hour,
        runs_per_day=runs_per_day,
        runs_per_week=runs_per_week,
        runs_per_month=runs_per_month,
    )


def profile(expressions: List[str]) -> ProfileResult:
    """Profile a list of cron expression strings."""
    result = ProfileResult()
    for raw in expressions:
        try:
            expr = CronExpression.parse(raw)
            p = _compute_profile(expr)
            p.expression = raw
        except ParseError as exc:
            p = ExpressionProfile(expression=raw, valid=False, error=str(exc))
        result.profiles.append(p)
    return result
