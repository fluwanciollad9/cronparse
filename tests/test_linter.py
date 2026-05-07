"""Tests for cronparse.linter."""

import pytest
from cronparse.linter import lint, LintResult, LintIssue


def test_lint_returns_lint_result():
    result = lint("* * * * *")
    assert isinstance(result, LintResult)


def test_lint_clean_expression_no_issues():
    result = lint("0 9 * * 1")
    assert result.valid
    assert not result.has_issues


def test_lint_invalid_expression_sets_error():
    result = lint("not a cron")
    assert not result.valid
    assert result.error


def test_lint_step_one_warning():
    result = lint("*/1 * * * *")
    assert result.valid
    codes = [i.code for i in result.issues]
    assert "L001" in codes


def test_lint_step_one_correct_field_name():
    result = lint("* */1 * * *")
    issue = next(i for i in result.issues if i.code == "L001")
    assert issue.field == "hour"


def test_lint_step_one_severity_is_warning():
    result = lint("*/1 * * * *")
    issue = next(i for i in result.issues if i.code == "L001")
    assert issue.severity == "warning"


def test_lint_leading_zero_info():
    result = lint("05 * * * *")
    codes = [i.code for i in result.issues]
    assert "L002" in codes


def test_lint_leading_zero_severity_is_info():
    result = lint("05 * * * *")
    issue = next(i for i in result.issues if i.code == "L002")
    assert issue.severity == "info"


def test_lint_no_leading_zero_for_single_digit():
    result = lint("5 * * * *")
    codes = [i.code for i in result.issues]
    assert "L002" not in codes


def test_lint_redundant_range_warning():
    result = lint("* * 5-5 * *")
    codes = [i.code for i in result.issues]
    assert "L003" in codes


def test_lint_redundant_range_correct_field():
    result = lint("* * * * 3-3")
    issue = next(i for i in result.issues if i.code == "L003")
    assert issue.field == "day_of_week"


def test_lint_valid_range_no_l003():
    result = lint("* * 1-5 * *")
    codes = [i.code for i in result.issues]
    assert "L003" not in codes


def test_lint_multiple_issues_detected():
    result = lint("*/1 * 3-3 * *")
    codes = [i.code for i in result.issues]
    assert "L001" in codes
    assert "L003" in codes


def test_lint_str_no_issues():
    result = lint("0 0 * * *")
    assert "no issues" in str(result)


def test_lint_str_with_issues():
    result = lint("*/1 * * * *")
    text = str(result)
    assert "L001" in text


def test_lint_str_error():
    result = lint("bad expr")
    text = str(result)
    assert "error" in text.lower()


def test_lint_issue_str():
    issue = LintIssue(field="minute", code="L001", message="test msg", severity="warning")
    text = str(issue)
    assert "WARNING" in text
    assert "L001" in text
    assert "minute" in text
