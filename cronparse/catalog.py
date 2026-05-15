"""Catalog module for storing, retrieving, and managing named cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.parser import CronExpression, ParseError
from cronparse.humanizer import humanize


@dataclass
class CatalogEntry:
    name: str
    expression: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return f"{self.name}: {self.expression} (tags: {tag_str})"


@dataclass
class CatalogResult:
    entries: List[CatalogEntry] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def entry_count(self) -> int:
        return len(self.entries)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def get(self, name: str) -> Optional[CatalogEntry]:
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None

    def by_tag(self, tag: str) -> List[CatalogEntry]:
        return [e for e in self.entries if tag in e.tags]

    def __str__(self) -> str:
        lines = [f"Catalog: {self.entry_count} entries, {self.error_count} errors"]
        for entry in self.entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)


def build_catalog(named_expressions: Dict[str, str], tags: Optional[Dict[str, List[str]]] = None) -> CatalogResult:
    """Build a catalog from a mapping of name -> cron expression string."""
    result = CatalogResult()
    tags = tags or {}
    for name, expr_str in named_expressions.items():
        try:
            parsed = CronExpression.parse(expr_str)
            desc = humanize(parsed)
            entry = CatalogEntry(
                name=name,
                expression=expr_str,
                description=desc,
                tags=list(tags.get(name, [])),
            )
            result.entries.append(entry)
        except (ParseError, Exception) as exc:
            result.errors[name] = str(exc)
    return result
