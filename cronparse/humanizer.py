"""Humanize cron expressions into readable English descriptions."""

from typing import Union
from cronparse.parser import CronExpression, CronField, ParseError


def _humanize_field(field: CronField, unit: str, singular: str) -> str:
    """Convert a single CronField into a human-readable string."""
    if field.wildcard:
        return f"every {singular}"

    if field.step and field.wildcard_base:
        return f"every {field.step} {unit}s"

    if field.step and field.range_start is not None and field.range_end is not None:
        return (
            f"every {field.step} {unit}s from {field.range_start} "
            f"through {field.range_end}"
        )

    if field.range_start is not None and field.range_end is not None:
        return f"from {field.range_start} through {field.range_end}"

    if field.values:
        items = ", ".join(str(v) for v in sorted(field.values))
        label = singular if len(field.values) == 1 else unit
        return f"at {label} {items}"

    return f"every {singular}"


DAY_NAMES = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday",
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


def _humanize_dow(field: CronField) -> str:
    if field.wildcard:
        return "every day of the week"
    if field.values:
        names = [DAY_NAMES.get(v, str(v)) for v in sorted(field.values)]
        return "on " + ", ".join(names)
    return _humanize_field(field, "weekdays", "weekday")


def _humanize_month(field: CronField) -> str:
    if field.wildcard:
        return "every month"
    if field.values:
        names = [MONTH_NAMES.get(v, str(v)) for v in sorted(field.values)]
        return "in " + ", ".join(names)
    return _humanize_field(field, "months", "month")


def humanize(expression: Union[str, CronExpression]) -> str:
    """Return a human-readable description of a cron expression."""
    if isinstance(expression, str):
        expression = CronExpression.parse(expression)

    minute = _humanize_field(expression.minute, "minutes", "minute")
    hour = _humanize_field(expression.hour, "hours", "hour")
    dom = _humanize_field(expression.day_of_month, "days", "day")
    month = _humanize_month(expression.month)
    dow = _humanize_dow(expression.day_of_week)

    parts = [f"At {minute} past {hour}"]

    if not expression.day_of_month.wildcard or not expression.day_of_week.wildcard:
        parts.append(f"{dom} of {month}")
        parts.append(dow)
    else:
        parts.append(month)

    return ", ".join(parts) + "."
