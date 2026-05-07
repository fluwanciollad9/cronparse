"""Tests for cronparse.reporter module."""

import json
import pytest
from cronparse.reporter import report, ExpressionReport


EVERY_MINUTE = "* * * * *"
DAILY = "0 12 * * *"
INVALID_SYNTAX = "not_a_cron_expression"


def test_report_returns_expression_report():
    result = report(EVERY_MINUTE)
    assert isinstance(result, ExpressionReport)


def test_report_valid_expression_is_valid():
    result = report(EVERY_MINUTE)
    assert result.valid is True
    assert result.parse_error is None


def test_report_invalid_syntax_not_valid():
    result = report(INVALID_SYNTAX)
    assert result.valid is False
    assert result.parse_error is not None


def test_report_invalid_has_no_human():
    result = report(INVALID_SYNTAX)
    assert result.human is None


def test_report_valid_has_human():
    result = report(EVERY_MINUTE)
    assert result.human is not None
    assert isinstance(result.human, str)
    assert len(result.human) > 0


def test_report_valid_has_tags_list():
    result = report(EVERY_MINUTE)
    assert isinstance(result.tags, list)


def test_report_conflicts_is_bool():
    result = report(DAILY)
    assert isinstance(result.conflicts, bool)


def test_report_validation_errors_is_list():
    result = report(EVERY_MINUTE)
    assert isinstance(result.validation_errors, list)


def test_report_explanation_is_dict():
    result = report(DAILY)
    assert result.explanation is not None
    assert isinstance(result.explanation, dict)


def test_report_explanation_has_expected_keys():
    result = report(DAILY)
    expected_keys = {"minute", "hour", "day", "month", "dow"}
    assert expected_keys.issubset(result.explanation.keys())


def test_report_to_dict_returns_dict():
    result = report(EVERY_MINUTE)
    d = result.to_dict()
    assert isinstance(d, dict)
    assert "raw" in d
    assert "valid" in d
    assert "human" in d
    assert "tags" in d
    assert "conflicts" in d


def test_report_to_json_is_valid_json():
    result = report(EVERY_MINUTE)
    js = result.to_json()
    parsed = json.loads(js)
    assert parsed["raw"] == EVERY_MINUTE


def test_report_str_contains_raw():
    result = report(EVERY_MINUTE)
    text = str(result)
    assert EVERY_MINUTE in text


def test_report_str_invalid_contains_error_label():
    result = report(INVALID_SYNTAX)
    text = str(result)
    assert "Parse error" in text or "error" in text.lower()


def test_report_str_valid_contains_human():
    result = report(EVERY_MINUTE)
    text = str(result)
    assert result.human in text
