"""Read exact active or private recovery labels, without modifying either index."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
from contextlib import closing

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def lookup(base,scan,ns,sid,lang,private_review=False):
    base,scan=Path(base),Path(scan)
    report=json.loads((scan/'report.json').read_bytes());diag=json.loads((scan/'diagnostic.json').read_bytes())
    if not (scan/'COMPLETE').is_file() or diag.get('status')!='PASS_PRIVATE_RECEIPT_SCOPE' or not diag.get('source_bytes_and_pointers_checked'):raise ValueError('Unqualified maintenance receipt')
    src=base/'active.sqlite';dbp=scan/'maintenance.sqlite'
    if sha(src)!=report['base_database_sha256'] or sha(dbp)!=report['maintenance_database_sha256'] or diag.get('database_sha256')!=report['maintenance_database_sha256']:raise ValueError('Database digest mismatch')
    with closing(sqlite3.connect(src.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        if not db.execute('SELECT 1 FROM identity WHERE namespace_id=? AND semantic_id=? AND kind IN (\'entity\',\'property\')',(ns,sid)).fetchone():return {'status':'IDENTITY_NOT_FOUND'}
        row=db.execute('SELECT preferred_term FROM lexical WHERE namespace_id=? AND semantic_id=? AND language_tag=?',(ns,sid,lang)).fetchone()
        if row:return {'status':'ACTIVE_CANONICAL','term':row[0],'language':lang}
    if not private_review:return {'status':'MISSING_ACTIVE_LABEL'}
    with closing(sqlite3.connect(dbp.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        row=db.execute('SELECT status,term,variants_json FROM resolution WHERE ns=? AND sid=? AND lang=?',(ns,sid,lang)).fetchone()
        if not row:return {'status':'NO_EXACT_RECOVERY'}
        return {'status':row[0],'term':row[1],'language':lang,'variants':json.loads(row[2]),'canonical':False,'evidence':[dict(zip(('native_id','path','sha256','pointer','method'),r)) for r in db.execute('SELECT native_id,path,sha256,pointer,method FROM observation WHERE ns=? AND sid=? AND lang=?',(ns,sid,lang))]}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--scan',required=True);p.add_argument('--namespace',required=True);p.add_argument('--id',required=True);p.add_argument('--language',required=True);p.add_argument('--private-review',action='store_true');a=p.parse_args();print(json.dumps(lookup(a.baseline,a.scan,a.namespace,a.id,a.language,a.private_review),ensure_ascii=True,indent=2))
