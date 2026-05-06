"""Compute similarity scores between two cron expressions."""

from dataclasses import dataclass, field
from typing import Dict

from .parser import CronExpression

FIELD_NAMES = ["minute", "hour", "day", "month", "dow"]

FIELD_WEIGHTS: Dict[str, float] = {
    "minute": 0.20,
    "hour": 0.25,
    "day": 0.20,
    "month": 0.15,
    "dow": 0.20,
}


@dataclass
class SimilarityReport:
    """Holds per-field and overall similarity between two cron expressions."""

    expr_a: str
    expr_b: str
    field_scores: Dict[str, float] = field(default_factory=dict)
    overall: float = 0.0

    def __str__(self) -> str:
        lines = [
            f"Similarity: {self.expr_a!r} vs {self.expr_b!r}",
            f"  Overall : {self.overall:.0%}",
        ]
        for name in FIELD_NAMES:
            score = self.field_scores.get(name, 0.0)
            lines.append(f"  {name:<8}: {score:.0%}")
        return "\n".join(lines)


def _token_score(a: str, b: str) -> float:
    """Return 1.0 if tokens are identical, 0.5 if one is a wildcard, else 0.0."""
    if a == b:
        return 1.0
    if a == "*" or b == "*":
        return 0.5
    return 0.0


def _field_score(tokens_a: list, tokens_b: list) -> float:
    """Average token-level similarity between two field token lists."""
    if not tokens_a or not tokens_b:
        return 0.0
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    if set_a == set_b:
        return 1.0
    if "*" in set_a or "*" in set_b:
        return 0.5
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def compare(expr_a: CronExpression, expr_b: CronExpression) -> SimilarityReport:
    """Compare two parsed CronExpression objects and return a SimilarityReport."""
    field_scores: Dict[str, float] = {}
    for name in FIELD_NAMES:
        tokens_a = getattr(expr_a, name)
        tokens_b = getattr(expr_b, name)
        field_scores[name] = _field_score(tokens_a, tokens_b)

    overall = sum(
        field_scores[name] * FIELD_WEIGHTS[name] for name in FIELD_NAMES
    )
    return SimilarityReport(
        expr_a=str(expr_a),
        expr_b=str(expr_b),
        field_scores=field_scores,
        overall=overall,
    )


def similarity_score(expr_a: CronExpression, expr_b: CronExpression) -> float:
    """Return a single float in [0, 1] representing overall similarity."""
    return compare(expr_a, expr_b).overall
