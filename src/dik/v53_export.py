"""Privacy-conscious, summary-only export of V5.3 local reports.

Local reports remain untouched. No JSONL source, SQLite checkpoint, local
Windows path or unreviewed lexical form is put into the shareable archive.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from .resource_locator import _unsafe

CSV_LIST = (
    'wikidata_schema_profiles.csv', 'wikidata_scan_progress.csv',
    'wikidata_qp_overlap.csv', 'wikidata_forms_candidates.csv',
    'wikidata_conflicts.csv', 'wikidata_identity_links_candidates.csv',
    'wikidata_nonlexical_qp_observations.csv',
    'wikidata_source_decisions.csv',
    'wikidata_online_observations_candidates.csv',
    'wikidata_online_potential_coverage.csv',
)
REDACT_COLS = {'path','checkpoint_ref','crosswalk_ref','form','forme_candidate',
               'source_chemin','catalogue','dossier','revision','source_url'}


def _safe_report(root: Path, path: Path):
    if not path.is_relative_to(root):
        raise ValueError('Export hors depot diK')
    for parent in (path, *path.parents):
        if parent == root.parent:break
        if _unsafe(parent):raise ValueError('Lien symbolique/jonction interdit')
    if not path.is_dir():raise ValueError('Dossier de rapports absent')


def _csv_redacted(path: Path) -> bytes:
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter=';')
        if not reader.fieldnames:return b''
        columns=list(reader.fieldnames)
        if 'form' in columns or 'forme_candidate' in columns:
            columns.append('form_sha256')
        out=io.StringIO(newline='')
        writer=csv.DictWriter(out,fieldnames=columns,delimiter=';',extrasaction='ignore')
        writer.writeheader()
        for row in reader:
            raw = row.get('form') or row.get('forme_candidate') or ''
            if 'form_sha256' in columns:
                row['form_sha256'] = hashlib.sha256(raw.encode('utf-8')).hexdigest() if raw else ''
            for col in REDACT_COLS:
                if col in row:row[col]='[EXPURGE]' if row[col] else ''
            writer.writerow(row)
    return out.getvalue().encode('utf-8-sig')


def export_v53(*, dik_root: str | Path, resolution_dir: str | Path,
               registry_file: str | Path | None = None,
               version: str = 'v54') -> dict:
    root=Path(dik_root).expanduser().absolute()
    reports=root/'reports'
    folder=Path(resolution_dir).expanduser().absolute()
    if _unsafe(root) or not root.is_dir() or _unsafe(reports):
        raise ValueError('Depot ou rapports invalides')
    _safe_report(reports,folder)
    if not (folder/'rapport.json').is_file():
        raise ValueError('rapport.json absent')
    doc=json.loads((folder/'rapport.json').read_text(encoding='utf-8'))
    summary={
        'schema':f'dik.{version}-shareable-summary/1.0',
        'status':doc.get('etat',''), 'date_utc':doc.get('date_utc',''),
        'no_translation':not doc.get('traduction_entre_langues',True),
        'locales':doc.get('locales',[]),'totaux':doc.get('totaux',{}),
        'par_langue':doc.get('par_langue',[]),
        'wikidata_v53':doc.get('wikidata_v53',{}),
        'wikidata_v54':doc.get('wikidata_v54',{}),
        'wikidata_v55':doc.get('wikidata_v55',{}),
        'wikidata_online':doc.get('wikidata_online',{}),
        'wikidata_thematic':doc.get('wikidata_thematic',{}),
        'redacted':True,
        'notice':'Aucun chemin local, contenu de JSONL, checkpoint ou forme candidate brute',
    }
    if registry_file:
        registry=Path(registry_file).expanduser().absolute()
        if not registry.is_file() or _unsafe(registry):
            raise ValueError('Registre non accessible pour export')
        src=json.loads(registry.read_text(encoding='utf-8'))
        summary['registry_counts']={'total':len(src.get('sources',[])),
              'by_kind':src.get('summary',{}).get('by_kind',{}),
              'searched_roots':len(src.get('roots_searched',[])),
              'unavailable_roots':len(src.get('roots_unavailable',[]))}
    entries={'synthese_expurgee.json':json.dumps(summary,ensure_ascii=False,indent=2).encode('utf-8')}
    for name in CSV_LIST:
        source=folder/name
        if source.is_file() and not _unsafe(source):
            entries[name]=_csv_redacted(source)
    for name in ('wikidata_schema_registry.json','wikidata_run_manifest.json'):
        source=folder/name
        if source.is_file() and not _unsafe(source):
            # Both files have schema IDs, hashes and numbers, not source paths/labels.
            content=json.loads(source.read_text(encoding='utf-8'))
            entries[name]=json.dumps(content,ensure_ascii=False,indent=2).encode('utf-8')
    entries['SHA256_EXPORT.json']=json.dumps({name:hashlib.sha256(data).hexdigest()
                   for name,data in sorted(entries.items())},indent=2).encode('utf-8')
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report_version='5_6' if version=='v56' else ('5_5' if version=='v55' else '5_4')
    filename=reports/f'DIK_V{report_version}_BILAN_{stamp}.zip'
    i=2
    while filename.exists():
        filename=reports/f'DIK_V{report_version}_BILAN_{stamp}_{i}.zip';i+=1
    with zipfile.ZipFile(filename,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in entries.items():z.writestr(name,data)
    return {'status':'CREATED','zip':str(filename),'files':len(entries),'redacted':True}
