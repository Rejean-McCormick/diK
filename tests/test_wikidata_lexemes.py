from pathlib import Path
import bz2
import gzip
import json

import pytest

from dik.wikidata_lexemes import LexemeError, import_lexeme_observations, audit_lexeme_observations
from dik.gf_handoff import build_gf_handoff, audit_gf_handoff

BASE = Path(__file__).parents[1]/'examples/world-dictionaries'
DUMP = BASE/'wikidata-lexeme-sample.jsonl'
IANA = BASE/'iana-fixtures/synthetic-language-subtag-registry.txt'


def _import(tmp_path, source=DUMP, **kwargs):
    return import_lexeme_observations(dump=source, output_dir=tmp_path/'out', snapshot='unit', **kwargs)


def test_observations_import_and_audit(tmp_path):
    result = _import(tmp_path, iana_registry=IANA)
    assert (result['lexemes'], result['forms'], result['senses']) == (2, 2, 2)
    assert result['scanned_entities'] == 3
    assert result['published_dictionaries'] == 0
    assert result['approved_kristal_crosswalks'] == 0
    assert audit_lexeme_observations(tmp_path/'out')['lexemes'] == 2
    first = json.loads((tmp_path/'out'/'lexemes.jsonl').read_text().splitlines()[0])
    assert first['external_lexeme_id'] == 'L101'
    assert first['forms'][0]['id'] == 'L101-F1'
    assert first['senses'][0]['id'] == 'L101-S1'
    assert first['gf_mapping_status'] == 'unmapped'
    assert first['kristal_identity'] is None
    assert first['lemmas'][0]['iana_valid'] is True


@pytest.mark.parametrize('suffix', ['.gz', '.bz2'])
def test_compressed_dump_and_array_source(tmp_path, suffix):
    objs = [json.loads(line) for line in DUMP.read_text().splitlines()]
    payload = ('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in objs) + '\n]\n').encode('utf-8')
    source = tmp_path/('dump.json'+suffix)
    source.write_bytes(gzip.compress(payload) if suffix == '.gz' else bz2.compress(payload))
    assert _import(tmp_path, source=source)['lexemes'] == 2


def test_sha_mismatch_no_output(tmp_path):
    with pytest.raises(LexemeError, match='SHA-256'):
        _import(tmp_path, expected_sha256='0'*64)
    assert not (tmp_path/'out').exists()


def test_overwrite_forbidden(tmp_path):
    _import(tmp_path)
    with pytest.raises(FileExistsError):
        _import(tmp_path)


def test_duplicate_lexeme_ids_rejected(tmp_path):
    source = tmp_path/'dump.jsonl'
    source.write_text(DUMP.read_text() + DUMP.read_text().splitlines()[1] + '\n')
    with pytest.raises(LexemeError, match='duplicate'):
        _import(tmp_path, source=source)
    assert not (tmp_path/'out').exists()


def test_form_id_wrong_owner_rejected(tmp_path):
    records = [json.loads(line) for line in DUMP.read_text().splitlines()]
    records[1]['forms'][0]['id'] = 'L999-F1'
    source = tmp_path/'dump.jsonl'
    source.write_text(''.join(json.dumps(x)+'\n' for x in records))
    with pytest.raises(LexemeError, match='form'):
        _import(tmp_path, source=source)


def test_resource_limit_prevents_partial_publication(tmp_path):
    with pytest.raises(LexemeError, match='resource limit'):
        _import(tmp_path, max_records=2)
    assert not (tmp_path/'out').exists()


def test_hash_tamper_rejected(tmp_path):
    _import(tmp_path)
    with (tmp_path/'out'/'lexemes.jsonl').open('ab') as stream:
        stream.write(b'{}\n')
    with pytest.raises(LexemeError, match='hash'):
        audit_lexeme_observations(tmp_path/'out')


def test_gf_handoff_and_integrity(tmp_path):
    _import(tmp_path)
    gf = build_gf_handoff(observations_dir=tmp_path/'out', output_dir=tmp_path/'gf', locale='fr')
    assert gf['candidate_lexemes'] == 2
    assert gf['candidate_forms'] == 1
    assert gf['gf_functions_created'] == 0
    assert audit_gf_handoff(tmp_path/'gf')['candidate_forms'] == 1
    data = [json.loads(x) for x in (tmp_path/'gf'/'candidates.jsonl').read_text().splitlines()]
    assert data[0]['gf_function'] is None
    assert data[0]['approved_kristal_link'] is None
    with (tmp_path/'gf'/'candidates.jsonl').open('ab') as stream:
        stream.write(b'{}\n')
    with pytest.raises(ValueError, match='checksum'):
        audit_gf_handoff(tmp_path/'gf')


def test_synthetic_iana_registry_not_required_for_observations(tmp_path):
    result = _import(tmp_path)
    assert result['iana_registry_sha256'] is None
    first = json.loads((tmp_path/'out'/'lexemes.jsonl').read_text().splitlines()[0])
    assert first['lemmas'][0]['iana_valid'] is None
