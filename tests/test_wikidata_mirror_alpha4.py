"""Offline adversarial tests. No Wikidata network is accessed."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from email.message import Message
import pytest

from dik.mirror import fetch_dump
from dik.snapshot_diff import compare_snapshots
from dik.operations import DiKError, import_wikidata_local
from dik._framework import dictionaries as fw
from dik.cli import make_parser

DEMO = Path(__file__).resolve().parents[1] / 'examples' / 'demo'
URL = 'https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2'


class Response:
    def __init__(self, data, *, status=200, headers=None, fail_after=None):
        self.data = data
        self.pos = 0
        self.status = status
        self.headers = Message()
        for key,val in (headers or {}).items():self.headers[key] = str(val)
        self.fail_after = fail_after
    def getcode(self):return self.status
    def geturl(self):return URL
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):
        if self.fail_after is not None and self.pos >= self.fail_after:
            raise OSError('simulated network interruption')
        if self.fail_after is not None:
            n = min(n,self.fail_after-self.pos)
        part = self.data[self.pos:self.pos+n]
        self.pos += len(part)
        return part


class Opener:
    def __init__(self,responses):self.responses=list(responses);self.requests=[]
    def open(self, req, timeout):
        self.requests.append(dict(req.header_items()))
        if not self.responses:raise AssertionError('unexpected extra network request')
        return self.responses.pop(0)


def test_fetch_resume_checksum_idempotent(tmp_path):
    content = b'A' * (1024*1024+7)
    checksum = hashlib.sha256(content).hexdigest()
    broken = Response(content,headers={'ETag':'"v1"','Content-Length':len(content)},fail_after=137)
    op = Opener([broken, Response(content[137:],status=206,headers={
         'ETag':'"v1"','Content-Range':f'bytes 137-{len(content)-1}/{len(content)}',
         'Content-Length':len(content)-137})])
    kwargs=dict(url=URL,root=tmp_path,snapshot='2026-10-16',expected_sha256=checksum,opener=op)
    with pytest.raises(DiKError,match='DOWNLOAD_INTERRUPTED'):
        fetch_dump(**kwargs)
    partial=tmp_path/'.incoming-2026-10-16'/'wikidata.json.bz2.part'
    assert partial.stat().st_size==137
    result=fetch_dump(**kwargs)
    assert result['status']=='published' and result['upstream_verified']
    assert op.requests[1]['Range']=='bytes=137-'
    assert result['sha256']==checksum
    assert Path(result['dump']).read_bytes()==content
    assert fetch_dump(**kwargs)['status']=='already_published'
    assert len(op.requests)==2


def test_resume_rejects_etag_change_or_incorrect_range(tmp_path):
    body=b'abcdef'
    cases=[(206,{'ETag':'"other"','Content-Range':'bytes 2-5/6'}),
           (200,{'ETag':'"v1"','Content-Length':'6'}),
           (206,{'ETag':'"v1"','Content-Range':'bytes 0-5/6'})]
    for i,(status,headers) in enumerate(cases):
        root=tmp_path/str(i)
        root.mkdir()
        stage=root/'.incoming-s1';stage.mkdir()
        (stage/'wikidata.json.bz2.part').write_bytes(b'ab')
        (stage/'transfer.json').write_text(json.dumps({
            'url':URL,'expected_sha256':None,'etag':'"v1"','last_modified':None,'total_size':6}))
        op=Opener([Response(body[2:],status=status,headers=headers)])
        with pytest.raises(DiKError,match='UNSAFE_RESUME'):
            fetch_dump(url=URL,root=root,snapshot='s1',opener=op)
        assert not (root/'s1').exists()
        assert (stage/'wikidata.json.bz2.part').read_bytes()==b'ab'


def test_checksum_missing_marks_unverified_and_bad_checksum_quarantines(tmp_path):
    content=b'12345678'
    op=Opener([Response(content,headers={'Content-Length':8})])
    result=fetch_dump(url=URL,root=tmp_path,snapshot='unverified',opener=op)
    assert not result['upstream_verified']
    assert json.loads(Path(result['manifest']).read_text())['imported_into_kristal'] is False
    op=Opener([Response(content,headers={'Content-Length':8})])
    with pytest.raises(DiKError,match='CHECKSUM_MISMATCH'):
        fetch_dump(url=URL,root=tmp_path,snapshot='bad',expected_sha256='0'*64,opener=op)
    assert not (tmp_path/'bad').exists()
    assert (tmp_path/'.incoming-bad').exists()
    with pytest.raises(DiKError,match='SOURCE_NOT_ALLOWED'):
        fetch_dump(url='http://127.0.0.1/private',root=tmp_path,snapshot='ss')
    with pytest.raises(DiKError,match='SOURCE_NOT_ALLOWED'):
        fetch_dump(url='https://dumps.wikimedia.org.evil.net/wikidatawiki/entities/data.json',root=tmp_path,snapshot='ss')


def test_resource_budget_and_lock(tmp_path):
    with pytest.raises(DiKError,match='RESOURCE_LIMIT'):
        fetch_dump(url=URL,root=tmp_path,snapshot='limit',max_bytes=2,
           opener=Opener([Response(b'abcdef',headers={'Content-Length':'6'})]))
    (tmp_path/'.lock-busy').write_text('other')
    with pytest.raises(DiKError,match='SNAPSHOT_BUSY'):
        fetch_dump(url=URL,root=tmp_path,snapshot='busy')
    assert (tmp_path/'.lock-busy').exists()


def test_recovery_after_completed_stage(tmp_path):
    content=b'a sample'
    checksum=hashlib.sha256(content).hexdigest()
    first=fetch_dump(url=URL,root=tmp_path,snapshot='recovery',opener=Opener([
        Response(content,headers={'Content-Length':len(content)})]))
    final=tmp_path/'recovery';stage=tmp_path/'.incoming-recovery'
    final.rename(stage)
    (stage/'transfer.json').write_text(json.dumps({'url':URL,'expected_sha256':None,'etag':None,'last_modified':None}))
    result=fetch_dump(url=URL,root=tmp_path,snapshot='recovery',opener=Opener([]))
    assert result['status']=='recovered' and result['sha256']==checksum
    assert (final/'mirror.json').is_file()


def _snapshot(tmp_path,name,lines):
    dump=tmp_path/(name+'.jsonl')
    dump.write_text('\n'.join(json.dumps(row,ensure_ascii=False) for row in lines)+'\n',encoding='utf-8')
    out=tmp_path/name
    import_wikidata_local(dump=dump,crosswalk=DEMO/'external-crosswalk.example.json',
      registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
      snapshot=name,locales=['fr','en'],output=out)
    return out/'catalog.json'


def _entity(label,*,en='Augustine',aliases=None,revid=1):
    return {'id':'Q8018','lastrevid':revid, 'labels':{'fr':{'value':label},
        **({'en':{'value':en}} if en else {})}, 'aliases':{'fr':[
           {'value':x} for x in (aliases or [])]}}


def test_snapshot_diff_streamed_and_review(tmp_path):
    before = _snapshot(tmp_path,'old',[_entity('Augustin',aliases=['Saint Augustin'])])
    after = _snapshot(tmp_path,'new',[_entity('Augustin d’Hippone',en=None,aliases=['St Augustin'],revid=2)])
    events=tmp_path/'events.jsonl'
    result=compare_snapshots(before=before,after=after,crosswalk=DEMO/'external-crosswalk.example.json',
       registry=DEMO/'identity-registry.example.json',sample_limit=1,events_path=events)
    assert result['total_events']==2
    assert result['by_change']=={'multiple_fields_changed':1,'removed':1}
    assert result['sample_truncated'] and len(result['samples'])==1
    records=[json.loads(x) for x in events.read_text().splitlines()]
    assert len(records)==2 and all(x['review_required'] for x in records)
    assert all(x['semantic_id']=='KQ1001' for x in records)
    assert not any(x['semantic_id']=='KQ1002' for x in records)
    with pytest.raises(DiKError,match='OUTPUT_EXISTS'):
        compare_snapshots(before=before,after=after,crosswalk=DEMO/'external-crosswalk.example.json',
           registry=DEMO/'identity-registry.example.json',events_path=events)


def test_revision_only_optional(tmp_path):
    before=_snapshot(tmp_path,'a',[_entity('Augustin',revid=1)])
    after=_snapshot(tmp_path,'b',[_entity('Augustin',revid=9)])
    params=dict(before=before,after=after,crosswalk=DEMO/'external-crosswalk.example.json',
        registry=DEMO/'identity-registry.example.json')
    assert compare_snapshots(**params)['total_events']==0
    report=compare_snapshots(**params,include_revision_only=True)
    assert report['by_change']=={'revision_only':2}  # One for each locale
    assert not any(e['review_required'] for e in report['samples'])


def test_alpha4_cli_parsers():
    parser=make_parser()
    assert parser.parse_args(['sync','fetch','--url',URL,'--snapshot','aa','--root','/tmp']).command=='fetch'
    assert parser.parse_args(['sync','diff','--before','a','--after','b','--registry','c','--crosswalk','d']).command=='diff'


def test_mirror_handoff_verified_only(tmp_path):
    import bz2
    from dik.mirror_import import import_verified_mirror
    content=bz2.compress((DEMO/'wikidata-small.sample.jsonl').read_bytes())
    digest=hashlib.sha256(content).hexdigest()
    op=Opener([Response(content,headers={'Content-Length':len(content),'ETag':'"immutable"'})])
    downloaded=fetch_dump(url=URL,root=tmp_path/'mirror',snapshot='verified',
         expected_sha256=digest,opener=op)
    kwargs={'manifest':Path(downloaded['manifest']),
       'crosswalk':DEMO/'external-crosswalk.example.json',
       'registry':DEMO/'identity-registry.example.json',
       'namespace':'example.org/kristal-demo','locales':['fr','en'],
       'root':tmp_path/'imported', 'approved_sha256':digest}
    first=import_verified_mirror(**kwargs)
    assert first['status']=='published' and first['upstream_verified']
    assert json.loads(Path(first['catalog']).read_text())['catalog_id']=='wikidata-import-verified'
    assert import_verified_mirror(**kwargs)['status']=='already_published'
    # Modified bytes invalidate the mirror, even if the published import exists.
    Path(downloaded['dump']).write_bytes(b'evil')
    with pytest.raises(DiKError,match='INTEGRITY_MISMATCH'):
        import_verified_mirror(**kwargs)


def test_unverified_mirror_never_trusted(tmp_path):
    from dik.mirror_import import import_verified_mirror
    download=fetch_dump(url=URL,root=tmp_path/'mirrors',snapshot='untrusted',
       opener=Opener([Response(b'anything',headers={'Content-Length':8})]))
    with pytest.raises(DiKError,match='UNVERIFIED_UPSTREAM'):
        import_verified_mirror(manifest=Path(download['manifest']),
           crosswalk=DEMO/'external-crosswalk.example.json',
           registry=DEMO/'identity-registry.example.json',
           namespace='example.org/kristal-demo',locales=['fr'],root=tmp_path/'jobs',approved_sha256='0'*64)


def test_weak_etag_alone_not_sufficient_for_resuming(tmp_path):
    stage=tmp_path/'.incoming-weak';stage.mkdir()
    (stage/'wikidata.json.bz2.part').write_bytes(b'abc')
    (stage/'transfer.json').write_text(json.dumps({
        'url':URL,'expected_sha256':None,'etag':'W/"weak"',
        'last_modified':None,'total_size':100}))
    with pytest.raises(DiKError,match='UNSAFE_RESUME'):
        fetch_dump(url=URL,root=tmp_path,snapshot='weak',opener=Opener([]))


def test_rejects_mismatched_http_content_range_length(tmp_path):
    stage=tmp_path/'.incoming-broken';stage.mkdir()
    (stage/'wikidata.json.bz2.part').write_bytes(b'abc')
    (stage/'transfer.json').write_text(json.dumps({
        'url':URL,'expected_sha256':None,'etag':'"strong"',
        'last_modified':None,'total_size':100}))
    response=Response(b'def',status=206,headers={
         'ETag':'"strong"','Content-Range':'bytes 3-11/100',
         'Content-Length':'3'})
    with pytest.raises(DiKError,match='INVALID_CONTENT_RANGE'):
        fetch_dump(url=URL,root=tmp_path,snapshot='broken',opener=Opener([response]))
