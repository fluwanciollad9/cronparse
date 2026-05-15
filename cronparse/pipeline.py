"""Composable pipeline for chaining filter and transform steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .filter import FilterResult, filter_by_field, filter_by_predicate, filter_by_tag
from .normalizer import normalize_string
from .parser import CronExpression


Step = Callable[[List[str]], List[str]]


@dataclass
class PipelineResult:
    """Final state after all pipeline steps have been applied."""

    output: List[str] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def output_count(self) -> int:
        return len(self.output)

    @property
    def dropped_count(self) -> int:
        return len(self.dropped)

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"PipelineResult: {self.output_count} kept, "
            f"{self.dropped_count} dropped, {len(self.errors)} errors"
        )


class Pipeline:
    """Build and execute a chain of filter steps over cron expressions."""

    def __init__(self) -> None:
        self._steps: List[tuple] = []  # (kind, *args)

    # --- builder interface ---

    def filter_field(self, field_name: str, value: str) -> "Pipeline":
        self._steps.append(("field", field_name, value))
        return self

    def filter_tag(self, tag_name: str) -> "Pipeline":
        self._steps.append(("tag", tag_name))
        return self

    def filter_predicate(self, predicate: Callable[[CronExpression], bool]) -> "Pipeline":
        self._steps.append(("predicate", predicate))
        return self

    def normalize(self) -> "Pipeline":
        self._steps.append(("normalize",))
        return self

    # --- execution ---

    def run(self, expressions: List[str]) -> PipelineResult:
        current = list(expressions)
        all_dropped: List[str] = []
        all_errors: List[str] = []

        for step in self._steps:
            kind = step[0]
            if kind == "field":
                fr: FilterResult = filter_by_field(current, step[1], step[2])
            elif kind == "tag":
                fr = filter_by_tag(current, step[1])
            elif kind == "predicate":
                fr = filter_by_predicate(current, step[1])
            elif kind == "normalize":
                current = [normalize_string(e) for e in current]
                continue
            else:
                continue  # unknown step – skip

            all_dropped.extend(fr.rejected)
            all_errors.extend(fr.errors)
            current = fr.matched

        return PipelineResult(output=current, dropped=all_dropped, errors=all_errors)
