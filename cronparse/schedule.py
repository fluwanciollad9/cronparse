"""Next-run schedule calculator for cron expressions."""

from datetime import datetime, timedelta
from typing import List, Optional

from cronparse.parser import CronExpression, parse


def _expand_field(expr: str, lo: int, hi: int) -> List[int]:
    """Expand a single cron field expression to a sorted list of integers."""
    values: set = set()

    for token in expr.split(","):
        token = token.strip()
        step = 1
        if "/" in token:
            token, step_str = token.split("/", 1)
            step = int(step_str)

        if token == "*":
            start, end = lo, hi
        elif "-" in token:
            start_s, end_s = token.split("-", 1)
            start, end = int(start_s), int(end_s)
        else:
            start = end = int(token)

        values.update(range(start, end + 1, step))

    return sorted(values)


def _next_value(current: int, candidates: List[int]) -> Optional[int]:
    """Return the smallest candidate >= current, or None if none exists."""
    for v in candidates:
        if v >= current:
            return v
    return None


def next_run(cron_expr: str, after: Optional[datetime] = None) -> datetime:
    """Return the next datetime at which *cron_expr* would fire.

    Args:
        cron_expr: A standard 5-field cron string.
        after: Start searching from this moment (default: now, truncated to
               the current minute).

    Returns:
        The next matching :class:`datetime` (second=0, microsecond=0).

    Raises:
        ValueError: If no matching time is found within 4 years.
    """
    parsed: CronExpression = parse(cron_expr)

    minutes = _expand_field(parsed.minute, 0, 59)
    hours = _expand_field(parsed.hour, 0, 23)
    doms = _expand_field(parsed.day_of_month, 1, 31)
    months = _expand_field(parsed.month, 1, 12)
    dows = _expand_field(parsed.day_of_week, 0, 7)  # 0 and 7 both = Sunday
    # Normalise Sunday: treat 7 as 0
    dows = sorted({0 if d == 7 else d for d in dows})

    if after is None:
        after = datetime.now().replace(second=0, microsecond=0)
    else:
        after = after.replace(second=0, microsecond=0)

    # Advance by one minute so we don't return the current moment
    candidate = after + timedelta(minutes=1)

    deadline = candidate + timedelta(days=4 * 365)

    while candidate <= deadline:
        if candidate.month not in months:
            # Jump to first valid month
            next_month = _next_value(candidate.month, months)
            if next_month is None:
                candidate = candidate.replace(month=1, day=1, hour=0, minute=0)
                candidate = candidate.replace(year=candidate.year + 1)
            else:
                candidate = candidate.replace(month=next_month, day=1, hour=0, minute=0)
            continue

        dom_ok = parsed.day_of_month == "*" or candidate.day in doms
        dow_ok = parsed.day_of_week == "*" or candidate.weekday() in [d if d != 0 else 6 for d in dows]
        # Python weekday: Mon=0 … Sun=6; cron dow: Sun=0 … Sat=6
        cron_dow = (candidate.weekday() + 1) % 7
        dow_ok = parsed.day_of_week == "*" or cron_dow in dows

        if not (dom_ok or dow_ok) if (parsed.day_of_month != "*" and parsed.day_of_week != "*") else not (dom_ok and dow_ok if parsed.day_of_month == "*" or parsed.day_of_week == "*" else dom_ok or dow_ok):
            candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            continue

        if candidate.hour not in hours:
            next_hour = _next_value(candidate.hour, hours)
            if next_hour is None:
                candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
            else:
                candidate = candidate.replace(hour=next_hour, minute=0)
            continue

        if candidate.minute not in minutes:
            next_minute = _next_value(candidate.minute, minutes)
            if next_minute is None:
                candidate = candidate.replace(minute=0) + timedelta(hours=1)
            else:
                candidate = candidate.replace(minute=next_minute)
            continue

        return candidate

    raise ValueError(f"No next run found for '{cron_expr}' within 4 years")


def next_n_runs(cron_expr: str, n: int = 5, after: Optional[datetime] = None) -> List[datetime]:
    """Return the next *n* datetimes at which *cron_expr* would fire."""
    results: List[datetime] = []
    cursor = after
    for _ in range(n):
        nxt = next_run(cron_expr, after=cursor)
        results.append(nxt)
        cursor = nxt
    return results
