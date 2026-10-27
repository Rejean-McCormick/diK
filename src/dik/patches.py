"""Patch intent candidates. diK cannot commit canonical semantic edits."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator
from .operations import DiKError
from .legacy import pointer_value
from ._framework import dictionaries as fw

SCHEMA=Path(__file__).with_name('contracts')/'dik-semantic-patch-intent.schema.json'


def inspect_patch(intent:dict, graph_path:Path) -> dict:
    errs=list(Draft202012Validator(json.loads(SCHEMA.read_text(encoding='utf-8'))).iter_errors(intent))
    if errs: raise DiKError('Patch schema invalid: '+errs[0].message)
    graph=fw.read_json(graph_path)
    if intent['source_graph_sha256']!=fw.sha256(graph_path) or intent['source_graph_id']!=graph['graph_id'] or intent['namespace_id']!=graph['namespace_id']:
        raise DiKError('STALE_SOURCE')
    if pointer_value(graph,intent['source_path'])!=intent['original']:
        raise DiKError('Patch original value differs from graph')
    return {'patch_id':intent['patch_id'],'validated':True,'review_status':intent['review_status'],
            'mutation_permitted_by_dik':False,
            'target':'lexical-curation' if intent['change_kind']=='lexical_only' else 'authorized-producer'}
