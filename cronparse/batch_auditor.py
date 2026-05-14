"""Batch auditing of multiple cron expressions."""

from dataclasses import dataclass, field
from typing import List, Dict
from cronparse.auditor import AuditResult, audit


@dataclass
class BatchAuditResult:
    results: List[AuditResult] = field(default_factory=list)

    def valid_count(self) -> int:
        return sum(1 for r in self.results if r.valid)

    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.valid)

    def clean_count(self) -> int:
        return sum(1 for r in self.results if r.is_clean())

    def critical_count(self) -> int:
        return sum(r.critical_count() for r in self.results)

    def warning_count(self) -> int:
        return sum(r.warning_count() for r in self.results)

    def by_severity(self) -> Dict[str, List[AuditResult]]:
        """Group results by worst severity: 'critical', 'warning', 'clean', 'error'."""
        groups: Dict[str, List[AuditResult]] = {
            "critical": [],
            "warning": [],
            "clean": [],
            "error": [],
        }
        for r in self.results:
            if not r.valid:
                groups["error"].append(r)
            elif r.critical_count() > 0:
                groups["critical"].append(r)
            elif r.warning_count() > 0:
                groups["warning"].append(r)
            else:
                groups["clean"].append(r)
        return groups

    def __str__(self) -> str:
        return (
            f"BatchAuditResult(total={len(self.results)}, "
            f"clean={self.clean_count()}, "
            f"warnings={self.warning_count()}, "
            f"critical={self.critical_count()}, "
            f"errors={self.error_count()})"
        )


def audit_many(expressions: List[str]) -> BatchAuditResult:
    """Audit multiple cron expression strings at once."""
    return BatchAuditResult(results=[audit(expr) for expr in expressions])
