"""Tests for cronparse.validator module."""

import pytest
from cronparse.validator import (
    validate,
    validate_field,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# validate_field
# ---------------------------------------------------------------------------

def test_validate_field_wildcard_is_valid():
    assert validate_field("*", "minute") == []


def test_validate_field_valid_number():
    assert validate_field("30", "minute") == []


def test_validate_field_out_of_range():
    errors = validate_field("60", "minute")
    assert len(errors) == 1
    assert "out of range" in errors[0]


def test_validate_field_valid_range():
    assert validate_field("1-5", "hour") == []


def test_validate_field_inverted_range():
    errors = validate_field("10-5", "hour")
    assert any("range start" in e for e in errors)


def test_validate_field_step_zero():
    errors = validate_field("*/0", "minute")
    assert any("zero" in e for e in errors)


def test_validate_field_valid_step():
    assert validate_field("*/15", "minute") == []


def test_validate_field_named_month_alias():
    assert validate_field("jan", "month") == []


def test_validate_field_named_dow_alias():
    assert validate_field("mon-fri", "day_of_week") == []


def test_validate_field_unknown_alias():
    errors = validate_field("xyz", "month")
    assert any("unknown" in e for e in errors)


def test_validate_field_list_mixed():
    # "0,30,60" — 60 is out of range for minutes
    errors = validate_field("0,30,60", "minute")
    assert len(errors) == 1


# ---------------------------------------------------------------------------
# validate (full expression)
# ---------------------------------------------------------------------------

def test_validate_wrong_number_of_fields():
    result = validate("* * * *")
    assert not result.valid
    assert any("5 fields" in e for e in result.errors)


def test_validate_valid_every_minute():
    result = validate("* * * * *")
    assert result.valid
    assert result.errors == []


def test_validate_specific_valid():
    result = validate("0 9 * * 1-5")
    assert result.valid


def test_validate_invalid_hour():
    result = validate("0 25 * * *")
    assert not result.valid
    assert any("hour" in e for e in result.errors)


def test_validate_dom_and_dow_both_set_warns():
    result = validate("0 12 15 * 1")
    assert result.valid
    assert len(result.warnings) == 1
    assert "OR" in result.warnings[0]


def test_validate_result_bool_true():
    result = validate("* * * * *")
    assert bool(result) is True


def test_validate_result_bool_false():
    result = validate("99 * * * *")
    assert bool(result) is False


def test_validate_result_str_ok():
    result = validate("* * * * *")
    assert str(result) == "OK"


def test_validate_result_str_errors():
    result = validate("99 * * * *")
    assert "ERROR" in str(result)
