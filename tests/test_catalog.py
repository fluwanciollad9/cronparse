"""Tests for cronparse.catalog and cronparse.catalog_io."""

import json
import pytest

from cronparse.catalog import build_catalog, CatalogEntry, CatalogResult
from cronparse.catalog_io import (
    catalog_to_dict,
    catalog_to_json,
    catalog_from_dict,
    catalog_from_json,
    catalog_from_mapping,
)

_EXPRESSIONS = {
    "every_minute": "* * * * *",
    "hourly": "0 * * * *",
    "daily_noon": "0 12 * * *",
    "weekly_monday": "0 9 * * 1",
}


def _catalog() -> CatalogResult:
    return build_catalog(_EXPRESSIONS)


def test_build_catalog_returns_catalog_result():
    result = _catalog()
    assert isinstance(result, CatalogResult)


def test_build_catalog_entry_count():
    result = _catalog()
    assert result.entry_count == 4


def test_build_catalog_no_errors_for_valid_expressions():
    result = _catalog()
    assert result.error_count == 0


def test_build_catalog_invalid_expression_captured_as_error():
    result = build_catalog({"bad": "not a cron"})
    assert result.error_count == 1
    assert "bad" in result.errors


def test_build_catalog_entry_has_description():
    result = _catalog()
    entry = result.get("every_minute")
    assert entry is not None
    assert len(entry.description) > 0


def test_build_catalog_with_tags():
    result = build_catalog(_EXPRESSIONS, tags={"hourly": ["frequent", "monitoring"]})
    entry = result.get("hourly")
    assert entry is not None
    assert "frequent" in entry.tags


def test_catalog_get_missing_name_returns_none():
    result = _catalog()
    assert result.get("nonexistent") is None


def test_catalog_by_tag_returns_matching_entries():
    result = build_catalog(_EXPRESSIONS, tags={"hourly": ["ops"], "daily_noon": ["ops"]})
    ops = result.by_tag("ops")
    assert len(ops) == 2


def test_catalog_str_contains_entry_count():
    result = _catalog()
    assert "4" in str(result)


def test_catalog_entry_str_contains_name():
    entry = CatalogEntry(name="test", expression="* * * * *", tags=["a"])
    assert "test" in str(entry)


def test_catalog_to_dict_has_entries_key():
    d = catalog_to_dict(_catalog())
    assert "entries" in d
    assert len(d["entries"]) == 4


def test_catalog_to_json_is_valid_json():
    text = catalog_to_json(_catalog())
    data = json.loads(text)
    assert isinstance(data, dict)


def test_catalog_from_dict_roundtrip():
    original = _catalog()
    d = catalog_to_dict(original)
    restored = catalog_from_dict(d)
    assert restored.entry_count == original.entry_count


def test_catalog_from_json_roundtrip():
    original = _catalog()
    text = catalog_to_json(original)
    restored = catalog_from_json(text)
    assert restored.entry_count == original.entry_count


def test_catalog_from_mapping_convenience():
    result = catalog_from_mapping({"daily": "0 0 * * *"})
    assert result.entry_count == 1
