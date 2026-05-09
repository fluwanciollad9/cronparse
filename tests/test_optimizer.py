"""Tests for cronparse.optimizer module."""

import pytest
from cronparse.optimizer import optimize, OptimizeResult, OptimizationHint


def test_optimize_returns_optimize_result():
    result = optimize("* * * * *")
    assert isinstance(result, OptimizeResult)


def test_optimize_clean_expression_unchanged():
    result = optimize("* * * * *")
    assert result.valid
    assert not result.was_changed
    assert result.optimized == "* * * * *"


def test_optimize_step_one_minute_becomes_wildcard():
    result = optimize("*/1 * * * *")
    assert result.valid
    assert result.was_changed
    assert result.optimized.startswith("*")
    assert "minute" in result.hints[0].field_name


def test_optimize_step_one_hour_becomes_wildcard():
    result = optimize("* */1 * * *")
    assert result.valid
    assert result.was_changed
    optimized_parts = result.optimized.split()
    assert optimized_parts[1] == "*"


def test_optimize_range_same_start_end_simplified():
    result = optimize("5-5 * * * *")
    assert result.valid
    assert result.was_changed
    parts = result.optimized.split()
    assert parts[0] == "5"


def test_optimize_range_different_start_end_unchanged():
    result = optimize("1-5 * * * *")
    assert result.valid
    parts = result.optimized.split()
    assert parts[0] == "1-5"


def test_optimize_hint_contains_field_name():
    result = optimize("*/1 * * * *")
    assert len(result.hints) >= 1
    assert result.hints[0].field_name == "minute"


def test_optimize_hint_str_format():
    result = optimize("*/1 * * * *")
    hint = result.hints[0]
    assert isinstance(hint, OptimizationHint)
    s = str(hint)
    assert "->" in s
    assert "minute" in s


def test_optimize_specific_values_unchanged():
    result = optimize("30 9 * * 1")
    assert result.valid
    assert not result.was_changed
    assert result.optimized == "30 9 * * 1"


def test_optimize_multiple_step_ones():
    result = optimize("*/1 */1 * * *")
    assert result.valid
    assert result.was_changed
    assert len(result.hints) == 2


def test_optimize_invalid_expression_returns_error():
    result = optimize("not a cron")
    assert not result.valid
    assert result.error is not None


def test_optimize_invalid_was_changed_false():
    result = optimize("bad expression here")
    assert not result.was_changed


def test_optimize_str_valid():
    result = optimize("*/1 * * * *")
    s = str(result)
    assert "->" in s
    assert "changed" in s


def test_optimize_str_invalid():
    result = optimize("garbage")
    s = str(result)
    assert "error" in s.lower()


def test_optimize_comma_list_with_step_one():
    result = optimize("*/1,*/1 * * * *")
    assert result.valid
    parts = result.optimized.split()
    assert "*/1" not in parts[0]
