"""Read-only, explainable lexical conflicts across indexed dictionary layers.

A conflict is NOT an assertion of semantic equivalence.  Reports are snapshots of
an index tied to catalog, registry and crosswalk digests; they do not approve any
identity, ranking, translation, or write to the canonical project.

Two disjoint categories:
- competing_preferred: multiple preferred terms for the SAME KQ/KP+locale.
- shared_term: the SAME exact NFC term is used for multiple KQ or multiple KP.

Both are intentionally warnings, never automatic merges. No casefolding or fuzzy
matching, and locales/namespaces/kinds cannot be conflated.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from . import FRAMEWORK_CONTRACT
from .index import normalize, _verify
from .operations import DiKError, Project
from ._framework import dictionaries as fw


def _database(project: Project, index: Path):
    uri = Path(index).resolve().as_uri() + '?mode=ro'
    db = sqlite3.connect(uri, uri=True)
    try:
        meta = _verify(db, project)
        if meta.get('conciliation_format') != 'dik-conciliation/1':
            raise DiKError('INDEX_UPGRADE_REQUIRED: rebuild your index with diK alpha.3')
        return db, meta
    except BaseException:
        db.close()
        raise


def _checked_locale(project: Project, locale: str):
    fw.check_locale(locale)
    catalog = fw.read_json(project.catalog)
    if locale not in {l['tag'] for l in catalog['languages']}:
        raise DiKError('UNDECLARED_LOCALE')


def variants(project: Project, index: Path, semantic_id: str, locale: str) -> dict:
    """Display all independent source observations for one KQ/KP.

    The preferred display still comes from the normative Framework resolver.
    Alternative labels never alter that decision.
    """
    _checked_locale(project, locale)
    registry = fw.read_json(project.registry)
    types = {v['id']: v['kind'] for v in registry['identities']}
    kind = {'entity': 'KQ', 'property': 'KP'}.get(types.get(semantic_id))
    if kind is None:
        raise DiKError('Unknown KQ/KP semantic identity')
    with_index, meta = _database(project, index)
    with closing(with_index) as db:
        rows = db.execute('''SELECT term,variant,layer_id,priority,source_kind,provenance
              FROM terms WHERE namespace=? AND locale=? AND semantic_id=?
              ORDER BY priority DESC,layer_id,variant,term''',
              (meta['namespace_id'], locale, semantic_id)).fetchall()
    # A higher priority is a presentation preference, NOT proof of truth.
    signals = [dict(term=term,variant=variant,layer_id=layer,priority=priority,
                    source_kind=source,provenance=json.loads(provenance))
               for term,variant,layer,priority,source,provenance in rows]
    preferred = sorted({normalize(s['term']) for s in signals if s['variant']=='preferred'})
    return {
        'contract_profile':'dik.lexical-variants/1-alpha', 'framework_contract':FRAMEWORK_CONTRACT,
        'namespace_id':meta['namespace_id'], 'semantic_id':semantic_id, 'kind':kind,
        'locale':locale, 'preferred_forms_count':len(preferred),
        'competing_preferred':len(preferred)>1, 'signals':signals,
        'decision':'unreviewed_observations', 'identity_approved_by_dik':False,
        'index_catalog_sha256':meta['catalog_sha256']
    }


def conflicts(project: Project, index: Path, *, locale: str, kind: str='all',
              conflict_type: str='all', page: int=1, page_size: int=25) -> dict:
    """Paginated deterministic conflicts. SQLite queries filter before pagination."""
    _checked_locale(project, locale)
    if kind not in ('KQ','KP','all'):
        raise DiKError('Unknown kind (use KQ, KP, all)')
    if conflict_type not in ('competing_preferred','shared_term','all'):
        raise DiKError('Unknown lexical conflict type')
    if not isinstance(page,int) or not 1 <= page <= 1_000_000:
        raise DiKError('Invalid page')
    if not isinstance(page_size,int) or not 1 <= page_size <= 100:
        raise DiKError('Invalid page size')
    db, meta = _database(project,index)
    criteria = ['namespace=?', 'locale=?']
    params: list[object] = [meta['namespace_id'], locale]
    if kind!='all': criteria.append('kind=?');params.append(kind)
    if conflict_type!='all':criteria.append('conflict_type=?');params.append(conflict_type)
    where=' AND '.join(criteria)
    with closing(db):
        total=db.execute('SELECT count(*) FROM conflicts WHERE '+where, params).fetchone()[0]
        rows=db.execute('''SELECT kind,conflict_type,group_key,affected_count
                          FROM conflicts WHERE '''+where+''' ORDER BY kind,conflict_type,group_key
                          LIMIT ? OFFSET ?''',params+[page_size,(page-1)*page_size]).fetchall()
    items=[{'kind': k,'type':t, 'key': key,'affected_count':n,
            'status':'requires_review', 'automatic_merge_allowed':False}
           for k,t,key,n in rows]
    return {'contract_profile':'dik.lexical-conflict-report/1-alpha',
            'namespace_id':meta['namespace_id'],'locale':locale, 'kind':kind,
            'conflict_type':conflict_type,'total':total,'page':page,'page_size':page_size,
            'items':items,'identity_approved_by_dik':False,
            'index_catalog_sha256':meta['catalog_sha256']}


def conflict_detail(project: Project, index: Path, *, locale: str, kind: str,
                    conflict_type: str, key: str) -> dict:
    """Explain one queued conflict. Always read-only; bounded by 200 observations."""
    _checked_locale(project,locale)
    if kind not in ('KQ','KP') or conflict_type not in ('competing_preferred','shared_term'):
        raise DiKError('Invalid conflict selector')
    if not key or len(key)>4096:
        raise DiKError('Invalid conflict key')
    db, meta = _database(project,index)
    with closing(db):
        registered=db.execute('''SELECT 1 FROM conflicts
            WHERE namespace=? AND locale=? AND kind=? AND conflict_type=? AND group_key=?''',
            (meta['namespace_id'],locale,kind,conflict_type,key)).fetchone()
        if not registered:raise DiKError('Unknown conflict or stale index')
        if conflict_type=='competing_preferred':
            rows=db.execute('''SELECT semantic_id,term,variant,layer_id,priority,source_kind,provenance
                    FROM terms WHERE namespace=? AND locale=? AND kind=? AND semantic_id=?
                    ORDER BY priority DESC,semantic_id,layer_id,term LIMIT 201''',
                    (meta['namespace_id'],locale,kind,key)).fetchall()
        else:
            rows=db.execute('''SELECT semantic_id,term,variant,layer_id,priority,source_kind,provenance
                    FROM terms WHERE namespace=? AND locale=? AND kind=? AND normalized=?
                    ORDER BY semantic_id,priority DESC,layer_id LIMIT 201''',
                    (meta['namespace_id'],locale,kind,key)).fetchall()
    return {'locale':locale,'kind':kind,'type':conflict_type,'key':key,
            'signals':[{'semantic_id':sid,'term':term,'variant':variant,'layer_id':layer,
                        'priority':priority,'source_kind':source,'provenance':json.loads(prov)}
                       for sid,term,variant,layer,priority,source,prov in rows[:200]],
            'truncated':len(rows)>200,'status':'requires_review',
            'automatic_merge_allowed':False}
