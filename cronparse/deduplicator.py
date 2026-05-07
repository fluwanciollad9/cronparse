"""Deduplication of cron expressions — identify and remove duplicate or equivalent entries."""

from dataclasses import dataclass, field
from typing import List, Tuple

from cronparse.parser import CronExpression, ParseError
from cronparse.normalizer import normalize_string


@dataclass
class DeduplicationResult:
    """Result of deduplicating a list of cron expressions."""
    unique: List[str]
    duplicates: List[Tuple[str, str]]  # (duplicate, canonical original)
    errors: List[Tuple[str, str]]      # (expression, error message)

    def __str__(self) -> str:
        lines = [f"Unique expressions: {len(self.unique)}"]
        if self.duplicates:
            lines.append(f"Duplicates found: {len(self.duplicates)}")
            for dup, orig in self.duplicates:
                lines.append(f"  '{dup}' is a duplicate of '{orig}'")
        if self.errors:
            lines.append(f"Invalid expressions: {len(self.errors)}")
            for expr, err in self.errors:
                lines.append(f"  '{expr}': {err}")
        return "\n".join(lines)


def _normalize_key(expression: str) -> str:
    """Return a normalized form of the expression for equality comparison."""
    try:
        return normalize_string(expression)
    except Exception:
        return expression.strip()


def deduplicate(expressions: List[str]) -> DeduplicationResult:
    """Deduplicate a list of cron expression strings.

    Two expressions are considered duplicates if their normalized forms are
    identical. The first occurrence is kept as the canonical entry.

    Args:
        expressions: List of cron expression strings.

    Returns:
        A DeduplicationResult with unique entries, duplicates, and errors.
    """
    unique: List[str] = []
    duplicates: List[Tuple[str, str]] = []
    errors: List[Tuple[str, str]] = []
    seen: dict = {}  # normalized key -> original expression

    for expr in expressions:
        try:
            CronExpression.parse(expr)
        except ParseError as exc:
            errors.append((expr, str(exc)))
            continue

        key = _normalize_key(expr)
        if key in seen:
            duplicates.append((expr, seen[key]))
        else:
            seen[key] = expr
            unique.append(expr)

    return DeduplicationResult(unique=unique, duplicates=duplicates, errors=errors)
