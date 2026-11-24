"""Regression tests: actual EncyK v0.2 schema, no licence/semantic promotion."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from dik.local_lexical_library import (
    LANGUAGES, build, lookup, plan, read_only_db, source_identity, status, export_summary,
)

ROOT=Path('30_working/lexical/harvester/index-v1')


def seed(root: Path, *, malformed=False):
    directory=root/ROOT
    directory.mkdir(parents=True)
    database=directory/'lexical.sqlite3'
    with sqlite3.connect(database) as db:
        db.executescript('''
            CREATE TABLE source_files(
              id INTEGER PRIMARY KEY,relative_path TEXT NOT NULL,kind TEXT,edition TEXT,
              status TEXT NOT NULL,source_sha256_verified INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE entries(
              id INTEGER PRIMARY KEY,source_id INTEGER NOT NULL,source_line INTEGER NOT NULL,
              language_code TEXT NOT NULL,lemma TEXT NOT NULL,lemma_key TEXT NOT NULL,pos TEXT,
              source_language_code TEXT,form_surface TEXT,form_key TEXT,grammatical_features TEXT,
              sense_observations INTEGER,form_observations INTEGER,translation_observations INTEGER,
              external_id TEXT,language_qid TEXT);
            CREATE INDEX idx_entries_language_lemma ON entries(language_code,lemma_key);
            CREATE TABLE language_stats(source_id INTEGER,language_code TEXT,lemma_observations INTEGER,
              sense_observations INTEGER,form_observations INTEGER,translation_observations INTEGER);
            INSERT INTO source_files VALUES(1,'raw-editions/fr/fr-extract.jsonl.gz','kaikki','fr','complete',0);
            INSERT INTO source_files VALUES(2,'unimorph/nob.zip','unimorph','nob','complete',0);
            INSERT INTO source_files VALUES(3,'broken/de.gz','kaikki','de','partial',0);
            INSERT INTO entries VALUES(1,1,1,'fr','chat','chat','noun','fra',NULL,NULL,NULL,2,3,0,NULL,NULL);
            INSERT INTO entries VALUES(2,1,2,'fr','chat','chat','noun','fra','chats','chats','PL',1,2,0,NULL,NULL);
            INSERT INTO entries VALUES(3,1,3,'fr','été','été','noun','fra',NULL,NULL,NULL,1,0,0,'L123','Q150');
            INSERT INTO entries VALUES(4,2,1,'nb','bok','bok','noun','nob',NULL,NULL,NULL,1,2,0,NULL,NULL);
            INSERT INTO entries VALUES(5,3,1,'de','Haus','haus','noun','deu',NULL,NULL,NULL,1,0,0,NULL,NULL);
            INSERT INTO language_stats VALUES(1,'fr',3,4,5,0);
            INSERT INTO language_stats VALUES(2,'nb',1,1,2,0);
            INSERT INTO language_stats VALUES(3,'de',1,1,0,0);
        ''')
        if malformed:
            db.execute('DROP INDEX idx_entries_language_lemma')
    (directory/'latest.json').write_text(json.dumps({
        'profile':'encyklopedia.lexical-source-index/candidate-v1',
        'database':str(database),'published':False,'source_licenses_reviewed':False,
        'generated_at':'2026-11-06T01:35:35Z'
    }),encoding='utf-8')
    (directory/'dik-source-handoff.candidate.json').write_text(json.dumps({
        'profile':'encyklopedia.to-dik.lexical-candidate-handoff/0.1',
        'source_index_database':str(database),'may_be_published':False
    }),encoding='utf-8')
    return database


class TestLocalLexicalLibrary(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/'EncyK'
        self.source=seed(self.root)
        self.dest=self.base/'diK-candidates'

    def test_plan_exact_fourteen_no_alias_and_no_changes(self):
        original=hashlib.sha256(self.source.read_bytes()).hexdigest()
        report=plan(encyk_root=self.root)
        self.assertEqual(report['language_codes'],list(LANGUAGES))
        self.assertEqual(report['languages']['fr']['lemmas'],3)
        self.assertEqual(report['languages']['no']['lemmas'],0)
        self.assertEqual(report['languages']['nn']['lemmas'],0)
        self.assertEqual(report['languages']['de']['lemmas'],0)
        self.assertFalse(report['dictionaries_published'])
        self.assertEqual(original,hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_build_all_no_invention_lookup_idempotent(self):
        report=build(encyk_root=self.root,output_dir=self.dest,batch_size=10,min_free_gib=0)
        self.assertEqual(report['status'],'COMPLETE')
        self.assertEqual(len(report['languages']),14)
        self.assertEqual(report['languages']['fr']['observations'],3)
        self.assertEqual(report['languages']['fr']['headword_pos_pairs'],2)
        self.assertEqual(report['languages']['no']['status'],'NO_DATA')
        self.assertEqual(report['languages']['de']['status'],'NO_DATA')
        self.assertEqual(status(collection_dir=self.dest)['status'],'COMPLETE')
        found=lookup(collection_dir=self.dest,language='fr',term='chat')
        self.assertEqual(found['results'][0]['source_observations'],2)
        self.assertFalse(found['publication'])
        form=lookup(collection_dir=self.dest,language='fr',term='chats')
        self.assertEqual(form['results'][0]['lemma'],'chat')
        with read_only_db(self.dest/'fr.sqlite3') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM observations').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT count(*) FROM lexemes').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT sum(license_reviewed) FROM sources').fetchone()[0],0)
        again=build(encyk_root=self.root,output_dir=self.dest,batch_size=10,min_free_gib=0)
        self.assertEqual(again['languages']['fr']['observations'],3)

    def test_export_is_tiny_and_no_private_paths_or_words(self):
        import zipfile
        build(encyk_root=self.root,output_dir=self.dest,batch_size=10,min_free_gib=0)
        report=self.base/'report.zip'
        result=export_summary(collection_dir=self.dest,output_zip=report)
        self.assertLess(result['size_bytes'],100_000)
        with zipfile.ZipFile(report) as z:
            self.assertEqual(set(z.namelist()),{'summary.json','langues.csv','SHA256_EXPORT.json'})
            doc=json.loads(z.read('summary.json'))
            self.assertEqual(doc['languages']['fr']['headword_pos_pairs'],2)
            self.assertNotIn(str(self.root), z.read('summary.json').decode())
            self.assertNotIn('chats', z.read('summary.json').decode())
            self.assertEqual(doc['published_dictionaries'],0)
        with self.assertRaises(FileExistsError):
            export_summary(collection_dir=self.dest,output_zip=report)

    def test_resume_partial_and_source_provenance(self):
        p=build(encyk_root=self.root,output_dir=self.dest,languages='fr',batch_size=10,
                max_rows_per_language=1,min_free_gib=0)
        self.assertEqual(p['status'],'PARTIAL')
        self.assertEqual(p['languages']['fr']['observations'],1)
        p=build(encyk_root=self.root,output_dir=self.dest,languages='fr',batch_size=10,min_free_gib=0)
        self.assertEqual(p['status'],'COMPLETE')
        self.assertEqual(p['languages']['fr']['observations'],3)
        with read_only_db(self.dest/'fr.sqlite3') as db:
            self.assertEqual(db.execute('SELECT source_line FROM observations ORDER BY source_row_id').fetchall(),[(1,),(2,),(3,)])

    def test_source_change_refused(self):
        build(encyk_root=self.root,output_dir=self.dest,languages='fr',batch_size=10,
              max_rows_per_language=1,min_free_gib=0)
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE entries SET lemma='chien' WHERE id=1")
        with self.assertRaisesRegex(ValueError,'incompatible'):
            build(encyk_root=self.root,output_dir=self.dest,languages='fr',batch_size=10,min_free_gib=0)

    def test_failclosed_schema_output_and_lang(self):
        with self.assertRaises(ValueError):
            build(encyk_root=self.root,output_dir=self.root/'within-source',min_free_gib=0)
        with self.assertRaises(ValueError):
            plan(encyk_root=self.root,languages='nb')
        with self.assertRaises(ValueError):
            plan(encyk_root=self.root,languages='fr,fr')
        foreign=self.base/'other'
        foreign.mkdir()
        (foreign/'user.txt').write_text('not for diK')
        with self.assertRaises(ValueError):
            build(encyk_root=self.root,output_dir=foreign,min_free_gib=0)

    def test_stat_missing_blocks_incomplete_false_success(self):
        with sqlite3.connect(self.source) as db:
            db.execute("DELETE FROM language_stats WHERE language_code='fr'")
        with self.assertRaisesRegex(ValueError,'language_stats manquant'):
            plan(encyk_root=self.root)

    def test_wrong_version_or_symlink_refused(self):
        with sqlite3.connect(self.source) as db:
            db.execute('DROP INDEX idx_entries_language_lemma')
        with self.assertRaisesRegex(ValueError,'Index EncyK'):
            plan(encyk_root=self.root)

if __name__=='__main__': unittest.main()
