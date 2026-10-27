"""Schema checked append-only review journal, not a canonical crosswalk writer."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from jsonschema import Draft202012Validator

from .operations import DiKError, Project
from ._framework import dictionaries as fw

SCHEMA=Path(__file__).with_name('contracts')/'dik-review-decision.schema.json'


def canonical_json(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


def validate_decision(decision:dict, project:Project):
    schema=json.loads(SCHEMA.read_text(encoding='utf-8'))
    errors=sorted(Draft202012Validator(schema).iter_errors(decision),key=lambda x: list(map(str,x.path)))
    if errors: raise DiKError('Invalid review decision: '+errors[0].message)
    graph=fw.read_json(project.graph)
    registry=fw.read_json(project.registry)
    ids={x['id']:x['kind'] for x in registry['identities']}
    target=decision['target']
    if target['namespace_id']!=graph['namespace_id']:
        raise DiKError('INVALID_NAMESPACE')
    if ids.get(target['id']) != ('entity' if target['kind']=='KQ' else 'property'):
        raise DiKError('Target reference is unregistered or wrong kind')
    if decision['status']=='accepted':
        if not decision.get('reviewer_id') or decision.get('reviewer_id')==decision['actor_id']:
            raise DiKError('UNAUTHORIZED_MIGRATION: independent reviewer required')
        if any(ids.get(e)!='source' for e in decision['evidence_refs']):
            raise DiKError('UNVERIFIED_ALIGNMENT: KS evidence not registered')
        if decision.get('mapping_kind')=='external_alignment' and decision['relation']!='exactMatch':
            # Non-exact relations may be approved as RELATED observations, but never substitutes.
            pass
    if decision['input_manifest_sha256']!=fw.sha256(project.manifest):
        raise DiKError('STALE_SOURCE: manifest digest mismatch')


def journal_records(path:Path)->list[dict]:
    path=Path(path)
    if not path.exists(): return []
    previous='0'*64
    result=[]
    for n,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        try: item=json.loads(line)
        except json.JSONDecodeError as e: raise DiKError(f'Corrupt journal line {n}') from e
        if item.get('previous_hash')!=previous or item.get('hash')!=digest({k:v for k,v in item.items() if k!='hash'}):
            raise DiKError('INTEGRITY_MISMATCH: review journal broken at line '+str(n))
        previous=item['hash'];result.append(item)
    return result


def append_review(path:Path,decision:dict,project:Project)->dict:
    """Exclusive file lock on POSIX, no writes on Windows without safe locking.

    One journal = one revision stream. Prevent duplicates, rollback, and active
    double exact alignment. This is an event log, NOT human authorization itself.
    """
    validate_decision(decision,project)
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    # Portable no-clobber lock; unexpected crash leaves explicit recovery responsibility.
    lock=path.with_name(path.name+'.lock')
    try: fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError as e: raise DiKError('Concurrent review writer; lock already held') from e
    os.close(fd)
    try:
        events=journal_records(path)
        old=[e['decision'] for e in events]
        if any(d['decision_id']==decision['decision_id'] for d in old):
            existing=next(d for d in old if d['decision_id']==decision['decision_id'])
            if existing==decision:
                return {'status':'already_recorded','decision_id':decision['decision_id']}
            raise DiKError('IDEMPOTENCY_CONFLICT: decision_id is already recorded')
        prevs=[d for d in old if d['target']==decision['target'] and d['candidate']==decision['candidate']]
        if prevs:
            if decision['revision']<=max(d['revision'] for d in prevs):
                raise DiKError('Review revision must increase monotonically')
            last=max(prevs,key=lambda d:d['revision'])
            allowed={
                'proposed':{'in_review','accepted','rejected'},
                'in_review':{'accepted','rejected'},
                'accepted':{'superseded'},'rejected':{'proposed'},'superseded':{'proposed'}
            }
            if decision['status'] not in allowed.get(last['status'],set()):
                raise DiKError('Invalid review status transition')
        if decision['mapping_kind']=='external_alignment' and decision['status']=='accepted' and decision['relation']=='exactMatch':
            for d in old:
                if d['status']!='accepted' or d['mapping_kind']!='external_alignment' or d['relation']!='exactMatch':continue
                if any(s.get('status')=='superseded' and s.get('supersedes')==d['decision_id'] for s in old): continue
                if d['target']==decision['target'] or (d['candidate']['source_system']==decision['candidate']['source_system'] and d['candidate']['source_record_id']==decision['candidate']['source_record_id']):
                    raise DiKError('UNVERIFIED_ALIGNMENT: duplicate active exact mapping')
        item={'previous_hash':events[-1]['hash'] if events else '0'*64, 'decision':decision}
        item['hash']=digest(item)
        # append+fsync, verify on next read. No concurrent writers allowed under this lock.
        with path.open('a',encoding='utf-8',newline='\n') as stream:
            stream.write(canonical_json(item)+'\n');stream.flush();os.fsync(stream.fileno())
        return {'status':'recorded','decision_id':decision['decision_id'],'journal_hash':item['hash']}
    finally:
        lock.unlink(missing_ok=True)
