"""Tests for cronparse.parser module."""

import pytest
from cronparse.parser import parse, ParseError, CronExpression


def test_parse_wildcard_all_fields():
    expr = parse("* * * * *")
    assert isinstance(expr, CronExpression)
    assert expr.fields[0].values == list(range(0, 60))  # minute
    assert expr.fields[1].values == list(range(0, 24))  # hour


def test_parse_specific_values():
    expr = parse("30 9 1 6 1")
    d = expr.as_dict()
    assert d["minute"] == [30]
    assert d["hour"] == [9]
    assert d["day_of_month"] == [1]
    assert d["month"] == [6]
    assert d["day_of_week"] == [1]


def test_parse_step_expression():
    expr = parse("*/15 * * * *")
    assert expr.fields[0].values == [0, 15, 30, 45]


def test_parse_range_expression():
    expr = parse("0 9-17 * * *")
    assert expr.fields[1].values == list(range(9, 18))


def test_parse_list_expression():
    expr = parse("0 8,12,18 * * *")
    assert expr.fields[1].values == [8, 12, 18]


def test_parse_month_alias():
    expr = parse("0 0 1 Jan *")
    assert expr.fields[3].values == [1]


def test_parse_dow_alias():
    expr = parse("0 0 * * Mon")
    assert expr.fields[4].values == [1]


def test_parse_combined():
    expr = parse("0,30 8-10 */5 * *")
    assert expr.fields[0].values == [0, 30]
    assert expr.fields[1].values == [8, 9, 10]
    assert 1 in expr.fields[2].values
    assert 6 in expr.fields[2].values


def test_parse_wrong_field_count_raises():
    with pytest.raises(ParseError, match="Expected 5 fields"):
        parse("* * * *")


def test_parse_out_of_range_raises():
    with pytest.raises(ParseError, match="out of range"):
        parse("60 * * * *")


def test_parse_invalid_range_raises():
    with pytest.raises(ParseError, match="Invalid range"):
        parse("0 18-9 * * *")


def test_parse_zero_step_raises():
    with pytest.raises(ParseError, match="Step must be positive"):
        parse("*/0 * * * *")


def test_as_dict_keys():
    expr = parse("* * * * *")
    keys = set(expr.as_dict().keys())
    assert keys == {"minute", "hour", "day_of_month", "month", "day_of_week"}
