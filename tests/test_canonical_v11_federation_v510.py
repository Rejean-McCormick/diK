"""V5.10: canonical state index, 180-style revisions, no false global approval."""
import json
from pathlib import Path

import pytest

from dik import canonical_v11, federated_registry as fed


def write(base, relative, value):
    p=base/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    return p


def make(root, kind='normal'):
    owner=root/'alpha';owner.mkdir()
    artifacts=[]
    for i,qid in enumerate(['Q8018','Q8018','Q9020']):
        rev=f'canon/domain/v11/updates/rev{i}'
        ns='kristal:test'
        texts={
          ('registry', 'kristal.v11.identity-registry', 'registry.json'):{'namespace_id':ns,'identities':[{'id':'KQ1001','kind':'entity','status':'stable','label':'Exemple'}]},
          ('graph','kristal.v11.semantic-graph','graph.json'):{'namespace_id':ns},
          ('crosswalk','kristal.v11.external-crosswalk','crosswalk.json'):{'mappings':[{
             'local_ref':{'namespace_id':ns,'id':'KQ1001'},
             'external_ref':{'system':'wikidata','id':qid},
             'relation':'exactMatch','status':'accepted',
             'review':{'decision_id':'REV1','evidence_refs':['KS10']}}]},
          ('catalog','kristal.v11.dictionary-catalog','dictionaries/catalog.json'):{'namespace_id':ns},
        }
        for (_,contract,filename),content in texts.items():
            rel=f'{rev}/{filename}'
            write(owner,rel,content)
            artifacts.append({'path':rel,'logical_contract':{'id':contract,'version':'11.0'}})
    artifacts.append({'path':'canon/missing.json','logical_contract':{'id':'special.native-state','version':'1'}})
    write(owner,'canon/state.index.json',{'canonical_artifacts':artifacts})
    return owner


def test_state_index_revision_dedup_not_approval(monkeypatch,tmp_path):
    root=tmp_path/'kristals';root.mkdir();make(root)
    monkeypatch.setattr(fed,'discover',lambda _:[])
    out=tmp_path/'registry'
    man=fed.build(official_root=root,output_dir=out,min_kristals=1)
    assert man['statistics']['reviewed_accepted_exact_links']==0
    assert man['statistics']['evaluable_kristals']==0
    c=man['canonical_v11']
    s=c['statistics']
    assert s['v11_revisions']==3==s['v11_revisions_observed']
    assert s['source_accepted_exact_per_revision_not_unique']==3
    assert s['distinct_accepted_exact_across_revisions_source_only']==2
    assert s['cross_revision_accepted_conflicts']==1
    assert s['canonical_missing_artifacts']==1
    assert s['new_global_approvals']==0 and s['selected_revisions']==0
    assert fed.audit(out)==man
    result=canonical_v11.query(out,wikidata_id='Q8018')
    assert len(result['results'])==2
    assert not result['approved_for_publication']
    assert all('UNSELECTED' in row['evidence_status'] for row in result['results'])
    with pytest.raises(ValueError,match='namespace'):
        canonical_v11.query(out,semantic_id='KQ1001')
    with pytest.raises(ValueError):
        canonical_v11.query(out,wikidata_id='Q8018',namespace='ns')


def test_untrusted_path_and_namespace_rejected(monkeypatch,tmp_path):
    root=tmp_path/'kristals';root.mkdir();owner=make(root)
    idx=owner/'canon/state.index.json'
    data=json.loads(idx.read_text(encoding='utf-8'))
    data['canonical_artifacts'].append({'path':'../../secrets.json','logical_contract':{'id':'kristal.v11.identity-registry'}})
    idx.write_text(json.dumps(data),encoding='utf-8')
    monkeypatch.setattr(fed,'discover',lambda _:[])
    man=fed.build(official_root=root,output_dir=tmp_path/'read',min_kristals=1)
    assert man['canonical_v11']['statistics']['canonical_missing_artifacts']==2


def test_cli_parser_revision_query():
    from dik.cli import make_parser
    args=make_parser().parse_args(['world','federation-revision-query','--dir','x','--wikidata-id','Q8018'])
    assert args.world_command=='federation-revision-query'
