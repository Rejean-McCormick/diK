"""Positive/negative tests: 126 official notion, exact Q/P, safe local catalogues."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from dik.cli import main
from dik.kristals14 import Kristals14Error
from dik.resolution14 import scan_resolution14

HERE = Path(__file__).resolve().parents[1]
DEMO = HERE/'examples/demo'


def _base(tmp_path):
    official = tmp_path/'kristal-public/kristals'
    official.mkdir(parents=True)
    dik = tmp_path/'diK'
    (dik/'src/dik').mkdir(parents=True)
    (dik/'pyproject.toml').write_text('name = "diK"\n')
    (dik/'src/dik/cli.py').write_text('# cli')
    return official, dik


def _project(official, name):
    root = official/name
    root.mkdir()
    (root/'kristal.discovery.json').write_text('{"format":"kristal.discovery/1.0"}')
    shutil.copytree(DEMO, root/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1')
    return root


def _rows(file):
    with Path(file).open('r', encoding='utf-8-sig', newline='') as src:
        return list(csv.DictReader(src, delimiter=';'))


def _alternate(base, term='Agustín'):
    root = base/'external/dataset1'
    root.mkdir(parents=True)
    for name in ('identity-registry.example.json','external-crosswalk.example.json','semantic-graph.example.json'):
        dst = name.replace('.example','')
        shutil.copy2(DEMO/name, root/dst)
    (root/'dictionaries').mkdir()
    layer = {'schema_version':'11.0', 'artifact_type':'kristal_curated_dictionary',
             'namespace_id':'example.org/kristal-demo', 'language':'es',
             'entries':[{'semantic_id':'KQ1001','preferred_term':term,
                         'alternate_terms':[], 'review':{'decision_id':'demo-es',
                         'reviewer':'demo', 'reason':'Test of independent lexical observation'}}]}
    content = json.dumps(layer, ensure_ascii=False)
    path = root/'dictionaries/curated-es.json'
    path.write_text(content, encoding='utf-8')
    catalog = {'schema_version':'11.0', 'artifact_type':'kristal_dictionary_catalog',
               'namespace_id':'example.org/kristal-demo', 'catalog_id':'demo-independent-es',
               'languages':[{'tag':'es', 'fallbacks':[], 'layers':[
                   {'layer_id':'demo-es', 'kind':'curated', 'priority':200,
                    'path':'curated-es.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}]}
    (root/'dictionaries/catalog.json').write_text(json.dumps(catalog))
    return root


def test_official_only_and_verified_catalogue_merge(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    _project(official,'physics')
    # Nested discovery copy must not become an official Kristal.
    copy = official/'bible'/ 'out' / 'copy'
    copy.mkdir(parents=True)
    (copy/'kristal.discovery.json').write_text('{}')
    _alternate(tmp_path)
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=2)
    assert result['totaux']['kristals_officiels']==2
    assert result['totaux']['kristals_evalues']==2
    assert result['totaux']['catalogue_raccorde']>=2
    assert result['traduction_entre_langues'] is False
    dest=Path(result['dossier_rapports'])
    es=[r for r in _rows(dest/'resolution_identifiants_14_langues.csv') if
        r['locale']=='es' and r['semantic_id']=='KQ1001']
    assert len(es)==2
    assert all(r['statut']=='catalogue_raccorde' and r['forme']=='Agustín' for r in es)
    assert len(_rows(dest/'kristals_officiels.csv'))==2
    assert dest.is_relative_to(dik/'reports')


def test_conflicting_verified_catalogues_do_not_pick_one(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    _alternate(tmp_path/'x', 'Term 1')
    _alternate(tmp_path/'y', 'Term 2')
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    dest=Path(result['dossier_rapports'])
    row=next(x for x in _rows(dest/'resolution_identifiants_14_langues.csv') if
             x['semantic_id']=='KQ1001' and x['locale']=='es')
    assert row['statut']=='conflit' and not row['forme']


def test_candidate_crosswalk_not_promoted_by_wikidata_dump(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    dump=tmp_path/'wikidata-entities.jsonl'
    dump.write_text(json.dumps({'id':'Q8018','labels':{
        'es':{'language':'es','value':'Agustín'},
        'de':{'language':'de','value':'Augustinus'}}})+'\n')
    result=scan_resolution14(official_root=official,sources_root=official,
                             dik_root=dik,min_kristals=1,wikidata_dump=dump,
                             approved_sha256=hashlib.sha256(dump.read_bytes()).hexdigest())
    rows=_rows(Path(result['dossier_rapports'])/'resolution_identifiants_14_langues.csv')
    approved=next(x for x in rows if x['semantic_id']=='KQ1001' and x['locale']=='es')
    candidate=next(x for x in rows if x['semantic_id']=='KQ1002' and x['locale']=='es')
    assert approved['statut']=='wikidata_observe' and approved['forme']=='Agustín'
    assert candidate['statut']=='non_resolu' and not candidate['forme']
    assert 'non_approuve' in candidate['statut_preuve']
    assert result['wikidata_dump_local']['empreinte_attendue_fournie'] is True


def test_mismatched_hash_no_output_published(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    dump=tmp_path/'wikidata-entities.jsonl'
    dump.write_text('{"id":"Q8018","labels":{}}\n')
    with pytest.raises(Kristals14Error, match='SHA-256'):
        scan_resolution14(official_root=official,sources_root=official,
                          dik_root=dik,min_kristals=1,wikidata_dump=dump,
                          approved_sha256='0'*64)
    assert not (dik/'reports').exists()


def test_isolated_catalogue_is_validated_against_official_registry(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    other = _alternate(tmp_path)
    (other/'identity-registry.json').unlink()
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    assert result['totaux']['catalogue_raccorde']>0
    sources=_rows(Path(result['dossier_rapports'])/'sources_dictionnaires.csv')
    assert any(x['etat']=='catalogue_raccorde_registre_officiel' for x in sources)


def test_report_missing_v11_does_not_inflate_failures(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    x=official/'legacy'
    x.mkdir()
    (x/'kristal.discovery.json').write_text('{}')
    result=scan_resolution14(official_root=official,sources_root=official,
                             dik_root=dik,min_kristals=2)
    assert result['totaux']['kristals_non_evaluables']==1
    assert result['totaux']['cellules_evaluees']==42
    assert result['etat']=='PARTIEL'


def test_cli_resolve14_reports_json(tmp_path,capsys):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    code=main(['coverage','resolve14','--official-root',str(official),
               '--sources-root',str(official),'--dik-root',str(dik), '--min-kristals','1'])
    assert code==0
    result=json.loads(capsys.readouterr().out)
    assert result['totaux']['kristals_officiels']==1


def test_refuses_wrong_official_root(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    with pytest.raises(Kristals14Error,match='Kristals officiels'):
        scan_resolution14(official_root=tmp_path/'kristal-public',sources_root=official,
                          dik_root=dik,min_kristals=1)


def test_contradictory_accepted_qp_source_rejected(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    other=_alternate(tmp_path)
    crosswalk=other/'external-crosswalk.json'
    data=json.loads(crosswalk.read_text())
    data['mappings'][0]['external_ref']['id']='Q987654321'
    crosswalk.write_text(json.dumps(data))
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    sources=_rows(Path(result['dossier_rapports'])/'sources_dictionnaires.csv')
    assert any(row['etat']=='crosswalk_contradictoire' for row in sources)
    assert result['totaux']['catalogue_raccorde']==0


def test_identifiants_non_resolus_does_not_include_resolved_sources(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    _alternate(tmp_path)
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    dest=Path(result['dossier_rapports'])
    unresolved=_rows(dest/'identifiants_non_resolus.csv')
    qualified=_rows(dest/'raccordements_a_qualifier.csv')
    assert all(r['statut'] in ('non_resolu','conflit') for r in unresolved)
    assert any(r['statut']=='catalogue_raccorde' for r in qualified)


def test_unregistered_id_in_isolated_catalogue_is_refused(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    other=_alternate(tmp_path)
    (other/'identity-registry.json').unlink()
    bad=other/'dictionaries/curated-es.json'
    layer=json.loads(bad.read_text())
    layer['entries'][0]['semantic_id']='KQ987654321'
    bad.write_text(json.dumps(layer))
    cat=other/'dictionaries/catalog.json'
    doc=json.loads(cat.read_text())
    doc['languages'][0]['layers'][0]['sha256']=hashlib.sha256(bad.read_bytes()).hexdigest()
    cat.write_text(json.dumps(doc))
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    assert result['totaux']['catalogue_raccorde']==0
    sources=_rows(Path(result['dossier_rapports'])/'sources_dictionnaires.csv')
    assert any(x['etat']=='audit_refuse' for x in sources)


def test_accepted_qp_can_be_inherited_from_audited_revision(tmp_path):
    official,dik=_base(tmp_path)
    kristal=_project(official,'bible')
    chosen=kristal/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1'
    # Officially selected source no longer has an accepted Q/P. It has a
    # genuine KQ-local curated label, so no imported Wikidata records rely on Q.
    crosswalk=chosen/'external-crosswalk.example.json'
    doc=json.loads(crosswalk.read_text())
    doc['mappings'][0]['status']='candidate'
    doc['mappings'][0].pop('review',None)
    crosswalk.write_text(json.dumps(doc))
    cat=chosen/'dictionaries/catalog.json'
    data=json.loads(cat.read_text())
    data['languages']=[{'tag':'fr','fallbacks':[], 'layers':[
        x for x in data['languages'][0]['layers'] if x['kind']=='curated']}]
    cat.write_text(json.dumps(data))
    other=_alternate(tmp_path)
    dump=tmp_path/'wikidata-entities.jsonl'
    dump.write_text(json.dumps({'id':'Q8018','labels':{'de':{'value':'Augustinus'}}})+'\n')
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1,wikidata_dump=dump)
    rows=_rows(Path(result['dossier_rapports'])/'resolution_identifiants_14_langues.csv')
    de=next(x for x in rows if x['semantic_id']=='KQ1001' and x['locale']=='de')
    assert de['statut']=='wikidata_observe'
    assert de['origine_lien_qp']=='crosswalk_autre_revision_auditee'
    assert de['identifiant_wikidata_accepte']=='Q8018'


def test_selected_catalogue_conflict_is_signalled_without_overriding(tmp_path):
    official,dik=_base(tmp_path)
    _project(official,'bible')
    other=_alternate(tmp_path)
    path=other/'dictionaries/curated-es.json'
    rec=json.loads(path.read_text())
    rec['language']='fr'
    rec['entries'][0]['preferred_term']='Autre Augustin'
    path.write_text(json.dumps(rec,ensure_ascii=False))
    catalog_path=other/'dictionaries/catalog.json'
    catalog=json.loads(catalog_path.read_text())
    lang=catalog['languages'][0]
    lang['tag']='fr'
    lang['layers'][0]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    catalog_path.write_text(json.dumps(catalog))
    result=scan_resolution14(official_root=official,sources_root=tmp_path,
                             dik_root=dik,min_kristals=1)
    row=next(x for x in _rows(Path(result['dossier_rapports'])/'resolution_identifiants_14_langues.csv')
             if x['semantic_id']=='KQ1001' and x['locale']=='fr')
    assert row['statut']=='catalogue_courant'
    assert row['forme']=='Saint Augustin'
    assert row['conflit_avec_catalogue_courant']=='oui'
    assert result['totaux']['conflits_de_revision_avec_courant']>=1
