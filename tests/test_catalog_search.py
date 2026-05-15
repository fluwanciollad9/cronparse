"""Tests for cronparse.catalog_search."""

import pytest

from cronparse.catalog import build_catalog
from cronparse.catalog_search import (
    search_by_name,
    search_by_tag,
    search_similar,
    SearchResult,
)

_EXPRESSIONS = {
    "every_minute": "* * * * *",
    "hourly": "0 * * * *",
    "daily_noon": "0 12 * * *",
    "weekly_monday": "0 9 * * 1",
    "monthly_first": "0 0 1 * *",
}

_TAGS = {
    "every_minute": ["frequent"],
    "hourly": ["frequent", "monitoring"],
    "daily_noon": ["daily"],
    "weekly_monday": ["weekly"],
    "monthly_first": ["monthly"],
}


def _catalog():
    return build_catalog(_EXPRESSIONS, tags=_TAGS)


def test_search_by_name_returns_search_result():
    result = search_by_name(_catalog(), "hour")
    assert isinstance(result, SearchResult)


def test_search_by_name_finds_match():
    result = search_by_name(_catalog(), "hourly")
    assert result.match_count == 1
    assert result.matches[0].name == "hourly"


def test_search_by_name_case_insensitive():
    result = search_by_name(_catalog(), "DAILY")
    assert result.match_count >= 1


def test_search_by_name_partial_match():
    result = search_by_name(_catalog(), "week")
    assert result.match_count == 1


def test_search_by_name_no_match():
    result = search_by_name(_catalog(), "zzznomatch")
    assert result.match_count == 0


def test_search_by_name_str_no_matches():
    result = search_by_name(_catalog(), "zzznomatch")
    assert "No matches" in str(result)


def test_search_by_tag_returns_search_result():
    result = search_by_tag(_catalog(), "frequent")
    assert isinstance(result, SearchResult)


def test_search_by_tag_finds_correct_entries():
    result = search_by_tag(_catalog(), "frequent")
    names = [e.name for e in result.matches]
    assert "every_minute" in names
    assert "hourly" in names


def test_search_by_tag_missing_tag_returns_empty():
    result = search_by_tag(_catalog(), "nonexistent_tag")
    assert result.match_count == 0


def test_search_similar_returns_search_result():
    result = search_similar(_catalog(), "0 * * * *")
    assert isinstance(result, SearchResult)


def test_search_similar_finds_identical_expression():
    result = search_similar(_catalog(), "0 * * * *", threshold=0.99)
    names = [e.name for e in result.matches]
    assert "hourly" in names


def test_search_similar_invalid_expression_returns_empty():
    result = search_similar(_catalog(), "not a cron")
    assert result.match_count == 0


def test_search_similar_str_contains_query():
    result = search_similar(_catalog(), "0 * * * *")
    assert "0 * * * *" in str(result)
