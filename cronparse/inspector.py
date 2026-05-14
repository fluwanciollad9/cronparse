"""Inspector module: deep field-level inspection of a cron expression."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, ParseError, parse
from .validator import validate


@dataclass
class FieldInspection:
    """Inspection details for a single cron field."""

    name: str
    raw: str
    is_wildcard: bool
    is_step: bool
    is_range: bool
    is_list: bool
    token_count: int
    min_value: Optional[int]
    max_value: Optional[int]

    def __str__(self) -> str:
        flags = []
        if self.is_wildcard:
            flags.append("wildcard")
        if self.is_step:
            flags.append("step")
        if self.is_range:
            flags.append("range")
        if self.is_list:
            flags.append("list")
        flag_str = ", ".join(flags) if flags else "literal"
        return f"{self.name}={self.raw!r} [{flag_str}]"


@dataclass
class InspectionResult:
    """Result of inspecting a full cron expression."""

    expression: str
    valid: bool
    error: Optional[str]
    fields: List[FieldInspection] = field(default_factory=list)

    def __str__(self) -> str:
        if not self.valid:
            return f"InspectionResult(invalid): {self.error}"
        lines = [f"InspectionResult({self.expression!r})"]
        for f_ in self.fields:
            lines.append(f"  {f_}")
        return "\n".join(lines)


_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


def _inspect_token(token: str, lo: int, hi: int) -> FieldInspection:
    """Derive inspection flags from a raw field token."""
    is_wildcard = token == "*"
    is_step = "/" in token
    is_range = "-" in token.lstrip("-") if not is_step else ("-" in token.split("/")[0])
    is_list = "," in token
    tokens = token.split(",")
    token_count = len(tokens)

    min_val: Optional[int] = None
    max_val: Optional[int] = None
    if is_wildcard:
        min_val, max_val = lo, hi
    else:
        nums = []
        for t in tokens:
            base = t.split("/")[0]
            if "-" in base:
                parts = base.split("-")
                try:
                    nums += [int(p) for p in parts if p.isdigit()]
                except ValueError:
                    pass
            elif base.isdigit():
                nums.append(int(base))
        if nums:
            min_val, max_val = min(nums), max(nums)

    return FieldInspection(
        name="",
        raw=token,
        is_wildcard=is_wildcard,
        is_step=is_step,
        is_range=is_range,
        is_list=is_list,
        token_count=token_count,
        min_value=min_val,
        max_value=max_val,
    )


def inspect(expression: str) -> InspectionResult:
    """Inspect a cron expression and return per-field details."""
    vr = validate(expression)
    if not vr:
        return InspectionResult(expression=expression, valid=False, error=str(vr))

    try:
        expr: CronExpression = parse(expression)
    except ParseError as exc:
        return InspectionResult(expression=expression, valid=False, error=str(exc))

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    raw_fields = [expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week]

    inspections: List[FieldInspection] = []
    for name, raw in zip(field_names, raw_fields):
        lo, hi = _FIELD_RANGES[name]
        fi = _inspect_token(raw, lo, hi)
        fi.name = name
        inspections.append(fi)

    return InspectionResult(expression=expression, valid=True, error=None, fields=inspections)
