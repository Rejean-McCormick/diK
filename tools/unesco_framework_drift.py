"""Read-only compare diK's draft.3 vendored-origin SHAs to the Framework draft.4 pin.

This is *source compatibility evidence*, not a claim of runtime conformance,
dictionary approval, 14-language coverage, or canonical-authoring authority.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import sys

class DriftError(ValueError):pass

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda:fh.read(2**20),b''):h.update(chunk)
    return h.hexdigest()

def inspect(*,framework:Path,diK:Path,integration_pack:Path):
    fw=(framework/'VERSION').read_text(encoding='utf8').strip() if (framework/'VERSION').is_file() else None
    src=json.loads((diK/'FRAMEWORK-SOURCE-SHA256.json').read_text(encoding='utf8'))
    pin=json.loads((integration_pack/'contracts'/'v11-framework-pin.json').read_text(encoding='utf8'))
    if src.get('contract')!='11.0.0-draft.3' or pin.get('version')!='11.0.0-draft.4':
        raise DriftError('Expected declared draft.3 -> draft.4 source comparison')
    if not isinstance(pin.get('files'),dict):raise DriftError('Pinned files absent')
    pinned=[]; mismatched=[]
    for rel,digest in pin['files'].items():
        if not isinstance(rel,str) or rel.startswith('/') or '..' in Path(rel).parts:
            raise DriftError('Unsafe pin path')
        p=framework/rel
        actual=file_sha(p) if p.is_file() else None
        pinned.append({'path':rel,'matches_pin':actual==digest})
        if actual!=digest:mismatched.append(rel)
    if fw!=pin['version']:mismatched.append('VERSION_METADATA')
    lineage=[]
    for item in src['files']:
        rel=item['upstream']
        if not isinstance(rel,str) or rel.startswith('/') or '..' in Path(rel).parts:
            raise DriftError('Unsafe diK lineage path')
        p=framework/rel
        actual=file_sha(p) if p.is_file() else None
        expected=item.get('upstream_sha256') or item.get('vendored_sha256')
        lineage.append({'path':rel,'same_upstream_source':actual==expected,'origin_draft':'11.0.0-draft.3',
                        'destination_draft':'11.0.0-draft.4','vendored_adaptation':not item.get('identical',False)})
    same=all(i['same_upstream_source'] for i in lineage)
    pinned_ok=not mismatched
    return {'format':'dik.unesco-framework-drift/1.0','source_contract':'11.0.0-draft.3',
            'framework_version':fw,'pinned_framework_verified':pinned_ok,
            'upstream_source_unchanged_for_dik_subset':same,
            'source_files_compared':len(lineage),'source_files_matched':sum(i['same_upstream_source'] for i in lineage),
            'pinned_files_compared':len(pinned),'pinned_files_matched':sum(i['matches_pin'] for i in pinned),
            'mismatches':mismatched,'lineage':lineage,
            'runtime_compatibility_qualified':False,'canonical_mutation_authorized':False,
            'public_release_authorized':False,
            'status':'SOURCE_COMPATIBLE_RUNTIME_UNQUALIFIED' if pinned_ok and same else 'BLOCKED_SOURCE_DRIFT'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--framework',type=Path,required=True);p.add_argument('--dik',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--integration-pack',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        d=inspect(framework=a.framework,diK=a.dik,integration_pack=a.integration_pack)
        print(json.dumps(d,ensure_ascii=False,indent=2));return 0 if d['pinned_framework_verified'] and d['upstream_source_unchanged_for_dik_subset'] else 2
    except (DriftError,FileNotFoundError,ValueError,KeyError) as e:
        print(json.dumps({'status':'BLOCKED','error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
