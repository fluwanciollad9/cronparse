"""Annotator module: attach human-readable annotations to each cron field."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import CronExpression, ParseError, _resolve_alias
from .humanizer import _humanize_field, _humanize_dow, _humanize_month
from .validator import validate_field


FIELD_NAMES = ["minute", "hour", "day", "month", "dow"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "dow": (0, 6),
}


@dataclass
class FieldAnnotation:
    name: str
    raw: str
    human: str
    valid: bool
    notes: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "OK" if self.valid else "INVALID"
        notes_str = f" [{', '.join(self.notes)}]" if self.notes else ""
        return f"{self.name}: {self.raw!r} => {self.human}{notes_str} ({status})"


@dataclass
class AnnotationResult:
    expression: str
    annotations: List[FieldAnnotation] = field(default_factory=list)
    parse_error: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.parse_error is None and all(a.valid for a in self.annotations)

    def as_dict(self) -> Dict:
        if self.parse_error:
            return {"expression": self.expression, "error": self.parse_error}
        return {
            "expression": self.expression,
            "valid": self.valid,
            "fields": [
                {"name": a.name, "raw": a.raw, "human": a.human, "valid": a.valid, "notes": a.notes}
                for a in self.annotations
            ],
        }

    def __str__(self) -> str:
        if self.parse_error:
            return f"AnnotationResult({self.expression!r}): ERROR - {self.parse_error}"
        lines = [f"AnnotationResult({self.expression!r}):"] + [f"  {a}" for a in self.annotations]
        return "\n".join(lines)


def _build_notes(name: str, raw: str) -> List[str]:
    notes = []
    if raw == "*":
        notes.append("wildcard")
    elif "/1" in raw:
        notes.append("step-of-one is redundant")
    if name == "dow" and raw == "7":
        notes.append("7 is non-standard for Sunday; prefer 0")
    return notes


def annotate(expression: str) -> AnnotationResult:
    """Parse a cron expression and return per-field annotations."""
    try:
        expr = CronExpression.parse(expression)
    except ParseError as exc:
        return AnnotationResult(expression=expression, parse_error=str(exc))

    raw_fields = [expr.minute, expr.hour, expr.day, expr.month, expr.dow]
    annotations: List[FieldAnnotation] = []

    for name, raw in zip(FIELD_NAMES, raw_fields):
        lo, hi = FIELD_RANGES[name]
        vresult = validate_field(raw, lo, hi)
        if name == "dow":
            human = _humanize_dow(raw)
        elif name == "month":
            human = _humanize_month(raw)
        else:
            human = _humanize_field(raw, name)
        notes = _build_notes(name, raw)
        annotations.append(
            FieldAnnotation(name=name, raw=raw, human=human, valid=bool(vresult), notes=notes)
        )

    return AnnotationResult(expression=expression, annotations=annotations)
