"""Forecast upcoming run times for one or more cron expressions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .parser import CronExpression, ParseError, parse
from .schedule import next_n_runs


@dataclass
class ExpressionForecast:
    """Forecast for a single cron expression."""

    expression: str
    runs: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.error is None

    def __str__(self) -> str:
        if not self.valid:
            return f"[{self.expression}] ERROR: {self.error}"
        lines = [f"[{self.expression}]"]
        for dt in self.runs:
            lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
        return "\n".join(lines)


@dataclass
class ForecastResult:
    """Aggregated forecast for multiple expressions."""

    forecasts: List[ExpressionForecast] = field(default_factory=list)
    n: int = 5

    @property
    def valid_count(self) -> int:
        return sum(1 for f in self.forecasts if f.valid)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.forecasts if not f.valid)

    def __str__(self) -> str:
        return "\n\n".join(str(f) for f in self.forecasts)


def forecast(
    expressions: List[str],
    n: int = 5,
    after: Optional[datetime] = None,
) -> ForecastResult:
    """Return the next *n* run times for each expression in *expressions*.

    Parameters
    ----------
    expressions:
        List of cron expression strings.
    n:
        Number of upcoming run times to compute per expression.
    after:
        Reference datetime; defaults to ``datetime.utcnow()``.
    """
    if after is None:
        after = datetime.utcnow()

    forecasts: List[ExpressionForecast] = []
    for expr_str in expressions:
        try:
            expr: CronExpression = parse(expr_str)
            runs = next_n_runs(expr, n=n, after=after)
            forecasts.append(ExpressionForecast(expression=expr_str, runs=runs))
        except (ParseError, ValueError) as exc:
            forecasts.append(
                ExpressionForecast(expression=expr_str, error=str(exc))
            )

    return ForecastResult(forecasts=forecasts, n=n)
