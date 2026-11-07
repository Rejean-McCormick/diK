"""Explicit, offline, knowledge-only SemantiK projection of diK GF candidates.

This is NOT a semantic crosswalk, GF mapping, runtime lexicon activation or
human approval. Wikidata Lexeme identity is preserved in a separate namespace.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .gf_handoff import audit_gf_handoff

PROFILE = "dik.semantik-knowledge-handoff/1.0-candidate"
LID = re.compile(r"L[1-9][0-9]*\Z")
LOCALE = re.compile(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*\Z")


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object')
    return value


def _rows(handoff: Path, *, limit: int) -> tuple[dict, list[dict]]:
    audit_gf_handoff(handoff)
    manifest = _json(handoff / 'manifest.json')
    locale = manifest['locale']
    if not LOCALE.fullmatch(locale):
        raise ValueError('Invalid locale in diK handoff')
    rows = []
    seen = set()
    with (handoff / 'candidates.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            source_id = row['source_lexeme_id']
            if not LID.fullmatch(source_id) or row.get('locale') != locale or source_id in seen:
                raise ValueError('Invalid or duplicate lexeme identity')
            seen.add(source_id)
            if len(seen) > limit:
                raise ValueError('Lexeme export limit exceeded; no partial output generated')
            if not isinstance(row.get('lemmas'), list) or not all(isinstance(v, str) and v for v in row['lemmas']):
                raise ValueError('Invalid lemma candidates')
            rows.append(row)
    return manifest, sorted(rows, key=lambda r: int(r['source_lexeme_id'][1:]))


def build_semantik_knowledge_candidate(*, handoff_dir: Path, output_dir: Path, max_entries: int = 50000) -> dict[str, Any]:
    """Project observed L IDs into *knowledge only* lexical artifact schema 1.1.

    A caller must separately decide semantic identity/sense and approve any GF
    mapping. The output is an unqualified review input and never a RuntimeSet.
    """
    if not 1 <= max_entries <= 2_000_000:
        raise ValueError('Invalid max_entries')
    handoff = Path(handoff_dir)
    if handoff.is_symlink():
        raise ValueError('Symlink handoff rejected')
    manifest, rows = _rows(handoff, limit=max_entries)
    target = Path(output_dir)
    if target.exists() or target.is_symlink():
        raise FileExistsError('Candidate output already exists; no overwrite')
    target.parent.mkdir(parents=True, exist_ok=True)
    upstream_hash = manifest['candidates_sha256']
    locale = manifest['locale'].lower()
    entries = []
    for r in rows:
        lid = r['source_lexeme_id']
        entries.append({
            'semantic_ref': f'wikidata:lexeme:{lid}',
            'language': locale,
            'lexical_ref': lid,
            'binding_kind': 'lexeme_ref',
            'source_kind': 'wikidata',
            'use_for': 'knowledge',
            'source_ref': f'wikidata:lexeme:{lid}',
            'properties': {
                'status': 'candidate_observation_only',
                'source_lexeme_id': lid,
                'lemmas_observed': r['lemmas'],
                'wikidata_language_qid_unmapped': r['source_language_item'],
                'wikidata_category_qid_unmapped': r['source_category_item'],
                'unmapped_forms': r['form_observations'],
                'review_required': ['semantic_identity', 'sense', 'grammatical_category', 'gf_mapping', 'licensing'],
            },
        })
    lexicon = {'schema_version': '1.1',
               'lexicon_id': 'dik-observations-' + upstream_hash[:16] + '-' + locale,
               'source_kind': 'wikidata',
               'source_ref': 'dik:gf-handoff:sha256:' + upstream_hash,
               'entries': entries}
    template = {
        'schema_id': 'dik.gf-human-mapping-decisions', 'schema_version': '1.0',
        'status': 'UNREVIEWED_TEMPLATE', 'locale': locale,
        'source_candidate_sha256': upstream_hash,
        'decisions': [{
            'source_lexeme_id': r['source_lexeme_id'],
            'semantic_ref': f'wikidata:lexeme:{r["source_lexeme_id"]}',
            'gf_function': None, 'gf_category': None, 'reviewer': None,
            'target_semantic_ref': None, 'semantic_authority_ref': None,
            'semantic_identity_reviewed': False,
            'license_reviewed': False, 'mapping_reviewed': False,
            'decision': 'pending'
        } for r in rows],
    }
    with tempfile.TemporaryDirectory(prefix='.dik-sem-k-', dir=str(target.parent)) as temp:
        stage = Path(temp)
        for name, body in (('semantik.knowledge.json', lexicon), ('gf-mapping-review.template.json', template)):
            (stage/name).write_text(json.dumps(body, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        result = {
            'schema_id': PROFILE, 'status': 'CANDIDATE_ONLY', 'released': False,
            'lexicon_sha256': _hash(stage/'semantik.knowledge.json'),
            'review_template_sha256': _hash(stage/'gf-mapping-review.template.json'),
            'source_candidate_sha256': upstream_hash,
            'source_manifest_sha256': _hash(handoff/'manifest.json'),
            'locale': locale, 'entries': len(entries), 'gf_bindings': 0,
            'files': ['semantik.knowledge.json', 'gf-mapping-review.template.json'],
        }
        (stage/'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        stage.rename(target)
    return {**result, 'output': str(target)}


def audit_semantik_knowledge_candidate(bundle_dir: Path) -> dict[str, Any]:
    directory = Path(bundle_dir)
    if directory.is_symlink():
        raise ValueError('Symlink bundle rejected')
    manifest = _json(directory/'manifest.json')
    if (manifest.get('schema_id') != PROFILE or manifest.get('status') != 'CANDIDATE_ONLY'
            or manifest.get('released') is not False or manifest.get('gf_bindings') != 0):
        raise ValueError('Invalid diK-SemantiK candidate manifest')
    for name, key in (('semantik.knowledge.json', 'lexicon_sha256'), ('gf-mapping-review.template.json', 'review_template_sha256')):
        file = directory/name
        if file.is_symlink() or _hash(file) != manifest[key]:
            raise ValueError('diK candidate checksum mismatch: ' + name)
    lexicon = _json(directory/'semantik.knowledge.json')
    template = _json(directory/'gf-mapping-review.template.json')
    if (lexicon.get('schema_version') != '1.1' or lexicon.get('source_kind') != 'wikidata'
            or not isinstance(lexicon.get('entries'), list)
            or len(lexicon['entries']) != manifest['entries']
            or template.get('source_candidate_sha256') != manifest['source_candidate_sha256']
            or len(template.get('decisions', [])) != manifest['entries']):
        raise ValueError('Candidate data identity/count mismatch')
    ids = set()
    for row, decision in zip(lexicon['entries'], template['decisions']):
        lid = row.get('lexical_ref')
        if (not isinstance(lid, str) or not LID.fullmatch(lid) or lid in ids
                or row.get('semantic_ref') != 'wikidata:lexeme:' + lid
                or row.get('use_for') != 'knowledge' or row.get('binding_kind') != 'lexeme_ref'
                or row.get('source_kind') != 'wikidata' or row.get('language') != manifest['locale']
                or decision.get('source_lexeme_id') != lid or decision.get('decision') != 'pending'
                or decision.get('gf_function') is not None or decision.get('mapping_reviewed') is not False):
            raise ValueError('Knowledge-only candidate was changed or elevated')
        ids.add(lid)
    return {'valid': True, 'status': 'CANDIDATE_ONLY', 'entries': len(ids), 'gf_bindings': 0, 'released': False,
            'locale': manifest['locale'], 'lexicon_sha256': manifest['lexicon_sha256']}
