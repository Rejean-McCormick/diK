"""S2 discovery index: frozen ISO code candidates, not dictionary availability."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from dik.world_languages import inspect_language_candidates, _canonical_line


BASE = Path(__file__).resolve().parents[1] / "examples" / "world-dictionaries"
INDEX = BASE / "language-code-candidates.jsonl"
MANIFEST = BASE / "language-code-candidates.manifest.json"


def fixture(tmp_path, records=None, manifest_updates=None):
    if records is None:
        records = [
            {"alpha3": "eng", "alpha2": "en", "name_en": "English", "scope_code": "I", "type_code": "L"},
            {"alpha3": "fra", "alpha2": "fr", "name_en": "French", "scope_code": "I", "type_code": "L"},
        ]
    idx = tmp_path / "codes.jsonl"
    idx.write_bytes(b"".join(_canonical_line(x) for x in records))
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["record_count"] = len(records)
    m["file_sha256"] = hashlib.sha256(idx.read_bytes()).hexdigest()
    m.update(manifest_updates or {})
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    return idx, manifest_path


def test_frozen_snapshot_is_auditable():
    report = inspect_language_candidates(INDEX, MANIFEST)
    assert report["language_code_candidates"] == 7910
    assert report["iana_validated_tags"] == 0
    assert report["imported_dictionaries"] == 0
    assert report["published_dictionaries"] == 0
    assert report["lexical_entries"] == 0
    assert report["types"]["L"] > 7000


def test_minimal_candidate_index(tmp_path):
    idx, manifest = fixture(tmp_path)
    assert inspect_language_candidates(idx, manifest)["language_code_candidates"] == 2


def test_unknown_language_counts_are_not_coverage(tmp_path):
    idx, manifest = fixture(tmp_path, manifest_updates={"dictionary_status": "verified"})
    with pytest.raises(ValueError, match="must not assert"):
        inspect_language_candidates(idx, manifest)


def test_reject_claim_of_iana_validation(tmp_path):
    idx, manifest = fixture(tmp_path, manifest_updates={"bcp47_status": "validated"})
    with pytest.raises(ValueError, match="IANA"):
        inspect_language_candidates(idx, manifest)


def test_reject_tampered_file(tmp_path):
    idx, manifest = fixture(tmp_path)
    idx.write_bytes(idx.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        inspect_language_candidates(idx, manifest)


def test_reject_duplicate_codes(tmp_path):
    record = {"alpha3": "eng", "alpha2": "en", "name_en": "English", "scope_code": "I", "type_code": "L"}
    idx, manifest = fixture(tmp_path, [record, copy.deepcopy(record)])
    with pytest.raises(ValueError, match="duplicate language code"):
        inspect_language_candidates(idx, manifest)


def test_reject_unsorted_index(tmp_path):
    records = [
        {"alpha3": "fra", "name_en": "French", "scope_code": "I", "type_code": "L"},
        {"alpha3": "eng", "name_en": "English", "scope_code": "I", "type_code": "L"},
    ]
    idx, manifest = fixture(tmp_path, records)
    with pytest.raises(ValueError, match="not sorted"):
        inspect_language_candidates(idx, manifest)


@pytest.mark.parametrize("invalid", [
    {"alpha3": "en", "name_en": "English", "scope_code": "I", "type_code": "L"},
    {"alpha3": "eng", "alpha2": "english", "name_en": "English", "scope_code": "I", "type_code": "L"},
    {"alpha3": "eng", "name_en": "", "scope_code": "I", "type_code": "L"},
    {"alpha3": "eng", "name_en": "English", "scope_code": "X", "type_code": "L"},
    {"alpha3": "eng", "name_en": "English", "scope_code": "I", "type_code": "X"},
    {"alpha3": "eng", "name_en": "English", "scope_code": "I", "type_code": "L", "KQ": "KQ1"},
    {"alpha3": "eng", "name_en": "English", "scope_code": "I", "type_code": "L", "translations": ["hello"]},
])
def test_reject_malformed_or_inflated_records(tmp_path, invalid):
    idx, manifest = fixture(tmp_path, [invalid])
    with pytest.raises(ValidationError):
        inspect_language_candidates(idx, manifest)


def test_reject_manifest_count_mismatch(tmp_path):
    idx, manifest = fixture(tmp_path, manifest_updates={"record_count": 99})
    with pytest.raises(ValueError, match="count mismatch"):
        inspect_language_candidates(idx, manifest)


def test_reject_manifest_published_profile(tmp_path):
    idx, manifest = fixture(tmp_path, manifest_updates={"purpose": "published"})
    with pytest.raises(ValueError, match="published dictionary"):
        inspect_language_candidates(idx, manifest)


def test_reject_manifest_extra_misleading_fields(tmp_path):
    idx, manifest = fixture(tmp_path, manifest_updates={"available_translations": 7910})
    with pytest.raises(ValueError, match="fields"):
        inspect_language_candidates(idx, manifest)
