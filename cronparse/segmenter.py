"""Segment a list of cron expressions into time-based buckets (hourly slots)."""

from dataclasses import dataclass, field
from typing import Dict, List

from cronparse.parser import CronExpression, ParseError
from cronparse.schedule import _expand_field


@dataclass
class SegmentResult:
    """Result of segmenting cron expressions by hour-of-day slot."""

    segments: Dict[int, List[str]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def __str__(self) -> str:
        lines = []
        for hour in sorted(self.segments):
            exprs = ", ".join(self.segments[hour])
            lines.append(f"Hour {hour:02d}: {exprs}")
        if self.errors:
            lines.append("Errors:")
            for expr, msg in self.errors.items():
                lines.append(f"  {expr!r}: {msg}")
        return "\n".join(lines) if lines else "(no segments)"


def segment(expressions: List[str]) -> SegmentResult:
    """Segment cron expressions by the hours they are active.

    Each expression may appear in multiple hour buckets if it runs
    across several hours (e.g. a wildcard hour field).

    Args:
        expressions: List of 5-field cron expression strings.

    Returns:
        SegmentResult mapping hour integers to lists of expressions.
    """
    segments: Dict[int, List[str]] = {}
    errors: Dict[str, str] = {}

    for raw in expressions:
        try:
            expr = CronExpression.parse(raw)
        except ParseError as exc:
            errors[raw] = str(exc)
            continue

        try:
            hours = _expand_field(expr.hour, 0, 23)
        except Exception as exc:  # pragma: no cover
            errors[raw] = f"expand error: {exc}"
            continue

        for h in hours:
            segments.setdefault(h, [])
            if raw not in segments[h]:
                segments[h].append(raw)

    return SegmentResult(segments=segments, errors=errors)
