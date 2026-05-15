"""Tests for cronparse.filter."""

import pytest

from cronparse.filter import (
    FilterResult,
    filter_by_field,
    filter_by_tag,
    filter_by_predicate,
)


# ---------------------------------------------------------------------------
# FilterResult helpers
# ---------------------------------------------------------------------------

def test_filter_result_initial_counts():
    fr = FilterResult()
    assert fr.match_count == 0
    assert fr.reject_count == 0
    assert fr.error_count == 0


def test_filter_result_populates_correctly():
    fr = FilterResult(matched=["a"], rejected=["b", "c"], errors=["x"])
    assert fr.match_count == 1
    assert fr.reject_count == 2
    assert fr.error_count == 1


# ---------------------------------------------------------------------------
# filter_by_field
# ---------------------------------------------------------------------------

EXPRESSIONS = [
    "0 * * * *",   # minute=0
    "0 0 * * *",   # minute=0, hour=0
    "*/5 * * * *", # minute=*/5
    "0 12 * * *",  # hour=12
]


def test_filter_by_field_minute_zero():
    result = filter_by_field(EXPRESSIONS, "minute", "0")
    assert "0 * * * *" in result.matched
    assert "0 0 * * *" in result.matched
    assert "*/5 * * * *" in result.rejected


def test_filter_by_field_hour_wildcard():
    result = filter_by_field(EXPRESSIONS, "hour", "*")
    assert "0 * * * *" in result.matched
    assert "*/5 * * * *" in result.matched
    assert "0 0 * * *" in result.rejected


def test_filter_by_field_hour_twelve():
    result = filter_by_field(EXPRESSIONS, "hour", "12")
    assert "0 12 * * *" in result.matched
    assert result.match_count == 1


def test_filter_by_field_invalid_expression_goes_to_errors():
    result = filter_by_field(["not a cron", "0 * * * *"], "minute", "0")
    assert result.error_count == 1
    assert "0 * * * *" in result.matched


def test_filter_by_field_unknown_field_raises():
    with pytest.raises(ValueError, match="Unknown field"):
        filter_by_field(["* * * * *"], "second", "0")


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_hourly():
    exprs = ["0 * * * *", "*/5 * * * *", "0 0 * * *"]
    result = filter_by_tag(exprs, "hourly")
    assert "0 * * * *" in result.matched


def test_filter_by_tag_daily():
    exprs = ["0 0 * * *", "0 * * * *"]
    result = filter_by_tag(exprs, "daily")
    assert "0 0 * * *" in result.matched
    assert "0 * * * *" in result.rejected


def test_filter_by_tag_no_match_goes_to_rejected():
    result = filter_by_tag(["* * * * *"], "monthly")
    assert result.reject_count == 1
    assert result.match_count == 0


# ---------------------------------------------------------------------------
# filter_by_predicate
# ---------------------------------------------------------------------------

def test_filter_by_predicate_minute_is_zero():
    exprs = ["0 * * * *", "*/5 * * * *", "0 12 * * *"]
    result = filter_by_predicate(exprs, lambda e: e.minute == "0")
    assert "0 * * * *" in result.matched
    assert "0 12 * * *" in result.matched
    assert "*/5 * * * *" in result.rejected


def test_filter_by_predicate_invalid_expression_captured():
    result = filter_by_predicate(["bad expr", "* * * * *"], lambda e: True)
    assert result.error_count == 1
    assert "* * * * *" in result.matched


def test_filter_by_predicate_all_rejected():
    result = filter_by_predicate(["* * * * *", "0 0 * * *"], lambda e: False)
    assert result.match_count == 0
    assert result.reject_count == 2
