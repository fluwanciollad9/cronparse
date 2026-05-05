"""Validation utilities for cron expressions and individual fields."""

from dataclasses import dataclass, field
from typing import List, Optional

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {"jan", "feb", "mar", "apr", "may", "jun",
                 "jul", "aug", "sep", "oct", "nov", "dec"}
DOW_ALIASES = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def __str__(self) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"ERROR: {e}")
        for w in self.warnings:
            lines.append(f"WARNING: {w}")
        return "\n".join(lines) if lines else "OK"


def _check_value_in_range(value: int, field_name: str) -> Optional[str]:
    lo, hi = FIELD_RANGES[field_name]
    if not (lo <= value <= hi):
        return f"{field_name}: value {value} out of range [{lo}, {hi}]"
    return None


def _validate_single_token(token: str, field_name: str) -> List[str]:
    errors = []
    lo, hi = FIELD_RANGES[field_name]

    if token == "*":
        return []

    if "/" in token:
        parts = token.split("/", 1)
        if not parts[1].isdigit():
            errors.append(f"{field_name}: step '{parts[1]}' is not a valid integer")
        elif int(parts[1]) == 0:
            errors.append(f"{field_name}: step value cannot be zero")
        token = parts[0]
        if token == "*":
            return errors

    if "-" in token:
        parts = token.split("-", 1)
        for p in parts:
            if p.isdigit():
                err = _check_value_in_range(int(p), field_name)
                if err:
                    errors.append(err)
            elif p.lower() not in (MONTH_ALIASES | DOW_ALIASES):
                errors.append(f"{field_name}: unknown alias '{p}'")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if int(parts[0]) > int(parts[1]):
                errors.append(f"{field_name}: range start {parts[0]} > end {parts[1]}")
        return errors

    if token.isdigit():
        err = _check_value_in_range(int(token), field_name)
        if err:
            errors.append(err)
    elif token.lower() not in (MONTH_ALIASES | DOW_ALIASES):
        errors.append(f"{field_name}: unknown token '{token}'")

    return errors


def validate_field(expression: str, field_name: str) -> List[str]:
    """Return a list of error strings for a single cron field expression."""
    errors = []
    for token in expression.split(","):
        errors.extend(_validate_single_token(token.strip(), field_name))
    return errors


def validate(cron_string: str) -> ValidationResult:
    """Validate a full 5-part cron expression string."""
    parts = cron_string.strip().split()
    if len(parts) != 5:
        return ValidationResult(
            valid=False,
            errors=[f"Expected 5 fields, got {len(parts)}"]
        )

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    all_errors: List[str] = []
    warnings: List[str] = []

    for token, fname in zip(parts, field_names):
        all_errors.extend(validate_field(token, fname))

    # Warn when both dom and dow are restricted (non-wildcard)
    if parts[2] != "*" and parts[4] != "*":
        warnings.append(
            "Both day-of-month and day-of-week are specified; "
            "most cron implementations treat this as OR logic"
        )

    return ValidationResult(
        valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=warnings,
    )
