"""Review-only impact analysis for Wikidata identity changes.

Input is a diK *normalized observation* JSONL, NOT an official Wikidata
redirect dump/delta. Operators must retain the underlying upstream evidence.
Every KQ/KP and accepted crosswalk remains unchanged. No write operation can
adopt a redirect, merge, split, or retire an identity.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re

from ._framework import dictionaries as fw
from .operations import DiKError

_IDENTIFIER = re.compile(r'^[QP][1-9][0-9]*$')
_DIGEST = re.compile(r'^[0-9a-f]{64}$')
_SCHEMA = Path(__file__).parent / 'contracts' / 'dik-wikidata-evolution-event.schema.json'
MAX_CHAIN = 2048


def _check_event(obj, validator):
    # Use a strict schema rather than forgiving/remapping external input.
    errors = list(validator.iter_errors(obj))
    if errors:
        raise DiKError('INVALID_EVOLUTION_EVENT: ' + errors[0].message)
    source, targets = obj['source_id'], obj['targets']
    if any(target[0] != source[0] for target in targets):
        raise DiKError('IDENTITY_KIND_MISMATCH: Wikidata Q/P families cannot mix')
    if source in targets:
        raise DiKError('REDIRECT_CYCLE: self-reference')
    if len(set(targets)) != len(targets):
        raise DiKError('DUPLICATE_TARGET')


def _read_events(source: Path, snapshot: str, max_records: int):
    if max_records < 1 or max_records > 10_000_000:
        raise DiKError('INVALID_MAX_RECORDS')
    if not source.is_file():
        raise DiKError('SOURCE_NOT_FOUND')
    schema = json.loads(_SCHEMA.read_text(encoding='utf-8'))
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(schema)
    mapping = {}
    digest = hashlib.sha256()
    with source.open('rb') as handle:
        line_no = 0
        while True:
            line = handle.readline(256 * 1024 + 1)
            if not line:
                break
            line_no += 1
            if len(line) > 256 * 1024:
                raise DiKError(f'RECORD_TOO_LARGE: line {line_no}')
            digest.update(line)
            if not line.strip():
                continue
            if len(mapping) >= max_records:
                raise DiKError('RESOURCE_LIMIT: too many normalized evolution records')
            try:
                item = json.loads(line)
            except (ValueError, UnicodeError) as exc:
                raise DiKError(f'INVALID_EVOLUTION_JSONL: line {line_no}') from exc
            _check_event(item, validator)
            if item['source_snapshot'] != snapshot:
                raise DiKError(f'SNAPSHOT_MISMATCH: line {line_no}')
            if item['source_id'] in mapping:
                raise DiKError(f'DUPLICATE_EVOLUTION_EVENT: {item["source_id"]}')
            mapping[item['source_id']] = item
    return mapping, digest.hexdigest()


def _resolve(start: str, events: dict) -> dict:
    current = start
    path = [start]
    seen = {start}
    references = []
    for _ in range(MAX_CHAIN):
        event = events.get(current)
        if event is None:
            return {'kind': 'terminal', 'terminal_id': current, 'path': path,
                    'evidence_references': references}
        references.append({'source_id': current, 'source_reference': event['source_reference']})
        kind = event['event_type']
        if kind == 'retired':
            return {'kind': 'retired', 'path': path, 'evidence_references': references}
        if kind == 'split_candidate':
            return {'kind': 'split_candidate', 'candidates': event['targets'],
                    'path': path, 'evidence_references': references}
        dest = event['targets'][0]
        if dest in seen:
            raise DiKError('REDIRECT_CYCLE: ' + ' -> '.join(path + [dest]))
        seen.add(dest)
        path.append(dest)
        current = dest
    raise DiKError('RESOURCE_LIMIT: redirect chain is too long')


def _validate_graph(events: dict) -> None:
    """Reject cycles even if currently unmapped (prevents latent unsafe imports)."""
    checked = set()
    for start in events:
        if start in checked:
            continue
        path, active = [], set()
        node = start
        while node in events and node not in checked:
            if node in active:
                raise DiKError('REDIRECT_CYCLE: ' + ' -> '.join(path + [node]))
            active.add(node)
            path.append(node)
            item = events[node]
            if item['event_type'] != 'redirect':
                break
            node = item['targets'][0]
            if len(path) > MAX_CHAIN:
                raise DiKError('RESOURCE_LIMIT: redirect chain is too long')
        checked.update(path)


def _read_crosswalk(crosswalk_path: Path, registry_path: Path, namespace: str):
    crosswalk = fw.read_json(crosswalk_path)
    registry = fw.read_json(registry_path)
    fw.check_schema(crosswalk, 'kristal-external-crosswalk.schema.json')
    fw.check_schema(registry, 'kristal-identity-registry.schema.json')
    if registry['namespace_id'] != namespace:
        raise DiKError('NAMESPACE_MISMATCH')
    fw.accepted_exact(crosswalk, namespace)
    registered = {record['id']: record['kind'] for record in registry['identities']}
    active = []
    for item in crosswalk['mappings']:
        if (item['status'] != 'accepted' or item['relation'] != 'exactMatch'
                or item['local_ref']['namespace_id'] != namespace):
            continue
        kid, external = item['local_ref']['id'], item['external_ref']['id']
        expected = 'entity' if kid.startswith('KQ') else 'property'
        if registered.get(kid) != expected:
            raise DiKError('UNREGISTERED_LOCAL_ID: ' + kid)
        if any(registered.get(ref) != 'source' for ref in item['review']['evidence_refs']):
            raise DiKError('UNREGISTERED_EVIDENCE: ' + item['mapping_id'])
        active.append(item)
    return sorted(active, key=lambda x: (x['external_ref']['id'], x['mapping_id']))


def analyze_evolution(*, observations: Path, crosswalk: Path, registry: Path,
                      namespace: str, snapshot: str,
                      approved_sha256: str | None = None, sample_limit: int = 25,
                      max_records: int = 250_000, events_jsonl: Path | None = None) -> dict:
    """Analyze external identity changes against approved local mappings.

    Output contains review *observations*, not approved semantic updates.
    Source references are operator-provided, not cryptographic proofs.
    """
    observations, crosswalk, registry = map(Path, (observations, crosswalk, registry))
    if not snapshot or len(snapshot) > 200:
        raise DiKError('INVALID_SNAPSHOT')
    if not 0 <= sample_limit <= 1000:
        raise DiKError('INVALID_SAMPLE_LIMIT')
    if approved_sha256 is not None and not _DIGEST.fullmatch(approved_sha256):
        raise DiKError('INVALID_APPROVED_SHA256')
    if events_jsonl is not None and Path(events_jsonl).exists():
        raise DiKError('OUTPUT_EXISTS')
    data, source_sha256 = _read_events(observations, snapshot, max_records)
    if approved_sha256 is not None and source_sha256 != approved_sha256:
        raise DiKError('INTEGRITY_MISMATCH: normalized observations digest does not match approved value')
    _validate_graph(data)
    active = _read_crosswalk(crosswalk, registry, namespace)
    resolved = {}
    by_terminal = defaultdict(list)
    affected = set()
    for mapping in active:
        xid = mapping['external_ref']['id']
        result = _resolve(xid, data) if xid in data else {'kind': 'terminal', 'terminal_id': xid,
                                                        'path': [xid], 'evidence_references': []}
        resolved[mapping['mapping_id']] = result
        if result['kind'] == 'terminal':
            by_terminal[result['terminal_id']].append(mapping)
        if xid in data:
            affected.add(mapping['mapping_id'])
    collisions = []
    collision_ids = set()
    for destination in sorted(by_terminal):
        group = by_terminal[destination]
        if len({(x['local_ref']['namespace_id'], x['local_ref']['id']) for x in group}) < 2:
            continue
        if not any(x['mapping_id'] in affected for x in group):
            continue
        mids = sorted(x['mapping_id'] for x in group)
        collision_ids.update(mids)
        collisions.append({'external_target':destination,'mapping_ids':mids,
            'local_ids':sorted({x['local_ref']['id'] for x in group}),
            'classification':'possible_external_merge',
            'decision':'human_review_required_no_identity_merge'})
    reports = []
    for item in active:
        mid = item['mapping_id']
        if mid not in affected:
            continue
        result = resolved[mid]
        kind = result['kind']
        category = ('redirect_chain' if kind == 'terminal' else
                    'retired_external_identifier' if kind == 'retired' else 'possible_split')
        if mid in collision_ids:
            category = 'redirect_collision_review'
        reports.append({'mapping_id':mid,'local_id':item['local_ref']['id'],
            'external_id':item['external_ref']['id'],
            'category':category, 'resolution':result,
            'requires_review':True,'crosswalk_changed':False,
            'proposal_only':True})
    reports.sort(key=lambda x: (x['local_id'], x['mapping_id']))
    if events_jsonl is not None:
        path = Path(events_jsonl)
        path.parent.mkdir(parents=True, exist_ok=True)
        created = False
        try:
            with path.open('x', encoding='utf-8', newline='\n') as handle:
                created = True
                for item in reports:
                    handle.write(json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(',', ':'))+'\n')
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise DiKError('OUTPUT_EXISTS') from exc
        except BaseException:
            if created:
                path.unlink(missing_ok=True)
            raise
    by_category = {}
    for item in reports:
        by_category[item['category']] = by_category.get(item['category'], 0) + 1
    return {'profile':'dik.wikidata-evolution-impact/1.0-candidate',
        'namespace_id':namespace,'source_snapshot':snapshot,
        'observations_sha256':source_sha256,
        'normalized_digest_verified':approved_sha256 is not None,
        'crosswalk_sha256':fw.sha256(crosswalk),'registry_sha256':fw.sha256(registry),
        'observations_count':len(data),'accepted_exact_mappings_checked':len(active),
        'affected_mappings':len(reports), 'by_category':dict(sorted(by_category.items())),
        'collisions':collisions,'samples':reports[:sample_limit],
        'sample_truncated':len(reports)>sample_limit,
        'events_jsonl':str(events_jsonl) if events_jsonl is not None else None,
        'canonical_mutation':False,'crosswalk_mutation':False,
        'warning':'Candidate observations only; verifying the normalized digest does not authenticate upstream Wikidata evidence. '+
                  'Wikidata edits never implicitly merge or renumber Kristal identities.'}
