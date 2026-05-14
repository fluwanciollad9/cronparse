"""Classify cron expressions into human-readable categories."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import CronExpression, ParseError, parse
from cronparse.schedule import _expand_field


CATEGORY_EVERY_MINUTE = "every-minute"
CATEGORY_SUB_HOURLY = "sub-hourly"
CATEGORY_HOURLY = "hourly"
CATEGORY_DAILY = "daily"
CATEGORY_WEEKLY = "weekly"
CATEGORY_MONTHLY = "monthly"
CATEGORY_YEARLY = "yearly"
CATEGORY_CUSTOM = "custom"


@dataclass
class ClassificationResult:
    expression: str
    category: Optional[str]
    error: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.error is None

    def __str__(self) -> str:
        if not self.valid:
            return f"{self.expression!r}: error — {self.error}"
        return f"{self.expression!r}: {self.category}"


@dataclass
class BatchClassification:
    results: List[ClassificationResult] = field(default_factory=list)

    @property
    def valid_count(self) -> int:
        return sum(1 for r in self.results if r.valid)

    @property
    def error_count(self) -> int:
        return len(self.results) - self.valid_count

    def by_category(self) -> dict:
        groups: dict = {}
        for r in self.results:
            if r.valid:
                groups.setdefault(r.category, []).append(r.expression)
        return groups

    def __str__(self) -> str:
        lines = [str(r) for r in self.results]
        return "\n".join(lines)


def _classify_expression(expr: CronExpression) -> str:
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)
    doms = _expand_field(expr.dom, 1, 31)
    months = _expand_field(expr.month, 1, 12)
    dows = _expand_field(expr.dow, 0, 6)

    all_minutes = len(minutes) == 60
    all_hours = len(hours) == 24
    all_doms = len(doms) == 31
    all_months = len(months) == 12
    all_dows = len(dows) == 7

    if all_minutes and all_hours and all_doms and all_months and all_dows:
        return CATEGORY_EVERY_MINUTE
    if all_hours and all_doms and all_months and all_dows:
        return CATEGORY_SUB_HOURLY if len(minutes) > 1 else CATEGORY_HOURLY
    if len(hours) == 1 and all_doms and all_months and all_dows:
        return CATEGORY_DAILY
    if not all_dows and all_doms and all_months:
        return CATEGORY_WEEKLY
    if not all_doms and all_months and all_dows:
        return CATEGORY_MONTHLY
    if not all_months:
        return CATEGORY_YEARLY
    return CATEGORY_CUSTOM


def classify(expression: str) -> ClassificationResult:
    try:
        expr = parse(expression)
        category = _classify_expression(expr)
        return ClassificationResult(expression=expression, category=category)
    except ParseError as exc:
        return ClassificationResult(expression=expression, category=None, error=str(exc))


def classify_many(expressions: List[str]) -> BatchClassification:
    return BatchClassification(results=[classify(e) for e in expressions])
