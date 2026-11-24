"""diK V5.3: conservative, resumable JSONL inspection of referenced Wikidata sources.

This is an OBSERVATION pipeline, NOT a source of published semantic labels.
Never infer a KQ/KP <-> Q/P mapping, a language, a label or a license. Raw
third-party files are read-only; checkpoint state stays under diK/reports.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Iterable

from .resource_locator import _unsafe
from .source_qualification import _verified_pointer
from .wikidata_json_array import ArraySyntaxError, iter_objects, peek_array

QP = re.compile(r"^[QP][1-9][0-9]*$")
WIKIDATA_URL = re.compile(r"^https?://www\.wikidata\.org/entity/(Q[1-9][0-9]*)$")
SEMANTIC = re.compile(r"^K[QP][1-9][0-9]*$")
LOCALE = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")
ADAPTER_VERSION = 'dik.wikidata-local-adapters/5.5.0'
CHECKPOINT_VERSION = 'dik.wikidata-checkpoint/5.5.0'
REPORT_VERSION = 'dik.wikidata-thematic-diagnostics/5.5.0'
MAX_JSON_LINE = 2_000_000  # raw bytes; special-case oversized lines without allocation
PROFILE_ROWS = 128


def _json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                   separators=(',', ':')).encode('utf-8')).hexdigest()


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _explicit_label(value: Any, locale: str) -> str | None:
    """Strictly labels, never descriptions, aliases, claims, lemmas, or other languages."""
    if isinstance(value, dict):
        if set(value) - {'value', 'language'}:
            return None
        if 'language' in value and value['language'] != locale:
            return None
        value = value.get('value')
    if isinstance(value, str) and 0 < len(value.strip()) <= 10_000:
        return value.strip()
    return None


def _locale_labels(obj: Any) -> bool:
    return isinstance(obj, dict) and bool(obj) and all(
        isinstance(k, str) and LOCALE.fullmatch(k) and
        _explicit_label(v, k) is not None for k, v in obj.items())


def _qp(value: Any) -> str | None:
    return value if isinstance(value, str) and QP.fullmatch(value) else None


def _typed_id(value: Any) -> str | None:
    if isinstance(value, dict) and set(value).issubset({'id','type','entity-type','numeric-id'}):
        return _qp(value.get('id'))
    return _qp(value)


def recognize(row: Any) -> tuple[str, list[dict]]:
    """A whitelist of structurally evidenced shapes; no recursive Q/P search.

    The statement/candidate adapters yield typed non-lexical observations.
    Unknown schemas must be profiled locally, not silently treated as absent.
    """
    if not isinstance(row, dict):
        return 'non_object', []
    if len(row) == 1:
        key, val = next(iter(row.items()))
        if _qp(key) and _locale_labels(val):
            return 'qp_keyed_locales/1', [dict(qp=key, role='lexical_entity',
                     field_path='$.'+key, labels=val, lexical=True)]
    # The four supplied gf-wikidata-tools/*.jsonl are actually pretty-printed
    # JSON ARRAYS, not JSONL. Each object has an entity URL and explicit labels.
    # Descriptions are NEVER lexical evidence. Missing/null locale values are
    # fine. Preserve original language tags (notably 'jp' is NOT 'ja').
    if set(('url', 'labels', 'descriptions')).issubset(row):
        url = row.get('url')
        match = WIKIDATA_URL.fullmatch(url) if isinstance(url,str) else None
        labels = row.get('labels')
        if (match and isinstance(labels,dict) and labels and
            all(isinstance(k,str) and LOCALE.fullmatch(k) and
                (v is None or isinstance(v,str) and len(v) <= 10_000)
                for k,v in labels.items()) and
            isinstance(row.get('descriptions'),dict)):
            return 'wikidata_entity_url_labels/1', [dict(
                qp=match.group(1), role='lexical_entity', field_path='$.url',
                labels=labels, lexical=True)]
        return 'schema_unknown', []
    entity = _qp(row.get('qid')) or _qp(row.get('id'))
    if entity and _locale_labels(row.get('labels')):
        key = 'qid' if row.get('qid') == entity else 'id'
        return 'id_labels/1', [dict(qp=entity, role='lexical_entity',
                 field_path='$.'+key, labels=row['labels'], lexical=True)]
    # Statements have distinct roles and are NEVER a lexicon on their own.
    if all(k in row for k in ('subject', 'predicate', 'object')):
        extracted = []
        for field, role in (('subject','entity_subject'),('predicate','property_predicate'),
                            ('object','entity_object')):
            value = _typed_id(row[field])
            if value and (field != 'predicate' or value.startswith('P')):
                extracted.append(dict(qp=value, role=role, field_path='$.'+field,
                                      labels={}, lexical=False))
        if extracted:
            return 'statement_triple/1', extracted
        return 'statement_triple/1', []
    # Local Kristal identity-candidates.jsonl: documented field names from
    # the V5.3 Windows schema report. This is NOT an accepted v11 crosswalk.
    # Require a namespace, an explicit KQ/KP, and a typed matching external Q/P.
    if all(k in row for k in ('semantic_id','external_id','namespace','identity_status','reason')):
        kid, ns = row['semantic_id'], row['namespace']
        external = _typed_id(row['external_id'])
        if (isinstance(kid,str) and SEMANTIC.fullmatch(kid) and
            isinstance(ns,str) and bool(ns.strip()) and len(ns)<=512 and
            external and kid[1]==external[0]):
            claimed = row.get('identity_status')
            claimed = claimed if isinstance(claimed,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,50}',claimed) else 'unparsed'
            return 'local_identity_candidate/1', [dict(
                qp=external, role='crosswalk_candidate', field_path='$.external_id',
                namespace=ns, semantic_id=kid, claimed_status=claimed,
                labels={}, lexical=False)]
        return 'local_identity_candidate/1', []
    # Thematic Wikidata statements have specific role-qualified subject/property
    # fields. They are factual assertions, never a lexicon or a crosswalk.
    if all(k in row for k in ('wikidata_subject','wikidata_property',
                                'semantic_subject_candidates','semantic_property_candidates','evidence')):
        result=[]
        subject=_typed_id(row['wikidata_subject'])
        prop=_typed_id(row['wikidata_property'])
        if subject and subject.startswith('Q'):
            result.append(dict(qp=subject, role='entity_subject',
                               field_path='$.wikidata_subject', labels={}, lexical=False))
        if prop and prop.startswith('P'):
            result.append(dict(qp=prop, role='property_predicate',
                               field_path='$.wikidata_property', labels={}, lexical=False))
        # Semantic candidate fields and evidence are intentionally NOT traversed.
        return 'local_wikidata_statement/1', result
    # Other candidate formats: remain proposals, never automatic identity links.
    if any(k in row for k in ('local_id', 'semantic_id', 'candidate_status', 'confidence')):
        key = next((k for k in ('candidate_qid','wikidata_qid','qid') if _qp(row.get(k))), None)
        if key is not None:
            return 'identity_candidate/1', [dict(qp=row[key], role='crosswalk_candidate',
                     field_path='$.'+key, labels={}, lexical=False)]
    # Standalone entities with no certified lexical field are still typed.
    if entity and not any(k in row for k in ('subject','predicate','object')):
        key = 'qid' if row.get('qid') == entity else 'id'
        return 'entity_id_only/1', [dict(qp=entity, role='entity_subject',
                 field_path='$.'+key, labels={}, lexical=False)]
    return 'schema_unknown', []


def _safe_fields(row: Any) -> list[str]:
    """Types/field names only: do not leak raw data into a report."""
    if not isinstance(row, dict):
        return [type(row).__name__]
    return sorted(str(x)[:90] for x in list(row)[:30])


def probe(path: Path, *, lines: int = PROFILE_ROWS) -> dict:
    """Bounded probe; only a CONSERVATIVE schema hint, not an absence claim."""
    types = collections.Counter()
    fields = collections.Counter()
    parsed = 0
    errors = 0
    container = 'json_array' if peek_array(path) else 'jsonl'
    with path.open('rb') as stream:
        if container == 'json_array':
            records = iter_objects(stream, max_item_bytes=MAX_JSON_LINE)
            for _ in range(lines):
                try:
                    row = next(records).obj
                except StopIteration:
                    break
                except (ArraySyntaxError, UnicodeError, ValueError):
                    errors += 1
                    break
                parsed += 1
                typ, _ = recognize(row)
                types[typ] += 1
                for field in _safe_fields(row):
                    fields[field] += 1
        else:
            for n in range(1, lines + 1):
                raw = stream.readline(MAX_JSON_LINE + 2)
                if not raw:
                    break
                if len(raw) > MAX_JSON_LINE:
                    while raw and not raw.endswith(b'\n'):
                        raw = stream.readline(MAX_JSON_LINE + 2)
                    errors += 1
                    continue
                if not raw.strip():
                    continue
                try:
                    row = json.loads(raw.decode('utf-8-sig' if n == 1 else 'utf-8'))
                except (UnicodeError, ValueError):
                    errors += 1
                    continue
                parsed += 1
                typ, _ = recognize(row)
                types[typ] += 1
                for field in _safe_fields(row):
                    fields[field] += 1
    known = {k: v for k, v in types.items() if k not in ('schema_unknown','non_object')}
    # Mixed recognised structures are inherently ambiguous until reviewed.
    if not known:
        status, schema = 'schema_unknown', ''
    elif len(known) != 1:
        status, schema = 'schema_ambiguous', ''
    elif max(known.values()) != parsed or errors:
        status, schema = 'schema_ambiguous', ''
    else:
        status, schema = 'schema_verified', next(iter(known))
    return {'status':status, 'schema_id':schema, 'container':container, 'profile_rows':parsed,
            'profile_errors':errors, 'shapes':dict(sorted(types.items())),
            'top_level_fields':dict(fields.most_common(30)),
            'adapter_version':ADAPTER_VERSION,
            'evidence':'types_et_chemins_explicitement_observes;pas_de_conclusion_absence_sur_echantillon'}


def _state_init(token: str, profile: dict) -> dict:
    return {'token': token, 'schema_id': profile['schema_id'], 'offset': 0,
            'line_next': 1, 'lines_read': 0, 'bytes_read': 0,
            'rows_valid_json': 0, 'rows_matching_schema': 0,
            'rows_with_qp': 0, 'rows_matching_accepted_qp': 0,
            'rows_with_label': 0, 'eligible_subject_rows': 0, 'malformed_json': 0, 'invalid_utf8': 0,
            'oversized_rows': 0, 'schema_mismatches': 0,
            'status': 'not_started', 'completed': False}


def _safe_workdir(folder: Path) -> Path:
    if not folder.is_absolute() or _unsafe(folder):
        raise ValueError('Dossier checkpoint invalide')
    if not folder.is_dir():
        folder.mkdir(parents=True, exist_ok=True)
    if _unsafe(folder):
        raise ValueError('Dossier checkpoint lie par jonction/symlink')
    return folder


def _db_open(db_path: Path, *, token: str, profile: dict) -> tuple[sqlite3.Connection, dict, bool]:
    if db_path.is_symlink():
        raise ValueError('Checkpoint symbolique interdit')
    conn = sqlite3.connect(str(db_path), timeout=45)
    try:
        conn.execute('PRAGMA synchronous=FULL')
        conn.execute('PRAGMA journal_mode=DELETE')
        conn.execute('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        conn.execute('CREATE TABLE IF NOT EXISTS ids (qp TEXT PRIMARY KEY)')
        conn.execute('''CREATE TABLE IF NOT EXISTS overlaps (
            qp TEXT NOT NULL, role TEXT NOT NULL, field_path TEXT NOT NULL,
            offset_bytes INTEGER NOT NULL, line INTEGER NOT NULL,
            PRIMARY KEY(qp,role,field_path,offset_bytes))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS nonlexical_hits (
            qp TEXT NOT NULL, role TEXT NOT NULL, field_path TEXT NOT NULL,
            line INTEGER NOT NULL, offset_bytes INTEGER NOT NULL,
            PRIMARY KEY(qp,role,field_path))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS candidate_links (
            namespace TEXT NOT NULL, semantic_id TEXT NOT NULL, qp TEXT NOT NULL,
            claimed_status TEXT NOT NULL, line INTEGER NOT NULL, offset_bytes INTEGER NOT NULL,
            PRIMARY KEY(namespace,semantic_id,qp,line,offset_bytes))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS forms (
            qp TEXT NOT NULL, locale TEXT NOT NULL, form TEXT NOT NULL,
            role TEXT NOT NULL, field_path TEXT NOT NULL,
            offset_bytes INTEGER NOT NULL, line INTEGER NOT NULL,
            PRIMARY KEY(qp,locale,form,field_path,offset_bytes))''')
        prior = conn.execute('SELECT value FROM meta WHERE key="state"').fetchone()
        reused = prior is not None
        if reused:
            state = json.loads(prior[0])
            if state.get('token') != token or state.get('schema_id') != profile['schema_id']:
                conn.close()
                # Treat a checkpoint for a changed policy/accepted-index as obsolete.
                db_path.unlink()
                db_path.with_suffix('.checkpoint.json').unlink(missing_ok=True)
                return _db_open(db_path, token=token, profile=profile)
        else:
            state = _state_init(token, profile)
            conn.execute('INSERT INTO meta VALUES (?,?)', ('state', json.dumps(state)))
            conn.commit()
        return conn, state, reused
    except Exception:
        conn.close()
        raise


def _commit(conn: sqlite3.Connection, state: dict) -> None:
    conn.execute('INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)',
                 ('state',json.dumps(state,sort_keys=True)))
    conn.commit()


def _status(state: dict, *, ids: int, overlaps: int, forms: int, conflicts: int) -> str:
    if state.get('status') in ('partial_budget','stale_source','incomplete_errors'):
        return state['status']
    if state['schema_mismatches'] or state['malformed_json'] or state['invalid_utf8'] or state['oversized_rows']:
        return 'completed_with_rejections' if state['completed'] else 'incomplete_errors'
    if not ids:
        return 'schema_verified_no_qp_extracted'
    if state.get('eligible_subject_rows', 0) == 0:
        return 'no_eligible_lexical_identity'
    if not overlaps:
        return 'complete_no_accepted_qp_overlap' if state['completed'] else 'partial_budget'
    if conflicts:
        return 'conflict'
    if forms:
        return 'candidate_labels_observed'
    return 'complete_overlap_no_lexical_field'


def _atomic_checkpoint(path: Path, record: dict) -> None:
    # The SQLite transaction is the source of truth. JSON is a human-readable copy.
    fd, name = tempfile.mkstemp(prefix='.checkpoint-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(record, out, ensure_ascii=False, sort_keys=True, indent=2)
            out.write('\n')
            out.flush(); os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def scan_file(record: dict, *, wanted: set[str], locales: tuple[str, ...],
              checkpoint_dir: Path, max_rows_per_pass: int = 0,
              max_bytes_per_pass: int = 0, max_pairs: int = 40000,
              max_source_bytes: int = 256 * 1024 * 1024,
              accepted_links: dict[tuple[str,str],str] | None = None) -> tuple[list[dict], list[dict], dict]:
    """A deterministic single pass (or a resumable bounded segment) over one source.

    Offsets are byte offsets, including BOM and an unterminated last line.
    A transaction includes both row evidence and the next offset, so a crash
    cannot create an orphaned observation or lose a position on retry.
    """
    profile_row = {'source_id':record.get('source_id',''),
                   'sha256':record.get('sha256',''), 'path':record.get('path',''),
                   'candidate_only':True, 'activations':0}
    try:
        path, reason = _verified_pointer(record, max_bytes=max_source_bytes)
    except (ValueError, OSError, TypeError, KeyError):
        path, reason = None, 'invalid_pointer'
    if path is None:
        profile_row.update(status={'introuvable':'pointer_missing','empreinte_modifiee':'pointer_stale',
                              'taille_modifiee':'pointer_stale','empreinte_absente':'hash_unverified',
                              'depasse_limite_verification':'hash_unverified'}.get(reason, reason),
                           reason=reason, completed=False)
        return [], [], profile_row
    if path.stat().st_size == 0:
        profile_row.update(status='empty_source',schema_id='',completed=True,
                           reason='fichier_vide;aucune_identite_extrait',
                           candidate_links_count=0, candidate_link_evidence=[])
        return [], [], profile_row
    info = probe(path)
    profile_row.update(info)
    if info['status'] != 'schema_verified':
        # Never claim "no overlap" without a verified adapter.
        profile_row.update(completed=False, reason='profilage_non_suffisant')
        return [], [], profile_row
    _safe_workdir(checkpoint_dir)
    digest = str(record['sha256']).lower()
    token = _json_sha({'version':CHECKPOINT_VERSION,'adapter':ADAPTER_VERSION,
                       'sha256':digest, 'container':info['container'], 'size':path.stat().st_size,
                       'source_id':record['source_id'],'schema':info['schema_id'],
                       'wanted':sorted(wanted),'locales':list(locales),
                       'accepted_links':sorted((ns,kid,qp) for (ns,kid),qp in (accepted_links or {}).items()),
                       'max_json_line':MAX_JSON_LINE})
    name = hashlib.sha256((record['source_id']+'\x00'+digest).encode()).hexdigest()[:28]
    db_path = checkpoint_dir/(name+'.sqlite3')
    conn, state, was_resumed = _db_open(db_path, token=token, profile=info)
    seen_this_pass = 0
    read_this_pass = 0
    try:
        # A changed file after initial preflight invalidates the entire persisted checkpoint.
        if _digest(path) != digest or path.stat().st_size != record['size_bytes']:
            state['status'] = 'stale_source'
            profile_row.update(status='stale_source', completed=False, reason='change_before_read')
            return [], [], profile_row
        if not state['completed']:
            state['status'] = 'running'
            with path.open('rb') as stream:
                array_mode = info['container'] == 'json_array'
                if array_mode:
                    rows = iter_objects(stream, offset=state['offset'],
                                        line=state['line_next'], max_item_bytes=MAX_JSON_LINE)
                else:
                    stream.seek(state['offset'])
                while True:
                    if max_rows_per_pass and seen_this_pass >= max_rows_per_pass:
                        state['status']='partial_budget'; break
                    if max_bytes_per_pass and read_this_pass >= max_bytes_per_pass:
                        state['status']='partial_budget'; break
                    if array_mode:
                        try:
                            record_item = next(rows)
                        except StopIteration:
                            state['status']='completed';state['completed']=True
                            break
                        except (ArraySyntaxError, UnicodeError, ValueError):
                            state['malformed_json'] += 1
                            state['status']='incomplete_errors'
                            break
                        start, end, obj = record_item.start, record_item.end, record_item.obj
                        record_line, next_line = record_item.line, record_item.next_line
                        ok = True
                    else:
                        start = stream.tell()
                        raw = stream.readline(MAX_JSON_LINE + 2)
                        if not raw:
                            state['status']='completed';state['completed']=True
                            break
                        if len(raw) > MAX_JSON_LINE:
                            while raw and not raw.endswith(b'\n'):
                                raw = stream.readline(MAX_JSON_LINE + 2)
                            state['oversized_rows']+=1
                            end=stream.tell()
                            state['line_next']+=1
                            state['offset']=end
                            state['lines_read']+=1
                            state['bytes_read']+=end-start
                            seen_this_pass+=1; read_this_pass+=end-start
                            if state['oversized_rows'] > 1000:
                                state['status']='incomplete_errors';break
                            if seen_this_pass % 1000 == 0:_commit(conn,state)
                            continue
                        ok=True
                        try:
                            obj=json.loads(raw.decode('utf-8-sig' if state['line_next']==1 else 'utf-8'))
                        except UnicodeError:
                            state['invalid_utf8']+=1;obj=None;ok=False
                        except ValueError:
                            state['malformed_json']+=1;obj=None;ok=False
                        end=stream.tell()
                        record_line=state['line_next']
                        next_line=record_line+1
                    if ok:
                        shape, extracted = recognize(obj)
                        proposed = []
                        if shape == state['schema_id']:
                            for item in extracted:
                                if item['qp'] not in wanted or not item['lexical']:
                                    continue
                                for locale in locales:
                                    value = _explicit_label(item['labels'].get(locale), locale)
                                    if value is not None:
                                        proposed.append((item['qp'],locale,value,item['role'],
                                                         item['field_path']+'.'+locale,start,record_line))
                        # Preserve the line boundary and all counters if this row
                        # exceeds the observation budget. Retry it on next pass.
                        current_count = conn.execute('SELECT COUNT(*) FROM forms').fetchone()[0]
                        if current_count + len(proposed) > max_pairs:
                            state['status']='partial_budget'
                            break
                        # Candidate identities are also bounded: otherwise a
                        # large unreviewed JSONL could fill memory and reports.
                        local_candidates=[x for x in extracted if x['role']=='crosswalk_candidate'
                                          and x.get('semantic_id')]
                        if local_candidates:
                            candidate_count=conn.execute('SELECT COUNT(*) FROM candidate_links').fetchone()[0]
                            if candidate_count + len(local_candidates) > max_pairs:
                                state['status']='partial_budget'
                                break
                        state['rows_valid_json'] += 1
                        if shape != state['schema_id']:
                            state['schema_mismatches'] += 1
                        else:
                            state['rows_matching_schema'] += 1
                            if extracted:
                                state['rows_with_qp'] += 1
                            matched = False
                            eligible = False
                            for item in extracted:
                                qp = item['qp']
                                conn.execute('INSERT OR IGNORE INTO ids(qp) VALUES(?)', (qp,))
                                if qp in wanted and item['role'] not in ('lexical_entity','entity_subject'):
                                    conn.execute('INSERT OR IGNORE INTO nonlexical_hits VALUES(?,?,?,?,?)',
                                        (qp,item['role'],item['field_path'],record_line,start))
                                if item['role']=='crosswalk_candidate' and item.get('semantic_id'):
                                    conn.execute('INSERT OR IGNORE INTO candidate_links VALUES (?,?,?,?,?,?)',
                                        (item['namespace'],item['semantic_id'],qp,
                                         item['claimed_status'],record_line,start))
                                # A statement predicate/object, or a proposed
                                # crosswalk, cannot define the lexical identity.
                                if item['role'] not in ('entity_subject','lexical_entity'):
                                    continue
                                eligible = True
                                if qp not in wanted:
                                    continue
                                matched = True
                                conn.execute('INSERT OR IGNORE INTO overlaps VALUES(?,?,?,?,?)',
                                             (qp,item['role'],item['field_path'],start,record_line))
                            if eligible: state['eligible_subject_rows'] += 1
                            for values in proposed:
                                conn.execute('INSERT OR IGNORE INTO forms VALUES(?,?,?,?,?,?,?)', values)
                            if matched: state['rows_matching_accepted_qp'] += 1
                            if proposed: state['rows_with_label'] += 1
                    state['offset']=end
                    state['line_next']=next_line
                    state['lines_read']+=1
                    state['bytes_read']+=end-start
                    seen_this_pass+=1
                    read_this_pass+=end-start
                    if seen_this_pass % 1000 == 0:
                        _commit(conn,state)
                    if state['status']=='partial_budget':break
                    if sum(state[k] for k in ('malformed_json','invalid_utf8','oversized_rows','schema_mismatches')) > 1000:
                        state['status']='incomplete_errors';break
        _commit(conn,state)
        # Verify again: a concurrent write during the scan must not be accepted.
        if _digest(path)!=digest or path.stat().st_size!=record['size_bytes']:
            state['status']='stale_source';state['completed']=False
            _commit(conn,state)
            profile_row.update(status='stale_source',completed=False,reason='change_during_scan')
            return [], [], profile_row
        ids = conn.execute('SELECT COUNT(*) FROM ids').fetchone()[0]
        overlaps = conn.execute('SELECT COUNT(DISTINCT qp) FROM overlaps').fetchone()[0]
        forms = conn.execute('SELECT COUNT(*) FROM forms').fetchone()[0]
        conflicts = conn.execute('''SELECT COUNT(*) FROM (
          SELECT qp,locale FROM forms GROUP BY qp,locale HAVING COUNT(DISTINCT form)>1)''').fetchone()[0]
        candidate_links = []
        for ns,kid,qp,claimed,line,offset in conn.execute('''SELECT namespace,semantic_id,qp,
                claimed_status,line,offset_bytes FROM candidate_links ORDER BY namespace,semantic_id,qp,line'''):
            expected=(accepted_links or {}).get((ns,kid))
            comparison=('consistent_with_existing_accepted' if expected==qp else
                        'contradicts_existing_accepted' if expected else 'no_existing_accepted')
            candidate_links.append(dict(namespace_id=ns,semantic_id=kid,external_id=qp,
                source_claimed_status=claimed,comparison=comparison,
                official_accepted_qp=expected or '',source_id=record['source_id'],
                source_sha256=digest,line=line,offset_bytes=offset))
        nonlexical_hits=[dict(qp=qp, role=role, field_path=field_path,
                              line=line,offset_bytes=offset,source_id=record['source_id'],
                              sha256=digest,candidate_only=True)
            for qp,role,field_path,line,offset in conn.execute('''SELECT qp,role,field_path,
                line,offset_bytes FROM nonlexical_hits ORDER BY qp,role''')]
        status = _status(state, ids=ids, overlaps=overlaps, forms=forms, conflicts=conflicts)
        profile_row.update({**{k:v for k,v in state.items() if k!='token'},
                            'status':status,'schema_id':info['schema_id'],
                            'candidate_links_count':len(candidate_links),
                            'nonlexical_accepted_qp_distinct':len({x['qp'] for x in nonlexical_hits}),
                            'nonlexical_accepted_qp_evidence':nonlexical_hits,
                            'candidate_link_evidence':candidate_links,
                            'candidate_links_consistent':sum(x['comparison']=='consistent_with_existing_accepted' for x in candidate_links),
                            'candidate_links_contradictory':sum(x['comparison']=='contradicts_existing_accepted' for x in candidate_links),
                            'distinct_qp':ids,'distinct_qp_matching_accepted':overlaps,
                            'explicit_labels_for_accepted_qp':forms,
                            'conflicts_within_source':conflicts,'resumed':was_resumed,
                            'checkpoint_ref':str(db_path),
                            'reason':'checkpoint_conserve_sous_dik_reports',
                            'adapter_version':ADAPTER_VERSION})
        # Observations are already bounded by max_pairs and joined to accepted Q/P.
        evidence = [dict(qp=r[0], locale=r[1], form=r[2], role=r[3],
                         field_path=r[4], offset_bytes=r[5], line=r[6],
                         source_id=record['source_id'],sha256=digest,
                         status='candidate_unpublished', candidate_only=True)
                    for r in conn.execute('SELECT qp,locale,form,role,field_path,offset_bytes,line FROM forms ORDER BY qp,locale,line')]
        overlapped = [dict(qp=r[0], role=r[1], field_path=r[2],
                           offset_bytes=r[3], line=r[4],source_id=record['source_id'],sha256=digest)
                      for r in conn.execute('SELECT qp,role,field_path,offset_bytes,line FROM overlaps ORDER BY qp,line')]
        _atomic_checkpoint(db_path.with_suffix('.checkpoint.json'),{
             'profile':CHECKPOINT_VERSION,'source_id':record['source_id'],
             'sha256':digest,'schema_id':info['schema_id'], 'container':info['container'],
             'adapter_version':ADAPTER_VERSION,'offset_bytes_next':state['offset'],
             'line_next':state['line_next'],'status':status,
             'completed':state['completed'],'candidate_only':True,'activations':0})
        return evidence, overlapped, profile_row
    finally:
        conn.close()


def observe_thematic_v53(registry: dict, *, wanted: set[str], locales: tuple[str, ...],
                         checkpoint_dir: Path, max_rows_per_pass: int = 0,
                         accepted_links: dict[tuple[str,str],str] | None = None,
                         max_bytes_per_pass: int = 0, max_pairs: int = 40000) -> tuple[dict, list[dict], dict, list[dict]]:
    """Scan thematic sources; preserve V5.2 observer interface plus overlap evidence."""
    if len(set(locales)) != 14 or len(locales) != 14:
        raise ValueError('V5.3 exige les 14 locales exactes du projet')
    from .scan14 import TARGET_LOCALES
    if tuple(locales) != tuple(TARGET_LOCALES):
        raise ValueError('Ordre et codes de locales non officiels')
    if max_rows_per_pass < 0 or max_bytes_per_pass < 0 or not 1 <= max_pairs <= 1_000_000:
        raise ValueError('Budgets incorrects')
    candidates = [s for s in registry.get('sources',[]) if s.get('kind')=='wikidata_thematic_candidate']
    profiles: list[dict] = []
    grouped: dict[tuple[str,str],list[dict]] = collections.defaultdict(list)
    overlaps: list[dict] = []
    seen: dict[str,str] = {}
    for entry in candidates:
        digest = entry.get('sha256') or ''
        if digest and digest in seen:
            profiles.append({'source_id':entry.get('source_id',''), 'sha256':digest,
                             'path':entry.get('path',''), 'status':'same_bytes_as_prior_source',
                             'identical_to_source_id':seen[digest], 'candidate_only':True,
                             'completed':False, 'activations':0})
            continue
        evidence, hits, row = scan_file(entry,wanted=wanted,locales=locales,
                                        checkpoint_dir=checkpoint_dir,
                                        max_rows_per_pass=max_rows_per_pass,
                                        max_bytes_per_pass=max_bytes_per_pass,max_pairs=max_pairs,
                                        accepted_links=accepted_links)
        if row.get('status') not in ('pointer_missing','pointer_stale','hash_unverified',
                                     'invalid_pointer','hors_racine','lien_ou_jonction'):
            if digest:
                seen[digest] = entry['source_id']
        profiles.append(row)
        overlaps.extend(hits)
        for item in evidence:
            grouped[(item['qp'],item['locale'])].append(item)
    conflicted = {key for key, values in grouped.items()
                  if len({x['form'] for x in values})>1}
    for key, values in grouped.items():
        for value in values:
            value['status'] = 'conflict' if key in conflicted else 'candidate_unpublished'
    incomplete = sum(x.get('status') in ('partial_budget','incomplete_errors','schema_unknown',
                                        'schema_ambiguous','pointer_missing','pointer_stale',
                                        'hash_unverified','stale_source','completed_with_rejections')
                     for x in profiles)
    summary = {
        'profile':REPORT_VERSION,'status':'PARTIAL' if incomplete else 'TRIAGE_ONLY',
        'candidate_only':True,'activations':0,'sources_registered':len(candidates),
        'sources_inspected':sum(bool(x.get('schema_id')) for x in profiles),
        'sources_completed':sum(bool(x.get('completed')) for x in profiles),
        'sources_schema_unknown':sum(x.get('status') in ('schema_unknown','schema_ambiguous') for x in profiles),
        'sources_incomplete':incomplete,
        'identical_copies_skipped':sum(x['status']=='same_bytes_as_prior_source' for x in profiles),
        'rows_valid_json':sum(x.get('rows_valid_json',0) for x in profiles),
        'rows_with_qp':sum(x.get('rows_with_qp',0) for x in profiles),
        'qp_overlapping_accepted_crosswalk':len({x['qp'] for x in overlaps}),
        'explicit_labels_observed':sum(len(x) for x in grouped.values()),
        'candidate_pairs_with_accepted_qp':len(grouped),
        'candidate_forms':sum(map(len,grouped.values())),
        'nonlexical_qp_observations':sum(len(x.get('nonlexical_accepted_qp_evidence',())) for x in profiles),
        'candidate_identity_links':sum(x.get('candidate_links_count',0) for x in profiles),
        'candidate_identity_links_consistent':sum(x.get('candidate_links_consistent',0) for x in profiles),
        'candidate_identity_links_contradictory':sum(x.get('candidate_links_contradictory',0) for x in profiles),
        'statement_sources_completed':sum(x.get('completed') and x.get('schema_id')=='local_wikidata_statement/1' for x in profiles),
        'conflicting_pairs':len(conflicted),
        'locales_exact':list(locales),
        'scope':'Observation candidate, aucun mapping implicite, aucune traduction',
    }
    return grouped, profiles, summary, overlaps
