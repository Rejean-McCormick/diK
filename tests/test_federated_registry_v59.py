"""The federated view never renumbers, merges or approves a source candidate."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from dik import federated_registry as fed


def fake_file(folder, filename, content):
    target=folder/filename
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(content),encoding='utf-8')
    return target


def fixture(root, name, namespace, wikidata, status='accepted', evidence=True):
    owner=root/name
    owner.mkdir(parents=True)
    r=fake_file(owner,'identity-registry.json',{'namespace_id':namespace,'identities':[
        {'id':'KQ1001','kind':'entity','status':'stable'}, {'id':'KP2001','kind':'property','status':'stable'}]})
    g=fake_file(owner,'semantic-graph.json',{'namespace_id':namespace})
    c=fake_file(owner,'dictionaries/catalog.json',{'namespace_id':namespace})
    x=fake_file(owner,'external-crosswalk.json',{'mappings':[
        {'local_ref':{'namespace_id':namespace,'id':'KQ1001'},'external_ref':{'system':'wikidata','id':wikidata},
         'relation':'exactMatch','status':status, 'mapping_id':'M1',
         'review':{'decision_id':'R1','evidence_refs':['KS17'] if evidence else []}},
        {'local_ref':{'namespace_id':namespace,'id':'KP2001'},'external_ref':{'system':'wikidata','id':'Q40'},
         'relation':'exactMatch','status':'accepted','review':{'decision_id':'R2','evidence_refs':['KS17']}}
    ]})
    return SimpleNamespace(folder=owner,manifest=None,graph=g,registry=r,crosswalk=x,catalog=c)


def prep(monkeypatch,tmp_path, same_ns=False):
    root=tmp_path/'official';root.mkdir()
    a=fixture(root,'alpha','ns:first','Q8018')
    b=fixture(root,'beta','ns:first' if same_ns else 'ns:second','Q8018','candidate')
    candidates={name:SimpleNamespace(folder=x.folder,manifest=x) for name,x in [('alpha',a),('beta',b)]}
    monkeypatch.setattr(fed,'discover',lambda _:list(candidates.values()))
    monkeypatch.setattr(fed,'_select',lambda c:(c.manifest,'',0))
    monkeypatch.setattr(fed.dictionaries,'audit',lambda *args:None)
    return root,tmp_path/'view'


def test_bidirectional_and_no_candidate_promotion(monkeypatch,tmp_path):
    root,out=prep(monkeypatch,tmp_path)
    manifest=fed.build(official_root=root,output_dir=out,min_kristals=2)
    stats=manifest['statistics']
    assert stats['local_kq_kp_occurrences']==4
    assert stats['reviewed_accepted_exact_links']==1
    assert stats['unreviewed_or_candidate_links']==1
    assert stats['invalid_source_mapping_rows']==2
    assert fed.audit(out)==manifest
    left=fed.query(directory=out,namespace='ns:first',semantic_id='KQ1001')
    assert left['links'][0]['decision']=='ACCEPTED_EXACT_REVIEWED'
    assert left['identities'][0]['label'] is None
    back=fed.query(directory=out,wikidata_id='Q8018')
    assert {x['namespace_id'] for x in back['links']}=={'ns:first','ns:second'}
    assert sum(x['decision']=='ACCEPTED_EXACT_REVIEWED' for x in back['links'])==1
    with pytest.raises(fed.RegistryError,match='namespace'):
        fed.query(directory=out,semantic_id='KQ1001')
    with pytest.raises(fed.RegistryError):
        fed.build(official_root=root,output_dir=out,min_kristals=2)
    with pytest.raises(fed.RegistryError):
        fed.build(official_root=root,output_dir=root/'new',min_kristals=2)
    with pytest.raises(fed.RegistryError):
        fed.build(official_root=root,output_dir=tmp_path/'incomplete',min_kristals=126)


def test_duplicate_full_key_and_hash_tamper(monkeypatch,tmp_path):
    root,out=prep(monkeypatch,tmp_path,same_ns=True)
    manifest=fed.build(official_root=root,output_dir=out,min_kristals=2)
    assert manifest['statistics']['duplicate_full_local_keys']==2
    result=fed.query(directory=out,namespace='ns:first',semantic_id='KQ1001')
    assert result['status']=='DUPLICATE_NAMESPACE_LOCAL_KEY_REVIEW_REQUIRED'
    with (out/'registry.sqlite3').open('ab') as f:f.write(b'changed')
    with pytest.raises(fed.RegistryError,match='SHA256'):
        fed.audit(out)


def test_cli_presence():
    from dik.cli import make_parser
    for args in [('world','federation-build','--official-root','x','--output-dir','y'),
                 ('world','federation-audit','--dir','x'),
                 ('world','federation-query','--dir','x','--wikidata-id','Q1')]:
        assert make_parser().parse_args(args).world_command.startswith('federation-')
