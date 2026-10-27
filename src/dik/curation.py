"""Write reviewed lexical corrections as a NEW immutable catalog snapshot.

Never edits the source catalog, imported Wikidata shards, canonical graph or crosswalk.
"""
from __future__ import annotations
import copy
import json
import os
import shutil
import tempfile
from pathlib import Path
from .operations import DiKError, Project
from ._framework import dictionaries as fw


def publish_preference(project:Project, *,semantic_id:str,locale:str,term:str,
      reviewer:str,decision_id:str,reason:str,destination:Path,priority:int=1000)->dict:
    if not all(isinstance(x,str) and x.strip() for x in (term,reviewer,decision_id,reason)):
        raise DiKError('Curated correction needs non-empty term, reviewer, decision and justification')
    if len(term)>4096:raise DiKError('Curated term exceeds size limit')
    fw.check_locale(locale)
    registry=fw.read_json(project.registry)
    if registry['namespace_id']!=fw.read_json(project.catalog)['namespace_id']:
        raise DiKError('INVALID_NAMESPACE')
    if semantic_id not in {x['id'] for x in registry['identities'] if x['kind'] in ('entity','property')}:
        raise DiKError('Unknown KQ/KP semantic identity')
    if not (201 <= priority <= 100000): raise DiKError('Curated priority must exceed imported default')
    fw.audit(project.catalog,project.crosswalk,project.registry)
    destination=Path(destination).resolve()
    if destination.exists(): raise DiKError('Destination immutable snapshot already exists')
    # Copy validated catalog and its declared shards only, no arbitrary files.
    catalog=fw.read_json(project.catalog)
    snapshot=copy.deepcopy(catalog)
    snapshot['catalog_id']=catalog['catalog_id']+'-curated-'+decision_id
    lang=next((x for x in snapshot['languages'] if x['tag']==locale),None)
    if lang is None:raise DiKError('UNDECLARED_LOCALE')
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.dik-curate-',dir=destination.parent))
    try:
        for language in snapshot['languages']:
            for layer in language['layers']:
                original=fw.safe_file(project.catalog.parent,layer['path'])
                target=staging/layer['path']
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(original,target)
                if fw.sha256(target)!=layer['sha256']:
                    raise DiKError('INTEGRITY_MISMATCH while copying dictionary')
        rel='curated/diK-'+decision_id+'-'+locale+'.json'
        if '/' in decision_id or '\\' in decision_id or decision_id in ('.','..') or not decision_id.replace('-','').replace('_','').isalnum():
            raise DiKError('Unsafe decision ID for filename')
        curated={'schema_version':'11.0','artifact_type':'kristal_curated_dictionary',
          'namespace_id':catalog['namespace_id'],'language':locale,
          'entries':[{'semantic_id':semantic_id,'preferred_term':term,
            'alternate_terms':[],'review':{'decision_id':decision_id,'reviewer':reviewer,'reason':reason}}]}
        fw.check_schema(curated,'kristal-curated-dictionary.schema.json')
        target=staging/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(curated,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if any(l['layer_id']=='dik-curated-'+decision_id for x in snapshot['languages'] for l in x['layers']):
            raise DiKError('Duplicate review decision in layers')
        lang['layers'].append({'layer_id':'dik-curated-'+decision_id,'kind':'curated','priority':priority,
                                  'path':rel,'sha256':fw.sha256(target)})
        fw.check_schema(snapshot,'kristal-dictionary-catalog.schema.json')
        (staging/'catalog.json').write_text(json.dumps(snapshot,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        fw.audit(staging/'catalog.json',project.crosswalk,project.registry)
        if destination.exists():raise DiKError('Destination appeared during staging')
        os.rename(staging,destination)
        return {'status':'published','catalog':str(destination/'catalog.json'),
            'catalog_sha256':fw.sha256(destination/'catalog.json'),'old_catalog_sha256':fw.sha256(project.catalog),
            'canonical_graph_unchanged':True}
    finally:
        if staging.exists():shutil.rmtree(staging)
