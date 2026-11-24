"""V5.8: test exact EncyK v0.5/v0.6 schema and safe 14-language federation."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

from dik.local_lexical_library import build,read_only_db
from dik.semantic_evidence_bridge import (
    _fingerprint_index, _candidate_id_real, bind, export_summary, lookup, plan,
)


class TestV58(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.root=self.base/'EncyK'
        self.collection=self.base/'collection-v57'
        idx=self.root/'30_working/lexical/harvester/index-v1'
        idx.mkdir(parents=True)
        self.index=idx/'lexical.sqlite3'
        with sqlite3.connect(self.index) as db:
            db.executescript('''
                CREATE TABLE source_files(id INTEGER PRIMARY KEY,relative_path TEXT,kind TEXT,edition TEXT,
                    status TEXT,source_sha256_verified INTEGER,size_bytes INTEGER,mtime_ns INTEGER,
                    cursor_lines INTEGER,accepted INTEGER,rejected INTEGER);
                CREATE TABLE entries(id INTEGER PRIMARY KEY,source_id INTEGER,source_line INTEGER,
                    language_code TEXT,lemma TEXT,lemma_key TEXT,pos TEXT,source_language_code TEXT,
                    form_surface TEXT,form_key TEXT,grammatical_features TEXT,sense_observations INTEGER,
                    form_observations INTEGER,translation_observations INTEGER,external_id TEXT,language_qid TEXT);
                CREATE INDEX idx_entries_language_lemma ON entries(language_code,lemma_key);
                CREATE TABLE language_stats(source_id INTEGER,language_code TEXT,lemma_observations INTEGER,
                    sense_observations INTEGER,form_observations INTEGER,translation_observations INTEGER);
                INSERT INTO source_files VALUES(1,'lex/fr.gz','kaikki','fr','complete',0,111,222,2,2,0);
                INSERT INTO source_files VALUES(2,'lex/en.gz','wikidata','en','complete',0,333,444,1,1,0);
                INSERT INTO entries VALUES(1,1,42,'fr','chat','chat','noun','fra',NULL,NULL,NULL,2,3,0,NULL,NULL);
                INSERT INTO entries VALUES(2,1,43,'fr','chat','chat','noun','fra','chats','chats','PL',1,2,0,NULL,NULL);
                INSERT INTO entries VALUES(3,2,8,'en','cat','cat','noun','eng',NULL,NULL,NULL,1,2,0,'L123','Q150');
                INSERT INTO language_stats VALUES(1,'fr',2,3,5,0);
                INSERT INTO language_stats VALUES(2,'en',1,1,2,0);
            ''')
            fingerprint=_fingerprint_index(db)
        (idx/'latest.json').write_text(json.dumps({'profile':'encyklopedia.lexical-source-index/candidate-v1',
            'database':str(self.index),'published':False,'source_licenses_reviewed':False}),encoding='utf-8')
        (idx/'dik-source-handoff.candidate.json').write_text(json.dumps({
            'profile':'encyklopedia.to-dik.lexical-candidate-handoff/0.1',
            'source_index_database':str(self.index),'may_be_published':False}),encoding='utf-8')
        build(encyk_root=self.root,output_dir=self.collection,min_free_gib=0,batch_size=10)
        rec=self.root/'30_working/lexical/harvester/dik-reconciliation-v1'
        enr=self.root/'30_working/lexical/harvester/dik-enrichment-v1'
        rec.mkdir(parents=True)
        enr.mkdir(parents=True)
        self.recdb=rec/'reconciliation.sqlite3'
        self.enrdb=enr/'enrichment.sqlite3'
        cid=_candidate_id_real('fr','chat')
        with sqlite3.connect(self.recdb) as db:
            db.executescript('''
                CREATE TABLE meta(k TEXT PRIMARY KEY,v TEXT);
                CREATE TABLE completed_languages(language TEXT PRIMARY KEY,cross_family_keys INTEGER);
                CREATE TABLE candidates(candidate_id TEXT PRIMARY KEY,language TEXT,lemma_key TEXT,provenance_json TEXT);
            ''')
            db.executemany('INSERT INTO meta VALUES(?,?)',[('index_fingerprint',fingerprint),
                     ('profile','encyklopedia.dik-lex1-candidate-reconciliation/0.5')])
            db.execute('INSERT INTO completed_languages VALUES(?,?)',('fr',1))
            db.execute('INSERT INTO candidates VALUES(?,?,?,?)',(cid,'fr','chat','{}'))
        with sqlite3.connect(self.enrdb) as db:
            db.executescript('''
                CREATE TABLE meta(k TEXT PRIMARY KEY,v TEXT);
                CREATE TABLE staged_languages(language TEXT PRIMARY KEY,candidate_count INTEGER,anchors_added INTEGER);
                CREATE TABLE evidence(source_id INTEGER,source_line INTEGER,candidate_id TEXT,language TEXT,
                    status TEXT,payload_json TEXT,PRIMARY KEY(source_id,source_line,candidate_id));
                CREATE INDEX ix_evidence_language_candidate ON evidence(language,candidate_id);
                CREATE TABLE review_tiers(language TEXT,tier TEXT,candidates INTEGER);
                CREATE TABLE source_progress(source_id INTEGER,status TEXT);
            ''')
            db.executemany('INSERT INTO meta VALUES(?,?)',[('index_fingerprint',fingerprint),
                   ('profile','encyklopedia.dik-lex1-anchored-evidence/candidate-v0.6')])
            db.execute('INSERT INTO staged_languages VALUES(?,?,?)',('fr',1,2))
            db.execute('INSERT INTO review_tiers VALUES(?,?,?)',('fr','some_sense_evidence_for_review',1))
            for line,word in [(42,'un félin'),(99,'une autre entrée')]:
                payload={'profile':'encyklopedia.dik-lex1-anchored-evidence/candidate-v0.6',
                         'candidate_id':cid,'language':'fr','source_id':1,'source_line':line,
                         'family':'kaikki','source_relative_path':'lex/fr.gz','status':'observed','sense_alignment_approved':False,
                         'license_reviewed':False,'observed_record':{'senses':[{'glosses':[word]}]}}
                db.execute('INSERT INTO evidence VALUES(?,?,?,?,?,?)',
                           (1,line,cid,'fr','observed',json.dumps(payload)))
        self._write_manifests(rec,enr,fingerprint)

    def _write_manifests(self,rec,enr,fp):
        (rec/'latest.json').write_text(json.dumps({
            'profile':'encyklopedia.dik-lex1-candidate-reconciliation/0.5',
            'status':'candidate_complete','source_index_fingerprint':fp,
            'candidate_database':str(self.recdb), 'approved_semantic_equivalences':0}),encoding='utf-8')
        (rec/'dik-review-queue.candidate.json').write_text(json.dumps({
            'profile':'encyklopedia.to-dik.lexical-review-queue/candidate-v0.5',
            'status':'unreviewed_candidate','source_index_fingerprint':fp,
            'may_be_published':False,'approved_matches':0}),encoding='utf-8')
        (enr/'latest.json').write_text(json.dumps({
            'profile':'encyklopedia.dik-lex1-anchored-evidence/candidate-v0.6',
            'status':'candidate_evidence_complete','source_index_fingerprint':fp,
            'output_database':str(self.enrdb),'approved_semantic_equivalences':0,
            'source_license_reviewed':False,'source_official_sha256_verified':False}),encoding='utf-8')
        (enr/'dik-enriched-handoff.candidate.json').write_text(json.dumps({
            'profile':'encyklopedia.to-dik.enriched-evidence-candidate/0.6',
            'source_index_fingerprint':fp,'may_be_published':False,'approved_matches':0}),encoding='utf-8')

    def test_read_only_plan_and_binding_idempotence(self):
        prior=self.index.stat().st_size
        data=plan(encyk_root=self.root,collection_dir=self.collection)
        self.assertEqual(set(data['languages']),{'en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt'})
        self.assertEqual(data['languages']['fr']['candidate_keys'],1)
        self.assertEqual(data['languages']['en']['candidate_keys'],0)
        self.assertEqual(data['approved_sense_matches'],0)
        result=bind(encyk_root=self.root,collection_dir=self.collection)
        self.assertEqual(result['languages_bound'],14)
        again=bind(encyk_root=self.root,collection_dir=self.collection)
        self.assertEqual(again['languages_bound'],14)
        self.assertEqual(self.index.stat().st_size,prior)
        self.assertEqual(len(list((self.collection/'semantic-v58').glob('*.json'))),14)

    def test_lookup_strict_line_anchor_and_homograph(self):
        bind(encyk_root=self.root,collection_dir=self.collection)
        result=lookup(encyk_root=self.root,collection_dir=self.collection,language='fr',term='chat')
        self.assertFalse(result['published'])
        proofs=result['results'][0]['candidate_evidence']
        self.assertEqual(len(proofs),2)
        self.assertEqual([p['anchor_matches_same_lexeme'] for p in proofs],[True,False])
        self.assertEqual(proofs[0]['gloss_candidates'],['un félin'])
        self.assertFalse(proofs[0]['sense_alignment_approved'])
        from_form=lookup(encyk_root=self.root,collection_dir=self.collection,language='fr',term='chats')
        self.assertEqual(from_form['results'][0]['lemma'],'chat')
        english=lookup(encyk_root=self.root,collection_dir=self.collection,language='en',term='cat')
        self.assertEqual(english['results'][0]['evidence_status'],'NO_CROSS_FAMILY_SAMPLE')
        with self.assertRaises(ValueError):
            lookup(encyk_root=self.root,collection_dir=self.collection,language='nb',term='bok')

    def test_report_without_words_paths_and_no_massive_copy(self):
        bind(encyk_root=self.root,collection_dir=self.collection)
        target=self.base/'report.zip'
        exported=export_summary(encyk_root=self.root,collection_dir=self.collection,output_zip=target)
        self.assertLess(exported['size_bytes'],40_000)
        with zipfile.ZipFile(target) as z:
            data=b''.join(z.read(n) for n in z.namelist())
            self.assertNotIn(str(self.root).encode(),data)
            self.assertNotIn('un f',data.decode('utf-8',errors='ignore'))
            self.assertEqual(json.loads(z.read('summary.json'))['approved_semantic_equivalences'],0)
        with self.assertRaises(ValueError):
            export_summary(encyk_root=self.root,collection_dir=self.collection,output_zip=target)

    def test_contract_change_ambiguous_or_foreign_binding_refused(self):
        bind(encyk_root=self.root,collection_dir=self.collection)
        bridge=self.collection/'semantic-v58/fr.json'
        bridge.write_text('{"modified":"user"}',encoding='utf-8')
        with self.assertRaises(ValueError):
            bind(encyk_root=self.root,collection_dir=self.collection,languages='fr')
        with self.assertRaises(ValueError):
            lookup(encyk_root=self.root,collection_dir=self.collection,language='fr',term='chat')
        with self.assertRaises(ValueError):
            plan(encyk_root=self.root,collection_dir=self.collection,languages='nb')

    def test_upstream_fingerprint_or_publication_refused(self):
        latest=self.root/'30_working/lexical/harvester/dik-enrichment-v1/latest.json'
        doc=json.loads(latest.read_text())
        doc['source_index_fingerprint']='f'*64
        latest.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'empreintes'):
            plan(encyk_root=self.root,collection_dir=self.collection)

    def test_no_v57_database_write(self):
        path=self.collection/'fr.sqlite3'
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        bind(encyk_root=self.root,collection_dir=self.collection)
        lookup(encyk_root=self.root,collection_dir=self.collection,language='fr',term='chat')
        self.assertEqual(before,hashlib.sha256(path.read_bytes()).hexdigest())

    def test_unapproved_source_status_is_not_promoted(self):
        handoff=self.root/'30_working/lexical/harvester/dik-enrichment-v1/dik-enriched-handoff.candidate.json'
        doc=json.loads(handoff.read_text())
        doc['may_be_published']=True
        handoff.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'contrat'):
            plan(encyk_root=self.root,collection_dir=self.collection)

    def test_sense_payload_wrong_source_family_refused(self):
        bind(encyk_root=self.root,collection_dir=self.collection)
        with sqlite3.connect(self.enrdb) as db:
            payload=json.loads(db.execute('SELECT payload_json FROM evidence WHERE source_line=42').fetchone()[0])
            payload['source_relative_path']='malicious/other-source.gz'
            db.execute('UPDATE evidence SET payload_json=? WHERE source_line=42',(json.dumps(payload),))
        with self.assertRaisesRegex(ValueError,'Provenance'):
            lookup(encyk_root=self.root,collection_dir=self.collection,language='fr',term='chat')

    def test_preflight_all_languages_before_writes(self):
        bind(encyk_root=self.root,collection_dir=self.collection,languages='pt')
        (self.collection/'semantic-v58/pt.json').write_text('user customised',encoding='utf-8')
        with self.assertRaises(ValueError):
            bind(encyk_root=self.root,collection_dir=self.collection)
        self.assertFalse((self.collection/'semantic-v58/fr.json').exists())

    def test_review_queue_counts_must_match(self):
        with sqlite3.connect(self.enrdb) as db:
            db.execute('UPDATE staged_languages SET candidate_count=2 WHERE language=?',('fr',))
        with self.assertRaisesRegex(ValueError,'nombre de candidats'):
            plan(encyk_root=self.root,collection_dir=self.collection)


if __name__=='__main__':unittest.main()
