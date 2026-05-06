"""Tag and label cron expressions with semantic categories."""

from dataclasses import dataclass, field
from cronparse.parser import CronExpression

KNOWN_TAGS = {
    "every_minute",
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "yearly",
    "business_hours",
    "midnight",
    "noon",
    "custom",
}


@dataclass
class TagResult:
    """Tags assigned to a cron expression."""
    tags: list = field(default_factory=list)
    labels: dict = field(default_factory=dict)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return f"Tags: {tag_str}"


def tag(expr: CronExpression) -> TagResult:
    """Assign semantic tags to a cron expression."""
    tags = []
    labels = {}

    m, h, d, mo, dow = expr.minute, expr.hour, expr.day, expr.month, expr.dow

    if m == "*" and h == "*" and d == "*" and mo == "*" and dow == "*":
        tags.append("every_minute")
        labels["frequency"] = "every minute"
        return TagResult(tags=tags, labels=labels)

    if m != "*" and h == "*" and d == "*" and mo == "*" and dow == "*":
        tags.append("hourly")
        labels["frequency"] = "hourly"

    if m != "*" and h != "*" and d == "*" and mo == "*" and dow == "*":
        tags.append("daily")
        labels["frequency"] = "daily"
        if h == "0" and m == "0":
            tags.append("midnight")
            labels["time"] = "midnight"
        elif h == "12" and m == "0":
            tags.append("noon")
            labels["time"] = "noon"

    if m != "*" and h != "*" and d == "*" and mo == "*" and dow != "*":
        tags.append("weekly")
        labels["frequency"] = "weekly"

    if m != "*" and h != "*" and d != "*" and mo == "*" and dow == "*":
        tags.append("monthly")
        labels["frequency"] = "monthly"

    if m != "*" and h != "*" and d != "*" and mo != "*" and dow == "*":
        tags.append("yearly")
        labels["frequency"] = "yearly"

    if h != "*" and not h.startswith("*"):
        try:
            hours = [int(x) for x in h.split(",")]
            if all(9 <= hr <= 17 for hr in hours):
                tags.append("business_hours")
                labels["context"] = "business hours"
        except ValueError:
            pass

    if not tags:
        tags.append("custom")
        labels["frequency"] = "custom schedule"

    return TagResult(tags=tags, labels=labels)


def tag_string(cron: str) -> TagResult:
    """Parse a cron string and return its tags."""
    expr = CronExpression.parse(cron)
    return tag(expr)
