"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize
from cronparse.conflicts import detect_conflicts
from cronparse.validator import validate
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.schedule import next_run, next_n_runs
from cronparse.diff import diff
from cronparse.explainer import explain, explain_text

__all__ = [
    "CronExpression",
    "ParseError",
    "humanize",
    "detect_conflicts",
    "validate",
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    "next_run",
    "next_n_runs",
    "diff",
    "explain",
    "explain_text",
]

__version__ = "0.1.0"
