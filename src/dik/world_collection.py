"""Sparse world dictionary *slots*, not empty fake dictionaries.

Every ISO 639-3 candidate has a discoverable placeholder. No slots imply that
BCP 47 normalization, language resources, translations, or GF mappings exist.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import tempfile
from typing import Any

from .world_languages import inspect_language_candidates
from .world_reconciliation import sha256_file

PROFILE = "dik.world-dictionary-slots/0.1-candidate"


def _json_line(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def build_collection_slots(*, index: Path, language_manifest: Path, output_dir: Path) -> dict[str, Any]:
    report = inspect_language_candidates(index, language_manifest)
    out = Path(output_dir)
    if out.exists() or out.is_symlink():
        raise FileExistsError("collection slots already exist; no overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    rows = 0
    with tempfile.TemporaryDirectory(prefix=".dik-world-slots-", dir=str(out.parent)) as stage_name:
        stage = Path(stage_name)
        output = stage / 'slots.jsonl'
        with Path(index).open('r', encoding='utf-8') as source, output.open('wb') as dest:
            for line in source:
                candidate = json.loads(line)
                obj = {
                    'iso6393': candidate['alpha3'],
                    'iso6391_candidate': candidate.get('alpha2'),
                    'name_en': candidate['name_en'],
                    'language_type': candidate['type_code'],
                    'language_scope': candidate['scope_code'],
                    'tag_candidates': [candidate.get('alpha2') or candidate['alpha3']],
                    'iana_status': 'not_checked',
                    'source_links': [],
                    'wikidata_lexeme_observations': 0,
                    'verified_lexical_entries': 0,
                    'published_dictionary_shards': 0,
                    'crosswalk_status': 'none',
                    'gf_status': 'not_mapped',
                    'status': 'empty_candidate_slot'
                }
                dest.write(_json_line(obj))
                counts[obj['language_type']] += 1
                rows += 1
        manifest = {
            'profile': PROFILE, 'purpose': 'discovery_only',
            'source_index_sha256': sha256_file(index),
            'source_manifest_sha256': sha256_file(language_manifest),
            'slots_file': 'slots.jsonl', 'slots_sha256': sha256_file(output),
            'slot_count': rows, 'type_counts': dict(sorted(counts.items())),
            'bcp47_validated_slots': 0, 'dictionaries_published': 0,
            'actual_lexical_entries': 0,
        }
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2)+'\n',encoding='utf-8')
        stage.rename(out)
    assert rows == report['language_code_candidates']
    return {**manifest, 'output': str(out)}


def audit_collection_slots(path: Path) -> dict[str, Any]:
    path = Path(path)
    if path.is_symlink():
        raise ValueError('untrusted collection slots directory')
    manifest = json.loads((path/'manifest.json').read_text(encoding='utf-8'))
    if (manifest.get('profile') != PROFILE or manifest.get('purpose') != 'discovery_only'
        or manifest.get('slots_file') != 'slots.jsonl' or manifest.get('bcp47_validated_slots') != 0
        or manifest.get('dictionaries_published') != 0 or manifest.get('actual_lexical_entries') != 0):
        raise ValueError('invalid collection slots manifest')
    file = path/'slots.jsonl'
    if file.is_symlink() or sha256_file(file) != manifest['slots_sha256']:
        raise ValueError('world collection slots hash mismatch')
    prev = ''
    count = 0
    types: Counter[str] = Counter()
    with file.open('rb') as stream:
        for line in stream:
            row = json.loads(line)
            if _json_line(row) != line or row['iso6393'] <= prev:
                raise ValueError('unsorted or noncanonical world slot')
            prev = row['iso6393']
            if (row.get('status') != 'empty_candidate_slot' or row.get('iana_status') != 'not_checked'
                or row.get('source_links') != [] or row.get('crosswalk_status') != 'none'
                or row.get('gf_status') != 'not_mapped' or row.get('verified_lexical_entries') != 0
                or row.get('wikidata_lexeme_observations') != 0 or row.get('published_dictionary_shards') != 0):
                raise ValueError('slot falsely claims published lexical coverage')
            count += 1
            types[row['language_type']] += 1
    if count != manifest['slot_count'] or dict(sorted(types.items())) != manifest['type_counts']:
        raise ValueError('world collection slot totals mismatch')
    return {'valid': True, 'candidate_slots': count, 'types': dict(sorted(types.items())),
            'actual_dictionaries': 0, 'lexical_entries': 0, 'status': 'discovery_only'}
