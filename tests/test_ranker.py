"""Tests for cronparse.ranker module."""

import pytest
from cronparse.ranker import rank, RankResult, RankedExpression, _frequency_score
from cronparse.parser import parse


def test_rank_returns_rank_result():
    result = rank(["* * * * *", "0 0 * * *"])
    assert isinstance(result, RankResult)


def test_rank_most_frequent_first():
    result = rank(["0 0 * * *", "* * * * *", "0 * * * *"])
    exprs = [r.expression for r in result.ranked]
    # "* * * * *" runs every minute, should be first
    assert exprs[0] == "* * * * *"


def test_rank_reverse_rarest_first():
    result = rank(["* * * * *", "0 0 1 1 *"], reverse=True)
    # rarest first
    assert result.ranked[0].expression == "0 0 1 1 *"


def test_rank_assigns_sequential_ranks():
    result = rank(["0 0 * * *", "* * * * *", "0 * * * *"])
    ranks = [r.rank for r in result.ranked]
    assert ranks == list(range(1, len(ranks) + 1))


def test_rank_invalid_expression_goes_to_errors():
    result = rank(["* * * * *", "not_a_cron"])
    assert len(result.errors) == 1
    assert result.errors[0][0] == "not_a_cron"


def test_rank_error_tuple_has_message():
    result = rank(["invalid"])
    expr, msg = result.errors[0]
    assert isinstance(msg, str)
    assert len(msg) > 0


def test_rank_empty_list():
    result = rank([])
    assert result.ranked == []
    assert result.errors == []


def test_rank_single_expression():
    result = rank(["0 12 * * 1"])
    assert len(result.ranked) == 1
    assert result.ranked[0].rank == 1


def test_frequency_score_every_minute():
    expr = parse("* * * * *")
    score = _frequency_score(expr)
    # 60 * 24 * 31 * 12 * 7
    assert score == 60 * 24 * 31 * 12 * 7


def test_frequency_score_once_a_year():
    expr = parse("0 0 1 1 *")
    score = _frequency_score(expr)
    # 1 minute * 1 hour * 1 day * 1 month * 7 dow
    assert score == 7


def test_ranked_expression_str():
    re = RankedExpression(expression="* * * * *", score=100.0, rank=1, reason="very frequent")
    s = str(re)
    assert "#1" in s
    assert "* * * * *" in s
    assert "very frequent" in s


def test_rank_result_str_includes_all():
    result = rank(["* * * * *", "0 0 * * *"])
    s = str(result)
    assert "* * * * *" in s
    assert "0 0 * * *" in s


def test_rank_result_str_with_errors():
    result = rank(["bad_expr"])
    s = str(result)
    assert "ERROR" in s
    assert "bad_expr" in s


def test_rank_result_str_empty():
    result = RankResult()
    assert str(result) == "(empty)"


def test_rank_scores_are_positive():
    result = rank(["*/5 * * * *", "0 0 * * 0", "30 6 1 * *"])
    for r in result.ranked:
        assert r.score > 0
