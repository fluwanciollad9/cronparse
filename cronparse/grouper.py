"""Group multiple cron expressions by shared field patterns."""

from dataclasses import dataclass, field
from typing import Dict, List
from cronparse.parser import CronExpression, ParseError
from cronparse.normalizer import normalize


@dataclass
class GroupResult:
    groups: Dict[str, List[str]]
    errors: Dict[str, str]

    def __str__(self) -> str:
        lines = []
        for key, expressions in self.groups.items():
            lines.append(f"[{key}]")
            for expr in expressions:
                lines.append(f"  {expr}")
        if self.errors:
            lines.append("[errors]")
            for expr, msg in self.errors.items():
                lines.append(f"  {expr}: {msg}")
        return "\n".join(lines)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def error_count(self) -> int:
        return len(self.errors)


def _group_key(parsed: CronExpression, by: str) -> str:
    """Return the normalized value of the requested field."""
    field_map = {
        "minute": parsed.minute,
        "hour": parsed.hour,
        "dom": parsed.dom,
        "month": parsed.month,
        "dow": parsed.dow,
    }
    if by not in field_map:
        raise ValueError(f"Unknown grouping field: {by!r}. Choose from {list(field_map)}.")
    return field_map[by]


def group(expressions: List[str], by: str = "hour") -> GroupResult:
    """Group cron expression strings by the normalized value of a given field.

    Args:
        expressions: List of cron expression strings.
        by: Which field to group by ('minute', 'hour', 'dom', 'month', 'dow').

    Returns:
        A GroupResult with groups mapping field values to expression lists,
        and errors for any unparseable inputs.
    """
    groups: Dict[str, List[str]] = {}
    errors: Dict[str, str] = {}

    for raw in expressions:
        try:
            normalized = normalize(raw)
            parsed = CronExpression.parse(normalized)
            key = _group_key(parsed, by)
        except (ParseError, ValueError) as exc:
            errors[raw] = str(exc)
            continue

        groups.setdefault(key, []).append(raw)

    return GroupResult(groups=groups, errors=errors)
