"""cronparse — Library for parsing and humanizing cron expressions."""

from .parser import CronExpression, CronField, ParseError, parse, as_dict
from .humanizer import humanize
from .validator import validate, ValidationResult
from .formatter import to_dict, to_json, to_table, to_cron_string
from .conflicts import detect_conflicts, ConflictReport
from .schedule import next_run, next_n_runs
from .diff import diff, CronDiff
from .explainer import explain, explain_text
from .normalizer import normalize, normalize_string
from .similarity import compare, SimilarityReport
from .merger import merge, MergeResult
from .tags import tag, TagResult
from .summarizer import summarize, MultiSummary
from .reporter import report, ExpressionReport
from .ranker import rank, RankResult
from .deduplicator import deduplicate, DeduplicationResult
from .grouper import group, GroupResult
from .linter import lint, LintResult
from .annotator import annotate, AnnotationResult
from .splitter import split, SplitResult
from .forecaster import forecast, ForecastResult
from .timeline import build_timeline, Timeline
from .optimizer import optimize, OptimizeResult
from .matcher import match, batch_match, MatchResult, BatchMatchResult
from .classifier import classify, batch_classify, ClassificationResult
from .profiler import profile, ProfileResult
from .auditor import audit, AuditResult
from .batch_auditor import audit_many, BatchAuditResult
from .segmenter import segment, SegmentResult
from .comparator import compare_many, ComparisonResult
from .inspector import inspect, InspectionResult
from .scorer import score, ScoreResult

__all__ = [
    "CronExpression",
    "CronField",
    "ParseError",
    "parse",
    "as_dict",
    "humanize",
    "validate",
    "ValidationResult",
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    "detect_conflicts",
    "ConflictReport",
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
    "batch_match",
    "MatchResult",
    "BatchMatchResult",
    "classify",
    "batch_classify",
    "ClassificationResult",
    "profile",
    "ProfileResult",
    "audit",
    "AuditResult",
    "audit_many",
    "BatchAuditResult",
    "segment",
    "SegmentResult",
    "compare_many",
    "ComparisonResult",
    "inspect",
    "InspectionResult",
    "score",
    "ScoreResult",
]
