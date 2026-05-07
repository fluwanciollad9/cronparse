"""cronparse — Library for parsing and humanizing cron expressions."""

from cronparse.parser import (
    CronExpression,
    CronField,
    ParseError,
    parse,
    as_dict,
)
from cronparse.humanizer import humanize
from cronparse.validator import validate, ValidationResult
from cronparse.conflicts import detect_conflicts, ConflictReport
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.schedule import next_run, next_n_runs
from cronparse.diff import diff, CronDiff
from cronparse.explainer import explain, explain_text
from cronparse.normalizer import normalize, normalize_string
from cronparse.similarity import compare, SimilarityReport
from cronparse.merger import merge, merge_strings, MergeResult
from cronparse.tags import tag, TagResult
from cronparse.summarizer import summarize, ExpressionSummary, MultiSummary
from cronparse.reporter import report, ExpressionReport
from cronparse.ranker import rank, RankResult, RankedExpression
from cronparse.deduplicator import deduplicate, DeduplicationResult
from cronparse.grouper import group, GroupResult
from cronparse.linter import lint, LintResult, LintIssue

__all__ = [
    # parser
    "CronExpression",
    "CronField",
    "ParseError",
    "parse",
    "as_dict",
    # humanizer
    "humanize",
    # validator
    "validate",
    "ValidationResult",
    # conflicts
    "detect_conflicts",
    "ConflictReport",
    # formatter
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    # schedule
    "next_run",
    "next_n_runs",
    # diff
    "diff",
    "CronDiff",
    # explainer
    "explain",
    "explain_text",
    # normalizer
    "normalize",
    "normalize_string",
    # similarity
    "compare",
    "SimilarityReport",
    # merger
    "merge",
    "merge_strings",
    "MergeResult",
    # tags
    "tag",
    "TagResult",
    # summarizer
    "summarize",
    "ExpressionSummary",
    "MultiSummary",
    # reporter
    "report",
    "ExpressionReport",
    # ranker
    "rank",
    "RankResult",
    "RankedExpression",
    # deduplicator
    "deduplicate",
    "DeduplicationResult",
    # grouper
    "group",
    "GroupResult",
    # linter
    "lint",
    "LintResult",
    "LintIssue",
]
