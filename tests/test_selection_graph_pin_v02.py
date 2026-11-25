"""XW- / ID-: a reviewed derived selection must bind the graph bytes too.

These are stdlib-only tests, so the most important refusal stays testable
even in a diagnostic environment without pytest.
"""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from dik import canonical_selection as selection


class GraphPinnedSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'review.json'
        self.digest = {
            'state_index_sha256': '1' * 64,
            'registry_sha256': '2' * 64,
            'crosswalk_sha256': '3' * 64,
            'catalog_sha256': '4' * 64,
            'graph_sha256': '5' * 64,
        }
        self.decision = {
            'kristal': 'example',
            'revision_dir': 'canon/domain/v11/updates/rev1',
            **self.digest,
            'review_decision_id': 'REVIEW-2026-11-24',
            'reviewer': 'operator-reviewed',
            'rationale': 'Graph and crosswalk bytes inspected for read-only view',
        }

    def write(self, *, profile=None, decision=None):
        self.path.write_text(json.dumps({
            'profile': profile or selection.DECISIONS_PROFILE,
            'scope': 'derived_view_only',
            'decisions': [self.decision if decision is None else decision],
        }), encoding='utf-8')

    def fake_db(self, *, graph_digest=None):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript('''
          CREATE TABLE canonical_sources (kristal TEXT);
          CREATE TABLE canonical_revisions (
            kristal TEXT, revision_dir TEXT, state TEXT,
            source_accepted_exact INTEGER, issue TEXT);
          CREATE TABLE canonical_revision_inputs (
            kristal TEXT, revision_dir TEXT, state_index_sha256 TEXT,
            registry_sha256 TEXT, crosswalk_sha256 TEXT, graph_sha256 TEXT,
            catalog_sha256 TEXT, graph_state TEXT);
          CREATE TABLE canonical_crosswalk_evidence (
            kristal TEXT, revision_dir TEXT, source_status TEXT, relation TEXT,
            namespace_id TEXT, semantic_id TEXT, wikidata_id TEXT);
        ''')
        db.execute('INSERT INTO canonical_sources VALUES (?)', ('example',))
        db.execute('INSERT INTO canonical_revisions VALUES (?,?,?,?,?)',
                   ('example', self.decision['revision_dir'], 'OBSERVED_UNSELECTED', 1, ''))
        db.execute('INSERT INTO canonical_revision_inputs VALUES (?,?,?,?,?,?,?,?)', (
            'example', self.decision['revision_dir'],
            self.digest['state_index_sha256'], self.digest['registry_sha256'],
            self.digest['crosswalk_sha256'], graph_digest or self.digest['graph_sha256'],
            self.digest['catalog_sha256'], 'INSPECTED'))
        return db

    def test_v02_selects_only_a_graph_hash_pinned_derived_view(self):
        self.write()
        self.assertIn('example', selection.read_decisions(self.path))
        stats = selection.ingest(self.fake_db(), decisions_file=self.path)
        self.assertEqual(stats['operator_pinned_view_revisions'], 1)
        self.assertEqual(stats['framework_authority_confirmed'], 0)
        self.assertEqual(stats['new_global_approvals'], 0)

    def test_graph_byte_drift_blocks_an_unchanged_other_four_hashes(self):
        self.write()
        with self.assertRaisesRegex(ValueError, 'stale'):
            selection.ingest(self.fake_db(graph_digest='9' * 64), decisions_file=self.path)

    def test_missing_graph_hash_and_v01_file_fail_closed(self):
        invalid = dict(self.decision)
        invalid.pop('graph_sha256')
        self.write(decision=invalid)
        with self.assertRaises(ValueError):
            selection.read_decisions(self.path)
        self.write(profile='dik.canonical-selection-decisions/0.1')
        with self.assertRaisesRegex(ValueError, '0.1|legacy'):
            selection.read_decisions(self.path)


if __name__ == '__main__':
    unittest.main()
