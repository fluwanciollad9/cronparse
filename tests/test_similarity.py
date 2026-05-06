"""Tests for cronparse.similarity module."""

import pytest

from cronparse.parser import CronExpression
from cronparse.similarity import (
    SimilarityReport,
    _field_score,
    _token_score,
    compare,
    similarity_score,
)


def _parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


# --- unit helpers ---

def test_token_score_identical():
    assert _token_score("5", "5") == 1.0


def test_token_score_wildcard_a():
    assert _token_score("*", "5") == 0.5


def test_token_score_wildcard_b():
    assert _token_score("10", "*") == 0.5


def test_token_score_different():
    assert _token_score("3", "7") == 0.0


def test_field_score_identical_sets():
    assert _field_score(["1", "2"], ["2", "1"]) == 1.0


def test_field_score_wildcard():
    assert _field_score(["*"], ["5"]) == 0.5


def test_field_score_no_overlap():
    assert _field_score(["1"], ["9"]) == 0.0


def test_field_score_partial_overlap():
    score = _field_score(["1", "2", "3"], ["2", "3", "4"])
    assert 0.0 < score < 1.0


# --- compare / SimilarityReport ---

def test_identical_expressions_score_one():
    a = _parse("*/5 * * * *")
    b = _parse("*/5 * * * *")
    report = compare(a, b)
    assert report.overall == pytest.approx(1.0)


def test_completely_different_fixed_expressions():
    a = _parse("0 0 1 1 0")
    b = _parse("59 23 31 12 6")
    report = compare(a, b)
    assert report.overall == pytest.approx(0.0)


def test_wildcard_vs_specific_is_partial():
    a = _parse("* * * * *")
    b = _parse("0 0 * * *")
    report = compare(a, b)
    assert 0.0 < report.overall < 1.0


def test_report_has_all_fields():
    a = _parse("0 12 * * 1")
    b = _parse("0 12 * * 1")
    report = compare(a, b)
    for name in ("minute", "hour", "day", "month", "dow"):
        assert name in report.field_scores


def test_similarity_score_convenience():
    a = _parse("0 9 * * 1-5")
    b = _parse("0 9 * * 1-5")
    assert similarity_score(a, b) == pytest.approx(1.0)


def test_str_report_contains_overall():
    a = _parse("0 * * * *")
    b = _parse("0 * * * *")
    report = compare(a, b)
    text = str(report)
    assert "Overall" in text
    assert "100%" in text


def test_partial_match_step_vs_wildcard():
    a = _parse("*/15 * * * *")
    b = _parse("* * * * *")
    score = similarity_score(a, b)
    # minute differs (step vs wildcard), others are equal wildcards
    assert 0.0 < score < 1.0
