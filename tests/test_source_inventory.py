"""DIK-LEX-1 discovery-only inventory checks (positive and negative)."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from dik.source_inventory import inspect_inventory


SEED = Path(__file__).resolve().parents[1] / "examples/world-dictionaries/source-inventory.json"


def seed():
    return json.loads(SEED.read_text(encoding="utf-8"))


def test_seed_is_only_discovery():
    report = inspect_inventory(seed())
    assert report["declared_locales"] == 7
    assert report["source_records"] == 3
    assert report["published_dictionaries"] == 0
    assert report["verified_translations"] == 0


def test_301_sparse_locales_are_not_301_translations():
    doc = seed()
    doc["locales"] = [
        {"tag": f"qaa-x-{i}", "candidate_sources": [], "coverage": "not_measured"}
        for i in range(301)
    ]
    report = inspect_inventory(doc)
    assert report["declared_locales"] == 301
    assert report["verified_translations"] == 0


@pytest.mark.parametrize("invalid", [
    {"tag": "fr_CA", "candidate_sources": [], "coverage": "not_measured"},
    {"tag": "fr", "candidate_sources": [], "coverage": "verified"},
    {"tag": "fr", "candidate_sources": [], "coverage": "not_measured", "exactMatch": "Q1"},
])
def test_reject_incorrect_or_unsupported_locale_claims(invalid):
    doc = seed()
    doc["locales"] = [invalid]
    with pytest.raises(ValidationError):
        inspect_inventory(doc)


def test_reject_unknown_source_references():
    doc = seed()
    doc["locales"][0]["candidate_sources"] = ["not-declared"]
    with pytest.raises(ValueError, match="undeclared"):
        inspect_inventory(doc)


def test_reject_duplicate_locales_case_insensitive():
    doc = seed()
    doc["locales"].append({"tag": "FR", "candidate_sources": [], "coverage": "not_measured"})
    with pytest.raises(ValueError, match="duplicate locale"):
        inspect_inventory(doc)


def test_reject_lexemes_as_entity_labels():
    doc = seed()
    doc["sources"][1]["target"] = "qp-label-candidates"
    with pytest.raises(ValueError, match="incompatible"):
        inspect_inventory(doc)


def test_reject_published_registry():
    doc = seed()
    doc["purpose"] = "published"
    with pytest.raises(ValidationError):
        inspect_inventory(doc)


def test_reject_duplicate_source_ids():
    doc = seed()
    doc["sources"].append(copy.deepcopy(doc["sources"][0]))
    with pytest.raises(ValueError, match="duplicate source"):
        inspect_inventory(doc)
