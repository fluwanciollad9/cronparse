"""Batch comparison of cron expressions against a reference expression."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, ParseError
from .similarity import compare, SimilarityReport


@dataclass
class ComparisonEntry:
    """Result of comparing one expression against a reference."""

    expression: str
    reference: str
    score: float
    report: Optional[SimilarityReport]
    error: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.error is None

    def __str__(self) -> str:
        if not self.valid:
            return f"{self.expression!r} vs {self.reference!r}: ERROR — {self.error}"
        return (
            f"{self.expression!r} vs {self.reference!r}: "
            f"similarity={self.score:.2f}"
        )


@dataclass
class ComparisonResult:
    """Aggregated result of comparing many expressions to a single reference."""

    reference: str
    entries: List[ComparisonEntry] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.valid)

    @property
    def error_count(self) -> int:
        return len(self.entries) - self.valid_count

    def best(self) -> Optional[ComparisonEntry]:
        valid = [e for e in self.entries if e.valid]
        return max(valid, key=lambda e: e.score) if valid else None

    def above_threshold(self, threshold: float = 0.8) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.valid and e.score >= threshold]

    def __str__(self) -> str:
        lines = [f"Reference: {self.reference!r} — {len(self.entries)} compared"]
        for entry in self.entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)


def compare_many(reference: str, expressions: List[str]) -> ComparisonResult:
    """Compare each expression in *expressions* against *reference*.

    Args:
        reference: The baseline cron expression string.
        expressions: List of cron expression strings to compare.

    Returns:
        A :class:`ComparisonResult` containing one entry per expression.
    """
    result = ComparisonResult(reference=reference)

    try:
        ref_expr = CronExpression.parse(reference)
    except (ParseError, ValueError) as exc:
        # If the reference itself is invalid every entry gets the same error.
        for expr_str in expressions:
            result.entries.append(
                ComparisonEntry(
                    expression=expr_str,
                    reference=reference,
                    score=0.0,
                    report=None,
                    error=f"Invalid reference: {exc}",
                )
            )
        return result

    for expr_str in expressions:
        try:
            candidate = CronExpression.parse(expr_str)
            report = compare(ref_expr, candidate)
            result.entries.append(
                ComparisonEntry(
                    expression=expr_str,
                    reference=reference,
                    score=report.overall_score,
                    report=report,
                )
            )
        except (ParseError, ValueError) as exc:
            result.entries.append(
                ComparisonEntry(
                    expression=expr_str,
                    reference=reference,
                    score=0.0,
                    report=None,
                    error=str(exc),
                )
            )

    return result
