"""Linter for cron expressions — detects style and best-practice issues."""

from dataclasses import dataclass, field
from typing import List

from cronparse.parser import CronExpression, ParseError, parse
from cronparse.normalizer import normalize


@dataclass
class LintIssue:
    field: str
    code: str
    message: str
    severity: str  # 'warning' | 'info'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message} ({self.code})"


@dataclass
class LintResult:
    expression: str
    issues: List[LintIssue] = field(default_factory=list)
    error: str = ""

    @property
    def valid(self) -> bool:
        return not self.error

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def __str__(self) -> str:
        if self.error:
            return f"LintResult(error={self.error!r})"
        if not self.issues:
            return f"LintResult({self.expression!r}): no issues"
        lines = [f"LintResult({self.expression!r}):"] + [f"  {i}" for i in self.issues]
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def _lint_field(fname: str, token: str, issues: List[LintIssue]) -> None:
    # Redundant step-1 (*/1 == *)
    if token == "*/1":
        issues.append(LintIssue(
            field=fname,
            code="L001",
            message="'*/1' is equivalent to '*'; prefer '*'",
            severity="warning",
        ))

    # Unnecessary leading zeros in numeric tokens
    for part in token.split(","):
        for sub in part.replace("/", "-").split("-"):
            if sub.isdigit() and len(sub) > 1 and sub.startswith("0"):
                issues.append(LintIssue(
                    field=fname,
                    code="L002",
                    message=f"Numeric token '{sub}' has unnecessary leading zero",
                    severity="info",
                ))

    # Redundant range where start == end (e.g. 5-5)
    if "-" in token and "/" not in token and "," not in token:
        parts = token.split("-")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if parts[0] == parts[1]:
                issues.append(LintIssue(
                    field=fname,
                    code="L003",
                    message=f"Range '{token}' start equals end; use a single value",
                    severity="warning",
                ))


def lint(expression: str) -> LintResult:
    """Lint a cron expression string and return a LintResult."""
    try:
        expr: CronExpression = parse(expression)
    except ParseError as exc:
        return LintResult(expression=expression, error=str(exc))

    tokens = [
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    ]

    issues: List[LintIssue] = []
    for fname, token in zip(_FIELD_NAMES, tokens):
        _lint_field(fname, token, issues)

    return LintResult(expression=expression, issues=issues)
