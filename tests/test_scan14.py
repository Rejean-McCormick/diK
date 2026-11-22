"""diK scan14 additive contract: direct/fallback/absent semantics, no writes to canon."""
from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from dik.cli import main
from dik.scan14 import TARGET_LOCALES, scan14, Scan14Error

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'examples' / 'demo'
HANDOFF = ROOT / 'integrations' / 'unesco-mt1-10' / 'handoff.json'


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def test_scan14_snapshot_14_exact_and_missing_registry(tmp_path):
    output = tmp_path / 'new_report'
    report = scan14(project=FIX/'dik.project.json', output=output, handoff=HANDOFF)
    assert tuple(report['locales_cibles']) == TARGET_LOCALES
    assert report['identites_KQ_KP_registre'] == 3
    assert report['totaux_statuts'] == {'direct': 2, 'repli': 0, 'manquant': 4, 'langue_non_configuree': 36}
    registry = rows(output/'registre_14_langues_KQ_KP.csv')
    assert len(registry) == 42
    assert next(r for r in registry if r['semantic_id']=='KQ1001' and r['locale']=='fr')['etat'] == 'direct'
    assert next(r for r in registry if r['semantic_id']=='KQ1001' and r['locale']=='es')['etat'] == 'langue_non_configuree'
    assert all(r['statut_preuve']=='catalogue_audite' for r in registry)
    assert not (output/'inventaire_termes_konstellation.csv').exists()
    assert report['catalogue_selectionne_est_demo']
    assert len(rows(output/'lacunes_14_langues.csv')) == 40
    assert report['reseau_utilise'] is False


def test_scan14_readonly_and_does_not_overwrite(tmp_path):
    copied = tmp_path/'project'
    shutil.copytree(FIX, copied)
    original = {p.relative_to(copied): p.read_bytes() for p in copied.rglob('*') if p.is_file()}
    out = tmp_path/'scan'
    scan14(project=copied/'dik.project.json', output=out)
    assert original == {p.relative_to(copied): p.read_bytes() for p in copied.rglob('*') if p.is_file()}
    with pytest.raises(Scan14Error, match='existe'):
        scan14(project=copied/'dik.project.json', output=out)
    with pytest.raises(Scan14Error, match='source'):
        scan14(project=copied/'dik.project.json', output=copied/'report')


def test_scan14_cli(tmp_path, capsys):
    out=tmp_path/'CLI'
    code=main(['coverage','scan14','--project',str(FIX/'dik.project.json'), '--out',str(out)])
    assert code==0
    assert 'identites_KQ_KP_registre' in capsys.readouterr().out
    assert (out/'rapport.json').is_file()
    assert main(['coverage','scan14','--project',str(FIX/'dik.project.json'), '--out',str(out)])==2


def test_scan14_refuses_mutated_hash_and_no_publish(tmp_path):
    project=tmp_path/'project'
    shutil.copytree(FIX,project)
    (project/'dictionaries/curated-fr.json').write_text('tampered\n',encoding='utf-8')
    out=tmp_path/'scan'
    with pytest.raises(Exception):
        scan14(project=project/'dik.project.json',output=out)
    assert not out.exists()


def test_scan14_refuses_locale_drift(tmp_path):
    doc=json.loads(HANDOFF.read_text())
    doc['target_locales'].remove('pt')
    handoff=tmp_path/'handoff.json'
    handoff.write_text(json.dumps(doc))
    with pytest.raises(Scan14Error, match='14 langues'):
        scan14(project=FIX/'dik.project.json',output=tmp_path/'out',handoff=handoff)
    assert not (tmp_path/'out').exists()


def test_scan14_inventory_no_inferred_identity(tmp_path):
    corpus=tmp_path/'kon'
    (corpus/'data').mkdir(parents=True)
    (corpus/'src/components').mkdir(parents=True)
    (corpus/'data/demo.pack.json').write_text(json.dumps({
        'title':'Démo','description':'Corpus','synthetic':True,
        'entities':[{'id':'human-1','type':'human','label':'Augustin'}],
        'assertions':[], 'policies':[], 'sources':[],
        'registry':{'relations':[{'id':'relation1','label':{'fr':'Domaine','en':'Field'}}]},
    }),encoding='utf-8')
    (corpus/'src/components/X.svelte').write_text('<p>Bonjour les humains</p>',encoding='utf-8')
    out=tmp_path/'report'
    report=scan14(project=FIX/'dik.project.json',output=out,konstellation=corpus)
    terms=rows(out/'inventaire_termes_konstellation.csv')
    assert any(r['texte_fr']=='Augustin' and r['statut_alignement']=='non_aligne' for r in terms)
    assert all(not r['semantic_id'] for r in terms)
    assert report['termes_konstellation_non_alignes']>=1
    labels=rows(out/'libelles_multilingues_dans_pack.csv')
    assert len(labels)==14
    assert {r['locale'] for r in labels if r['etat_pack']=='direct_dans_pack'}=={'fr','en'}


def test_scan14_uses_real_dik_priority_and_fallback(tmp_path):
    project=tmp_path/'project'
    shutil.copytree(FIX,project)
    out=tmp_path/'out'
    catalog_path=project/'dictionaries/catalog.json'
    catalog=json.loads(catalog_path.read_text())
    catalog['languages'].append({'tag':'no','fallbacks':['fr'],'layers':[]})
    catalog_path.write_text(json.dumps(catalog))
    report=scan14(project=project/'dik.project.json',output=out)
    assert report['totaux_statuts']['repli']==1
    entry=next(r for r in rows(out/'registre_14_langues_KQ_KP.csv') if r['semantic_id']=='KQ1001' and r['locale']=='no')
    assert entry['etat']=='repli' and entry['langue_source']=='fr'
    assert entry['libelle_resolu']


def test_scan14_rejects_untrusted_mapping(tmp_path):
    mapping=tmp_path/'map.csv'
    mapping.write_text('konstellation_id;namespace_id;semantic_id;relation;status\nh1;example.org/kristal-demo;KQ1001;exactMatch;accepted\n',encoding='utf-8')
    with pytest.raises(Scan14Error,match='non disponible|non qualifi|mapping'):
        scan14(project=FIX/'dik.project.json',output=tmp_path/'out',mapping=mapping)
    assert not (tmp_path/'out').exists()
