"""Non-executable semantic conversion plans; old Kristals are NEVER edited.

The operator supplies the roles of exact JSON pointers. No guessing textual
fields / citations / prose. Only candidate recommendations are emitted.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from . import _framework
from ._framework import dictionaries as fw
from .operations import DiKError, Project
from .index import reverse_lookup


def pointer_value(root, pointer):
    if not isinstance(pointer,str) or not pointer.startswith('/') or pointer=='/':
        raise DiKError('Invalid JSON Pointer')
    parts=pointer[1:].split('/')
    value=root
    for segment in parts:
        if '~' in segment and (segment.replace('~1','').replace('~0','').find('~')>=0):
            raise DiKError('Invalid pointer escaping')
        key=segment.replace('~1','/').replace('~0','~')
        if isinstance(value,list):
            if not key.isdecimal() or (len(key)>1 and key[0]=='0') or int(key)>=len(value):
                raise DiKError('Pointer refers to missing list entry')
            value=value[int(key)]
        elif isinstance(value,dict) and key in value:
            value=value[key]
        else:raise DiKError('Pointer does not exist: '+pointer)
    return value


def conversion_candidates(project:Project, source:Path, index:Path,
                          roles:list[dict], *, locale:str, plan_id:str='proposal') -> dict:
    """Creates no false target IDs. Unresolved positions stay OUT of Framework plan."""
    fw.check_locale(locale)
    source=Path(source)
    doc=fw.read_json(source)
    reg=fw.read_json(project.registry)
    accepted={e['id']:e['kind'] for e in reg['identities']}
    catalog=fw.read_json(project.catalog)
    crosswalk=fw.read_json(project.crosswalk)
    operations=[]; unresolved=[]; seen=set()
    for n, role in enumerate(roles,1):
        path=role.get('source_path'); kind=role.get('semantic_role')
        if kind not in ('entity','property') or path in seen:
            raise DiKError('Roles must be unique explicit semantic entity/property pointers')
        seen.add(path)
        original=pointer_value(doc,path)
        if not isinstance(original,str) or not original:
            raise DiKError('Only nonempty semantic reference strings accepted')
        target_kind='KQ' if kind=='entity' else 'KP'
        if accepted.get(original)==kind:
            target=original; candidates=[original]
        else:
            lookup=reverse_lookup(project,index,term=original,locale=locale,kind=target_kind)
            candidates=[c['semantic_id'] for c in lookup['candidates']]
            target=candidates[0] if len(candidates)==1 and not lookup['truncated'] else None
        if not target:
            unresolved.append({'source_path':path,'original_value':original,'semantic_role':kind,
                               'candidate_ids':candidates, 'reason':'ambiguous' if candidates else 'no_candidate'})
            continue
        operations.append({'operation_id':f'candidate-{n}', 'source_path':path,
            'original_value':original,'semantic_role':kind,'target_id':target,
            'decision':{'status':'pending'}})
    plan={'schema_version':'11.0','artifact_type':'kristal_dik_conversion_plan','plan_id':plan_id,
          'namespace_id':catalog['namespace_id'],
          'source':{'artifact_id':str(doc.get('graph_id',source.name)), 'sha256':fw.sha256(source),
                    'declared_version':str(doc.get('schema_version','legacy'))},
          'catalog_id':catalog['catalog_id'],'crosswalk_id':crosswalk['crosswalk_id'],
          'operations':operations}
    fw.check_schema(plan,'kristal-dik-conversion-plan.schema.json')
    return {'plan':plan,'unresolved':unresolved,
            'warning':'NON-EXECUTABLE. A unique lexical candidate is not an approved identity.'}


def validate_plan_source(plan:dict,source:Path)->dict:
    fw.check_schema(plan,'kristal-dik-conversion-plan.schema.json')
    if fw.sha256(source)!=plan['source']['sha256']:
        raise DiKError('STALE_SOURCE: source bytes changed')
    doc=fw.read_json(source)
    for op in plan['operations']:
        if pointer_value(doc,op['source_path'])!=op['original_value']:
            raise DiKError('STALE_SOURCE: JSON pointer value changed')
    return {'source_verified':True,'all_approved':bool(plan['operations']) and all(
            op['decision']['status']=='approved' for op in plan['operations']),
            'mutation_permitted_by_dik':False}
