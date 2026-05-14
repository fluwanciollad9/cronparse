"""Tests for cronparse.profiler."""

import pytest
from cronparse.profiler import profile, ExpressionProfile, ProfileResult


def test_profile_returns_profile_result():
    result = profile(["* * * * *"])
    assert isinstance(result, ProfileResult)


def test_profile_result_contains_one_profile_per_expression():
    result = profile(["* * * * *", "0 * * * *"])
    assert len(result.profiles) == 2


def test_profile_valid_count():
    result = profile(["* * * * *", "0 * * * *", "bad"])
    assert result.valid_count == 2


def test_profile_error_count():
    result = profile(["* * * * *", "bad"])
    assert result.error_count == 1


def test_profile_every_minute_runs_per_hour():
    result = profile(["* * * * *"])
    p = result.profiles[0]
    assert p.valid
    assert p.runs_per_hour == 60.0


def test_profile_every_minute_runs_per_day():
    result = profile(["* * * * *"])
    p = result.profiles[0]
    assert p.runs_per_day == 60.0 * 24


def test_profile_hourly_runs_per_hour():
    result = profile(["0 * * * *"])
    p = result.profiles[0]
    assert p.valid
    assert p.runs_per_hour == 1.0


def test_profile_hourly_runs_per_day():
    result = profile(["0 * * * *"])
    p = result.profiles[0]
    assert p.runs_per_day == 24.0


def test_profile_specific_time_runs_per_day():
    result = profile(["30 9 * * *"])
    p = result.profiles[0]
    assert p.valid
    assert p.runs_per_day == 1.0


def test_profile_step_expression():
    result = profile(["*/15 * * * *"])
    p = result.profiles[0]
    assert p.valid
    assert p.runs_per_hour == 4.0


def test_profile_invalid_expression_not_valid():
    result = profile(["not a cron"])
    p = result.profiles[0]
    assert not p.valid
    assert p.error is not None


def test_profile_invalid_has_no_runs():
    result = profile(["bad"])
    p = result.profiles[0]
    assert p.runs_per_hour is None
    assert p.runs_per_day is None


def test_profile_str_valid():
    result = profile(["0 * * * *"])
    text = str(result)
    assert "/hr" in text
    assert "/day" in text


def test_profile_str_invalid():
    result = profile(["bad"])
    text = str(result)
    assert "[invalid]" in text


def test_profile_expression_field_preserved():
    raw = "5 4 * * 1"
    result = profile([raw])
    assert result.profiles[0].expression == raw
