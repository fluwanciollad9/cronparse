"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from cronparse.parser import CronExpression, CronField, ParseError, parse, as_dict
from cronparse.humanizer import humanize
from cronparse.conflicts import ConflictReport, detect_conflicts
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.validator import validate, ValidationResult
from cronparse.schedule import next_run, next_n_runs
from cronparse.diff import diff, CronDiff
from cronparse.explainer import explain, explain_text
from cronparse.normalizer import normalize, normalize_string
from cronparse.similarity import compare, SimilarityReport
from cronparse.merger import merge, merge_strings, MergeResult
from cronparse.tags import tag, TagResult
from cronparse.summarizer import summarize, MultiSummary
from cronparse.reporter import report, ExpressionReport
from cronparse.ranker import rank, RankResult
from cronparse.deduplicator import deduplicate, DeduplicationResult
from cronparse.grouper import group, GroupResult
from cronparse.linter import lint, LintResult
from cronparse.annotator import annotate, AnnotationResult
from cronparse.splitter import split, SplitResult
from cronparse.forecaster import forecast, ForecastResult
from cronparse.timeline import build_timeline, Timeline
from cronparse.optimizer import optimize, OptimizeResult
from cronparse.matcher import match, BatchMatchResult
from cronparse.classifier import classify, classify_many, ClassificationResult, BatchClassification

__all__ = [
    "CronExpression",
    "CronField",
    "ParseError",
    "parse",
    "as_dict",
    "humanize",
    "ConflictReport",
    "detect_conflicts",
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    "validate",
    "ValidationResult",
    "next_run",
    "next_n_runs",
    "diff",
    "CronDiff",
    "explain",
    "explain_text",
    "normalize",
    "normalize_string",
    "compare",
    "SimilarityReport",
    "merge",
    "merge_strings",
    "MergeResult",
    "tag",
    "TagResult",
    "summarize",
    "MultiSummary",
    "report",
    "ExpressionReport",
    "rank",
    "RankResult",
    "deduplicate",
    "DeduplicationResult",
    "group",
    "GroupResult",
    "lint",
    "LintResult",
    "annotate",
    "AnnotationResult",
    "split",
    "SplitResult",
    "forecast",
    "ForecastResult",
    "build_timeline",
    "Timeline",
    "optimize",
    "OptimizeResult",
    "match",
    "BatchMatchResult",
    "classify",
    "classify_many",
    "ClassificationResult",
    "BatchClassification",
]
