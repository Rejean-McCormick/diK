"""Local streaming Wikidata Lexeme L/S/F observations, *not* Kristal dictionaries.

Full-dump JSON/JSONL and .gz/.bz2 line-oriented formats are supported. No
crosswalk, inferred translation, reviewed preference, or grammatical mapping is
produced. Statements/claims not covered by this bounded projection stay in the
original source dump and are not represented as imported.
"""
from __future__ import annotations

import bz2
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import tempfile
from typing import Any

from .iana_registry import Registry, check_tag, load_registry
from .world_reconciliation import sha256_file

PROFILE = "dik.wikidata-lexeme-observations/0.1-candidate"
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}\Z")
LID = re.compile(r"L[1-9][0-9]*\Z")
FID = re.compile(r"(L[1-9][0-9]*)-F[1-9][0-9]*\Z")
SID = re.compile(r"(L[1-9][0-9]*)-S[1-9][0-9]*\Z")
QID = re.compile(r"Q[1-9][0-9]*\Z")
LOCALE = re.compile(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*\Z")


class LexemeError(ValueError):
    pass


def _json_bytes(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _stream_source(path: Path, *, max_line_bytes: int):
    opener = gzip.open if path.suffix == ".gz" else bz2.open if path.suffix == ".bz2" else open
    with opener(path, "rb") as stream:
        while True:
            line = stream.readline(max_line_bytes + 1)
            if not line:
                return
            if len(line) > max_line_bytes:
                raise LexemeError("source entity exceeds max_line_bytes")
            try:
                yield line.decode("utf-8").strip()
            except UnicodeError as exc:
                raise LexemeError("non UTF-8 source") from exc


def _text_entries(mapping: Any, *, registry: Registry | None, stats: Counter, maximum: int) -> list[dict[str, Any]]:
    if not isinstance(mapping, dict):
        raise LexemeError("lexical text map must be an object")
    rows = []
    for locale in sorted(mapping):
        value = mapping[locale]
        if not isinstance(locale, str) or not LOCALE.fullmatch(locale):
            raise LexemeError("invalid lexical text locale syntax")
        if not isinstance(value, dict) or value.get("language", locale).lower() != locale.lower():
            raise LexemeError("lexical text language disagrees with key")
        text = value.get("value")
        if not isinstance(text, str) or not text or len(text) > maximum or "\x00" in text:
            raise LexemeError("invalid lexical text value")
        tag = check_tag(locale, registry) if registry else {"tag": locale, "valid": None, "status": "iana_not_checked"}
        rows.append({"locale": locale, "value": text, "tag_status": tag.get("status", "invalid"),
                     "iana_valid": tag.get("valid")})
        stats[locale] += 1
    return rows


def _qid(obj: Any, *, field: str) -> str:
    if not isinstance(obj, str) or not QID.fullmatch(obj):
        raise LexemeError(f"invalid {field} Wikidata Q identifier")
    return obj


def _project(entity: dict[str, Any], registry: Registry | None, counts: dict[str, Counter]) -> dict:
    lid = entity.get("id")
    if not isinstance(lid, str) or not LID.fullmatch(lid):
        raise LexemeError("invalid lexeme ID")
    language = _qid(entity.get("language"), field="language")
    category = _qid(entity.get("lexicalCategory"), field="lexicalCategory")
    lemmas = _text_entries(entity.get("lemmas", {}), registry=registry, stats=counts["lemmas"], maximum=10000)
    forms = []
    senses = []
    for form in entity.get("forms", []):
        if not isinstance(form, dict) or not FID.fullmatch(str(form.get("id", ""))) or not form["id"].startswith(lid + "-"):
            raise LexemeError("form must have an L-F ID belonging to its lexeme")
        features = form.get("grammaticalFeatures", [])
        if not isinstance(features, list) or any(not isinstance(f, str) or not QID.fullmatch(f) for f in features) or len(set(features)) != len(features):
            raise LexemeError("invalid grammatical feature Q IDs")
        forms.append({"id": form["id"], "representations": _text_entries(form.get("representations", {}), registry=registry, stats=counts["forms"], maximum=10000),
                      "grammatical_features": sorted(features)})
    for sense in entity.get("senses", []):
        if not isinstance(sense, dict) or not SID.fullmatch(str(sense.get("id", ""))) or not sense["id"].startswith(lid + "-"):
            raise LexemeError("sense must have an L-S ID belonging to its lexeme")
        senses.append({"id": sense["id"], "glosses": _text_entries(sense.get("glosses", {}), registry=registry, stats=counts["glosses"], maximum=30000)})
    if len({f["id"] for f in forms}) != len(forms) or len({s["id"] for s in senses}) != len(senses):
        raise LexemeError("duplicate form or sense ID")
    return {"external_lexeme_id": lid, "external_language_item": language,
            "external_lexical_category_item": category,
            "lemmas": lemmas, "forms": forms, "senses": senses,
            "status": "observation_only", "kristal_identity": None,
            "gf_mapping_status": "unmapped", "translation_status": "not_reviewed"}


def import_lexeme_observations(*, dump: Path, output_dir: Path, snapshot: str,
                               iana_registry: Path | None = None, expected_sha256: str | None = None,
                               max_records: int = 5_000_000,
                               max_line_bytes: int = 16 * 1024 * 1024) -> dict[str, Any]:
    if not NAME.fullmatch(snapshot) or snapshot in {".", ".."}:
        raise LexemeError("invalid snapshot name")
    if not 1 <= max_records <= 100_000_000 or not 1024 <= max_line_bytes <= 256 * 1024 * 1024:
        raise LexemeError("invalid resource bounds")
    dump = Path(dump)
    if not dump.is_file():
        raise FileNotFoundError(dump)
    digest = sha256_file(dump)
    if expected_sha256 is not None and (not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256) or expected_sha256.lower() != digest):
        raise LexemeError("source SHA-256 does not match supplied expected digest")
    registry = load_registry(iana_registry) if iana_registry is not None else None
    out = Path(output_dir)
    if out.exists() or out.is_symlink():
        raise FileExistsError("output directory exists; observations are immutable")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".dik-lexemes-", dir=str(out.parent)) as stage_name:
        stage = Path(stage_name)
        db = sqlite3.connect(str(stage / "seen.sqlite"))
        db.execute("CREATE TABLE known (id TEXT PRIMARY KEY)")
        counts = {"lemmas": Counter(), "forms": Counter(), "glosses": Counter()}
        observations = 0
        forms_count = 0
        senses_count = 0
        scanned = 0
        mode = "unknown"
        data = stage / "lexemes.jsonl"
        try:
            with data.open("wb") as sink:
                for line in _stream_source(dump, max_line_bytes=max_line_bytes):
                    if not line:
                        continue
                    if mode == "closed":
                        raise LexemeError("trailing data after JSON array")
                    if line == "[":
                        if mode != "unknown":
                            raise LexemeError("unexpected array open")
                        mode = "array"
                        continue
                    if line == "]":
                        if mode != "array":
                            raise LexemeError("unexpected array close")
                        mode = "closed"
                        continue
                    if mode == "unknown":
                        mode = "jsonl"
                    if mode == "array" and line.endswith(","):
                        line = line[:-1].rstrip()
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise LexemeError("requires one Wikidata entity per physical line") from exc
                    if not isinstance(obj, dict):
                        raise LexemeError("Wikidata entity must be a JSON object")
                    scanned += 1
                    if scanned > max_records:
                        raise LexemeError("resource limit reached: no truncated snapshot published")
                    # A full entities dump also contains Q/P. Ignore those completely.
                    if not LID.fullmatch(str(obj.get("id", ""))):
                        if obj.get("type") == "lexeme":
                            raise LexemeError("malformed lexeme entity ID")
                        continue
                    if obj.get("type") not in (None, "lexeme"):
                        raise LexemeError("L ID with incompatible entity type")
                    try:
                        db.execute("INSERT INTO known(id) VALUES (?)", (obj["id"],))
                    except sqlite3.IntegrityError as exc:
                        raise LexemeError("duplicate lexeme ID") from exc
                    rec = _project(obj, registry, counts)
                    sink.write(_json_bytes(rec))
                    observations += 1
                    forms_count += len(rec["forms"])
                    senses_count += len(rec["senses"])
            if mode == "array":
                raise LexemeError("unclosed JSON array")
        finally:
            db.close()
        (stage / "seen.sqlite").unlink()
        by_locale = {name: dict(sorted(counter.items())) for name, counter in counts.items()}
        stats = stage / "locale-stats.json"
        stats.write_text(json.dumps({"profile": "dik.wikidata-lexeme-locale-stats/0.1-candidate",
                                    "counts": by_locale, "published_dictionaries": 0},
                                   ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        manifest = {
            "profile": PROFILE, "snapshot": snapshot, "source_kind": "wikidata-lexemes",
            "purpose": "observation_only", "source_sha256": digest,
            "source_sha256_expected_by_operator": expected_sha256 is not None,
            "iana_registry_sha256": registry.sha256 if registry else None,
            "iana_registry_file_date": registry.file_date if registry else None,
            "observations_file": "lexemes.jsonl", "observations_sha256": sha256_file(data),
            "stats_file": "locale-stats.json", "stats_sha256": sha256_file(stats),
            "scanned_entities": scanned, "lexemes": observations,
            "forms": forms_count, "senses": senses_count,
            "published_dictionaries": 0, "approved_kristal_crosswalks": 0,
            "import_fidelity": "lemmas_forms_features_sense_glosses_only",
            "not_imported": "claims, references, qualifiers, provenance per statement, GF functions",
            "license_claim": "wikidata_structured_data_CC0_per_source_policy; user_verification_required",
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        stage.rename(out)
    return {**manifest, "output": str(out)}


def audit_lexeme_observations(path: Path) -> dict[str, Any]:
    base = Path(path)
    if base.is_symlink():
        raise LexemeError("symlinked output directory not trusted")
    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("profile") != PROFILE or manifest.get("purpose") != "observation_only" or manifest.get("published_dictionaries") != 0 or manifest.get("approved_kristal_crosswalks") != 0:
        raise LexemeError("invalid observation manifest")
    for file_key, sha_key, expected in (("observations_file", "observations_sha256", "lexemes.jsonl"),
                                        ("stats_file", "stats_sha256", "locale-stats.json")):
        if manifest.get(file_key) != expected:
            raise LexemeError("unknown filename in observation manifest")
        f = base / expected
        if f.is_symlink() or sha256_file(f) != manifest.get(sha_key):
            raise LexemeError("observation output hash mismatch")
    count = forms = senses = 0
    with (base / "lexemes.jsonl").open("rb") as src:
        for line in src:
            rec = json.loads(line)
            if _json_bytes(rec) != line or rec.get("status") != "observation_only" or rec.get("kristal_identity") is not None or rec.get("translation_status") != "not_reviewed":
                raise LexemeError("invalid lexical observation")
            if not LID.fullmatch(rec["external_lexeme_id"]):
                raise LexemeError("invalid LID in observation")
            count += 1
            forms += len(rec["forms"])
            senses += len(rec["senses"])
    if (count, forms, senses) != (manifest["lexemes"], manifest["forms"], manifest["senses"]):
        raise LexemeError("lexeme/form/sense counts do not match")
    return {"valid": True, "snapshot": manifest["snapshot"], "lexemes": count,
            "forms": forms, "senses": senses, "published_dictionaries": 0,
            "reviewed_translations": 0, "approved_kristal_crosswalks": 0}
