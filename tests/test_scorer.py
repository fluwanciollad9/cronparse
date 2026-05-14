"""Tests for cronparse.scorer."""

import pytest
from cronparse.scorer import score, ScoreResult, ExpressionScore


def test_score_returns_score_result():
    result = score(["* * * * *"])
    assert isinstance(result, ScoreResult)


def test_score_result_contains_one_score_per_expression():
    result = score(["* * * * *", "0 9 * * 1"])
    assert len(result.scores) == 2


def test_score_entries_are_expression_scores():
    result = score(["* * * * *"])
    assert isinstance(result.scores[0], ExpressionScore)


def test_score_valid_count():
    result = score(["* * * * *", "bad expression", "0 9 * * 1"])
    assert result.valid_count == 2


def test_score_error_count():
    result = score(["* * * * *", "bad expression"])
    assert result.error_count == 1


def test_score_invalid_expression_not_valid():
    result = score(["bad expression"])
    assert not result.scores[0].valid


def test_score_invalid_has_error_message():
    result = score(["bad expression"])
    assert result.scores[0].error != ""


def test_score_invalid_zero_values():
    result = score(["bad expression"])
    s = result.scores[0]
    assert s.complexity == 0
    assert s.readability == 0
    assert s.overall == 0.0


def test_score_wildcard_complexity_is_zero():
    result = score(["* * * * *"])
    assert result.scores[0].complexity == 0


def test_score_wildcard_readability_is_ten():
    result = score(["* * * * *"])
    assert result.scores[0].readability == 10


def test_score_wildcard_notes_contain_wildcard_only():
    result = score(["* * * * *"])
    assert "wildcard-only" in result.scores[0].notes


def test_score_wildcard_notes_contain_highly_readable():
    result = score(["* * * * *"])
    assert "highly-readable" in result.scores[0].notes


def test_score_specific_values_complexity_nonzero():
    result = score(["0 9 * * 1"])
    assert result.scores[0].complexity > 0


def test_score_step_expression_reduces_readability():
    result_plain = score(["0 9 * * *"])
    result_step = score(["*/5 * * * *"])
    assert result_step.scores[0].readability <= result_plain.scores[0].readability


def test_score_list_expression_increases_complexity():
    result_single = score(["0 9 * * 1"])
    result_list = score(["0 9 * * 1,2,3,4,5"])
    assert result_list.scores[0].complexity > result_single.scores[0].complexity


def test_score_overall_is_float():
    result = score(["0 9 * * 1"])
    assert isinstance(result.scores[0].overall, float)


def test_score_average_overall_zero_when_all_invalid():
    result = score(["bad"])
    assert result.average_overall == 0.0


def test_score_average_overall_positive_when_valid():
    result = score(["* * * * *"])
    assert result.average_overall > 0.0


def test_score_str_contains_expression():
    result = score(["0 9 * * 1"])
    assert "0 9 * * 1" in str(result)


def test_score_str_invalid_shows_invalid_label():
    result = score(["bad"])
    assert "[invalid]" in str(result.scores[0])


def test_score_str_valid_shows_fields():
    result = score(["* * * * *"])
    out = str(result.scores[0])
    assert "complexity=" in out
    assert "readability=" in out
    assert "overall=" in out


def test_score_empty_list():
    result = score([])
    assert result.valid_count == 0
    assert result.error_count == 0
    assert result.average_overall == 0.0
