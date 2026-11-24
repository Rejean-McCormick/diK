"""Read-only federated index of Framework v11 KQ/KP and reviewed Wikidata links.

A derived *index*, not a new semantic authority. No source changes, no lexical
inference, no automatic approval. Output is an immutable, independently audited
SQLite snapshot plus a hash-protected, path-free manifest.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

from .kristals14 import discover, _select
from ._framework import dictionaries

PROFILE = 'dik.federated-semantic-registry/0.1-candidate'
TARGET_LANGUAGES = ('en','fr','es','de','nl','sv','da','nn','fi','et','af','it','pt')
LOCAL_ID = re.compile(r'^(KQ|KP)[0-9]+$')
WIKIDATA_ID = re.compile(r'^[QP][1-9][0-9]*$')


class RegistryError(ValueError):
    pass


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _safe_subfile(path: Path, root: Path):
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise RegistryError('source outside official root, symlink or missing file')


def _connect(db: Path):
    connection=sqlite3.connect(db)
    connection.executescript('''
      PRAGMA journal_mode=DELETE;
      CREATE TABLE identities (
        kristal TEXT NOT NULL, namespace_id TEXT NOT NULL, semantic_id TEXT NOT NULL,
        kind TEXT NOT NULL, local_status TEXT NOT NULL,
        label TEXT, definition TEXT,
        PRIMARY KEY(kristal,namespace_id,semantic_id));
      CREATE INDEX ix_identity_ns ON identities(namespace_id,semantic_id);
      CREATE TABLE crosswalk (
        kristal TEXT NOT NULL, namespace_id TEXT NOT NULL, semantic_id TEXT NOT NULL,
        wikidata_id TEXT NOT NULL, relation TEXT NOT NULL, source_status TEXT NOT NULL,
        decision TEXT NOT NULL, mapping_id TEXT NOT NULL,
        review_decision_id TEXT, evidence_refs_json TEXT NOT NULL);
      CREATE INDEX ix_crosswalk_q ON crosswalk(wikidata_id,decision);
      CREATE INDEX ix_crosswalk_local ON crosswalk(namespace_id,semantic_id,decision);
      CREATE TABLE kristals(kristal TEXT PRIMARY KEY, state TEXT NOT NULL,
        registered INTEGER NOT NULL, accepted_exact INTEGER NOT NULL, issue TEXT NOT NULL);
    ''')
    return connection


def _validate_kind(local: str, external: str) -> bool:
    return bool(LOCAL_ID.fullmatch(local) and WIKIDATA_ID.fullmatch(external) and
                ((local.startswith('KQ') and external.startswith('Q')) or
                 (local.startswith('KP') and external.startswith('P'))))


def _snapshot(source, owner: Path, root: Path):
    for file in (source.registry, source.graph, source.crosswalk, source.catalog):
        _safe_subfile(Path(file),root)
    # Same frozen Framework audit used for the coverage pipeline.
    dictionaries.audit(source.catalog, source.crosswalk, source.registry)
    registry = dictionaries.read_json(source.registry)
    graph = dictionaries.read_json(source.graph)
    crosswalk = dictionaries.read_json(source.crosswalk)
    catalog = dictionaries.read_json(source.catalog)
    namespace = registry['namespace_id']
    if not isinstance(namespace,str) or not namespace or namespace != graph.get('namespace_id') or namespace != catalog.get('namespace_id'):
        raise RegistryError('source namespaces disagree')
    return namespace, registry, crosswalk


def build(*, official_root: Path, output_dir: Path, min_kristals: int=126,
          selection_file: Path | None=None) -> dict:
    """Create one new registry; fail closed if a different output already exists."""
    root=Path(official_root).resolve(strict=True)
    out=Path(output_dir).absolute()
    if not root.is_dir() or out.is_symlink() or out.exists() or out.resolve().is_relative_to(root):
        raise RegistryError('output exists or overlaps protected official Kristals')
    if not 1<=min_kristals<=10000:
        raise RegistryError('invalid minimum official Kristal count')
    official={p.name:p for p in root.iterdir() if p.is_dir() and not p.is_symlink()}
    if len(official)<min_kristals:
        raise RegistryError('insufficient official Kristals; refusing an accidental partial scan')
    candidates={c.folder.name:c for c in discover(root) if c.folder.parent==root}
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.dik-federation-',dir=out.parent) as tmp:
        folder=Path(tmp)
        dbfile=folder/'registry.sqlite3'
        db=_connect(dbfile)
        issues=[]
        try:
            for name in sorted(official):
                c=candidates.get(name)
                if not c:
                    db.execute('INSERT INTO kristals VALUES (?,?,?,?,?)',(name,'NOT_EVALUABLE',0,0,'No official v11 candidate'))
                    continue
                snap, reason, _ = _select(c)
                if snap is None:
                    db.execute('INSERT INTO kristals VALUES (?,?,?,?,?)',(name,'NOT_EVALUABLE',0,0,reason[:300]))
                    continue
                try:
                    ns,reg,cw=_snapshot(snap,c.folder,root)
                    refs={}
                    for ident in reg['identities']:
                        ident_id=ident.get('id')
                        kind=ident.get('kind')
                        if kind not in ('entity','property') or not isinstance(ident_id,str) or not LOCAL_ID.fullmatch(ident_id):
                            continue
                        if (kind=='entity') != ident_id.startswith('KQ'):
                            raise RegistryError('identity kind disagrees with id prefix')
                        if ident_id in refs:
                            raise RegistryError('duplicate local identity in same registry')
                        refs[ident_id]=kind
                        label=ident.get('label') if isinstance(ident.get('label'),str) else None
                        definition=ident.get('definition') if isinstance(ident.get('definition'),str) else None
                        db.execute('INSERT INTO identities VALUES (?,?,?,?,?,?,?)',
                                   (name,ns,ident_id,kind,str(ident.get('status','unspecified')),label,definition))
                    approved=0
                    for mapping in cw['mappings']:
                        lr=mapping.get('local_ref') or {}
                        er=mapping.get('external_ref') or {}
                        local=lr.get('id'); external=er.get('id')
                        if not isinstance(local,str) or not isinstance(external,str):
                            continue
                        if local not in refs or lr.get('namespace_id')!=ns or er.get('system')!='wikidata' or not _validate_kind(local,external):
                            issues.append((name,'invalid_or_unregistered_mapping'))
                            continue
                        relation=mapping.get('relation','unknown'); status=mapping.get('status','unknown')
                        review=mapping.get('review') if isinstance(mapping.get('review'),dict) else {}
                        evidence=review.get('evidence_refs')
                        evidence=evidence if isinstance(evidence,list) and all(isinstance(v,str) and v.startswith('KS') for v in evidence) else []
                        decision_id=review.get('decision_id') if isinstance(review.get('decision_id'),str) else None
                        if relation=='exactMatch' and status=='accepted' and decision_id and evidence:
                            decision='ACCEPTED_EXACT_REVIEWED';approved+=1
                        elif status=='accepted':
                            decision='ACCEPTED_SOURCE_NOT_APPROVED_FOR_QUERY'
                        elif status=='rejected':
                            decision='REJECTED'
                        else:
                            decision='CANDIDATE_ONLY'
                        db.execute('INSERT INTO crosswalk VALUES (?,?,?,?,?,?,?,?,?,?)',
                                   (name,ns,local,external,relation,status,decision,str(mapping.get('mapping_id','')),
                                    decision_id,json.dumps(evidence,separators=(',',':'))))
                    db.execute('INSERT INTO kristals VALUES (?,?,?,?,?)',(name,'EVALUABLE',len(refs),approved,''))
                except (OSError,ValueError,KeyError,sqlite3.DatabaseError) as exc:
                    # No partial rows survive for an invalid official source.
                    db.execute('DELETE FROM crosswalk WHERE kristal=?',(name,))
                    db.execute('DELETE FROM identities WHERE kristal=?',(name,))
                    db.execute('INSERT INTO kristals VALUES (?,?,?,?,?)',(name,'NOT_EVALUABLE',0,0,type(exc).__name__+': '+str(exc)[:220]))
            from .canonical_v11 import ingest as ingest_canonical
            canonical_stats=ingest_canonical(db,root,sorted(official))
            from .canonical_selection import ingest as ingest_selection
            selection_stats=ingest_selection(db, decisions_file=selection_file)
            db.commit()
            stats={
                'official_kristals':len(official),
                'evaluable_kristals':db.execute("SELECT COUNT(*) FROM kristals WHERE state='EVALUABLE'").fetchone()[0],
                'non_evaluable_kristals':db.execute("SELECT COUNT(*) FROM kristals WHERE state='NOT_EVALUABLE'").fetchone()[0],
                'local_kq_kp_occurrences':db.execute('SELECT COUNT(*) FROM identities').fetchone()[0],
                'reviewed_accepted_exact_links':db.execute("SELECT COUNT(*) FROM crosswalk WHERE decision='ACCEPTED_EXACT_REVIEWED'").fetchone()[0],
                'unreviewed_or_candidate_links':db.execute("SELECT COUNT(*) FROM crosswalk WHERE decision!='ACCEPTED_EXACT_REVIEWED'").fetchone()[0],
                'duplicate_full_local_keys':db.execute('''SELECT COUNT(*) FROM (SELECT namespace_id,semantic_id
                  FROM identities GROUP BY namespace_id,semantic_id HAVING COUNT(DISTINCT kristal)>1)''').fetchone()[0],
                'ambiguous_local_external_links':db.execute('''SELECT COUNT(*) FROM (SELECT namespace_id,semantic_id
                  FROM crosswalk WHERE decision='ACCEPTED_EXACT_REVIEWED' GROUP BY namespace_id,semantic_id
                  HAVING COUNT(DISTINCT wikidata_id)>1)''').fetchone()[0],
                'invalid_source_mapping_rows':len(issues),
            }
            db.execute('VACUUM')
        finally:
            db.close()
        manifest={
            'profile':PROFILE,'purpose':'read_only_derived_index_not_canonical',
            'status':'CANDIDATE_FEDERATED_VIEW','source_role':'framework_official_kristals',
            'languages_target':list(TARGET_LANGUAGES),'legacy_no_retained':True,
            'source_roots_exported':False,'new_semantic_authority_created':False,
            'automatic_approvals':0,'published_dictionaries':0,
            'sqlite_file':'registry.sqlite3','sqlite_sha256':_hash(dbfile),'statistics':stats,
            'canonical_v11':{'profile':'dik.canonical-v11-revision-evidence/0.1',
                             'status':'UNSELECTED_SOURCE_EVIDENCE',
                             'statistics':canonical_stats},
            'canonical_selection':{'profile':'dik.canonical-revision-selection/0.1',
                                   'status':'DERIVED_VIEW_ONLY_NOT_FRAMEWORK_AUTHORITY',
                                   'statistics':selection_stats},
        }
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
        # Atomic promotion: no source file is ever modified, no overwriting.
        os.rename(folder,out)
    return manifest


def audit(directory: Path) -> dict:
    path=Path(directory)
    if path.is_symlink(): raise RegistryError('symlinked federation output refused')
    manifest=json.loads((path/'manifest.json').read_text(encoding='utf-8'))
    if (manifest.get('profile')!=PROFILE or manifest.get('purpose')!='read_only_derived_index_not_canonical'
        or manifest.get('sqlite_file')!='registry.sqlite3' or manifest.get('automatic_approvals')!=0
        or manifest.get('published_dictionaries')!=0 or manifest.get('languages_target')!=list(TARGET_LANGUAGES)):
        raise RegistryError('nonconforming federation manifest')
    sqlite_file=path/'registry.sqlite3'
    if sqlite_file.is_symlink() or _hash(sqlite_file)!=manifest.get('sqlite_sha256'):
        raise RegistryError('federated index SHA256 mismatch')
    with sqlite3.connect(f'{sqlite_file.resolve().as_uri()}?mode=ro&immutable=1',uri=True) as db:
        quick=db.execute('PRAGMA quick_check').fetchone()[0]
        if quick!='ok': raise RegistryError('federated index integrity failure')
        count=db.execute('SELECT COUNT(*) FROM kristals').fetchone()[0]
        if count!=manifest['statistics']['official_kristals']:
            raise RegistryError('manifest/index count mismatch')
        canonical=manifest.get('canonical_v11')
        if canonical is not None:
            if (canonical.get('profile')!='dik.canonical-v11-revision-evidence/0.1'
                or canonical.get('status')!='UNSELECTED_SOURCE_EVIDENCE'):
                raise RegistryError('canonical evidence profile mismatch')
            cs=canonical['statistics']
            if cs.get('selected_revisions')!=0 or cs.get('new_global_approvals')!=0:
                raise RegistryError('canonical evidence cannot authorize publication')
            revision_rows=db.execute('SELECT COUNT(*) FROM canonical_revisions').fetchone()[0]
            if revision_rows!=cs.get('v11_revisions'):
                raise RegistryError('canonical revision count mismatch')
        selection=manifest.get('canonical_selection')
        if selection is not None:
            if (selection.get('profile')!='dik.canonical-revision-selection/0.1'
                or selection.get('status')!='DERIVED_VIEW_ONLY_NOT_FRAMEWORK_AUTHORITY'):
                raise RegistryError('canonical selection profile mismatch')
            ss=selection.get('statistics') or {}
            if ss.get('framework_authority_confirmed')!=0 or ss.get('new_global_approvals')!=0 or ss.get('published_dictionaries')!=0:
                raise RegistryError('selection cannot authorize sources or publication')
            rows=db.execute('SELECT decision,selected_revision_dir,selected_source_exact,source_authority_confirmed,globally_approved_new_links FROM canonical_selection').fetchall()
            if len(rows)!=ss.get('official_kristals') or len(rows)!=count:
                raise RegistryError('canonical selection row count mismatch')
            if any(x[3]!=0 or x[4]!=0 for x in rows):
                raise RegistryError('canonical selection authority elevated')
            if any((x[0] in ('SINGLE_DECLARED_DERIVED_VIEW','OPERATOR_PINNED_DERIVED_VIEW')) != (x[1] is not None) for x in rows):
                raise RegistryError('canonical selection inconsistent')
            if sum(x[2] for x in rows)!=ss.get('selected_source_exact_per_view_not_global_approval'):
                raise RegistryError('canonical selection count mismatch')
            if db.execute('''SELECT COUNT(*) FROM canonical_selection s
                     WHERE s.selected_revision_dir IS NOT NULL AND NOT EXISTS
                       (SELECT 1 FROM canonical_revisions r
                        WHERE r.kristal=s.kristal AND r.revision_dir=s.selected_revision_dir
                          AND r.state='OBSERVED_UNSELECTED')''').fetchone()[0]:
                raise RegistryError('selected canonical revision missing or unverified')
    return manifest


def query(*, directory: Path, namespace: str|None=None, semantic_id: str|None=None,
          wikidata_id: str|None=None, limit: int=100) -> dict:
    manifest=audit(directory)
    if not 1<=limit<=500:
        raise RegistryError('invalid query limit')
    local=namespace is not None or semantic_id is not None
    if local == (wikidata_id is not None):
        raise RegistryError('provide EITHER full namespace+KQ/KP OR Wikidata Q/P')
    if local and (not namespace or not semantic_id or not LOCAL_ID.fullmatch(semantic_id)):
        raise RegistryError('never query a local identifier without its namespace')
    if not local and (not isinstance(wikidata_id,str) or not WIKIDATA_ID.fullmatch(wikidata_id)):
        raise RegistryError('invalid Q/P')
    dbfile=Path(directory)/manifest['sqlite_file']
    with sqlite3.connect(f'{dbfile.resolve().as_uri()}?mode=ro&immutable=1',uri=True) as db:
        db.row_factory=sqlite3.Row
        if local:
            vals=list(db.execute('''SELECT kristal,namespace_id,semantic_id,kind,local_status,label,definition
             FROM identities WHERE namespace_id=? AND semantic_id=? ORDER BY kristal LIMIT ?''',
             (namespace,semantic_id,limit+1)))
            links=list(db.execute('''SELECT kristal,wikidata_id,relation,source_status,decision,review_decision_id,evidence_refs_json
              FROM crosswalk WHERE namespace_id=? AND semantic_id=? ORDER BY kristal,wikidata_id LIMIT ?''',
              (namespace,semantic_id,limit+1)))
        else:
            links=list(db.execute('''SELECT kristal,namespace_id,semantic_id,relation,source_status,decision,
             review_decision_id,evidence_refs_json FROM crosswalk WHERE wikidata_id=?
             ORDER BY kristal,namespace_id,semantic_id LIMIT ?''',(wikidata_id,limit+1)))
            vals=[]
    truncated=len(links)>limit or len(vals)>limit
    if local and len({r['kristal'] for r in vals})>1:
        status='DUPLICATE_NAMESPACE_LOCAL_KEY_REVIEW_REQUIRED'
    else:
        status='OBSERVATION_ONLY'
    results=[{k:val for k,val in dict(r).items() if k!='evidence_refs_json'} |
             ({'evidence_refs':json.loads(r['evidence_refs_json'])} if 'evidence_refs_json' in r.keys() else {}) for r in links[:limit]]
    # Exact accepted links are kept distinguishable from candidate links.
    return {'profile':PROFILE,'status':status,'approved_for_publication':False,
            'identities':[dict(v) for v in vals[:limit]],'links':results,'truncated':truncated}
