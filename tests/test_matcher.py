"""Tests for cronparse.matcher."""

from datetime import datetime

import pytest

from cronparse.matcher import (
    BatchMatchResult,
    MatchResult,
    match,
    match_any,
)

# Fixed reference datetime: 2024-03-15 (Friday) 14:30
DT = datetime(2024, 3, 15, 14, 30)


# ---------------------------------------------------------------------------
# match() — single expression
# ---------------------------------------------------------------------------

def test_match_returns_match_result():
    result = match("* * * * *", DT)
    assert isinstance(result, MatchResult)


def test_match_wildcard_always_matches():
    assert match("* * * * *", DT).matched is True


def test_match_correct_minute():
    assert match("30 * * * *", DT).matched is True


def test_match_wrong_minute():
    assert match("0 * * * *", DT).matched is False


def test_match_correct_hour():
    assert match("* 14 * * *", DT).matched is True


def test_match_wrong_hour():
    assert match("* 9 * * *", DT).matched is False


def test_match_correct_day():
    assert match("* * 15 * *", DT).matched is True


def test_match_wrong_day():
    assert match("* * 1 * *", DT).matched is False


def test_match_correct_month():
    # March == 3
    assert match("* * * 3 *", DT).matched is True


def test_match_wrong_month():
    assert match("* * * 1 *", DT).matched is False


def test_match_correct_dow():
    # 2024-03-15 is Friday; cron Friday == 5
    assert match("* * * * 5", DT).matched is True


def test_match_wrong_dow():
    assert match("* * * * 1", DT).matched is False


def test_match_step_expression_matches():
    # Every 2 minutes — 30 is divisible by 2
    assert match("*/2 * * * *", DT).matched is True


def test_match_step_expression_no_match():
    # Every 7 minutes — 30 % 7 != 0
    assert match("*/7 * * * *", DT).matched is False


def test_match_range_matches():
    assert match("25-35 * * * *", DT).matched is True


def test_match_range_no_match():
    assert match("0-10 * * * *", DT).matched is False


def test_match_list_matches():
    assert match("15,30,45 * * * *", DT).matched is True


def test_match_invalid_expression_returns_error():
    result = match("not_a_cron", DT)
    assert result.matched is False
    assert result.error is not None


def test_match_bool_true():
    assert bool(match("* * * * *", DT)) is True


def test_match_bool_false():
    assert bool(match("0 0 * * *", DT)) is False


def test_match_str_match():
    result = match("* * * * *", DT)
    assert "MATCH" in str(result)


def test_match_str_no_match():
    result = match("0 0 * * *", DT)
    assert "NO MATCH" in str(result)


def test_match_str_error():
    result = match("bad", DT)
    assert "ERROR" in str(result)


# ---------------------------------------------------------------------------
# match_any() — batch
# ---------------------------------------------------------------------------

def test_match_any_returns_batch_result():
    result = match_any(["* * * * *", "0 0 * * *"], DT)
    assert isinstance(result, BatchMatchResult)


def test_match_any_matched_count():
    result = match_any(["* * * * *", "30 14 * * *", "0 0 * * *"], DT)
    assert result.matched_count == 2


def test_match_any_error_count():
    result = match_any(["* * * * *", "bad_expr"], DT)
    assert result.error_count == 1


def test_match_any_matched_expressions():
    result = match_any(["* * * * *", "0 0 * * *"], DT)
    assert "* * * * *" in result.matched_expressions()
    assert "0 0 * * *" not in result.matched_expressions()


def test_match_any_str_contains_datetime():
    result = match_any(["* * * * *"], DT)
    assert DT.isoformat() in str(result)
