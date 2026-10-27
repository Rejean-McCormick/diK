"""Reviewed Wikidata mapping export to a NEW Framework v11 crosswalk revision.

A journal is operator-attested, not cryptographically authenticated. diK checks
schema, KS references and collisions; the user/producer must supply true review.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path

from .operations import Project,DiKError,write_new,serialize_json
from ._framework import dictionaries as fw
from .governance import journal_records,validate_decision


def publish_crosswalk(project:Project,journal:Path,output:Path,revision_id:str)->dict:
    if not re.fullmatch(r'[A-Za-z0-9._-]{1,100}',revision_id) or revision_id in ('.','..'):
        raise DiKError('Invalid crosswalk revision ID')
    events=journal_records(journal)
    old=fw.read_json(project.crosswalk)
    registry=fw.read_json(project.registry)
    ids={item['id']:item['kind'] for item in registry['identities']}
    result=copy.deepcopy(old)
    result['crosswalk_id']=old['crosswalk_id']+'-'+revision_id
    known={m['mapping_id'] for m in result['mappings']}
    revoked={e['decision']['supersedes'] for e in events if e['decision']['status']=='superseded'
             and 'supersedes' in e['decision']}
    added=[]
    for event in events:
        d=event['decision']
        if d['status']!='accepted' or d['relation']!='exactMatch' or d['mapping_kind']!='external_alignment' or d['decision_id'] in revoked:
            continue
        validate_decision(d,project)
        candidate=d['candidate'];kid=d['target']['id'];qid=candidate['source_record_id']
        if candidate['source_system']!='wikidata' or not re.fullmatch(r'[QP][1-9][0-9]*',qid):
            raise DiKError('Only valid Wikidata Q/P alignments exportable')
        if not ((kid.startswith('KQ') and qid.startswith('Q') and ids.get(kid)=='entity') or
                (kid.startswith('KP') and qid.startswith('P') and ids.get(kid)=='property')):
            raise DiKError('KQ/Q or KP/P kind mismatch')
        # Review based on old snapshot is not equivalent to verified crosswalk publication.
        mapping_id='dik-'+d['decision_id']
        if mapping_id in known:raise DiKError('Duplicate crosswalk mapping ID')
        known.add(mapping_id)
        result['mappings'].append({'mapping_id':mapping_id,
            'local_ref':{'namespace_id':d['target']['namespace_id'],'id':kid},
            'external_ref':{'system':'wikidata','id':qid},'relation':'exactMatch',
            'status':'accepted','review':{'method':'human',
                'decision_id':d['decision_id'],'evidence_refs':d['evidence_refs']}})
        added.append(mapping_id)
    fw.check_schema(result,'kristal-external-crosswalk.schema.json')
    fw.accepted_exact(result,registry['namespace_id'])
    write_new(output,serialize_json(result))
    return {'status':'published_new_crosswalk','path':str(output),'added':added,
        'source_sha256':fw.sha256(project.crosswalk),'output_sha256':fw.sha256(output),
        'old_crosswalk_unmodified':True,
        'notice':'Review identities are operator-attested, not cryptographically verified.'}
