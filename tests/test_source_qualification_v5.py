"""V5 qualification: observation is not publication or implicit translation."""
import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from dik.resource_locator import discover_resources, save_registry
from dik.source_qualification import (qualify_resources, _qid_lexicon_profile,
                                      observe_registered_qid_lexicon)
from dik.resolution14 import scan_resolution14

DEMO = Path(__file__).resolve().parents[1] / 'examples' / 'demo'


def _root(tmp_path):
    root = tmp_path / 'mycode'
    qdir = root / 'Grammatical-Framework' / 'gf-wikidata_repos_source' / 'gf-wikidata-tools' / 'extraction' / 'data'
    qdir.mkdir(parents=True)
    lex = qdir / 'qid-lexicon.jsonl'
    lex.write_text('\n'.join((
        json.dumps({'qid':'Q8018', 'labels':{'fr':'Saint Augustin','es':{'value':'Agustín'}}}),
        json.dumps({'qid':'Q8019', 'labels':{'es':'ne_pas_approuver'}}),
        json.dumps({'qid':'Q8018', 'labels':{'en':'Augustine'}}),
    ))+'\n', encoding='utf-8')
    gf = root/'Grammatical-Framework'/'GF_Lexicons_Archive'
    gf.mkdir(parents=True)
    (gf/'DictFre.gf').write_text('concrete DictFre of Dict = {}',encoding='utf-8')
    return root, lex, gf


def test_qualification_does_not_activate_and_does_not_duplicate(tmp_path):
    root, lex, gf = _root(tmp_path)
    dik=tmp_path/'diK';dik.mkdir()
    reg=discover_resources(sources_root=root)
    saved=save_registry(reg,dik_root=dik)
    report=qualify_resources(registry_file=saved['registry'],dik_root=dik)
    assert report['sources_found']==2
    assert report['activations']==0
    assert report['qid_lexicon_probe']['statistics']['explicit_labels_accepted_for_observation']==4
    assert Path(report['report_dir']).is_relative_to(dik/'reports')
    with (Path(report['report_dir'])/'source-qualification.csv').open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==2
    assert all(x['semantic_link']=='non_prouve_par_la_decouverte' for x in rows)
    assert all(x['rights_status']=='non_qualifie' for x in rows)
    assert all(not x['status'].startswith('actif') for x in rows)


def test_hash_change_is_reported_instead_of_trusted(tmp_path):
    root, lex, gf = _root(tmp_path)
    dik=tmp_path/'diK';dik.mkdir()
    saved=save_registry(discover_resources(sources_root=root),dik_root=dik)
    lex.write_text('{}\n', encoding='utf-8')
    report=qualify_resources(registry_file=saved['registry'],dik_root=dik)
    assert report['state']=='PARTIAL'
    assert report['by_status']['non_verifie']==1
    doc=json.loads(Path(report['report_dir'],'rapport.json').read_text(encoding='utf-8'))
    assert doc['activations']==0


def test_qid_explicit_labels_require_preapproved_qp_and_conflicts_refused(tmp_path):
    root, lex, gf = _root(tmp_path)
    doc=discover_resources(sources_root=root)
    forms,info=observe_registered_qid_lexicon(doc,wanted={'Q8018'},locales=('fr','es','en'))
    assert forms=={('Q8018','fr'):'Saint Augustin',('Q8018','es'):'Agustín',('Q8018','en'):'Augustine'}
    assert info['candidate_only'] and info['source_id']
    lex.write_text(lex.read_text()+json.dumps({'qid':'Q8018','labels':{'es':'CONTRADICTION'}})+'\n')
    doc=discover_resources(sources_root=root)
    forms,info=observe_registered_qid_lexicon(doc,wanted={'Q8018'},locales=('es','fr'))
    assert ('Q8018','es') not in forms
    assert ('Q8018','fr') in forms
    assert info['statistics']['conflicting_qp_locale']==1
    assert ('Q8019','es') not in forms


def test_no_lemma_gf_word_inferred_as_qid_label(tmp_path):
    p=tmp_path/'qid-lexicon.jsonl'
    p.write_text(json.dumps({'qid':'Q8018','lemma':'mot','gf_function':'word_N',
                             'forms':{'fr':'autre_mot'}})+'\n')
    forms,meta=_qid_lexicon_profile(p,wanted={'Q8018'},locales=('fr',))
    assert forms=={}
    assert meta['schema_known'] is False


def test_candidate_wikidata_never_alters_coverage(tmp_path):
    root,lex,gf=_root(tmp_path)
    official=root/'Kristal/kristal-public/kristals'
    official.mkdir(parents=True)
    test=official/'demo'
    test.mkdir()
    (test/'kristal.discovery.json').write_text('{}')
    shutil.copytree(DEMO,test/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1')
    dik=tmp_path/'diK';(dik/'src/dik').mkdir(parents=True)
    (dik/'src/dik/cli.py').write_text('# CLI')
    (dik/'pyproject.toml').write_text('name = \"dik\"')
    saved=save_registry(discover_resources(sources_root=root),dik_root=dik)
    result=scan_resolution14(official_root=official,sources_root=root,
                dik_root=dik,min_kristals=1,resource_registry=saved['registry'],
                observe_qid_lexicon=True)
    assert result['totaux']['kristals_officiels']==1
    assert result['totaux']['wikidata_qid_observations_non_publiees']>=1
    assert result['totaux']['wikidata_observe']==0  # candidate QID is NOT a dump
    assert result['wikidata_qid_lexicon']['candidate_only']
    with (Path(result['dossier_rapports'])/'wikidata_qid_observations_candidates.csv').open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f,delimiter=';'))
    assert rows and all(row['statut']=='observation_non_publiee' for row in rows)
    assert result['traduction_entre_langues'] is False


def test_actual_qid_keyed_jsonl_labels_exact_language_and_no_translation(tmp_path):
    p=tmp_path/'qid-lexicon.jsonl'
    p.write_text('\n'.join([
        json.dumps({'Q132469': {'fr':'dernier théorème de Fermat',
                                 'en':"Fermat's Last Theorem", 'nn':'Fermats siste teorem'}}, ensure_ascii=False),
        json.dumps({'Q172298': {'fr':'décomposition primaire', 'en':'primary decomposition'}}, ensure_ascii=False),
    ])+'\n', encoding='utf-8')
    forms, meta = _qid_lexicon_profile(p, wanted=None, locales=('fr','en','no','nn'))
    assert forms[('Q132469','fr')] == 'dernier théorème de Fermat'
    assert forms[('Q172298','en')] == 'primary decomposition'
    assert ('Q132469','no') not in forms  # nor should it copy `nn` or `nb`
    assert meta['schema_known'] is True
    assert meta['statistics']['schema_qp_keyed_locales'] == 2
    assert meta['statistics']['rows_with_qp_id'] == 2
    assert meta['candidate_only'] is True


def test_qid_keyed_lexicon_known_schema_even_when_no_wanted_id_matches(tmp_path):
    p=tmp_path/'qid-lexicon.jsonl'
    p.write_text('{"Q132469":{"fr":"dernier théorème de Fermat"}}\n', encoding='utf8')
    values, meta = _qid_lexicon_profile(p, wanted={'Q999999'}, locales=('fr',))
    assert values == {}
    assert meta['schema_known'] is True
    assert meta['statistics']['rows_matching_requested_qp'] == 0
    assert meta['statistics']['explicit_labels_accepted_for_observation'] == 0


def test_qid_keyed_collisions_and_unrelated_dict_rejected(tmp_path):
    p=tmp_path/'qid-lexicon.jsonl'
    rows=[{'Q132469':{'fr':'A','en':'Shared'}},
          {'Q132469':{'fr':'B','en':'Shared'}},
          {'Q132469':{'fr':'A'}},
          {'label':'autre'},
          {'Q132469':{'fr':'C'},'Q172298':{'fr':'D'}}]
    p.write_text('\n'.join(json.dumps(x) for x in rows)+'\n', encoding='utf8')
    found, meta=_qid_lexicon_profile(p,wanted={'Q132469'},locales=('fr','en'))
    assert found == {('Q132469','en'):'Shared'}
    assert meta['statistics']['conflicting_qp_locale'] == 1
    assert meta['statistics']['no_qp_id'] == 2


def test_real_pasted_50_records_sample_is_recognized():
    # The full 50-record data file stays on the user's PC, not committed in diK.
    # This test uses a minimal shape-equivalent sample instead.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as base:
        f=Path(base)/'qid-lexicon.jsonl'
        f.write_text(json.dumps({'Q132469':{'fr':'dernier théorème de Fermat','af':'Fermat se laaste stelling'}}, ensure_ascii=False)+'\n', encoding='utf-8')
        words,info=_qid_lexicon_profile(f,wanted={'Q132469'},locales=('fr','af'))
        assert len(words)==2 and info['schema_known'] and info['candidate_only']
