"""Core cron expression parser module."""

from dataclasses import dataclass
from typing import List, Optional


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    values: List[int]


@dataclass
class CronExpression:
    raw: str
    fields: List[CronField]

    def as_dict(self) -> dict:
        return {f.name: f.values for f in self.fields}


class ParseError(ValueError):
    pass


def _resolve_alias(value: str, field_name: str) -> str:
    lower = value.lower()
    if field_name == "month" and lower in MONTH_ALIASES:
        return str(MONTH_ALIASES[lower])
    if field_name == "day_of_week" and lower in DOW_ALIASES:
        return str(DOW_ALIASES[lower])
    return value


def _parse_int(value: str, field_name: str, context: str) -> int:
    """Parse an integer from a string, raising ParseError on failure."""
    try:
        return int(value)
    except ValueError:
        raise ParseError(
            f"Expected an integer in field '{field_name}', got '{value}' in '{context}'"
        )


def _parse_field(raw: str, field_name: str) -> List[int]:
    min_val, max_val = FIELD_RANGES[field_name]
    values = set()

    for part in raw.split(","):
        part = _resolve_alias(part, field_name)
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:
            base, step_str = part.split("/", 1)
            step = _parse_int(step_str, field_name, part)
            if step <= 0:
                raise ParseError(f"Step must be positive in field '{field_name}': {part}")
            start = min_val if base == "*" else _parse_int(base, field_name, part)
            values.update(range(start, max_val + 1, step))
        elif "-" in part:
            start_str, end_str = part.split("-", 1)
            start, end = _parse_int(start_str, field_name, part), _parse_int(end_str, field_name, part)
            if start > end:
                raise ParseError(f"Invalid range in field '{field_name}': {part}")
            values.update(range(start, end + 1))
        else:
            values.add(_parse_int(part, field_name, part))

    out_of_range = [v for v in values if not (min_val <= v <= max_val)]
    if out_of_range:
        raise ParseError(
            f"Values {out_of_range} out of range [{min_val},{max_val}] for field '{field_name}'"
        )

    return sorted(values)


def parse(expression: str) -> CronExpression:
    """Parse a cron expression string into a CronExpression object."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ParseError(
            f"Expected 5 fields, got {len(parts)}: '{expression}'"
        )

    fields = [
        CronField(name=name, raw=raw, values=_parse_field(raw, name))
        for name, raw in zip(FIELD_NAMES, parts)
    ]
    return CronExpression(raw=expression, fields=fields)
