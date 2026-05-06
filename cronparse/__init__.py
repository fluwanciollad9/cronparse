"""cronparse — Library for parsing and humanizing cron expressions."""

from .parser import CronExpression, ParseError
from .humanizer import humanize
from .conflicts import has_conflicts, ConflictReport
from .validator import validate
from .formatter import to_dict, to_json, to_table, to_cron_string
from .schedule import next_run, next_n_runs
from .diff import diff, CronDiff
from .explainer import explain, explain_text
from .normalizer import normalize, normalize_string
from .similarity import compare as compare_similarity, similarity_score, SimilarityReport

__all__ = [
    # parser
    "CronExpression",
    "ParseError",
    # humanizer
    "humanize",
    # conflicts
    "has_conflicts",
    "ConflictReport",
    # validator
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
    "diff",
    "CronDiff",
    # explainer
    "explain",
    "explain_text",
    # normalizer
    "normalize",
    "normalize_string",
    # similarity
    "compare_similarity",
    "similarity_score",
    "SimilarityReport",
]
