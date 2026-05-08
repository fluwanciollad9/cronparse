"""Tests for cronparse.annotator module."""

import pytest
from cronparse.annotator import annotate, AnnotationResult, FieldAnnotation, FIELD_NAMES


def test_annotate_returns_annotation_result():
    result = annotate("* * * * *")
    assert isinstance(result, AnnotationResult)


def test_annotate_wildcard_all_fields_valid():
    result = annotate("* * * * *")
    assert result.valid is True
    assert result.parse_error is None


def test_annotate_produces_five_field_annotations():
    result = annotate("* * * * *")
    assert len(result.annotations) == 5


def test_annotate_field_names_in_order():
    result = annotate("* * * * *")
    names = [a.name for a in result.annotations]
    assert names == FIELD_NAMES


def test_annotate_wildcard_notes_contain_wildcard():
    result = annotate("* * * * *")
    for annotation in result.annotations:
        assert "wildcard" in annotation.notes


def test_annotate_specific_values_valid():
    result = annotate("30 9 1 1 1")
    assert result.valid is True


def test_annotate_specific_values_no_wildcard_note():
    result = annotate("30 9 1 1 1")
    for annotation in result.annotations:
        assert "wildcard" not in annotation.notes


def test_annotate_invalid_expression_sets_parse_error():
    result = annotate("not a cron")
    assert result.parse_error is not None
    assert result.valid is False


def test_annotate_invalid_expression_empty_annotations():
    result = annotate("bad expression here")
    assert result.annotations == []


def test_annotate_step_one_note():
    result = annotate("*/1 * * * *")
    minute_ann = result.annotations[0]
    assert "step-of-one is redundant" in minute_ann.notes


def test_annotate_dow_7_note():
    result = annotate("* * * * 7")
    dow_ann = result.annotations[4]
    assert "7 is non-standard for Sunday; prefer 0" in dow_ann.notes


def test_annotate_human_field_not_empty():
    result = annotate("0 12 * * *")
    for annotation in result.annotations:
        assert annotation.human != ""


def test_annotate_as_dict_contains_fields():
    result = annotate("0 6 * * 1")
    d = result.as_dict()
    assert "fields" in d
    assert len(d["fields"]) == 5


def test_annotate_as_dict_error_on_invalid():
    result = annotate("totally wrong")
    d = result.as_dict()
    assert "error" in d
    assert "fields" not in d


def test_annotate_str_contains_expression():
    expr = "30 8 * * 1-5"
    result = annotate(expr)
    assert expr in str(result)


def test_annotate_field_annotation_str_shows_name_and_raw():
    result = annotate("5 4 * * *")
    minute_str = str(result.annotations[0])
    assert "minute" in minute_str
    assert "'5'" in minute_str


def test_annotate_range_expression_valid():
    result = annotate("0 9-17 * * 1-5")
    assert result.valid is True


def test_annotate_named_month_valid():
    result = annotate("0 0 1 JAN *")
    assert result.valid is True
