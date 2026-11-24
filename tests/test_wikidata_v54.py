"""V5.4: local schema shapes observed in the Windows V5.3 report.

Fixtures use the field NAMES actually present in the local schema report; the
example VALUES are synthetic and must not be mistaken for the real source data.
"""
import hashlib
import json
from pathlib import Path

from dik.scan14 import TARGET_LOCALES
from dik.wikidata_v53 import recognize, probe, scan_file, observe_thematic_v53


def _entry(tmp_path, records):
    path=tmp_path/'identity-candidates.jsonl'
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf-8')
    return {'path':str(path),'root':str(tmp_path),'source_id':'synthetic-1',
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'size_bytes':path.stat().st_size, 'kind':'wikidata_thematic_candidate',
            'allowed_for_resolution':False}


def _scan(tmp_path, entry, *, wanted=None, accepted=None, **opts):
    return scan_file(entry,wanted=wanted or {'Q8018','P31'},
        accepted_links=accepted or {},locales=tuple(TARGET_LOCALES),
        checkpoint_dir=tmp_path/'reports'/'cp',**opts)


def test_identity_candidates_observed_with_comparison_not_promoted(tmp_path):
    rows=[
      {'semantic_id':'KQ1001','external_id':'Q8018','namespace':'example.org/one',
       'identity_status':'accepted','reason':'untrusted-source-claim'},
      {'semantic_id':'KQ1001','external_id':'Q765','namespace':'example.org/one',
       'identity_status':'candidate','reason':'alternate'},
      {'semantic_id':'KP2','external_id':'P31','namespace':'example.org/one',
       'identity_status':'candidate','reason':'property'},
      {'semantic_id':'KQ1001','external_id':'Q8018','namespace':'example.org/two',
       'identity_status':'accepted','reason':'same-string-other-namespace'},
    ]
    entry=_entry(tmp_path,rows)
    observed,overlaps,meta=_scan(tmp_path,entry,
          accepted={('example.org/one','KQ1001'):'Q8018',('example.org/one','KP2'):'P31'})
    assert probe(Path(entry['path']))['schema_id']=='local_identity_candidate/1'
    assert meta['completed'] and meta['rows_with_qp']==4
    assert meta['status']=='no_eligible_lexical_identity'
    assert not observed and not overlaps
    assert meta['candidate_links_count']==4
    assert meta['candidate_links_consistent']==2
    assert meta['candidate_links_contradictory']==1
    evidence=meta['candidate_link_evidence']
    assert {(e['namespace_id'],e['external_id'],e['comparison']) for e in evidence}=={
        ('example.org/one','Q8018','consistent_with_existing_accepted'),
        ('example.org/one','Q765','contradicts_existing_accepted'),
        ('example.org/one','P31','consistent_with_existing_accepted'),
        ('example.org/two','Q8018','no_existing_accepted'),
    }
    assert meta['activations']==0
    assert len(meta['nonlexical_accepted_qp_evidence'])==2


def test_forged_namespace_and_wrong_identifier_types_are_rejected(tmp_path):
    values=[
      {'semantic_id':'KQ5','external_id':'P31','namespace':'x','identity_status':'accepted','reason':''},
      {'semantic_id':'KP5','external_id':'Q8018','namespace':'x','identity_status':'accepted','reason':''},
      {'semantic_id':'KQ0','external_id':'Q8018','namespace':'x','identity_status':'accepted','reason':''},
      {'semantic_id':'KQ5','external_id':'Q8018','namespace':'','identity_status':'accepted','reason':''},
      {'semantic_id':'KQ5','external_id':'http://wikidata.org/entity/Q8018','namespace':'x','identity_status':'accepted','reason':''},
    ]
    entry=_entry(tmp_path,values)
    _,_,meta=_scan(tmp_path,entry)
    assert meta['schema_id']=='local_identity_candidate/1'
    assert meta['status']=='schema_verified_no_qp_extracted'
    assert meta['candidate_links_count']==0


def test_real_report_field_names_for_statements_are_nonlexical(tmp_path):
    rows=[{'wikidata_subject':'Q8018','wikidata_property':'P31',
           'semantic_subject_candidates':['KQ1001'],
           'semantic_property_candidates':['KP5'],
           'evidence':{'label':'NEVER USE'},
           'assertion_regime':'candidate','checksum_verification':False,
           'external_seed_keys':[],'format':'v1','full_source_claim':False}]
    entry=_entry(tmp_path,rows)
    out,overlaps,meta=_scan(tmp_path,entry)
    assert meta['completed'] and meta['schema_id']=='local_wikidata_statement/1'
    assert out==[]
    assert len(overlaps)==1 and overlaps[0]['qp']=='Q8018'
    assert overlaps[0]['role']=='entity_subject'
    nonlex=meta['nonlexical_accepted_qp_evidence']
    assert len(nonlex)==1 and nonlex[0]['qp']=='P31'
    assert nonlex[0]['role']=='property_predicate'
    assert meta['candidate_links_count']==0
    assert meta['explicit_labels_for_accepted_qp']==0


def test_wikidata_property_only_is_never_joined_as_subject(tmp_path):
    entry=_entry(tmp_path,[{
        'wikidata_subject':'Q999','wikidata_property':'P31',
        'semantic_subject_candidates':['KQ1001'],
        'semantic_property_candidates':['KP31'],'evidence':['Q8018']}])
    _,overlaps,meta=_scan(tmp_path,entry,wanted={'P31'})
    assert overlaps==[]
    assert meta['status']=='complete_no_accepted_qp_overlap'
    assert meta['nonlexical_accepted_qp_distinct']==1


def test_candidate_checkpoint_resume_rechecks_acceptance_and_no_duplicates(tmp_path):
    rows=[{'semantic_id':'KQ1001','external_id':'Q8018','namespace':'ns',
          'identity_status':'candidate','reason':''} for _ in range(4)]
    entry=_entry(tmp_path,rows)
    one,_,meta=_scan(tmp_path,entry,accepted={('ns','KQ1001'):'Q8018'},max_rows_per_pass=2)
    assert meta['status']=='partial_budget' and meta['candidate_links_count']==2
    two,_,meta=_scan(tmp_path,entry,accepted={('ns','KQ1001'):'Q8018'})
    assert meta['completed'] and meta['candidate_links_count']==4 and meta['resumed']
    assert not one and not two
    _,_,newmeta=_scan(tmp_path,entry,accepted={('ns','KQ1001'):'Q123'})
    assert not newmeta['resumed'] and newmeta['candidate_links_contradictory']==4


def test_empty_local_jsonl_has_explicit_empty_status(tmp_path):
    entry=_entry(tmp_path,[])
    out,hits,meta=_scan(tmp_path,entry)
    assert not out and not hits
    assert meta['status']=='empty_source' and meta['completed']
    assert not meta['candidate_links_count']


def test_observer_aggregates_candidate_counts_without_lexical_forms(tmp_path):
    entries=[]
    for i, data in enumerate([
       {'semantic_id':'KQ1001','external_id':'Q8018','namespace':'ns',
        'identity_status':'candidate','reason':''},
       {'wikidata_subject':'Q8018','wikidata_property':'P31',
        'semantic_subject_candidates':[],'semantic_property_candidates':[], 'evidence':{}},
    ]):
        folder=tmp_path/str(i);folder.mkdir()
        e=_entry(folder,[data]);e['source_id']=f'synthetic-{i}';entries.append(e)
    candidates,profiles,summary,overlaps=observe_thematic_v53({'sources':entries},
        wanted={'Q8018','P31'},accepted_links={('ns','KQ1001'):'Q8018'},
        locales=tuple(TARGET_LOCALES),checkpoint_dir=tmp_path/'reports'/'cp')
    assert not candidates and summary['candidate_forms']==0
    assert summary['candidate_identity_links']==1
    assert summary['statement_sources_completed']==1
    assert summary['nonlexical_qp_observations']==2
    assert summary['activations']==0
    assert len(overlaps)==1


def test_resolution14_wires_new_candidate_and_role_reports(tmp_path):
    """Integration: still no published words, but both new CSVs get real evidence."""
    import csv
    import shutil
    from dik.resource_locator import discover_resources, save_registry
    from dik.resolution14 import scan_resolution14
    demo=Path(__file__).resolve().parents[1]/'examples'/'demo'
    root=tmp_path/'mycode'
    official=root/'Kristal/kristal-public/kristals'
    target=official/'demo'
    target.mkdir(parents=True)
    (target/'kristal.discovery.json').write_text('{}')
    shutil.copytree(demo,target/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1')
    src=root/'Kristal/locals/Kristal-Demo/external-source-library/wikidata/maxwd-synthetic'
    src.mkdir(parents=True)
    (src/'identity-candidates.jsonl').write_text(json.dumps({
        'semantic_id':'KQ1001','external_id':'Q8018','namespace':'example.org/kristal-demo',
        'identity_status':'accepted','reason':'source-claim-is-not-evidence'})+'\n')
    (src/'statements.jsonl').write_text(json.dumps({
        'wikidata_subject':'Q8018','wikidata_property':'P31',
        'semantic_subject_candidates':['KQ1001'],
        'semantic_property_candidates':[],'evidence':['untrusted']})+'\n')
    dik=tmp_path/'diK'
    (dik/'src/dik').mkdir(parents=True)
    (dik/'src/dik/cli.py').write_text('# fixture')
    (dik/'pyproject.toml').write_text('name = "dik"')
    reg=save_registry(discover_resources(sources_root=root),dik_root=dik)['registry']
    original=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
       min_kristals=1,resource_registry=reg)
    updated=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
       min_kristals=1,resource_registry=reg,observe_wikidata_thematic=True)
    assert updated['totaux']['cellules_evaluees']==original['totaux']['cellules_evaluees']
    for k in ('catalogue_courant','catalogue_raccorde','wikidata_observe','non_resolu','conflit'):
        assert updated['totaux'][k]==original['totaux'][k]
    assert updated['wikidata_v54']['candidate_identity_links_consistent']==1
    assert updated['wikidata_v54']['nonlexical_qp_observations']>=1
    target_dir=Path(updated['dossier_rapports'])
    with (target_dir/'wikidata_identity_links_candidates.csv').open(encoding='utf-8-sig',newline='') as f:
        values=list(csv.DictReader(f,delimiter=';'))
    assert len(values)==1
    assert values[0]['comparison']=='consistent_with_existing_accepted'
    assert values[0]['candidate_only']=='True'
    with (target_dir/'wikidata_nonlexical_qp_observations.csv').open(encoding='utf-8-sig',newline='') as f:
        roles=list(csv.DictReader(f,delimiter=';'))
    assert {x['role'] for x in roles}>= {'crosswalk_candidate'}
    from dik.v53_export import export_v53
    exported=export_v53(dik_root=dik,resolution_dir=target_dir,registry_file=reg)
    import zipfile
    with zipfile.ZipFile(exported['zip']) as z:
        assert 'wikidata_identity_links_candidates.csv' in z.namelist()
        assert 'wikidata_nonlexical_qp_observations.csv' in z.namelist()
        assert 'C:\\' not in z.read('wikidata_identity_links_candidates.csv').decode('utf-8')
    assert Path(exported['zip']).name.startswith('DIK_V5_4_BILAN_')


def test_candidate_identity_budget_is_explicit_and_resumeable(tmp_path):
    rows=[{'semantic_id':f'KQ{n}','external_id':'Q8018','namespace':'ns',
          'identity_status':'candidate','reason':''} for n in (1,2,3)]
    entry=_entry(tmp_path,rows)
    _,_,first=_scan(tmp_path,entry,max_pairs=2)
    assert first['status']=='partial_budget' and first['candidate_links_count']==2
    assert not first['completed'] and first['lines_read']==2
    _,_,second=_scan(tmp_path,entry,max_pairs=3)
    assert second['status']=='no_eligible_lexical_identity' and second['completed']
    assert second['candidate_links_count']==3 and second['resumed']
