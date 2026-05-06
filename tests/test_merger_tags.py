"""Tests for cronparse.tags module."""

import pytest
from cronparse.parser import CronExpression
from cronparse.tags import TagResult, tag, tag_string, KNOWN_TAGS


def _parse(cron: str) -> CronExpression:
    return CronExpression.parse(cron)


# --- TagResult ---

def test_tag_result_has_tag_true():
    result = TagResult(tags=["daily", "midnight"])
    assert result.has_tag("daily")


def test_tag_result_has_tag_false():
    result = TagResult(tags=["daily"])
    assert not result.has_tag("weekly")


def test_tag_result_str_with_tags():
    result = TagResult(tags=["daily", "midnight"])
    assert "daily" in str(result)
    assert "midnight" in str(result)


def test_tag_result_str_no_tags():
    result = TagResult(tags=[])
    assert "none" in str(result)


# --- tag ---

def test_tag_every_minute():
    result = tag(_parse("* * * * *"))
    assert result.has_tag("every_minute")


def test_tag_hourly():
    result = tag(_parse("0 * * * *"))
    assert result.has_tag("hourly")


def test_tag_daily():
    result = tag(_parse("30 8 * * *"))
    assert result.has_tag("daily")


def test_tag_midnight():
    result = tag(_parse("0 0 * * *"))
    assert result.has_tag("midnight")
    assert result.has_tag("daily")


def test_tag_noon():
    result = tag(_parse("0 12 * * *"))
    assert result.has_tag("noon")
    assert result.has_tag("daily")


def test_tag_weekly():
    result = tag(_parse("0 9 * * 1"))
    assert result.has_tag("weekly")


def test_tag_monthly():
    result = tag(_parse("0 6 1 * *"))
    assert result.has_tag("monthly")


def test_tag_yearly():
    result = tag(_parse("0 0 1 1 *"))
    assert result.has_tag("yearly")


def test_tag_business_hours():
    result = tag(_parse("0 10 * * *"))
    assert result.has_tag("business_hours")


def test_tag_custom():
    result = tag(_parse("*/7 */3 * * *"))
    assert result.has_tag("custom")


def test_tag_labels_populated():
    result = tag(_parse("0 0 * * *"))
    assert "frequency" in result.labels
    assert "time" in result.labels


# --- tag_string ---

def test_tag_string_daily():
    result = tag_string("0 8 * * *")
    assert result.has_tag("daily")


def test_all_tags_are_known():
    for cron in ["* * * * *", "0 * * * *", "0 8 * * *", "0 0 * * *",
                 "0 9 * * 1", "0 6 1 * *", "0 0 1 1 *"]:
        result = tag_string(cron)
        for t in result.tags:
            assert t in KNOWN_TAGS, f"Unknown tag '{t}' for '{cron}'"
