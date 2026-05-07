"""Tests for cronparse.summarizer module."""

import pytest
from cronparse.summarizer import (
    summarize,
    group_by_tag,
    ExpressionSummary,
    MultiSummary,
)


EVERY_MINUTE = "* * * * *"
DAILY_NOON = "0 12 * * *"
WEEKLY = "0 9 * * 1"
INVALID = "99 99 99 99 99"
BAD_SYNTAX = "not a cron"


def test_summarize_returns_multi_summary():
    result = summarize([EVERY_MINUTE, DAILY_NOON])
    assert isinstance(result, MultiSummary)
    assert result.total == 2


def test_summarize_all_valid():
    result = summarize([EVERY_MINUTE, DAILY_NOON, WEEKLY])
    assert result.valid == 3
    assert result.invalid == 0


def test_summarize_with_invalid():
    result = summarize([EVERY_MINUTE, BAD_SYNTAX])
    assert result.valid == 1
    assert result.invalid == 1


def test_summarize_invalid_has_error():
    result = summarize([BAD_SYNTAX])
    s = result.summaries[0]
    assert s.error is not None
    assert s.expression is None
    assert s.human is None


def test_summarize_valid_has_human():
    result = summarize([EVERY_MINUTE])
    s = result.summaries[0]
    assert s.error is None
    assert s.human is not None
    assert len(s.human) > 0


def test_summarize_valid_has_tags():
    result = summarize([EVERY_MINUTE])
    s = result.summaries[0]
    assert isinstance(s.tags, list)


def test_summarize_common_tags_subset():
    result = summarize([EVERY_MINUTE, DAILY_NOON])
    for tag in result.common_tags:
        for s in result.summaries:
            if s.error is None:
                assert tag in s.tags


def test_summarize_empty_list():
    result = summarize([])
    assert result.total == 0
    assert result.valid == 0
    assert result.invalid == 0
    assert result.common_tags == []


def test_summarize_all_invalid_no_common_tags():
    result = summarize([BAD_SYNTAX, "also bad"])
    assert result.common_tags == []


def test_group_by_tag_returns_dict():
    result = summarize([EVERY_MINUTE, DAILY_NOON, WEEKLY])
    groups = group_by_tag(result)
    assert isinstance(groups, dict)


def test_group_by_tag_excludes_invalid():
    result = summarize([EVERY_MINUTE, BAD_SYNTAX])
    groups = group_by_tag(result)
    for summaries in groups.values():
        for s in summaries:
            assert s.error is None


def test_group_by_tag_entries_contain_summary():
    result = summarize([EVERY_MINUTE])
    groups = group_by_tag(result)
    for tag_name, summaries in groups.items():
        assert all(isinstance(s, ExpressionSummary) for s in summaries)


def test_expression_summary_str_valid():
    result = summarize([EVERY_MINUTE])
    s = result.summaries[0]
    text = str(s)
    assert EVERY_MINUTE in text
    assert "ERROR" not in text


def test_expression_summary_str_invalid():
    result = summarize([BAD_SYNTAX])
    s = result.summaries[0]
    text = str(s)
    assert "ERROR" in text


def test_multi_summary_str():
    result = summarize([EVERY_MINUTE, DAILY_NOON])
    text = str(result)
    assert "MultiSummary" in text
    assert "2" in text
