"""Import/export helpers for persisting catalogs as JSON or plain-text."""

from __future__ import annotations

import json
from typing import Any, Dict

from cronparse.catalog import CatalogEntry, CatalogResult, build_catalog


def catalog_to_dict(catalog: CatalogResult) -> Dict[str, Any]:
    """Serialise a CatalogResult to a plain dict."""
    return {
        "entries": [
            {
                "name": e.name,
                "expression": e.expression,
                "description": e.description,
                "tags": e.tags,
            }
            for e in catalog.entries
        ],
        "errors": dict(catalog.errors),
    }


def catalog_to_json(catalog: CatalogResult, indent: int = 2) -> str:
    """Serialise a CatalogResult to a JSON string."""
    return json.dumps(catalog_to_dict(catalog), indent=indent)


def catalog_from_dict(data: Dict[str, Any]) -> CatalogResult:
    """Deserialise a CatalogResult from a plain dict produced by catalog_to_dict."""
    result = CatalogResult()
    for item in data.get("entries", []):
        entry = CatalogEntry(
            name=item["name"],
            expression=item["expression"],
            description=item.get("description", ""),
            tags=list(item.get("tags", [])),
        )
        result.entries.append(entry)
    result.errors.update(data.get("errors", {}))
    return result


def catalog_from_json(text: str) -> CatalogResult:
    """Deserialise a CatalogResult from a JSON string."""
    return catalog_from_dict(json.loads(text))


def catalog_from_mapping(mapping: Dict[str, str]) -> CatalogResult:
    """Convenience wrapper around build_catalog for a bare name->expression dict."""
    return build_catalog(mapping)
