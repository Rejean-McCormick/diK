from pathlib import Path
import json
import pytest

from dik.world_sources import inspect_resource_catalog

CATALOG = Path(__file__).parents[1]/'examples/world-dictionaries/resource-catalog.json'


def test_world_resource_catalog_is_candidate_only():
    result = inspect_resource_catalog(CATALOG)
    assert result['discovery_resources'] >= 20
    assert result['license_approved'] == 0
    assert result['dictionaries_published'] == 0


def test_reject_duplicate_source(tmp_path):
    obj = json.loads(CATALOG.read_text())
    obj['resources'].append(obj['resources'][0])
    path = tmp_path/'dup.json'
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError, match='duplicate'):
        inspect_resource_catalog(path)


def test_reject_invented_license_approval(tmp_path):
    obj = json.loads(CATALOG.read_text())
    obj['resources'][0]['license_status'] = 'approved'
    path = tmp_path/'bad.json'
    path.write_text(json.dumps(obj))
    with pytest.raises(Exception):
        inspect_resource_catalog(path)


def test_reject_unsafe_source_url(tmp_path):
    obj = json.loads(CATALOG.read_text())
    obj['resources'][0]['url'] = 'https://admin:password@example.org/'
    path = tmp_path/'bad.json'
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError, match='URL'):
        inspect_resource_catalog(path)
