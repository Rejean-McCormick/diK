"""V5.11 conservative canonical selection: real read-only derived view only."""
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from dik import federated_registry as fed
from dik import canonical_selection as sel


def write(root, relative, payload):
    path=root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    return path


def make(root, name, qids, *, same=False, conflict=False):
    owner=root/name
    owner.mkdir()
    artifacts=[]
    for i,q in enumerate(qids):
        rev=f'canon/domain/v11/updates/rev{i}'
        ns=f'kristal:{name}'
        mapping={'local_ref':{'namespace_id':ns,'id':'KQ1001'},'external_ref':{'system':'wikidata','id':q},
                 'relation':'exactMatch','status':'accepted','review':{'decision_id':'R-1234','evidence_refs':['KS11']}}
        links=[mapping]
        if conflict: links.append({**mapping,'external_ref':{'system':'wikidata','id':'Q99'}})
        entries=[{'id':'KQ1001','kind':'entity','status':'stable','label':'Mot','definition':'Sens déclaré'}]
        if i and not same: entries.append({'id':'KQ1002','kind':'entity','status':'stable','label':'Autre'})
        for contract,part,data in (
            ('kristal.v11.identity-registry','registry.json',{'namespace_id':ns,'identities':entries}),
            ('kristal.v11.semantic-graph','graph.json',{'namespace_id':ns}),
            ('kristal.v11.external-crosswalk','crosswalk.json',{'mappings':links}),
            ('kristal.v11.dictionary-catalog','dictionaries/catalog.json',{'namespace_id':ns})):
            path=f'{rev}/{part}'
            write(owner,path,data)
            artifacts.append({'path':path,'logical_contract':{'id':contract,'version':'11.0'}})
    write(owner,'canon/state.index.json',{'format':'kristal.authoring-state-index/2.0.0',
                                         'canonical_artifacts':artifacts})


def build(monkeypatch,root,path,selection_file=None):
    monkeypatch.setattr(fed,'discover',lambda _:[])
    return fed.build(official_root=root,output_dir=path,min_kristals=1,selection_file=selection_file)


def dbrow(out,kristal):
    with sqlite3.connect(out/'registry.sqlite3') as db:
        return db.execute('SELECT decision,selected_revision_dir,review_decision_id FROM canonical_selection WHERE kristal=?',(kristal,)).fetchone()


def test_singleton_only_source_view_and_queries(tmp_path,monkeypatch):
    root=tmp_path/'official';root.mkdir();make(root,'solo',['Q8018'])
    man=build(monkeypatch,root,tmp_path/'view')
    stats=man['canonical_selection']['statistics']
    assert stats['single_declared_view_revisions']==1
    assert stats['framework_authority_confirmed']==stats['new_global_approvals']==0
    assert dbrow(tmp_path/'view','solo')[0]=='SINGLE_DECLARED_DERIVED_VIEW'
    one=sel.query(tmp_path/'view',namespace='kristal:solo',semantic_id='KQ1001')
    assert one['results'][0]['wikidata_id']=='Q8018'
    assert len(sel.query(tmp_path/'view',wikidata_id='Q8018')['results'])==1
    assert one['approved_for_publication'] is False
    assert man['statistics']['reviewed_accepted_exact_links']==0
    assert fed.audit(tmp_path/'view')==man
    assert 'kristal:solo' not in (tmp_path/'view'/'manifest.json').read_text()
    with pytest.raises(ValueError):sel.query(tmp_path/'view',semantic_id='KQ1001')


def test_divergent_and_equivalent_are_not_chosen(tmp_path,monkeypatch):
    root=tmp_path/'official';root.mkdir()
    make(root,'divergent',['Q8018','Q1234'])
    make(root,'equivalent',['Q66','Q66'],same=True)
    make(root,'absent',[])
    man=build(monkeypatch,root,tmp_path/'view')
    stats=man['canonical_selection']['statistics']
    assert stats['multiple_divergent_unselected']==1
    assert stats['multiple_equivalent_evidence_unselected']==1
    assert stats['no_v11_revision']==1
    assert sel.query(tmp_path/'view',wikidata_id='Q66')['results']==[]
    assert dbrow(tmp_path/'view','divergent')[1] is None
    queue=tmp_path/'review-queue.json'
    result=sel.review_queue(tmp_path/'view',queue)
    assert result['pending_kristals']==2
    assert 'revision_dir' in queue.read_text()
    with pytest.raises(ValueError):sel.review_queue(tmp_path/'view',queue)
    assert fed.audit(tmp_path/'view')==man


def test_operator_decision_is_hash_pinned_and_no_approval(tmp_path,monkeypatch):
    root=tmp_path/'official';root.mkdir()
    make(root,'alpha',['Q8018','Q1234'])
    first=tmp_path/'initial';build(monkeypatch,root,first)
    with sqlite3.connect(first/'registry.sqlite3') as db:
        row=db.execute('''SELECT revision_dir,state_index_sha256,registry_sha256,crosswalk_sha256,catalog_sha256
             FROM canonical_revision_inputs WHERE kristal='alpha' ORDER BY revision_dir LIMIT 1''').fetchone()
    decision=dict(zip(('revision_dir','state_index_sha256','registry_sha256','crosswalk_sha256','catalog_sha256'),row))
    decision.update(kristal='alpha',review_decision_id='REVIEW-2026-11-24',reviewer='reviewer-01',
                    rationale='Source selected for derived view only following manual review')
    file=write(tmp_path,'selection.json',{'profile':sel.DECISIONS_PROFILE,'scope':'derived_view_only',
                                          'decisions':[decision]})
    man=build(monkeypatch,root,tmp_path/'chosen',file)
    assert man['canonical_selection']['statistics']['operator_pinned_view_revisions']==1
    assert man['canonical_selection']['statistics']['new_global_approvals']==0
    assert len(sel.query(tmp_path/'chosen',wikidata_id='Q8018')['results'])==1
    assert len(sel.query(tmp_path/'chosen',wikidata_id='Q1234')['results'])==0
    assert fed.audit(tmp_path/'chosen')==man
    original=root/'alpha'/decision['revision_dir']/'registry.json'
    original.write_text(original.read_text()+'\n',encoding='utf-8') # Same JSON, different bytes
    with pytest.raises(ValueError,match='stale'):
        build(monkeypatch,root,tmp_path/'refused',file)
    assert not (tmp_path/'refused').exists()


def test_bad_decision_and_same_revision_conflicts_fail_closed(tmp_path,monkeypatch):
    root=tmp_path/'official';root.mkdir();make(root,'solo',['Q8018'],conflict=True)
    man=build(monkeypatch,root,tmp_path/'view')
    assert man['canonical_selection']['statistics']['single_declared_view_revisions']==0
    assert dbrow(tmp_path/'view','solo')[0]=='SINGLE_REVISION_NOT_VERIFIED'
    assert sel.query(tmp_path/'view',wikidata_id='Q8018')['results']==[]
    no_authority=write(tmp_path,'invalid.json',{'profile':sel.DECISIONS_PROFILE,'scope':'global_authority','decisions':[]})
    with pytest.raises(ValueError):sel.read_decisions(no_authority)


def test_selection_cli_parser():
    from dik.cli import make_parser
    p=make_parser()
    assert p.parse_args(['world','federation-build','--official-root','x','--output-dir','y','--selection-file','review.json']).selection_file=='review.json'
    assert p.parse_args(['world','federation-selection-query','--dir','x','--wikidata-id','Q8018']).world_command=='federation-selection-query'
    assert p.parse_args(['world','federation-selection-review','--dir','x','--output-file','y']).world_command=='federation-selection-review'
