"""Alpha.3: source-level disagreement is not semantic equivalence."""
import http.client
import json
import shutil
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

import pytest

from dik.operations import DiKError, load_project
from dik._framework import dictionaries as fw
from dik.index import build
from dik.conciliation import conflicts, variants, conflict_detail
from dik.webapp import handler_factory, html_page

DEMO=Path(__file__).resolve().parents[1]/'examples/demo'


@pytest.fixture
def project():
    return load_project(DEMO/'dik.project.json')


@pytest.fixture
def indexed(project,tmp_path):
    path=tmp_path/'index.sqlite'
    build(project,path)
    return path


def test_competing_preferred_has_provenance_but_not_merge(project,indexed):
    report=conflicts(project,indexed,locale='fr')
    assert report['total']==1
    assert report['items'][0]=={
        'kind':'KQ','type':'competing_preferred','key':'KQ1001','affected_count':2,
        'status':'requires_review','automatic_merge_allowed':False}
    obs=variants(project,indexed,'KQ1001','fr')
    assert obs['competing_preferred'] and obs['preferred_forms_count']==2
    assert {(x['term'],x['source_kind']) for x in obs['signals'] if x['variant']=='preferred'}=={
        ('Saint Augustin','curated'),("Augustin d'Hippone",'wikidata')}
    assert not obs['identity_approved_by_dik']
    assert conflict_detail(project,indexed,locale='fr',kind='KQ',
                           conflict_type='competing_preferred',key='KQ1001')['automatic_merge_allowed'] is False


def test_locale_and_kind_isolation(project,indexed):
    assert conflicts(project,indexed,locale='en')['total']==0
    assert conflicts(project,indexed,locale='fr-CA')['total']==0
    assert conflicts(project,indexed,locale='fr',kind='KP')['total']==0
    with pytest.raises(DiKError,match='UNDECLARED_LOCALE'):
        conflicts(project,indexed,locale='xx')
    with pytest.raises(DiKError,match='Unknown'):
        variants(project,indexed,'Q8018','fr')
    with pytest.raises(DiKError,match='Unknown'):
        conflict_detail(project,indexed,locale='fr',kind='KQ',
                        conflict_type='shared_term',key='Saint Augustin')


def test_old_index_and_stale_input_are_blocked(project,indexed,tmp_path):
    import sqlite3
    with sqlite3.connect(indexed) as db:
        db.execute("DELETE FROM meta WHERE key='conciliation_format'")
    with pytest.raises(DiKError,match='INDEX_UPGRADE_REQUIRED'):
        conflicts(project,indexed,locale='fr')
    fresh=tmp_path/'fresh.sqlite';build(project,fresh)
    from dataclasses import replace
    changed=tmp_path/'stale.json'
    changed.write_text(project.crosswalk.read_text()+' ')
    with pytest.raises(DiKError,match='STALE_SOURCE'):
        conflicts(replace(project,crosswalk=changed),fresh,locale='fr')


def test_shared_homonym_across_two_kq_and_pagination(tmp_path):
    root=tmp_path/'demo'
    shutil.copytree(DEMO,root)
    catalog_path=root/'dictionaries/catalog.json'
    curated_path=root/'dictionaries/curated-fr.json'
    curated=json.loads(curated_path.read_text())
    curated['entries'].append({'semantic_id':'KQ1002','preferred_term':'Saint Augustin',
        'alternate_terms':[],'review':{'decision_id':'demo-other','reviewer':'reviewer',
                                      'reason':'Test a homonym, not equivalence'}})
    curated_path.write_text(json.dumps(curated,ensure_ascii=False))
    catalog=json.loads(catalog_path.read_text())
    catalog['languages'][0]['layers'][1]['sha256']=fw.sha256(curated_path)
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False))
    project=load_project(root/'dik.project.json')
    index=tmp_path/'review.sqlite';build(project,index)
    report=conflicts(project,index,locale='fr',page_size=1)
    assert report['total']==2 and len(report['items'])==1
    second=conflicts(project,index,locale='fr',page=2,page_size=1)
    assert second['items'][0]['type']=='shared_term'
    detail=conflict_detail(project,index,locale='fr',kind='KQ',
                           conflict_type='shared_term',key='Saint Augustin')
    assert {x['semantic_id'] for x in detail['signals']}=={'KQ1001','KQ1002'}
    assert not detail['automatic_merge_allowed']
    assert fw.read_json(project.graph)==fw.read_json(DEMO/'graph.json') if (DEMO/'graph.json').exists() else True


def test_web_queue_and_sources_still_read_only(project,indexed):
    rendered=html_page(project,indexed,locale='fr')
    assert 'Termes concurrents' in rendered and 'KQ1001' in rendered
    assert 'À examiner' in rendered
    concept=html_page(project,indexed,locale='fr',semantic_id='KQ1001')
    assert 'Comparer les dictionnaires' in concept
    assert 'Saint Augustin' in concept and 'wikidata-demo-snapshot-fr' in concept
    server=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(project,indexed))
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try:
        c=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
        c.request('GET','/api/conciliation?locale=fr',headers={'Host':f'127.0.0.1:{server.server_port}'})
        response=c.getresponse()
        assert response.status==200
        result=json.loads(response.read())
        assert result['total']==1 and result['identity_approved_by_dik'] is False
        c.close()
    finally:
        server.shutdown();server.server_close();worker.join(timeout=5)
