"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from .parser import CronExpression, CronField, ParseError, parse, as_dict
from .humanizer import humanize
from .conflicts import ConflictReport, detect_conflicts
from .validator import ValidationResult, validate
from .formatter import to_dict, to_json, to_table, to_cron_string
from .schedule import next_run, next_n_runs
from .diff import CronDiff, diff
from .explainer import explain, explain_text
from .normalizer import normalize, normalize_string
from .similarity import SimilarityReport, compare
from .merger import MergeResult, merge, merge_strings
from .tags import TagResult, tag, tag_string
from .summarizer import ExpressionSummary, MultiSummary, summarize
from .reporter import ExpressionReport, report
from .ranker import RankResult, RankedExpression, rank

__all__ = [
    # parser
    "CronExpression",
    "CronField",
    "ParseError",
    "parse",
    "as_dict",
    # humanizer
    "humanize",
    # conflicts
    "ConflictReport",
    "detect_conflicts",
    # validator
    "ValidationResult",
    "validate",
    # formatter
    "to_dict",
    "to_json",
    "to_table",
    "to_cron_string",
    # schedule
    "next_run",
    "next_n_runs",
    # diff
    "CronDiff",
    "diff",
    # explainer
    "explain",
    "explain_text",
    # normalizer
    "normalize",
    "normalize_string",
    # similarity
    "SimilarityReport",
    "compare",
    # merger
    "MergeResult",
    "merge",
    "merge_strings",
    # tags
    "TagResult",
    "tag",
    "tag_string",
    # summarizer
    "ExpressionSummary",
    "MultiSummary",
    "summarize",
    # reporter
    "ExpressionReport",
    "report",
    # ranker
    "RankResult",
    "RankedExpression",
    "rank",
]
