"""Deterministic reversible reading projections of Kristal v11 graphs.

Canonical graph is *embedded*, unmodified. Human/LLM friendly labels are ONLY
annotations, never semantic identities. Restoring is a structural decoding, not
lexical reverse matching. No network calls or destructive writes.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from . import FRAMEWORK_CONTRACT
from ._framework import coverage as cov
from ._framework import dictionaries as ref
from .operations import DiKError, Project

PROFILE = 'dik.reversible-projection/1.0'


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _collect_lexical_index(catalog_path: Path, locale: str, wanted: set[str]) -> dict[str, dict]:
    """One pass per layer, not one file scan per KQ/KP; respect explicit fallbacks."""
    catalog = ref.read_json(catalog_path)
    languages = {lang['tag']: lang for lang in catalog['languages']}
    if locale not in languages:
        raise DiKError(f'Langue non déclarée dans le catalogue: {locale}')
    search = [locale] + languages[locale]['fallbacks']
    snapshots: dict[str, dict] = {}
    base = catalog_path.resolve().parent
    for tag in search:
        selected: dict[str, tuple[int, str, str]] = {}
        for layer in languages[tag]['layers']:
            file = ref.safe_file(base, layer['path'])
            for entry, _ in ref.layer_records(file, layer['kind']):
                sem_id = entry['semantic_id']
                if sem_id not in wanted:
                    continue
                candidate = (layer['priority'], entry['preferred_term'], layer['layer_id'])
                old = selected.get(sem_id)
                if old is None or candidate[0] > old[0]:
                    selected[sem_id] = candidate
                elif candidate[0] == old[0] and candidate[1] != old[1]:
                    raise DiKError(f'Conflit de libellés au même rang: {tag}/{sem_id}')
        snapshots[tag] = selected
    resolved = {}
    for sem_id in sorted(wanted):
        for tag in search:
            entry = snapshots[tag].get(sem_id)
            if entry is not None:
                resolved[sem_id] = {
                    'id': sem_id, 'label': entry[1],
                    'status': 'direct' if tag == locale else 'fallback',
                    'effective_locale': tag, 'layer_id': entry[2],
                }
                break
        else:
            resolved[sem_id] = {'id':sem_id, 'label':None, 'status':'missing'}
    return resolved


def _readable(graph: dict, dictionary: dict[str, dict], locale: str) -> dict:
    """All semantic positions contain their IDs, including qualifier properties."""
    def label(sem_id: str) -> dict:
        return copy.deepcopy(dictionary[sem_id])

    def annotated_object(obj: dict) -> dict:
        if obj['kind'] == 'entity':
            return {'kind':'entity', 'reference':label(obj['id'])}
        return copy.deepcopy(obj)  # literals are *data*; never lexicalize or reinterpret

    statements = []
    for stmt in graph['assertions']:
        rendered = {
            'assertion_id': stmt['id'],
            'subject': label(stmt['subject']),
            'predicate': label(stmt['predicate']),
            'object': annotated_object(stmt['object']),
            'sources': list(stmt['sources']),
        }
        if 'qualifiers' in stmt:
            rendered['qualifiers'] = [
                {'predicate': label(q['predicate']), 'object': annotated_object(q['object'])}
                for q in stmt['qualifiers']
            ]
        statements.append(rendered)
    status = {'direct':0, 'fallback':0, 'missing':0}
    for record in dictionary.values():
        status[record['status']] += 1
    return {
        'requested_locale':locale,
        'entities':[label(i) for i in graph['entities']],
        'properties':[label(i) for i in graph['properties']],
        'statements':statements,
        'coverage_counts':status,
        'complete_direct':status['fallback'] == status['missing'] == 0,
        'complete_usable':status['missing'] == 0,
    }


def project_graph(project: Project, locale: str) -> dict:
    ref.audit(project.catalog, project.crosswalk, project.registry)
    graph = ref.read_json(project.graph)
    registry = ref.read_json(project.registry)
    catalog = ref.read_json(project.catalog)
    ids = cov._references(graph, registry)
    if catalog['namespace_id'] != graph['namespace_id']:
        raise DiKError('Namespace catalogue/graphe différent')
    wanted = ids['KQ'] | ids['KP']
    index = _collect_lexical_index(project.catalog, locale, wanted)
    readable = _readable(graph, index, locale)
    anchors = {
        'framework_contract':FRAMEWORK_CONTRACT,
        'namespace_id':graph['namespace_id'],
        'graph_id':graph['graph_id'],
        'source_sha256':{
            'graph':ref.sha256(project.graph),
            'catalog':ref.sha256(project.catalog),
            'registry':ref.sha256(project.registry),
            'crosswalk':ref.sha256(project.crosswalk),
        },
    }
    core = copy.deepcopy(graph)
    return {
        'projection_format':PROFILE,
        'derived_only':True,
        'anchors':anchors,
        'canonical_graph':core,
        'readable':readable,
        'digests':{
            'canonical_graph':digest(core),
            'readable':digest(readable),
            'anchors':digest(anchors),
        },
        'limits': 'La lecture linguistique ne fait pas autorité. Pour modifier le sens, utiliser une migration sémantique révisée, pas des changements de libellés.',
    }


def restore_projection(envelope: dict, project: Project | None = None) -> dict:
    """Restore pure graph. Never infer KQ/KP from words.

    With an original project, also authenticate consistency with *current pinned
    project files* and regenerate the reading view. Without it, hashes are only
    checksums against accidental damage, not signatures against a hostile editor.
    """
    from .compact import COMPACT_PROFILE, restore_compact
    if isinstance(envelope, dict) and envelope.get('projection_format') == COMPACT_PROFILE:
        return restore_compact(envelope, project)
    if not isinstance(envelope,dict) or set(envelope) != {
        'projection_format','derived_only','anchors','canonical_graph','readable','digests','limits'
    } or envelope['projection_format'] != PROFILE or envelope['derived_only'] is not True:
        raise DiKError('Enveloppe de projection diK non reconnue')
    anchors = envelope['anchors']
    if not isinstance(anchors,dict) or anchors.get('framework_contract') != FRAMEWORK_CONTRACT:
        raise DiKError('Contrat Framework non supporté')
    hashes = envelope['digests']
    if not isinstance(hashes,dict) or set(hashes) != {'canonical_graph','readable','anchors'}:
        raise DiKError('Empreintes de projection invalides')
    for key, obj in [('canonical_graph',envelope['canonical_graph']),
                     ('readable',envelope['readable']),('anchors',anchors)]:
        if hashes[key] != digest(obj):
            raise DiKError(f'Projection modifiée ou altérée ({key}); pas de restauration implicite')
    graph = envelope['canonical_graph']
    ref.check_schema(graph,'kristal-semantic-graph.schema.json')
    if graph['namespace_id'] != anchors['namespace_id'] or graph['graph_id'] != anchors['graph_id']:
        raise DiKError('Identité du graphe incohérente')
    # Independent check: every ID in the view must be associated with the same ID
    # in canonical content. No word-to-ID guessing or silent edited view acceptance.
    view = envelope['readable']
    if not isinstance(view,dict) or set(view) != {
        'requested_locale','entities','properties','statements','coverage_counts',
        'complete_direct','complete_usable'
    }:
        raise DiKError('Projection linguistique malformée')
    if [x.get('id') for x in view['entities']] != graph['entities']:
        raise DiKError('Références KQ divergentes dans la projection')
    if [x.get('id') for x in view['properties']] != graph['properties']:
        raise DiKError('Références KP divergentes dans la projection')
    if len(view['statements']) != len(graph['assertions']):
        raise DiKError('Assertions manquantes dans la projection')
    for displayed, stmt in zip(view['statements'],graph['assertions']):
        if (displayed.get('assertion_id') != stmt['id'] or
            displayed.get('subject',{}).get('id') != stmt['subject'] or
            displayed.get('predicate',{}).get('id') != stmt['predicate'] or
            displayed.get('sources') != stmt['sources']):
            raise DiKError(f'Références de l’assertion divergentes: {stmt["id"]}')
        shown_obj = displayed.get('object',{})
        if stmt['object']['kind'] == 'entity':
            if shown_obj.get('kind') != 'entity' or shown_obj.get('reference',{}).get('id') != stmt['object']['id']:
                raise DiKError('Objet KQ divergent dans la projection')
        elif shown_obj != stmt['object']:
            raise DiKError('Valeur littérale divergente dans la projection')
        expected_quals = stmt.get('qualifiers', [])
        shown_quals = displayed.get('qualifiers', [])
        if len(expected_quals) != len(shown_quals):
            raise DiKError('Qualificatifs divergents dans la projection')
        for got, q in zip(shown_quals,expected_quals):
            if got.get('predicate',{}).get('id') != q['predicate']:
                raise DiKError('Identifiant KP de qualificatif divergent')
            obj = got.get('object',{})
            if q['object']['kind'] == 'entity':
                if obj.get('kind') != 'entity' or obj.get('reference',{}).get('id') != q['object']['id']:
                    raise DiKError('Objet KQ de qualificatif divergent')
            elif obj != q['object']:
                raise DiKError('Littéral de qualificatif divergent')
    if project is not None:
        # Detect replaced source/dictionaries and cosmetic edits even if a
        # caller recomputed the unsecured JSON checksums.
        true_anchors = {
            'graph':ref.sha256(project.graph), 'catalog':ref.sha256(project.catalog),
            'registry':ref.sha256(project.registry), 'crosswalk':ref.sha256(project.crosswalk),
        }
        if anchors.get('source_sha256') != true_anchors:
            raise DiKError('Sources/version du dictionnaire modifiées depuis la projection')
        regenerated = project_graph(project,view['requested_locale'])
        if envelope != regenerated:
            raise DiKError('Projection différente de celle vérifiée à partir des sources')
    return copy.deepcopy(graph)


def _markdown_ref(refitem: dict, style: str = "annotated") -> str:
    label = refitem.get('label')
    ident = refitem['id']
    # Escape pipes/newlines for simple markdown; retain anchor in inline code.
    text = str(label).replace('\\','\\\\').replace('|','\\|').replace('\n',' ') if label else f'[{ident}: non traduit]'
    return text if style == 'clean' else f'{text} (`{ident}`)'


def readable_markdown(envelope: dict, style: str = "annotated") -> str:
    from .compact import COMPACT_PROFILE, compact_markdown
    if isinstance(envelope, dict) and envelope.get('projection_format') == COMPACT_PROFILE:
        return compact_markdown(envelope, style)
    if style not in ('annotated','clean'):
        raise DiKError('Style de lecture invalide')
    view = envelope['readable']
    anchor = envelope['anchors']
    lines = [f'# Kristal {anchor["graph_id"]} — {view["requested_locale"]}', '',
             '> Projection de lecture dérivée, non canonique. Conserver le JSON diK pour une reconversion exacte.',
             '', '| Assertion | Sujet | Propriété | Objet | Sources |',
             '|---|---|---|---|---|']
    for stmt in view['statements']:
        obj = stmt['object']
        thing = (_markdown_ref(obj['reference'],style) if obj['kind']=='entity'
                 else f'{json.dumps(obj["value"],ensure_ascii=False)} ({obj["datatype"]})')
        lines.append('| '+' | '.join((f'`{stmt["assertion_id"]}`' if style == 'annotated' else '—',
             _markdown_ref(stmt['subject'],style), _markdown_ref(stmt['predicate'],style),
             thing.replace('|','\\|'), ', '.join('`'+s+'`' for s in stmt['sources']) if style == 'annotated' else str(len(stmt['sources']))+' source(s)'))+' |')
        for q in stmt.get('qualifiers',[]):
            qobj = q['object']
            qt = (_markdown_ref(qobj['reference'],style) if qobj['kind']=='entity'
                  else json.dumps(qobj['value'],ensure_ascii=False))
            lines.append(f'\n  - Qualificatif : {_markdown_ref(q["predicate"],style)} → {qt}')
    counts = view['coverage_counts']
    lines += ['',f'Couverture des références KQ/KP : {counts["direct"]} directes, '
              f'{counts["fallback"]} par repli, {counts["missing"]} manquantes.',
              '', 'Le texte seul ne permet **pas** une reconversion fiable. Utiliser le JSON de projection avec empreintes (non signé).']
    return '\n'.join(lines)+'\n'
