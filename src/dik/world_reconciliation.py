"""Frozen ISO 639-3 to locally supplied IANA BCP 47 reconciliation.

No Wikidata alignment, translation, or published dictionary is ever inferred.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .iana_registry import Registry, load_registry
from .world_languages import inspect_language_candidates

PROFILE = "dik.world-language-reconciliation/0.1-candidate"
NAME = re.compile(r"^[A-Za-z0-9._-]{1,96}$")


def _line(obj: dict[str, Any]) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    d = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            d.update(chunk)
    return d.hexdigest()


def _reconcile(code: dict, registry: Registry) -> dict:
    iso3 = code["alpha3"]
    iso2 = code.get("alpha2")
    # Both ISO 639-1 and 639-3 identifiers may be represented in IANA;
    # we report both observations without silently asserting equivalence.
    found = []
    for candidate in dict.fromkeys([iso2, iso3]):
        if not candidate:
            continue
        record = registry.get("language", candidate)
        if record is not None:
            found.append({"subtag": candidate, "deprecated": "Deprecated" in record,
                          "preferred_value": record.get("Preferred-Value")})
    if not found:
        state = "not_registered_in_supplied_snapshot"
        preferred = None
    elif any(not item["deprecated"] for item in found):
        state = "registered_candidate"
        preferred = next(item["subtag"] for item in found if not item["deprecated"])
    else:
        state = "deprecated_candidate"
        preferred = next((x["preferred_value"] for x in found if x["preferred_value"]), None)
    return {"alpha3": iso3, "alpha2": iso2, "name_en": code["name_en"],
            "scope_code": code["scope_code"], "type_code": code["type_code"],
            "iana_record_matches": found, "status": state,
            "suggested_language_subtag": preferred,
            "crosswalk_status": "none", "dictionary_status": "none_imported"}


def build_reconciliation(*, index: Path, source_manifest: Path, iana_registry: Path,
                         output_dir: Path) -> dict[str, Any]:
    """Write a new complete, hashed report directory; never overwrite a report."""
    inspect = inspect_language_candidates(index, source_manifest)
    registry = load_registry(iana_registry)
    out = Path(output_dir)
    if out.exists() or out.is_symlink():
        raise FileExistsError("reconciliation output already exists")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".dik-iana-", dir=str(out.parent)) as stage_name:
        stage = Path(stage_name)
        data_path = stage / "reconciliation.jsonl"
        counts: Counter[str] = Counter()
        digest = hashlib.sha256()
        count = 0
        with Path(index).open("r", encoding="utf-8") as src, data_path.open("wb") as dst:
            for raw in src:
                obj = _reconcile(json.loads(raw), registry)
                b = _line(obj)
                dst.write(b)
                digest.update(b)
                counts[obj["status"]] += 1
                count += 1
        manifest = {
            "profile": PROFILE, "purpose": "discovery_only",
            "iso6393_index_sha256": sha256_file(index),
            "iso6393_manifest_sha256": sha256_file(source_manifest),
            "iana_registry_sha256": registry.sha256,
            "iana_registry_file_date": registry.file_date,
            "iana_source_authenticity": "operator_supplied_unverified",
            "records_file": "reconciliation.jsonl",
            "records_sha256": digest.hexdigest(), "record_count": count,
            "status_counts": dict(sorted(counts.items())),
            "published_dictionaries": 0, "approved_external_alignments": 0,
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        # A successful atomic rename is the only publication of these *candidate* reports.
        stage.rename(out)
    return {**manifest, "output": str(out), "iso6393_candidates_checked": inspect["language_code_candidates"]}


def audit_reconciliation(path: Path) -> dict[str, Any]:
    path = Path(path)
    if path.is_symlink():
        raise ValueError("symlink report directory rejected")
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    required = {"profile", "purpose", "iso6393_index_sha256", "iso6393_manifest_sha256",
                "iana_registry_sha256", "iana_registry_file_date", "iana_source_authenticity",
                "records_file", "records_sha256", "record_count", "status_counts",
                "published_dictionaries", "approved_external_alignments"}
    if set(manifest) != required or manifest["profile"] != PROFILE or manifest["purpose"] != "discovery_only":
        raise ValueError("invalid candidate report manifest")
    if manifest["records_file"] != "reconciliation.jsonl" or manifest["published_dictionaries"] != 0 or manifest["approved_external_alignments"] != 0:
        raise ValueError("report must not claim published dictionaries or accepted alignments")
    records = path / "reconciliation.jsonl"
    if records.is_symlink() or not records.is_file() or sha256_file(records) != manifest["records_sha256"]:
        raise ValueError("reconciliation hash mismatch")
    seen = set()
    counter: Counter[str] = Counter()
    prev = ""
    with records.open("rb") as stream:
        for line in stream:
            obj = json.loads(line)
            if _line(obj) != line:
                raise ValueError("noncanonical record")
            key = obj["alpha3"]
            if key <= prev or key in seen:
                raise ValueError("report not ordered or contains duplicate code")
            if obj["dictionary_status"] != "none_imported" or obj["crosswalk_status"] != "none":
                raise ValueError("unauthorized promotion detected")
            seen.add(key)
            prev = key
            counter[obj["status"]] += 1
    if len(seen) != manifest["record_count"] or dict(sorted(counter.items())) != manifest["status_counts"]:
        raise ValueError("reconciliation count mismatch")
    return {"valid": True, "records_checked": len(seen), "registry_file_date": manifest["iana_registry_file_date"],
            "status_counts": dict(sorted(counter.items())), "published_dictionaries": 0}
