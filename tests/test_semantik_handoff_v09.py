"""v0.9 lexical transfer: no inferred semantic identity or GF functions."""
import json
from pathlib import Path
import pytest

from dik.wikidata_lexemes import import_lexeme_observations
from dik.gf_handoff import build_gf_handoff
from dik.semantik_handoff import build_semantik_knowledge_candidate, audit_semantik_knowledge_candidate

DATA=Path(__file__).parents[1]/'examples/world-dictionaries/wikidata-lexeme-sample.jsonl'


def _bundle(tmp_path):
    import_lexeme_observations(dump=DATA,output_dir=tmp_path/'obs',snapshot='test-v09')
    build_gf_handoff(observations_dir=tmp_path/'obs',output_dir=tmp_path/'gf',locale='fr')
    return build_semantik_knowledge_candidate(handoff_dir=tmp_path/'gf',output_dir=tmp_path/'sem')


def test_knowledge_only_and_provenance(tmp_path):
    report=_bundle(tmp_path)
    assert report['entries']==2 and report['gf_bindings']==0 and report['released'] is False
    assert audit_semantik_knowledge_candidate(tmp_path/'sem')['entries']==2
    data=json.loads((tmp_path/'sem'/'semantik.knowledge.json').read_text())
    assert data['schema_version']=='1.1'
    assert all(r['use_for']=='knowledge' and r['binding_kind']=='lexeme_ref' for r in data['entries'])
    assert data['entries'][0]['semantic_ref']=='wikidata:lexeme:L101'
    template=json.loads((tmp_path/'sem'/'gf-mapping-review.template.json').read_text())
    assert all(not d['mapping_reviewed'] and not d['semantic_identity_reviewed'] and d['gf_function'] is None for d in template['decisions'])


def test_immutability_and_tamper(tmp_path):
    _bundle(tmp_path)
    with pytest.raises(FileExistsError):
        build_semantik_knowledge_candidate(handoff_dir=tmp_path/'gf',output_dir=tmp_path/'sem')
    (tmp_path/'sem'/'semantik.knowledge.json').write_text('{}')
    with pytest.raises(ValueError,match='checksum'):
        audit_semantik_knowledge_candidate(tmp_path/'sem')


def test_limit_is_fail_closed(tmp_path):
    import_lexeme_observations(dump=DATA,output_dir=tmp_path/'obs',snapshot='test-v09')
    build_gf_handoff(observations_dir=tmp_path/'obs',output_dir=tmp_path/'gf',locale='fr')
    with pytest.raises(ValueError,match='limit'):
        build_semantik_knowledge_candidate(handoff_dir=tmp_path/'gf',output_dir=tmp_path/'sem',max_entries=1)
    assert not (tmp_path/'sem').exists()
