"""V5.6 online requests always mocked: no internet used in CI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs,urlparse

import pytest

from dik.online_sources import (DEFAULT_USER_AGENT, PROVIDERS, TARGET_LOCALES,
                                _record_for, fetch_accepted, observe_online)


def repo(tmp_path):
    r=tmp_path/'dik'
    (r/'src/dik').mkdir(parents=True)
    (r/'src/dik/cli.py').write_text('# marker\n')
    (r/'pyproject.toml').write_text('[project]\nname = "dik"\nversion = "1.0"\n')
    return r


def fixture_response(*ids, extra=False):
    entities={}
    for qp in ids:
        entities[qp]={'id':qp,'type':'item' if qp.startswith('Q') else 'property',
                      'labels':{'fr':{'language':'fr','value':f'{qp} en français'},
                                'en':{'language':'en','value':f'{qp} English'},
                                'nb':{'language':'nb','value':'Norwegian Bokmål'},
                                'no':{'language':'nb','value':'fallback prohibited'},
                                'de':{'language':'de','value':'AA\nBB'},
                                'description':{'language':'description','value':'not a name'}}}
    return json.dumps({'success':1,'entities':entities},ensure_ascii=False).encode('utf-8')


def allowed_targets():
    return {('ns-a','KQ1'):'Q42',('ns-b','KQ2'):'Q42',('ns-a','KP3'):'P31'}, {
        'official_kristals':126,'evaluated':57,'accepted_identity_links':3,
        'unique_qp':2, 'contradictory_links_excluded':0,'crosswalk_sha256':{},
    }


def test_consent_and_scope_and_catalog(tmp_path):
    root=repo(tmp_path)
    with pytest.raises(ValueError,match='--allow-network'):
        fetch_accepted(official_root='unused',dik_root=root,targets_override=allowed_targets())
    assert tuple(x['id'] for x in PROVIDERS)==('wikidata_action_api','kaikki_wiktionary','gf_rgl')
    assert tuple(TARGET_LOCALES)==('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')


def test_network_fetch_resume_and_candidate_observation(tmp_path):
    root=repo(tmp_path)
    calls=[]
    def mocked(url,ids):
        assert url.startswith('https://www.wikidata.org/w/api.php?')
        p=parse_qs(urlparse(url).query)
        assert p['action']==['wbgetentities']
        assert p['languages']==['|'.join(TARGET_LOCALES)]
        assert p['maxlag']==['5']
        assert 'languagefallback' not in p
        assert 'KQ' not in url and 'KP' not in url
        calls.append(ids)
        return fixture_response(*ids)
    result=fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                          targets_override=allowed_targets(), batch_size=1,
                          delay=0,transport=mocked)
    assert result['status']=='COMPLETE'
    assert result['unique_accepted_qp_requested']==2
    assert result['new_qp_fetched']==2
    assert result['new_labels_observed']==4
    assert len(calls)==2
    index=Path(result['index'])
    forms,info=observe_online(index,wanted={'Q42','P31','Q99'})
    assert info['status']=='CACHE_PARTIAL'
    assert info['wikidata_qp_cached']==2
    assert info['explicit_labels_candidate']==4
    assert forms['Q42','fr']['form']=='Q42 en français'
    assert ('Q42','no') not in forms and ('Q42','nb') not in forms
    again=fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                         targets_override=allowed_targets(),batch_size=1,
                         delay=0,transport=mocked)
    assert again['new_qp_fetched']==0
    assert len(calls)==2
    # Changing just one byte of a blob must not be accepted as evidence.
    entry=json.loads(index.read_text())['entries']['Q42']
    blob=index.parent/'blobs'/(entry['response_sha256']+'.json')
    blob.write_bytes(blob.read_bytes()+b' ')
    with pytest.raises(ValueError,match='Blob'):
        observe_online(index,wanted={'Q42'})
    with pytest.raises(ValueError,match='Blob'):
        fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                       targets_override=allowed_targets(),transport=mocked)


def test_budget_and_network_error_keeps_previous_batches(tmp_path):
    root=repo(tmp_path)
    targets=({('n','KQ1'):'Q42',('n','KQ2'):'Q43',('n','KQ3'):'Q44'},
             {'official_kristals':126,'evaluated':57,'crosswalk_sha256':{}})
    calls=[]
    def broken(url,ids):
        calls.append(ids)
        if len(calls)==2:
            raise ValueError('faux 429')
        return fixture_response(*ids)
    r=fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                     targets_override=targets,batch_size=1,max_ids=3,
                     transport=broken,delay=0)
    assert r['status']=='PARTIAL_NETWORK_ERROR'
    assert r['new_qp_fetched']==1 and r['unique_qp_cached']==1
    r2=fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                      targets_override=targets,batch_size=1,max_ids=1,
                      transport=lambda url,ids:fixture_response(*ids),delay=0)
    assert r2['status']=='PARTIAL_BUDGET'
    assert r2['unique_qp_cached']==2


def test_redirect_and_missing_never_create_false_match():
    body=json.dumps({'success':1,'redirects':[{'from':'Q42','to':'Q43'}],
                     'entities':{'Q42':{'id':'Q43','labels':{
                         'fr':{'language':'fr','value':'NO'}}}}}).encode('utf-8')
    x=_record_for('Q42',body,'2026-11-23T00:00:00+00:00')
    assert x['status']=='needs_review_redirect_or_absent' and not x['labels']
    missing=_record_for('P31',json.dumps({'success':1,'entities':{
        'P31':{'id':'P31','missing':''}}}).encode(), 'x')
    assert missing['status']=='not_found' and not missing['labels']
    with pytest.raises(ValueError):
        _record_for('Q42',b'{"success":0,"entities":{}}','x')


def test_no_arbitrary_index_or_language_substitution(tmp_path):
    root=repo(tmp_path)
    def mocked(url,ids):return fixture_response(*ids)
    result=fetch_accepted(official_root='unused',dik_root=root,allow_network=True,
                          targets_override=allowed_targets(),transport=mocked,delay=0)
    with pytest.raises(ValueError,match='14 codes'):
        observe_online(result['index'],wanted={'Q42'},locales=('en','fr','nb'))
    with pytest.raises(ValueError):
        observe_online(Path(result['index']).parent/'other.json',wanted={'Q42'})


def test_cli_catalog_and_consent(tmp_path):
    from dik.cli import main
    from contextlib import redirect_stdout,redirect_stderr
    import io
    out=io.StringIO()
    with redirect_stdout(out):
        assert main(['sources','online-catalog'])==0
    assert 'wikidata_action_api' in out.getvalue()
    root=repo(tmp_path)
    stderr=io.StringIO()
    with redirect_stderr(stderr):
        assert main(['sources','online-fetch','--official-root','not-on-disk',
                     '--dik-root',str(root)])==2
    assert '--allow-network' in stderr.getvalue()


def test_real_demo_crosswalk_online_audit_and_redacted_export(tmp_path):
    from dik.resolution14 import scan_resolution14
    from dik.online_sources import accepted_official_qp
    from dik.v53_export import export_v53
    import csv,shutil,zipfile
    demo=Path(__file__).resolve().parents[1]/'examples/demo'
    official=tmp_path/'kristal-public/kristals'
    project=official/'bible'
    project.mkdir(parents=True)
    (project/'kristal.discovery.json').write_text('{"format":"kristal.discovery/1.0"}')
    shutil.copytree(demo,project/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1')
    root=repo(tmp_path)
    links,meta=accepted_official_qp(official,min_kristals=1)
    assert links[('example.org/kristal-demo','KQ1001')]=='Q8018'
    assert ('example.org/kristal-demo','KQ1002') not in links
    def fake(url,ids):
        return json.dumps({'success':1,'entities':{qp:{'id':qp,'labels':{
            'es':{'language':'es','value':'Palabra nueva'},
            'en':{'language':'en','value':'Old test name'}}} for qp in ids}}).encode()
    fetch=fetch_accepted(official_root=official,dik_root=root,min_kristals=1,
                         allow_network=True,transport=fake,delay=0)
    original=scan_resolution14(official_root=official,sources_root=official,
                               dik_root=root,min_kristals=1)
    audited=scan_resolution14(official_root=official,sources_root=official,
                              dik_root=root,min_kristals=1,online_index=fetch['index'])
    assert audited['totaux']['cellules_evaluees']==original['totaux']['cellules_evaluees']
    for status in ('catalogue_courant','catalogue_raccorde','wikidata_observe',
                   'conflit','non_resolu'):
        assert audited['totaux'][status]==original['totaux'][status]
    assert audited['wikidata_online']['candidate_rows_for_kristals']>=1
    folder=Path(audited['dossier_rapports'])
    with (folder/'wikidata_online_observations_candidates.csv').open(encoding='utf-8-sig') as fd:
        rows=list(csv.DictReader(fd,delimiter=';'))
    assert any(x['wikidata_qp']=='Q8018' and x['forme_candidate']=='Palabra nueva' for x in rows)
    assert all(x['semantic_id']=='KQ1001' for x in rows)
    with (folder/'wikidata_online_potential_coverage.csv').open(encoding='utf-8-sig') as fd:
        summary=list(csv.DictReader(fd,delimiter=';'))
    assert len(summary)==14 and all(x['nouvelles_formes_publiees']=='0' for x in summary)
    report=export_v53(dik_root=root,resolution_dir=folder,version='v56')
    with zipfile.ZipFile(report['zip']) as archive:
        assert archive.testzip() is None
        content=archive.read('wikidata_online_observations_candidates.csv').decode('utf-8-sig')
        assert 'Palabra nueva' not in content
        assert 'source_url' in content
        assert 'wikidata_online' in archive.read('synthese_expurgee.json').decode()
