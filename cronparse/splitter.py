"""Split a list of cron expressions into time-based buckets (hourly, daily, weekly, etc.)."""

from dataclasses import dataclass, field
from typing import Dict, List

from cronparse.parser import CronExpression, ParseError
from cronparse.normalizer import normalize


@dataclass
class SplitResult:
    """Result of splitting cron expressions into frequency buckets."""
    buckets: Dict[str, List[str]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = []
        for bucket, expressions in sorted(self.buckets.items()):
            lines.append(f"[{bucket}] ({len(expressions)} expression(s))")
            for expr in expressions:
                lines.append(f"  {expr}")
        if self.errors:
            lines.append("[errors]")
            for expr, msg in self.errors.items():
                lines.append(f"  {expr}: {msg}")
        return "\n".join(lines) if lines else "(empty)"

    def bucket_count(self) -> int:
        return len(self.buckets)

    def error_count(self) -> int:
        return len(self.errors)


def _classify(expr: CronExpression) -> str:
    """Classify a parsed cron expression into a frequency bucket name."""
    minute = expr.minute
    hour = expr.hour
    dom = expr.dom
    dow = expr.dow

    # Every minute
    if minute == "*" and hour == "*" and dom == "*" and dow == "*":
        return "every_minute"

    # Multiple times per hour (step on minute)
    if minute.startswith("*/") and hour == "*":
        return "sub_hourly"

    # Hourly: runs once per hour at a fixed minute
    if hour == "*" and dom == "*" and dow == "*":
        return "hourly"

    # Multiple times per day (step on hour)
    if hour.startswith("*/") and dom == "*" and dow == "*":
        return "multi_daily"

    # Weekly: restricted by day-of-week
    if dow != "*":
        return "weekly"

    # Monthly: restricted by day-of-month
    if dom != "*":
        return "monthly"

    # Daily fallback
    return "daily"


def split(expressions: List[str]) -> SplitResult:
    """Split cron expression strings into labelled frequency buckets."""
    result = SplitResult()
    for raw in expressions:
        normalized = normalize(raw)
        try:
            expr = CronExpression.parse(normalized)
        except (ParseError, ValueError) as exc:
            result.errors[raw] = str(exc)
            continue
        bucket = _classify(expr)
        result.buckets.setdefault(bucket, []).append(raw)
    return result
