"""Tests for cronparse.merger module."""

import pytest
from cronparse.parser import CronExpression
from cronparse.merger import (
    MergeResult,
    _merge_field,
    merge,
    merge_strings,
)


# --- _merge_field ---

def test_merge_field_identical():
    result, conflict = _merge_field("5", "5")
    assert result == "5"
    assert conflict is None


def test_merge_field_wildcard_a():
    result, conflict = _merge_field("*", "10")
    assert result == "10"
    assert conflict is None


def test_merge_field_wildcard_b():
    result, conflict = _merge_field("15", "*")
    assert result == "15"
    assert conflict is None


def test_merge_field_both_wildcards():
    result, conflict = _merge_field("*", "*")
    assert result == "*"
    assert conflict is None


def test_merge_field_distinct_values():
    result, conflict = _merge_field("5", "10")
    assert "5" in result
    assert "10" in result
    assert conflict is None


def test_merge_field_list_union():
    result, conflict = _merge_field("1,2", "2,3")
    assert conflict is None
    tokens = result.split(",")
    assert "1" in tokens
    assert "2" in tokens
    assert "3" in tokens


def test_merge_field_complex_conflict():
    result, conflict = _merge_field("*/5", "10")
    assert conflict is not None
    assert "*/5" in conflict


# --- merge ---

def test_merge_identical_expressions():
    expr = CronExpression.parse("0 12 * * 1")
    result = merge(expr, expr)
    assert isinstance(result, MergeResult)
    assert result.merged_string == "0 12 * * 1"
    assert result.conflicts == []


def test_merge_complementary_wildcards():
    a = CronExpression.parse("0 * * * *")
    b = CronExpression.parse("* 12 * * *")
    result = merge(a, b)
    assert result.merged_string == "0 12 * * *"
    assert result.conflicts == []


def test_merge_distinct_minutes():
    a = CronExpression.parse("5 12 * * *")
    b = CronExpression.parse("10 12 * * *")
    result = merge(a, b)
    assert "5" in result.merged_string
    assert "10" in result.merged_string
    assert result.conflicts == []


def test_merge_with_conflict():
    a = CronExpression.parse("*/5 * * * *")
    b = CronExpression.parse("10 * * * *")
    result = merge(a, b)
    assert len(result.conflicts) == 1
    assert "minute" in result.conflicts[0]


# --- merge_strings ---

def test_merge_strings_basic():
    result = merge_strings("0 6 * * *", "0 18 * * *")
    assert "0" in result.merged_string
    assert "6" in result.merged_string
    assert "18" in result.merged_string


def test_merge_result_str_no_conflicts():
    result = merge_strings("* * * * *", "* * * * *")
    assert str(result) == "* * * * *"


def test_merge_result_str_with_conflicts():
    result = merge_strings("*/5 * * * *", "10 * * * *")
    output = str(result)
    assert "Conflicts" in output
