"""Formatter module for converting CronExpression objects to various output formats."""

from typing import Any, Dict
from cronparse.parser import CronExpression, as_dict


def to_dict(expr: CronExpression) -> Dict[str, Any]:
    """Convert a CronExpression to a plain dictionary representation."""
    return as_dict(expr)


def to_json(expr: CronExpression, indent: int = 2) -> str:
    """Serialize a CronExpression to a JSON string."""
    import json
    data = {
        "expression": expr.raw,
        "fields": as_dict(expr),
    }
    return json.dumps(data, indent=indent)


def to_table(expr: CronExpression) -> str:
    """Format a CronExpression as a human-readable table string."""
    fields = as_dict(expr)
    header = f"{'Field':<20} {'Value':<20}"
    separator = "-" * 42
    rows = [header, separator]
    field_labels = [
        ("minute", "Minute"),
        ("hour", "Hour"),
        ("day_of_month", "Day of Month"),
        ("month", "Month"),
        ("day_of_week", "Day of Week"),
    ]
    for key, label in field_labels:
        value = fields.get(key, "*")
        rows.append(f"{label:<20} {str(value):<20}")
    if hasattr(expr, "raw"):
        rows.append(separator)
        rows.append(f"Expression: {expr.raw}")
    return "\n".join(rows)


def to_cron_string(expr: CronExpression) -> str:
    """Reconstruct the canonical cron string from a CronExpression."""
    fields = as_dict(expr)
    parts = [
        str(fields.get("minute", "*")),
        str(fields.get("hour", "*")),
        str(fields.get("day_of_month", "*")),
        str(fields.get("month", "*")),
        str(fields.get("day_of_week", "*")),
    ]
    return " ".join(parts)
