"""Review-gated discovery catalog of global lexical and grammatical resources."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).parent / "contracts" / "dik-world-resource-catalog.schema.json"


def inspect_resource_catalog(path: Path) -> dict:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(doc)
    ids = [entry["resource_id"] for entry in doc["resources"]]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate resource_id")
    types = Counter()
    for entry in doc["resources"]:
        u = urlsplit(entry["url"])
        if u.scheme != "https" or not u.hostname or u.username or u.password or u.fragment:
            raise ValueError("resource URL must be an official HTTPS locator without credentials/fragment")
        types[entry["resource_type"]] += 1
    return {"profile": doc["profile"], "catalog_id": doc["catalog_id"],
            "discovery_resources": len(ids), "resource_types": dict(sorted(types.items())),
            "license_approved": 0, "records_imported": 0,
            "dictionaries_published": 0, "status": "discovery_only"}
