"""Bounded-memory Wikidata import with transactional checkpoints (alpha.7).

Snapshot files and KQ/KP mappings are never modified.  Resume of raw JSON(L)
uses checked byte offsets; compressed inputs resume by replaying to the saved line.
A SQLite staging database is *derived*, and is never the published source of truth.
"""
from __future__ import annotations

import bz2
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
from pathlib import Path

from . import FRAMEWORK_CONTRACT
from .operations import DiKError
from ._framework import dictionaries as fw

FORMAT = 'dik.large-import/1.0-candidate'
TRANSFORM = 'wikidata-large-import-1.0.0-alpha.7'
SAFE_NAME = re.compile(r'[A-Za-z0-9._-]+\Z')


def _compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _hash_text(value):
    return hashlib.sha256(_compact(value).encode('utf-8')).hexdigest()


def _open_source(path):
    suffix = path.suffix.lower()
    if suffix == '.gz':
        return gzip.open(path, 'rb')
    if suffix == '.bz2':
        return bz2.open(path, 'rb')
    return path.open('rb')


def _read_source(path, *, start_line, start_offset, max_line_bytes):
    """Yield (physical line number, next uncompressed offset or 0, raw bytes).

    Does not claim random access to bzip2/gzip compressed streams.
    """
    compressed = path.suffix.lower() in ('.gz', '.bz2')
    with _open_source(path) as f:
        if not compressed:
            f.seek(start_offset)
        line = 0 if compressed else start_line
        while True:
            raw = f.readline(max_line_bytes + 1)
            if not raw:
                break
            if len(raw) > max_line_bytes:
                raise DiKError('ENTITY_LINE_TOO_LARGE')
            line += 1
            if compressed and line <= start_line:
                continue
            yield line, 0 if compressed else f.tell(), raw
        if compressed and line < start_line:
            raise DiKError('CHECKPOINT_BEYOND_EOF')


def _validate_registry(crosswalk, registry, namespace):
    reg = fw.read_json(registry)
    fw.check_schema(reg, 'kristal-identity-registry.schema.json')
    if reg['namespace_id'] != namespace:
        raise DiKError('REGISTRY_NAMESPACE_MISMATCH')
    xwalk = fw.read_json(crosswalk)
    accepted, _ = fw.accepted_exact(xwalk, namespace)
    kinds = {r['id']: r['kind'] for r in reg['identities']}
    for mapping in xwalk['mappings']:
        if mapping['status'] == 'accepted' and mapping['local_ref']['namespace_id'] == namespace:
            if any(kinds.get(proof) != 'source' for proof in mapping['review']['evidence_refs']):
                raise DiKError('CROSSWALK_EVIDENCE_MISSING')
    for external, local in accepted.items():
        if kinds.get(local) != ('entity' if external.startswith('Q') else 'property'):
            raise DiKError('CROSSWALK_IDENTITY_KIND_MISMATCH')
    return accepted


def _init_db(db):
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('CREATE TABLE IF NOT EXISTS words (lang TEXT NOT NULL, kid TEXT NOT NULL, record TEXT NOT NULL, PRIMARY KEY(lang, kid)) WITHOUT ROWID')
    db.execute('CREATE TABLE IF NOT EXISTS checkpoint (id INTEGER PRIMARY KEY CHECK (id=1), line INTEGER NOT NULL, pos INTEGER NOT NULL, scanned INTEGER NOT NULL, matched INTEGER NOT NULL, mode TEXT NOT NULL, closed INTEGER NOT NULL)')
    db.execute("INSERT OR IGNORE INTO checkpoint VALUES (1,0,0,0,0,'unknown',0)")
    db.commit()


def _checkpoint(db):
    return db.execute('SELECT line,pos,scanned,matched,mode,closed FROM checkpoint WHERE id=1').fetchone()


def _commit_chunk(db, *, line, pos, scanned, matched, mode, closed):
    db.execute('UPDATE checkpoint SET line=?,pos=?,scanned=?,matched=?,mode=?,closed=? WHERE id=1',
               (line,pos,scanned,matched,mode,int(closed)))
    db.commit()


def _verify_published(final, expected_key):
    manifest_file = final / 'dik-job.json'
    catfile = final / 'catalog.json'
    if not manifest_file.is_file() or not catfile.is_file() or final.is_symlink():
        raise DiKError('IDEMPOTENCY_CONFLICT: incomplete or untrusted published snapshot')
    marker = fw.read_json(manifest_file)
    if marker.get('profile') != FORMAT or marker.get('idempotency_key') != expected_key:
        raise DiKError('IDEMPOTENCY_CONFLICT: different source or transform')
    if fw.sha256(catfile) != marker.get('catalog_sha256'):
        raise DiKError('INTEGRITY_MISMATCH: catalog changed')
    catalog = fw.read_json(catfile)
    fw.check_schema(catalog, 'kristal-dictionary-catalog.schema.json')
    for lang in catalog['languages']:
        for layer in lang['layers']:
            path = fw.safe_file(final, layer['path'])
            if fw.sha256(path) != layer['sha256']:
                raise DiKError('INTEGRITY_MISMATCH: lexical layer changed')
    return {'status':'already_published', 'catalog': str(catfile),
            'idempotency_key': expected_key, 'entities_scanned': marker['entities_scanned'],
            'accepted_exact_entities_seen': marker['accepted_exact_entities_seen'],
            'labels_by_locale': marker['labels_by_locale']}


def import_large(*, dump: Path, crosswalk: Path, registry: Path, namespace: str,
                 snapshot: str, locales: list[str], root: Path, batch_lines: int = 5000,
                 max_line_bytes: int = 128 * 1024 * 1024,
                 approved_sha256: str | None = None,
                 _stop_after_lines: int | None = None) -> dict:
    """Import selectively using constant-size chunks and an on-disk index.

    The underscored injection point is for interruption testing only.
    A crash leaves the stage SQLite database to be resumed on the next run.
    """
    if not isinstance(snapshot, str) or not SAFE_NAME.fullmatch(snapshot) or snapshot in ('.','..'):
        raise DiKError('INVALID_SNAPSHOT_ID')
    if batch_lines < 1 or batch_lines > 1_000_000 or max_line_bytes < 1024:
        raise DiKError('INVALID_RESOURCE_LIMIT')
    if not locales or any(not isinstance(x,str) or not x for x in locales) or len(set(locales)) != len(locales):
        raise DiKError('INVALID_LANGUAGES')
    locales = list(locales)
    for loc in locales:
        fw.check_locale(loc)
    dump, crosswalk, registry = (Path(x).resolve() for x in (dump,crosswalk,registry))
    if not dump.is_file() or not crosswalk.is_file() or not registry.is_file():
        raise DiKError('MISSING_INPUT')
    accepted = _validate_registry(crosswalk, registry, namespace)
    # Streaming digest ensures a resumable stage cannot silently accept different bytes.
    dump_sha = fw.sha256(dump)
    if approved_sha256 is not None:
        if not re.fullmatch(r'[0-9a-fA-F]{64}', approved_sha256) or dump_sha != approved_sha256.lower():
            raise DiKError('APPROVED_SHA256_MISMATCH')
    pins = {'dump_sha256': dump_sha, 'upstream_verified':approved_sha256 is not None, 'crosswalk_sha256': fw.sha256(crosswalk),
            'registry_sha256': fw.sha256(registry), 'namespace': namespace,
            'snapshot': snapshot, 'locales': locales, 'transform': TRANSFORM}
    key = _hash_text(pins)
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    final = root / key
    if final.exists():
        return _verify_published(final, key)
    stage = root / ('.dik-large-' + key)
    lock = root / ('.lock-large-' + key)
    try:
        with lock.open('x',encoding='utf-8') as f:
            f.write(f'pid={os.getpid()}\n')
            f.flush(); os.fsync(f.fileno())
    except FileExistsError as e:
        raise DiKError('SNAPSHOT_BUSY: verify no importer is running before removing a stale lock') from e
    try:
        if final.exists():
            return _verify_published(final, key)
        if stage.is_symlink():
            raise DiKError('UNTRUSTED_STAGE_SYMLINK')
        stage.mkdir(exist_ok=True)
        pins_file = stage / 'source-pins.json'
        if pins_file.exists():
            if fw.read_json(pins_file) != pins:
                raise DiKError('STAGE_PINS_MISMATCH')
        else:
            # Stage metadata created exclusively, no silent takeover of foreign contents.
            if any(stage.iterdir()):
                raise DiKError('UNRECOGNIZED_STAGE')
            with pins_file.open('x',encoding='utf-8') as dest:
                dest.write(json.dumps(pins,sort_keys=True,indent=2)+'\n')
                dest.flush();os.fsync(dest.fileno())
        db = sqlite3.connect(str(stage/'progress.sqlite'),timeout=1.0)
        try:
            _init_db(db)
            old_line,pos,scanned,matched,mode,closed = _checkpoint(db)
            if closed:
                # Finalization may have been interrupted: replay output from the sealed index.
                pass
            else:
                pending = 0
                last_line, last_pos = old_line, pos
                for line_no, off, raw in _read_source(dump,start_line=old_line,start_offset=pos,max_line_bytes=max_line_bytes):
                    last_line,last_pos = line_no,off
                    try:
                        text = raw.decode('utf-8').strip()
                    except UnicodeDecodeError as e:
                        raise DiKError('INVALID_UTF8_DUMP') from e
                    if not text:
                        continue
                    if mode == 'closed':
                        raise DiKError('TRAILING_DATA_AFTER_ARRAY')
                    if text == '[':
                        if mode != 'unknown':raise DiKError('UNEXPECTED_ARRAY_OPEN')
                        mode = 'array'
                    elif text == ']':
                        if mode != 'array':raise DiKError('UNEXPECTED_ARRAY_CLOSE')
                        mode = 'closed'
                    else:
                        if mode == 'unknown': mode = 'jsonl'
                        if text.endswith(',') and mode == 'array':text=text[:-1].rstrip()
                        try:
                            entity = json.loads(text)
                        except ValueError as e:
                            raise DiKError(f'INVALID_DUMP_ENTITY at line {line_no}: {e}') from e
                        if not isinstance(entity,dict) or not isinstance(entity.get('id'),str):
                            raise DiKError(f'INVALID_DUMP_ENTITY at line {line_no}')
                        scanned += 1
                        kid = accepted.get(entity['id'])
                        if kid:
                            matched += 1
                            for loc in locales:
                                record = fw.make_import_record(entity,kid,loc,namespace,snapshot)
                                if record is not None:
                                    try:
                                        db.execute('INSERT INTO words VALUES (?,?,?)',
                                            (loc,kid,_compact(record)))
                                    except sqlite3.IntegrityError as e:
                                        raise DiKError(f'DUPLICATE_ENTITY: {loc}/{kid}') from e
                    pending += 1
                    if pending >= batch_lines:
                        _commit_chunk(db,line=last_line,pos=last_pos,scanned=scanned,
                                      matched=matched,mode=mode,closed=False)
                        pending=0
                    if _stop_after_lines is not None and line_no >= _stop_after_lines:
                        # Simulate abrupt interruption after the last durable checkpoint.
                        db.rollback()
                        raise DiKError('SIMULATED_INTERRUPTION')
                if mode == 'array':
                    db.rollback()
                    raise DiKError('TRUNCATED_ARRAY_DUMP')
                if mode == 'unknown':
                    db.rollback()
                    raise DiKError('EMPTY_DUMP')
                _commit_chunk(db,line=last_line,pos=last_pos,scanned=scanned,
                              matched=matched,mode=mode,closed=True)
            if fw.sha256(dump) != dump_sha:
                raise DiKError('SOURCE_CHANGED_DURING_IMPORT')
            # Publishing is also restartable. No graph/crosswalk is mutated.
            artifact = stage / 'artifact'
            if artifact.exists():
                shutil.rmtree(artifact)
            artifact.mkdir()
            counts={}
            languages=[]
            for loc in locales:
                rel=f'imported/wikidata/{snapshot}/{loc}.jsonl'
                target=artifact/rel
                target.parent.mkdir(parents=True,exist_ok=True)
                n=0
                with target.open('x',encoding='utf-8',newline='\n') as out:
                    for (payload,) in db.execute('SELECT record FROM words WHERE lang=? ORDER BY kid',(loc,)):
                        out.write(payload+'\n');n+=1
                    out.flush(); os.fsync(out.fileno())
                counts[loc]=n
                languages.append({'tag':loc, 'fallbacks':[], 'layers':[{
                   'layer_id':f'wikidata-{snapshot}-{loc}', 'kind':'wikidata',
                   'priority':100,'path':rel,'sha256':fw.sha256(target),'source_snapshot':snapshot}]})
            catalog={'schema_version':'11.0','artifact_type':'kristal_dictionary_catalog',
                     'catalog_id':f'wikidata-import-{snapshot}', 'namespace_id':namespace,
                     'languages':languages}
            fw.check_schema(catalog,'kristal-dictionary-catalog.schema.json')
            catfile = artifact/'catalog.json'
            with catfile.open('x',encoding='utf-8') as out:
                out.write(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
                out.flush();os.fsync(out.fileno())
            marker={'profile':FORMAT,'idempotency_key':key,'source_pins':pins,
                    'catalog_sha256':fw.sha256(catfile),'entities_scanned':scanned,
                    'accepted_exact_entities_seen':matched,'labels_by_locale':counts,
                    'framework_contract':FRAMEWORK_CONTRACT,
                    'upstream_verified': approved_sha256 is not None}
            with (artifact/'dik-job.json').open('x',encoding='utf-8') as out:
                out.write(json.dumps(marker,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
                out.flush();os.fsync(out.fileno())
            if final.exists():
                raise DiKError('OUTPUT_EXISTS')
            os.rename(artifact,final)
        finally:
            db.close()
        shutil.rmtree(stage)
        return {'status':'published','catalog':str(final/'catalog.json'),
                'idempotency_key':key, 'entities_scanned':scanned,
                'accepted_exact_entities_seen':matched,'labels_by_locale':counts,
                'upstream_verified': approved_sha256 is not None,
                'restart_strategy': 'byte-offset' if dump.suffix.lower() not in ('.gz','.bz2') else 'replay-to-line',
                'warning':'Accepted exact Wikidata correspondences only; no implicit equivalences. Local checksum alone is not source attestation.'}
    finally:
        lock.unlink(missing_ok=True)
