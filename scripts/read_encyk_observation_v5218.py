"""Read an external lexical observation, never a canonical label or accepted link."""
import argparse,hashlib,json,sqlite3
from pathlib import Path
from contextlib import closing

def read(out,wid,lang):
    out=Path(out);p=out/'indexed.sqlite';r=json.loads((out/'report.json').read_bytes());d=json.loads((out/'diagnostic.json').read_bytes())
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    if h!=r['database_sha256'] or h!=d['database_sha256'] or h!=(out/'COMPLETE').read_text() or d['status']!='PASS_INDEXED_PRIVATE_SCOPE':raise ValueError('Invalid receipt')
    result={'external_id':wid,'language':lang,'scope':'private-observation','canonical':False,'source_authenticated':False,'label':None,'aliases':None,'revision':None,'status':'NO_EXACT_OBSERVATION'}
    if lang=='und':result['status']='UNDETERMINED_LANGUAGE';return result
    with closing(sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)) as c:
        row=c.execute('SELECT record_json FROM indexed_entity WHERE wid=?',(wid,)).fetchone()
        if row:
            d=json.loads(row[0]);result.update(label=(d['labels'] or {}).get(lang),aliases=(d['aliases'] or {}).get(lang),revision=d['revision'],status='INDEXED_DUMP_OBSERVATION')
        else:
            row=c.execute('SELECT record_json FROM compact_entity WHERE wid=?',(wid,)).fetchone()
            if row and lang in ('fr','en'):result.update(label=json.loads(row[0]).get('label_'+lang),status='COMPACT_LABEL_REVISION_UNKNOWN')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--wid',required=True);p.add_argument('--lang',required=True);a=p.parse_args();print(json.dumps(read(a.output,a.wid,a.lang),ensure_ascii=True,indent=2))
