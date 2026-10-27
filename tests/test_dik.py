"""Integration and regression tests for diK's first milestone.

Fixtures are copied byte-for-byte from Framework 11.0.0-draft.3.
"""
from __future__ import annotations

import csv
import hashlib
import json
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dik import FRAMEWORK_CONTRACT
from dik._framework import dictionaries as ref
from dik.cli import main
from dik.operations import (DiKError, coverage_report, dictionary_resolve,
                             dictionaries_audit, import_wikidata_local, inspect,
                             load_project)

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'examples' / 'demo'


class BasicFixture(unittest.TestCase):
    def setUp(self):
        self.project = load_project(FIX / 'dik.project.json')

    def test_contract_version(self):
        self.assertEqual(FRAMEWORK_CONTRACT, '11.0.0-draft.3')

    def test_inspect_and_report_match_framework_fixture(self):
        summary = inspect(self.project)
        self.assertEqual(summary['semantic_reference_count'], {'KQ': 2, 'KP': 1})
        self.assertEqual(summary['accepted_exact_wikidata_mappings'], 1)
        result = coverage_report(self.project, ['fr','en','fr-CA'])
        expected = json.loads((FIX / 'dik-coverage.example.json').read_text())
        self.assertEqual(result, expected)

    def test_direct_and_fallback_not_conflated(self):
        result = coverage_report(self.project, ['fr-CA'])['locales'][0]
        self.assertEqual(result['KQ']['direct'], 0)
        self.assertEqual(result['KQ']['fallback'], 1)
        self.assertEqual(result['KP']['missing'], 1)
        self.assertFalse(result['complete_direct'])
        self.assertFalse(result['complete_usable'])

    def test_dictionary_lookup_validates_identity(self):
        resolved = dictionary_resolve(self.project, 'KQ1001','fr-CA')
        self.assertEqual(resolved['status'], 'resolved')
        self.assertEqual(resolved['effective_locale'], 'fr')
        self.assertTrue(resolved['fallback'])
        with self.assertRaises(DiKError):
            dictionary_resolve(self.project, 'KQ9999999', 'fr')

    def test_audit_and_integrity_checks(self):
        self.assertEqual(dictionaries_audit(self.project)['locales'], 3)
        self.assertEqual(ref.sha256(self.project.graph),
                         '50caca8e1af9af62d5af7f757c87b05d2302e00ab18010ea2bc6606f0a7fec27')

    def test_unknown_locale_rejected(self):
        with self.assertRaises(ref.DictionaryError):
            coverage_report(self.project, ['not-present'])

    def test_zero_denominator_and_301_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for p in ('identity-registry.example.json','semantic-graph.example.json',
                      'external-crosswalk.example.json'):
                shutil.copyfile(FIX/p, root/p)
            graph = json.loads((root/'semantic-graph.example.json').read_text())
            graph['entities'] = []
            graph['properties'] = []
            graph['sources'] = []
            graph['assertions'] = []
            (root/'semantic-graph.example.json').write_text(json.dumps(graph))
            catalog = json.loads((FIX/'dictionaries/catalog.json').read_text())
            catalog['languages'] = []
            # Codes syntactically distinct; no translation is invented.
            for i in range(301):
                tag=f'zz-{i:03d}'
                catalog['languages'].append({'tag':tag,'fallbacks':[],'layers':[]})
            (root/'catalog.json').write_text(json.dumps(catalog))
            manifest = {
                'format_version':'0.1','framework_contract':FRAMEWORK_CONTRACT,
                'graph':'semantic-graph.example.json','registry':'identity-registry.example.json',
                'crosswalk':'external-crosswalk.example.json','catalog':'catalog.json'
            }
            (root/'dik.project.json').write_text(json.dumps(manifest))
            project=load_project(root/'dik.project.json')
            report=coverage_report(project)
            self.assertEqual(len(report['locales']),301)
            self.assertTrue(all(x['KQ']['total']==0 and x['KP']['total']==0 for x in report['locales']))
            # No mathematically fictitious 100% ratio in the machine contract.
            self.assertTrue(all(x['KQ']['direct']==0 and x['KP']['direct']==0 for x in report['locales']))

    def test_text_used_as_semantic_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=json.loads(self.project.graph.read_text())
            bad['entities'][0]="Augustin d'Hippone"
            p=Path(tmp)/'graph.json'
            p.write_text(json.dumps(bad))
            from dik._framework.coverage import _references
            with self.assertRaises(ref.DictionaryError):
                _references(ref.read_json(p), ref.read_json(self.project.registry))

    def test_import_wikidata_streaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/'new-snapshot'
            result=import_wikidata_local(dump=FIX/'wikidata-small.sample.jsonl',
                crosswalk=self.project.crosswalk, registry=self.project.registry,
                namespace='example.org/kristal-demo', snapshot='test-snap', locales=['fr','en','de'],
                output=output)
            self.assertEqual(result['entities_scanned'],2)
            self.assertEqual(result['accepted_exact_entities_seen'],1)
            self.assertEqual(result['labels_by_locale'],{'fr':1,'en':1,'de':0})
            self.assertTrue((output/'catalog.json').is_file())
            self.assertEqual(ref.audit(output/'catalog.json', self.project.crosswalk, self.project.registry)['locales'],3)
            with self.assertRaises(DiKError):
                import_wikidata_local(dump=FIX/'wikidata-small.sample.jsonl',
                    crosswalk=self.project.crosswalk, registry=self.project.registry,
                    namespace='example.org/kristal-demo', snapshot='test-snap', locales=['fr'], output=output)

    def test_import_rejects_wrong_namespace_and_does_not_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'output'
            with self.assertRaises(DiKError):
                import_wikidata_local(dump=FIX/'wikidata-small.sample.jsonl',
                    crosswalk=self.project.crosswalk, registry=self.project.registry,
                    namespace='wrong/namespace', snapshot='snap', locales=['fr'], output=out)
            self.assertFalse(out.exists())

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            m=json.loads((FIX/'dik.project.json').read_text())
            m['graph']='../outside.json'
            (dest/'dik.project.json').write_text(json.dumps(m))
            with self.assertRaises(ref.DictionaryError):
                load_project(dest/'dik.project.json')

    def test_cli_writes_json_and_csv_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'report.json'
            csv_path=Path(tmp)/'report.csv'
            args=['coverage','report','--project',str(self.project.manifest),
                  '--locales','fr,en,fr-CA','--output',str(out),'--csv',str(csv_path)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args),0)
            self.assertEqual(json.loads(out.read_text())['semantic_reference_count']['KQ'], 2)
            with csv_path.open(newline='') as fh:
                rows=list(csv.DictReader(fh))
            self.assertEqual(len(rows),6)
            original_hash=hashlib.sha256(out.read_bytes()).hexdigest()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args),2) # Existing files not overwritten.
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), original_hash)

    def test_import_requires_reviewed_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            crosswalk=json.loads(self.project.crosswalk.read_text())
            crosswalk['mappings'][0]['status']='candidate'
            crosswalk['mappings'][0].pop('review',None)
            cp=root/'crosswalk.json'
            cp.write_text(json.dumps(crosswalk))
            result=import_wikidata_local(dump=FIX/'wikidata-small.sample.jsonl',
                crosswalk=cp, registry=self.project.registry,
                namespace='example.org/kristal-demo',snapshot='only-approved',locales=['fr'],
                output=root/'out')
            self.assertEqual(result['accepted_exact_entities_seen'],0)
            self.assertEqual(result['labels_by_locale']['fr'],0)

    def test_reject_invalid_kq_p_mapping(self):
        crosswalk=json.loads(self.project.crosswalk.read_text())
        crosswalk['mappings'][0]['external_ref']['id']='P8018'
        with self.assertRaises(ref.DictionaryError):
            ref.accepted_exact(crosswalk,'example.org/kristal-demo')

    def test_multiple_outputs_preflight_no_partial_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            csv_path=root/'already-there.csv'
            csv_path.write_text('existing\n')
            new_json=root/'new.json'
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['coverage','report','--project',str(self.project.manifest),
                                       '--output',str(new_json),'--csv',str(csv_path)]),2)
            self.assertFalse(new_json.exists())
            self.assertEqual(csv_path.read_text(),'existing\n')

    def test_reject_unregistered_crosswalk_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for p in ('identity-registry.example.json','semantic-graph.example.json',
                      'external-crosswalk.example.json'):
                shutil.copyfile(FIX/p, root/p)
            shutil.copytree(FIX/'dictionaries', root/'dictionaries')
            crosswalk=json.loads((root/'external-crosswalk.example.json').read_text())
            crosswalk['mappings'][0]['review']['evidence_refs']=['KS999999']
            (root/'external-crosswalk.example.json').write_text(json.dumps(crosswalk))
            shutil.copyfile(FIX/'dik.project.json', root/'dik.project.json')
            with self.assertRaises(DiKError):
                inspect(load_project(root/'dik.project.json'))

    def test_catalog_hash_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            shutil.copytree(FIX/'dictionaries', root/'dictionaries')
            with (root/'dictionaries/curated-fr.json').open('a') as fh:
                fh.write('\n')
            with self.assertRaises(ref.DictionaryError):
                ref.audit(root/'dictionaries/catalog.json', self.project.crosswalk,self.project.registry)


if __name__ == '__main__':
    unittest.main()
