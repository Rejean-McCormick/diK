"""Compare immutable Wikidata lexical snapshots without changing KQ/KP mappings.

Only Wikidata layers are compared; curated layers never change. Event output is
streamed, while JSON summary samples are bounded even for very large imports.
"""
from __future__ import annotations
import json
import os
from collections import Counter
from pathlib import Path

from ._framework import dictionaries as fw
from .operations import DiKError, serialize_json


def _wikidata_layers(catalog_path: Path):
    cat = fw.read_json(catalog_path)
    layers = {}
    for lang in cat['languages']:
        choices = [x for x in lang['layers'] if x['kind'] == 'wikidata']
        if len(choices) > 1:
            raise DiKError('AMBIGUOUS_SOURCE: multiple Wikidata layers for one locale')
        if choices:
            layers[lang['tag']] = fw.safe_file(catalog_path.parent, choices[0]['path'])
    return cat, layers


def _entries(path):
    if path is None: return
    previous = None
    with path.open(encoding='utf-8') as src:
        for number, line in enumerate(src, 1):
            if not line.strip(): continue
            try: obj = json.loads(line)
            except ValueError as exc: raise DiKError(f'INVALID_SNAPSHOT_JSONL: {path}:{number}') from exc
            kid = obj['semantic_id']
            if previous is not None and kid <= previous:
                raise DiKError('UNSORTED_SNAPSHOT: lexical layer not strictly ordered')
            previous = kid
            yield obj


def _change(before, after):
    if before is None: return 'added'
    if after is None: return 'removed'
    fields = ('external_id','preferred_term','aliases','description')
    changed = [k for k in fields if before.get(k) != after.get(k)]
    if not changed:
        return 'revision_only' if before.get('source_revision') != after.get('source_revision') else None
    if 'external_id' in changed: return 'external_id_changed'
    if changed == ['preferred_term']: return 'label_changed'
    if changed == ['aliases']: return 'aliases_changed'
    if changed == ['description']: return 'description_changed'
    return 'multiple_fields_changed'


def compare_snapshots(*, before: Path, after: Path, crosswalk: Path, registry: Path,
                      sample_limit: int = 25, events_path: Path | None = None,
                      include_revision_only: bool = False) -> dict:
    before, after = Path(before).resolve(), Path(after).resolve()
    if sample_limit < 0 or sample_limit > 1000:
        raise DiKError('INVALID_SAMPLE_LIMIT: expected 0..1000')
    if events_path is not None:
        events_path = Path(events_path).resolve()
        if events_path.exists(): raise DiKError('OUTPUT_EXISTS: never overwrite existing events')
    fw.audit(before, crosswalk, registry)
    fw.audit(after, crosswalk, registry)
    old, old_layers = _wikidata_layers(before)
    new, new_layers = _wikidata_layers(after)
    if old['namespace_id'] != new['namespace_id']:
        raise DiKError('NAMESPACE_MISMATCH')
    counts = Counter()
    samples = []
    total = 0
    stream = None
    tmp = None
    try:
        if events_path is not None:
            events_path.parent.mkdir(parents=True,exist_ok=True)
            tmp = events_path.with_name('.' + events_path.name + '.incomplete')
            stream = tmp.open('x',encoding='utf-8')
        for locale in sorted(set(old_layers)|set(new_layers)):
            left = iter(_entries(old_layers.get(locale)))
            right = iter(_entries(new_layers.get(locale)))
            a, b = next(left,None), next(right,None)
            while a is not None or b is not None:
                if b is None or (a is not None and a['semantic_id'] < b['semantic_id']):
                    prior, current = a, None
                    a = next(left,None)
                elif a is None or b['semantic_id'] < a['semantic_id']:
                    prior, current = None, b
                    b = next(right,None)
                else:
                    prior, current = a, b
                    a,b = next(left,None),next(right,None)
                change = _change(prior,current)
                if change is None or (change == 'revision_only' and not include_revision_only):
                    continue
                semantic_id = (prior or current)['semantic_id']
                event = {'locale':locale,'semantic_id':semantic_id,
                    'change':change,'review_required':change != 'revision_only',
                    'before':prior,'after':current}
                counts[change] += 1
                total += 1
                if len(samples) < sample_limit:
                    samples.append(event)
                if stream:
                    stream.write(json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n')
        if stream:
            stream.flush();os.fsync(stream.fileno());stream.close();stream=None
            if events_path.exists():raise DiKError('OUTPUT_EXISTS: concurrent destination')
            os.rename(tmp,events_path)
        return {'profile':'dik.wikidata-snapshot-diff/1.0-candidate',
            'namespace_id':old['namespace_id'],'before_catalog_sha256':fw.sha256(before),
            'after_catalog_sha256':fw.sha256(after), 'before_catalog_id':old['catalog_id'],
            'after_catalog_id':new['catalog_id'], 'total_events':total,
            'by_change':dict(sorted(counts.items())),'samples':samples,
            'sample_truncated':total>len(samples),
            'events_jsonl':str(events_path) if events_path else None,
            'mutates_canonical_graph':False,
            'note':'Label changes are observations, not accepted identity changes.'}
    finally:
        if stream: stream.close()
        if tmp and tmp.exists():tmp.unlink()
