"""Industrial local import: bounded-memory streaming and crash-safe checkpoints.

These tests are offline and small; they are not a benchmark on a real Wikidata dump.
"""
from __future__ import annotations

import bz2
import gzip
import json
import sqlite3
from pathlib import Path

import pytest
from dik.large_import import import_large
from dik.operations import import_wikidata_local, DiKError
from dik._framework import dictionaries as fw
from dik.cli import main

DEMO = Path(__file__).resolve().parents[1]/'examples'/'demo'
COMMON={'crosswalk':DEMO/'external-crosswalk.example.json',
        'registry':DEMO/'identity-registry.example.json',
        'namespace':'example.org/kristal-demo', 'locales':['fr','en'],
        'snapshot':'a7'}


def _dump(path, *, array=True, n=29):
    with path.open('wb') as f:
        if array:f.write(b'[\n')
        for i in range(n):
            entity={'id': 'Q8018' if i==12 else 'Q'+str(900000+i),
                    'labels': {'fr': {'language':'fr','value':'Augustin' if i==12 else str(i)},
                               'en': {'language':'en','value':'Augustine' if i==12 else str(i)}},
                    'lastrevid': 42}
            f.write(json.dumps(entity,ensure_ascii=False).encode('utf8'))
            f.write(b',\n' if array and i<n-1 else b'\n')
        if array:f.write(b']\n')
    return path


def _check_payloads(new, old):
    a,b=fw.read_json(new),fw.read_json(old)
    assert a==b
    for la, lb in zip(a['languages'],b['languages']):
        for x,y in zip(la['layers'],lb['layers']):
            path1=fw.safe_file(new.parent,x['path'])
            path2=fw.safe_file(old.parent,y['path'])
            assert path1.read_bytes()==path2.read_bytes()


def test_same_canonical_output_idempotence_and_old_importer(tmp_path):
    dump=_dump(tmp_path/'all.json')
    result=import_large(dump=dump,root=tmp_path/'snapshots',batch_lines=2,**COMMON)
    assert result['status']=='published'
    assert result['entities_scanned']==29 and result['accepted_exact_entities_seen']==1
    old=tmp_path/'baseline'
    import_wikidata_local(dump=dump,output=old,**COMMON)
    new=Path(result['catalog'])
    _check_payloads(new,old/'catalog.json')
    assert fw.audit(new,COMMON['crosswalk'],COMMON['registry'])['records_by_locale']=={'en':1,'fr':1}
    repeat=import_large(dump=dump,root=tmp_path/'snapshots',batch_lines=3,**COMMON)
    assert repeat['status']=='already_published' and repeat['idempotency_key']==result['idempotency_key']


def test_resume_at_transaction_boundaries(tmp_path):
    dump=_dump(tmp_path/'src.jsonl',array=False,n=41)
    kw=dict(dump=dump,root=tmp_path/'out',batch_lines=5,**COMMON)
    with pytest.raises(DiKError, match='SIMULATED_INTERRUPTION'):
        import_large(**kw,_stop_after_lines=17)
    stage=next((tmp_path/'out').glob('.dik-large-*'))
    with sqlite3.connect(stage/'progress.sqlite') as db:
        row=db.execute('SELECT line,scanned FROM checkpoint').fetchone()
    assert row==(15,15)
    result=import_large(**kw)
    assert result['status']=='published' and result['entities_scanned']==41
    assert not stage.exists()
    assert fw.audit(Path(result['catalog']),COMMON['crosswalk'],COMMON['registry'])['records_by_locale']=={'en':1,'fr':1}


@pytest.mark.parametrize('ext, compressor', [('.bz2',bz2.compress),('.gz',gzip.compress)])
def test_compressed_resume_from_line_without_random_seek(tmp_path,ext,compressor):
    original=_dump(tmp_path/'original.json',n=37)
    comp=tmp_path/('all.json'+ext)
    comp.write_bytes(compressor(original.read_bytes()))
    kw=dict(dump=comp,root=tmp_path/'out',batch_lines=4,**COMMON)
    with pytest.raises(DiKError,match='SIMULATED_INTERRUPTION'):
        import_large(**kw,_stop_after_lines=18)
    result=import_large(**kw)
    assert result['restart_strategy']=='replay-to-line'
    assert result['entities_scanned']==37
    assert Path(result['catalog']).is_file()


def test_integrity_rejects_changed_published_layer(tmp_path):
    result=import_large(dump=_dump(tmp_path/'src.json'),root=tmp_path/'out',**COMMON)
    cat=Path(result['catalog']); data=fw.read_json(cat)
    target=fw.safe_file(cat.parent,data['languages'][0]['layers'][0]['path'])
    target.write_text('tampered\n')
    with pytest.raises(DiKError,match='INTEGRITY_MISMATCH'):
        import_large(dump=tmp_path/'src.json',root=tmp_path/'out',**COMMON)


def test_source_changed_between_attempts_starts_new_key(tmp_path):
    dump=_dump(tmp_path/'src.jsonl',array=False)
    kw=dict(dump=dump,root=tmp_path/'out',batch_lines=3,**COMMON)
    with pytest.raises(DiKError,match='SIMULATED_INTERRUPTION'):
        import_large(**kw,_stop_after_lines=9)
    with dump.open('ab') as f:f.write(b'{"id":"Q999"}\n')
    result=import_large(**kw)
    assert result['entities_scanned']==30
    assert len(list((tmp_path/'out').glob('.dik-large-*')))==1


def test_truncated_array_is_never_published(tmp_path):
    dump=_dump(tmp_path/'src.json')
    dump.write_bytes(dump.read_bytes().replace(b']\n',b''))
    with pytest.raises(DiKError,match='TRUNCATED_ARRAY_DUMP'):
        import_large(dump=dump,root=tmp_path/'out',batch_lines=3,**COMMON)
    assert not list((tmp_path/'out').glob('*/catalog.json'))


def test_duplicate_entity_rejected(tmp_path):
    dump=tmp_path/'dup.jsonl'
    ent={'id':'Q8018','labels':{'fr':{'value':'A'},'en':{'value':'B'}}}
    dump.write_text(json.dumps(ent)+'\n'+json.dumps(ent)+'\n',encoding='utf8')
    with pytest.raises(DiKError,match='DUPLICATE_ENTITY'):
        import_large(dump=dump,root=tmp_path/'out',batch_lines=1,**COMMON)


def test_lock_and_limits(tmp_path):
    dump=_dump(tmp_path/'src.jsonl',array=False)
    kw=dict(dump=dump,root=tmp_path/'out',**COMMON)
    with pytest.raises(DiKError,match='INVALID_RESOURCE_LIMIT'):
        import_large(**kw,batch_lines=0)
    root=tmp_path/'out';root.mkdir()
    with pytest.raises(DiKError,match='SIMULATED_INTERRUPTION'):
        import_large(**kw,_stop_after_lines=1)
    stage=next(root.glob('.dik-large-*'))
    lock=root/('.lock-large-'+stage.name.removeprefix('.dik-large-'))
    lock.write_text('other worker')
    with pytest.raises(DiKError,match='SNAPSHOT_BUSY'):
        import_large(**kw)
    lock.unlink()
    assert import_large(**kw)['status']=='published'


def test_cli_import_large(tmp_path,capsys):
    dump=_dump(tmp_path/'src.jsonl',array=False)
    rc=main(['sync','import-large','--dump',str(dump),'--crosswalk',str(COMMON['crosswalk']),
             '--registry',str(COMMON['registry']),'--namespace',COMMON['namespace'],
             '--snapshot','a7','--locales','fr,en','--root',str(tmp_path/'out'),
             '--batch-lines','4'])
    assert rc==0
    payload=json.loads(capsys.readouterr().out)
    assert payload['status']=='published'


def test_sha256_attestation_optional_but_never_fabricated(tmp_path):
    from dik._framework.dictionaries import sha256
    dump=_dump(tmp_path/'src.jsonl',array=False)
    kw=dict(dump=dump,root=tmp_path/'out',**COMMON)
    with pytest.raises(DiKError,match='APPROVED_SHA256_MISMATCH'):
        import_large(**kw,approved_sha256='0'*64)
    result=import_large(**kw,approved_sha256=sha256(dump))
    assert result['upstream_verified'] is True
    marker=fw.read_json(Path(result['catalog']).parent/'dik-job.json')
    assert marker['upstream_verified'] is True
    no_attest=import_large(**{**kw,'root':tmp_path/'other'})
    assert no_attest['upstream_verified'] is False


def test_301_locale_catalog_no_invented_translation(tmp_path):
    dump=_dump(tmp_path/'src.jsonl',array=False,n=2)
    # 301 syntactically valid tags test scale, NOT 301 verified IANA languages.
    locales=['fr-'+str(i).zfill(3) for i in range(1,302)]
    result=import_large(dump=dump,crosswalk=COMMON['crosswalk'],
        registry=COMMON['registry'],namespace=COMMON['namespace'],
        snapshot='many-languages',locales=locales,root=tmp_path/'out')
    catalog=fw.read_json(result['catalog'])
    assert len(catalog['languages'])==301
    assert all(n==0 for n in result['labels_by_locale'].values())
