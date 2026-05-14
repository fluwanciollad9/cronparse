"""cronparse — Library for parsing and humanizing cron expressions."""

from .parser import CronExpression, CronField, ParseError
from .humanizer import humanize
from .validator import validate
from .conflicts import has_conflicts
from .formatter import to_dict, to_json, to_table, to_cron_string
from .schedule import next_run, next_n_runs
from .diff import diff
from .explainer import explain, explain_text
from .normalizer import normalize, normalize_string
from .similarity import compare
from .merger import merge
from .tags import tag
from .summarizer import summarize
from .reporter import report
from .ranker import rank
from .deduplicator import deduplicate
from .grouper import group
from .linter import lint
from .annotator import annotate
from .splitter import split
from .forecaster import forecast
from .timeline import build_timeline
from .optimizer import optimize
from .matcher import match, match_many
from .classifier import classify, classify_many
from .profiler import profile
from .auditor import audit
from .batch_auditor import audit_many
from .segmenter import segment
from .comparator import compare_many

__all__ = [
    # Core
    "CronExpression",
    "CronField",
    "ParseError",
    # Features
    "humanize",
    "validate",
    "has_conflicts",
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    "next_run",
    "next_n_runs",
    "diff",
    "explain",
    "explain_text",
    "normalize",
    "normalize_string",
    "compare",
    "merge",
    "tag",
    "summarize",
    "report",
    "rank",
    "deduplicate",
    "group",
    "lint",
    "annotate",
    "split",
    "forecast",
    "build_timeline",
    "optimize",
    "match",
    "match_many",
    "classify",
    "classify_many",
    "profile",
    "audit",
    "audit_many",
    "segment",
    "compare_many",
]
