"""Build a merged, sorted timeline from multiple cron expressions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .forecaster import forecast


@dataclass
class TimelineEntry:
    """A single scheduled event on the timeline."""

    at: datetime
    expression: str

    def __str__(self) -> str:
        return f"{self.at.strftime('%Y-%m-%d %H:%M')}  {self.expression}"


@dataclass
class Timeline:
    """Sorted sequence of upcoming events across multiple expressions."""

    entries: List[TimelineEntry] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def event_count(self) -> int:
        return len(self.entries)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def expressions_at(self, dt: datetime) -> List[str]:
        """Return all expressions scheduled to run at *dt* (minute precision)."""
        target = dt.replace(second=0, microsecond=0)
        return [
            e.expression
            for e in self.entries
            if e.at.replace(second=0, microsecond=0) == target
        ]

    def __str__(self) -> str:
        lines = [str(e) for e in self.entries]
        for expr, err in self.errors.items():
            lines.append(f"ERROR [{expr}]: {err}")
        return "\n".join(lines) if lines else "(empty timeline)"


def build_timeline(
    expressions: List[str],
    n: int = 5,
    after: Optional[datetime] = None,
) -> Timeline:
    """Merge upcoming runs from *expressions* into a single sorted timeline.

    Parameters
    ----------
    expressions:
        Cron expression strings to include.
    n:
        Number of upcoming runs to fetch per expression.
    after:
        Reference datetime; defaults to ``datetime.utcnow()``.
    """
    if after is None:
        after = datetime.utcnow()

    result = forecast(expressions, n=n, after=after)

    entries: List[TimelineEntry] = []
    errors: Dict[str, str] = {}

    for fc in result.forecasts:
        if fc.valid:
            for run in fc.runs:
                entries.append(TimelineEntry(at=run, expression=fc.expression))
        else:
            errors[fc.expression] = fc.error or "unknown error"

    entries.sort(key=lambda e: e.at)
    return Timeline(entries=entries, errors=errors)
