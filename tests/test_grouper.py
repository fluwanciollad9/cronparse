"""Tests for cronparse.grouper module."""

import pytest
from cronparse.grouper import group, GroupResult


def test_group_returns_group_result():
    result = group(["0 9 * * *", "30 9 * * *"])
    assert isinstance(result, GroupResult)


def test_group_by_hour_same_hour():
    result = group(["0 9 * * *", "30 9 * * 1"], by="hour")
    assert "9" in result.groups
    assert len(result.groups["9"]) == 2


def test_group_by_hour_different_hours():
    result = group(["0 8 * * *", "0 9 * * *", "0 10 * * *"], by="hour")
    assert result.group_count == 3
    assert "8" in result.groups
    assert "9" in result.groups
    assert "10" in result.groups


def test_group_by_minute():
    result = group(["0 * * * *", "0 9 * * *", "30 6 * * *"], by="minute")
    assert "0" in result.groups
    assert len(result.groups["0"]) == 2
    assert "30" in result.groups


def test_group_by_dow():
    result = group(["0 9 * * 1", "0 10 * * 1", "0 9 * * 5"], by="dow")
    assert "1" in result.groups
    assert len(result.groups["1"]) == 2
    assert "5" in result.groups


def test_group_by_month():
    result = group(["0 0 1 1 *", "0 0 1 1 5", "0 0 1 6 *"], by="month")
    assert "1" in result.groups
    assert len(result.groups["1"]) == 2


def test_group_wildcard_field():
    result = group(["* * * * *", "0 * * * *"], by="hour")
    assert "*" in result.groups


def test_group_invalid_expression_goes_to_errors():
    result = group(["0 9 * * *", "not a cron"], by="hour")
    assert "not a cron" in result.errors
    assert result.error_count == 1


def test_group_all_invalid():
    result = group(["bad1", "bad2"], by="hour")
    assert result.group_count == 0
    assert result.error_count == 2


def test_group_unknown_field_raises():
    with pytest.raises(ValueError, match="Unknown grouping field"):
        group(["0 9 * * *"], by="second")


def test_group_empty_list():
    result = group([], by="hour")
    assert result.group_count == 0
    assert result.error_count == 0


def test_group_result_str_contains_key():
    result = group(["0 9 * * *"], by="hour")
    text = str(result)
    assert "[9]" in text
    assert "0 9 * * *" in text


def test_group_result_str_contains_errors():
    result = group(["bad_expr"], by="hour")
    text = str(result)
    assert "[errors]" in text
    assert "bad_expr" in text
