"""Tests for cronparse.formatter and cronparse.cli modules."""

import json
import pytest

from cronparse.parser import CronExpression
from cronparse.formatter import to_dict, to_json, to_table, to_cron_string
from cronparse.cli import run


# --- formatter tests ---

def test_to_dict_wildcard():
    expr = CronExpression("* * * * *")
    result = to_dict(expr)
    assert isinstance(result, dict)
    assert "minute" in result
    assert "hour" in result


def test_to_json_structure():
    expr = CronExpression("0 12 * * 1")
    output = to_json(expr)
    data = json.loads(output)
    assert "expression" in data
    assert "fields" in data
    assert data["expression"] == "0 12 * * 1"


def test_to_table_contains_labels():
    expr = CronExpression("30 6 * * *")
    table = to_table(expr)
    assert "Minute" in table
    assert "Hour" in table
    assert "Day of Month" in table
    assert "Month" in table
    assert "Day of Week" in table


def test_to_table_contains_expression():
    expr = CronExpression("0 0 1 1 *")
    table = to_table(expr)
    assert "0 0 1 1 *" in table


def test_to_cron_string_roundtrip():
    raw = "*/5 0 * * 1-5"
    expr = CronExpression(raw)
    result = to_cron_string(expr)
    # Reconstruct should produce same fields
    parts = result.split()
    assert len(parts) == 5


def test_to_cron_string_wildcard():
    expr = CronExpression("* * * * *")
    assert to_cron_string(expr) == "* * * * *"


# --- CLI tests ---

def test_cli_human_format(capsys):
    ret = run(["0 9 * * 1", "--format", "human"])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_cli_json_format(capsys):
    ret = run(["* * * * *", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "expression" in data


def test_cli_table_format(capsys):
    ret = run(["0 12 * * *", "--format", "table"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Minute" in captured.out


def test_cli_cron_format(capsys):
    ret = run(["0 0 * * *", "--format", "cron"])
    assert ret == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip().split()) == 5


def test_cli_invalid_expression(capsys):
    ret = run(["invalid expression here"])
    assert ret == 1


def test_cli_invalid_expression_prints_error(capsys):
    """Ensure that an invalid expression produces a non-empty error message on stderr."""
    ret = run(["invalid expression here"])
    assert ret == 1
    captured = capsys.readouterr()
    assert len(captured.err.strip()) > 0


def test_cli_check_conflicts_no_issues(capsys):
    ret = run(["0 12 * * *", "--check-conflicts"])
    assert ret == 0
