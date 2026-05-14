"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from .parser import CronExpression, CronField, ParseError, parse, as_dict
from .humanizer import humanize
from .conflicts import ConflictReport, has_conflicts
from .validator import ValidationResult, validate
from .formatter import to_dict, to_json, to_table, to_cron_string
from .schedule import next_run, next_n_runs
from .diff import CronDiff, diff
from .explainer import explain, explain_text
from .normalizer import normalize, normalize_string
from .similarity import SimilarityReport, compare
from .merger import MergeResult, merge
from .tags import TagResult, tag
from .summarizer import MultiSummary, summarize
from .reporter import ExpressionReport, report
from .ranker import RankResult, rank
from .deduplicator import DeduplicationResult, deduplicate
from .grouper import GroupResult, group
from .linter import LintResult, lint
from .annotator import AnnotationResult, annotate
from .splitter import SplitResult, split
from .forecaster import ForecastResult, forecast
from .timeline import Timeline, build_timeline
from .optimizer import OptimizeResult, optimize
from .matcher import MatchResult, BatchMatchResult, match, match_many
from .classifier import ClassificationResult, BatchClassification, classify, classify_many
from .profiler import ProfileResult, profile
from .auditor import AuditResult, audit
from .batch_auditor import BatchAuditResult, audit_many
from .segmenter import SegmentResult, segment
from .comparator import ComparisonResult, compare_many
from .inspector import InspectionResult, FieldInspection, inspect

__all__ = [
    # parser
    "CronExpression", "CronField", "ParseError", "parse", "as_dict",
    # humanizer
    "humanize",
    # conflicts
    "ConflictReport", "has_conflicts",
    # validator
    "ValidationResult", "validate",
    # formatter
    "to_dict", "to_json", "to_table", "to_cron_string",
    # schedule
    "next_run", "next_n_runs",
    # diff
    "CronDiff", "diff",
    # explainer
    "explain", "explain_text",
    # normalizer
    "normalize", "normalize_string",
    # similarity
    "SimilarityReport", "compare",
    # merger
    "MergeResult", "merge",
    # tags
    "TagResult", "tag",
    # summarizer
    "MultiSummary", "summarize",
    # reporter
    "ExpressionReport", "report",
    # ranker
    "RankResult", "rank",
    # deduplicator
    "DeduplicationResult", "deduplicate",
    # grouper
    "GroupResult", "group",
    # linter
    "LintResult", "lint",
    # annotator
    "AnnotationResult", "annotate",
    # splitter
    "SplitResult", "split",
    # forecaster
    "ForecastResult", "forecast",
    # timeline
    "Timeline", "build_timeline",
    # optimizer
    "OptimizeResult", "optimize",
    # matcher
    "MatchResult", "BatchMatchResult", "match", "match_many",
    # classifier
    "ClassificationResult", "BatchClassification", "classify", "classify_many",
    # profiler
    "ProfileResult", "profile",
    # auditor
    "AuditResult", "audit",
    # batch_auditor
    "BatchAuditResult", "audit_many",
    # segmenter
    "SegmentResult", "segment",
    # comparator
    "ComparisonResult", "compare_many",
    # inspector
    "InspectionResult", "FieldInspection", "inspect",
]
