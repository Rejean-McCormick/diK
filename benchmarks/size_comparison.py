"""Reproducible synthetic JSON-size comparison; not a production benchmark.

Run: PYTHONPATH=src python benchmarks/size_comparison.py
"""
import copy
import json
from pathlib import Path

from dik.compact import project_compact
from dik.operations import load_project
from dik.projection import project_graph

root = Path(__file__).resolve().parents[1]
project = load_project(root/'examples/demo/dik.project.json')
verbose = project_graph(project, 'fr')
compact = project_compact(project, 'fr')
print('statements,verbose_bytes,compact_bytes,savings_percent')
for n in (1, 100, 1000, 5000):
    a = copy.deepcopy(verbose)
    b = copy.deepcopy(compact)
    stmt = a['canonical_graph']['assertions'][0]
    view = a['readable']['statements'][0]
    data = [dict(stmt, id=f'KA{3001+i}') for i in range(n)]
    a['canonical_graph']['assertions'] = data
    a['readable']['statements'] = [dict(view, assertion_id=f'KA{3001+i}') for i in range(n)]
    b['canonical_graph']['assertions'] = data
    def byte_len(obj):
        return len(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                              separators=(',', ':')).encode('utf-8'))
    old, new = byte_len(a), byte_len(b)
    print(f'{n},{old},{new},{(1-new/old)*100:.1f}')
