"""Optimizer for simplifying cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, ParseError
from .normalizer import normalize


@dataclass
class OptimizationHint:
    field_name: str
    original: str
    suggested: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.field_name}] '{self.original}' -> '{self.suggested}': {self.reason}"


@dataclass
class OptimizeResult:
    expression: str
    optimized: str
    hints: List[OptimizationHint] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def valid(self) -> bool:
        return self.error is None

    @property
    def was_changed(self) -> bool:
        return self.valid and self.expression != self.optimized

    def __str__(self) -> str:
        if not self.valid:
            return f"OptimizeResult(error={self.error})"
        changed = "changed" if self.was_changed else "unchanged"
        hints = f", {len(self.hints)} hint(s)" if self.hints else ""
        return f"OptimizeResult('{self.expression}' -> '{self.optimized}', {changed}{hints})"


_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]
_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "dom": (1, 31),
    "month": (1, 12),
    "dow": (0, 7),
}


def _optimize_token(token: str, field_name: str) -> tuple:
    """Return (optimized_token, hint_or_None)."""
    lo, hi = _FIELD_RANGES[field_name]
    span = hi - lo + 1

    # */1 -> *
    if token.startswith("*/"):
        step = token[2:]
        if step == "1":
            return "*", OptimizationHint(field_name, token, "*", "step of 1 is equivalent to wildcard")
        try:
            s = int(step)
            if span % s == 0 and s == span:
                return "*", OptimizationHint(field_name, token, "*", "step equals full range, use wildcard")
        except ValueError:
            pass

    # a-b where a == b -> a
    if "-" in token and "/" not in token and "," not in token:
        parts = token.split("-", 1)
        if len(parts) == 2 and parts[0] == parts[1]:
            return parts[0], OptimizationHint(field_name, token, parts[0], "range start equals end, use single value")

    return token, None


def _optimize_field(raw: str, field_name: str) -> tuple:
    """Optimize a full field string (may contain comma-separated tokens)."""
    tokens = raw.split(",")
    optimized_tokens = []
    hints = []
    for t in tokens:
        opt, hint = _optimize_token(t.strip(), field_name)
        optimized_tokens.append(opt)
        if hint:
            hints.append(hint)
    return ",".join(optimized_tokens), hints


def optimize(expression: str) -> OptimizeResult:
    """Attempt to simplify a cron expression without changing its semantics."""
    try:
        normalized = normalize(expression)
        parsed = CronExpression(normalized)
    except (ParseError, Exception) as exc:
        return OptimizeResult(expression=expression, optimized=expression, error=str(exc))

    raw_fields = [
        parsed.minute,
        parsed.hour,
        parsed.dom,
        parsed.month,
        parsed.dow,
    ]

    all_hints: List[OptimizationHint] = []
    optimized_fields = []
    for raw, name in zip(raw_fields, _FIELD_NAMES):
        opt_field, hints = _optimize_field(raw, name)
        optimized_fields.append(opt_field)
        all_hints.extend(hints)

    optimized_expr = " ".join(optimized_fields)
    return OptimizeResult(
        expression=expression,
        optimized=optimized_expr,
        hints=all_hints,
    )
