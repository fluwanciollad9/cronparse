"""Tests for cronparse.comparator module."""

import pytest

from cronparse.comparator import compare_many, ComparisonResult, ComparisonEntry


REF = "0 9 * * 1-5"  # 09:00 Mon-Fri


# ---------------------------------------------------------------------------
# Basic return-type checks
# ---------------------------------------------------------------------------

def test_compare_many_returns_comparison_result():
    result = compare_many(REF, ["0 9 * * 1-5"])
    assert isinstance(result, ComparisonResult)


def test_compare_many_entry_count_matches_input():
    exprs = ["0 9 * * 1-5", "0 10 * * *", "*/5 * * * *"]
    result = compare_many(REF, exprs)
    assert len(result.entries) == 3


def test_compare_many_entries_are_comparison_entries():
    result = compare_many(REF, ["0 9 * * 1-5"])
    assert all(isinstance(e, ComparisonEntry) for e in result.entries)


# ---------------------------------------------------------------------------
# Scores
# ---------------------------------------------------------------------------

def test_identical_expression_has_score_one():
    result = compare_many(REF, [REF])
    assert result.entries[0].score == pytest.approx(1.0)


def test_completely_different_expression_has_lower_score():
    result = compare_many(REF, ["*/5 * * * *"])
    assert result.entries[0].score < 1.0


def test_score_between_zero_and_one():
    exprs = ["0 9 * * 1-5", "30 8 * * *", "0 0 1 1 *"]
    result = compare_many(REF, exprs)
    for entry in result.entries:
        if entry.valid:
            assert 0.0 <= entry.score <= 1.0


# ---------------------------------------------------------------------------
# valid / error handling
# ---------------------------------------------------------------------------

def test_valid_expression_has_no_error():
    result = compare_many(REF, [REF])
    assert result.entries[0].valid
    assert result.entries[0].error is None


def test_invalid_expression_sets_error():
    result = compare_many(REF, ["not a cron"])
    assert not result.entries[0].valid
    assert result.entries[0].error is not None


def test_invalid_reference_all_entries_have_errors():
    result = compare_many("bad reference", ["* * * * *", "0 9 * * *"])
    assert all(not e.valid for e in result.entries)
    assert all("Invalid reference" in e.error for e in result.entries)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def test_valid_count():
    result = compare_many(REF, [REF, "not cron", "0 10 * * *"])
    assert result.valid_count == 2


def test_error_count():
    result = compare_many(REF, [REF, "not cron"])
    assert result.error_count == 1


def test_best_returns_highest_score():
    result = compare_many(REF, [REF, "*/5 * * * *"])
    best = result.best()
    assert best is not None
    assert best.score == pytest.approx(1.0)


def test_best_returns_none_when_all_invalid():
    result = compare_many(REF, ["bad", "also bad"])
    assert result.best() is None


def test_above_threshold_filters_correctly():
    result = compare_many(REF, [REF, "*/5 * * * *"])
    above = result.above_threshold(0.9)
    assert all(e.score >= 0.9 for e in above)


def test_above_threshold_empty_when_none_qualify():
    result = compare_many(REF, ["*/5 * * * *"])
    above = result.above_threshold(1.0)
    # The non-identical expression should not reach score 1.0
    for entry in above:
        assert entry.score >= 1.0


# ---------------------------------------------------------------------------
# __str__ smoke tests
# ---------------------------------------------------------------------------

def test_str_contains_reference():
    result = compare_many(REF, [REF])
    assert REF in str(result)


def test_entry_str_valid():
    result = compare_many(REF, [REF])
    s = str(result.entries[0])
    assert "similarity" in s


def test_entry_str_invalid():
    result = compare_many(REF, ["bad cron"])
    s = str(result.entries[0])
    assert "ERROR" in s
