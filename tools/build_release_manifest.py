"""Rebuild or verify diK release integrity manifests reproducibly.

Two-file layering avoids a self-hash cycle. Source code and documentation are
covered, not generated caches or Git internals.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
OMIT_DIRS={'.git','.pytest_cache','__pycache__','build','dist','.venv','.mypy_cache'}
OMIT_FILES={'RELEASE-SHA256.json','RELEASE_MANIFEST_SHA256.json'}

def all_files():
    return sorted((p for p in ROOT.rglob('*') if p.is_file() and not any(
        part in OMIT_DIRS or part.endswith('.egg-info') for part in p.relative_to(ROOT).parts)),
        key=lambda p:p.relative_to(ROOT).as_posix())

def json_str(obj):return json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n'

def manifests():
    files=all_files()
    first={'release':'1.0.0-alpha.7','framework_contract':'11.0.0-draft.3',
           'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in files if p.name not in OMIT_FILES]}
    first_bytes=json_str(first).encode('utf-8')
    second={'version':'1.0.0-alpha.7',
            'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in files if p.name not in OMIT_FILES}}
    second['files']['RELEASE-SHA256.json']=hashlib.sha256(first_bytes).hexdigest()
    return first_bytes, json_str(second).encode('utf-8')

if __name__=='__main__':
    b1,b2=manifests()
    paths=(ROOT/'RELEASE-SHA256.json',ROOT/'RELEASE_MANIFEST_SHA256.json')
    if len(sys.argv)>1 and sys.argv[1]=='--verify':
        assert paths[0].read_bytes()==b1,'RELEASE-SHA256 differs from source files'
        assert paths[1].read_bytes()==b2,'RELEASE_MANIFEST_SHA256 differs from source files'
        print('Release manifests verified')
    else:
        paths[0].write_bytes(b1);paths[1].write_bytes(b2)
        print('Release manifests regenerated')
