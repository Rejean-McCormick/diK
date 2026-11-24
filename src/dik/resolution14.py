"""Audit de RESOLUTION lexicale, sans traduction, pour le catalogue officiel Kristal.

Les identites sont (namespace,KQ/KP). Les Q/P Wikidata ne sont consultes
que via des exactMatch accepted avec preuves KS. Les imports GF candidats ne
sont jamais traites comme des formes resolues. Toutes les sources sont lues.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from ._framework import dictionaries as d
from .gf_handoff import audit_gf_handoff
from .kristals14 import (Kristals14Error, _output_directory, _select, _source,
                         _tree, _writer, discover)
from .scan14 import TARGET_LOCALES, _preindexed_layers

DETAIL = ['kristal', 'namespace_id', 'semantic_id', 'famille', 'locale', 'statut',
          'forme', 'identifiant_wikidata_accepte', 'origine_lien_qp', 'source_type', 'source_chemin',
          'source_couche', 'statut_preuve', 'conflit_avec_catalogue_courant', 'action']
COVERAGE = ['kristal', 'namespace_id', 'locale', 'etat_kristal', 'identites',
            'catalogue_courant', 'catalogue_raccorde', 'wikidata_observe',
            'conflit', 'non_resolu', 'identites_avec_qp_accepte', 'identites_avec_qp_candidat', 'cause']
SOURCE = ['catalogue', 'namespace_id', 'etat', 'justification', 'sha256', 'locales', 'entrees_utilisees']
GF = ['dossier', 'etat', 'locale', 'candidats', 'formes', 'justification']
STATES = ('catalogue_courant', 'catalogue_raccorde', 'wikidata_observe', 'conflit', 'non_resolu')


@dataclass
class Official:
    name: str
    namespace: str
    snapshot: object
    identities: list[tuple[str, str]]
    selected: dict
    crosswalk: dict
    accepted: dict[str, str]  # KQ/KP -> Q/P
    candidates: set[str]


def _read_crosswalk(snapshot, namespace, known):
    doc = d.read_json(snapshot.crosswalk)
    by_ext, by_local = d.accepted_exact(doc, namespace)
    reg = d.read_json(snapshot.registry)
    kind = {r['id']: r['kind'] for r in reg['identities']}
    for record in doc['mappings']:
        local = record['local_ref']
        if local['namespace_id'] != namespace:
            continue
        sid = local['id']
        if record['status'] == 'accepted':
            if sid not in known or any(kind.get(ref) != 'source' for ref in
                                        record.get('review', {}).get('evidence_refs', ())):
                raise Kristals14Error(f'Correspondance Wikidata acceptee sans preuve KS: {sid}')
    candidates = {m['local_ref']['id'] for m in doc['mappings'] if
                  m['local_ref']['namespace_id'] == namespace and
                  m['status'] != 'accepted' and m['local_ref']['id'] in known}
    return by_local, candidates


def _catalogs(root: Path):
    """Only structural v11 dictionary catalogues; no matching by word/name."""
    for directory, files in _tree(root):
        if directory.name.lower() == 'dictionaries' and 'catalog.json' in files:
            path = directory/'catalog.json'
            if not path.is_symlink():
                yield path


def _gf_sources(root: Path, manifests: list[Path] | None = None):
    # GF projection bundles are inventoried; never used for semantic coverage.
    source = ((folder / 'manifest.json' for folder, files in _tree(root)
               if 'manifest.json' in files) if manifests is None else iter(manifests))
    for manifest in source:
        folder = manifest.parent
        try:
            if manifest.is_symlink() or manifest.stat().st_size > 100_000:
                continue
            data = json.loads(manifest.read_text(encoding='utf-8'))
            # The repository contains many unrelated manifest.json files.
            # Some are top-level lists/scalars, not GF handoff objects.
            if not isinstance(data, dict):
                continue
            if data.get('profile') != 'dik.gf-lexical-handoff/0.1-candidate':
                continue
            try:
                result = audit_gf_handoff(folder)
                yield dict(dossier=str(folder), etat='candidat_seulement', locale=data['locale'],
                           candidats=result['candidate_lexemes'], formes=result['candidate_forms'],
                           justification='Aucun lien Kristal/GF approuve dans ce format')
            except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
                yield dict(dossier=str(folder), etat='audit_impossible', locale=data.get('locale', ''),
                           justification=f'{type(exc).__name__}: {exc}')
        except (OSError, UnicodeError, ValueError, TypeError):
            continue


def _source_index(officials: list[Official], sources_root: Path,
                  catalog_paths: list[Path] | None = None):
    """Validate external v11 layers using their OWN canonical registry/crosswalk.

    Same namespace and KQ/KP are required. An accepted Q/P may not contradict
    a selected accepted Q/P. A matching spelling never creates an equivalence.
    """
    namespaces = {x.namespace for x in officials}
    official_by_namespace = collections.defaultdict(list)
    for item in officials:
        official_by_namespace[item.namespace].append(item)
    official_accepted = collections.defaultdict(set)
    for item in officials:
        for kid, qid in item.accepted.items():
            official_accepted[item.namespace, kid].add(qid)
    result = collections.defaultdict(lambda: collections.defaultdict(set))
    linked_qp = collections.defaultdict(lambda: collections.defaultdict(set))
    inventory = []
    counts = collections.Counter()
    # Hash + path independently; no assumed authenticity from local SHA.
    seen_paths = set()
    audited_core = set()
    for path in (_catalogs(sources_root) if catalog_paths is None else catalog_paths):
        if path in seen_paths:
            continue
        seen_paths.add(path)
        row = dict(catalogue=str(path), namespace_id='', etat='', justification='',
                   sha256='', locales='', entrees_utilisees=0)
        try:
            if path.stat().st_size > 25_000_000:
                raise Kristals14Error('Catalogue trop volumineux pour inventaire automatique')
            catalog = d.read_json(path)
            d.check_schema(catalog, 'kristal-dictionary-catalog.schema.json')
            ns = catalog['namespace_id']
            row.update(namespace_id=ns, locales=','.join(x['tag'] for x in catalog['languages']),
                       sha256=d.sha256(path))
            if ns not in namespaces:
                # These sources cannot be transplanted into another namespace.
                row.update(etat='autre_namespace', justification='Aucun identifiant de ce namespace dans le catalogue officiel')
                inventory.append(row)
                counts[row['etat']] += 1
                continue
            base = path.parent.parent
            registry = base/'identity-registry.json'
            crosswalk = base/'external-crosswalk.json'
            graph = base/'semantic-graph.json'
            own_full = all(f.is_file() and not f.is_symlink() for f in (registry, crosswalk, graph))
            if not own_full:
                # An isolated updated dictionary catalogue may deliberately
                # inherit the official v11 registry/crosswalk. Prove this by
                # running the ENTIRE Framework dictionary audit against it;
                # never attach it merely because a word has the same spelling.
                refs = official_by_namespace[ns]
                if len(refs) != 1:
                    row.update(etat='source_v11_incomplete', justification=(
                        'Registre/crosswalk/graphe absents; zero ou plusieurs revisions officielles possibles'))
                    inventory.append(row)
                    counts[row['etat']] += 1
                    continue
                registry = refs[0].snapshot.registry
                crosswalk = refs[0].snapshot.crosswalk
                graph = refs[0].snapshot.graph
            # Exact source copies need layer hash checks but not a second JSON-schema
            # validation of every record. A differing layer is never trusted.
            core = (row['sha256'], d.sha256(registry), d.sha256(crosswalk), d.sha256(graph))
            if core in audited_core:
                for lang in catalog['languages']:
                    for layer in lang['layers']:
                        target = d.safe_file(path.parent, layer['path'])
                        if d.sha256(target) != layer['sha256']:
                            raise Kristals14Error('Couche modifiee dans une copie de catalogue')
                row.update(etat='copie_validee', justification='Meme ensemble canonique que catalogue deja audite; SHA des couches revérifies')
                inventory.append(row)
                counts[row['etat']] += 1
                continue
            d.audit(path, crosswalk, registry)
            reg = d.read_json(registry)
            g = d.read_json(graph)
            if not (reg['namespace_id'] == ns == g['namespace_id']):
                raise Kristals14Error('Namespace contradictoire dans le projet source')
            known = {x['id'] for x in reg['identities'] if x['kind'] in ('entity', 'property')}
            by_local, _ = _read_crosswalk(SimpleNamespace(crosswalk=crosswalk, registry=registry), ns, known)
            conflicts = [(kid, qid) for kid, qid in by_local.items()
                         if official_accepted[ns, kid] and qid not in official_accepted[ns, kid]]
            if conflicts:
                row.update(etat='crosswalk_contradictoire', justification=(
                    f'{len(conflicts)} exactMatch accepted contradictoire(s) entre revisions'))
                inventory.append(row)
                counts[row['etat']] += 1
                continue
            indexed, layers = _preindexed_layers(SimpleNamespace(catalog=path), catalog, known,
                                                 locales=set(TARGET_LOCALES))
            usable = sum(len(records) for records in indexed.values())
            # Every term is keyed by namespace + KQ/KP, not by external Q alone.
            for locale, records in indexed.items():
                for sid, (priority, term, layer) in records.items():
                    result[ns, sid, locale]['values'].add(term)
                    result[ns, sid, locale]['sources'].add((str(path), layer))
            for kid, qid in by_local.items():
                linked_qp[ns, kid][qid].add(str(crosswalk))
            audited_core.add(core)
            row.update(etat=('catalogue_v11_audite' if own_full else 'catalogue_raccorde_registre_officiel'),
                       justification=('Schemas, empreintes, registre et crosswalk verifies localement; '
                        'pas une certification de provenance externe' if own_full else
                        'Catalogue isole audite sur le registre/crosswalk OFFICIEL du meme namespace; '
                        'valeurs non publiees dans la revision selectionnee'), entrees_utilisees=usable)
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
            row.update(etat='audit_refuse', justification=f'{type(exc).__name__}: {exc}')
        inventory.append(row)
        counts[row['etat']] += 1
    return result, linked_qp, inventory, counts


def _wikidata_local(dump: Path | None, approved_sha256: str | None,
                    wanted: set[str]):
    """Optional local observation, NEVER a KQ mapping or a certified dictionary.

    Stream only requested accepted Q/P, never Wikidata L/S/F as an entity label.
    """
    if dump is None:
        if approved_sha256:
            raise Kristals14Error('Une empreinte attendue necessite --wikidata-dump')
        return {}, {'etat':'non_fourni', 'observations':0}
    dump = dump.expanduser().absolute()
    if not dump.is_file() or dump.is_symlink():
        raise Kristals14Error(f'Dump Wikidata introuvable ou symbolique: {dump}')
    fingerprint = d.sha256(dump)
    if approved_sha256:
        if not re.fullmatch('[a-fA-F0-9]{64}', approved_sha256):
            raise Kristals14Error('SHA-256 attendu invalide')
        if fingerprint.lower() != approved_sha256.lower():
            raise Kristals14Error('SHA-256 du dump Wikidata different de la valeur fournie; scan annule')
    observations = {}
    for entity in d.stream_entities(dump):
        qid = entity.get('id')
        if qid not in wanted:
            continue
        if qid in observations:
            raise Kristals14Error(f'Q/P Wikidata duplique dans le dump: {qid}')
        labels = {}
        for locale in TARGET_LOCALES:
            label = d.source_value(entity.get('labels', {}).get(locale))
            if label:
                labels[locale] = label
        observations[qid] = labels
    return observations, dict(etat='observe_localement', chemin=str(dump), sha256=fingerprint,
                              empreinte_attendue_fournie=bool(approved_sha256),
                              avertissement='Un SHA local ne prouve pas seul la provenance Wikidata',
                              identifiants_retrouves=len(observations), observations=sum(map(len, observations.values())))


def scan_resolution14(*, official_root: str | Path, sources_root: str | Path,
                      dik_root: str | Path | None = None, reports_root: str | Path | None = None,
                      min_kristals: int = 126, wikidata_dump: str | Path | None = None,
                      approved_sha256: str | None = None,
                      resource_registry: str | Path | None = None,
                      online_index: str | Path | None = None,
                      wikidata_source_id: str | None = None,
                      observe_qid_lexicon: bool = False,
                      observe_wikidata_thematic: bool = False,
                      wikidata_max_rows_per_pass: int = 0,
                      wikidata_max_bytes_per_pass: int = 0,
                      wikidata_max_candidates: int = 40000) -> dict:
    """Resolve 14 locales for official Kristals using *audited* local dictionaries.

    No write outside diK/reports. No network, no language-to-language translation.
    Unlinked GF/lexeme resources remain candidates. Non-evaluable projects are
    excluded from coverage denominators, but included in the official inventory.
    """
    sources_root = Path(sources_root).expanduser().absolute()
    if official_root is None:
        choices = [sources_root / 'Kristal' / 'kristal-public' / 'kristals',
                   sources_root / 'kristal-public' / 'kristals']
        matches = [p for p in choices if p.is_dir() and not p.is_symlink()]
        if len(matches) != 1:
            raise Kristals14Error('Racine officielle introuvable ou ambigue : indiquer --official-root')
        official_root = matches[0]
    official_root = Path(official_root).expanduser().absolute()
    dik_root = Path(dik_root).expanduser().absolute() if dik_root else Path(__file__).resolve().parents[2]
    if any(p.is_symlink() or not p.is_dir() for p in (official_root, sources_root, dik_root)):
        raise Kristals14Error('Racine du portefeuille, des sources ou de diK invalide')
    if min_kristals < 1:
        raise Kristals14Error('Minimum de Kristals invalide')
    reports = _output_directory(dik_root, Path(reports_root) if reports_root else Path('reports/resolution_14_langues'))
    # Crucial distinction: one official, immediate discovery directory = one Kristal.
    children = sorted((p for p in official_root.iterdir() if p.is_dir() and not p.is_symlink()
                       and (p/'kristal.discovery.json').is_file()
                       and not (p/'kristal.discovery.json').is_symlink()), key=lambda p:p.name.casefold())
    if len(children) < min_kristals:
        raise Kristals14Error(f'{len(children)} Kristals officiels (< {min_kristals}); verifie le chemin --official-root')
    discovered = {c.folder:c for c in discover(official_root)}
    officials = []
    inventory = []
    for child in children:
        candidate = discovered.get(child)
        if candidate is None:
            inventory.append(dict(kristal=child.name, dossier=str(child), etat='non_evaluable',
                                  cause='Aucun dossier de decouverte exploitable'))
            continue
        snapshot, notice, ignored = _select(candidate)
        if snapshot is None:
            inventory.append(dict(kristal=child.name, dossier=str(child), etat='non_evaluable',
                                  cause=notice, revisions_ignorees=ignored))
            continue
        try:
            ns, identities, active, languages, indexed, layers = _source(snapshot)
            known = {sid for sid, _ in identities}
            accepted, cand = _read_crosswalk(snapshot, ns, known)
            officials.append(Official(child.name, ns, snapshot, identities, indexed, d.read_json(snapshot.crosswalk),
                                      accepted, cand))
            inventory.append(dict(kristal=child.name, dossier=str(child), etat='evaluable',
                                  namespace_id=ns, identites=len(identities), revision=str(snapshot.root),
                                  identites_avec_qp_accepte=len(accepted), identites_avec_qp_candidat=len(cand),
                                  revisions_ignorees=ignored, avertissement=notice))
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
            inventory.append(dict(kristal=child.name, dossier=str(child), etat='non_evaluable',
                                  cause=f'{type(exc).__name__}: {exc}', revision=str(snapshot.root)))
    registry_doc = None
    catalog_paths = None
    gf_manifests = None
    if resource_registry is not None:
        from .resource_locator import load_registry, catalog_references, _unsafe
        registry_doc = load_registry(resource_registry)
        catalog_paths = catalog_references(registry_doc)
        gf_manifests = [Path(entry['path']) for entry in registry_doc['sources']
                        if entry['kind'] == 'gf_manifest_candidate' and
                        not _unsafe(Path(entry['path'])) and Path(entry['path']).is_file()]
    if wikidata_source_id:
        if wikidata_dump:
            raise Kristals14Error('Choisir --wikidata-dump OU --wikidata-source-id, pas les deux')
        if registry_doc is None:
            raise Kristals14Error('--wikidata-source-id exige --resource-registry')
        matches = [entry for entry in registry_doc['sources']
                   if entry['source_id'] == wikidata_source_id and
                   entry['kind'] == 'wikidata_qp_dump_candidate']
        if len(matches) != 1:
            raise Kristals14Error('Source Q/P introuvable ou non qualifiee comme dump Q/P')
        entry = matches[0]
        path = Path(entry['path'])
        if not path.is_file() or path.is_symlink():
            raise Kristals14Error('Source Wikidata deplacee ou lien symbolique')
        if entry.get('sha256') and d.sha256(path) != entry['sha256']:
            raise Kristals14Error('Dump Wikidata modifie depuis sa decouverte')
        wikidata_dump = path
    global_index, qp_index, source_inventory, sources_count = _source_index(
        officials, sources_root, catalog_paths=catalog_paths)
    # Previously reviewed exactMatch from another audited canonical revision may
    # supply a Q/P, but competing Q/P are never silently selected.
    trusted_qp = {}
    qp_conflicts = 0
    for item in officials:
        for sid, _ in item.identities:
            possible = set(qp_index.get((item.namespace, sid), {}))
            possible.update([item.accepted[sid]] if sid in item.accepted else [])
            if len(possible) == 1:
                trusted_qp[item.namespace, sid] = next(iter(possible))
            elif len(possible) > 1:
                qp_conflicts += 1
    wanted = set(trusted_qp.values())
    wikidata, wikidata_info = _wikidata_local(Path(wikidata_dump) if wikidata_dump else None,
                                             approved_sha256, wanted)
    qid_candidate_forms = {}
    qid_candidate_info = {'status': 'not_requested', 'candidate_only': True}
    if observe_qid_lexicon:
        if registry_doc is None:
            raise Kristals14Error('--observe-qid-lexicon exige --resource-registry')
        from .source_qualification import observe_registered_qid_lexicon
        qid_candidate_forms, qid_candidate_info = observe_registered_qid_lexicon(
            registry_doc, wanted=wanted, locales=tuple(TARGET_LOCALES))
    online_observations = {}
    online_info = {'status':'NOT_REQUESTED','candidate_only':True,'activations':0}
    if online_index is not None:
        from .online_sources import observe_online
        online_path = Path(online_index).expanduser().absolute()
        # No access to arbitrary files outside diK/reports.
        if not online_path.is_relative_to(dik_root/'reports'):
            raise Kristals14Error('Cache en ligne hors diK/reports')
        online_observations, online_info = observe_online(
            online_path,wanted=wanted,locales=tuple(TARGET_LOCALES))
    thematic_observations = {}
    thematic_profiles = []
    thematic_overlaps = []
    thematic_info = {'status':'not_requested', 'candidate_only': True, 'activations':0}
    if observe_wikidata_thematic:
        if registry_doc is None:
            raise Kristals14Error('--observe-wikidata-thematic exige --resource-registry')
        from .wikidata_v53 import observe_thematic_v53
        thematic_observations, thematic_profiles, thematic_info, thematic_overlaps = observe_thematic_v53(
            registry_doc, wanted=wanted, locales=tuple(TARGET_LOCALES),
            checkpoint_dir=reports/'checkpoints_v53',
            max_rows_per_pass=wikidata_max_rows_per_pass,
            max_bytes_per_pass=wikidata_max_bytes_per_pass,
            max_pairs=wikidata_max_candidates, accepted_links=trusted_qp)
    gf = list(_gf_sources(sources_root, manifests=gf_manifests))
    reports.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = reports/f'RESOLUTION_{now}'
    index = 2
    while dest.exists():
        dest = reports/f'RESOLUTION_{now}_{index}'
        index += 1
    stage = Path(tempfile.mkdtemp(prefix='.resolution14-', dir=reports))
    open_files = {}
    totals = collections.Counter()
    per_lang = collections.defaultdict(collections.Counter)
    try:
        for name, columns in (
            ('resolution_identifiants_14_langues.csv', DETAIL),
            ('identifiants_non_resolus.csv', DETAIL),
            ('raccordements_a_qualifier.csv', DETAIL),
            ('couverture_kristals_14_langues.csv', COVERAGE),
            ('sources_dictionnaires.csv', SOURCE),
            ('sources_gf_candidates.csv', GF),
            ('wikidata_online_observations_candidates.csv',
             ['kristal','namespace_id','semantic_id','wikidata_qp','locale','forme_candidate',
              'source_url','response_sha256','license','retrieved_utc','candidate_only','publication']),
            ('wikidata_online_potential_coverage.csv',
             ['locale','cellules_candidates','non_resolues_avec_candidat','nouvelles_formes_publiees']),
            ('wikidata_qid_observations_candidates.csv',
             ['kristal','namespace_id','semantic_id','wikidata_qp','locale','forme_candidate',
              'source_id','statut','avertissement']),
            ('wikidata_thematic_sources.csv',
             ['source_id','path','sha256','status','rows_read','rows_with_qp',
              'rows_matching_accepted_qp','distinct_qp','distinct_qp_matching_accepted',
              'explicit_labels_for_accepted_qp','conflicts_within_source',
              'invalid_or_oversized_rows','truncated','candidate_only',
              'identical_to_source_id']),
            ('wikidata_thematic_observations_candidates.csv',
             ['kristal','namespace_id','semantic_id','wikidata_qp','locale',
              'forme_candidate','source_id','sha256','statut','avertissement']),
            ('wikidata_schema_profiles.csv',
             ['source_id','sha256','family','schema_id','container','status','evidence','adapter_version',
              'schema_shapes','schema_fields','completed','candidate_only']),
            ('wikidata_scan_progress.csv',
             ['source_id','bytes_read','lines_read','line_next','completed','checkpoint_ref',
              'stop_reason','status','sha256']),
            ('wikidata_qp_overlap.csv',
             ['namespace_id','semantic_id','wikidata_qp','crosswalk_ref','source_id',
              'record_location','field_path','identity_role','overlap_status']),
            ('wikidata_forms_candidates.csv',
             ['namespace_id','semantic_id','wikidata_qp','locale','form','source_id','source_sha256',
              'field_path','record_location','candidate_status']),
            ('wikidata_identity_links_candidates.csv',
             ['source_id','source_sha256','namespace_id','semantic_id','external_id',
              'source_claimed_status','comparison','official_accepted_qp',
              'record_location','candidate_only']),
            ('wikidata_nonlexical_qp_observations.csv',
             ['source_id','sha256','wikidata_qp','role','field_path','record_location','candidate_only']),
            ('wikidata_conflicts.csv',
             ['scope','namespace_id','semantic_id','wikidata_qp','locale','source_ids','reason']),
            ('wikidata_source_decisions.csv',
             ['source_id','rights_status','provenance_status','review_state','decision_ref']),
            ('kristals_officiels.csv', ['kristal','dossier','etat','namespace_id','identites','revision',
                                     'identites_avec_qp_accepte','identites_avec_qp_candidat','cause',
                                     'revisions_ignorees','avertissement']),
        ):
            open_files[name] = _writer(stage/name, columns)
        def emit(filename, row):
            # Prevent Excel formula execution when human-readable CSV is opened.
            # Original source files and exact terms remain unchanged on disk.
            safe = {key: ("'"+value if isinstance(value, str) and
                             value.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')) else value)
                    for key, value in row.items()}
            open_files[filename][1].writerow(safe)
        with (stage/'scan.log').open('w', encoding='utf-8') as log:
            def event(text):
                log.write(text+'\n')
                log.flush()
            event(f'diK resolution14 v3; utc={now}; no_network=oui; no_translation=oui')
            event(f'portefeuille_officiel={official_root}; recherche_dictionnaires={sources_root}')
            if resource_registry: event(f'registre_ressources={resource_registry}')
            for row in inventory:
                emit('kristals_officiels.csv', row)
                event(f'{row["kristal"]}: {row["etat"]} — {row.get("cause", "") or row.get("identites", "")}')
            for row in source_inventory:
                emit('sources_dictionnaires.csv', row)
            for row in gf:
                emit('sources_gf_candidates.csv', row)
            for row in thematic_profiles:
                emit('wikidata_thematic_sources.csv', {
                    **row,
                    'rows_read':row.get('lines_read',0),
                    'invalid_or_oversized_rows':sum(row.get(k,0) for k in
                        ('malformed_json','invalid_utf8','oversized_rows','schema_mismatches')),
                    'truncated':bool(row.get('status') in ('partial_budget','incomplete_errors') or
                                      (row.get('schema_id') and not row.get('completed',False))),
                })
            # V5.3: distinct evidence tables, no semantic activation. The
            # accepted mapping is always selected by the audited v11 code.
            for row in thematic_profiles:
                emit('wikidata_schema_profiles.csv', {
                    'source_id':row.get('source_id',''), 'sha256':row.get('sha256',''),
                    'family':'wikidata_thematic_candidate', 'schema_id':row.get('schema_id',''),
                    'container':row.get('container',''), 'status':row.get('status',''), 'evidence':row.get('evidence',''),
                    'adapter_version':row.get('adapter_version',''),
                    'schema_shapes':json.dumps(row.get('shapes',{}),ensure_ascii=False),
                    'schema_fields':json.dumps(row.get('top_level_fields',{}),ensure_ascii=False),
                    'completed':row.get('completed',False), 'candidate_only':True,
                })
                emit('wikidata_scan_progress.csv', {
                    'source_id':row.get('source_id',''), 'bytes_read':row.get('bytes_read',0),
                    'lines_read':row.get('lines_read',0), 'line_next':row.get('line_next',1),
                    'completed':row.get('completed',False),
                    'checkpoint_ref':row.get('checkpoint_ref',''),
                    'stop_reason':row.get('reason',''), 'status':row.get('status',''),
                    'sha256':row.get('sha256',''),
                })
                emit('wikidata_source_decisions.csv', {
                    'source_id':row.get('source_id',''), 'rights_status':'not_verified',
                    'provenance_status':'sha_local_only', 'review_state':'unapproved',
                    'decision_ref':'',
                })
                for observation in row.get('nonlexical_accepted_qp_evidence',()):
                    emit('wikidata_nonlexical_qp_observations.csv', {
                        'source_id':observation['source_id'],'sha256':observation['sha256'],
                        'wikidata_qp':observation['qp'],'role':observation['role'],
                        'field_path':observation['field_path'],
                        'record_location':f"byte:{observation['offset_bytes']};line:{observation['line']}",
                        'candidate_only':True,
                    })
                for candidate in row.get('candidate_link_evidence',()):
                    emit('wikidata_identity_links_candidates.csv', {
                        **{k:v for k,v in candidate.items() if k not in ('offset_bytes','line')},
                        'record_location':f"byte:{candidate['offset_bytes']};line:{candidate['line']}",
                        'candidate_only':True,
                    })
            # Multiple Kristals can use the same accepted Q/P without becoming
            # the same namespace. Never join on spelling or numeric suffix.
            by_qp = collections.defaultdict(list)
            for item in officials:
                for sid,_ in item.identities:
                    qp = trusted_qp.get((item.namespace,sid))
                    if qp:
                        by_qp[qp].append((item,sid))
            for hit in thematic_overlaps:
                for item,sid in by_qp.get(hit['qp'],()):
                    emit('wikidata_qp_overlap.csv', {
                        'namespace_id':item.namespace,'semantic_id':sid,
                        'wikidata_qp':hit['qp'],
                        'crosswalk_ref':str(item.snapshot.crosswalk) if item.accepted.get(sid)==hit['qp'] else 'autre_revision_v11_auditee',
                        'source_id':hit['source_id'],
                        'record_location':f"byte:{hit['offset_bytes']};line:{hit['line']}",
                        'field_path':hit['field_path'],'identity_role':hit['role'],
                        'overlap_status':'candidate_only',
                    })
            thematic_observation_count = 0
            qid_observation_count = 0
            if qid_candidate_forms:
                for item in officials:
                    for sid, _ in item.identities:
                        qid = trusted_qp.get((item.namespace, sid))
                        if not qid:
                            continue
                        for locale in TARGET_LOCALES:
                            term = qid_candidate_forms.get((qid, locale))
                            if not term:
                                continue
                            emit('wikidata_qid_observations_candidates.csv', {
                                'kristal': item.name, 'namespace_id':item.namespace,
                                'semantic_id':sid, 'wikidata_qp':qid, 'locale':locale,
                                'forme_candidate':term, 'source_id':qid_candidate_info.get('source_id',''),
                                'statut':'observation_non_publiee',
                                'avertissement':'format_lexical_et_droits_non_certifies;pas_de_traduction'})
                            qid_observation_count += 1
            online_candidate_rows = 0
            online_potential = collections.Counter()
            online_missing_candidate = collections.Counter()
            if online_observations:
                for item in officials:
                    for sid, _ in item.identities:
                        qp = trusted_qp.get((item.namespace,sid))
                        if not qp:
                            continue
                        for locale in TARGET_LOCALES:
                            hit = online_observations.get((qp,locale))
                            if hit is None:
                                continue
                            online_candidate_rows += 1
                            online_potential[locale] += 1
                            # Potential ONLY; unrelated to validated/current coverage totals.
                            direct = item.selected.get(locale,{}).get(sid)
                            options = global_index.get((item.namespace,sid,locale),{})
                            if not direct and not options.get('values',set()):
                                online_missing_candidate[locale] += 1
                            emit('wikidata_online_observations_candidates.csv',{
                                'kristal':item.name,'namespace_id':item.namespace,
                                'semantic_id':sid,'wikidata_qp':qp,'locale':locale,
                                'forme_candidate':hit['form'],
                                'source_url':hit['source_url'],
                                'response_sha256':hit['response_sha256'],
                                'license':hit['license'],
                                'retrieved_utc':hit['retrieved_utc'],
                                'candidate_only':True,'publication':'non_approuvee',
                            })
            for locale in TARGET_LOCALES:
                emit('wikidata_online_potential_coverage.csv',{
                    'locale':locale,'cellules_candidates':online_potential[locale],
                    'non_resolues_avec_candidat':online_missing_candidate[locale],
                    'nouvelles_formes_publiees':0,
                })
            # Thematic JSONL observations are *candidates*, never a coverage source.
            # Join them only through already-audited, unambiguous KQ/KP -> Q/P.
            if thematic_observations:
                for item in officials:
                    for sid, _ in item.identities:
                        qp = trusted_qp.get((item.namespace, sid))
                        if not qp:
                            continue
                        for locale in TARGET_LOCALES:
                            for match in thematic_observations.get((qp, locale), ()):
                                emit('wikidata_thematic_observations_candidates.csv', {
                                    'kristal':item.name, 'namespace_id':item.namespace,
                                    'semantic_id':sid, 'wikidata_qp':qp, 'locale':locale,
                                    'forme_candidate':match['form'],
                                    'source_id':match['source_id'], 'sha256':match['sha256'],
                                    'statut':match['status'],
                                    'avertissement':'source_thematique_non_approuvee;pas_de_traduction',
                                })
                                emit('wikidata_forms_candidates.csv', {
                                    'namespace_id':item.namespace, 'semantic_id':sid,
                                    'wikidata_qp':qp, 'locale':locale,'form':match['form'],
                                    'source_id':match['source_id'],'source_sha256':match['sha256'],
                                    'field_path':match.get('field_path',''),
                                    'record_location':f"byte:{match.get('offset_bytes',0)};line:{match.get('line',0)}",
                                    'candidate_status':match['status'],
                                })
                                if match['status']=='conflict':
                                    emit('wikidata_conflicts.csv', {
                                        'scope':'qp_locale','namespace_id':item.namespace,
                                        'semantic_id':sid,'wikidata_qp':qp,'locale':locale,
                                        'source_ids':'|'.join(sorted({m['source_id'] for m in thematic_observations.get((qp,locale),())})),
                                        'reason':'formes_explicitement_contradictoires_pas_de_selection',
                                    })
                                thematic_observation_count += 1
            for item in officials:
                for locale in TARGET_LOCALES:
                    subtotals = collections.Counter()
                    for sid, kind in item.identities:
                        direct = item.selected.get(locale, {}).get(sid)
                        options = global_index.get((item.namespace, sid, locale), {})
                        alternatives = options.get('values', set())
                        other_sources = options.get('sources', set())
                        qid = trusted_qp.get((item.namespace, sid), '')
                        link_origin = ('crosswalk_selectionne' if item.accepted.get(sid)==qid and qid
                                       else ('crosswalk_autre_revision_auditee' if qid else ''))
                        word = source_kind = src_path = src_layer = proof = ''
                        if direct:
                            state = 'catalogue_courant'
                            word = direct[1]; src_layer = direct[2]
                            src_path = str(item.snapshot.catalog)
                            source_kind = 'framework_v11'
                            proof = 'couche_auditee_locale'
                        elif len(alternatives) > 1:
                            state = 'conflit'
                            proof = 'plusieurs_formes_dans_catalogues_audites'
                            source_kind = 'framework_v11'
                            src_path = '|'.join(sorted(x[0] for x in other_sources)[:5])
                        elif len(alternatives) == 1:
                            state = 'catalogue_raccorde'
                            word = next(iter(alternatives))
                            source_kind = 'framework_v11_autre_revision'
                            src_path, src_layer = sorted(other_sources)[0]
                            proof = 'structure_et_empreinte_locale_auditees'
                        elif qid and wikidata.get(qid, {}).get(locale):
                            state = 'wikidata_observe'
                            word = wikidata[qid][locale]
                            source_kind = 'wikidata_QP_dump_local'
                            src_path = wikidata_info.get('chemin','')
                            proof = 'exactMatch_accepte_KS_et_observation_locale_non_publiee'
                        else:
                            state = 'non_resolu'
                            if len(qp_index.get((item.namespace, sid), {})) > 1:
                                proof = 'plusieurs_exactMatch_accepted_contradictoires'
                            elif qid:
                                proof = 'QP_accepte_sans_libelle_connecte_pour_locale'
                            elif sid in item.candidates:
                                proof = 'crosswalk_candidat_non_approuve'
                            else:
                                proof = 'pas_de_correspondance_externe_approuvee'
                        revision_conflict = bool(direct and any(v != direct[1] for v in alternatives))
                        if revision_conflict:
                            totals['conflits_de_revision_avec_courant'] += 1
                        action = {
                            'catalogue_courant':'aucune', 'catalogue_raccorde':'evaluer_raccordement_catalogue',
                            'wikidata_observe':'qualifier_import_source_et_licence',
                            'conflit':'revoir_priorites_et_provenance',
                            'non_resolu':'verifier_sources_lexicales_et_crosswalk',
                        }[state]
                        row = dict(kristal=item.name, namespace_id=item.namespace,
                                   semantic_id=sid, famille=kind, locale=locale,
                                   statut=state, forme=word, identifiant_wikidata_accepte=qid,
                                   origine_lien_qp=link_origin,
                                   source_type=source_kind, source_chemin=src_path,
                                   source_couche=src_layer, statut_preuve=proof,
                                   conflit_avec_catalogue_courant='oui' if revision_conflict else 'non',
                                   action=action)
                        emit('resolution_identifiants_14_langues.csv', row)
                        if state in ('conflit', 'non_resolu'):
                            emit('identifiants_non_resolus.csv', row)
                        elif state in ('catalogue_raccorde', 'wikidata_observe') or revision_conflict:
                            emit('raccordements_a_qualifier.csv', row)
                        subtotals[state] += 1
                        totals[state] += 1
                        per_lang[locale][state] += 1
                    emit('couverture_kristals_14_langues.csv', {
                        'kristal':item.name, 'namespace_id':item.namespace, 'locale':locale,
                        'etat_kristal':'evaluable', 'identites':len(item.identities),
                        **{s:subtotals[s] for s in STATES},
                        'identites_avec_qp_accepte':len(item.accepted),
                        'identites_avec_qp_candidat':len(item.candidates),
                    })
            for row in inventory:
                if row['etat'] != 'evaluable':
                    for locale in TARGET_LOCALES:
                        emit('couverture_kristals_14_langues.csv', dict(kristal=row['kristal'], locale=locale,
                             etat_kristal='non_evaluable', cause=row.get('cause','')))
            event(f'fin: {len(children)} officiels, {len(officials)} evaluables, '
                  f'{sum(totals.values())} cellules')
        payload = {
            'schema':'dik.resolution.portfolio14/3.0', 'etat':'PARTIEL' if len(officials)<len(children) else 'EVALUE_SUR_SOURCES_LOCALES',
            'mode':'LECTURE_SEULE', 'traduction_entre_langues':False, 'reseau_utilise':False,
            'date_utc':now, 'portefeuille_officiel':str(official_root),
            'sources_recherchees':str(sources_root), 'registre_ressources':str(resource_registry or ''),
            'sources_reperees':len(registry_doc['sources']) if registry_doc else None,
            'wikidata_source_id_selectionne':wikidata_source_id or '',
            'dossier_rapports':str(dest),
            'locales':list(TARGET_LOCALES),
            'totaux':{
                'kristals_officiels':len(children), 'kristals_evalues':len(officials),
                'kristals_non_evaluables':len(children)-len(officials),
                'identites_par_kristal':sum(len(o.identities) for o in officials),
                'cellules_evaluees':sum(totals.values()),
                **{s:totals[s] for s in STATES},
                'identites_qp_acceptees':sum(len(o.accepted) for o in officials),
                'identites_qp_candidates':sum(len(o.candidates) for o in officials),
                'identites_qp_acceptes_apres_raccordement':len(trusted_qp),
                'identites_aux_liens_qp_contradictoires':qp_conflicts,
                'catalogues_sources_detectes':len(source_inventory),
                'catalogues_v11_audites':sources_count['catalogue_v11_audite'],
                'catalogues_qualifies_sur_registre_officiel':sources_count['catalogue_raccorde_registre_officiel'],
                'gf_handoffs_candidats':len(gf),
                'wikidata_qid_observations_non_publiees':
                    qid_observation_count if observe_qid_lexicon else 0,
                'wikidata_thematic_observations_non_publiees': thematic_observation_count,
                'wikidata_online_observations_non_publiees':online_candidate_rows,
                'wikidata_online_potentiel_non_resolu':sum(online_missing_candidate.values()),
                'conflits_de_revision_avec_courant':totals['conflits_de_revision_avec_courant'],
            },
            'par_langue':[{'locale':locale, **{s:per_lang[locale][s] for s in STATES}} for locale in TARGET_LOCALES],
            'wikidata_online':{**online_info, 'candidate_rows_for_kristals':online_candidate_rows,
                               'candidate_missing_cells':sum(online_missing_candidate.values()),
                               'published_forms':0},
            'wikidata_dump_local':wikidata_info,
            'wikidata_qid_lexicon':{**qid_candidate_info, 'observations_pour_kristals':
                                   qid_observation_count if observe_qid_lexicon else 0},
            'wikidata_thematic':{**thematic_info, 'observations_pour_kristals':
                                 thematic_observation_count},
            'wikidata_v53': {
                'profile':'dik.wikidata-thematic-diagnostics/5.3.0',
                'candidate_only':True,'activations':0,
                'sources_total':thematic_info.get('sources_registered',0),
                'sources_completed':thematic_info.get('sources_completed',0),
                'sources_schema_unknown':thematic_info.get('sources_schema_unknown',0),
                'sources_incomplete':thematic_info.get('sources_incomplete',0),
                'rows_valid_json':thematic_info.get('rows_valid_json',0),
                'rows_with_qp':thematic_info.get('rows_with_qp',0),
                'qp_overlapping_accepted_crosswalk':thematic_info.get('qp_overlapping_accepted_crosswalk',0),
                'explicit_labels_observed':thematic_info.get('explicit_labels_observed',0),
                'controls':'aucune activation; aucun candidat dans couverture',
            },
            'wikidata_v54': {
                'profile':'dik.wikidata-thematic-diagnostics/5.4.0',
                'candidate_only':True,'activations':0,
                'sources_total':thematic_info.get('sources_registered',0),
                'sources_completed':thematic_info.get('sources_completed',0),
                'sources_schema_unknown':thematic_info.get('sources_schema_unknown',0),
                'candidate_identity_links':thematic_info.get('candidate_identity_links',0),
                'candidate_identity_links_consistent':thematic_info.get('candidate_identity_links_consistent',0),
                'candidate_identity_links_contradictory':thematic_info.get('candidate_identity_links_contradictory',0),
                'nonlexical_qp_observations':thematic_info.get('nonlexical_qp_observations',0),
                'statement_sources_completed':thematic_info.get('statement_sources_completed',0),
                'controls':'aucune activation; aucune forme non lexicale dans la couverture',
            },
            'wikidata_v55': {
                'profile':'dik.wikidata-thematic-diagnostics/5.5.0',
                'candidate_only':True,'activations':0,
                'sources_total':thematic_info.get('sources_registered',0),
                'sources_completed':thematic_info.get('sources_completed',0),
                'sources_schema_unknown':thematic_info.get('sources_schema_unknown',0),
                'json_array_sources_completed':sum(
                    bool(x.get('completed')) and x.get('container')=='json_array'
                    for x in thematic_profiles),
                'json_array_rows_read':sum(x.get('rows_valid_json',0)
                    for x in thematic_profiles if x.get('container')=='json_array'),
                'qp_overlapping_accepted_crosswalk':thematic_info.get('qp_overlapping_accepted_crosswalk',0),
                'candidate_forms':thematic_info.get('candidate_forms',0),
                'candidate_identity_links':thematic_info.get('candidate_identity_links',0),
                'notice':'Les libelles des fichiers GF-Wikidata restent candidats non publies',
            },
            'kristals':inventory,
            'limites':[
                'Un Kristal officiel = un dossier immediate de kristal-public/kristals ayant kristal.discovery.json.',
                'Les KQ/KP restent dans leur namespace. Q/P ne sont lies que par exactMatch accepted et preuves KS.',
                'Des exactMatch accepted contradictoires entre revisions ne sont pas fusionnes.',
                'Un catalogue v11 audite prouve structure, empreintes et alignement local, pas authentification externe.',
                'Les crosswalks candidats ne donnent aucun mot valide; aucun alignement lexical par similarite.',
                'GF handoff candidat: aucun paradigme grammatical ni forme inflechie validee par cet audit.',
                'Les langues non resolues ne sont pas des traductions manquantes.',
                'Les observations QID et Wikidata thematiques sont des candidats non actives : elles ne changent jamais les totaux de couverture.',
                'Un source_id Wikidata est une reference locale, pas une certification de provenance ou de droits.',
                'L’absence de dump Wikidata officiel local ne prouve pas l’absence de labels sur Wikidata.',
                'Wikidata V5.6: observation en ligne candidate CC0, aucune activation, aucun fallback linguistique, aucun transfert de KQ/KP au fournisseur.',
                'Aucun ecrasement, aucune traduction automatique, aucun reseau, aucun Git/Render.',
            ],
        }
        if observe_wikidata_thematic:
            from .wikidata_v53 import ADAPTER_VERSION, REPORT_VERSION
            source_schemas = {row['source_id']:{
                'status':row.get('status',''),
                'schema_id':row.get('schema_id',''), 'container':row.get('container',''),
                'sha256':row.get('sha256',''),
                'adapter_version':row.get('adapter_version','')
            } for row in thematic_profiles}
            (stage/'wikidata_schema_registry.json').write_text(json.dumps({
                'profile':'dik.wikidata-schema-registry/5.5.0',
                'adapter_version':ADAPTER_VERSION,
                'sources':source_schemas,
                'candidate_only':True,'activations':0,
            },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            manifest = {
                'schema':REPORT_VERSION,
                'wikidata_adapter':ADAPTER_VERSION,
                'official_locales':list(TARGET_LOCALES),
                'resource_registry_sha256':d.sha256(Path(resource_registry)),
                'official_crosswalk_sha256':{item.name:d.sha256(item.snapshot.crosswalk) for item in officials},
                'max_rows_per_pass':wikidata_max_rows_per_pass,
                'max_bytes_per_pass':wikidata_max_bytes_per_pass,
                'max_candidates_per_source':wikidata_max_candidates,
                'candidate_only':True,'activations':0,
                'no_translation':True,
                'report_status':thematic_info.get('status',''),
            }
            (stage/'wikidata_run_manifest.json').write_text(json.dumps(manifest,
                ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (stage/'rapport.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        for stream, _ in open_files.values():
            stream.close()
        open_files.clear()
        stage.rename(dest)
        return payload
    finally:
        for stream, _ in open_files.values():
            stream.close()
        if stage.exists():
            shutil.rmtree(stage)
