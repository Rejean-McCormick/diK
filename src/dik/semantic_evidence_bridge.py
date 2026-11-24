"""DIK-LEX-1 V5.8: federated, read-only EncyK semantic evidence for 14 local dictionaries.

EncyK v0.5 candidates are homographs, not meanings. v0.6 evidence is sampled and
source-anchored. This bridge never copies the massive EncyK SQLite data,
changes a V5.7 SQLite, approves rights, maps L/S/F to KQ/KP, or publishes data.
"""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import zipfile

from .local_lexical_library import (
    LANGUAGES, PROFILE as LEX_PROFILE, _checked_file, _exclusive_lock,
    _json_read, _languages, _meta, _safe_output, read_only_db, sha256, source_identity,
)

BRIDGE_PROFILE = 'dik.enriched-local-dictionary/5.8-candidate'
REPORT_PROFILE = 'dik.enriched-local-summary/5.8'
H_ROOT = Path('30_working/lexical/harvester')
ENR = H_ROOT / 'dik-enrichment-v1'
REC = H_ROOT / 'dik-reconciliation-v1'
INDEX = H_ROOT / 'index-v1'
V05 = 'encyklopedia.dik-lex1-candidate-reconciliation/0.5'
V06 = 'encyklopedia.dik-lex1-anchored-evidence/candidate-v0.6'


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _fingerprint_index(db: sqlite3.Connection) -> str:
    """Byte-compatible with EncyK quality_audit.db_fingerprint, no entry scan."""
    h = hashlib.sha256()
    version = db.execute('PRAGMA user_version').fetchone()[0]
    h.update(f'lexical-quality-v1|{version}\n'.encode())
    for row in db.execute('''SELECT id,relative_path,kind,edition,size_bytes,mtime_ns,
        status,cursor_lines,accepted,rejected FROM source_files ORDER BY id'''):
        h.update(json.dumps(row, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n')
    for row in db.execute('''SELECT source_id,language_code,lemma_observations,
        sense_observations,form_observations,translation_observations
        FROM language_stats ORDER BY source_id,language_code'''):
        h.update(json.dumps(row, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n')
    return h.hexdigest()


def _tables(db, required):
    for table, expected in required.items():
        available = {r[1] for r in db.execute(f'PRAGMA table_info({table})')}
        if not expected <= available:
            raise ValueError('Schema EncyK v0.5/v0.6 incompatible: '
                             + table + ': ' + ','.join(sorted(expected-available)))


def _safe_dbfile(root: Path, directory: Path, field: str, manifest: dict, filename: str) -> Path:
    expected = (root / directory / filename).absolute()
    declared = manifest.get(field)
    if not isinstance(declared, str) or not declared:
        raise ValueError('Champ de base EncyK manquant : ' + field)
    # Windows path stored by EncyK; string compare avoids comparing foreign Path semantics.
    if str(declared).replace('/', '\\').casefold() != str(expected).replace('/', '\\').casefold():
        raise ValueError('Chemin de base EncyK non conforme : ' + field)
    return _checked_file(expected)


def _load_contract(root: Path, collection: Path) -> dict:
    root, collection = Path(root).absolute(), Path(collection).absolute()
    if not root.is_dir() or not collection.is_dir():
        raise ValueError('Racine EncyK ou collection V5.7 manquante')
    index_identity = source_identity(root)
    v57 = _json_read(collection / 'manifest.json')
    if (v57.get('profile') != LEX_PROFILE or v57.get('published_dictionaries') != 0 or
            v57.get('source_fingerprint') != index_identity['fingerprint']):
        raise ValueError('Collection V5.7 absente, approuvee ou liee a un autre index EncyK')
    v05 = _json_read(_checked_file(root / REC / 'latest.json'))
    v06 = _json_read(_checked_file(root / ENR / 'latest.json'))
    h05 = _json_read(_checked_file(root / REC / 'dik-review-queue.candidate.json'))
    h06 = _json_read(_checked_file(root / ENR / 'dik-enriched-handoff.candidate.json'))
    if (v05.get('profile') != V05 or v05.get('status') != 'candidate_complete' or
        v06.get('profile') != V06 or v06.get('status') != 'candidate_evidence_complete' or
        h05.get('profile') != 'encyklopedia.to-dik.lexical-review-queue/candidate-v0.5' or
        h06.get('profile') != 'encyklopedia.to-dik.enriched-evidence-candidate/0.6' or
        h05.get('may_be_published') is not False or h06.get('may_be_published') is not False or
        h05.get('approved_matches') != 0 or h06.get('approved_matches') != 0 or
        v05.get('approved_semantic_equivalences',0) != 0 or
        v06.get('approved_semantic_equivalences') != 0 or
        v06.get('source_license_reviewed') is not False or
        v06.get('source_official_sha256_verified') is not False):
        raise ValueError('EncyK v0.5/v0.6 : contrat non canonique inattendu')
    fingerprints = {v05.get('source_index_fingerprint'),v06.get('source_index_fingerprint'),
                    h05.get('source_index_fingerprint'),h06.get('source_index_fingerprint')}
    if len(fingerprints)!=1 or None in fingerprints:
        raise ValueError('EncyK : empreintes v0.5/v0.6 divergentes')
    rec_db = _safe_dbfile(root, REC, 'candidate_database', v05, 'reconciliation.sqlite3')
    enr_db = _safe_dbfile(root, ENR, 'output_database', v06, 'enrichment.sqlite3')
    with ExitStack() as stack:
        idx = stack.enter_context(read_only_db(Path(index_identity['database'])))
        rec = stack.enter_context(read_only_db(rec_db))
        enr = stack.enter_context(read_only_db(enr_db))
        _tables(idx,{'source_files':{'id','relative_path','kind','edition','size_bytes','mtime_ns','status',
                                    'cursor_lines','accepted','rejected'},
                     'language_stats':{'source_id','language_code','lemma_observations',
                                     'sense_observations','form_observations','translation_observations'}})
        _tables(rec,{'meta':{'k','v'},'completed_languages':{'language','cross_family_keys'},
                     'candidates':{'candidate_id','language','lemma_key','provenance_json'}})
        _tables(enr,{'meta':{'k','v'},'staged_languages':{'language','candidate_count','anchors_added'},
                     'evidence':{'candidate_id','language','source_id','source_line','status','payload_json'},
                     'review_tiers':{'language','tier','candidates'},'source_progress':{'status'}})
        index_fp = _fingerprint_index(idx)
        if index_fp not in fingerprints:
            raise ValueError('EncyK : catalogue index-v1 modifie depuis enrichissement')
        for db, profile in ((rec,V05),(enr,V06)):
            m = dict(db.execute("SELECT k,v FROM meta WHERE k IN ('index_fingerprint','profile')"))
            if m.get('index_fingerprint') != index_fp or m.get('profile') != profile:
                raise ValueError('EncyK : meta SQLite incoherentes avec manifestes')
        # Quick validation of lookup indexes; prevents accidental multi-gigabyte scans.
        ric = {row[1] for row in rec.execute('PRAGMA index_list(candidates)')}
        eic = {row[1] for row in enr.execute('PRAGMA index_list(evidence)')}
        if 'ix_evidence_language_candidate' not in eic or not ric:
            raise ValueError('Index SQLite requis absent : rapprochement massif refuse')
        perlang = {}
        tiers = {}
        allowed_tiers={'glosses_plus_wikidata_sense_ids_for_review',
                       'morphology_or_lemma_only','some_sense_evidence_for_review'}
        for lang,tier,count in enr.execute('SELECT language,tier,candidates FROM review_tiers'):
            if lang in LANGUAGES:
                if tier not in allowed_tiers or int(count)<0:
                    raise ValueError('Type de revue EncyK non reconnu')
                tiers.setdefault(lang,{})[tier] = count
        progress=dict(enr.execute('SELECT status,COUNT(*) FROM source_progress GROUP BY status'))
        if any(status!='complete' for status in progress):
            raise ValueError('Preuves EncyK v0.6 non entierement capturees')
        recon = dict(rec.execute('SELECT language,cross_family_keys FROM completed_languages'))
        staged = {lang:(c,a) for lang,c,a in enr.execute('SELECT language,candidate_count,anchors_added FROM staged_languages')}
        for lang in LANGUAGES:
            a,b = staged.get(lang,(0,0))
            if a < 0 or b < 0 or recon.get(lang,0)<0:
                raise ValueError('Compteur source negatif')
            if recon.get(lang,0) != a:
                raise ValueError('EncyK : nombre de candidats v0.5/v0.6 different : '+lang)
            if sum(tiers.get(lang,{}).values()) not in (0,a):
                raise ValueError('EncyK : revue par tier incoherente : '+lang)
            perlang[lang]={'candidate_keys':a, 'sampled_source_anchors':b,
                           'cross_family_keys':recon.get(lang,0),
                           'review_tiers':tiers.get(lang,{}),
                           'lexical_observations':v57.get('languages',{}).get(lang,{}).get('observations',0),
                           'v57_status':v57.get('languages',{}).get(lang,{}).get('status','NOT_STARTED')}
    hashes = {name:sha256(root / directory / name) for directory,names in (
        (REC,('latest.json','dik-review-queue.candidate.json')),
        (ENR,('latest.json','dik-enriched-handoff.candidate.json')))
        for name in names}
    return {'root':root,'collection':collection,'index_fp':index_fp,
            'collection_fp':index_identity['fingerprint'],
            'manifest_hashes':hashes,'reconciliation_db':rec_db,'enrichment_db':enr_db,
            'languages':perlang}


def plan(*, encyk_root: Path, collection_dir: Path, languages: str | None=None) -> dict:
    selected = _languages(languages)
    contract=_load_contract(encyk_root,collection_dir)
    return {'profile':BRIDGE_PROFILE,'status':'PLAN_ONLY','network_used':False,
            'source_read_only':True,'no_massive_copy':True,
            'languages':{lang:contract['languages'][lang] for lang in selected},
            'approved_sense_matches':0,'licensed_sources_approved':0,
            'published_dictionaries':0,
            'limitation':'v0.6 sampled, homographs not semantic equivalences; source review required'}


def _bond_hash(contract: dict) -> str:
    material={'collection_fp':contract['collection_fp'],'index_fp':contract['index_fp'],
              'manifest_hashes':contract['manifest_hashes']}
    return hashlib.sha256(json.dumps(material,sort_keys=True).encode('utf-8')).hexdigest()


def bind(*, encyk_root:Path, collection_dir:Path, languages:str|None=None) -> dict:
    """Create only lightweight per-language pointers, never touch 14 V5.7 DBs."""
    selected=_languages(languages)
    c=_load_contract(encyk_root,collection_dir)
    out=_safe_output(c['root'],c['collection']/'semantic-v58')
    bond=_bond_hash(c)
    if out.exists() and not out.is_dir():
        raise ValueError('Repertoire du pont occupe par un fichier')
    out.mkdir(parents=True,exist_ok=True)
    with _exclusive_lock(c['collection']):
        planned=[]
        # Preflight all 14 files before any write: keep customized files untouched.
        for lang in selected:
            local=c['collection']/(lang+'.sqlite3')
            _checked_file(local)
            with read_only_db(local) as db:
                if (_meta(db,'profile')!=LEX_PROFILE or _meta(db,'language')!=lang or
                    _meta(db,'source_fingerprint')!=c['collection_fp'] or _meta(db,'published')!='0' or
                    _meta(db,'status') not in ('COMPLETE','NO_DATA')):
                    raise ValueError('Dictionnaire V5.7 non complet ou incompatible: '+lang)
            data={'profile':BRIDGE_PROFILE,'language':lang,'bond':bond,
                  'reconciliation_db':str(c['reconciliation_db']),
                  'enrichment_db':str(c['enrichment_db']),
                  'index_fingerprint':c['index_fp'],
                  'collection_fingerprint':c['collection_fp'],
                  'status':'BOUND_CANDIDATES_ONLY','source_read_only':True,
                  'candidate_keys':c['languages'][lang]['candidate_keys'],
                  'sampled_source_anchors':c['languages'][lang]['sampled_source_anchors'],
                  'approved_sense_matches':0,'licensed_sources_approved':0,'may_be_published':False}
            dst=out/(lang+'.json')
            body=(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
            if dst.exists():
                _checked_file(dst)
                if dst.read_bytes() != body:
                    raise ValueError('Pont V5.8 modifie/incompatible: '+lang+'; rien a ecraser')
            planned.append((dst,body))
        for dst,body in planned:
            if not dst.exists():
                tmp=out/(dst.name+'.tmp.'+str(os.getpid()))
                try:
                    with tmp.open('xb') as stream:stream.write(body)
                    os.replace(tmp,dst)
                finally:tmp.unlink(missing_ok=True)
    return {'profile':BRIDGE_PROFILE,'status':'BOUND_CANDIDATES_ONLY',
            'languages_bound':len(selected),'network_used':False,'source_read_only':True,
            'V57_sqlite_modified':False,'approved_sense_matches':0,
            'published_dictionaries':0,
            'note':'Preuves v0.6 consultees a la demande depuis EncyK; pas de copie massive'}


def _candidate_id(lang: str, key: str) -> str:
    payload=json.dumps([lang,key],ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return 'lexcand-'+hashlib.sha256(payload).hexdigest()


def _candidate_id_real(lang: str,key: str) -> str:
    # EncyK v0.5 uses the hash prefix/format below; keep exact definition.
    return _candidate_id(lang,key)


def _glosses(record: object) -> list[str]:
    if not isinstance(record,dict):return []
    out=[]
    for sense in record.get('senses',[])[:4] if isinstance(record.get('senses'),list) else []:
        if not isinstance(sense,dict):continue
        for name in ('glosses','raw_glosses'):
            value=sense.get(name)
            if isinstance(value,list):
                out.extend(x[:280] for x in value[:3] if isinstance(x,str))
            elif isinstance(value,str):out.append(value[:280])
            if len(out)>=4:return out[:4]
    return out[:4]


def _external_senses(record: object) -> list[str]:
    if not isinstance(record,dict):return []
    senses=record.get('senses')
    if not isinstance(senses,list):return []
    ids=[]
    for sense in senses[:24]:
        if not isinstance(sense,dict):continue
        val=sense.get('sense_id')
        if isinstance(val,str) and re.fullmatch(r'L[1-9][0-9]*-S[1-9][0-9]*',val):
            ids.append(val)
        if len(ids)>=8:break
    return ids


def lookup(*, encyk_root:Path, collection_dir:Path, language:str, term:str,
           max_lexemes:int=10, max_evidence:int=8) -> dict:
    """On-demand candidate proof lookup, exact source anchor when available."""
    if language not in LANGUAGES or not term or len(term)>200 or not (1<=max_lexemes<=30) or not (1<=max_evidence<=50):
        raise ValueError('Code de langue, mot ou limites incorrects')
    c=_load_contract(encyk_root,collection_dir)
    binding=_json_read(_checked_file(c['collection']/'semantic-v58'/(language+'.json')))
    if binding.get('profile')!=BRIDGE_PROFILE or binding.get('bond')!=_bond_hash(c) or binding.get('may_be_published') is not False:
        raise ValueError('Pont V5.8 absent ou obsolete')
    with ExitStack() as stack:
        dic=stack.enter_context(read_only_db(c['collection']/(language+'.sqlite3')))
        rec=stack.enter_context(read_only_db(c['reconciliation_db']))
        ev=stack.enter_context(read_only_db(c['enrichment_db']))
        if _meta(dic,'status') not in ('COMPLETE','NO_DATA') or _meta(dic,'language')!=language:
            raise ValueError('Dictionnaire local V5.7 incomplet')
        terms=dic.execute('SELECT uid,lemma,pos,lemma_key FROM lexemes WHERE lemma=? ORDER BY pos LIMIT ?',
                           (term,max_lexemes)).fetchall()
        if not terms:
            terms=dic.execute('''SELECT DISTINCT l.uid,l.lemma,l.pos,l.lemma_key FROM observations o
                 JOIN lexemes l ON l.uid=o.uid WHERE o.form_surface=? ORDER BY l.lemma LIMIT ?''',
                 (term,max_lexemes)).fetchall()
        results=[]
        for uid,lemma,pos,key in terms:
            cid=_candidate_id_real(language,key)
            row=rec.execute('SELECT candidate_id,language,lemma_key FROM candidates WHERE candidate_id=?',
                            (cid,)).fetchone()
            if row is None or tuple(row)!=(cid,language,key):
                results.append({'lemma':lemma,'pos':pos,'candidate_evidence':[],
                                'evidence_status':'NO_CROSS_FAMILY_SAMPLE'})
                continue
            observed={(int(a),int(b)) for a,b in dic.execute('SELECT source_id,source_line FROM observations WHERE uid=?',(uid,))}
            local_sources={a:(b,c) for a,b,c in dic.execute('SELECT id,relative_path,kind FROM sources')}
            proofs=[]
            for sid,line,status,payload in ev.execute('''SELECT source_id,source_line,status,payload_json
                FROM evidence WHERE language=? AND candidate_id=?
                ORDER BY source_id,source_line LIMIT ?''',(language,cid,max_evidence)):
                try:doc=json.loads(payload)
                except (ValueError,TypeError):
                    raise ValueError('Preuve EncyK JSON invalide (aucune promotion)')
                if (not isinstance(doc,dict) or doc.get('candidate_id')!=cid or
                    doc.get('language')!=language or doc.get('source_id')!=sid or
                    doc.get('source_line')!=line or doc.get('sense_alignment_approved') is not False or
                    doc.get('license_reviewed') is not False):
                    raise ValueError('Preuve EncyK incoherente, refus')
                if status != doc.get('status') or sid not in local_sources or \
                    doc.get('source_relative_path') != local_sources[sid][0] or \
                    doc.get('family') != local_sources[sid][1]:
                    raise ValueError('Provenance de source EncyK incompatible (refus de preuve)')
                matched=(int(sid),int(line)) in observed
                record=doc.get('observed_record') if status=='observed' else None
                proofs.append({'source_id':sid,'source_line':line,'family':doc.get('family'),
                               'status':status,'anchor_matches_same_lexeme':matched,
                               'relationship':'SOURCE_ANCHORED_OBSERVATION' if matched else 'HOMOGRAPH_KEY_ONLY',
                               'gloss_candidates':_glosses(record),
                               'external_wikidata_sense_ids':_external_senses(record),
                               'sense_alignment_approved':False,'license_reviewed':False})
            results.append({'lemma':lemma,'pos':pos,'candidate_evidence':proofs,
                            'evidence_status':'UNREVIEWED_HOMOGRAPH_CANDIDATE',
                            'sense_alignment_approved':False})
    return {'profile':BRIDGE_PROFILE,'language':language,'query':term,
            'results':results,'published':False,'approved_semantic_equivalences':0,
            'warning':'Sources et sens candidats seulement; aucune equivalence KQ/KP automatique'}


def export_summary(*, encyk_root:Path, collection_dir:Path, output_zip:Path) -> dict:
    c=_load_contract(encyk_root,collection_dir)
    out=c['collection']/'semantic-v58'
    report={}
    for lang in LANGUAGES:
        path=_checked_file(out/(lang+'.json'))
        doc=_json_read(path)
        if (doc.get('profile')!=BRIDGE_PROFILE or doc.get('language')!=lang or
            doc.get('bond')!=_bond_hash(c) or doc.get('may_be_published') is not False):
            raise ValueError('Lien V5.8 altere/absent: '+lang)
        report[lang]={'candidate_keys':int(doc['candidate_keys']),
                      'sampled_source_anchors':int(doc['sampled_source_anchors']),
                      'lexical_observations':int(c['languages'][lang]['lexical_observations']),
                      'review_tiers':c['languages'][lang]['review_tiers'],
                      'status':'BOUND_CANDIDATES_ONLY'}
    body={'profile':REPORT_PROFILE,'generated_at':_now(),
          'status':'BOUND_CANDIDATES_ONLY','languages':report,'source_read_only':True,
          'v57_sqlite_unchanged':True,'network_used':False,
          'licences_approved':0,'approved_semantic_equivalences':0,'published_dictionaries':0,
          'limitations':['v06_sampled_not_exhaustive','candidate_homographs_not_senses',
                         'licences_not_reviewed','no_kq_kp_automatic_promotion',
                         'no_14_dictionaries_declared_published']}
    b=(json.dumps(body,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    stream=io.StringIO(newline='')
    writer=csv.writer(stream)
    writer.writerow(['language','candidate_keys','sampled_source_anchors','lexical_observations'])
    for lang,entry in report.items():
        writer.writerow([lang,entry['candidate_keys'],entry['sampled_source_anchors'],entry['lexical_observations']])
    data=stream.getvalue().encode('utf-8-sig')
    hashes=(json.dumps({'summary.json':hashlib.sha256(b).hexdigest(),
                         'langues.csv':hashlib.sha256(data).hexdigest()},indent=2)+'\n').encode('utf-8')
    output_zip=Path(output_zip).absolute()
    if output_zip.suffix.lower()!='.zip' or output_zip.exists() or output_zip.is_symlink():
        raise ValueError('ZIP de bilan attendu, fichier deja present refuse')
    if output_zip.is_relative_to(c['root']) or output_zip.is_relative_to(c['collection']):
        raise ValueError('Rapport hors des dossiers de donnees obligatoire')
    output_zip.parent.mkdir(parents=True,exist_ok=True)
    tmp=output_zip.with_name(output_zip.name+'.partial.'+str(os.getpid()))
    try:
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('summary.json',b)
            z.writestr('langues.csv',data)
            z.writestr('SHA256_EXPORT.json',hashes)
        if tmp.stat().st_size>1_048_576:
            raise ValueError('ZIP de bilan depasse 1 Mio')
        os.replace(tmp,output_zip)
    finally:tmp.unlink(missing_ok=True)
    return {'status':'EXPORTED','zip':str(output_zip),'size_bytes':output_zip.stat().st_size,
            'languages':14,'contains_lexical_words':False,'contains_local_paths':False}
