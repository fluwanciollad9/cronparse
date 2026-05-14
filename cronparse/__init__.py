"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from cronparse.parser import CronExpression, CronField, ParseError
from cronparse.humanizer import humanize
from cronparse.conflicts import has_conflicts, ConflictReport
from cronparse.validator import ValidationResult
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.schedule import next_run, next_n_runs
from cronparse.diff import CronDiff
from cronparse.explainer import explain, explain_text
from cronparse.normalizer import normalize, normalize_string
from cronparse.similarity import compare, SimilarityReport
from cronparse.merger import merge, merge_strings, MergeResult
from cronparse.tags import tag, TagResult
from cronparse.summarizer import ExpressionSummary, MultiSummary
from cronparse.reporter import report, ExpressionReport
from cronparse.ranker import RankResult, RankedExpression
from cronparse.deduplicator import deduplicate, DeduplicationResult
from cronparse.grouper import GroupResult
from cronparse.linter import LintResult, LintIssue
from cronparse.annotator import AnnotationResult, FieldAnnotation
from cronparse.splitter import SplitResult
from cronparse.forecaster import ForecastResult, ExpressionForecast
from cronparse.timeline import Timeline, TimelineEntry
from cronparse.optimizer import OptimizeResult, OptimizationHint
from cronparse.matcher import MatchResult, BatchMatchResult
from cronparse.classifier import ClassificationResult, BatchClassification
from cronparse.profiler import profile, ProfileResult, ExpressionProfile

__all__ = [
    "CronExpression",
    "CronField",
    "ParseError",
    "humanize",
    "has_conflicts",
    "ConflictReport",
    "ValidationResult",
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    "next_run",
    "next_n_runs",
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
    "ExpressionSummary",
    "MultiSummary",
    "report",
    "ExpressionReport",
    "RankResult",
    "RankedExpression",
    "deduplicate",
    "DeduplicationResult",
    "GroupResult",
    "LintResult",
    "LintIssue",
    "AnnotationResult",
    "FieldAnnotation",
    "SplitResult",
    "ForecastResult",
    "ExpressionForecast",
    "Timeline",
    "TimelineEntry",
    "OptimizeResult",
    "OptimizationHint",
    "MatchResult",
    "BatchMatchResult",
    "ClassificationResult",
    "BatchClassification",
    "profile",
    "ProfileResult",
    "ExpressionProfile",
]
