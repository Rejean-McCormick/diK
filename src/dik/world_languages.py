"""Versioned ISO 639-3 *discovery candidates*, not published language dictionaries.

This module intentionally does not canonicalize BCP 47 tags or assign any
Wikidata, GF, or Kristal lexical entry. It can audit a frozen JSONL snapshot
without importing the optional pycountry tool used to generate that snapshot.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA = Path(__file__).parent / "contracts" / "dik-language-code-candidate.schema.json"
PROFILE = "dik.language-code-candidates/0.1-candidate"
CODE = re.compile(r"[a-z]{3}\Z")


def _canonical_line(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for data in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def inspect_language_candidates(index_path: Path, manifest_path: Path) -> dict[str, Any]:
    """Validate a frozen code index; never imply IANA or dictionary certification."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mandatory = {
        "profile", "purpose", "source", "source_version", "source_data_sha256",
        "file_sha256", "record_count", "bcp47_status", "dictionary_status",
    }
    if set(manifest) != mandatory:
        raise ValueError("manifest fields must match the candidate profile exactly")
    if manifest["profile"] != PROFILE or manifest["purpose"] != "discovery_only":
        raise ValueError("manifest cannot be a published dictionary")
    if manifest["source"] != "pycountry:iso639-3" or not isinstance(manifest["source_version"], str):
        raise ValueError("unrecognized source provenance")
    if not manifest["source_version"]:
        raise ValueError("missing source version")
    if manifest["bcp47_status"] != "not_iana_validated" or manifest["dictionary_status"] != "none_imported":
        raise ValueError("manifest must not assert IANA validation or dictionary coverage")
    if not isinstance(manifest["record_count"], int) or isinstance(manifest["record_count"], bool) or manifest["record_count"] < 1:
        raise ValueError("invalid record count")
    for key in ("file_sha256", "source_data_sha256"):
        if not isinstance(manifest[key], str) or not re.fullmatch(r"[0-9a-f]{64}", manifest[key]):
            raise ValueError(f"invalid {key}")
    if _sha256(index_path) != manifest["file_sha256"]:
        raise ValueError("index SHA-256 mismatch")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    seen: set[str] = set()
    previous = ""
    type_counts: Counter[str] = Counter()
    scope_counts: Counter[str] = Counter()
    with index_path.open("r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                raise ValueError(f"blank line {n}")
            value = json.loads(line)
            validator.validate(value)
            code = value["alpha3"]
            if code in seen:
                raise ValueError(f"duplicate language code: {code}")
            if previous and code <= previous:
                raise ValueError(f"index not sorted: {code}")
            if _canonical_line(value).decode("utf-8") != line:
                raise ValueError(f"noncanonical JSONL line {n}")
            seen.add(code)
            previous = code
            type_counts[value["type_code"]] += 1
            scope_counts[value["scope_code"]] += 1
    if len(seen) != manifest["record_count"]:
        raise ValueError("manifest record count mismatch")
    return {
        "profile": PROFILE,
        "language_code_candidates": len(seen),
        "types": dict(sorted(type_counts.items())),
        "scopes": dict(sorted(scope_counts.items())),
        "iana_validated_tags": 0,
        "imported_dictionaries": 0,
        "published_dictionaries": 0,
        "lexical_entries": 0,
        "status": "discovery_only",
    }


def build_language_candidates(index_path: Path, manifest_path: Path) -> dict[str, Any]:
    """Generate deterministic frozen index from the locally *installed* pycountry.

    This is an explicit developer action. `pycountry` is not a runtime diK
    dependency, and regeneration is never automatic during a diK import.
    """
    import pycountry  # optional, only used to generate reference candidates

    source_file = Path(pycountry.__file__).parent / "databases" / "iso639-3.json"
    if not source_file.is_file():
        raise FileNotFoundError("expected pycountry iso639-3.json dataset")
    values: list[dict[str, str]] = []
    for language in pycountry.languages:
        alpha3 = getattr(language, "alpha_3", None)
        if not isinstance(alpha3, str) or not CODE.fullmatch(alpha3):
            raise ValueError("unexpected ISO 639-3 code")
        value = {
            "alpha3": alpha3,
            "name_en": language.name,
            "scope_code": language.scope,
            "type_code": language.type,
        }
        alpha2 = getattr(language, "alpha_2", None)
        if alpha2:
            value["alpha2"] = alpha2
        values.append(value)
    values.sort(key=lambda v: v["alpha3"])
    index_path.parent.mkdir(parents=True, exist_ok=True)
    # Use a temporary file and replace atomically only after the write completes.
    staging = index_path.with_suffix(index_path.suffix + ".tmp")
    try:
        with staging.open("wb") as output:
            for value in values:
                output.write(_canonical_line(value))
        manifest = {
            "profile": PROFILE,
            "purpose": "discovery_only",
            "source": "pycountry:iso639-3",
            "source_version": importlib.metadata.version("pycountry"),
            "source_data_sha256": _sha256(source_file),
            "file_sha256": _sha256(staging),
            "record_count": len(values),
            "bcp47_status": "not_iana_validated",
            "dictionary_status": "none_imported",
        }
        # Do not accept a malformed generation; validate using temporary files.
        manifest_tmp = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
        manifest_tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            inspect_language_candidates(staging, manifest_tmp)
            staging.replace(index_path)
            manifest_tmp.replace(manifest_path)
        finally:
            manifest_tmp.unlink(missing_ok=True)
    finally:
        staging.unlink(missing_ok=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit frozen world-language code candidates (not dictionaries)")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "build"):
        p = sub.add_parser(command)
        p.add_argument("index", type=Path)
        p.add_argument("manifest", type=Path)
    args = parser.parse_args()
    if args.command == "inspect":
        report = inspect_language_candidates(args.index, args.manifest)
    else:
        report = build_language_candidates(args.index, args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
