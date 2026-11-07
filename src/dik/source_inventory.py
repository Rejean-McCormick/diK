"""Offline discovery-only source inventory, outside canonical Framework dictionaries.

LEX-001/005/020/023: no label-based identity, no implied coverage or publication.
Locale tags receive only a preliminary syntax check, NOT IANA BCP 47 verification.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).parent / "contracts" / "dik-dictionary-source-inventory.schema.json"
TARGET_BY_KIND = {
    "wikidata-qp": "qp-label-candidates",
    "wikidata-lexemes": "lexeme-observations",
    "external-dictionary": "external-term-candidates",
}


def inspect_inventory(document: dict[str, Any]) -> dict[str, Any]:
    """Validate candidate metadata and summarize it without claiming lexical coverage."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(document)
    sources = document["sources"]
    source_ids = [entry["source_id"] for entry in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("duplicate source_id")
    for source in sources:
        if source["target"] != TARGET_BY_KIND[source["kind"]]:
            raise ValueError("source kind and target are incompatible")
    known = set(source_ids)
    locales = document["locales"]
    tags = [entry["tag"].casefold() for entry in locales]
    if len(tags) != len(set(tags)):
        raise ValueError("duplicate locale tag (case-insensitive)")
    for locale in locales:
        unknown = set(locale["candidate_sources"]) - known
        if unknown:
            raise ValueError(f"undeclared candidate sources: {sorted(unknown)}")
    return {
        "inventory_id": document["inventory_id"],
        "source_records": len(sources),
        "declared_locales": len(locales),
        "verified_translations": 0,
        "published_dictionaries": 0,
        "status": "discovery_only",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a discovery-only diK source inventory")
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    document = json.loads(args.inventory.read_text(encoding="utf-8"))
    print(json.dumps(inspect_inventory(document), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
