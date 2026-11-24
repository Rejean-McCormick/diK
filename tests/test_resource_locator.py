"""Reference registry: offline discovery, fail-closed pointers and no false KQ/GF linkage."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from dik.cli import main
from dik.resource_locator import (discover_resources, save_registry, load_registry,
                                   validate_registry, catalog_references)


def _workspace(tmp_path):
    root = tmp_path / 'mycode'
    lex = root / 'Grammatical-Framework' / 'GF_Lexicons_Archive'
    lex.mkdir(parents=True)
    (lex / 'DictFre.gf').write_text('concrete DictFre of Dict = {}', encoding='utf-8')
    wikidata = root / 'Grammatical-Framework' / 'gf-wikidata_repos_source' / 'gf-wikidata-tools' / 'extraction' / 'data'
    wikidata.mkdir(parents=True)
    (wikidata / 'qid-lexicon.jsonl').write_text('{"qid":"Q1"}\n', encoding='utf-8')
    return root, lex, wikidata


def test_discovery_is_metadata_only_and_finds_known_roots(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    doc = discover_resources(sources_root=root)
    kinds = {r['kind'] for r in doc['sources']}
    assert kinds == {'gf_lexicon_candidate', 'wikidata_qid_lexicon_candidate'}
    assert len(doc['sources']) == 2
    assert all(r['sha256'] and not r['allowed_for_resolution'] for r in doc['sources'])
    assert not (root / 'reports').exists()
    assert doc['policy']['translation_between_languages'] is False
    assert any(x['reason'] == 'absent' for x in doc['roots_unavailable'])


def test_registry_persists_under_dik_only_and_detects_modification(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    dik = tmp_path / 'dik'
    dik.mkdir()
    result = save_registry(discover_resources(sources_root=root), dik_root=dik)
    assert Path(result['registry']).is_file()
    assert Path(result['latest_registry']).is_file()
    assert result['etat'] == 'inventory_only'
    assert validate_registry(result['registry'])['counts']['unchanged'] == 2
    (lex / 'DictFre.gf').write_text('modified', encoding='utf-8')
    state = validate_registry(result['registry'])
    assert state['counts']['modified_or_unverified'] == 1
    assert state['status'] == 'STALE'
    with pytest.raises(ValueError, match='périmé'):
        from dik.cli import make_parser, run
        run(make_parser().parse_args(['sources', 'verify', '--registry', result['registry']]))
    assert len(load_registry(result['registry'])['sources']) == 2
    assert not (root / 'reports').exists()
    with pytest.raises(ValueError):
        save_registry(discover_resources(sources_root=root), dik_root=dik, reports_root='../../bad')


def test_reject_or_skip_unsafe_symlink(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    bad = lex / 'DictEng.gf'
    try:
        bad.symlink_to(tmp_path / 'other')
    except (OSError, NotImplementedError):
        pytest.skip('symlink unsupported')
    doc = discover_resources(sources_root=root)
    assert len(doc['sources']) == 2


def test_catalog_integrity_before_v11_audit(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    folder = root / 'Kristal' / 'kristal-public' / 'kristals' / 'a' / 'canon' / 'v11' / 'dictionaries'
    folder.mkdir(parents=True)
    file = folder / 'catalog.json'
    file.write_text('{"namespace_id":"n"}', encoding='utf-8')
    reg = discover_resources(sources_root=root)
    assert catalog_references(reg) == [file]
    file.write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='modifie'):
        catalog_references(reg)


def test_forged_outside_root_is_rejected(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    registry = discover_resources(sources_root=root)
    registry['sources'][0]['root'] = str(tmp_path / 'different')
    p = tmp_path / 'fake.json'
    p.write_text(json.dumps(registry), encoding='utf-8')
    with pytest.raises(ValueError, match='dehors'):
        load_registry(p)


def test_large_files_remain_unhashed_and_unapproved(tmp_path):
    root, lex, wd = _workspace(tmp_path)
    doc = discover_resources(sources_root=root, max_hash_bytes=1)
    assert all(x['state'] == 'found_unhashed' and x['sha256'] is None for x in doc['sources'])
    assert all(not x['allowed_for_resolution'] for x in doc['sources'])


def test_cli_discovery_smoke(tmp_path, capsys):
    root, lex, wd = _workspace(tmp_path)
    dik = tmp_path / 'dik'; dik.mkdir()
    assert main(['sources', 'discover', '--sources-root', str(root), '--dik-root', str(dik)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result['sources'] == 2
    assert main(['sources', 'verify', '--registry', result['registry']]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output['total'] == 2


def test_unhashed_registry_is_incomplete_not_verified(tmp_path):
    root, _, _ = _workspace(tmp_path)
    dik = tmp_path / 'dik'; dik.mkdir()
    inventory = discover_resources(sources_root=root, max_hash_bytes=1)
    report = save_registry(inventory, dik_root=dik)
    result = validate_registry(report['registry'])
    assert result['status'] == 'INCOMPLETE'
    assert result['counts']['not_fingerprinted'] == 2
