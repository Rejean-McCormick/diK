"""Multi-Kristal coverage by namespace and versioned catalog, never merging IDs blindly."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

from .operations import load_project, coverage_report, DiKError
from ._framework import dictionaries as fw

SCHEMA=Path(__file__).with_name('contracts')/'dik-portfolio-coverage.schema.json'


def portfolio_report(manifests:list[str|Path], locales:list[str], *, report_id='portfolio') -> dict:
    if not manifests or not locales or len(locales)!=len(set(locales)):
        raise DiKError('Provide projects and unique requested locales')
    for locale in locales:fw.check_locale(locale)
    details=[]; keys=set(); groups={}
    for manifest in manifests:
        project=load_project(manifest)
        data=coverage_report(project,locales=locales)
        identity=(data['namespace_id'],data['graph_id'])
        if identity in keys: raise DiKError('Duplicate (namespace,graph_id) in portfolio')
        keys.add(identity)
        group_key=(data['namespace_id'],data['catalog_id'],data['catalog_sha256'])
        as_bytes=json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
        groups.setdefault(group_key,[]).append({'namespace_id':data['namespace_id'],'graph_id':data['graph_id'],
            'graph_sha256':data['graph_sha256'],
            'framework_report_sha256':hashlib.sha256(as_bytes).hexdigest()})
        for row in data['locales']:
            details.append({'namespace_id':data['namespace_id'],'graph_id':data['graph_id'],
                'catalog_id':data['catalog_id'],'catalog_sha256':data['catalog_sha256'],
                'locale':row['tag'],'KQ':row['KQ'],'KP':row['KP'],
                'complete_direct':row['complete_direct'],'complete_usable':row['complete_usable']})
    schema=json.loads(SCHEMA.read_text(encoding='utf-8'))
    reports=[]
    for i,((namespace,catalog_id,catalog_hash),graph_reports) in enumerate(sorted(groups.items()),1):
        report={'contract_profile':'dik.portfolio-coverage/1.0-candidate',
            'report_id':report_id+'-group-'+str(i),'catalog_id':catalog_id,'catalog_sha256':catalog_hash,
            'requested_locales':locales,
            'graph_reports':sorted(graph_reports,key=lambda x:(x['namespace_id'],x['graph_id'])),
            'legacy_unresolved_graph_ids':[]}
        errors=list(Draft202012Validator(schema).iter_errors(report))
        if errors:raise DiKError('Portfolio schema invalid: '+errors[0].message)
        reports.append(report)
    return {'contract_profile':'dik.portfolio-bundle/1.0-alpha',
            'report':reports[0] if len(reports)==1 else None,
            'group_reports':reports,
            'matrix':sorted(details,key=lambda x:(x['namespace_id'],x['graph_id'],x['locale'])),
            'mixed_catalog_snapshots':len(groups)>1,
            'notes':'Counts per graph, grouped by namespace/catalog SHA. A cross-group average is not computed.'}
