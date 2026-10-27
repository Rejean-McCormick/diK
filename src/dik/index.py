"""Reconstructible SQLite read model for sparse multilingual dictionaries.

Authoritative inputs are the Framework catalog and SHA-verified shards, never SQLite.
Lookup produces CANDIDATES; no score or uniqueness grants an identity decision.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unicodedata
from pathlib import Path

from ._framework import dictionaries as fw
from .operations import DiKError, Project

SCHEMA = '''
CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE terms(namespace TEXT NOT NULL, locale TEXT NOT NULL, semantic_id TEXT NOT NULL,
 kind TEXT NOT NULL, term TEXT NOT NULL, normalized TEXT NOT NULL, variant TEXT NOT NULL,
 layer_id TEXT NOT NULL, priority INTEGER NOT NULL, source_kind TEXT NOT NULL,
 provenance TEXT NOT NULL,
 UNIQUE(namespace,locale,semantic_id,term,variant,layer_id));
CREATE INDEX idx_term ON terms(namespace,locale,kind,normalized,semantic_id);
CREATE INDEX idx_identifier ON terms(namespace,locale,semantic_id,priority DESC);
CREATE TABLE conflicts(namespace TEXT NOT NULL, locale TEXT NOT NULL, kind TEXT NOT NULL,
 conflict_type TEXT NOT NULL, group_key TEXT NOT NULL, affected_count INTEGER NOT NULL,
 PRIMARY KEY(namespace,locale,kind,conflict_type,group_key));
CREATE INDEX idx_conflicts_queue ON conflicts(namespace,locale,kind,conflict_type,group_key);
'''


def normalize(term: str) -> str:
    """Only NFC; casefolding would make a different, explicit fuzzy search mode."""
    return unicodedata.normalize('NFC', term)


def build(project: Project, output: Path) -> dict:
    """Verify all sources, stream records to temp database and publish atomically."""
    output = Path(output).resolve()
    if output.exists():
        raise DiKError('Index already exists; choose a new path to preserve old snapshots')
    fw.audit(project.catalog, project.crosswalk, project.registry)
    catalog = fw.read_json(project.catalog)
    reg = fw.read_json(project.registry)
    kinds = {i['id']:i['kind'] for i in reg['identities']}
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tempname = tempfile.mkstemp(prefix='.dik-index-',suffix='.sqlite',dir=output.parent)
    os.close(fd)
    tmp = Path(tempname)
    db = None
    count = 0
    try:
        db = sqlite3.connect(tmp)
        db.executescript(SCHEMA)
        for key, value in [('catalog_sha256',fw.sha256(project.catalog)),
                           ('registry_sha256',fw.sha256(project.registry)),
                           ('crosswalk_sha256',fw.sha256(project.crosswalk)),
                           ('namespace_id',catalog['namespace_id']),
                           ('catalog_id',catalog['catalog_id']),('index_format','dik-index/1'),
                           ('conciliation_format','dik-conciliation/1')]:
            db.execute('INSERT INTO meta VALUES (?,?)',(key,value))
        for lang in catalog['languages']:
            locale = lang['tag']
            for layer in lang['layers']:
                path = fw.safe_file(project.catalog.parent,layer['path'])
                if fw.sha256(path) != layer['sha256']:
                    raise DiKError('INTEGRITY_MISMATCH: ' + layer['path'])
                for record, _ in fw.layer_records(path,layer['kind']):
                    kid=record['semantic_id']
                    kind = {'entity':'KQ','property':'KP'}.get(kinds.get(kid))
                    if kind is None:
                        raise DiKError('Unregistered semantic reference in layer: '+kid)
                    primary = record['preferred_term']
                    aliases = record.get('alternate_terms', record.get('aliases', []))
                    for term, variant in [(primary,'preferred')]+[(alias,'alias') for alias in aliases]:
                        if not isinstance(term,str) or not term:
                            continue
                        provenance=json.dumps({'layer':layer['layer_id'],'source':layer.get('source_snapshot'),
                           'external_id':record.get('external_id')}, sort_keys=True, ensure_ascii=False)
                        db.execute('INSERT OR IGNORE INTO terms VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                         (catalog['namespace_id'],locale,kid,kind,term,normalize(term),variant,
                          layer['layer_id'],layer['priority'],layer['kind'],provenance))
                        count+=1
        # Precompute paginated conflict queues once during index build. Read-only
        # Web requests never scan entire dictionary shards or allocate all results.
        db.execute("""INSERT INTO conflicts
          SELECT namespace,locale,kind,'competing_preferred',semantic_id,
                 COUNT(DISTINCT normalized)
          FROM terms WHERE variant='preferred'
          GROUP BY namespace,locale,kind,semantic_id
          HAVING COUNT(DISTINCT normalized)>1""")
        db.execute("""INSERT INTO conflicts
          SELECT namespace,locale,kind,'shared_term',normalized,
                 COUNT(DISTINCT semantic_id)
          FROM terms
          GROUP BY namespace,locale,kind,normalized
          HAVING COUNT(DISTINCT semantic_id)>1""")
        db.commit()
        db.close(); db=None
        os.replace(tmp,output)
        return {'index':str(output),'rows_processed':count,'catalog_sha256':fw.sha256(project.catalog),
                'namespace_id':catalog['namespace_id'],'index_sha256':fw.sha256(output)}
    finally:
        if db is not None: db.close()
        tmp.unlink(missing_ok=True)


def _verify(db: sqlite3.Connection, project: Project) -> dict:
    meta=dict(db.execute('SELECT key,value FROM meta'))
    if (meta.get('catalog_sha256')!=fw.sha256(project.catalog) or
        meta.get('registry_sha256')!=fw.sha256(project.registry) or
        meta.get('crosswalk_sha256')!=fw.sha256(project.crosswalk)):
        raise DiKError('STALE_SOURCE: index inputs changed; rebuild the index')
    return meta


def reverse_lookup(project: Project, index: Path, *, term: str, locale: str,
                   kind: str, limit: int = 200) -> dict:
    """Exact NFC, explicit namespace + locale + kind. Never approves a mapping."""
    fw.check_locale(locale)
    if kind not in ('KQ','KP') or not isinstance(term,str) or not term:
        raise DiKError('Expected non-empty term and expected_kind KQ or KP')
    if not 1<=limit<=1000: raise DiKError('Result limit must be in 1..1000')
    uri=Path(index).resolve().as_uri()+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as db:
        meta=_verify(db,project)
        matches=db.execute('''SELECT semantic_id,term,variant,layer_id,priority,source_kind,provenance
          FROM terms WHERE namespace=? AND locale=? AND kind=? AND normalized=?
          ORDER BY semantic_id,priority DESC,layer_id,term''',
          (meta['namespace_id'],locale,kind,normalize(term))).fetchall()
    entries={}
    for sid,display,variant,layer,priority,source_kind,provenance in matches:
        entries.setdefault(sid,[]).append({'term':display,'variant':variant,'layer_id':layer,
            'priority':priority,'source_kind':source_kind,'provenance':json.loads(provenance)})
    ids=sorted(entries)
    return {'namespace_id':meta['namespace_id'],'term':term,'locale':locale,'expected_kind':kind,
        'state':'no_candidate' if not ids else 'unique_candidate' if len(ids)==1 else 'ambiguous',
        'candidate_count':len(ids),'truncated':len(ids)>limit,
        'candidates':[{'semantic_id':sid,'signals':entries[sid],
                       'status':'candidate_unreviewed'} for sid in ids[:limit]],
        'identity_approved':False,'index_catalog_sha256':meta['catalog_sha256']}
