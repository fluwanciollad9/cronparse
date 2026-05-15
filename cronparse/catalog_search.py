"""Search utilities for CatalogResult instances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cronparse.catalog import CatalogEntry, CatalogResult
from cronparse.parser import CronExpression
from cronparse.similarity import compare


@dataclass
class SearchResult:
    query: str
    matches: List[CatalogEntry]

    @property
    def match_count(self) -> int:
        return len(self.matches)

    def __str__(self) -> str:
        if not self.matches:
            return f"No matches for '{self.query}'"
        lines = [f"Matches for '{self.query}':"]
        for entry in self.matches:
            lines.append(f"  {entry.name}: {entry.expression}")
        return "\n".join(lines)


def search_by_name(catalog: CatalogResult, query: str) -> SearchResult:
    """Return entries whose name contains the query string (case-insensitive)."""
    q = query.lower()
    matches = [e for e in catalog.entries if q in e.name.lower()]
    return SearchResult(query=query, matches=matches)


def search_by_tag(catalog: CatalogResult, tag: str) -> SearchResult:
    """Return entries that carry the given tag."""
    matches = catalog.by_tag(tag)
    return SearchResult(query=tag, matches=matches)


def search_similar(catalog: CatalogResult, expression: str, threshold: float = 0.7) -> SearchResult:
    """Return catalog entries whose expression is similar to the given one."""
    try:
        ref = CronExpression.parse(expression)
    except Exception:
        return SearchResult(query=expression, matches=[])

    matches = []
    for entry in catalog.entries:
        try:
            candidate = CronExpression.parse(entry.expression)
            report = compare(ref, candidate)
            if report.score >= threshold:
                matches.append(entry)
        except Exception:
            continue
    return SearchResult(query=expression, matches=matches)
