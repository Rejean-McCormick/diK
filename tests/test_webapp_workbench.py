"""Task-centred UX, canonical safety and local HTTP boundary regression tests."""
import http.client
import json
import re
import threading
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode

import pytest
from dik.operations import load_project, DiKError
from dik.index import build
from dik.webapp import html_page,handler_factory,serve
from dik._framework import dictionaries as fw
from dik.compact import restore_compact

DEMO = Path(__file__).resolve().parents[1]/'examples'/'demo'

@pytest.fixture
def project():return load_project(DEMO/'dik.project.json')

@pytest.fixture
def index(project,tmp_path):
    dest=tmp_path/'search.sqlite'
    build(project,dest)
    return dest


def test_three_main_intentions_not_a_menu_per_module(project,index):
    doc=html_page(project,index,term='Saint Augustin',kind='KQ',locale='fr')
    assert 'aria-label="Navigation principale"' in doc
    assert doc.count('aria-current="page"')==1
    assert all(title in doc for title in ['Concepts et traductions','Complétude','Lire un Kristal'])
    assert 'unique_candidate' in doc and 'Candidat non approuvé' in doc
    assert 'KQ1001' in doc
    assert '<script' not in doc


def test_concept_is_contextual_and_local_curations_are_opt_in(project,index):
    original=html_page(project,index,semantic_id='KQ1001',locale='fr')
    assert 'Q8018' in original and 'exactMatch' in original
    assert 'Mode consultation' in original and 'name="csrf"' not in original
    assert 'name="id" value="KQ1001"' in html_page(project,index,semantic_id='KQ1001',locale='fr',writable=True,csrf_token='x'*32)
    assert 'name="id" value="KQ1001"' in original  # context retained when switching language
    missing=html_page(project,index,semantic_id='KQ1002',locale='fr')
    assert 'Traduction manquante' in missing


def test_coverage_pagination_301_languages(project,tmp_path):
    # Valid synthetic sparse catalog; do not invent missing translations.
    import itertools,string
    catalog=json.loads(project.catalog.read_text())
    tags=['z'+a+b for a,b in itertools.product(string.ascii_lowercase,string.ascii_lowercase)][:301]
    catalog['languages']=[{'tag':t,'fallbacks':[],'layers':[]} for t in tags]
    new=tmp_path/'catalog.json'
    new.write_text(json.dumps(catalog),encoding='utf-8')
    alternate=replace(project,catalog=new)
    content=html_page(alternate,None,view='coverage',locale=tags[-1],page=13)
    assert 'Langues (301)' in content and 'Page 13 / 13' in content
    assert tags[-1] in content and '0/3' in content
    assert 'KQ1001' in content  # clickable missing ids
    assert 'Page 13 / 13' in content


def test_projection_clean_vs_annotated(project):
    clean=html_page(project,None,view='projection',locale='fr',style='clean')
    annotated=html_page(project,None,view='projection',locale='fr',style='annotated')
    assert 'Saint Augustin' in clean and 'Saint Augustin' in annotated
    assert '<code>KQ1001</code>' not in clean
    assert '<code>KQ1001</code>' in annotated
    assert 'Exporter le JSON réversible' in clean


def request(server, method, path, body=None, headers=None):
    cn=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=8)
    cn.request(method,path,body=body,headers=headers or {})
    r=cn.getresponse();data=r.read();result=(r.status,dict(r.getheaders()),data)
    cn.close();return result

@pytest.fixture
def serving(project,index,tmp_path):
    workspace=tmp_path/'out'
    server=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(project,index,workspace=workspace))
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:yield server,workspace
    finally:server.shutdown();server.server_close();t.join(timeout=5)


def test_local_curate_stages_immutable_catalog_not_canon(serving,project):
    server,workspace=serving
    before={key:fw.sha256(getattr(project,key)) for key in ['graph','catalog','crosswalk','registry']}
    status,headers,body=request(server,'GET','/?view=workspace&id=KQ1002&locale=fr')
    assert status==200
    html=body.decode()
    token=re.search(r'name="csrf" value="([^"]+)"',html).group(1)
    payload={'csrf':token,'confirm':'yes','id':'KQ1002','locale':'fr',
             'term':'Grâce améliorée','reviewer':'local-user','reason':'Reviewed locally for example'}
    body=urlencode(payload).encode()
    headers={'Content-Type':'application/x-www-form-urlencoded',
             'Origin':f'http://127.0.0.1:{server.server_port}'}
    assert request(server,'POST','/curate',body,headers)[0]==201
    outputs=list((workspace/'curations').glob('*/catalog.json'))
    assert len(outputs)==1
    assert fw.resolve(outputs[0],'KQ1002','fr')['term']=='Grâce améliorée'
    assert {key:fw.sha256(getattr(project,key)) for key in before}==before
    assert fw.resolve(project.catalog,'KQ1002','fr')['status']=='missing'


def test_local_server_rejects_csrf_forgery_and_hosts(serving):
    server,workspace=serving
    status,_,_=request(server,'GET','/',headers={'Host':'evil.example'})
    assert status==403
    form=urlencode({'csrf':'fake','id':'KQ1002','locale':'fr','term':'Bad','reviewer':'a',
                   'reason':'b','confirm':'yes'}).encode()
    headers={'Content-Type':'application/x-www-form-urlencoded'}
    assert request(server,'POST','/curate',form,headers)[0]==403
    good_headers={**headers,'Origin':'https://malicious.example'}
    assert request(server,'POST','/curate',form,good_headers)[0]==403
    assert not list(workspace.glob('curations/*'))


def test_readonly_server_disallows_post(project,index):
    server=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(project,index))
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
        status,_,_=request(server,'POST','/curate')
        assert status==405
        status,_,body=request(server,'GET','/api/health')
        assert json.loads(body)['mode']=='read-only'
    finally:server.shutdown();server.server_close();t.join(timeout=5)


def test_downloaded_compact_can_restore_exact_graph(serving,project):
    server,_=serving
    status,headers,payload=request(server,'GET','/api/projection?locale=fr')
    assert status==200 and headers['Content-Disposition'].startswith('attachment;')
    graph=restore_compact(json.loads(payload),project)
    assert graph==fw.read_json(project.graph)
