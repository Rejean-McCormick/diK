"""Multi-Kristal audit: real Framework fixture, no implicit identity or source writes."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from dik.cli import main
from dik.kristals14 import Kristals14Error, discover, scan_kristals14

REPO = Path(__file__).resolve().parents[1]
DEMO = REPO/'examples/demo'


def _dik_root(tmp_path):
    root=tmp_path/'diK'
    (root/'src/dik').mkdir(parents=True)
    (root/'pyproject.toml').write_text('[project]\nname="dik"\n')
    (root/'src/dik/cli.py').write_text('# placeholder')
    return root


def _kristal(root, name, with_manifest=True, corrupt=False):
    repo=root/name
    repo.mkdir(parents=True)
    (repo/'kristal.discovery.json').write_text('{"format":"kristal.discovery/1.0"}')
    if with_manifest:
        target=repo/'canon/domain/v11/updates/wikidata-2026-11-21-v11-2'
        shutil.copytree(DEMO, target)
        if corrupt:
            (target/'dictionaries/curated-fr.json').write_text('tampered')
    return repo


def _csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def test_portfolio_reports_all_kristals_and_unknown_not_as_missing(tmp_path):
    source=tmp_path/'source'
    source.mkdir()
    a=_kristal(source,'kristal-a')
    _kristal(source,'kristal-b', corrupt=True)
    _kristal(source,'kristal-legacy', with_manifest=False)
    original={p.relative_to(source):p.read_bytes() for p in source.rglob('*') if p.is_file()}
    dik=_dik_root(tmp_path)
    result=scan_kristals14(root=source, dik_root=dik, min_kristals=3)
    out=Path(result['dossier_rapports'])
    assert out.parent==dik/'reports/scans_14_langues'
    assert result['etat']=='PARTIEL'
    assert result['totaux']['kristals_decouverts']==3
    assert result['totaux']['kristals_evalues']==1
    assert result['totaux']['kristals_non_evaluables']==2
    assert result['totaux']['identites_KQ_KP_par_kristal']==3
    assert result['totaux']['verifications_linguistiques']==42
    assert len(_csv_rows(out/'couverture_kristals_langues.csv'))==42
    row_by_name={r['kristal']:r for r in _csv_rows(out/'kristals_14_langues.csv')}
    assert len(row_by_name['kristal-a']['registre_sha256'])==64
    no_coverage=[r for r in _csv_rows(out/'couverture_kristals_langues.csv')
                 if r['kristal']=='kristal-legacy']
    assert all(not r['identites_KQ_KP'] and not r['pourcentage_direct']
               for r in no_coverage)
    assert len(_csv_rows(out/'matrice_14_langues.csv'))==42
    assert len(_csv_rows(out/'lacunes_14_langues.csv'))==40
    assert len(_csv_rows(out/'kristals_14_langues.csv'))==3
    assert len(_csv_rows(out/'alertes_14_langues.csv'))>=2
    assert all(row['kristal']=='kristal-a' for row in _csv_rows(out/'matrice_14_langues.csv'))
    assert (out/'scan.log').is_file()
    assert json.loads((out/'rapport.json').read_text())['mode']=='LECTURE_SEULE'
    assert original=={p.relative_to(source):p.read_bytes() for p in source.rglob('*') if p.is_file()}


def test_portfolio_chooses_newest_coherent_revision(tmp_path):
    root=tmp_path/'root'
    root.mkdir()
    k=_kristal(root,'kristal-a')
    base=k/'canon/domain/v11/updates'
    shutil.copytree(base/'wikidata-2026-11-21-v11-2', base/'wikidata-2026-10-27-v11-1')
    (base/'wikidata-2026-11-30-v11-3').mkdir()
    (base/'wikidata-2026-11-30-v11-3/identity-registry.json').write_text('{}')
    result=scan_kristals14(root=root, dik_root=_dik_root(tmp_path))
    assert result['totaux']['kristals_evalues']==1
    assert 'v11-2' in result['kristals'][0]['revision']
    rows=_csv_rows(Path(result['dossier_rapports'])/'alertes_14_langues.csv')
    assert {r['code'] for r in rows}=={'REVISIONS_IGNORES','REVISIONS_PARTIELLES'}


def test_portfolio_rejects_misplaced_reports_and_minimum(tmp_path):
    root=tmp_path/'root'
    root.mkdir()
    _kristal(root,'one')
    dik=_dik_root(tmp_path)
    with pytest.raises(Kristals14Error, match='dossier diK'):
        scan_kristals14(root=root, dik_root=dik, reports_root=tmp_path/'somewhere')
    with pytest.raises(Kristals14Error, match='minimum'):
        scan_kristals14(root=root, dik_root=dik, min_kristals=2)
    assert not (dik/'reports').exists()
    result=scan_kristals14(root=root,dik_root=dik,reports_root=Path('reports/custom'))
    assert Path(result['dossier_rapports']).parent==dik/'reports/custom'


def test_portfolio_cli_and_symlink_guard(tmp_path,capsys):
    root=tmp_path/'root'
    root.mkdir()
    _kristal(root,'one')
    dik=_dik_root(tmp_path)
    assert main(['coverage','kristals14','--root',str(root),'--dik-root',str(dik)])==0
    assert 'verifications_linguistiques' in capsys.readouterr().out
    alias=tmp_path/'alias'
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(Kristals14Error, match='symbolique'):
        scan_kristals14(root=alias, dik_root=dik)


def test_portfolio_does_not_promote_demo_without_kristal_marker(tmp_path):
    root=tmp_path/'root'
    root.mkdir()
    (root/'examples').mkdir()
    shutil.copytree(DEMO, root/'examples/demo')
    assert discover(root)==[]


def test_portfolio_duplicate_leaf_names_remain_distinct(tmp_path):
    root=tmp_path/'root'
    root.mkdir()
    for repo in ('repo-a','repo-b'):
        (root/repo).mkdir()
        _kristal(root/repo, 'same-name')
    output=scan_kristals14(root=root, dik_root=_dik_root(tmp_path))
    labels=[item['kristal'] for item in output['kristals']]
    assert len(set(labels))==2
    assert set(labels)=={'repo-a/same-name', 'repo-b/same-name'}
    assert output['totaux']['verifications_linguistiques']==42
    assert output['totaux']['copies_exactes']==1
    assert len(_csv_rows(Path(output['dossier_rapports'])/'copies_exactes_14_langues.csv')) == 1


def test_portfolio_reuse_verified_external_catalog_without_auto_merging(tmp_path):
    import hashlib
    root=tmp_path/'root'
    root.mkdir()
    repo=_kristal(root,'local')
    selected=repo/'canon/domain/v11/updates/wikidata-2026-11-21-v11-2'
    alt=repo/'dictionary_candidates'
    (alt/'dictionaries').mkdir(parents=True)
    shutil.copyfile(selected/'identity-registry.example.json', alt/'identity-registry.json')
    shutil.copyfile(selected/'external-crosswalk.example.json', alt/'external-crosswalk.json')
    curated=json.loads((selected/'dictionaries/curated-fr.json').read_text())
    curated['language']='de'
    curated['entries'][0]['preferred_term']='Heiliger Augustinus'
    layer=alt/'dictionaries/curated-de.json'
    layer.write_text(json.dumps(curated,ensure_ascii=False))
    catalog={
        'schema_version':'11.0', 'artifact_type':'kristal_dictionary_catalog',
        'catalog_id':'external-verified-candidate',
        'namespace_id':curated['namespace_id'],
        'languages':[{'tag':'de', 'fallbacks':[], 'layers':[
            {'layer_id':'candidate-de','kind':'curated','priority':200,
             'path':'curated-de.json','sha256':hashlib.sha256(layer.read_bytes()).hexdigest()}
        ]}]
    }
    (alt/'dictionaries/catalog.json').write_text(json.dumps(catalog))
    report=scan_kristals14(root=root,dik_root=_dik_root(tmp_path))
    out=Path(report['dossier_rapports'])
    assert report['totaux']['catalogues_alternatifs_reperes']==1
    assert report['totaux']['catalogues_alternatifs_valides']==1
    assert report['totaux']['cellules_avec_candidat']==1
    candidates=_csv_rows(out/'catalogues_candidats_14_langues.csv')
    assert candidates[0]['etat_preuve']=='compatible_audite'
    found=_csv_rows(out/'traductions_a_recuperer_14_langues.csv')
    assert len(found)==1
    assert found[0]['semantic_id']=='KQ1001' and found[0]['locale']=='de'
    assert found[0]['libelle_candidat']=='Heiliger Augustinus'
    # A found outside term must NOT turn a nonconfigured canonical locale into direct.
    matrix=_csv_rows(out/'matrice_14_langues.csv')
    assert next(r for r in matrix if r['semantic_id']=='KQ1001' and r['locale']=='de')['etat']=='langue_non_configuree'


def test_portfolio_rejects_unproven_catalog_equivalence(tmp_path):
    root=tmp_path/'root'; root.mkdir()
    repo=_kristal(root,'local')
    alt=repo/'some_other_version/dictionaries'
    alt.mkdir(parents=True)
    selected=repo/'canon/domain/v11/updates/wikidata-2026-11-21-v11-2'
    changed=json.loads((selected/'dictionaries/catalog.json').read_text())
    changed['catalog_id']='unproven-unlinked-catalog'
    (alt/'catalog.json').write_text(json.dumps(changed))
    # The alternative has no accompanying registry/crosswalk; an identical
    # namespace alone is insufficient to accept its dictionary labels.
    result=scan_kristals14(root=root,dik_root=_dik_root(tmp_path))
    out=Path(result['dossier_rapports'])
    assert result['totaux']['catalogues_alternatifs_reperes']==1
    assert result['totaux']['catalogues_alternatifs_valides']==0
    assert result['totaux']['cellules_avec_candidat']==0
    assert _csv_rows(out/'catalogues_candidats_14_langues.csv')[0]['etat_preuve']=='rattachement_non_prouve'


def test_portfolio_corrupt_copy_is_not_counted_as_exact(tmp_path):
    root=tmp_path/'root'; root.mkdir()
    _kristal(root,'aaa')
    b=_kristal(root,'bbb')
    layer=b/'canon/domain/v11/updates/wikidata-2026-11-21-v11-2/dictionaries/curated-fr.json'
    layer.write_text('changed')
    report=scan_kristals14(root=root,dik_root=_dik_root(tmp_path))
    assert report['totaux']['copies_exactes']==0
    assert report['totaux']['kristals_evalues']==1
    assert report['totaux']['kristals_non_evaluables']==1


def test_portfolio_invalid_manifest_can_fall_back_to_a_complete_v11(tmp_path):
    root=tmp_path/'root'; root.mkdir()
    repo=_kristal(root,'foo')
    bad=repo/'z-invalid'
    bad.mkdir()
    (bad/'dik.project.json').write_text('{"bad":true}')
    report=scan_kristals14(root=root,dik_root=_dik_root(tmp_path))
    assert report['totaux']['kristals_evalues']==1
