"""Explicit opt-in diagnostic reader, not the existing diK production query path."""
import argparse,importlib.util,json
from pathlib import Path

def read(framework,generation,slug,occurrence,expected_report_sha256):
    spec=importlib.util.spec_from_file_location('kristal_structured_framework_v5214',Path(framework)/'tools/v11/structured_native_v5214.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
    root=Path(generation);report_raw=f.safe(root,'report.json').read_bytes();f.require(f.sha(report_raw)==expected_report_sha256,'Report SHA-256 mismatch');r=json.loads(report_raw);f.require(r['status']=='STRUCTURED_REPRESENTATION_DRAFT_VALIDATED_MIGRATION_PENDING','Unsupported generation');entry=next((x for x in r['packets'] if x['slug']==slug),None);f.require(entry is not None,'Unknown slug');packet_root=f.safe(root,'structured/'+slug);raw=f.safe(packet_root,'packet.json').read_bytes();f.require(f.sha(raw)==entry['packet_sha256'],'Packet digest mismatch');packet=json.loads(raw);f.require(packet['slug']==slug,'Packet scope mismatch');return f.encode(f.read_occurrence(packet_root,packet,occurrence))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--framework',required=True,type=Path);p.add_argument('--generation',required=True,type=Path);p.add_argument('--slug',required=True);p.add_argument('--occurrence',required=True);p.add_argument('--report-sha256',required=True);a=p.parse_args();print(read(a.framework,a.generation,a.slug,a.occurrence,a.report_sha256))
