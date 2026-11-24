"""V5.5 tests: the four supplied gf-wikidata JSON *arrays*, not JSONL."""
import hashlib
import json
from pathlib import Path

import pytest

from dik.scan14 import TARGET_LOCALES
from dik.wikidata_json_array import ArraySyntaxError, iter_objects, peek_array
from dik.wikidata_v53 import probe, scan_file


def _entry(folder, name, rows):
    folder.mkdir(parents=True, exist_ok=True)
    p=folder/name
    p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'source_id':'v55-'+name, 'path':str(p), 'root':str(folder),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'size_bytes':p.stat().st_size, 'kind':'wikidata_thematic_candidate',
            'allowed_for_resolution':False}


def _entity(qp='Q16', *, en='Canada', sv='Kanada', url=None):
    return {'url':url or f'http://www.wikidata.org/entity/{qp}',
            'labels':{'en':en,'sv':sv,'jp':'カナダ','zh':'加拿大','el':None,'bn':None},
            'descriptions':{'en':'=TEST_DESCRIPTION_NEVER_USE','sv':'Test description'}}


def _scan(folder, entry, *, wanted=('Q16',), budget=0):
    return scan_file(entry,wanted=set(wanted),locales=TARGET_LOCALES,
                     checkpoint_dir=folder/'reports'/'cp',max_rows_per_pass=budget)


def test_json_array_real_shape_and_explicit_locales(tmp_path):
    e=_entry(tmp_path,'Country.jsonl',[_entity()])
    p=Path(e['path'])
    assert peek_array(p)
    hint=probe(p)
    assert hint['status']=='schema_verified'
    assert hint['container']=='json_array'
    assert hint['schema_id']=='wikidata_entity_url_labels/1'
    forms,hits,meta=_scan(tmp_path,e)
    assert meta['completed'] and meta['rows_valid_json']==1
    assert meta['status']=='candidate_labels_observed'
    assert len(hits)==1 and hits[0]['role']=='lexical_entity'
    assert {(r['locale'],r['form']) for r in forms}=={('en','Canada'),('sv','Kanada')}
    assert 'jp' not in {r['locale'] for r in forms}
    assert all(r['form']!='=TEST_DESCRIPTION_NEVER_USE' for r in forms)
    assert meta['activations']==0


def test_incremental_resume_preserves_distinct_entries(tmp_path):
    e=_entry(tmp_path,'City.jsonl',[_entity('Q111',en='First'),_entity(),_entity('Q222',en='Third')])
    one,hits,meta=_scan(tmp_path,e,budget=1)
    assert meta['status']=='partial_budget' and meta['rows_valid_json']==1
    assert not one and not hits
    second,hits,meta=_scan(tmp_path,e,budget=1)
    assert meta['status']=='partial_budget' and meta['rows_valid_json']==2
    assert meta['resumed'] and len(hits)==1 and len(second)==2
    final,hits,meta=_scan(tmp_path,e)
    assert meta['completed'] and meta['rows_valid_json']==3
    assert len(hits)==1 and len(final)==2
    again,hits,meta=_scan(tmp_path,e)
    assert meta['completed'] and meta['resumed'] and len(again)==2


def test_schema_validation_refuses_fake_url_and_confusable_language(tmp_path):
    e=_entry(tmp_path,'University.jsonl',[_entity(url='https://evil.example/entity/Q16')])
    assert probe(Path(e['path']))['status']=='schema_unknown'
    forms,hits,meta=_scan(tmp_path,e)
    assert not forms and not hits and meta['status']=='schema_unknown'
    assert not meta['completed']


def test_nulls_strings_and_escaped_delimiters(tmp_path):
    e=_entry(tmp_path,'City.jsonl',[_entity(en='A }, { [ bracket',sv='Quote: " and \\')])
    forms,hits,meta=_scan(tmp_path,e)
    assert meta['completed'] and meta['status']=='candidate_labels_observed'
    assert len(forms)==2 and len(hits)==1


def test_truncated_array_never_claims_no_overlap(tmp_path):
    e=_entry(tmp_path,'City.jsonl',[_entity()]+[_entity('Q'+str(1000+i)) for i in range(130)])
    p=Path(e['path'])
    p.write_bytes(p.read_bytes()[:-1])  # remove the closing ']'
    e['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();e['size_bytes']=p.stat().st_size
    forms,hits,meta=_scan(tmp_path,e)
    assert meta['status']=='incomplete_errors' and not meta['completed']
    assert len(forms)==2 and len(hits)==1
    assert meta['rows_valid_json']==131


def test_source_changed_invalidates_checkpoint(tmp_path):
    e=_entry(tmp_path,'Country.jsonl',[_entity()])
    forms,hits,meta=_scan(tmp_path,e,budget=1)
    p=Path(e['path']);p.write_text(json.dumps([_entity('Q17')]),encoding='utf-8')
    forms,hits,meta=_scan(tmp_path,e)
    assert meta['status']=='pointer_stale' and not forms and not hits


def test_array_syntax_rejects_trailing_comma_and_tail(tmp_path):
    for data in ('[{"x":1},]', '[{"x":1}] garbage', '[{"x":1} {"x":2}]'):
        p=tmp_path/'bad.jsonl';p.write_text(data)
        with p.open('rb') as stream:
            with pytest.raises(ArraySyntaxError):
                list(iter_objects(stream))


def test_actual_supplied_shapes_are_scannable_without_copying_sources(tmp_path):
    # A minimal representative of the real City/Country/University/Part_of world files.
    names=('City.jsonl','Country.jsonl','University.jsonl','Part_of world.jsonl')
    ids=('Q69747','Q16','Q75478','Q46')
    for n,qp in zip(names,ids):
        folder=tmp_path/n.replace(' ','_')
        e=_entry(folder,n,[_entity(qp,en=n,sv='test')])
        forms,hits,meta=_scan(folder,e,wanted=(qp,))
        assert meta['schema_id']=='wikidata_entity_url_labels/1'
        assert meta['container']=='json_array' and meta['completed']
        assert len(forms)==2 and len(hits)==1


def test_resolve14_writes_json_array_candidates_without_coverage_inflation(tmp_path):
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
    src=root/'Grammatical-Framework/gf-wikidata_repos_source/gf-wikidata-tools/data'
    src.mkdir(parents=True)
    _entry(src,'Country.jsonl',[_entity('Q8018',en='Example English',sv='Exempel på svenska')])
    dik=tmp_path/'diK'
    (dik/'src/dik').mkdir(parents=True)
    (dik/'src/dik/cli.py').write_text('# fixture')
    (dik/'pyproject.toml').write_text('name="dik"')
    reg=save_registry(discover_resources(sources_root=root),dik_root=dik)['registry']
    plain=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
                           min_kristals=1,resource_registry=reg)
    updated=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
                             min_kristals=1,resource_registry=reg,
                             observe_wikidata_thematic=True)
    assert updated['wikidata_v55']['json_array_sources_completed']==1
    assert updated['wikidata_v55']['json_array_rows_read']==1
    assert updated['wikidata_v55']['candidate_forms']==2
    for key in ('catalogue_courant','catalogue_raccorde','wikidata_observe','non_resolu','conflit'):
        assert updated['totaux'][key]==plain['totaux'][key]
    report=Path(updated['dossier_rapports'])
    with (report/'wikidata_schema_profiles.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f,delimiter=';'))
    assert any(row['container']=='json_array' for row in rows)
    with (report/'wikidata_forms_candidates.csv').open(encoding='utf-8-sig',newline='') as f:
        forms=list(csv.DictReader(f,delimiter=';'))
    assert {(r['locale'],r['form']) for r in forms}=={
        ('en','Example English'),('sv','Exempel på svenska')}
    assert all(r['candidate_status']=='candidate_unpublished' for r in forms)
