"""Explicit private CLI; no production integration."""
import argparse,importlib.util
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--framework',required=True,type=Path);p.add_argument('--generation',required=True,type=Path);p.add_argument('--report-sha256',required=True);p.add_argument('--purpose',choices=('active-only','private-review'),default='active-only');sp=p.add_subparsers(dest='layer',required=True)
    for name,fields in [('active-graph',('namespace',)),('active-assertion',('namespace','semantic_id')),('active',('namespace','semantic_id')),('candidate',('namespace','semantic_id')),('structured',('slug','occurrence_id')),('native-artifact',('slug','path')),('native-record',('slug','path','collection','native_id'))]:
        q=sp.add_parser(name)
        for key in fields:q.add_argument(key)
        if name=='native-artifact':q.add_argument('--pointer')
        q.set_defaults(fields=fields)
    a=p.parse_args();s=importlib.util.spec_from_file_location('kristal_operational_cli',a.framework/'tools/v11/operational_native_v5216.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.Reader(a.generation,a.report_sha256,a.purpose);args=[getattr(a,key) for key in a.fields]
    if a.layer=='native-artifact':args.append(a.pointer)
    result=r.active_graph(*args) if a.layer=='active-graph' else r.active_assertion(*args) if a.layer=='active-assertion' else r.read(a.layer,*args)
    print(m.f.encode(result))
if __name__=='__main__':main()
