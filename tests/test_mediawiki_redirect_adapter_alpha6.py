"""Official MediaWiki action=query&redirects=1 response handling, offline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from dik.cli import make_parser, run
from dik.operations import DiKError
from dik.redirect_sources import extract_api_redirects
from dik.wikidata_evolution import analyze_evolution

DEMO = Path(__file__).resolve().parents[1] / 'examples' / 'demo'
SNAPSHOT = 'wd-20261016-query-redirects'


def response(*redirects):
    return {'batchcomplete': True, 'query': {'redirects': [{'from': src, 'to': dst} for src, dst in redirects],
                   'pages': [{'ns': 0, 'title': 'Q9000'}]}}


def write_source(tmp_path, payload, name='official-response.json'):
    path = tmp_path / name
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf8')
    return path


def do(tmp_path, src, **kwargs):
    return extract_api_redirects(source=src, output=tmp_path/'events.jsonl', snapshot=SNAPSHOT, **kwargs)


def test_real_api_shape_normalizes_and_roundtrips_to_impact(tmp_path):
    src = write_source(tmp_path, response(('Q8018','Q9000'), ('Property:P50','Property:P90')))
    before = src.read_bytes()
    report = do(tmp_path, src, approved_sha256=hashlib.sha256(before).hexdigest())
    assert report['source_digest_verified']
    assert report['redirect_events'] == 2
    normalized = [json.loads(x) for x in (tmp_path/'events.jsonl').read_text().splitlines()]
    assert [(x['source_id'], x['targets']) for x in normalized] == [('Q8018',['Q9000']),('P50',['P90'])]
    assert normalized[0]['source_reference'].startswith('wikidata-action-api:sha256:')
    assert src.read_bytes()==before
    assert hashlib.sha256((tmp_path/'events.jsonl').read_bytes()).hexdigest() == report['output_sha256']
    result=analyze_evolution(observations=tmp_path/'events.jsonl',
       crosswalk=DEMO/'external-crosswalk.example.json',
       registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
       snapshot=SNAPSHOT,approved_sha256=report['output_sha256'])
    assert result['affected_mappings']==1
    assert result['samples'][0]['local_id']=='KQ1001'
    assert result['samples'][0]['resolution']['terminal_id']=='Q9000'
    assert not result['canonical_mutation'] and not result['crosswalk_mutation']


def test_jsonl_batches_and_no_redirects(tmp_path):
    path=tmp_path/'responses.jsonl'
    path.write_text('\n'.join(json.dumps(x) for x in [response(('Q8018','Q9000')),response(),response(('Property:P50','Property:P51'))])+'\n')
    result=do(tmp_path,path,input_format='action-api-jsonl')
    assert result['redirect_events']==2 and result['responses_processed']==3


def test_missing_not_converted_to_retirement(tmp_path):
    # A missing page alone does not prove that the identity has been deleted or split.
    src=write_source(tmp_path,{'batchcomplete':True,'query':{'pages':[{'title':'Q8018','missing':True}]}})
    assert do(tmp_path,src)['redirect_events']==0
    assert (tmp_path/'events.jsonl').read_text()==''


@pytest.mark.parametrize('payload,error',[
    ({'error':{'code':'badrequest'}},'INVALID_MEDIAWIKI_RESPONSE'),
    ({'query':{'redirects':'not-a-list'}},'INVALID_MEDIAWIKI_RESPONSE'),
    ({'continue':{'rdcontinue':'...'},'query':{'redirects':[]}},'INCOMPLETE_MEDIAWIKI_RESPONSE'),
    (response(('Q8018','Property:P50')),'IDENTITY_KIND_MISMATCH'),
    (response(('Q8018','Q8018')),'REDIRECT_CYCLE'),
    (response(('KQ1001','Q8018')),'UNSUPPORTED_MEDIAWIKI_TITLE'),
    (response(('Q8018','Q42'),('Q8018','Q43')),'DUPLICATE_EVOLUTION_EVENT'),
    (response(('Talk:Q8018','Q9000')),'UNSUPPORTED_MEDIAWIKI_TITLE'),
    ({'query':{'redirects':[{'from':'Q8018'}]}},'INVALID_MEDIAWIKI_REDIRECT'),
])
def test_rejects_unsafe_or_unsupported_json(tmp_path, payload, error):
    src=write_source(tmp_path,payload)
    with pytest.raises(DiKError,match=error):
        do(tmp_path,src)
    assert not (tmp_path/'events.jsonl').exists()


def test_integrity_resource_and_nonclobber(tmp_path):
    src=write_source(tmp_path,response(('Q8018','Q9000')))
    with pytest.raises(DiKError,match='INTEGRITY_MISMATCH'):
        do(tmp_path,src,approved_sha256='1'*64)
    with pytest.raises(DiKError,match='RESOURCE_LIMIT'):
        do(tmp_path,src,max_bytes=10)
    with pytest.raises(DiKError,match='RESOURCE_LIMIT'):
        do(tmp_path,src,max_records=0)
    assert not (tmp_path/'events.jsonl').exists()
    target=tmp_path/'events.jsonl'
    target.write_text('original')
    with pytest.raises(DiKError,match='OUTPUT_EXISTS'):
        do(tmp_path,src)
    assert target.read_text()=='original'
    target.unlink()
    with pytest.raises(DiKError,match='OUTPUT_EXISTS'):
        extract_api_redirects(source=src,output=src,snapshot=SNAPSHOT)


def test_cli_and_official_envelope_scope(tmp_path):
    src=write_source(tmp_path,response(('Q8018','Q9000')))
    args=make_parser().parse_args(['sync','extract-redirects','--source',str(src),'--snapshot',SNAPSHOT,
          '--output',str(tmp_path/'fromcli.jsonl')])
    result=run(args)
    assert result['redirect_events']==1
    assert (tmp_path/'fromcli.jsonl').is_file()
    assert 'Q8018' in (tmp_path/'fromcli.jsonl').read_text()


def test_cross_batch_duplicates_and_invalid_jsonl(tmp_path):
    path=tmp_path/'batches.jsonl'
    path.write_text(json.dumps(response(('Q8018','Q42')))+'\n'+json.dumps(response(('Q8018','Q43')))+'\n')
    with pytest.raises(DiKError,match='DUPLICATE_EVOLUTION_EVENT'):
        do(tmp_path,path,input_format='action-api-jsonl')
    assert not (tmp_path/'events.jsonl').exists()
    path.write_text('{\n')
    with pytest.raises(DiKError,match='INVALID_MEDIAWIKI_JSONL'):
        do(tmp_path,path,input_format='action-api-jsonl')

class FakeHTTPReply:
    def __init__(self, url, payload, status=200):
        self._url=url;self._body=json.dumps(payload).encode();self.status=status
    def __enter__(self):return self
    def __exit__(self,*_):return None
    def geturl(self):return self._url
    def getcode(self):return self.status
    def read(self,n=-1):return self._body[:n]

class FakeOpener:
    def __init__(self, payload, override_url=None):
        self.payload=payload;self.requests=[];self.override_url=override_url
    def open(self,req,timeout):
        self.requests.append(req.full_url)
        return FakeHTTPReply(self.override_url or req.full_url,self.payload)


def test_bounded_live_api_probe_and_pipeline(tmp_path):
    from dik.wikidata_probe import probe_crosswalk_redirects
    from urllib.parse import parse_qs, urlsplit
    opener=FakeOpener(response(('Q8018','Q9000')))
    output=tmp_path/'official.jsonl'
    result=probe_crosswalk_redirects(crosswalk=DEMO/'external-crosswalk.example.json',
        registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
        output=output,user_agent='diK test operator contact@example.org',opener=opener)
    assert result['approved_exact_external_ids_queried']==1
    assert result['redirects_found']==1
    assert len(opener.requests)==1
    query=parse_qs(urlsplit(opener.requests[0]).query)
    assert query['titles']==['Q8018'] and query['redirects']==['1']
    x=extract_api_redirects(source=output,output=tmp_path/'events.jsonl',snapshot=SNAPSHOT,
               input_format='action-api-jsonl',approved_sha256=result['responses_sha256'])
    assert x['redirect_events']==1
    assert not result['canonical_mutation'] and not x['crosswalk_mutation']


def test_api_probe_rejects_nonwikidata_responses(tmp_path):
    from dik.wikidata_probe import probe_crosswalk_redirects
    kwargs=dict(crosswalk=DEMO/'external-crosswalk.example.json',
        registry=DEMO/'identity-registry.example.json',namespace='example.org/kristal-demo',
        output=tmp_path/'api.jsonl',user_agent='diK contact@example.org')
    with pytest.raises(DiKError,match='UNSAFE_REDIRECT'):
        probe_crosswalk_redirects(**kwargs,opener=FakeOpener(response(('Q8018','Q9000')),'https://example.org/api'))
    with pytest.raises(DiKError,match='UNEXPECTED_MEDIAWIKI_REDIRECT'):
        probe_crosswalk_redirects(**kwargs,opener=FakeOpener(response(('Q77','Q9000'))))
    with pytest.raises(DiKError,match='RESOURCE_LIMIT'):
        probe_crosswalk_redirects(**{**kwargs,'max_ids':0},opener=FakeOpener(response()))
    with pytest.raises(DiKError,match='INVALID_RATE_LIMIT'):
        probe_crosswalk_redirects(**{**kwargs,'delay_seconds':0.01},opener=FakeOpener(response()))
    with pytest.raises(DiKError,match='USER_AGENT_REQUIRED'):
        probe_crosswalk_redirects(**{**kwargs,'user_agent':'diK'},opener=FakeOpener(response()))
    assert not (tmp_path/'api.jsonl').exists()
