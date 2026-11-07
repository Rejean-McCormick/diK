"""Read-only GF/SemantiK *candidate* handoff from Wikidata L/S/F observations.

Never create GF functions, synthesize inflections or turn Wikidata Q IDs into
Kristal KQ/KP identifiers. The resulting files need explicit human/linguistic
mapping and license review before any grammatical or lexical publication.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import tempfile
from typing import Any

from .wikidata_lexemes import audit_lexeme_observations
from .world_reconciliation import sha256_file

PROFILE = "dik.gf-lexical-handoff/0.1-candidate"


def build_gf_handoff(*, observations_dir: Path, output_dir: Path, locale: str) -> dict[str, Any]:
    audit_lexeme_observations(observations_dir)
    if not isinstance(locale, str) or not locale or len(locale) > 64:
        raise ValueError("locale required")
    out = Path(output_dir)
    if out.exists() or out.is_symlink():
        raise FileExistsError("GF candidate output exists")
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = Counter()
    with tempfile.TemporaryDirectory(prefix=".dik-gf-", dir=str(out.parent)) as stage_name:
        stage = Path(stage_name)
        output = stage / "candidates.jsonl"
        with (Path(observations_dir) / "lexemes.jsonl").open("r", encoding="utf-8") as src, output.open("wb") as dst:
            for line in src:
                item = json.loads(line)
                lemmas = [x for x in item["lemmas"] if x["locale"].lower() == locale.lower()]
                forms = []
                for form in item["forms"]:
                    reps = [r for r in form["representations"] if r["locale"].lower() == locale.lower()]
                    if reps:
                        forms.append({"source_form_id": form["id"], "representations": [r["value"] for r in reps],
                                      "unmapped_grammatical_qids": form["grammatical_features"]})
                if not lemmas and not forms:
                    continue
                row = {"source_lexeme_id": item["external_lexeme_id"], "locale": locale,
                       "source_language_item": item["external_language_item"],
                       "source_category_item": item["external_lexical_category_item"],
                       "lemmas": [l["value"] for l in lemmas], "form_observations": forms,
                       "gf_function": None, "gf_category": None, "gf_paradigm": None,
                       "status": "needs_explicit_gf_mapping", "approved_kristal_link": None}
                dst.write((json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
                summary["candidate_lexemes"] += 1
                summary["candidate_forms"] += len(forms)
        manifest = {"profile": PROFILE, "purpose": "candidate_only", "locale": locale,
                    "source_lexeme_sha256": sha256_file(Path(observations_dir) / "lexemes.jsonl"),
                    "candidates_sha256": sha256_file(output), "candidates_file": "candidates.jsonl",
                    "candidate_lexemes": summary["candidate_lexemes"],
                    "candidate_forms": summary["candidate_forms"],
                    "gf_functions_created": 0, "verified_dictionaries": 0,
                    "requires": ["review_of_semantic_identity", "grammatical_feature_mapping", "GF_function_and_paradigm", "licensing_check"]}
        (stage / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        stage.rename(out)
    return {**manifest, "output": str(out)}


def audit_gf_handoff(path: Path) -> dict[str, Any]:
    base = Path(path)
    if base.is_symlink():
        raise ValueError("untrusted GF candidate directory")
    doc = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    if doc.get("profile") != PROFILE or doc.get("purpose") != "candidate_only" or doc.get("candidates_file") != "candidates.jsonl" or doc.get("gf_functions_created") != 0 or doc.get("verified_dictionaries") != 0:
        raise ValueError("invalid GF candidate manifest")
    file = base / "candidates.jsonl"
    if file.is_symlink() or sha256_file(file) != doc["candidates_sha256"]:
        raise ValueError("GF candidate checksum mismatch")
    lexemes = forms = 0
    with file.open("r", encoding="utf-8") as src:
        for line in src:
            row = json.loads(line)
            if row.get("gf_function") is not None or row.get("gf_paradigm") is not None or row.get("approved_kristal_link") is not None or row.get("status") != "needs_explicit_gf_mapping":
                raise ValueError("unexpected claimed mapping in GF handoff")
            lexemes += 1
            forms += len(row["form_observations"])
    if (lexemes, forms) != (doc["candidate_lexemes"], doc["candidate_forms"]):
        raise ValueError("GF candidate counts mismatch")
    return {"valid": True, "candidate_lexemes": lexemes, "candidate_forms": forms, "gf_functions_created": 0}
