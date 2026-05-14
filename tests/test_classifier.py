"""Tests for cronparse.classifier module."""

import pytest
from cronparse.classifier import (
    classify,
    classify_many,
    ClassificationResult,
    BatchClassification,
    CATEGORY_EVERY_MINUTE,
    CATEGORY_SUB_HOURLY,
    CATEGORY_HOURLY,
    CATEGORY_DAILY,
    CATEGORY_WEEKLY,
    CATEGORY_MONTHLY,
    CATEGORY_YEARLY,
    CATEGORY_CUSTOM,
)


def test_classify_returns_classification_result():
    result = classify("* * * * *")
    assert isinstance(result, ClassificationResult)


def test_classify_every_minute():
    result = classify("* * * * *")
    assert result.valid
    assert result.category == CATEGORY_EVERY_MINUTE


def test_classify_hourly():
    result = classify("0 * * * *")
    assert result.valid
    assert result.category == CATEGORY_HOURLY


def test_classify_sub_hourly_step():
    result = classify("*/15 * * * *")
    assert result.valid
    assert result.category == CATEGORY_SUB_HOURLY


def test_classify_sub_hourly_list():
    result = classify("0,30 * * * *")
    assert result.valid
    assert result.category == CATEGORY_SUB_HOURLY


def test_classify_daily():
    result = classify("0 9 * * *")
    assert result.valid
    assert result.category == CATEGORY_DAILY


def test_classify_weekly():
    result = classify("0 9 * * 1")
    assert result.valid
    assert result.category == CATEGORY_WEEKLY


def test_classify_monthly():
    result = classify("0 9 1 * *")
    assert result.valid
    assert result.category == CATEGORY_MONTHLY


def test_classify_yearly():
    result = classify("0 0 1 1 *")
    assert result.valid
    assert result.category == CATEGORY_YEARLY


def test_classify_invalid_expression_sets_error():
    result = classify("invalid")
    assert not result.valid
    assert result.error is not None
    assert result.category is None


def test_classify_str_valid():
    result = classify("0 9 * * *")
    text = str(result)
    assert "daily" in text
    assert "0 9 * * *" in text


def test_classify_str_invalid():
    result = classify("bad expr")
    text = str(result)
    assert "error" in text


def test_classify_many_returns_batch():
    batch = classify_many(["* * * * *", "0 9 * * *"])
    assert isinstance(batch, BatchClassification)
    assert len(batch.results) == 2


def test_classify_many_valid_count():
    batch = classify_many(["* * * * *", "0 9 * * *", "bad"])
    assert batch.valid_count == 2
    assert batch.error_count == 1


def test_classify_many_by_category_groups_correctly():
    batch = classify_many(["* * * * *", "0 9 * * *", "0 8 * * *"])
    groups = batch.by_category()
    assert CATEGORY_EVERY_MINUTE in groups
    assert CATEGORY_DAILY in groups
    assert len(groups[CATEGORY_DAILY]) == 2


def test_classify_many_str_contains_all_expressions():
    batch = classify_many(["* * * * *", "0 9 * * *"])
    text = str(batch)
    assert "* * * * *" in text
    assert "0 9 * * *" in text


def test_classify_many_empty_list():
    batch = classify_many([])
    assert batch.valid_count == 0
    assert batch.error_count == 0
    assert batch.by_category() == {}
