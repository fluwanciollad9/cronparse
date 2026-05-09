"""Tests for cronparse.timeline."""

from datetime import datetime

import pytest

from cronparse.timeline import Timeline, TimelineEntry, build_timeline

REF = datetime(2024, 3, 10, 8, 0, 0)


# ---------------------------------------------------------------------------
# build_timeline return type
# ---------------------------------------------------------------------------

def test_build_timeline_returns_timeline():
    result = build_timeline(["* * * * *"], n=3, after=REF)
    assert isinstance(result, Timeline)


def test_build_timeline_entries_are_timeline_entries():
    result = build_timeline(["0 * * * *"], n=2, after=REF)
    for entry in result.entries:
        assert isinstance(entry, TimelineEntry)


# ---------------------------------------------------------------------------
# Sorting & merging
# ---------------------------------------------------------------------------

def test_build_timeline_entries_sorted_ascending():
    result = build_timeline(["*/5 * * * *", "*/7 * * * *"], n=4, after=REF)
    times = [e.at for e in result.entries]
    assert times == sorted(times)


def test_build_timeline_contains_entries_from_all_expressions():
    exprs = ["0 9 * * *", "0 17 * * *"]
    result = build_timeline(exprs, n=2, after=REF)
    found = {e.expression for e in result.entries}
    assert found == set(exprs)


def test_build_timeline_event_count():
    # 2 expressions × 3 runs each = 6 entries
    result = build_timeline(["*/10 * * * *", "*/20 * * * *"], n=3, after=REF)
    assert result.event_count == 6


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_build_timeline_invalid_expression_goes_to_errors():
    result = build_timeline(["not_valid"], n=3, after=REF)
    assert result.error_count == 1
    assert "not_valid" in result.errors


def test_build_timeline_invalid_does_not_add_entries():
    result = build_timeline(["not_valid"], n=3, after=REF)
    assert result.event_count == 0


def test_build_timeline_mixed_valid_and_invalid():
    result = build_timeline(["* * * * *", "bad"], n=2, after=REF)
    assert result.event_count == 2
    assert result.error_count == 1


# ---------------------------------------------------------------------------
# expressions_at
# ---------------------------------------------------------------------------

def test_expressions_at_returns_matching_expression():
    result = build_timeline(["0 9 * * *"], n=3, after=REF)
    # find the first entry and query it
    if result.entries:
        first = result.entries[0]
        matches = result.expressions_at(first.at)
        assert "0 9 * * *" in matches


def test_expressions_at_returns_empty_for_unscheduled_time():
    result = build_timeline(["0 9 * * *"], n=3, after=REF)
    unscheduled = datetime(2000, 1, 1, 0, 0)
    assert result.expressions_at(unscheduled) == []


# ---------------------------------------------------------------------------
# __str__ and helpers
# ---------------------------------------------------------------------------

def test_timeline_str_contains_expression():
    result = build_timeline(["0 0 * * *"], n=1, after=REF)
    assert "0 0 * * *" in str(result)


def test_timeline_str_empty_when_no_entries_no_errors():
    result = build_timeline([], n=5, after=REF)
    assert "empty" in str(result).lower()


def test_timeline_error_count_zero_for_valid_only():
    result = build_timeline(["* * * * *"], n=2, after=REF)
    assert result.error_count == 0


def test_timeline_entry_str_format():
    dt = datetime(2024, 3, 10, 9, 30)
    entry = TimelineEntry(at=dt, expression="30 9 * * *")
    text = str(entry)
    assert "2024-03-10 09:30" in text
    assert "30 9 * * *" in text
