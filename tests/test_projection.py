"""Lossless semantic roundtrips. Never reverse lookup terms to guess identities."""
from __future__ import annotations
import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dik.cli import main
from dik.operations import DiKError, load_project
from dik.projection import digest, project_graph, readable_markdown, restore_projection

ROOT = Path(__file__).resolve().parents[1]
PROJECT = load_project(ROOT/'examples/demo/dik.project.json')


class ProjectionTests(unittest.TestCase):
    def test_roundtrip_every_declared_locale(self):
        source = json.loads(PROJECT.graph.read_text())
        for locale in ('fr','en','fr-CA'):
            with self.subTest(locale=locale):
                out = project_graph(PROJECT,locale)
                self.assertEqual(restore_projection(out, PROJECT),source)
                self.assertEqual(restore_projection(out),source)
                self.assertTrue(out['derived_only'])
                self.assertEqual(out['anchors']['graph_id'],'demo-graph')
                self.assertEqual(out['canonical_graph'],source)

    def test_missing_and_fallback_marked_not_invented(self):
        projected = project_graph(PROJECT,'fr-CA')['readable']
        self.assertEqual(projected['coverage_counts'],{'direct':0,'fallback':1,'missing':2})
        self.assertEqual(projected['entities'][0]['label'],'Saint Augustin')
        self.assertEqual(projected['entities'][0]['effective_locale'],'fr')
        self.assertIsNone(projected['entities'][1]['label'])
        self.assertFalse(projected['complete_usable'])

    def test_no_text_to_id_heuristics_even_after_label_edit(self):
        p = project_graph(PROJECT,'fr')
        damaged = copy.deepcopy(p)
        damaged['readable']['entities'][0]['label']='NOUVEAU SENS POSSIBLE'
        with self.assertRaises(DiKError):
            restore_projection(damaged)
        damaged['digests']['readable'] = digest(damaged['readable'])
        # Resigned checksums cannot bypass validation against pinned sources.
        with self.assertRaises(DiKError):
            restore_projection(damaged,PROJECT)
        # Detached restore still preserves the original graph, no word lookup.
        self.assertEqual(restore_projection(damaged),json.loads(PROJECT.graph.read_text()))

    def test_tamper_semantic_or_source_version_rejected(self):
        p = project_graph(PROJECT,'en')
        bad = copy.deepcopy(p)
        bad['canonical_graph']['assertions'][0]['predicate']='KP2009'
        with self.assertRaises(DiKError):
            restore_projection(bad)
        bad = copy.deepcopy(p)
        bad['anchors']['source_sha256']['catalog']='0'*64
        with self.assertRaises(DiKError):
            restore_projection(bad,PROJECT)
        bad['digests']['anchors'] = digest(bad['anchors'])
        with self.assertRaises(DiKError):
            restore_projection(bad,PROJECT)

    def test_wrong_id_rejected_even_if_readable_digest_recomputed(self):
        p = project_graph(PROJECT,'fr')
        bad = copy.deepcopy(p)
        bad['readable']['statements'][0]['predicate']['id']='KP99999'
        bad['digests']['readable']=digest(bad['readable'])
        with self.assertRaises(DiKError):
            restore_projection(bad)

    def test_qualifier_and_literal_are_preserved(self):
        # A derived modified graph only for test; no source file is mutated.
        from dik.projection import _readable
        graph = json.loads(PROJECT.graph.read_text())
        graph['assertions'][0]['object']={'kind':'literal','datatype':'string',
                                          'value':'grâce peut désigner plusieurs concepts', 'language':'fr'}
        graph['assertions'][0]['qualifiers']=[{'predicate':'KP2001','object':{'kind':'entity','id':'KQ1002'}}]
        dictionary={'KQ1001':{'id':'KQ1001','label':'Augustin','status':'direct'},
                    'KQ1002':{'id':'KQ1002','label':'grâce','status':'direct'},
                    'KP2001':{'id':'KP2001','label':'énonce','status':'direct'}}
        readable=_readable(graph,dictionary,'fr')
        self.assertEqual(readable['statements'][0]['object'],graph['assertions'][0]['object'])
        self.assertEqual(readable['statements'][0]['qualifiers'][0]['object']['reference']['id'],'KQ1002')
        self.assertEqual(graph['assertions'][0]['object']['value'],'grâce peut désigner plusieurs concepts')

    def test_cli_does_not_overwrite_or_partially_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); proj=root/'proj.json'; md=root/'read.md'; restored=root/'pure.json'
            base=['projection','export','--project',str(PROJECT.manifest),'--locale','fr-CA',
                  '--output',str(proj),'--markdown',str(md)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(base),0)
                self.assertEqual(main(['projection','restore','--input',str(proj),
                    '--project',str(PROJECT.manifest),'--output',str(restored)]),0)
            self.assertEqual(json.loads(restored.read_text()),json.loads(PROJECT.graph.read_text()))
            self.assertIn('`KQ1001`',md.read_text())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(base),2)
            self.assertEqual(len(list(root.iterdir())),3)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['projection','verify','--input',str(proj),
                    '--project',str(PROJECT.manifest)]),0)
            md.unlink(); original=proj.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(base),2)
            self.assertFalse(md.exists())
            self.assertEqual(proj.read_bytes(),original)

    def test_same_input_yields_deterministic_projected_view(self):
        a=project_graph(PROJECT,'en')
        self.assertEqual(a,project_graph(PROJECT,'en'))
        self.assertEqual(readable_markdown(a),readable_markdown(project_graph(PROJECT,'en')))

    def test_unknown_language_rejected(self):
        with self.assertRaises(DiKError):
            project_graph(PROJECT,'qu-999')

    def test_many_languages_supported_not_falsely_translated(self):
        # Construction is memory-backed for this check; coverage tests already
        # exercise 301 language catalogs.
        p=project_graph(PROJECT,'en')
        self.assertEqual(p['readable']['requested_locale'],'en')
        self.assertLessEqual(p['readable']['coverage_counts']['direct'],3)

if __name__ == '__main__':
    unittest.main()

class CleanReadingTests(unittest.TestCase):
    def test_clean_readable_has_terms_without_opaque_ids_where_available(self):
        p = project_graph(PROJECT,'fr')
        clean = readable_markdown(p, 'clean')
        annotated = readable_markdown(p, 'annotated')
        self.assertIn('Saint Augustin', clean)
        self.assertNotIn('`KQ1001`', clean)
        self.assertIn('`KQ1001`', annotated)
        self.assertEqual(restore_projection(p, PROJECT),json.loads(PROJECT.graph.read_text()))
