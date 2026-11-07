from pathlib import Path
import json
import pytest

from dik.world_collection import build_collection_slots, audit_collection_slots

BASE = Path(__file__).parents[1]/'examples/world-dictionaries'
IDX = BASE/'language-code-candidates.jsonl'
MAN = BASE/'language-code-candidates.manifest.json'


def test_build_full_world_slots_and_audit(tmp_path):
    result = build_collection_slots(index=IDX, language_manifest=MAN, output_dir=tmp_path/'slots')
    assert result['slot_count'] == 7910
    assert result['dictionaries_published'] == 0
    audit = audit_collection_slots(tmp_path/'slots')
    assert audit['candidate_slots'] == 7910
    assert audit['actual_dictionaries'] == 0
    with pytest.raises(FileExistsError):
        build_collection_slots(index=IDX, language_manifest=MAN, output_dir=tmp_path/'slots')


def test_reject_false_coverage_claim(tmp_path):
    build_collection_slots(index=IDX, language_manifest=MAN, output_dir=tmp_path/'slots')
    p = tmp_path/'slots'/'manifest.json'
    obj = json.loads(p.read_text())
    obj['dictionaries_published'] = 7910
    p.write_text(json.dumps(obj))
    with pytest.raises(ValueError):
        audit_collection_slots(tmp_path/'slots')


def test_reject_source_index_mutation(tmp_path):
    changed = tmp_path/'candidate-manifest.json'
    doc = json.loads(MAN.read_text())
    doc['file_sha256'] = 'a'*64
    changed.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        build_collection_slots(index=IDX, language_manifest=changed, output_dir=tmp_path/'slots')
    assert not (tmp_path/'slots').exists()
