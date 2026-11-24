"""Additive, read-only, revision-aware canonical evidence for the federated view.

Every file comes from a Kristal's canon/state.index.json. No revision is
promoted to the active semantic authority; source-side 'accepted' is never
silently promoted to diK global approval. No text is exported in the manifest.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import sqlite3

CONTRACTS = {
    'kristal.v11.identity-registry': 'registry',
    'kristal.v11.external-crosswalk': 'crosswalk',
    'kristal.v11.semantic-graph': 'graph',
    'kristal.v11.dictionary-catalog': 'catalog',
}
LOCAL = re.compile(r'^(KQ|KP)[0-9]+$')
QPID = re.compile(r'^[QP][1-9][0-9]*$')
MAX_FILE = 8 * 1024 * 1024


def _hash_source(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _member(owner: Path, root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or '\\' in rel or ':' in rel:
        raise ValueError('unsafe canonical path')
    part = PurePosixPath(rel)
    if part.is_absolute() or any(p in ('..', '.', '') for p in part.parts):
        raise ValueError('unsafe canonical relative path')
    path = owner.joinpath(*part.parts)
    if any(p.is_symlink() for p in (owner, *[owner.joinpath(*part.parts[:i]) for i in range(1,len(part.parts)+1)])):
        raise ValueError('symlink in canonical source')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('canonical file outside official root')
    return path


def _json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ValueError('canonical JSON unavailable or exceeds metadata cap')
    value=json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('canonical artifact must be a JSON object')
    return value


def _revision_dir(contract: str, rel: str) -> str:
    parts=rel.split('/')
    return '/'.join(parts[:-2] if contract=='kristal.v11.dictionary-catalog' else parts[:-1])


def _init(db: sqlite3.Connection) -> None:
    db.executescript('''
      CREATE TABLE canonical_sources (
        kristal TEXT PRIMARY KEY, index_state TEXT NOT NULL,
        artifacts_declared INTEGER NOT NULL, missing_artifacts INTEGER NOT NULL,
        native_registries INTEGER NOT NULL, revisions_v11 INTEGER NOT NULL,
        issue TEXT NOT NULL);
      CREATE TABLE canonical_revisions (
        kristal TEXT NOT NULL, revision_dir TEXT NOT NULL,
        namespace_id TEXT NOT NULL, state TEXT NOT NULL,
        entity_kq INTEGER NOT NULL, property_kp INTEGER NOT NULL,
        source_accepted_exact INTEGER NOT NULL,
        source_accepted_reviewed INTEGER NOT NULL,
        candidates INTEGER NOT NULL, issue TEXT NOT NULL,
        PRIMARY KEY(kristal,revision_dir));
      CREATE TABLE canonical_identity_evidence (
        kristal TEXT NOT NULL, revision_dir TEXT NOT NULL,
        namespace_id TEXT NOT NULL, semantic_id TEXT NOT NULL,
        kind TEXT NOT NULL, source_status TEXT NOT NULL,
        label TEXT, definition TEXT,
        PRIMARY KEY(kristal,revision_dir,namespace_id,semantic_id));
      CREATE INDEX ci_local ON canonical_identity_evidence(namespace_id,semantic_id);
      CREATE TABLE canonical_crosswalk_evidence (
        kristal TEXT NOT NULL, revision_dir TEXT NOT NULL,
        namespace_id TEXT NOT NULL, semantic_id TEXT NOT NULL,
        wikidata_id TEXT NOT NULL, relation TEXT NOT NULL,
        source_status TEXT NOT NULL, evidence_status TEXT NOT NULL,
        review_decision_id TEXT, evidence_refs_json TEXT NOT NULL);
      CREATE INDEX cc_wikidata ON canonical_crosswalk_evidence(wikidata_id);
      CREATE INDEX cc_local ON canonical_crosswalk_evidence(namespace_id,semantic_id);
      CREATE TABLE canonical_revision_inputs (
        kristal TEXT NOT NULL, revision_dir TEXT NOT NULL,
        state_index_sha256 TEXT, registry_sha256 TEXT,
        crosswalk_sha256 TEXT, graph_sha256 TEXT, catalog_sha256 TEXT,
        graph_state TEXT NOT NULL,
        PRIMARY KEY(kristal,revision_dir));
    ''')


def ingest(db: sqlite3.Connection, root: Path, official_names: list[str]) -> dict:
    """Index each declared V11 revision separately; never select an active one."""
    _init(db)
    for name in official_names:
        owner=root/name
        index=owner/'canon'/'state.index.json'
        artifacts=[]
        source_issue=''
        if index.is_symlink() or not index.is_file():
            source_issue='CANONICAL_INDEX_ABSENT'
        else:
            try:
                doc=_json(index)
                artifacts=doc['canonical_artifacts']
                if not isinstance(artifacts,list):
                    raise ValueError('canonical_artifacts not list')
            except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
                source_issue='INDEX_UNREADABLE:'+type(e).__name__
        index_digest=_hash_source(index) if not source_issue else None
        bydir=defaultdict(dict)
        missing=0
        native=0
        for art in artifacts:
            if not isinstance(art,dict):
                source_issue='INDEX_INVALID_ARTIFACT'; continue
            rel=art.get('path')
            contract=(art.get('logical_contract') or {}).get('id')
            try:
                p=_member(owner,root,rel)
                if not p.is_file():
                    missing+=1
            except (ValueError,OSError):
                missing+=1
                continue
            if contract and contract.endswith('.identity-registry') and contract not in CONTRACTS:
                native+=1
            if contract in CONTRACTS:
                folder=_revision_dir(contract,rel)
                if contract in bydir[folder]:
                    source_issue='DUPLICATE_V11_ARTIFACT_IN_REVISION'
                bydir[folder][CONTRACTS[contract]]=rel
        rev_count=0
        for rev,parts in sorted(bydir.items()):
            if 'registry' not in parts:
                continue
            rev_count+=1
            issue=''
            namespace=''
            entity_count=property_count=accepted=reviewed=candidates=0
            identities=[]; links=[]
            fingerprint=None
            try:
                if 'crosswalk' not in parts or 'graph' not in parts or 'catalog' not in parts:
                    raise ValueError('missing required canonical V11 peer')
                reg=_json(_member(owner,root,parts['registry']))
                cw=_json(_member(owner,root,parts['crosswalk']))
                graph_path=_member(owner,root,parts['graph'])
                if not graph_path.is_file():
                    raise ValueError('canonical semantic graph missing')
                graph_oversized=graph_path.stat().st_size>MAX_FILE
                gr={} if graph_oversized else _json(graph_path)
                cat=_json(_member(owner,root,parts['catalog']))
                fingerprint=(index_digest,
                    _hash_source(_member(owner,root,parts['registry'])),
                    _hash_source(_member(owner,root,parts['crosswalk'])),
                    None if graph_oversized else _hash_source(graph_path),
                    _hash_source(_member(owner,root,parts['catalog'])),
                    'METADATA_ONLY' if graph_oversized else 'INSPECTED')
                namespace=reg.get('namespace_id')
                if (not isinstance(namespace,str) or not namespace or
                    (not graph_oversized and gr.get('namespace_id')!=namespace) or cat.get('namespace_id')!=namespace):
                    raise ValueError('inconsistent namespace')
                registry_refs={}
                for ident in reg.get('identities',[]):
                    if not isinstance(ident,dict):continue
                    sid=ident.get('id');kind=ident.get('kind')
                    if not isinstance(sid,str) or not LOCAL.fullmatch(sid):continue
                    if (kind=='entity') != sid.startswith('KQ') or kind not in ('entity','property'):
                        raise ValueError('identity kind/id mismatch')
                    if sid in registry_refs:
                        raise ValueError('duplicate identity in revision')
                    registry_refs[sid]=kind
                    entity_count+=sid.startswith('KQ');property_count+=sid.startswith('KP')
                    identities.append((name,rev,namespace,sid,kind,str(ident.get('status','unspecified')),
                                      ident.get('label') if isinstance(ident.get('label'),str) else None,
                                      ident.get('definition') if isinstance(ident.get('definition'),str) else None))
                for m in cw.get('mappings',[]):
                    lr=m.get('local_ref') or {};er=m.get('external_ref') or {}
                    local=lr.get('id');external=er.get('id')
                    if (local not in registry_refs or lr.get('namespace_id')!=namespace or er.get('system')!='wikidata'
                        or not isinstance(external,str) or not QPID.fullmatch(external)
                        or (local.startswith('KQ') and not external.startswith('Q'))
                        or (local.startswith('KP') and not external.startswith('P'))):
                        raise ValueError('invalid/unregistered Q/P mapping')
                    relation=m.get('relation','unknown');status=m.get('status','unknown')
                    review=m.get('review') or {}
                    if not isinstance(review,dict):review={}
                    decision=review.get('decision_id')
                    evidence=review.get('evidence_refs')
                    if not isinstance(evidence,list) or not all(isinstance(v,str) and v.startswith('KS') for v in evidence):
                        evidence=[]
                    if status=='accepted' and relation=='exactMatch':
                        accepted+=1
                        if isinstance(decision,str) and decision and evidence:
                            reviewed+=1
                            evidence_status='SOURCE_ACCEPTED_REVIEWED_REVISION_UNSELECTED'
                        else:evidence_status='SOURCE_ACCEPTED_REVIEW_INCOMPLETE'
                    elif status=='rejected': evidence_status='REJECTED'
                    else:
                        candidates+=1
                        evidence_status='CANDIDATE_OR_NONEXACT'
                    links.append((name,rev,namespace,local,external,relation,status,evidence_status,
                                  decision if isinstance(decision,str) else None,
                                  json.dumps(evidence,ensure_ascii=False,separators=(',',':'))))
                db.executemany('INSERT INTO canonical_identity_evidence VALUES (?,?,?,?,?,?,?,?)',identities)
                db.executemany('INSERT INTO canonical_crosswalk_evidence VALUES (?,?,?,?,?,?,?,?,?,?)',links)
                state=('OBSERVED_UNSELECTED_GRAPH_NOT_INSPECTED' if graph_oversized
                       else 'OBSERVED_UNSELECTED')
            except (ValueError,KeyError,OSError,sqlite3.DatabaseError) as exc:
                # One invalid revision never partially contributes to the index.
                db.execute('DELETE FROM canonical_identity_evidence WHERE kristal=? AND revision_dir=?',(name,rev))
                db.execute('DELETE FROM canonical_crosswalk_evidence WHERE kristal=? AND revision_dir=?',(name,rev))
                issue=type(exc).__name__+': '+str(exc)[:180]
                state='REVISION_UNREADABLE'
                entity_count=property_count=accepted=reviewed=candidates=0
            if fingerprint is not None and state.startswith('OBSERVED_UNSELECTED'):
                db.execute('INSERT INTO canonical_revision_inputs VALUES (?,?,?,?,?,?,?,?)',
                           (name,rev,*fingerprint))
            db.execute('INSERT INTO canonical_revisions VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (name,rev,namespace,state,entity_count,property_count,accepted,reviewed,candidates,issue))
        db.execute('INSERT INTO canonical_sources VALUES (?,?,?,?,?,?,?)',
                   (name,'INDEX_READABLE' if not source_issue else source_issue,
                    len(artifacts),missing,native,rev_count,source_issue))
    db.commit()
    scalar=lambda sql: db.execute(sql).fetchone()[0]
    return {
      'index_readable':scalar("SELECT COUNT(*) FROM canonical_sources WHERE index_state='INDEX_READABLE'"),
      'kristals_with_v11':scalar('SELECT COUNT(*) FROM canonical_sources WHERE revisions_v11>0'),
      'kristals_without_v11':scalar('SELECT COUNT(*) FROM canonical_sources WHERE revisions_v11=0'),
      'v11_revisions':scalar('SELECT COUNT(*) FROM canonical_revisions'),
      'v11_revisions_observed':scalar("SELECT COUNT(*) FROM canonical_revisions WHERE state LIKE 'OBSERVED_UNSELECTED%'"),
      'canonical_missing_artifacts':scalar('SELECT COALESCE(SUM(missing_artifacts),0) FROM canonical_sources'),
      'large_graphs_metadata_only':scalar("SELECT COUNT(*) FROM canonical_revisions WHERE state='OBSERVED_UNSELECTED_GRAPH_NOT_INSPECTED'"),
      'source_accepted_exact_per_revision_not_unique':scalar('SELECT COALESCE(SUM(source_accepted_exact),0) FROM canonical_revisions'),
      'source_accepted_reviewed_per_revision_not_unique':scalar('SELECT COALESCE(SUM(source_accepted_reviewed),0) FROM canonical_revisions'),
      'distinct_accepted_exact_across_revisions_source_only':scalar('''SELECT COUNT(*) FROM (
        SELECT kristal,namespace_id,semantic_id,wikidata_id FROM canonical_crosswalk_evidence
        WHERE source_status='accepted' AND relation='exactMatch'
        GROUP BY kristal,namespace_id,semantic_id,wikidata_id)'''),
      'cross_revision_accepted_conflicts':scalar('''SELECT COUNT(*) FROM (
        SELECT kristal,namespace_id,semantic_id FROM canonical_crosswalk_evidence
        WHERE source_status='accepted' AND relation='exactMatch'
        GROUP BY kristal,namespace_id,semantic_id HAVING COUNT(DISTINCT wikidata_id)>1)'''),
      'selected_revisions':0,
      'new_global_approvals':0,
    }


def query(directory: Path, *, namespace: str|None=None, semantic_id: str|None=None,
          wikidata_id: str|None=None, limit: int=100) -> dict:
    """Search *unselected source evidence* without changing the approved view."""
    if not 1<=limit<=500:raise ValueError('invalid query limit')
    local=namespace is not None or semantic_id is not None
    if local==(wikidata_id is not None):raise ValueError('use full local key OR Wikidata Q/P')
    if local and (not namespace or not isinstance(semantic_id,str) or not LOCAL.fullmatch(semantic_id)):
        raise ValueError('namespace and KQ/KP required')
    if not local and (not isinstance(wikidata_id,str) or not QPID.fullmatch(wikidata_id)):
        raise ValueError('invalid Wikidata Q/P')
    from .federated_registry import audit
    manifest=audit(directory)
    if (manifest.get('canonical_v11') or {}).get('profile')!='dik.canonical-v11-revision-evidence/0.1':
        raise ValueError('canonical V11 evidence unavailable in this registry')
    dbpath=Path(directory)/manifest['sqlite_file']
    with sqlite3.connect(f'{dbpath.resolve().as_uri()}?mode=ro&immutable=1',uri=True) as db:
        db.row_factory=sqlite3.Row
        if local:
            sql='''SELECT kristal,revision_dir,namespace_id,semantic_id,wikidata_id,relation,
              source_status,evidence_status,review_decision_id FROM canonical_crosswalk_evidence
              WHERE namespace_id=? AND semantic_id=? ORDER BY kristal,revision_dir,wikidata_id LIMIT ?'''
            results=list(db.execute(sql,(namespace,semantic_id,limit+1)))
        else:
            sql='''SELECT kristal,revision_dir,namespace_id,semantic_id,wikidata_id,relation,
              source_status,evidence_status,review_decision_id FROM canonical_crosswalk_evidence
              WHERE wikidata_id=? ORDER BY kristal,revision_dir,semantic_id LIMIT ?'''
            results=list(db.execute(sql,(wikidata_id,limit+1)))
    return {'profile':'dik.canonical-v11-revision-evidence/0.1',
            'status':'UNSELECTED_SOURCE_EVIDENCE_NOT_AUTHORIZED',
            'approved_for_publication':False,
            'results':[dict(r) for r in results[:limit]],'truncated':len(results)>limit}
