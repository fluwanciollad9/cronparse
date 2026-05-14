"""Tests for cronparse.auditor."""

import pytest
from cronparse.auditor import audit, AuditResult, AuditIssue


def test_audit_returns_audit_result():
    result = audit("* * * * *")
    assert isinstance(result, AuditResult)


def test_audit_every_minute_is_valid():
    result = audit("* * * * *")
    assert result.valid is True


def test_audit_every_minute_has_critical():
    result = audit("* * * * *")
    assert result.critical_count() >= 1


def test_audit_every_minute_not_clean():
    result = audit("* * * * *")
    assert result.is_clean() is False


def test_audit_specific_time_is_clean():
    result = audit("30 6 * * 1")
    assert result.valid is True
    assert result.is_clean() is True


def test_audit_specific_time_no_issues():
    result = audit("30 6 * * 1")
    assert result.issues == []


def test_audit_step_one_minute_warning():
    result = audit("*/1 * * * *")
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("Step of 1" in w.message for w in warnings)


def test_audit_step_one_hour_warning():
    result = audit("0 */1 * * *")
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("Step of 1" in w.message for w in warnings)


def test_audit_full_range_equivalent_warning():
    # 0-59 covers all minutes — should warn to use '*'
    result = audit("0-59 * * * *")
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("use '*'" in w.message for w in warnings)


def test_audit_invalid_expression_not_valid():
    result = audit("not a cron")
    assert result.valid is False


def test_audit_invalid_expression_has_error():
    result = audit("not a cron")
    assert result.error is not None
    assert isinstance(result.error, str)


def test_audit_invalid_is_not_clean():
    result = audit("bad")
    assert result.is_clean() is False


def test_audit_warning_count():
    result = audit("*/1 */1 * * *")
    assert result.warning_count() >= 2


def test_audit_issue_str():
    issue = AuditIssue(severity="warning", field="minute", message="test msg")
    text = str(issue)
    assert "WARNING" in text
    assert "minute" in text
    assert "test msg" in text


def test_audit_result_str_valid():
    result = audit("30 6 * * 1")
    text = str(result)
    assert "30 6 * * 1" in text


def test_audit_result_str_invalid():
    result = audit("garbage")
    text = str(result)
    assert "error" in text.lower()


def test_audit_critical_issue_field_name():
    result = audit("* * * * *")
    critical = [i for i in result.issues if i.severity == "critical"]
    assert critical[0].field == "minute"
