"""cronparse — Library for parsing and humanizing cron expressions with conflict detection."""

from cronparse.parser import CronExpression, CronField, ParseError, as_dict
from cronparse.humanizer import humanize
from cronparse.validator import validate_field, validate
from cronparse.conflicts import detect_conflicts
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.schedule import next_run, next_n_runs
from cronparse.diff import diff, CronDiff
from cronparse.explainer import explain, explain_text
from cronparse.normalizer import normalize, normalize_string
from cronparse.similarity import compare, SimilarityReport
from cronparse.merger import merge, merge_strings, MergeResult
from cronparse.tags import tag, tag_string, TagResult
from cronparse.summarizer import summarize, ExpressionSummary, MultiSummary
from cronparse.reporter import report, ExpressionReport
from cronparse.ranker import rank, RankResult, RankedExpression
from cronparse.deduplicator import deduplicate, DeduplicationResult

__all__ = [
    # parser
    "CronExpression",
    "CronField",
    "ParseError",
    "as_dict",
    # humanizer
    "humanize",
    # validator
    "validate_field",
    "validate",
    # conflicts
    "detect_conflicts",
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
    "tag_string",
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
]
