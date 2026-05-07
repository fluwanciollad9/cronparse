"""Tests for cronparse.deduplicator."""

import pytest
from cronparse.deduplicator import deduplicate, DeduplicationResult


def test_deduplicate_returns_deduplication_result():
    result = deduplicate(["* * * * *"])
    assert isinstance(result, DeduplicationResult)


def test_deduplicate_single_expression_is_unique():
    result = deduplicate(["0 12 * * *"])
    assert result.unique == ["0 12 * * *"]
    assert result.duplicates == []
    assert result.errors == []


def test_deduplicate_identical_strings_detected():
    result = deduplicate(["0 12 * * *", "0 12 * * *"])
    assert len(result.unique) == 1
    assert len(result.duplicates) == 1
    assert result.duplicates[0][0] == "0 12 * * *"


def test_deduplicate_normalized_equivalents_detected():
    # JAN and 1 normalize to the same value in month field
    result = deduplicate(["0 0 1 JAN *", "0 0 1 1 *"])
    assert len(result.unique) == 1
    assert len(result.duplicates) == 1


def test_deduplicate_different_expressions_all_unique():
    exprs = ["0 6 * * *", "0 12 * * *", "0 18 * * *"]
    result = deduplicate(exprs)
    assert len(result.unique) == 3
    assert result.duplicates == []


def test_deduplicate_preserves_first_occurrence_as_canonical():
    result = deduplicate(["*/5 * * * *", "*/5 * * * *"])
    assert result.unique[0] == "*/5 * * * *"
    assert result.duplicates[0][1] == "*/5 * * * *"


def test_deduplicate_invalid_expression_goes_to_errors():
    result = deduplicate(["not a cron"])
    assert result.errors
    assert result.errors[0][0] == "not a cron"
    assert result.unique == []


def test_deduplicate_mixed_valid_invalid_and_duplicate():
    exprs = ["0 0 * * *", "bad expr", "0 0 * * *"]
    result = deduplicate(exprs)
    assert len(result.unique) == 1
    assert len(result.errors) == 1
    assert len(result.duplicates) == 1


def test_deduplicate_empty_list():
    result = deduplicate([])
    assert result.unique == []
    assert result.duplicates == []
    assert result.errors == []


def test_deduplicate_str_shows_unique_count():
    result = deduplicate(["0 1 * * *", "0 2 * * *"])
    output = str(result)
    assert "Unique expressions: 2" in output


def test_deduplicate_str_shows_duplicates():
    result = deduplicate(["0 1 * * *", "0 1 * * *"])
    output = str(result)
    assert "Duplicates found: 1" in output
    assert "is a duplicate of" in output


def test_deduplicate_str_shows_errors():
    result = deduplicate(["bad"])
    output = str(result)
    assert "Invalid expressions: 1" in output


def test_deduplicate_dow_alias_equivalence():
    # MON and 1 are equivalent day-of-week values
    result = deduplicate(["0 9 * * MON", "0 9 * * 1"])
    assert len(result.unique) == 1
    assert len(result.duplicates) == 1
