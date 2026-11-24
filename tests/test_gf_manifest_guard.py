"""Regression: unrelated manifest.json files under C:\\mycode must not abort GF inventory."""
import json
from pathlib import Path

import pytest

from dik.resolution14 import _gf_sources


@pytest.mark.parametrize('content', [[], [1, 2], None, 123, 'other', True, {'profile': 'other'}])
def test_non_gf_manifest_root_is_skipped(tmp_path: Path, content):
    directory = tmp_path / 'other-repo'
    directory.mkdir()
    (directory / 'manifest.json').write_text(json.dumps(content), encoding='utf-8')
    assert list(_gf_sources(tmp_path)) == []


def test_malformed_gf_handoff_is_reported_not_fatal(tmp_path: Path):
    directory = tmp_path / 'gf-candidate'
    directory.mkdir()
    (directory / 'manifest.json').write_text(json.dumps({
        'profile': 'dik.gf-lexical-handoff/0.1-candidate',
        'locale': 'fr',
        'purpose': 'candidate_only',
        'candidates_file': 'candidates.jsonl',
        'candidate_lexemes': 0,
        'candidate_forms': 0,
        'candidates_sha256': 'invalid',
        'gf_functions_created': 0,
        'verified_dictionaries': 0,
    }), encoding='utf-8')
    rows = list(_gf_sources(tmp_path))
    assert len(rows) == 1
    assert rows[0]['etat'] == 'audit_impossible'
    assert rows[0]['locale'] == 'fr'
