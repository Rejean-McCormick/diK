"""Local Wikidata snapshot jobs; deterministic IDs, verified isolated publication."""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path

from . import __version__
from .operations import DiKError, import_wikidata_local
from ._framework import dictionaries as fw


def job_key(*, dump:Path,crosswalk:Path,registry:Path,namespace:str,snapshot:str,locales:list[str])->str:
    payload={'source_sha256':fw.sha256(dump),'crosswalk_sha256':fw.sha256(crosswalk),
        'registry_sha256':fw.sha256(registry),'namespace':namespace,'snapshot':snapshot,
        'locales':sorted(locales),'transform':'wikidata-import-local-v11-draft.3'}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def import_idempotent(*,dump:Path,crosswalk:Path,registry:Path,namespace:str,
                      snapshot:str,locales:list[str],root:Path)->dict:
    """A repeat with matching source hashes verifies the prior result, never overwrites it.

    This simple version does not attempt unvalidated resume inside a compressed dump.
    """
    root=Path(root).resolve()
    key=job_key(dump=dump,crosswalk=crosswalk,registry=registry,namespace=namespace,snapshot=snapshot,locales=locales)
    output=root/key
    if output.exists():
        expected=output/'catalog.json'
        marker=output/'dik-job.json'
        if not expected.is_file():
            raise DiKError('IDEMPOTENCY_CONFLICT: incomplete existing job')
        # Crash after catalog atomic publication but before job sidecar:
        # independently validate and recover derived metadata, never re-import.
        if not marker.is_file():
            catalog=fw.read_json(expected)
            if catalog.get('catalog_id')!='wikidata-import-'+snapshot:
                raise DiKError('IDEMPOTENCY_CONFLICT: unexpected existing catalog')
            fw.audit(expected,crosswalk,registry)
            # Source hash alone is insufficient to attest catalog bytes. Replay
            # the deterministic transformation into a private directory and
            # compare exact catalog + all declared shard hashes before repair.
            with tempfile.TemporaryDirectory(prefix='.dik-verify-recovery-',dir=root) as temp:
                fresh=Path(temp)/'recomputed'
                import_wikidata_local(dump=dump,crosswalk=crosswalk,registry=registry,
                    namespace=namespace,snapshot=snapshot,locales=locales,output=fresh)
                fresh_catalog=fw.read_json(fresh/'catalog.json')
                existing_catalog=fw.read_json(expected)
                if fresh_catalog != existing_catalog:
                    raise DiKError('INTEGRITY_MISMATCH: snapshot differs from source replay')
                for language in fresh_catalog['languages']:
                    for layer in language['layers']:
                        if fw.sha256(fw.safe_file(fresh,layer['path'])) != fw.sha256(fw.safe_file(output,layer['path'])):
                            raise DiKError('INTEGRITY_MISMATCH: snapshot layer differs from source replay')
            recovered={'idempotency_key':key,'source_sha256':fw.sha256(dump),
                       'catalog_sha256':fw.sha256(expected),
                       'transform':'wikidata-import-local-v11-draft.3',
                       'locales':sorted(locales)}
            try:
                with marker.open('x',encoding='utf-8') as dst:
                    dst.write(json.dumps(recovered,sort_keys=True,indent=2)+'\n')
                    dst.flush();os.fsync(dst.fileno())
            except FileExistsError:
                pass
        obj=fw.read_json(marker)
        if obj.get('idempotency_key')!=key or obj.get('catalog_sha256')!=fw.sha256(expected):
            raise DiKError('INTEGRITY_MISMATCH: existing job tampered')
        fw.audit(expected,crosswalk,registry)
        return {'status':'already_published','idempotency_key':key,'catalog':str(expected)}
    # Reuse safe, no-clobber, streamed Framework v11 importer. It atomically renames stage.
    result=import_wikidata_local(dump=dump,crosswalk=crosswalk,registry=registry,
         namespace=namespace,snapshot=snapshot,locales=locales,output=output)
    # Sidecar is derived job metadata; failure here leaves a valid immutable catalog.
    marker={'idempotency_key':key,'source_sha256':fw.sha256(dump),'catalog_sha256':fw.sha256(output/'catalog.json'),
         'transform':'wikidata-import-local-v11-draft.3','locales':sorted(locales)}
    with (output/'dik-job.json').open('x',encoding='utf-8') as f:
        f.write(json.dumps(marker,sort_keys=True,indent=2)+'\n')
        f.flush();os.fsync(f.fileno())
    return {'status':'published','idempotency_key':key,'catalog':str(output/'catalog.json'),
        'entities_scanned':result['entities_scanned'],'labels_by_locale':result['labels_by_locale']}
