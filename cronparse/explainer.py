"""Provides detailed field-by-field explanations for cron expressions."""

from cronparse.parser import CronExpression, CronField

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

DOW_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _explain_field(field: CronField, field_name: str) -> str:
    """Return a human-readable explanation for a single cron field."""
    raw = field.raw

    if raw == "*":
        return f"{field_name}: every {field_name.replace('_', ' ')}"

    if raw.startswith("*/"):
        step = raw[2:]
        return f"{field_name}: every {step} {field_name.replace('_', ' ')}(s)"

    if "-" in raw and "/" in raw:
        range_part, step = raw.split("/")
        start, end = range_part.split("-")
        return (
            f"{field_name}: every {step} {field_name.replace('_', ' ')}(s) "
            f"from {start} through {end}"
        )

    if "-" in raw:
        start, end = raw.split("-", 1)
        if field_name == "month":
            try:
                start = MONTH_NAMES[int(start)]
                end = MONTH_NAMES[int(end)]
            except (ValueError, IndexError):
                pass
        elif field_name == "day_of_week":
            try:
                start = DOW_NAMES[int(start)]
                end = DOW_NAMES[int(end)]
            except (ValueError, IndexError):
                pass
        return f"{field_name}: from {start} through {end}"

    if "," in raw:
        parts = raw.split(",")
        if field_name == "month":
            parts = [MONTH_NAMES[int(p)] if p.isdigit() else p for p in parts]
        elif field_name == "day_of_week":
            parts = [DOW_NAMES[int(p)] if p.isdigit() else p for p in parts]
        return f"{field_name}: at {', '.join(parts)}"

    value = raw
    if field_name == "month" and raw.isdigit():
        try:
            value = MONTH_NAMES[int(raw)]
        except IndexError:
            pass
    elif field_name == "day_of_week" and raw.isdigit():
        try:
            value = DOW_NAMES[int(raw)]
        except IndexError:
            pass

    return f"{field_name}: at {value}"


def explain(expr: CronExpression) -> dict:
    """Return a dict mapping each field name to its explanation string."""
    fields = [
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    ]
    return {
        name: _explain_field(field, name)
        for name, field in zip(FIELD_NAMES, fields)
    }


def explain_text(expr: CronExpression) -> str:
    """Return a multi-line text explanation of the cron expression."""
    explanations = explain(expr)
    lines = [f"Expression: {expr.raw}"]
    lines.append("-" * 40)
    for description in explanations.values():
        lines.append(f"  {description}")
    return "\n".join(lines)
