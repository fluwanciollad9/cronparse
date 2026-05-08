"""Tests for cronparse.splitter."""

import pytest
from cronparse.splitter import split, SplitResult


def test_split_returns_split_result():
    result = split(["* * * * *"])
    assert isinstance(result, SplitResult)


def test_split_every_minute():
    result = split(["* * * * *"])
    assert "every_minute" in result.buckets
    assert "* * * * *" in result.buckets["every_minute"]


def test_split_sub_hourly_step():
    result = split(["*/5 * * * *", "*/15 * * * *"])
    assert "sub_hourly" in result.buckets
    assert len(result.buckets["sub_hourly"]) == 2


def test_split_hourly():
    result = split(["0 * * * *", "30 * * * *"])
    assert "hourly" in result.buckets
    assert len(result.buckets["hourly"]) == 2


def test_split_multi_daily_step_hour():
    result = split(["0 */6 * * *"])
    assert "multi_daily" in result.buckets


def test_split_daily():
    result = split(["0 9 * * *", "30 18 * * *"])
    assert "daily" in result.buckets
    assert len(result.buckets["daily"]) == 2


def test_split_weekly():
    result = split(["0 9 * * 1", "0 0 * * MON"])
    assert "weekly" in result.buckets
    assert len(result.buckets["weekly"]) == 2


def test_split_monthly():
    result = split(["0 0 1 * *", "0 12 15 * *"])
    assert "monthly" in result.buckets
    assert len(result.buckets["monthly"]) == 2


def test_split_invalid_expression_goes_to_errors():
    result = split(["not a cron"])
    assert result.error_count() == 1
    assert "not a cron" in result.errors


def test_split_mixed_valid_and_invalid():
    result = split(["0 9 * * *", "bad expr"])
    assert "daily" in result.buckets
    assert result.error_count() == 1


def test_split_empty_input():
    result = split([])
    assert result.bucket_count() == 0
    assert result.error_count() == 0


def test_split_bucket_count():
    result = split(["* * * * *", "0 9 * * *", "0 0 1 * *"])
    assert result.bucket_count() == 3


def test_split_str_contains_bucket_label():
    result = split(["0 9 * * *"])
    output = str(result)
    assert "daily" in output
    assert "0 9 * * *" in output


def test_split_str_empty():
    result = split([])
    assert str(result) == "(empty)"


def test_split_str_shows_errors():
    result = split(["invalid"])
    output = str(result)
    assert "errors" in output
    assert "invalid" in output
