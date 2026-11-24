"""DIK-LEX-1: materialise fourteen local *candidate* dictionaries from EncyK.

No network, no source writes, no canonical KQ/KP mutation and no licence promotion.
Only complete EncyK source files are eligible. Source SQLite is opened in
mode=ro with PRAGMA query_only=ON (never immutable=1: WAL may hold data).

The EncyK v0.2 index stores lemma/form observations and counts of senses, NOT
full glosses. This importer retains what is actually stored, without inventing
senses, equivalences or inflections.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
from urllib.parse import quote
from typing import Any, Iterator

LANGUAGES = ('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')
PROFILE = 'dik.local-lexical-library/5.7-candidate'
EN_INDEX = Path('30_working/lexical/harvester/index-v1')
FIELDS = (
    'id','source_id','source_line','language_code','lemma','lemma_key','pos',
    'source_language_code','form_surface','form_key','grammatical_features',
    'sense_observations','form_observations','translation_observations',
    'external_id','language_qid',
)
REQUIRED_TABLES = {
    'entries': set(FIELDS),
    'source_files': {'id','relative_path','kind','edition','status','source_sha256_verified'},
    'language_stats': {'source_id','language_code','lemma_observations','sense_observations',
                       'form_observations','translation_observations'},
}


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def canonical(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _json_read(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(doc, dict):
        raise ValueError('Document JSON invalide: ' + str(path))
    return doc


def _checked_file(path: Path) -> Path:
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError('Fichier regulier requis : ' + str(path))
    return path


def _stat(path: Path) -> dict[str, int] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError('Fichier source non regulier : ' + str(path))
    st = path.stat()
    return {'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns}


def source_identity(root: Path) -> dict[str, Any]:
    root = Path(root).absolute()
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Racine EncyK absente ou lien interdit: ' + str(root))
    directory = root / EN_INDEX
    latest = _checked_file(directory / 'latest.json')
    handoff = _checked_file(directory / 'dik-source-handoff.candidate.json')
    state, proposal = _json_read(latest), _json_read(handoff)
    if (state.get('profile') != 'encyklopedia.lexical-source-index/candidate-v1'
        or proposal.get('profile') != 'encyklopedia.to-dik.lexical-candidate-handoff/0.1'
        or proposal.get('may_be_published') is not False
        or state.get('published') is not False
        or state.get('source_licenses_reviewed') is not False):
        raise ValueError('EncyK : contrat de source candidate non reconnu')
    db = _checked_file(directory / 'lexical.sqlite3')
    declared = state.get('database')
    if not isinstance(declared,str) or not declared:
        raise ValueError('Manifest EncyK sans chemin SQLite')
    if Path(declared).absolute() != db:
        raise ValueError('Chemin SQLite non conforme au manifest EncyK')
    if str(proposal.get('source_index_database','')).casefold() != str(declared).casefold():
        raise ValueError('Incoherence entre manifest et handoff EncyK')
    identity = {
        'database': str(db),
        'database_stat': _stat(db),
        'wal_stat': _stat(Path(str(db) + '-wal')),
        'latest_sha256': sha256(latest),
        'handoff_sha256': sha256(handoff),
        'generated_at': state.get('generated_at'),
    }
    identity['fingerprint'] = hashlib.sha256(canonical(identity).encode('utf-8')).hexdigest()
    return identity


@contextmanager
def read_only_db(path: Path) -> Iterator[sqlite3.Connection]:
    # SQLite URI quoting ensures spaces and special characters in Windows paths.
    uri = 'file:' + quote(str(Path(path).absolute()).replace('\\','/'), safe='/:') + '?mode=ro'
    conn = sqlite3.connect(uri, uri=True, timeout=25)
    try:
        conn.execute('PRAGMA query_only=ON')
        conn.execute('PRAGMA busy_timeout=25000')
        if int(conn.execute('PRAGMA query_only').fetchone()[0]) != 1:
            raise RuntimeError('SQLite source pas en lecture seule')
        yield conn
    finally:
        conn.close()


def verify_schema(conn: sqlite3.Connection) -> None:
    for table, columns in REQUIRED_TABLES.items():
        actual = {row[1] for row in conn.execute('PRAGMA table_info(' + table + ')')}
        if not columns <= actual:
            raise ValueError(f'Schema EncyK incompatible: {table}, absent={sorted(columns-actual)}')
    indexes = {row[1] for row in conn.execute('PRAGMA index_list(entries)')}
    if 'idx_entries_language_lemma' not in indexes:
        raise ValueError('Index EncyK (language_code, lemma_key) absent; scan massif refuse')


def _languages(value: str | None) -> tuple[str, ...]:
    if value is None:
        return LANGUAGES
    codes = tuple(x.strip() for x in value.split(','))
    if not codes or any(x not in LANGUAGES for x in codes) or len(codes) != len(set(codes)):
        raise ValueError('Langues invalides (14 codes officiels exacts uniquement)')
    return codes


def _stats(conn: sqlite3.Connection) -> dict[str, dict[str, int]]:
    counts = {x: {'lemmas':0,'senses':0,'forms':0,'translations':0,'sources':0} for x in LANGUAGES}
    cur = conn.execute('''SELECT ls.language_code,
        COALESCE(SUM(ls.lemma_observations),0),
        COALESCE(SUM(ls.sense_observations),0),
        COALESCE(SUM(ls.form_observations),0),
        COALESCE(SUM(ls.translation_observations),0),COUNT(DISTINCT ls.source_id)
        FROM language_stats ls JOIN source_files sf ON sf.id=ls.source_id
        WHERE sf.status='complete' AND ls.language_code IN (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        GROUP BY ls.language_code''',LANGUAGES)
    for lang,lem,sens,forms,trans,sources in cur:
        counts[lang] = dict(lemmas=lem, senses=sens, forms=forms, translations=trans, sources=sources)
    # Prevent silent data loss if EncyK entries exist but summary rows are absent.
    for lang in LANGUAGES:
        if not counts[lang]['lemmas']:
            exists = conn.execute('''SELECT 1 FROM entries e INDEXED BY idx_entries_language_lemma
              WHERE e.language_code=? AND EXISTS(SELECT 1 FROM source_files sf
                WHERE sf.id=e.source_id AND sf.status='complete') LIMIT 1''',(lang,)).fetchone()
            if exists:
                raise ValueError('Index EncyK : language_stats manquant pour ' + lang)
    return counts


def plan(*, encyk_root: Path, languages: str | None = None) -> dict[str, Any]:
    selected = _languages(languages)
    identity = source_identity(encyk_root)
    with read_only_db(Path(identity['database'])) as src:
        verify_schema(src)
        stats = _stats(src)
        total = src.execute("SELECT COUNT(*) FROM source_files WHERE status='complete'").fetchone()[0]
        excluded = src.execute("SELECT status, COUNT(*) FROM source_files WHERE status<>'complete' GROUP BY status").fetchall()
    if source_identity(encyk_root)['fingerprint'] != identity['fingerprint']:
        raise RuntimeError('Source EncyK modifiee pendant le plan')
    return {
        'profile': PROFILE, 'status': 'PLAN_ONLY', 'network_used': False,
        'source_read_only': True, 'source_fingerprint': identity['fingerprint'],
        'source_fingerprint_strength': 'file-stat-and-small-manifests-not-whole-database-hash',
        'eligible_source_files':total,'excluded_source_states':dict(excluded),
        'languages': {k:stats[k] for k in selected}, 'language_codes':list(selected),
        'rights_reviewed':False,'semantic_equivalences_approved':0,'dictionaries_published':0,
        'note': 'Observations locales de l index, pas gloses/sens complets ni lemmes uniques',
    }


SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY, relative_path TEXT NOT NULL,kind TEXT,edition TEXT,
  source_sha256_verified INTEGER NOT NULL,license_reviewed INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lexemes (
  uid TEXT PRIMARY KEY, lemma_key TEXT NOT NULL,lemma TEXT NOT NULL,pos TEXT NOT NULL,
  semantic_status TEXT NOT NULL DEFAULT 'unreviewed_candidate');
CREATE INDEX IF NOT EXISTS lexemes_by_lemma ON lexemes(lemma);
CREATE TABLE IF NOT EXISTS observations (
  source_row_id INTEGER PRIMARY KEY, uid TEXT NOT NULL REFERENCES lexemes(uid),
  source_id INTEGER NOT NULL REFERENCES sources(id),source_line INTEGER NOT NULL,
  source_language_code TEXT,form_surface TEXT,form_key TEXT,grammatical_features TEXT,
  sense_observations INTEGER NOT NULL,form_observations INTEGER NOT NULL,
  translation_observations INTEGER NOT NULL,external_id TEXT,language_qid TEXT);
CREATE INDEX IF NOT EXISTS observations_by_uid ON observations(uid);
CREATE INDEX IF NOT EXISTS observations_by_form ON observations(form_surface);
'''


def _meta(conn: sqlite3.Connection, key: str, default: str = '') -> str:
    row = conn.execute('SELECT value FROM meta WHERE key=?',(key,)).fetchone()
    return row[0] if row else default


def _setmeta(conn: sqlite3.Connection, key: str, value: Any):
    conn.execute('INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                 (key,str(value)))


def _safe_output(source_root: Path, output: Path) -> Path:
    output = Path(output).absolute()
    root = Path(source_root).absolute()
    if output == root or output.is_relative_to(root) or root.is_relative_to(output):
        raise ValueError('La sortie doit etre hors de l arborescence EncyK')
    # Refuse existing symlinks/junctions throughout the output path.
    cur = output
    while True:
        if (cur.exists() or cur.is_symlink()) and (cur.is_symlink() or getattr(cur,'is_junction',lambda:False)()):
            raise ValueError('Lien symbolique ou jonction en sortie : '+str(cur))
        if cur.parent == cur:
            break
        cur = cur.parent
    return output


@contextmanager
def _exclusive_lock(output: Path):
    path = output/'dik-local-build.lock'
    with path.open('a+b') as f:
        f.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                if f.tell() == 0 and path.stat().st_size == 0:
                    f.write(b'0');f.flush();f.seek(0)
                msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except (OSError,BlockingIOError) as err:
            raise RuntimeError('Une autre construction diK est en cours') from err
        try:
            yield
        finally:
            if os.name=='nt':
                f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:
                fcntl.flock(f.fileno(),fcntl.LOCK_UN)


def _uid(language: str, key: str, lemma: str, pos: str) -> str:
    return hashlib.sha256('\x00'.join((language,key,lemma,pos)).encode('utf-8')).hexdigest()


def _create_or_verify(dest: Path, lang: str, identity: dict, expected: int, src: sqlite3.Connection) -> sqlite3.Connection:
    if dest.is_symlink() or getattr(dest,'is_junction',lambda:False)():
        raise ValueError('Dictionnaire symlink interdit')
    exists = dest.exists()
    conn = sqlite3.connect(dest,timeout=60)
    try:
        conn.execute('PRAGMA busy_timeout=60000')
        conn.execute('PRAGMA foreign_keys=ON')
        # Destination-only journal mode, never applied to EncyK source.
        if not exists:
            conn.execute('PRAGMA journal_mode=DELETE')
            conn.executescript(SCHEMA)
            with conn:
                for k,v in (('profile',PROFILE),('language',lang),('source_fingerprint',identity['fingerprint']),
                            ('status','IN_PROGRESS'),('last_key',''),('last_id','0'),('rows_imported','0'),
                            ('expected_rows',str(expected)),('rights_reviewed','0'),('published','0')):
                    _setmeta(conn,k,v)
                conn.executemany('''INSERT INTO sources
                  (id,relative_path,kind,edition,source_sha256_verified,license_reviewed,status)
                  VALUES (?,?,?,?,?,0,?)''', src.execute('''SELECT id,relative_path,kind,edition,
                  source_sha256_verified,status FROM source_files WHERE status='complete' ORDER BY id''').fetchall())
        else:
            if (_meta(conn,'profile') != PROFILE or _meta(conn,'language') != lang or
                _meta(conn,'source_fingerprint') != identity['fingerprint'] or
                _meta(conn,'expected_rows') != str(expected) or _meta(conn,'published') != '0'):
                raise ValueError('Dictionnaire existant incompatible, ne rien ecraser: '+str(dest))
            if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Dictionnaire local corrompu : '+str(dest))
        return conn
    except BaseException:
        conn.close()
        raise


def _batch(src: sqlite3.Connection, lang: str, last_key: str, last_id: int, n: int) -> list[tuple]:
    # Indexed (language_code, lemma_key) in EncyK; id is unique rowid tiebreaker.
    return src.execute('''SELECT e.id,e.source_id,e.source_line,e.language_code,e.lemma,e.lemma_key,
         e.pos,e.source_language_code,e.form_surface,e.form_key,e.grammatical_features,
         e.sense_observations,e.form_observations,e.translation_observations,e.external_id,e.language_qid
         FROM entries e INDEXED BY idx_entries_language_lemma
         WHERE e.language_code=? AND (e.lemma_key>? OR (e.lemma_key=? AND e.id>?))
         AND EXISTS (SELECT 1 FROM source_files sf WHERE sf.id=e.source_id AND sf.status='complete')
         ORDER BY e.lemma_key,e.id LIMIT ?''',(lang,last_key,last_key,last_id,n)).fetchall()


def _insert_batch(dst: sqlite3.Connection, lang: str, rows: list[tuple]) -> int:
    lexes = []
    obs = []
    for r in rows:
        rid,sid,line,code,lemma,key,pos,slang,form,fkey,features,senses,forms,translations,ext,qid = r
        if code!=lang or not isinstance(key,str) or not isinstance(lemma,str):
            raise ValueError('Langue ou type de lexeme incorrect dans l index')
        pos = pos or ''
        uid = _uid(lang,key,lemma,pos)
        lexes.append((uid,key,lemma,pos))
        obs.append((rid,uid,sid,line,slang,form,fkey,features,senses,forms,translations,ext,qid))
    with dst:
        dst.executemany('INSERT OR IGNORE INTO lexemes(uid,lemma_key,lemma,pos) VALUES(?,?,?,?)',lexes)
        dst.executemany('''INSERT OR IGNORE INTO observations(
          source_row_id,uid,source_id,source_line,source_language_code,form_surface,form_key,
          grammatical_features,sense_observations,form_observations,translation_observations,
          external_id,language_qid) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',obs)
        _setmeta(dst,'last_key',rows[-1][5])
        _setmeta(dst,'last_id',rows[-1][0])
        _setmeta(dst,'rows_imported',int(_meta(dst,'rows_imported','0'))+len(rows))
    return len(rows)


def _read_state(path: Path, expected: int) -> dict:
    if not path.is_file():
        return {'status':'NOT_STARTED','observations':0,'expected':expected}
    with read_only_db(path) as conn:
        return {'status':_meta(conn,'status','UNKNOWN'),
                'observations':int(_meta(conn,'rows_imported','0')),
                'expected':int(_meta(conn,'expected_rows','0')),
                'headword_pos_pairs':int(_meta(conn,'headword_pos_pairs','0')) if _meta(conn,'status')=='COMPLETE' else None,
                'path':str(path)}


def _write_report(out: Path, selected: tuple[str,...], stats: dict, identity: dict) -> dict:
    result = {
        'profile':PROFILE, 'generated_at':utc(), 'source_fingerprint':identity['fingerprint'],
        'source_read_only':True,'network_used':False,
        'licences_approved':0,'semantic_matches_approved':0,'published_dictionaries':0,
        'languages':{lang:_read_state(out / (lang+'.sqlite3'),stats[lang]['lemmas']) for lang in selected},
        'status':'COMPLETE' if all(_read_state(out/(lang+'.sqlite3'),stats[lang]['lemmas'])['status']
                                   in ('COMPLETE','NO_DATA') for lang in selected) else 'PARTIAL',
        'warning':'Dictionnaires locaux candidats : sens complets non presents dans index EncyK; pas de publication.'
    }
    tmp = out / ('manifest.json.tmp.' + str(os.getpid()))
    tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    os.replace(tmp, out/'manifest.json')
    return result


def build(*, encyk_root: Path, output_dir: Path, languages: str | None = None,
          batch_size: int = 4000, max_rows_per_language: int = 0,
          min_free_gib: float = 10.0) -> dict[str, Any]:
    """Build/resume full per-language dictionaries. max_rows=0 means NO LIMIT."""
    if batch_size < 10 or batch_size > 50000 or max_rows_per_language < 0 or min_free_gib < 0:
        raise ValueError('Parametres batch/limite/espace incorrects')
    langs = _languages(languages)
    identity = source_identity(encyk_root)
    out = _safe_output(encyk_root, output_dir)
    if out.exists() and not out.is_dir():
        raise ValueError('Sortie existante non repertoire')
    if out.exists() and not (out/'manifest.json').is_file() and any(out.iterdir()):
        raise ValueError('Repertoire sortie non vide et etranger : '+str(out))
    if (out/'manifest.json').is_file():
        existing=_json_read(out/'manifest.json')
        if existing.get('profile')!=PROFILE or existing.get('source_fingerprint')!=identity['fingerprint']:
            raise ValueError('Collection existante incompatible : choisir une nouvelle sortie')
    # Free space before starting; no huge archive copying, but full dictionaries take space.
    out.mkdir(parents=True,exist_ok=True)
    with _exclusive_lock(out):
        with read_only_db(Path(identity['database'])) as src:
            verify_schema(src)
            stats = _stats(src)
            # Manifest first: an interrupted import remains resumable.
            _write_report(out,langs,stats,identity)
            version = src.execute('PRAGMA data_version').fetchone()[0]
            for lang in langs:
                expected = int(stats[lang]['lemmas'])
                print(f'[diK V5.7] {lang}: {expected} observations eligibles',file=sys.stderr,flush=True)
                path = out/(lang+'.sqlite3')
                dst = _create_or_verify(path,lang,identity,expected,src)
                try:
                    if expected == 0:
                        with dst:_setmeta(dst,'status','NO_DATA')
                        _write_report(out, langs, stats, identity)
                        continue
                    inserted_this_run = 0
                    while True:
                        if source_identity(encyk_root)['fingerprint'] != identity['fingerprint'] or \
                           src.execute('PRAGMA data_version').fetchone()[0] != version:
                            raise RuntimeError('Index EncyK change pendant import : reprise bloquee')
                        # Never intentionally fill a disk below the requested reserve.
                        available=shutil.disk_usage(out).free
                        if available < int(min_free_gib*(1024**3)):
                            raise RuntimeError('Espace libre insuffisant sur le disque de sortie')
                        last_key,last_id=_meta(dst,'last_key'),int(_meta(dst,'last_id','0'))
                        budget=batch_size if not max_rows_per_language else min(batch_size,max_rows_per_language-inserted_this_run)
                        if budget<=0:
                            break
                        rows=_batch(src,lang,last_key,last_id,budget)
                        if not rows:
                            imported=int(_meta(dst,'rows_imported','0'))
                            with dst:
                                _setmeta(dst,'status','COMPLETE' if imported==expected else 'COUNT_MISMATCH')
                                if imported == expected:
                                    _setmeta(dst,'headword_pos_pairs',dst.execute('SELECT COUNT(*) FROM lexemes').fetchone()[0])
                            if imported!=expected:
                                raise RuntimeError(f'Index EncyK incoherent ({lang}): {imported} != {expected}')
                            break
                        _insert_batch(dst,lang,rows)
                        inserted_this_run+=len(rows)
                        if inserted_this_run % (batch_size*25) < batch_size:
                            print(f'[diK V5.7] {lang}: {_meta(dst,"rows_imported")} / {expected}',file=sys.stderr,flush=True)
                        if len(rows)<budget:
                            # Need an extra query to confirm the cursor reached its end.
                            continue
                    _write_report(out,langs,stats,identity)
                finally:
                    dst.close()
            if source_identity(encyk_root)['fingerprint'] != identity['fingerprint']:
                raise RuntimeError('Source EncyK changee pendant construction')
        return _write_report(out,langs,stats,identity)


def status(*, collection_dir: Path) -> dict[str,Any]:
    out=Path(collection_dir)
    doc=_json_read(out/'manifest.json')
    if doc.get('profile')!=PROFILE or doc.get('published_dictionaries')!=0:
        raise ValueError('Collection locale non reconnue')
    res={**doc,'languages':{}}
    for lang, info in doc['languages'].items():
        if lang not in LANGUAGES:
            raise ValueError('Code non canonique en sortie')
        current=_read_state(out/(lang+'.sqlite3'),info['expected'])
        if current['expected']!=info['expected']:
            raise ValueError('Etat du dictionnaire incoherent: '+lang)
        res['languages'][lang]=current
    return res


def lookup(*, collection_dir: Path, language: str, term: str, limit: int = 20) -> dict[str,Any]:
    if language not in LANGUAGES or not term or len(term)>200 or not (1<=limit<=100):
        raise ValueError('Langue, terme ou limite incorrects')
    path=Path(collection_dir)/(language+'.sqlite3')
    _checked_file(path)
    with read_only_db(path) as conn:
        if _meta(conn,'profile')!=PROFILE or _meta(conn,'language')!=language:
            raise ValueError('Dictionnaire candidat non reconnu')
        matches=conn.execute('''SELECT l.lemma,l.pos,l.lemma_key,COUNT(o.source_row_id),
             SUM(o.sense_observations),SUM(o.form_observations),SUM(o.translation_observations)
             FROM lexemes l JOIN observations o ON o.uid=l.uid
             WHERE l.lemma=? GROUP BY l.uid ORDER BY l.pos LIMIT ?''',(term,limit)).fetchall()
        if not matches:
            matches=conn.execute('''SELECT l.lemma,l.pos,l.lemma_key,COUNT(o.source_row_id),
               SUM(o.sense_observations),SUM(o.form_observations),SUM(o.translation_observations)
               FROM observations o JOIN lexemes l ON l.uid=o.uid
               WHERE o.form_surface=? GROUP BY l.uid ORDER BY l.lemma LIMIT ?''',(term,limit)).fetchall()
    return {'profile':PROFILE,'language':language,'query':term,'publication':False,
            'results':[dict(lemma=x[0],pos=x[1],search_key=x[2],source_observations=x[3],
                            sense_counts=x[4],form_counts=x[5],translation_counts=x[6]) for x in matches]}


def export_summary(*, collection_dir: Path, output_zip: Path) -> dict[str, Any]:
    """Privacy-conscious tiny ZIP: counters only, never words, paths or source DBs."""
    import csv
    import io
    import zipfile
    state = status(collection_dir=collection_dir)
    output_zip = Path(output_zip).absolute()
    if output_zip.exists() or output_zip.is_symlink():
        raise FileExistsError('Un rapport existe deja : '+str(output_zip))
    if output_zip.suffix.lower() != '.zip':
        raise ValueError('Rapport attendu au format ZIP')
    if output_zip.is_relative_to(Path(collection_dir).absolute()):
        raise ValueError('Exporter le rapport hors des bases locales')
    # Do not leak local Windows paths or lexical content into support reports.
    rows = {}
    for lang, data in state['languages'].items():
        rows[lang] = {
            'status':data['status'],
            'observations':data['observations'],
            'expected':data['expected'],
            'headword_pos_pairs':data.get('headword_pos_pairs'),
        }
    report = {
        'profile': 'dik.local-lexical-library-summary/5.7',
        'generated_at':utc(),
        'source_fingerprint':state['source_fingerprint'],
        'status': 'COMPLETE' if all(r['status'] in ('COMPLETE','NO_DATA') for r in rows.values()) else 'PARTIAL',
        'languages':rows,
        'network_used':False, 'source_read_only':True,
        'licences_approved':0,'semantic_matches_approved':0,'published_dictionaries':0,
        'limitations':['unreviewed_source_licences','no_source_approved_sha256',
                       'lemma_and_form_observations_not_complete_senses',
                       'no_kq_kp_automatic_promotion', 'no_language_alias_fallback'],
    }
    stream = io.StringIO(newline='')
    writer = csv.writer(stream)
    writer.writerow(('language','status','observations','expected','headword_pos_pairs'))
    for lang in LANGUAGES:
        if lang in rows:
            d=rows[lang]
            writer.writerow((lang,d['status'],d['observations'],d['expected'],
                             d['headword_pos_pairs'] if d['headword_pos_pairs'] is not None else ''))
    body = (json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode('utf-8')
    summary = stream.getvalue().encode('utf-8-sig')
    hashes = (json.dumps({'summary.json':hashlib.sha256(body).hexdigest(),
                          'langues.csv':hashlib.sha256(summary).hexdigest()},indent=2)+'\n').encode('utf8')
    output_zip.parent.mkdir(parents=True,exist_ok=True)
    temp = output_zip.with_name(output_zip.name+'.partial.'+str(os.getpid()))
    try:
        with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('summary.json',body)
            z.writestr('langues.csv',summary)
            z.writestr('SHA256_EXPORT.json',hashes)
        if temp.stat().st_size > 1_048_576:
            raise ValueError('Rapport trop volumineux : plus de 1 Mio')
        os.replace(temp,output_zip)
    finally:
        temp.unlink(missing_ok=True)
    return {'status':'EXPORTED','zip':str(output_zip),'size_bytes':output_zip.stat().st_size,
            'languages':len(rows),'contains_lexical_words':False,'contains_local_paths':False}
