"""Tests for cronparse.diff module."""

import pytest

from cronparse.diff import diff, CronDiff, FieldDiff
from cronparse.parser import ParseError


def test_diff_identical_expressions_no_changes():
    result = diff("* * * * *", "* * * * *")
    assert not result.has_changes
    assert result.changes == []


def test_diff_single_field_change():
    result = diff("0 * * * *", "30 * * * *")
    assert result.has_changes
    assert len(result.changes) == 1
    assert result.changes[0].name == "minute"
    assert result.changes[0].old_value == "0"
    assert result.changes[0].new_value == "30"


def test_diff_multiple_fields_changed():
    result = diff("0 0 * * *", "30 12 * * *")
    assert result.has_changes
    assert len(result.changes) == 2
    assert result.changed_fields == ["minute", "hour"]


def test_diff_all_fields_changed():
    result = diff("* * * * *", "0 12 1 6 1")
    assert len(result.changes) == 5
    assert set(result.changed_fields) == {
        "minute", "hour", "day_of_month", "month", "day_of_week"
    }


def test_diff_step_expression_change():
    result = diff("*/5 * * * *", "*/10 * * * *")
    assert result.has_changes
    assert result.changes[0].name == "minute"
    assert result.changes[0].old_value == "*/5"
    assert result.changes[0].new_value == "*/10"


def test_diff_range_expression_change():
    result = diff("0 9-17 * * *", "0 8-18 * * *")
    assert result.has_changes
    assert result.changes[0].name == "hour"


def test_diff_changed_fields_list():
    result = diff("0 0 1 * *", "0 0 1 12 *")
    assert "month" in result.changed_fields
    assert "minute" not in result.changed_fields


def test_diff_str_no_changes():
    result = diff("* * * * *", "* * * * *")
    assert str(result) == "No differences found."


def test_diff_str_with_changes():
    result = diff("0 * * * *", "5 * * * *")
    output = str(result)
    assert "minute" in output
    assert "0" in output
    assert "5" in output


def test_diff_invalid_old_expression_raises():
    with pytest.raises(Exception):
        diff("invalid", "* * * * *")


def test_diff_invalid_new_expression_raises():
    with pytest.raises(Exception):
        diff("* * * * *", "not valid")


def test_field_diff_str():
    fd = FieldDiff(name="hour", old_value="0", new_value="12")
    assert str(fd) == "hour: '0' -> '12'"


def test_diff_stores_original_expressions():
    result = diff("0 0 * * *", "0 12 * * *")
    assert result.old_expression == "0 0 * * *"
    assert result.new_expression == "0 12 * * *"
