"""diK 1.0 alpha: deterministic tests of implemented new modules."""
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from dik.operations import load_project,DiKError
from dik._framework import dictionaries as fw
from dik.index import build, reverse_lookup
from dik.governance import append_review,journal_records
from dik.legacy import conversion_candidates,validate_plan_source
from dik.portfolio import portfolio_report
from dik.curation import publish_preference
from dik.patches import inspect_patch
from dik.sync import import_idempotent

DEMO=Path(__file__).resolve().parents[1]/'examples'/'demo'

@pytest.fixture
def project():return load_project(DEMO/'dik.project.json')

@pytest.fixture
def idx(project,tmp_path):
    result=build(project,tmp_path/'index.sqlite')
    return Path(result['index'])


def test_lookup_exact_and_not_approval(project,idx):
    d=reverse_lookup(project,idx,term='Saint Augustin',locale='fr',kind='KQ')
    assert d['state']=='unique_candidate' and d['candidate_count']==1
    assert d['candidates'][0]['semantic_id']=='KQ1001' and not d['identity_approved']
    assert reverse_lookup(project,idx,term='saint augustin',locale='fr',kind='KQ')['state']=='no_candidate'
    assert reverse_lookup(project,idx,term='Saint Augustin',locale='en',kind='KQ')['state']=='no_candidate'
    assert reverse_lookup(project,idx,term='Saint Augustin',locale='fr',kind='KP')['state']=='no_candidate'


def test_index_stale(project,idx,tmp_path):
    manifest=json.loads(project.manifest.read_text())
    copy=tmp_path/'demo';copy.mkdir()
    for name in ('graph','registry','crosswalk','catalog'):
        # project.copy with separate catalog file corrupt digest => stale should fail
        pass
    from dataclasses import replace
    stale=replace(project,crosswalk=tmp_path/'crosswalk.json')
    (tmp_path/'crosswalk.json').write_text(project.crosswalk.read_text()+' ')
    with pytest.raises(DiKError,match='STALE_SOURCE'):
        reverse_lookup(stale,idx,term='Saint Augustin',locale='fr',kind='KQ')


def make_review(project,status='accepted',decision_id='r1',revision=1,reviewer='independent-human'):
    return {'contract_profile':'dik.review-decision/1.0-candidate',
        'decision_id':decision_id,'revision':revision,'mapping_kind':'external_alignment',
        'target':{'namespace_id':'example.org/kristal-demo','kind':'KQ','id':'KQ1001'},
        'candidate':{'source_system':'wikidata','source_snapshot':'demo-snapshot',
                     'source_record_id':'Q8018','locale':'fr','term':'Saint Augustin'},
        'relation':'exactMatch','status':status,'actor_id':'test-author',
        'input_manifest_sha256':fw.sha256(project.manifest),
        'reason':'Human reviewed fictional fixture','reviewer_id':reviewer,
        'decision_method':'human','evidence_refs':['KS4001']}


def test_review_journal_and_idempotency(project,tmp_path):
    path=tmp_path/'review.jsonl'; d=make_review(project)
    assert append_review(path,d,project)['status']=='recorded'
    assert append_review(path,d,project)['status']=='already_recorded'
    assert len(journal_records(path))==1
    changed=make_review(project,decision_id='r1',reviewer='another')
    with pytest.raises(DiKError,match='IDEMPOTENCY_CONFLICT'):append_review(path,changed,project)
    d2=make_review(project,decision_id='r2')
    with pytest.raises(DiKError,match='revision|duplicate|transition'):append_review(path,d2,project)
    data=path.read_text();path.write_text(data.replace('reviewed','tampered'))
    with pytest.raises(DiKError,match='INTEGRITY_MISMATCH'):journal_records(path)


def test_no_self_review(project,tmp_path):
    d=make_review(project,reviewer='test-author')
    with pytest.raises(DiKError,match='independent reviewer'):
        append_review(tmp_path/'journal.jsonl',d,project)
    assert not (tmp_path/'journal.jsonl').exists()


def test_portfolio(project):
    result=portfolio_report([project.manifest],['fr','en'])
    assert len(result['matrix'])==2 and result['report']['contract_profile'].startswith('dik.portfolio')
    with pytest.raises(DiKError,match='Duplicate'):portfolio_report([project.manifest,project.manifest],['fr'])


def test_non_executable_legacy(project,idx,tmp_path):
    src=tmp_path/'legacy.json'
    src.write_text(json.dumps({'graph_id':'legacy', 'subject':'Saint Augustin',
             'text':'Saint Augustin','predicate':'parle_de','object':{'id':'grâce'}},ensure_ascii=False))
    roles=[{'source_path':'/subject','semantic_role':'entity'},
           {'source_path':'/predicate','semantic_role':'property'},
           {'source_path':'/object/id','semantic_role':'entity'}]
    result=conversion_candidates(project,src,idx,roles,locale='fr')
    assert len(result['plan']['operations'])==1
    assert len(result['unresolved'])==2
    assert all(x['decision']['status']=='pending' for x in result['plan']['operations'])
    assert validate_plan_source(result['plan'],src)['mutation_permitted_by_dik'] is False
    src.write_text(src.read_text()+' ')
    with pytest.raises(DiKError,match='STALE_SOURCE'):validate_plan_source(result['plan'],src)


def test_curated_copy(project,tmp_path):
    old_sha=fw.sha256(project.graph)
    destination=tmp_path/'new'
    result=publish_preference(project,semantic_id='KQ1002',locale='fr',term='grâce sanctifiante',
          reviewer='test-reviewer',decision_id='demo-review',reason='For testing',destination=destination)
    assert result['status']=='published'
    assert fw.resolve(destination/'catalog.json','KQ1002','fr')['term']=='grâce sanctifiante'
    assert fw.sha256(project.graph)==old_sha
    assert fw.resolve(project.catalog,'KQ1002','fr')['status']=='missing'
    with pytest.raises(DiKError,match='exists'):publish_preference(project,semantic_id='KQ1002',locale='fr',
           term='new',reviewer='x',decision_id='new',reason='test',destination=destination)


def test_import_idempotent(project,tmp_path):
    import json
    root=tmp_path/'jobs'
    result=import_idempotent(dump=DEMO/'wikidata-small.sample.jsonl',crosswalk=project.crosswalk,
         registry=project.registry,namespace='example.org/kristal-demo',snapshot='demo-new',
         locales=['fr','en'],root=root)
    assert result['status']=='published'
    same=import_idempotent(dump=DEMO/'wikidata-small.sample.jsonl',crosswalk=project.crosswalk,
         registry=project.registry,namespace='example.org/kristal-demo',snapshot='demo-new',
         locales=['fr','en'],root=root)
    assert same['status']=='already_published'
    assert len([p for p in root.iterdir() if p.is_dir()])==1


def test_patch_never_commits(project):
    graph=fw.read_json(project.graph)
    intent={'contract_profile':'dik.semantic-patch-intent/1.0-candidate','patch_id':'p1',
      'source_graph_id':graph['graph_id'],'namespace_id':graph['namespace_id'],
      'source_graph_sha256':fw.sha256(project.graph),'source_path':'/assertions/0/predicate',
      'change_kind':'semantic_relation','original':'KP2001','proposed':'KP2002',
      'review_status':'pending','reason':'Test only'}
    assert inspect_patch(intent,project.graph)['mutation_permitted_by_dik'] is False
    intent['source_graph_sha256']='0'*64
    with pytest.raises(DiKError,match='STALE_SOURCE'):inspect_patch(intent,project.graph)


def test_html_escaping_and_non_mutating_ui(project,idx):
    from dik.webapp import html_page,handler_factory
    rendered=html_page(project,idx,locale='fr',term='Augustin d\'Hippone',kind='KQ')
    assert 'unique_candidate' in rendered and 'KQ1001' in rendered
    assert 'name="term"' in rendered
    assert 'Augustin d&#x27;Hippone' in rendered


def test_http_loopback_read_only(project,idx):
    import http.client
    import threading
    from http.server import ThreadingHTTPServer
    from dik.webapp import handler_factory
    s=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(project,idx))
    worker=threading.Thread(target=s.serve_forever,daemon=True)
    worker.start()
    try:
        cn=http.client.HTTPConnection('127.0.0.1',s.server_port,timeout=5)
        cn.request('GET','/api/lookup?term=Saint%20Augustin&locale=fr&kind=KQ')
        res=cn.getresponse(); d=json.loads(res.read())
        assert res.status==200 and d['state']=='unique_candidate'
        cn.request('POST','/api/resolve'); res=cn.getresponse();res.read()
        assert res.status==405
        cn.close()
    finally:
        s.shutdown();s.server_close();worker.join(timeout=2)


def test_import_recover_sidecar(project,tmp_path):
    root=tmp_path/'jobs'; params={
       'dump':DEMO/'wikidata-small.sample.jsonl','crosswalk':project.crosswalk,
       'registry':project.registry,'namespace':'example.org/kristal-demo',
       'snapshot':'recovery','locales':['fr'], 'root':root}
    r=import_idempotent(**params)
    sidecar=Path(r['catalog']).parent/'dik-job.json';sidecar.unlink()
    result=import_idempotent(**params)
    assert result['status']=='already_published' and sidecar.exists()


def test_reconciled_crosswalk_is_new_revision(project,tmp_path):
    from dik.reconcile import publish_crosswalk
    path=tmp_path/'review.jsonl'
    # Original sample already accepted KQ1001-Q8018. Reject accidental second exact match.
    d=make_review(project)
    append_review(path,d,project)
    with pytest.raises((DiKError,fw.DictionaryError),match='duplicate|correspondence|mapping'):
        publish_crosswalk(project,path,tmp_path/'new-crosswalk.json','revision-1')
    assert not (tmp_path/'new-crosswalk.json').exists()


def test_portfolio_groups_different_catalog_snapshots(project,tmp_path):
    import shutil
    src=tmp_path/'demo-copy';shutil.copytree(DEMO,src)
    graph=src/'semantic-graph.example.json'; g=json.loads(graph.read_text())
    g['graph_id']='demo-graph-2';graph.write_text(json.dumps(g))
    catalog=src/'dictionaries'/'catalog.json'; c=json.loads(catalog.read_text())
    c['catalog_id']='new-catalog-revision';catalog.write_text(json.dumps(c))
    result=portfolio_report([project.manifest,src/'dik.project.json'],['fr','en'])
    assert result['mixed_catalog_snapshots'] and len(result['group_reports'])==2
    assert len(result['matrix'])==4


def test_sparse_catalog_more_than_300_languages(project,tmp_path):
    # 301 languages can be declared without inventing translations or a dense matrix.
    import itertools,string
    from dataclasses import replace
    base=json.loads(project.catalog.read_text())
    tags=['q'+a+b for a,b in itertools.product(string.ascii_lowercase,string.ascii_lowercase)][:301]
    base['catalog_id']='sparse-301'
    base['languages']=[{'tag':tag,'fallbacks':[],'layers':[]} for tag in tags]
    catalog=tmp_path/'catalog.json';catalog.write_text(json.dumps(base))
    alt=replace(project,catalog=catalog)
    fw.audit(alt.catalog,alt.crosswalk,alt.registry)
    from dik.operations import coverage_report
    report=coverage_report(alt,locales=tags[:5])
    assert all(row['KQ']['direct']==0 and not row['complete_direct'] for row in report['locales'])
