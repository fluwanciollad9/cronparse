"""Tests for cronparse.batch_auditor."""

import pytest
from cronparse.batch_auditor import audit_many, BatchAuditResult


CLEAN = "30 6 * * 1"
EVERY_MIN = "* * * * *"
STEP_ONE = "*/1 * * * *"
INVALID = "not valid"


def test_audit_many_returns_batch_result():
    result = audit_many([CLEAN])
    assert isinstance(result, BatchAuditResult)


def test_audit_many_result_count_matches_input():
    result = audit_many([CLEAN, EVERY_MIN, INVALID])
    assert len(result.results) == 3


def test_audit_many_valid_count():
    result = audit_many([CLEAN, EVERY_MIN, INVALID])
    assert result.valid_count() == 2


def test_audit_many_error_count():
    result = audit_many([CLEAN, EVERY_MIN, INVALID])
    assert result.error_count() == 1


def test_audit_many_clean_count():
    result = audit_many([CLEAN, EVERY_MIN, INVALID])
    assert result.clean_count() == 1


def test_audit_many_critical_count():
    result = audit_many([EVERY_MIN])
    assert result.critical_count() >= 1


def test_audit_many_warning_count():
    result = audit_many([STEP_ONE])
    assert result.warning_count() >= 1


def test_audit_many_empty_input():
    result = audit_many([])
    assert len(result.results) == 0
    assert result.valid_count() == 0


def test_audit_many_by_severity_keys():
    result = audit_many([CLEAN, EVERY_MIN, INVALID])
    groups = result.by_severity()
    assert set(groups.keys()) == {"critical", "warning", "clean", "error"}


def test_audit_many_by_severity_clean():
    result = audit_many([CLEAN])
    groups = result.by_severity()
    assert len(groups["clean"]) == 1


def test_audit_many_by_severity_critical():
    result = audit_many([EVERY_MIN])
    groups = result.by_severity()
    assert len(groups["critical"]) == 1


def test_audit_many_by_severity_error():
    result = audit_many([INVALID])
    groups = result.by_severity()
    assert len(groups["error"]) == 1


def test_audit_many_str_contains_total():
    result = audit_many([CLEAN, INVALID])
    text = str(result)
    assert "total=2" in text


def test_audit_many_str_contains_errors():
    result = audit_many([INVALID])
    text = str(result)
    assert "errors=1" in text


def test_audit_many_all_clean():
    result = audit_many([CLEAN, "0 12 * * *", "15 3 * * 5"])
    assert result.clean_count() == 3
    assert result.critical_count() == 0
