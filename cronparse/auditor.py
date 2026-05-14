"""Audit cron expressions for security and operational concerns."""

from dataclasses import dataclass, field
from typing import List, Optional
from cronparse.parser import CronExpression, ParseError
from cronparse.schedule import _expand_field


@dataclass
class AuditIssue:
    severity: str  # 'critical', 'warning', 'info'
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"


@dataclass
class AuditResult:
    expression: str
    valid: bool
    issues: List[AuditIssue] = field(default_factory=list)
    error: Optional[str] = None

    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "critical")

    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def is_clean(self) -> bool:
        return self.valid and self.critical_count() == 0

    def __str__(self) -> str:
        if not self.valid:
            return f"AuditResult({self.expression!r}, error={self.error!r})"
        lines = [f"AuditResult({self.expression!r}, issues={len(self.issues)})"]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)


def _audit_expression(expr: CronExpression) -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    field_names = ["minute", "hour", "dom", "month", "dow"]
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]

    for fname, (lo, hi), token in zip(field_names, ranges, [
        expr.minute, expr.hour, expr.dom, expr.month, expr.dow
    ]):
        try:
            values = _expand_field(token, lo, hi)
        except Exception:
            continue

        # Warn if every value in range is covered (wildcard-equivalent)
        if token != "*" and len(values) == (hi - lo + 1):
            issues.append(AuditIssue(
                severity="warning",
                field=fname,
                message=f"Expression covers all values ({lo}-{hi}); use '*' instead.",
            ))

        # Critical: minute wildcard combined with hour wildcard means every minute
        if fname == "minute" and token == "*" and expr.hour == "*":
            issues.append(AuditIssue(
                severity="critical",
                field="minute",
                message="Runs every minute — this may cause excessive load.",
            ))

        # Warning: step of 1 is redundant
        if "/1" in token:
            issues.append(AuditIssue(
                severity="warning",
                field=fname,
                message="Step of 1 is redundant; use '*' or a plain range.",
            ))

    return issues


def audit(expression: str) -> AuditResult:
    """Audit a single cron expression string."""
    try:
        expr = CronExpression.parse(expression)
    except ParseError as exc:
        return AuditResult(expression=expression, valid=False, error=str(exc))

    issues = _audit_expression(expr)
    return AuditResult(expression=expression, valid=True, issues=issues)
