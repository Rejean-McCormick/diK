"""Compact reversible linguistic overlay for Kristal graphs (diK 0.3).

The *only* semantic content is canonical_graph. A single immutable-view lexicon
is keyed by KQ/KP IDs; no lexical text is ever used to recover an identity.
The compact envelope is an app-level diK contract, not yet a Framework schema.
"""
from __future__ import annotations

import copy
import html
import json
from pathlib import Path

from . import FRAMEWORK_CONTRACT
from ._framework import coverage as cov
from ._framework import dictionaries as ref
from .operations import DiKError, Project
from .projection import _collect_lexical_index, digest

COMPACT_PROFILE = 'dik.compact-projection/1.0'
LIMITS = ('Vue derivee, sans autorite semantique. Les libelles ne creent ni '
          'identites ni modifications du graphe; ne pas restaurer depuis du texte libre.')


def _counts(entries: dict) -> dict[str, int]:
    counts = {'direct': 0, 'fallback': 0, 'missing': 0}
    for entry in entries.values():
        status = entry.get('status') if isinstance(entry, dict) else None
        if status not in counts:
            raise DiKError('Statut lexical non reconnu')
        counts[status] += 1
    return counts


def project_compact(project: Project, locale: str) -> dict:
    """One canonical graph and one de-duplicated vocabulary for one locale."""
    ref.audit(project.catalog, project.crosswalk, project.registry)
    graph = ref.read_json(project.graph)
    registry = ref.read_json(project.registry)
    catalog = ref.read_json(project.catalog)
    references = cov._references(graph, registry)
    if catalog['namespace_id'] != graph['namespace_id']:
        raise DiKError('Namespace catalogue/graphe different')
    wanted = references['KQ'] | references['KP']
    lookup = _collect_lexical_index(project.catalog, locale, wanted)
    # The ID is the object key, not duplicated in every lexical entry/statement.
    entries = {sem_id: {k: v for k, v in lookup[sem_id].items() if k != 'id'}
               for sem_id in sorted(lookup)}
    counts = _counts(entries)
    lexicon = {
        'requested_locale': locale,
        'entries': entries,
        'coverage_counts': counts,
        'complete_direct': counts['fallback'] == counts['missing'] == 0,
        'complete_usable': counts['missing'] == 0,
    }
    anchors = {
        'framework_contract': FRAMEWORK_CONTRACT,
        'namespace_id': graph['namespace_id'],
        'graph_id': graph['graph_id'],
        'source_sha256': {
            'graph': ref.sha256(project.graph),
            'catalog': ref.sha256(project.catalog),
            'registry': ref.sha256(project.registry),
            'crosswalk': ref.sha256(project.crosswalk),
        },
    }
    return {
        'projection_format': COMPACT_PROFILE,
        'derived_only': True,
        'anchors': anchors,
        'canonical_graph': graph,
        'lexicon': lexicon,
        'digests': {
            'canonical_graph': digest(graph),
            'lexicon': digest(lexicon),
            'anchors': digest(anchors),
        },
        'limits': LIMITS,
    }


def _check_consistency(graph: dict, lexicon: dict) -> None:
    """Independent structural checks; no trust in a derived lexical field."""
    if not isinstance(lexicon, dict) or set(lexicon) != {
        'requested_locale', 'entries', 'coverage_counts', 'complete_direct', 'complete_usable'
    }:
        raise DiKError('Structure du lexique compact invalide')
    if not isinstance(lexicon['requested_locale'], str) or not lexicon['requested_locale']:
        raise DiKError('Langue invalide')
    expected_entities = set(graph['entities'])
    expected_properties = set(graph['properties'])
    if len(graph['entities']) != len(expected_entities) or len(graph['properties']) != len(expected_properties):
        raise DiKError('Identifiants canoniques dupliques')
    wanted = expected_entities | expected_properties
    entries = lexicon['entries']
    if not isinstance(entries, dict) or set(entries) != wanted:
        raise DiKError('Lexique compact: identifiants manquants ou inconnus')
    for sem_id, info in entries.items():
        if not isinstance(info, dict):
            raise DiKError(f'Libelle malforme: {sem_id}')
        status = info.get('status')
        if status == 'missing':
            if set(info) != {'label', 'status'} or info['label'] is not None:
                raise DiKError('Un libelle absent doit rester null, sans identite inventee')
        elif status in ('direct', 'fallback'):
            if set(info) != {'label', 'status', 'effective_locale', 'layer_id'}:
                raise DiKError('Provenance lexicale incomplete')
            if not all(isinstance(info[k], str) and info[k] for k in ('label','effective_locale','layer_id')):
                raise DiKError('Libelle ou provenance vides')
            if (status == 'direct') != (info['effective_locale'] == lexicon['requested_locale']):
                raise DiKError('Statut de traduction incoherent avec la langue effective')
        else:
            raise DiKError(f'Statut lexical invalide: {status}')
    counts = _counts(entries)
    if counts != lexicon['coverage_counts']:
        raise DiKError('Comptes de couverture incoherents')
    if lexicon['complete_direct'] is not (counts['fallback'] == counts['missing'] == 0):
        raise DiKError('Completude directe incorrecte')
    if lexicon['complete_usable'] is not (counts['missing'] == 0):
        raise DiKError('Completude utilisable incorrecte')
    source_ids = set(graph['sources'])
    assertion_ids: set[str] = set()
    for stmt in graph['assertions']:
        if stmt['id'] in assertion_ids:
            raise DiKError('Assertion canonique dupliquee')
        assertion_ids.add(stmt['id'])
        if stmt['subject'] not in expected_entities or stmt['predicate'] not in expected_properties:
            raise DiKError('Reference sujet/propriete hors graphe')
        if not set(stmt['sources']).issubset(source_ids):
            raise DiKError('Source inconnue dans une assertion')
        for obj in [stmt['object'], *(q['object'] for q in stmt.get('qualifiers', []))]:
            if obj['kind'] == 'entity' and obj['id'] not in expected_entities:
                raise DiKError('Reference objet hors graphe')
        for q in stmt.get('qualifiers', []):
            if q['predicate'] not in expected_properties:
                raise DiKError('Propriete de qualificatif hors graphe')


def restore_compact(envelope: dict, project: Project | None = None) -> dict:
    """Restore by selecting canonical_graph, never by mapping words to IDs."""
    if not isinstance(envelope, dict) or set(envelope) != {
        'projection_format', 'derived_only', 'anchors', 'canonical_graph', 'lexicon', 'digests', 'limits'
    } or envelope['projection_format'] != COMPACT_PROFILE or envelope['derived_only'] is not True:
        raise DiKError('Enveloppe compacte inconnue')
    anchors = envelope['anchors']
    if not isinstance(anchors, dict) or set(anchors) != {
        'framework_contract', 'namespace_id', 'graph_id', 'source_sha256'
    } or anchors['framework_contract'] != FRAMEWORK_CONTRACT:
        raise DiKError('Ancrage Framework invalide')
    hashes = envelope['digests']
    if not isinstance(hashes, dict) or set(hashes) != {'canonical_graph', 'lexicon', 'anchors'}:
        raise DiKError('Empreintes compactes invalides')
    for key in ('canonical_graph', 'lexicon', 'anchors'):
        if hashes[key] != digest(envelope[key]):
            raise DiKError(f'Projection compacte alteree: {key}')
    graph = envelope['canonical_graph']
    ref.check_schema(graph, 'kristal-semantic-graph.schema.json')
    if graph['namespace_id'] != anchors['namespace_id'] or graph['graph_id'] != anchors['graph_id']:
        raise DiKError('Ancrage graphe incoherent')
    _check_consistency(graph, envelope['lexicon'])
    if project is not None:
        source_hashes = {
            'graph': ref.sha256(project.graph),
            'catalog': ref.sha256(project.catalog),
            'registry': ref.sha256(project.registry),
            'crosswalk': ref.sha256(project.crosswalk),
        }
        if anchors['source_sha256'] != source_hashes:
            raise DiKError('Sources ou dictionnaires modifies depuis projection')
        regenerated = project_compact(project, envelope['lexicon']['requested_locale'])
        if regenerated != envelope:
            raise DiKError('Projection non conforme aux sources approuvees')
    return copy.deepcopy(graph)


def _escape_md(value: object) -> str:
    text = html.escape(str(value), quote=False)
    return (text.replace('\\', '\\\\')
                .replace('|', '\\|').replace('`', '\\`')
                .replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))


def compact_markdown(envelope: dict, style: str = 'annotated') -> str:
    """Render directly from canonical assertions and a single lexical table."""
    if style not in ('annotated', 'clean'):
        raise DiKError('Style de lecture invalide')
    lex = envelope['lexicon']
    graph = envelope['canonical_graph']
    entries = lex['entries']
    def show(sem_id: str) -> str:
        info = entries[sem_id]
        label = info['label']
        display = _escape_md(label) if label is not None else f'[{sem_id}: non traduit]'
        return display if style == 'clean' else f'{display} (`{sem_id}`)'
    def obj_text(obj: dict) -> str:
        if obj['kind'] == 'entity':
            return show(obj['id'])
        return _escape_md(json.dumps(obj['value'], ensure_ascii=False, allow_nan=False)) + \
               f' ({_escape_md(obj["datatype"])})'
    lines = [f'# Kristal {_escape_md(graph["graph_id"])} — {_escape_md(lex["requested_locale"])}', '',
             '> Vue derivee, non canonique. Le Markdown seul est non reversible; garder le JSON diK.',
             '', '| Assertion | Sujet | Propriete | Objet | Sources |',
             '|---|---|---|---|---|']
    for stmt in graph['assertions']:
        lines.append('| ' + ' | '.join([
            f'`{stmt["id"]}`' if style == 'annotated' else '—',
            show(stmt['subject']), show(stmt['predicate']), obj_text(stmt['object']),
            ', '.join(f'`{s}`' for s in stmt['sources']) if style == 'annotated'
            else f'{len(stmt["sources"])} source(s)',
        ]) + ' |')
        for qualifier in stmt.get('qualifiers', []):
            # A clean display must NOT accidentally leak KP IDs for qualifiers.
            lines.append(f'\n  - Qualificatif : {show(qualifier["predicate"])} → '
                         f'{obj_text(qualifier["object"])}')
    counts = lex['coverage_counts']
    lines += ['', f'Couverture KQ/KP : {counts["direct"]} directes, '
              f'{counts["fallback"]} par repli, {counts["missing"]} manquantes.',
              '', 'Une edition de cette lecture ne peut pas etre reconvertie automatiquement en identites.']
    return '\n'.join(lines) + '\n'
