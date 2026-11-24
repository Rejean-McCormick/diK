"""V5.2: provenance-first observations from Q/P thematic source JSONL."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from dik.resource_locator import discover_resources, save_registry
from dik.scan14 import TARGET_LOCALES
from dik.source_qualification import qualify_resources
from dik.wikidata_thematic import _explicit_row, _profile, observe_thematic_sources
from dik.resolution14 import scan_resolution14

DEMO = Path(__file__).resolve().parents[1] / 'examples' / 'demo'


def _setup(tmp_path):
    root=tmp_path/'mycode'
    folder=root/'Grammatical-Framework/gf-wikidata_repos_source/gf-wikidata-tools/data'
    folder.mkdir(parents=True)
    first=folder/'City.jsonl'
    first.write_text('\n'.join([
        json.dumps({'id':'Q8018','labels':{'fr':{'value':'Augustin'},'en':'Augustine','nb':'not-no'}}),
        json.dumps({'Q8019':{'fr':'Not accepted','en':'Unaccepted'}}),
        json.dumps({'qid':'Q8018','labels':{'es':'Agustín'}}),
        json.dumps({'qid':'Q8018','lemma':'Should never be a label','forms':{'de':'No'}}),
        json.dumps({'id':'L321','labels':{'fr':'lexeme is not entity'}}),
        json.dumps({'id':'Q8018','labels':{'nn':'Nynorsk only'}}),
    ])+'\n',encoding='utf-8')
    second=folder/'Country.jsonl'
    second.write_text(json.dumps({'Q8018':{'fr':'Augustin-CONFLICT','en':'Augustine'}})+'\n',encoding='utf-8')
    # The identities and statements candidates are not necessarily lexicons.
    local=root/'Kristal/locals/Kristal-Test/external-source-library/wikidata/maxwd-123'
    local.mkdir(parents=True)
    (local/'identity-candidates.jsonl').write_text(json.dumps({'qid':'Q8018','confidence':0.99,'label':'WRONG','language':'fr'})+'\n')
    (local/'statements.jsonl').write_text(json.dumps({'subject':'Q8018','predicate':'P31','value':'Q5'})+'\n')
    return root, first, second


def test_thematic_accepted_qp_strict_locale_conflicts_and_no_publish(tmp_path):
    root,first,second=_setup(tmp_path)
    doc=discover_resources(sources_root=root)
    values,profiles,summary=observe_thematic_sources(doc,wanted={'Q8018'},locales=tuple(TARGET_LOCALES))
    assert summary['sources_registered']==4
    assert summary['activations']==0 and summary['candidate_only']
    assert ('Q8019','fr') not in values
    assert ('Q8018','no') not in values
    assert ('Q8018','nb') not in values
    assert ('Q8018','nn') in values
    assert values['Q8018','fr'][0]['status']=='conflict_between_sources'
    assert values['Q8018','fr'][1]['status']=='conflict_between_sources'
    assert len(values['Q8018','en'])==2
    assert all(v['status']=='observation_non_publiee' for v in values['Q8018','en'])
    assert summary['conflicting_pairs']==1
    assert all(v['candidate_only'] for vs in values.values() for v in vs)
    assert sum(x.get('rows_matching_accepted_qp',0) for x in profiles)==6
    assert next(p for p in profiles if p['path'].endswith('statements.jsonl'))['status']=='no_accepted_qp_overlap'


def test_thematic_hash_mismatch_refused(tmp_path):
    root,first,second=_setup(tmp_path)
    doc=discover_resources(sources_root=root)
    first.write_text('{"Q8018":{"fr":"tampered"}}\n')
    values,profiles,summary=observe_thematic_sources(doc,wanted={'Q8018'},locales=('fr',))
    assert summary['sources_not_verified']==1
    assert any(p['status'] in ('empreinte_modifiee', 'taille_modifiee') for p in profiles)
    assert all(v['form']!='tampered' for vs in values.values() for v in vs)


def test_thematic_duplicate_sha_only_one_set_of_observations(tmp_path):
    root,first,second=_setup(tmp_path)
    shutil.copy2(first,second)
    doc=discover_resources(sources_root=root)
    values,profiles,summary=observe_thematic_sources(doc,wanted={'Q8018'},locales=('fr','en'))
    assert summary['identical_copies_skipped']==1
    assert len(values['Q8018','fr'])==1


def test_thematic_truncation_never_claims_complete(tmp_path):
    source=tmp_path/'small.jsonl'
    source.write_text(''.join(json.dumps({'Q8018':{'fr':f'word-{i}'}})+'\n' for i in range(5)))
    words, details=_profile(source,{'Q8018'},('fr',),max_rows=2)
    assert details['truncated'] and details['status']=='truncated'
    assert words=={} and details['conflicts_within_source']==1


def test_thematic_does_not_infer_semantics_from_statement_or_lemma():
    assert _explicit_row({'subject':'Q8018','property':'P31','value':'Q5'})[0] is None
    qid, labels, shape=_explicit_row({'qid':'Q8018','lemma':'word','forms':{'fr':'word'}})
    assert (qid,labels,shape)==('Q8018',None,'id_without_labels')
    assert _explicit_row({'id':'L1','labels':{'fr':'lexeme'}})[0] is None


def test_official_locale_counter_is_exactly_14(tmp_path):
    root,first,second=_setup(tmp_path)
    qdir=root/'Grammatical-Framework/gf-wikidata_repos_source/gf-wikidata-tools/extraction/data'
    qdir.mkdir(parents=True)
    q=(qdir/'qid-lexicon.jsonl')
    q.write_text(json.dumps({'Q8018':{'fr':'label','nb':'only nb','nn':'only nn'}})+'\n')
    dik=tmp_path/'dik'; dik.mkdir()
    saved=save_registry(discover_resources(sources_root=root),dik_root=dik)
    qual=qualify_resources(registry_file=saved['registry'],dik_root=dik)
    probe=qual['qid_lexicon_probe']
    assert probe['official_locales']==list(TARGET_LOCALES)
    assert len(probe['official_locales'])==14
    assert 'nb' not in probe['official_locales']
    assert probe['statistics']['explicit_labels_accepted_for_observation']==2
    with (Path(qual['report_dir'])/'source-qualification.csv').open(encoding='utf-8') as fp:
        rows=list(csv.DictReader(fp))
    assert any(x['status']=='lexique_qid_schema_reconnu_non_habilite' for x in rows)


def test_resolve14_thematic_does_not_inflate_coverage(tmp_path):
    root,first,second=_setup(tmp_path)
    official=root/'Kristal/kristal-public/kristals'
    official.mkdir(parents=True)
    proj=official/'demo'; proj.mkdir()
    (proj/'kristal.discovery.json').write_text('{}')
    shutil.copytree(DEMO,proj/'canon/domain/v11/updates/wikidata-2026-11-01-v11-1')
    dik=tmp_path/'diK';(dik/'src/dik').mkdir(parents=True)
    (dik/'src/dik/cli.py').write_text('# fixture')
    (dik/'pyproject.toml').write_text('name = \"dik\"')
    saved=save_registry(discover_resources(sources_root=root),dik_root=dik)
    original=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
                               min_kristals=1,resource_registry=saved['registry'])
    joined=scan_resolution14(official_root=official,sources_root=root,dik_root=dik,
                               min_kristals=1,resource_registry=saved['registry'],
                               observe_wikidata_thematic=True)
    states=('catalogue_courant','catalogue_raccorde','wikidata_observe','non_resolu','conflit')
    assert all(original['totaux'][k]==joined['totaux'][k] for k in states)
    assert joined['wikidata_thematic']['candidate_only']
    assert joined['wikidata_thematic']['sources_registered']>=4
    assert joined['traduction_entre_langues'] is False
    report=Path(joined['dossier_rapports'])
    assert (report/'wikidata_thematic_sources.csv').exists()
    assert (report/'wikidata_thematic_observations_candidates.csv').exists()
