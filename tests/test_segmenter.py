"""Tests for cronparse.segmenter."""

import pytest
from cronparse.segmenter import segment, SegmentResult


def test_segment_returns_segment_result():
    result = segment(["0 * * * *"])
    assert isinstance(result, SegmentResult)


def test_segment_wildcard_hour_appears_in_all_24_buckets():
    result = segment(["0 * * * *"])
    assert result.segment_count == 24
    for h in range(24):
        assert "0 * * * *" in result.segments[h]


def test_segment_specific_hour_single_bucket():
    result = segment(["30 9 * * *"])
    assert 9 in result.segments
    assert "30 9 * * *" in result.segments[9]
    # Should not appear in other hours
    for h in range(24):
        if h != 9:
            assert h not in result.segments or "30 9 * * *" not in result.segments.get(h, [])


def test_segment_range_hour_spans_correct_buckets():
    result = segment(["0 8-10 * * *"])
    for h in (8, 9, 10):
        assert h in result.segments
        assert "0 8-10 * * *" in result.segments[h]
    assert 7 not in result.segments or "0 8-10 * * *" not in result.segments.get(7, [])


def test_segment_step_hour_covers_expected_buckets():
    result = segment(["0 */6 * * *"])
    assert set(result.segments.keys()) == {0, 6, 12, 18}


def test_segment_list_hour_covers_listed_buckets():
    result = segment(["0 1,13 * * *"])
    assert 1 in result.segments
    assert 13 in result.segments
    assert result.segment_count == 2


def test_segment_multiple_expressions_same_hour():
    result = segment(["0 9 * * *", "15 9 * * *"])
    assert len(result.segments[9]) == 2


def test_segment_multiple_expressions_different_hours():
    result = segment(["0 8 * * *", "0 10 * * *"])
    assert 8 in result.segments
    assert 10 in result.segments
    assert "0 8 * * *" not in result.segments.get(10, [])
    assert "0 10 * * *" not in result.segments.get(8, [])


def test_segment_invalid_expression_goes_to_errors():
    result = segment(["not a cron"])
    assert result.error_count == 1
    assert "not a cron" in result.errors
    assert result.segment_count == 0


def test_segment_mixed_valid_and_invalid():
    result = segment(["0 9 * * *", "bad expr"])
    assert result.error_count == 1
    assert result.segment_count == 1


def test_segment_empty_input():
    result = segment([])
    assert result.segment_count == 0
    assert result.error_count == 0


def test_segment_str_contains_hour_label():
    result = segment(["0 9 * * *"])
    output = str(result)
    assert "Hour 09" in output


def test_segment_str_no_segments_shows_placeholder():
    result = segment([])
    assert str(result) == "(no segments)"


def test_segment_str_includes_errors():
    result = segment(["bad"])
    output = str(result)
    assert "Errors" in output or "bad" in output
