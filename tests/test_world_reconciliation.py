from pathlib import Path
import json

import pytest

from dik.world_reconciliation import build_reconciliation, audit_reconciliation

BASE = Path(__file__).parents[1]/'examples/world-dictionaries'
INDEX = BASE/'language-code-candidates.jsonl'
MANIFEST = BASE/'language-code-candidates.manifest.json'
IANA = BASE/'iana-fixtures/synthetic-language-subtag-registry.txt'


def test_full_7910_iso_reconciliation_cleans_and_audits(tmp_path):
    out = tmp_path/'reconciliation'
    report = build_reconciliation(index=INDEX, source_manifest=MANIFEST, iana_registry=IANA, output_dir=out)
    assert report['record_count'] == 7910
    assert report['published_dictionaries'] == 0
    assert audit_reconciliation(out)['records_checked'] == 7910
    assert report['iana_source_authenticity'] == 'operator_supplied_unverified'
    with pytest.raises(FileExistsError):
        build_reconciliation(index=INDEX, source_manifest=MANIFEST, iana_registry=IANA, output_dir=out)


def test_changed_manifest_hash_rejected(tmp_path):
    corrupted = tmp_path/'manifest.json'
    manifest = json.loads(MANIFEST.read_text())
    manifest['record_count'] = 1
    corrupted.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        build_reconciliation(index=INDEX, source_manifest=corrupted, iana_registry=IANA, output_dir=tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_reconcile_tampering_and_promotion_rejected(tmp_path):
    out = tmp_path/'report'
    build_reconciliation(index=INDEX, source_manifest=MANIFEST, iana_registry=IANA, output_dir=out)
    with (out/'reconciliation.jsonl').open('ab') as src:
        src.write(b'{}\n')
    with pytest.raises(ValueError, match='hash'):
        audit_reconciliation(out)


def test_reconcile_fake_publication_rejected(tmp_path):
    out = tmp_path/'report'
    build_reconciliation(index=INDEX, source_manifest=MANIFEST, iana_registry=IANA, output_dir=out)
    doc = json.loads((out/'manifest.json').read_text())
    doc['published_dictionaries'] = 7910
    (out/'manifest.json').write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        audit_reconciliation(out)
