"""Tests for the humanizer and conflict detection modules."""

import pytest
from cronparse.parser import CronExpression
from cronparse.humanizer import humanize
from cronparse.conflicts import detect_conflicts


# ---------------------------------------------------------------------------
# Humanizer tests
# ---------------------------------------------------------------------------

def test_humanize_every_minute():
    result = humanize("* * * * *")
    assert "every minute" in result
    assert "every hour" in result


def test_humanize_specific_time():
    result = humanize("30 9 * * *")
    assert "30" in result
    assert "9" in result


def test_humanize_step_expression():
    result = humanize("*/15 * * * *")
    assert "15" in result


def test_humanize_day_of_week():
    result = humanize("0 9 * * 1")
    assert "Monday" in result


def test_humanize_named_month():
    result = humanize("0 0 1 12 *")
    assert "December" in result


def test_humanize_accepts_string():
    result = humanize("0 0 * * *")
    assert isinstance(result, str)
    assert len(result) > 0


def test_humanize_accepts_expression_object():
    expr = CronExpression.parse("0 12 * * *")
    result = humanize(expr)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_no_conflicts_simple():
    expr = CronExpression.parse("0 9 * * *")
    report = detect_conflicts(expr)
    assert not report.has_conflicts
    assert not report.has_warnings


def test_conflict_feb_31():
    expr = CronExpression.parse("0 0 31 2 *")
    report = detect_conflicts(expr)
    assert report.has_conflicts
    assert any("February" in e for e in report.errors)


def test_conflict_day31_in_april():
    expr = CronExpression.parse("0 0 31 4 *")
    report = detect_conflicts(expr)
    assert report.has_conflicts


def test_warning_dom_and_dow_both_set():
    expr = CronExpression.parse("0 9 15 * 1")
    report = detect_conflicts(expr)
    assert report.has_warnings
    assert any("day-of-month" in w for w in report.warnings)


def test_conflict_report_str():
    expr = CronExpression.parse("0 0 31 2 *")
    report = detect_conflicts(expr)
    text = str(report)
    assert "ERROR" in text


def test_no_conflict_report_str():
    expr = CronExpression.parse("0 9 * * *")
    report = detect_conflicts(expr)
    assert "No conflicts" in str(report)
