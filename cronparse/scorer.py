"""Score cron expressions by complexity and readability."""

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, ParseError, parse


@dataclass
class ExpressionScore:
    expression: str
    valid: bool
    complexity: int
    readability: int
    overall: float
    notes: List[str] = field(default_factory=list)
    error: str = ""

    def __str__(self) -> str:
        if not self.valid:
            return f"[invalid] {self.expression}: {self.error}"
        return (
            f"{self.expression} | complexity={self.complexity} "
            f"readability={self.readability} overall={self.overall:.2f}"
        )


@dataclass
class ScoreResult:
    scores: List[ExpressionScore] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return sum(1 for s in self.scores if s.valid)

    @property
    def error_count(self) -> int:
        return sum(1 for s in self.scores if not s.valid)

    @property
    def average_overall(self) -> float:
        valid = [s.overall for s in self.scores if s.valid]
        return sum(valid) / len(valid) if valid else 0.0

    def __str__(self) -> str:
        lines = [str(s) for s in self.scores]
        lines.append(f"avg_overall={self.average_overall:.2f}")
        return "\n".join(lines)


def _complexity_score(expr: CronExpression) -> int:
    """Higher = more complex."""
    score = 0
    for f in [expr.minute, expr.hour, expr.day, expr.month, expr.dow]:
        if f == "*":
            score += 0
        elif "," in f:
            score += len(f.split(",")) + 1
        elif "/" in f:
            score += 2
        elif "-" in f:
            score += 2
        else:
            score += 1
    return score


def _readability_score(expr: CronExpression) -> int:
    """Higher = more readable (0-10 scale)."""
    score = 10
    for f in [expr.minute, expr.hour, expr.day, expr.month, expr.dow]:
        if "," in f and len(f.split(",")) > 4:
            score -= 2
        if "/" in f:
            score -= 1
        if "-" in f and "/" in f:
            score -= 1
    return max(0, score)


def _score_one(expression: str) -> ExpressionScore:
    try:
        expr = parse(expression)
    except ParseError as exc:
        return ExpressionScore(
            expression=expression,
            valid=False,
            complexity=0,
            readability=0,
            overall=0.0,
            error=str(exc),
        )

    complexity = _complexity_score(expr)
    readability = _readability_score(expr)
    overall = round(readability / (1 + complexity * 0.5), 2)

    notes: List[str] = []
    if complexity == 0:
        notes.append("wildcard-only")
    if readability == 10:
        notes.append("highly-readable")
    if complexity > 10:
        notes.append("high-complexity")

    return ExpressionScore(
        expression=expression,
        valid=True,
        complexity=complexity,
        readability=readability,
        overall=overall,
        notes=notes,
    )


def score(expressions: List[str]) -> ScoreResult:
    """Score a list of cron expression strings."""
    return ScoreResult(scores=[_score_one(e) for e in expressions])
