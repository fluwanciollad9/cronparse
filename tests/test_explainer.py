"""Tests for cronparse.explainer module."""

import pytest
from cronparse.parser import CronExpression
from cronparse.explainer import explain, explain_text


def _parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_explain_wildcard_all_fields():
    result = explain(_parse("* * * * *"))
    assert result["minute"] == "minute: every minute"
    assert result["hour"] == "hour: every hour"
    assert result["day_of_month"] == "day_of_month: every day of month"
    assert result["month"] == "month: every month"
    assert result["day_of_week"] == "day_of_week: every day of week"


def test_explain_specific_values():
    result = explain(_parse("30 9 1 1 0"))
    assert "30" in result["minute"]
    assert "9" in result["hour"]
    assert "1" in result["day_of_month"]
    assert "January" in result["month"]
    assert "Sunday" in result["day_of_week"]


def test_explain_step_expression():
    result = explain(_parse("*/5 * * * *"))
    assert result["minute"] == "minute: every 5 minute(s)"


def test_explain_range_expression():
    result = explain(_parse("0 9-17 * * *"))
    assert "9" in result["hour"]
    assert "17" in result["hour"]
    assert "from" in result["hour"]


def test_explain_range_with_step():
    result = explain(_parse("0 */2 * * *"))
    assert "every 2" in result["hour"]


def test_explain_range_step_combined():
    result = explain(_parse("0 8-18/2 * * *"))
    assert "8" in result["hour"]
    assert "18" in result["hour"]
    assert "every 2" in result["hour"]


def test_explain_list_expression():
    result = explain(_parse("0 0 * 3,6,9 *"))
    assert "March" in result["month"] or "3" in result["month"]


def test_explain_dow_range():
    result = explain(_parse("0 0 * * 1-5"))
    assert "Monday" in result["day_of_week"]
    assert "Friday" in result["day_of_week"]


def test_explain_text_contains_expression():
    expr = _parse("*/15 * * * *")
    text = explain_text(expr)
    assert "*/15 * * * *" in text


def test_explain_text_contains_all_fields():
    expr = _parse("0 12 * * *")
    text = explain_text(expr)
    assert "minute" in text
    assert "hour" in text
    assert "day_of_month" in text
    assert "month" in text
    assert "day_of_week" in text


def test_explain_returns_dict_with_five_keys():
    result = explain(_parse("* * * * *"))
    assert set(result.keys()) == {"minute", "hour", "day_of_month", "month", "day_of_week"}


def test_explain_text_separator_line():
    expr = _parse("0 0 * * *")
    text = explain_text(expr)
    assert "---" in text
