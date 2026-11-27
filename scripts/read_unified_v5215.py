"""Explicit opt-in private reader; does not replace diK's production path."""
import argparse,importlib.util
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--framework',required=True,type=Path);p.add_argument('--generation',required=True,type=Path);p.add_argument('--report-sha256',required=True);sp=p.add_subparsers(dest='layer',required=True)
    for name,fields in [('active',('namespace','semantic_id')),('candidate',('namespace','semantic_id')),('structured',('slug','occurrence_id')),('native-artifact',('slug','path')),('native-record',('slug','path','collection','native_id'))]:
        q=sp.add_parser(name)
        for key in fields:q.add_argument(key)
        if name=='native-artifact':q.add_argument('--pointer')
        q.set_defaults(fields=fields)
    a=p.parse_args();path=a.framework/'tools/v11/unified_native_v5215.py';s=importlib.util.spec_from_file_location('kristal_unified_reader_cli',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.Reader(a.generation,a.report_sha256);args=[getattr(a,key) for key in a.fields]
    if a.layer=='native-artifact':args.append(a.pointer)
    method={'active':r.active,'candidate':r.candidate,'structured':r.structured,'native-artifact':r.artifact,'native-record':r.native_record}[a.layer];print(m.f.encode(method(*args)))
if __name__=='__main__':main()
