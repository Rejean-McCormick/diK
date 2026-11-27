"""Read local operational labels and selected assertions; no canon or network writes."""
import argparse,hashlib,json,sqlite3
from pathlib import Path,PurePosixPath
from contextlib import closing

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(x,m):
    if not x:raise ValueError(m)
class Reader:
    def __init__(self,run,baseline):
        self.run=Path(run);self.base=Path(baseline);p=self.run/'repair.sqlite';r=json.loads((self.run/'report.json').read_bytes());d=json.loads((self.run/'diagnostic.json').read_bytes())
        need(d['status']=='PASS_PRIVATE_OPERATIONAL_SCOPE' and (self.run/'COMPLETE').read_text()==r['database_sha256']==d['database_sha256']==sha(p),'Unverified repair receipt')
        need(sha(self.base/'active.sqlite')==r['baseline_sha256'],'Baseline drift')
        self.c=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)
        self.b=sqlite3.connect((self.base/'active.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
    def close(self):self.c.close();self.b.close()
    def label(self,ns,sid,lang,canonical_only=False):
        row=self.c.execute('SELECT term,status FROM effective WHERE ns=? AND sid=? AND lang=?',(ns,sid,lang)).fetchone()
        if row and (not canonical_only or row[1]=='ACTIVE_CANONICAL'):return {'status':row[1],'text':row[0],'language':lang,'is_label':True,'canonical':row[1]=='ACTIVE_CANONICAL'}
        ref=self.c.execute('SELECT native_json FROM display_ref WHERE ns=? AND sid=?',(ns,sid)).fetchone()
        if not ref:return {'status':'IDENTITY_NOT_FOUND'}
        if canonical_only:return {'status':'MISSING_CANONICAL_LABEL'}
        # Explicitly no inferred language or manufactured lexical entry.
        names=json.loads(ref[0]);return {'status':'NATIVE_IDENTIFIER_FALLBACK' if len(names)==1 else 'SEMANTIC_IDENTIFIER_FALLBACK','text':names[0] if len(names)==1 else sid,'language':None,'is_label':False,'canonical':False,'available_languages':[r[0] for r in self.c.execute('SELECT lang FROM effective WHERE ns=? AND sid=? ORDER BY lang',(ns,sid))]}
    def assertion(self,ns,sid,canonical_only=False):
        row=self.b.execute('SELECT slug,json_pointer FROM v52161_active_assertion WHERE namespace_id=? AND semantic_id=?',(ns,sid)).fetchone()
        if not row:return {'status':'ASSERTION_NOT_SELECTED'}
        slug,pointer=row;status,rj=self.c.execute('SELECT status,record_json FROM graph_scope WHERE slug=? AND ns=?',(slug,ns)).fetchone();g=json.loads(rj)
        if canonical_only and status!='QUALIFIED_ACTIVE_GRAPH':return {'status':'LEXICALLY_BLOCKED'}
        rel=PurePosixPath(g['graph_path']);need(not rel.is_absolute() and '..' not in rel.parts and '\\' not in str(rel) and ':' not in str(rel),'Unsafe graph path');path=self.base.joinpath(*rel.parts);need(sha(path)==g['graph_sha256'],'Graph drift');data=json.loads(path.read_bytes());
        for x in pointer.split('/')[1:]:data=data[int(x)] if isinstance(data,list) else data[x]
        need(data.get('id')==sid,'Assertion pointer mismatch')
        return {'status':status,'assertion':data,'canonical_lexical_qualified':status=='QUALIFIED_ACTIVE_GRAPH'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--baseline',required=True);p.add_argument('--namespace',required=True);p.add_argument('--id',required=True);p.add_argument('--language',default='fr');p.add_argument('--assertion',action='store_true');p.add_argument('--canonical-only',action='store_true');a=p.parse_args();r=Reader(a.run,a.baseline)
    try:print(json.dumps(r.assertion(a.namespace,a.id,a.canonical_only) if a.assertion else r.label(a.namespace,a.id,a.language,a.canonical_only),ensure_ascii=False,indent=2))
    finally:r.close()
