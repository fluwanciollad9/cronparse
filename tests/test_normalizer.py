"""Tests for cronparse.normalizer module."""

import pytest
from cronparse.parser import CronExpression
from cronparse.normalizer import normalize, normalize_string, _normalize_field, MONTH_ALIASES, DOW_ALIASES


def test_normalize_wildcard_unchanged():
    expr = CronExpression("* * * * *")
    result = normalize(expr)
    assert result.minute == "*"
    assert result.hour == "*"
    assert result.dom == "*"
    assert result.month == "*"
    assert result.dow == "*"


def test_normalize_numeric_unchanged():
    expr = CronExpression("0 12 1 6 3")
    result = normalize(expr)
    assert result.month == "6"
    assert result.dow == "3"


def test_normalize_month_alias_single():
    expr = CronExpression("0 0 1 jan *")
    result = normalize(expr)
    assert result.month == "1"


def test_normalize_month_alias_uppercase():
    expr = CronExpression("0 0 1 DEC *")
    result = normalize(expr)
    assert result.month == "12"


def test_normalize_dow_alias_single():
    expr = CronExpression("0 9 * * mon")
    result = normalize(expr)
    assert result.dow == "1"


def test_normalize_dow_alias_sun():
    expr = CronExpression("0 0 * * sun")
    result = normalize(expr)
    assert result.dow == "0"


def test_normalize_month_range_alias():
    result = _normalize_field("jan-mar", MONTH_ALIASES)
    assert result == "1-3"


def test_normalize_dow_range_alias():
    result = _normalize_field("mon-fri", DOW_ALIASES)
    assert result == "1-5"


def test_normalize_step_with_alias():
    result = _normalize_field("jan-jun/2", MONTH_ALIASES)
    assert result == "1-6/2"


def test_normalize_list_alias():
    result = _normalize_field("jan,mar,dec", MONTH_ALIASES)
    assert result == "1,3,12"


def test_normalize_string_returns_str():
    result = normalize_string("30 6 * feb fri")
    assert isinstance(result, str)
    assert "2" in result  # feb -> 2
    assert "5" in result  # fri -> 5


def test_normalize_string_already_numeric():
    original = "0 12 * * *"
    result = normalize_string(original)
    assert result == original


def test_normalize_returns_cron_expression_instance():
    expr = CronExpression("0 0 * jan mon")
    result = normalize(expr)
    assert isinstance(result, CronExpression)


def test_normalize_preserves_minute_and_hour():
    expr = CronExpression("15 8 * jan *")
    result = normalize(expr)
    assert result.minute == "15"
    assert result.hour == "8"
    assert result.month == "1"
