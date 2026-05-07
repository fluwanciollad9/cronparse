"""Generate a structured report for one or more cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize
from cronparse.conflicts import has_conflicts
from cronparse.validator import validate
from cronparse.tags import tag
from cronparse.explainer import explain


@dataclass
class ExpressionReport:
    raw: str
    valid: bool
    human: Optional[str]
    tags: List[str]
    conflicts: bool
    validation_errors: List[str]
    explanation: Optional[Dict[str, str]]
    parse_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw": self.raw,
            "valid": self.valid,
            "human": self.human,
            "tags": self.tags,
            "conflicts": self.conflicts,
            "validation_errors": self.validation_errors,
            "explanation": self.explanation,
            "parse_error": self.parse_error,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def __str__(self) -> str:
        lines = [f"Report for: {self.raw!r}"]
        lines.append(f"  Valid       : {self.valid}")
        if self.parse_error:
            lines.append(f"  Parse error : {self.parse_error}")
            return "\n".join(lines)
        lines.append(f"  Human       : {self.human}")
        lines.append(f"  Tags        : {', '.join(self.tags) or 'none'}")
        lines.append(f"  Conflicts   : {self.conflicts}")
        if self.validation_errors:
            lines.append(f"  Errors      : {'; '.join(self.validation_errors)}")
        return "\n".join(lines)


def report(raw: str) -> ExpressionReport:
    """Build a full diagnostic report for a single cron expression string."""
    try:
        expr = CronExpression.parse(raw)
    except (ParseError, Exception) as exc:
        return ExpressionReport(
            raw=raw,
            valid=False,
            human=None,
            tags=[],
            conflicts=False,
            validation_errors=[],
            explanation=None,
            parse_error=str(exc),
        )

    vresult = validate(expr)
    errors = [str(vresult)] if not vresult else []
    tag_result = tag(expr)
    conflict_report = has_conflicts(expr)
    human = humanize(expr)
    explanation = explain(expr)

    return ExpressionReport(
        raw=raw,
        valid=bool(vresult),
        human=human,
        tags=tag_result.tags,
        conflicts=conflict_report.has_conflicts(),
        validation_errors=errors,
        explanation=explanation,
    )
