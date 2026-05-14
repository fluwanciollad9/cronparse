"""Tests for cronparse.inspector module."""

import pytest
from cronparse.inspector import inspect, InspectionResult, FieldInspection


def test_inspect_returns_inspection_result():
    result = inspect("* * * * *")
    assert isinstance(result, InspectionResult)


def test_inspect_wildcard_all_fields_valid():
    result = inspect("* * * * *")
    assert result.valid is True
    assert result.error is None


def test_inspect_produces_five_field_inspections():
    result = inspect("* * * * *")
    assert len(result.fields) == 5


def test_inspect_field_names_in_order():
    result = inspect("* * * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_inspect_wildcard_field_is_wildcard():
    result = inspect("* * * * *")
    for fi in result.fields:
        assert fi.is_wildcard is True


def test_inspect_wildcard_not_step_range_list():
    result = inspect("* * * * *")
    for fi in result.fields:
        assert fi.is_step is False
        assert fi.is_range is False
        assert fi.is_list is False


def test_inspect_specific_minute_not_wildcard():
    result = inspect("30 * * * *")
    minute = result.fields[0]
    assert minute.is_wildcard is False
    assert minute.raw == "30"


def test_inspect_step_expression_detected():
    result = inspect("*/15 * * * *")
    minute = result.fields[0]
    assert minute.is_step is True


def test_inspect_range_expression_detected():
    result = inspect("0 9-17 * * *")
    hour = result.fields[1]
    assert hour.is_range is True
    assert hour.raw == "9-17"


def test_inspect_list_expression_detected():
    result = inspect("0 0 * * 1,3,5")
    dow = result.fields[4]
    assert dow.is_list is True
    assert dow.token_count == 3


def test_inspect_wildcard_min_max_covers_full_range():
    result = inspect("* * * * *")
    minute = result.fields[0]
    assert minute.min_value == 0
    assert minute.max_value == 59


def test_inspect_specific_value_min_max_equal():
    result = inspect("30 * * * *")
    minute = result.fields[0]
    assert minute.min_value == 30
    assert minute.max_value == 30


def test_inspect_range_min_max():
    result = inspect("0 9-17 * * *")
    hour = result.fields[1]
    assert hour.min_value == 9
    assert hour.max_value == 17


def test_inspect_invalid_expression_not_valid():
    result = inspect("99 99 99 99 99")
    assert result.valid is False
    assert result.error is not None


def test_inspect_invalid_has_no_fields():
    result = inspect("not a cron")
    assert result.valid is False
    assert result.fields == []


def test_inspect_str_valid():
    result = inspect("0 12 * * 1")
    text = str(result)
    assert "0 12 * * 1" in text
    assert "minute" in text


def test_inspect_str_invalid():
    result = inspect("bad")
    text = str(result)
    assert "invalid" in text.lower()


def test_field_inspection_str_wildcard():
    result = inspect("* * * * *")
    text = str(result.fields[0])
    assert "wildcard" in text


def test_field_inspection_str_step():
    result = inspect("*/5 * * * *")
    text = str(result.fields[0])
    assert "step" in text
