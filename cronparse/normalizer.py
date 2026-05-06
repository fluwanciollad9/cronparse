"""Normalize cron expressions to a canonical form."""

from cronparse.parser import CronExpression, ParseError

# Aliases for months
MONTH_ALIASES = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}

# Aliases for days of week
DOW_ALIASES = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}


def _normalize_token(token: str, aliases: dict) -> str:
    """Replace named aliases with numeric equivalents in a token."""
    lower = token.lower()
    if lower in aliases:
        return aliases[lower]
    # Handle ranges like JAN-MAR or SUN-FRI
    if "-" in token:
        parts = token.split("-", 1)
        return "-".join(_normalize_token(p, aliases) for p in parts)
    # Handle lists like JAN,MAR
    if "," in token:
        parts = token.split(",")
        return ",".join(_normalize_token(p, aliases) for p in parts)
    return token


def _normalize_field(expression: str, aliases: dict) -> str:
    """Normalize a single cron field expression."""
    if expression == "*":
        return "*"
    # Handle step expressions like */2 or JAN-JUN/2
    if "/" in expression:
        base, step = expression.split("/", 1)
        return f"{_normalize_token(base, aliases)}/{step}"
    return _normalize_token(expression, aliases)


def normalize(expr: CronExpression) -> CronExpression:
    """Return a new CronExpression with all aliases replaced by numbers.

    Args:
        expr: A parsed CronExpression instance.

    Returns:
        A new CronExpression with normalized (numeric) field values.

    Raises:
        ParseError: If the normalized string cannot be re-parsed.
    """
    normalized_minute = expr.minute
    normalized_hour = expr.hour
    normalized_dom = expr.dom
    normalized_month = _normalize_field(expr.month, MONTH_ALIASES)
    normalized_dow = _normalize_field(expr.dow, DOW_ALIASES)

    normalized_str = " ".join([
        normalized_minute,
        normalized_hour,
        normalized_dom,
        normalized_month,
        normalized_dow,
    ])
    return CronExpression(normalized_str)


def normalize_string(cron_string: str) -> str:
    """Parse and normalize a cron string, returning the canonical form.

    Args:
        cron_string: A raw cron expression string.

    Returns:
        A normalized cron expression string with numeric values.

    Raises:
        ParseError: If the input cannot be parsed.
    """
    expr = CronExpression(cron_string)
    normalized = normalize(expr)
    return str(normalized)
