"""diK compact identity-preserving projection, regression and scale tests."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from dik.cli import main
from dik.compact import COMPACT_PROFILE, _check_consistency, compact_markdown, project_compact
from dik.operations import DiKError, load_project
from dik.projection import digest, project_graph, restore_projection, readable_markdown

ROOT = Path(__file__).resolve().parents[1]
PROJECT = load_project(ROOT/'examples/demo/dik.project.json')


class CompactTests(unittest.TestCase):
    def test_round_trip_all_languages_including_missing(self):
        original = json.loads(PROJECT.graph.read_text(encoding='utf-8'))
        for lang in ('fr', 'en', 'fr-CA'):
            with self.subTest(lang=lang):
                p = project_compact(PROJECT,lang)
                self.assertEqual(p['projection_format'], COMPACT_PROFILE)
                self.assertEqual(restore_projection(p,PROJECT),original)
                self.assertEqual(restore_projection(p),original)
                self.assertNotIn('readable',p)
                self.assertEqual(set(p['lexicon']['entries']),{'KQ1001','KQ1002','KP2001'})
                self.assertEqual(p,project_compact(PROJECT,lang))

    def test_language_in_fallback_with_no_invention(self):
        lex = project_compact(PROJECT,'fr-CA')['lexicon']
        self.assertEqual(lex['coverage_counts'],{'direct':0,'fallback':1,'missing':2})
        self.assertEqual(lex['entries']['KQ1001']['label'],'Saint Augustin')
        self.assertEqual(lex['entries']['KQ1001']['effective_locale'],'fr')
        self.assertIsNone(lex['entries']['KQ1002']['label'])
        self.assertFalse(lex['complete_usable'])

    def test_tampering_checksums_and_verified_sources(self):
        p=project_compact(PROJECT,'fr')
        bad=copy.deepcopy(p)
        bad['lexicon']['entries']['KQ1001']['label']='other meaning'
        with self.assertRaises(DiKError):
            restore_projection(bad)
        bad['digests']['lexicon']=digest(bad['lexicon'])
        # A detached archive cannot authenticate a hostile editor; with source, reject.
        self.assertEqual(restore_projection(bad),p['canonical_graph'])
        with self.assertRaises(DiKError):
            restore_projection(bad,PROJECT)

    def test_duplicate_or_foreign_identifiers_fail_even_if_digest_changed(self):
        p=project_compact(PROJECT,'en')
        for modification in ('remove','add','counts','claim_direct','provenance'):
            with self.subTest(modification=modification):
                bad=copy.deepcopy(p)
                lex=bad['lexicon']
                if modification=='remove':
                    lex['entries'].pop('KQ1001')
                if modification=='add':
                    lex['entries']['KQ9999']={'status':'missing','label':None}
                if modification=='counts':
                    lex['coverage_counts']['missing']+=1
                if modification=='claim_direct':
                    lex['entries']['KQ1001']={'label':'Saint Augustin','status':'direct','effective_locale':'fr','layer_id':'invented'}
                if modification=='provenance':
                    lex['entries']['KQ1001']={'label':'Saint Augustin','status':'fallback'}
                bad['digests']['lexicon']=digest(lex)
                with self.assertRaises(DiKError):
                    restore_projection(bad)

    def test_literal_qualifier_protection_and_safe_markdown(self):
        p=project_compact(PROJECT,'fr')
        graph=copy.deepcopy(p['canonical_graph'])
        graph['assertions'][0]['object']={
            'kind':'literal','datatype':'string','value':'bon | mal\n<script>\t`test`'
        }
        graph['assertions'][0]['qualifiers']=[{'predicate':'KP2001','object':{'kind':'entity','id':'KQ1002'}}]
        p['canonical_graph']=graph
        p['digests']['canonical_graph']=digest(graph)
        self.assertEqual(restore_projection(p),graph)
        clean=compact_markdown(p,'clean')
        self.assertIn('bon \\| mal',clean)
        self.assertIn('&lt;script&gt;',clean)
        self.assertNotIn('`KP2001`',clean)
        annotated=compact_markdown(p,'annotated')
        self.assertIn('`KP2001`',annotated)
        self.assertIn('[KQ1002: non traduit]',clean)

    def test_compact_repeated_assertions_significantly_smaller(self):
        base=project_graph(PROJECT,'fr')
        compact=project_compact(PROJECT,'fr')
        graph=copy.deepcopy(compact['canonical_graph'])
        view=copy.deepcopy(base['readable'])
        original_stmt=copy.deepcopy(graph['assertions'][0])
        original_view=copy.deepcopy(view['statements'][0])
        # Synthetic repetition tests storage duplication, not registry validation.
        graph['assertions']=[dict(original_stmt,id=f'KA{3001+i}') for i in range(1000)]
        view['statements']=[dict(original_view,assertion_id=f'KA{3001+i}') for i in range(1000)]
        base['canonical_graph']=graph
        base['readable']=view
        compact['canonical_graph']=graph
        # Both store the same canonical facts, but only verbose repeats terms.
        compact_bytes=len(json.dumps(compact,ensure_ascii=False,separators=(',',':')))
        verbose_bytes=len(json.dumps(base,ensure_ascii=False,separators=(',',':')))
        self.assertLess(compact_bytes,verbose_bytes*0.72)
        _check_consistency(graph,compact['lexicon'])

    def test_cli_default_compact_and_legacy_verbose_flag(self):
        with tempfile.TemporaryDirectory() as dirname:
            root=Path(dirname)
            compact=root/'compact.json'; verbose=root/'verbose.json'; human=root/'human.md'; restored=root/'restored.json'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['projection','export','--project',str(PROJECT.manifest),
                                       '--locale','fr','--output',str(compact),'--markdown',str(human),
                                       '--style','clean']),0)
                self.assertEqual(main(['projection','export','--project',str(PROJECT.manifest),
                                       '--locale','fr','--output',str(verbose),'--format','verbose']),0)
                self.assertEqual(main(['projection','verify','--input',str(compact),
                                       '--project',str(PROJECT.manifest)]),0)
                self.assertEqual(main(['projection','restore','--input',str(compact),
                                       '--project',str(PROJECT.manifest),'--output',str(restored)]),0)
            self.assertEqual(json.loads(compact.read_text())['projection_format'],COMPACT_PROFILE)
            self.assertEqual(json.loads(verbose.read_text())['projection_format'],'dik.reversible-projection/1.0')
            self.assertEqual(json.loads(restored.read_text()),json.loads(PROJECT.graph.read_text()))
            self.assertNotIn('`KQ1001`',human.read_text())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['projection','export','--project',str(PROJECT.manifest),
                                       '--locale','fr','--output',str(compact)]),2)

    def test_no_undeclared_language(self):
        with self.assertRaises(DiKError):
            project_compact(PROJECT,'no-XX')


if __name__=='__main__':
    unittest.main()
