"""Rank and sort cron expressions by various criteria."""

from dataclasses import dataclass, field
from typing import List, Tuple
from .parser import CronExpression, ParseError, parse
from .schedule import _expand_field


@dataclass
class RankedExpression:
    expression: str
    score: float
    rank: int
    reason: str

    def __str__(self) -> str:
        return f"[#{self.rank}] {self.expression!r} (score={self.score:.3f}) — {self.reason}"


@dataclass
class RankResult:
    ranked: List[RankedExpression] = field(default_factory=list)
    errors: List[Tuple[str, str]] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        for r in self.ranked:
            lines.append(str(r))
        for expr, err in self.errors:
            lines.append(f"[ERROR] {expr!r}: {err}")
        return "\n".join(lines) if lines else "(empty)"


def _frequency_score(expr: CronExpression) -> float:
    """Lower score = runs more frequently."""
    try:
        minutes = len(_expand_field(expr.minute, 0, 59))
        hours = len(_expand_field(expr.hour, 0, 23))
        days = len(_expand_field(expr.day_of_month, 1, 31))
        months = len(_expand_field(expr.month, 1, 12))
        dows = len(_expand_field(expr.day_of_week, 0, 6))
    except Exception:
        return float("inf")
    return minutes * hours * days * months * dows


def _describe_frequency(score: float) -> str:
    if score <= 60:
        return "very frequent (multiple times per hour)"
    elif score <= 1440:
        return "frequent (multiple times per day)"
    elif score <= 10080:
        return "moderate (multiple times per week)"
    elif score <= 44640:
        return "infrequent (a few times per month)"
    else:
        return "rare (less than monthly)"


def rank(expressions: List[str], reverse: bool = False) -> RankResult:
    """Rank cron expressions by run frequency.

    Args:
        expressions: List of cron expression strings.
        reverse: If True, rank rarest first (highest score first).

    Returns:
        RankResult with ranked expressions and any parse errors.
    """
    result = RankResult()
    scored: List[Tuple[float, str, CronExpression]] = []

    for expr_str in expressions:
        try:
            expr = parse(expr_str)
            score = _frequency_score(expr)
            scored.append((score, expr_str, expr))
        except ParseError as e:
            result.errors.append((expr_str, str(e)))

    scored.sort(key=lambda t: t[0], reverse=reverse)

    for rank_idx, (score, expr_str, _expr) in enumerate(scored, start=1):
        reason = _describe_frequency(score)
        result.ranked.append(
            RankedExpression(
                expression=expr_str,
                score=score,
                rank=rank_idx,
                reason=reason,
            )
        )

    return result
