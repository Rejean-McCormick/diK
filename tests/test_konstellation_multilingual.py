import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integrations'/'konstellation_light'))
from contract import new_document,validate,ContractError
DIGEST='sha256:'+'a'*64
class ContractTests(unittest.TestCase):
    def test_locale_without_fixed_supported_languages(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'ja',[
            {'node_id':'KQ1','label':'星', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'review:1'}}])
        self.assertEqual(validate(doc,require_reviewed=True)['locale'],'ja')
    def test_candidate_never_published_by_reader(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'fr-CA',[
            {'node_id':'KQ1','definition':'Note candidate.', 'provenance':{'provider':'editorial','source_refs':['source:1'], 'review_status':'candidate'}}])
        with self.assertRaises(ContractError):validate(doc,require_reviewed=True)
    def test_reject_duplicate_identity(self):
        row={'node_id':'KQ1','label':'Term', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'r1'}}
        with self.assertRaises(ContractError):new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'en',[row,row])

import json
from from_dik import export
class DiKAdapterTests(unittest.TestCase):
    def test_curated_reviewed_terms(self):
        curated=json.loads((ROOT/'examples/demo/dictionaries/curated-fr.json').read_text(encoding='utf-8'))
        obj=export(curated,slug='astronomy',state_ref='urn:kristal:astronomy:state',surface_digest=DIGEST)
        self.assertEqual(obj['entries'][0]['node_id'],'KQ1001')
        self.assertEqual(obj['entries'][0]['provenance']['review_status'],'reviewed')
    def test_imported_data_not_automatically_curated(self):
        with self.assertRaises(ContractError):export({'schema_version':'11.0','artifact_type':'kristal_wikidata_lexical_record'},slug='astronomy',state_ref='urn:x',surface_digest=DIGEST)

    def test_curated_predicate_is_a_relation_not_a_node(self):
        obj=export({'schema_version':'11.0','artifact_type':'kristal_curated_dictionary','language':'en',
                    'entries':[{'semantic_id':'KP500','preferred_term':'Related to','review':{'decision_id':'review:kp'}}]},
                    slug='astronomy',state_ref='urn:x',surface_digest=DIGEST)
        self.assertEqual(len(obj['entries']),0)
        self.assertEqual(obj['relations'][0]['relation_id'],'KP500')
