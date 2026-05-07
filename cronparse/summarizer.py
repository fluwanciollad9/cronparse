"""Summarize and compare multiple cron expressions at once."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize
from cronparse.tags import tag


@dataclass
class ExpressionSummary:
    raw: str
    expression: Optional[CronExpression]
    human: Optional[str]
    tags: List[str]
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.error:
            return f"[ERROR] {self.raw}: {self.error}"
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return f"{self.raw!r} => {self.human} (tags: {tag_str})"


@dataclass
class MultiSummary:
    summaries: List[ExpressionSummary]
    total: int
    valid: int
    invalid: int
    common_tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"MultiSummary: {self.valid}/{self.total} valid expressions"]
        if self.common_tags:
            lines.append(f"Common tags: {', '.join(self.common_tags)}")
        for s in self.summaries:
            lines.append(f"  {s}")
        return "\n".join(lines)


def _summarize_one(raw: str) -> ExpressionSummary:
    try:
        expr = CronExpression.parse(raw)
        human = humanize(expr)
        tag_result = tag(expr)
        tags = tag_result.tags
        return ExpressionSummary(raw=raw, expression=expr, human=human, tags=tags)
    except (ParseError, Exception) as exc:
        return ExpressionSummary(
            raw=raw, expression=None, human=None, tags=[], error=str(exc)
        )


def summarize(expressions: List[str]) -> MultiSummary:
    """Summarize a list of raw cron expression strings."""
    summaries = [_summarize_one(raw) for raw in expressions]
    valid = [s for s in summaries if s.error is None]
    invalid = [s for s in summaries if s.error is not None]

    if valid:
        tag_sets = [set(s.tags) for s in valid]
        common = set.intersection(*tag_sets) if tag_sets else set()
        common_tags = sorted(common)
    else:
        common_tags = []

    return MultiSummary(
        summaries=summaries,
        total=len(summaries),
        valid=len(valid),
        invalid=len(invalid),
        common_tags=common_tags,
    )


def group_by_tag(multi: MultiSummary) -> Dict[str, List[ExpressionSummary]]:
    """Group valid summaries by their tags."""
    groups: Dict[str, List[ExpressionSummary]] = {}
    for s in multi.summaries:
        if s.error:
            continue
        for t in s.tags:
            groups.setdefault(t, []).append(s)
    return groups
