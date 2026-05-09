"""Match cron expressions against a datetime to check if they fire."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .parser import CronExpression, ParseError, parse
from .schedule import _expand_field


@dataclass
class MatchResult:
    expression: str
    matched: bool
    error: str | None = None

    def __bool__(self) -> bool:
        return self.matched

    def __str__(self) -> str:
        if self.error:
            return f"{self.expression!r}: ERROR — {self.error}"
        status = "MATCH" if self.matched else "NO MATCH"
        return f"{self.expression!r}: {status}"


@dataclass
class BatchMatchResult:
    dt: datetime
    results: List[MatchResult] = field(default_factory=list)

    @property
    def matched_count(self) -> int:
        return sum(1 for r in self.results if r.matched)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)

    def matched_expressions(self) -> List[str]:
        return [r.expression for r in self.results if r.matched]

    def __str__(self) -> str:
        lines = [f"Matches at {self.dt.isoformat()}:"]
        for r in self.results:
            lines.append(f"  {r}")
        lines.append(f"  Total matched: {self.matched_count}/{len(self.results)}")
        return "\n".join(lines)


def _matches_expression(expr: CronExpression, dt: datetime) -> bool:
    """Return True if *expr* fires at the given datetime (minute precision)."""
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)
    days = _expand_field(expr.day, 1, 31)
    months = _expand_field(expr.month, 1, 12)
    dows = _expand_field(expr.dow, 0, 6)

    return (
        dt.minute in minutes
        and dt.hour in hours
        and dt.day in days
        and dt.month in months
        and dt.weekday() in {(d - 1) % 7 for d in dows}  # cron 0=Sun, Python 0=Mon
    )


def match(expression: str, dt: datetime) -> MatchResult:
    """Check whether *expression* fires at *dt*."""
    try:
        expr = parse(expression)
    except ParseError as exc:
        return MatchResult(expression=expression, matched=False, error=str(exc))
    try:
        matched = _matches_expression(expr, dt)
    except Exception as exc:  # pragma: no cover
        return MatchResult(expression=expression, matched=False, error=str(exc))
    return MatchResult(expression=expression, matched=matched)


def match_any(expressions: List[str], dt: datetime) -> BatchMatchResult:
    """Check each expression in *expressions* against *dt*."""
    results = [match(expr, dt) for expr in expressions]
    return BatchMatchResult(dt=dt, results=results)
