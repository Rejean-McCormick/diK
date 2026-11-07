"""Offline IANA Language Subtag Registry parser and conservative RFC 5646 checker.

The caller supplies an authentic, versioned *local* IANA text registry. A file
hash proves local integrity, not independent authenticity. This module does not
edit Framework dictionaries or generate translations.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
import hashlib
from pathlib import Path
import re
from typing import Any

ALNUM = re.compile(r"^[A-Za-z0-9]+$")
LANG = re.compile(r"^[A-Za-z]{2,8}$")
EXTLANG = re.compile(r"^[A-Za-z]{3}$")
SCRIPT = re.compile(r"^[A-Za-z]{4}$")
REGION = re.compile(r"^(?:[A-Za-z]{2}|[0-9]{3})$")
VARIANT = re.compile(r"^(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3})$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TYPES = {"language", "extlang", "script", "region", "variant", "grandfathered", "redundant"}
REPEATABLE = {"Description", "Prefix", "Comments"}


class RegistryError(ValueError):
    """Reject incomplete, unpinned or malformed registries/tags."""


@dataclass(frozen=True)
class Registry:
    file_date: str
    sha256: str
    entries: dict[str, dict[str, dict[str, Any]]]

    def get(self, kind: str, code: str) -> dict[str, Any] | None:
        return self.entries.get(kind, {}).get(code.lower())

    def summary(self) -> dict[str, Any]:
        return {"profile": "dik.iana-language-registry/0.1-candidate",
                "file_date": self.file_date, "file_sha256": self.sha256,
                "subtags_by_type": {kind: len(self.entries[kind]) for kind in sorted(self.entries)},
                "data_source": "operator_supplied_local_file", "authority_verified": False,
                "note": "SHA-256 verifies these local bytes, not provenance from IANA."}


def _parse_record(lines: list[str]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for line in lines:
        if line.startswith(" "):
            if not record:
                raise RegistryError("orphan folded field")
            last = next(reversed(record))
            old = record[last]
            if isinstance(old, list):
                old[-1] += " " + line.strip()
            else:
                record[last] = old + " " + line.strip()
            continue
        if ":" not in line:
            raise RegistryError("malformed registry field")
        key, value = line.split(":", 1)
        value = value.strip()
        if not key or not value:
            raise RegistryError("empty registry field")
        if key in record:
            if key not in REPEATABLE:
                raise RegistryError(f"duplicate singular registry field: {key}")
            if not isinstance(record[key], list):
                record[key] = [record[key]]
            record[key].append(value)
        else:
            record[key] = value
    kind = record.get("Type", "").lower()
    if kind not in TYPES:
        raise RegistryError(f"unsupported registry type: {kind}")
    key = "Tag" if kind in {"grandfathered", "redundant"} else "Subtag"
    if key not in record or not isinstance(record[key], str):
        raise RegistryError(f"missing {key} for {kind}")
    if "Description" not in record or "Added" not in record:
        raise RegistryError("missing Description or Added")
    for day in ("Added", "Deprecated"):
        if day in record:
            if not isinstance(record[day], str) or not DATE.fullmatch(record[day]):
                raise RegistryError(f"invalid {day}")
            date.fromisoformat(record[day])
    for k in REPEATABLE:
        if k in record and isinstance(record[k], str):
            record[k] = [record[k]]
    return record


def load_registry(path: Path, *, max_bytes: int = 25_000_000) -> Registry:
    """Read official RFC 5646 TXT format from local disk; no networking."""
    path = Path(path)
    if not 128 <= max_bytes <= 100_000_000:
        raise RegistryError("invalid byte limit")
    if path.stat().st_size > max_bytes:
        raise RegistryError("registry exceeds byte limit")
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise RegistryError("registry exceeds byte limit")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RegistryError("unexpected BOM")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RegistryError("registry is not UTF-8") from exc
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise RegistryError("invalid line ending")
    blocks = [x for x in text.split("\n%%\n") if x.strip()]
    if len(blocks) < 2:
        raise RegistryError("missing IANA record separators")
    header = blocks.pop(0).strip()
    if not header.startswith("File-Date: ") or "\n" in header:
        raise RegistryError("missing File-Date header")
    file_date = header.removeprefix("File-Date: ")
    if not DATE.fullmatch(file_date):
        raise RegistryError("invalid File-Date")
    date.fromisoformat(file_date)
    entries: dict[str, dict[str, dict[str, Any]]] = {t: {} for t in TYPES}
    for block in blocks:
        rec = _parse_record(block.strip().splitlines())
        kind = rec["Type"].lower()
        key_name = "Tag" if kind in {"grandfathered", "redundant"} else "Subtag"
        key = rec[key_name].lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key):
            raise RegistryError("invalid subtag characters")
        if key in entries[kind]:
            raise RegistryError(f"duplicate registry entry: {kind}/{key}")
        entries[kind][key] = rec
    return Registry(file_date, hashlib.sha256(raw).hexdigest(), entries)


def _checked(kind: str, code: str, registry: Registry, notes: list[str]) -> bool:
    record = registry.get(kind, code)
    if record is None:
        notes.append("unregistered:" + kind + ":" + code)
        return False
    if "Deprecated" in record:
        suffix = ":preferred=" + str(record["Preferred-Value"]) if "Preferred-Value" in record else ""
        notes.append("deprecated:" + kind + ":" + code + suffix)
    return True


def check_tag(tag: str, registry: Registry) -> dict[str, Any]:
    """Conservative tag validation, explicitly not CLDR alias canonicalization.

    Return recognized / rejected; never synthesize replacements or translations.
    """
    if not isinstance(tag, str) or not tag or len(tag) > 255 or "_" in tag:
        return {"tag": tag, "valid": False, "reason": "invalid_syntax"}
    norm = tag.lower()
    for kind in ("grandfathered", "redundant"):
        rec = registry.get(kind, norm)
        if rec:
            notes: list[str] = []
            _checked(kind, norm, registry, notes)
            return {"tag": tag, "valid": True, "status": "registered_tag",
                    "normalized_case": rec["Tag"], "notes": notes,
                    "registry_date": registry.file_date}
    parts = tag.split("-")
    if any(not 1 <= len(x) <= 8 or not ALNUM.fullmatch(x) for x in parts):
        return {"tag": tag, "valid": False, "reason": "invalid_syntax"}
    if norm.startswith("x-") and len(parts) >= 2:
        return {"tag": tag, "valid": True, "status": "private_use",
                "normalized_case": norm, "notes": ["not_registered_language"],
                "registry_date": registry.file_date}
    if not LANG.fullmatch(parts[0]):
        return {"tag": tag, "valid": False, "reason": "invalid_language"}
    notes: list[str] = []
    valid = _checked("language", parts[0], registry, notes)
    canonical = [parts[0].lower()]
    i = 1
    base = [parts[0].lower()]
    if len(parts[0]) in (2, 3):
        extcount = 0
        while i < len(parts) and EXTLANG.fullmatch(parts[i]) and extcount < 3:
            ext = parts[i].lower()
            ok = _checked("extlang", ext, registry, notes)
            valid &= ok
            rec = registry.get("extlang", ext)
            if rec and "Prefix" in rec and not any("-".join(base).startswith(x.lower()) for x in rec["Prefix"]):
                valid = False
                notes.append("invalid_extlang_prefix:" + ext)
            base.append(ext)
            canonical.append(ext)
            i += 1
            extcount += 1
    if i < len(parts) and SCRIPT.fullmatch(parts[i]):
        valid &= _checked("script", parts[i], registry, notes)
        canonical.append(parts[i].title())
        base.append(parts[i].lower())
        i += 1
    if i < len(parts) and REGION.fullmatch(parts[i]):
        valid &= _checked("region", parts[i], registry, notes)
        canonical.append(parts[i].upper())
        base.append(parts[i].lower())
        i += 1
    variants: set[str] = set()
    while i < len(parts) and VARIANT.fullmatch(parts[i]):
        v = parts[i].lower()
        if v in variants:
            return {"tag": tag, "valid": False, "reason": "duplicate_variant"}
        variants.add(v)
        valid &= _checked("variant", v, registry, notes)
        rec = registry.get("variant", v)
        if rec and "Prefix" in rec:
            prior = "-".join(base)
            if not any(prior == pre.lower() or prior.startswith(pre.lower() + "-") for pre in rec["Prefix"]):
                valid = False
                notes.append("invalid_variant_prefix:" + v)
        canonical.append(v)
        base.append(v)
        i += 1
    singles: set[str] = set()
    while i < len(parts) and len(parts[i]) == 1 and parts[i].lower() != "x":
        singleton = parts[i].lower()
        if singleton in singles:
            return {"tag": tag, "valid": False, "reason": "duplicate_extension"}
        singles.add(singleton)
        canonical.append(singleton)
        i += 1
        n = 0
        while i < len(parts) and 2 <= len(parts[i]) <= 8:
            canonical.append(parts[i].lower())
            i += 1
            n += 1
        if not n:
            return {"tag": tag, "valid": False, "reason": "empty_extension"}
    if i < len(parts) and parts[i].lower() == "x":
        canonical.append("x")
        i += 1
        if i == len(parts):
            return {"tag": tag, "valid": False, "reason": "empty_private_use"}
        canonical.extend(x.lower() for x in parts[i:])
        i = len(parts)
    if i != len(parts):
        return {"tag": tag, "valid": False, "reason": "unexpected_subtag"}
    return {"tag": tag, "valid": bool(valid),
            "status": "registered_components" if valid else "unregistered_components",
            "normalized_case": "-".join(canonical), "notes": notes,
            "registry_date": registry.file_date}
