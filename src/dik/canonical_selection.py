"""V5.11: fail-closed, read-only *derived-view* selection of canonical V11 revisions.

The Framework canonical index declares all its artifacts, not an active revision.
A singleton may be used as a sole declared source for a derived lookup; multiple
revisions require an explicit, input-hash-pinned review decision. This NEVER
establishes Framework authority or approves a new Wikidata equivalence.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sqlite3

PROFILE = 'dik.canonical-revision-selection/0.1'
LEGACY_DECISIONS_PROFILE = 'dik.canonical-selection-decisions/0.1'
DECISIONS_PROFILE = 'dik.canonical-selection-decisions/0.2'
HEX = re.compile(r'^[0-9a-f]{64}$')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _valid_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 500


def read_decisions(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ValueError('selection decisions unavailable, symlinked or too large')
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(data, dict) and data.get('profile') == LEGACY_DECISIONS_PROFILE:
        raise ValueError('legacy 0.1 selection decisions lack graph_sha256; re-review against exact graph bytes using profile 0.2')
    if not isinstance(data, dict) or data.get('profile') != DECISIONS_PROFILE or data.get('scope') != 'derived_view_only':
        raise ValueError('selection decisions profile/scope invalid')
    entries = data.get('decisions')
    if not isinstance(entries, list) or len(entries) > 126:
        raise ValueError('selection decisions must be a bounded list')
    decisions = {}
    expected = {'kristal', 'revision_dir', 'state_index_sha256', 'registry_sha256',
                'crosswalk_sha256', 'graph_sha256', 'catalog_sha256',
                'review_decision_id', 'reviewer', 'rationale'}
    for record in entries:
        if not isinstance(record, dict) or set(record) != expected:
            raise ValueError('selection decision missing or unexpected fields')
        if not all(_valid_text(record.get(k)) for k in ('kristal','revision_dir','review_decision_id','reviewer','rationale')):
            raise ValueError('selection decision requires an identified reviewer and reason')
        if len(record['review_decision_id']) < 6 or len(record['rationale'].strip()) < 12:
            raise ValueError('selection decision lacks sufficiently precise review metadata')
        if not all(isinstance(record[k],str) and HEX.fullmatch(record[k]) for k in
                   ('state_index_sha256','registry_sha256','crosswalk_sha256','graph_sha256','catalog_sha256')):
            raise ValueError('selection decision hashes invalid')
        name=record['kristal']
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*',name) or name in decisions:
            raise ValueError('duplicate/invalid Kristal in selection decisions')
        decisions[name] = record
    return decisions


def _evidence_signature(db: sqlite3.Connection, kristal: str, revision: str) -> str:
    """Compare both identity and crosswalk *observations*, not graph semantics."""
    h = hashlib.sha256()
    for table, fields in [
        ('canonical_identity_evidence','namespace_id,semantic_id,kind,source_status,label,definition'),
        ('canonical_crosswalk_evidence','namespace_id,semantic_id,wikidata_id,relation,source_status,evidence_status,review_decision_id,evidence_refs_json')
    ]:
        h.update((table+'\0').encode())
        query=f'SELECT {fields} FROM {table} WHERE kristal=? AND revision_dir=? ORDER BY {fields}'
        for row in db.execute(query,(kristal,revision)):
            h.update(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode('utf-8')+b'\n')
    return h.hexdigest()


def _usable(rev: dict, digests: dict) -> bool:
    return (rev['state'] == 'OBSERVED_UNSELECTED' and digests is not None
            and digests['graph_state'] == 'INSPECTED'
            and all(digests[k] is not None for k in
                    ('state_index_sha256','registry_sha256','crosswalk_sha256','catalog_sha256','graph_sha256')))


def ingest(db: sqlite3.Connection, *, decisions_file: Path | None=None) -> dict:
    """Record explicit selection states while keeping V5.9 approvals unchanged."""
    decisions=read_decisions(decisions_file)
    db.executescript('''
      CREATE TABLE canonical_selection (
        kristal TEXT PRIMARY KEY, decision TEXT NOT NULL,
        selected_revision_dir TEXT, review_decision_id TEXT,
        reason_code TEXT NOT NULL, selected_source_exact INTEGER NOT NULL,
        source_authority_confirmed INTEGER NOT NULL DEFAULT 0,
        globally_approved_new_links INTEGER NOT NULL DEFAULT 0);
      CREATE INDEX canonical_sel_decision ON canonical_selection(decision);
    ''')
    sources=[r[0] for r in db.execute('SELECT kristal FROM canonical_sources ORDER BY kristal')]
    source_set=set(sources)
    for stray in decisions.keys()-source_set:
        raise ValueError('selection decision names a nonofficial Kristal: '+stray)
    for name in sources:
        rows=[dict(zip(('revision_dir','state','source_accepted_exact','issue'),r)) for r in db.execute(
            'SELECT revision_dir,state,source_accepted_exact,issue FROM canonical_revisions WHERE kristal=? ORDER BY revision_dir',(name,))]
        inputs={r[0]:dict(zip(('state_index_sha256','registry_sha256','crosswalk_sha256','graph_sha256','catalog_sha256','graph_state'),r[1:]))
                for r in db.execute('''SELECT revision_dir,state_index_sha256,registry_sha256,crosswalk_sha256,
                   graph_sha256,catalog_sha256,graph_state FROM canonical_revision_inputs WHERE kristal=?''',(name,))}
        selected=None;decision_id=None;count=0
        # A source revision containing contradictory accepted Q/P for one ID
        # must never become a chosen view, even as a singleton.
        conflicts={r[0] for r in db.execute("""SELECT revision_dir FROM canonical_crosswalk_evidence
            WHERE kristal=? AND source_status='accepted' AND relation='exactMatch'
            GROUP BY revision_dir,namespace_id,semantic_id
            HAVING COUNT(DISTINCT wikidata_id)>1""",(name,))}
        def eligible(r):
            return _usable(r,inputs.get(r['revision_dir'])) and r['revision_dir'] not in conflicts
        if not rows:
            state,reason='NO_V11_REVISION','NO_SOURCE_REVISION'
        elif name in decisions:
            entry=decisions[name]
            if entry['revision_dir'] not in {r['revision_dir'] for r in rows}:
                raise ValueError('review decision targets missing revision: '+name)
            candidate=next(r for r in rows if r['revision_dir']==entry['revision_dir'])
            dig=inputs.get(candidate['revision_dir'])
            if not eligible(candidate):
                raise ValueError('review decision targets unverified/incomplete revision: '+name)
            for input_key,expected in [('state_index_sha256','state_index_sha256'),('registry_sha256','registry_sha256'),
                                       ('crosswalk_sha256','crosswalk_sha256'),('graph_sha256','graph_sha256'),
                                       ('catalog_sha256','catalog_sha256')]:
                if dig[input_key]!=entry[expected]:
                    raise ValueError('review decision stale, source changed: '+name)
            selected=candidate['revision_dir'];decision_id=entry['review_decision_id']
            state,reason='OPERATOR_PINNED_DERIVED_VIEW','EXPLICIT_REVIEW_WITH_PINNED_SHA256_NOT_FRAMEWORK_AUTHORITY'
            count=candidate['source_accepted_exact']
        elif len(rows)==1:
            candidate=rows[0]
            if eligible(candidate):
                selected=candidate['revision_dir'];count=candidate['source_accepted_exact']
                state,reason='SINGLE_DECLARED_DERIVED_VIEW','ONLY_COMPLETE_V11_REVISION_IN_SOURCE_INDEX'
            else:
                state,reason='SINGLE_REVISION_NOT_VERIFIED','INCOMPLETE_OR_GRAPH_UNINSPECTED'
        else:
            signatures={_evidence_signature(db,name,r['revision_dir']) for r in rows if eligible(r)}
            if len(signatures)==1 and all(eligible(r) for r in rows):
                state,reason='MULTIPLE_EQUIVALENT_EVIDENCE_UNSELECTED','NO_EXPLICIT_AUTHORITY_EVEN_IF_LEXICAL_EVIDENCE_SAME'
            elif not all(eligible(r) for r in rows):
                state,reason='MULTIPLE_INCOMPLETE_UNSELECTED','SOURCE_REVISION_UNREADABLE_OR_GRAPH_UNINSPECTED'
            else:
                state,reason='MULTIPLE_DIVERGENT_UNSELECTED','REQUIRES_EXPLICIT_REVIEW_AND_PINNED_SHA256'
        db.execute('INSERT INTO canonical_selection VALUES (?,?,?,?,?,?,?,?)',
                   (name,state,selected,decision_id,reason,count,0,0))
    scalar=lambda sql:db.execute(sql).fetchone()[0]
    return {
        'official_kristals':len(sources),
        'single_declared_view_revisions':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='SINGLE_DECLARED_DERIVED_VIEW'"),
        'operator_pinned_view_revisions':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='OPERATOR_PINNED_DERIVED_VIEW'"),
        'multiple_divergent_unselected':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='MULTIPLE_DIVERGENT_UNSELECTED'"),
        'multiple_equivalent_evidence_unselected':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='MULTIPLE_EQUIVALENT_EVIDENCE_UNSELECTED'"),
        'multiple_incomplete_unselected':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='MULTIPLE_INCOMPLETE_UNSELECTED'"),
        'single_unverified':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='SINGLE_REVISION_NOT_VERIFIED'"),
        'no_v11_revision':scalar("SELECT COUNT(*) FROM canonical_selection WHERE decision='NO_V11_REVISION'"),
        'selected_source_exact_per_view_not_global_approval':scalar('SELECT COALESCE(SUM(selected_source_exact),0) FROM canonical_selection'),
        'framework_authority_confirmed':0,
        'new_global_approvals':0,
        'published_dictionaries':0,
    }


def query(directory: Path, *, namespace: str | None=None, semantic_id: str | None=None,
          wikidata_id: str | None=None, limit: int=100) -> dict:
    """Look up only pinned/singleton revisions, explicitly NOT globally approved."""
    from .canonical_v11 import LOCAL,QPID
    from .federated_registry import audit
    if not 1 <= limit <= 500:
        raise ValueError('invalid query limit')
    local=namespace is not None or semantic_id is not None
    if local == (wikidata_id is not None):
        raise ValueError('require complete namespace+KQ/KP OR Wikidata Q/P')
    if local and (not isinstance(namespace,str) or not namespace or not isinstance(semantic_id,str) or not LOCAL.fullmatch(semantic_id)):
        raise ValueError('namespace and KQ/KP required')
    if not local and (not isinstance(wikidata_id,str) or not QPID.fullmatch(wikidata_id)):
        raise ValueError('invalid Wikidata ID')
    manifest=audit(directory)
    if (manifest.get('canonical_selection') or {}).get('profile') != PROFILE:
        raise ValueError('V5.11 selection not present')
    dbpath=Path(directory)/manifest['sqlite_file']
    with sqlite3.connect(f'{dbpath.resolve().as_uri()}?mode=ro&immutable=1',uri=True) as db:
        db.row_factory=sqlite3.Row
        sql='''SELECT c.kristal,c.revision_dir,c.namespace_id,c.semantic_id,c.wikidata_id,
                   c.relation,c.source_status,c.evidence_status,s.decision,s.review_decision_id
               FROM canonical_crosswalk_evidence c JOIN canonical_selection s
               ON c.kristal=s.kristal AND c.revision_dir=s.selected_revision_dir'''
        if local:
            cond='WHERE c.namespace_id=? AND c.semantic_id=?'; params=(namespace,semantic_id,limit+1)
        else:
            cond='WHERE c.wikidata_id=?';params=(wikidata_id,limit+1)
        results=list(db.execute(sql+' '+cond+' ORDER BY c.kristal,c.semantic_id,c.wikidata_id LIMIT ?',params))
    local_collision=local and len({r['kristal'] for r in results})>1
    return {'profile':PROFILE,'status':('AMBIGUOUS_NAMESPACE_LOCAL_KEY_NOT_MERGED' if local_collision
               else 'SELECTED_DERIVED_SOURCE_EVIDENCE_NOT_CANONICAL_APPROVAL'),
            'approved_for_publication':False,'new_global_approvals':0,
            'results':[dict(x) for x in results[:limit]],'truncated':len(results)>limit}


def review_queue(directory: Path, output_file: Path) -> dict:
    """Write LOCAL options with source hashes; never nominate a winner."""
    from .federated_registry import audit
    manifest=audit(directory)
    if (manifest.get('canonical_selection') or {}).get('profile') != PROFILE:
        raise ValueError('V5.11 selection unavailable')
    output_file=Path(output_file)
    if output_file.exists() or output_file.is_symlink() or output_file.resolve().is_relative_to(Path(directory).resolve()):
        raise ValueError('review queue output exists or overlaps protected registry')
    dbfile=Path(directory)/manifest['sqlite_file']
    with sqlite3.connect(f'{dbfile.resolve().as_uri()}?mode=ro&immutable=1',uri=True) as db:
        db.row_factory=sqlite3.Row
        pending=[]
        for selected in db.execute('''SELECT kristal,decision,reason_code FROM canonical_selection
           WHERE selected_revision_dir IS NULL AND decision!='NO_V11_REVISION' ORDER BY kristal'''):
            versions=[]
            for rev in db.execute('''SELECT r.revision_dir,r.state,r.entity_kq,r.property_kp,
                      r.source_accepted_exact,i.state_index_sha256,i.registry_sha256,
                      i.crosswalk_sha256,i.graph_sha256,i.catalog_sha256,i.graph_state
                  FROM canonical_revisions r LEFT JOIN canonical_revision_inputs i
                    ON r.kristal=i.kristal AND r.revision_dir=i.revision_dir
                  WHERE r.kristal=? ORDER BY r.revision_dir''',(selected['kristal'],)):
                versions.append(dict(rev))
            pending.append({'kristal':selected['kristal'],'reason':selected['decision'],
                            'revisions':versions})
    document={'profile':'dik.canonical-selection-review-queue/0.1',
              'note':'This is NOT an authority decision or an approval; review outside this tool.',
              'selection_decisions_profile':DECISIONS_PROFILE,
              'pending':pending}
    output_file.parent.mkdir(parents=True,exist_ok=True)
    with output_file.open('x',encoding='utf-8') as fh:
        json.dump(document,fh,ensure_ascii=False,sort_keys=True,indent=2)
        fh.write('\n')
    return {'profile':document['profile'],'pending_kristals':len(pending),
            'output_file':str(output_file)}
