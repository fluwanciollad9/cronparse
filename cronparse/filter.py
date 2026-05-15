"""Filter a collection of cron expressions by various criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, ParseError, parse
from .tags import tag


@dataclass
class FilterResult:
    """Result of a filter operation over multiple cron expressions."""

    matched: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def reject_count(self) -> int:
        return len(self.rejected)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"FilterResult: {self.match_count} matched, "
            f"{self.reject_count} rejected, {self.error_count} errors",
        ]
        for expr in self.matched:
            lines.append(f"  + {expr}")
        return "\n".join(lines)


def filter_by_field(
    expressions: List[str],
    field_name: str,
    value: str,
) -> FilterResult:
    """Keep expressions where *field_name* equals *value* (supports '*')."""
    _FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]
    if field_name not in _FIELD_NAMES:
        raise ValueError(f"Unknown field: {field_name!r}. Choose from {_FIELD_NAMES}")

    result = FilterResult()
    idx = _FIELD_NAMES.index(field_name)
    for raw in expressions:
        try:
            expr: CronExpression = parse(raw)
        except ParseError as exc:
            result.errors.append(raw)
            continue
        parts = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
        if parts[idx] == value:
            result.matched.append(raw)
        else:
            result.rejected.append(raw)
    return result


def filter_by_tag(
    expressions: List[str],
    tag_name: str,
) -> FilterResult:
    """Keep expressions that carry *tag_name* (as produced by tags.tag)."""
    result = FilterResult()
    for raw in expressions:
        try:
            tag_result = tag(raw)
        except Exception:
            result.errors.append(raw)
            continue
        if tag_result.has_tag(tag_name):
            result.matched.append(raw)
        else:
            result.rejected.append(raw)
    return result


def filter_by_predicate(
    expressions: List[str],
    predicate,
) -> FilterResult:
    """Keep expressions for which *predicate(CronExpression)* returns True."""
    result = FilterResult()
    for raw in expressions:
        try:
            expr: CronExpression = parse(raw)
        except ParseError:
            result.errors.append(raw)
            continue
        if predicate(expr):
            result.matched.append(raw)
        else:
            result.rejected.append(raw)
    return result
