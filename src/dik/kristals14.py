"""Local, read-only 14-locale portfolio audit of real Kristal repositories.

Discovers Kristals before selecting one coherent *v11 snapshot* per Kristal.
Never infers KQ/KP from strings, never merges namespaces, never edits sources.
Reports are published atomically in the diK checkout's ignored reports folder.
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

from ._framework import coverage as framework_coverage
from ._framework import dictionaries
from .operations import load_project
from .scan14 import TARGET_LOCALES, _preindexed_layers, _resolve

# Do not walk dependencies, generated reports, or demo fixtures on C:\mycode.
SKIP_DIRS = frozenset({
    '.git', '.hg', '.svn', '__pycache__', '.pytest_cache', '.venv', 'venv',
    'node_modules', '.next', 'build', 'dist', 'reports', 'local-snapshots',
    '.dik-cache', 'coverage', 'examples', 'tests', 'fixtures',
    'koa_upgrade_runs',
})
DETAIL_COLUMNS = [
    'kristal', 'namespace_id', 'semantic_id', 'famille', 'dans_graphe',
    'locale', 'etat', 'libelle_resolu', 'langue_source', 'preuve_couche',
    'statut_preuve', 'action', 'revision',
]
KRISTAL_COLUMNS = [
    'kristal', 'dossier', 'etat', 'revision', 'namespace_id',
    'graphe_sha256', 'registre_sha256', 'catalogue_sha256', 'crosswalk_sha256',
    'identites_KQ_KP',
    'references_graphe', 'langues_configurees', 'cellules_directes',
    'cellules_repli', 'cellules_manquantes', 'cellules_non_configurees',
    'cause',
]
CATALOG_COLUMNS = [
    'kristal', 'revision', 'namespace_id', 'locale', 'couche', 'type',
    'chemin', 'priorite', 'entrees_lues', 'sha256', 'integrite',
]
ALERT_COLUMNS = ['kristal', 'niveau', 'code', 'detail', 'chemin']
CANDIDATE_COLUMNS = [
    'kristal', 'catalogue', 'namespace_id', 'locales', 'etat_preuve',
    'detail', 'identites_liees', 'empreinte_catalogue',
]
RECOVERY_COLUMNS = [
    'kristal', 'namespace_id', 'semantic_id', 'famille', 'locale',
    'libelle_candidat', 'catalogue_alternatif', 'preuve_couche', 'etat_preuve', 'action',
]
PER_LANGUAGE_COLUMNS = [
    'kristal', 'revision', 'namespace_id', 'locale', 'etat_kristal',
    'identites_KQ_KP', 'direct', 'repli', 'manquant',
    'langue_non_configuree', 'pourcentage_direct', 'complet_direct', 'cause',
]


class Kristals14Error(ValueError):
    """Unsafe scan configuration or invalid portfolio output."""


@dataclass(frozen=True)
class Snapshot:
    root: Path
    graph: Path
    registry: Path
    crosswalk: Path
    catalog: Path
    manifest: Path | None = None


@dataclass
class Candidate:
    folder: Path
    snapshots: list[Path]
    manifests: list[Path]
    catalogs: list[Path]


def _tree(root: Path):
    """Iterate local directories without following symlinks or generated trees."""
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d.casefold() not in SKIP_DIRS and
                         not (Path(current) / d).is_symlink())
        yield Path(current), set(files)


def _owner(path: Path, discoveries: set[Path], root: Path) -> Path | None:
    for parent in [path, *path.parents]:
        if parent in discoveries:
            return parent
        if parent == root:
            break
    # Standalone projects may have canon/domain/v11 but no discovery file.
    for parent in [path, *path.parents]:
        if parent == root.parent:
            break
        if (parent / 'canon').is_dir() or (parent / '.kristal').is_dir():
            return parent
    if path == root and ((root / 'dik.project.json').exists() or
                         (root / 'identity-registry.json').exists()):
        return root
    return None


def discover(root: Path) -> list[Candidate]:
    if not root.is_dir():
        raise Kristals14Error(f'Dossier source introuvable: {root}')
    if root.is_symlink():
        raise Kristals14Error('Racine source symbolique refusée')
    discovery: set[Path] = set()
    registries: list[Path] = []
    manifests: list[Path] = []
    catalogs: list[Path] = []
    for folder, names in _tree(root):
        if 'kristal.discovery.json' in names:
            discovery.add(folder)
        if 'identity-registry.json' in names and (
            'v11' in folder.parts or (folder / 'dictionaries' / 'catalog.json').is_file()
        ):
            registries.append(folder)
        if 'dik.project.json' in names:
            manifests.append(folder / 'dik.project.json')
        if folder.name == 'dictionaries' and 'catalog.json' in names:
            catalogs.append(folder / 'catalog.json')
    found = {p: Candidate(p, [], [], []) for p in discovery}
    for folder in registries:
        owner = _owner(folder, discovery, root)
        if owner is not None:
            found.setdefault(owner, Candidate(owner, [], [], [])).snapshots.append(folder)
    for manifest in manifests:
        owner = _owner(manifest.parent, discovery, root)
        if owner is not None:
            found.setdefault(owner, Candidate(owner, [], [], [])).manifests.append(manifest)
    for catalog in catalogs:
        owner = _owner(catalog.parent, discovery, root)
        if owner is not None and owner in found:
            found[owner].catalogs.append(catalog)
    return sorted(found.values(), key=lambda c: c.folder.as_posix().casefold())


def _revision_key(path: Path) -> tuple:
    """Deterministic revision ordering; dated updates and numeric v11 revisions win."""
    path_string = path.as_posix().lower()
    segments = re.findall(r'\d+', path_string.split('/v11/', 1)[-1])
    # Date + revision in snapshot basename, rather than arbitrary parent digits.
    leaf = path.name.lower()
    date_match = re.search(r'(20\d\d)[-_.]?(\d\d)[-_.]?(\d\d)', leaf)
    day = ''.join(date_match.groups()) if date_match else ''
    rev_match = re.search(r'(?:v11|revision|rev)[-_.]?(\d+)(?:[-_.](\d+))?', leaf)
    revision = tuple(int(v) for v in rev_match.groups() if v is not None) if rev_match else ()
    return (day, revision, tuple(int(v) for v in segments[-5:]), path_string)


def _select(candidate: Candidate) -> tuple[Snapshot | None, str, int]:
    """Prefer explicit dik.project, otherwise latest complete v11 snapshot.

    An incomplete *newer* snapshot must not silently override an older valid one;
    candidates without the coherent four-file bundle are ignored and reported.
    """
    manifest_errors = []
    for path in sorted(candidate.manifests, key=lambda p: _revision_key(p.parent), reverse=True):
        try:
            p = load_project(path)
            partial = [folder for folder in candidate.snapshots if not all(
                file.is_file() and not file.is_symlink() for file in (
                    folder/'semantic-graph.json', folder/'identity-registry.json',
                    folder/'external-crosswalk.json', folder/'dictionaries/catalog.json'))]
            old = (len(candidate.manifests) - 1 +
                   sum(folder != path.parent for folder in candidate.snapshots if folder not in partial))
            notice = f'{len(partial)} révisions partielles ignorées' if partial else ''
            return Snapshot(path.parent, p.graph, p.registry, p.crosswalk,
                            p.catalog, path), notice, old
        except (OSError, ValueError, KeyError) as exc:
            manifest_errors.append(f'Manifeste diK invalide ({path}): {exc}')
    complete = []
    incomplete = []
    for folder in candidate.snapshots:
        graph, registry = folder/'semantic-graph.json', folder/'identity-registry.json'
        crosswalk, catalog = folder/'external-crosswalk.json', folder/'dictionaries/catalog.json'
        if all(p.is_file() and not p.is_symlink() for p in (graph, registry, crosswalk, catalog)):
            complete.append(Snapshot(folder, graph, registry, crosswalk, catalog))
        else:
            incomplete.append(folder)
    if complete:
        chosen = max(complete, key=lambda s: _revision_key(s.root))
        notes = ([f'{len(incomplete)} révisions partielles ignorées'] if incomplete else [])
        if manifest_errors:
            notes.append(f'{len(manifest_errors)} manifeste(s) invalides ignoré(s)')
        return chosen, '; '.join(notes), len(complete) - 1
    problem = ('Registre v11 sans ensemble graphe/registre/crosswalk/catalogue complet'
               if incomplete else 'Aucun registre KQ/KP v11 exploitable')
    if manifest_errors:
        problem = f'{manifest_errors[0]}; {problem}'
    return None, problem, 0


def _within(path: Path, ancestor: Path) -> bool:
    return path == ancestor or ancestor in path.parents


def _output_directory(dik_root: Path, reports_root: Path | None) -> Path:
    dik_root = dik_root.resolve()
    if not (dik_root/'pyproject.toml').is_file() or not (dik_root/'src/dik/cli.py').is_file():
        raise Kristals14Error(f'Racine de diK invalide: {dik_root}')
    if reports_root is None:
        folder = dik_root/'reports'/'scans_14_langues'
    else:
        folder = reports_root.expanduser()
        if not folder.is_absolute():
            folder = dik_root/folder
    folder = folder.absolute()
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise Kristals14Error('Sortie dans un dossier symbolique refusée')
    folder = folder.resolve()
    if not _within(folder, dik_root):
        raise Kristals14Error('Tous les rapports doivent rester sous le dossier diK')
    return folder


def _writer(path: Path, columns: list[str]):
    stream = path.open('w', encoding='utf-8-sig', newline='')
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', delimiter=';')
    writer.writeheader()
    return stream, writer


def _source(snapshot: Snapshot):
    """Validate exact Framework v11 snapshot before counting a single cell."""
    dictionaries.audit(snapshot.catalog, snapshot.crosswalk, snapshot.registry)
    graph = dictionaries.read_json(snapshot.graph)
    registry = dictionaries.read_json(snapshot.registry)
    catalog = dictionaries.read_json(snapshot.catalog)
    namespace = registry['namespace_id']
    if namespace != graph['namespace_id'] or namespace != catalog['namespace_id']:
        raise Kristals14Error('Namespace divergent entre graphe, registre et catalogue')
    active = framework_coverage._references(graph, registry)
    identities = sorted((r['id'], 'KQ' if r['kind'] == 'entity' else 'KP')
                        for r in registry['identities'] if r['kind'] in ('entity','property'))
    known = {sid for sid, _ in identities}
    languages = {r['tag']:r for r in catalog['languages']}
    reachable = set(TARGET_LOCALES)
    for locale in TARGET_LOCALES:
        if locale in languages:
            reachable.update(languages[locale]['fallbacks'])
    by_locale, layers = _preindexed_layers(SimpleNamespace(catalog=snapshot.catalog),
                                          catalog, known, locales=reachable)
    return namespace, identities, active['KQ'] | active['KP'], languages, by_locale, layers


def _role_order(candidate: Candidate, root: Path) -> tuple:
    """Prefer ordinary repository over byte-identical generated/staged copies."""
    path = candidate.folder.relative_to(root).as_posix().casefold()
    parts = path.split('/')
    bad = ('staging', 'archive', 'archives', 'backup', 'backups',
           'sortie', 'prepared', 'mirror', 'mirrors', 'temp')
    penalty = sum(10 for part in parts if any(word in part for word in bad))
    penalty += sum(5 for part in parts if part.startswith('liens_') or part.startswith('lot-'))
    if '/kristal-public/kristals/' in f'/{path}/':
        penalty -= 3
    return (penalty, len(parts), path)


def _fingerprint(snapshot: Snapshot) -> tuple[str, ...]:
    files = (snapshot.graph, snapshot.registry, snapshot.catalog, snapshot.crosswalk)
    if not all(p.is_file() and not p.is_symlink() for p in files):
        raise Kristals14Error('Fichier v11 manquant ou lien symbolique')
    return tuple(dictionaries.sha256(p) for p in files)


def _verify_copy_layers(snapshot: Snapshot) -> None:
    """Check bytes of every declared layer before accepting the dedup shortcut.

    The same four exact core files passed a prior full audit. Layer files can
    differ by folder, so check every local path and digest again.
    """
    catalog = dictionaries.read_json(snapshot.catalog)
    for language in catalog['languages']:
        for layer in language['layers']:
            layer_path = dictionaries.safe_file(snapshot.catalog.parent, layer['path'])
            if dictionaries.sha256(layer_path) != layer['sha256']:
                raise Kristals14Error(f'Couche modifiée dans une copie: {layer_path}')


def _alternatives(candidate: Candidate, snapshot: Snapshot, *,
                  label: str, namespace: str, identities: list[tuple[str, str]],
                  core_hashes: tuple[str, ...], extra_catalogs=()) -> tuple[list[dict], dict]:
    """Inventory nonselected local catalogs; propose words ONLY with exact proof.

    Alternative layers do not modify canonical coverage or get merged implicitly.
    A matching namespace alone is not a semantic equivalence proof.
    """
    rows = []
    alternatives = collections.defaultdict(list)
    registered = {sid for sid, _ in identities}
    target = set(TARGET_LOCALES)
    for path in sorted(set(candidate.catalogs) | set(extra_catalogs)):
        if path == snapshot.catalog:
            continue
        row = dict(kristal=label, catalogue=str(path), namespace_id='',
                   locales='', etat_preuve='non_verifie', detail='',
                   identites_liees=0, empreinte_catalogue='')
        try:
            if path.is_symlink():
                raise Kristals14Error('Catalogue alternatif symbolique refusé')
            if dictionaries.sha256(path) == core_hashes[2]:
                continue  # Exact same catalog cannot contain new labels.
            catalog = dictionaries.read_json(path)
            dictionaries.check_schema(catalog, 'kristal-dictionary-catalog.schema.json')
            row.update(namespace_id=catalog['namespace_id'],
                       locales=','.join(x['tag'] for x in catalog['languages']),
                       empreinte_catalogue=dictionaries.sha256(path))
            if catalog['namespace_id'] != namespace:
                row.update(etat_preuve='namespace_different',
                           detail='Identités non liées: namespace différent')
            else:
                other_root = path.parent.parent
                other_registry = other_root/'identity-registry.json'
                other_crosswalk = other_root/'external-crosswalk.json'
                if not (other_registry.is_file() and other_crosswalk.is_file() and
                        not other_registry.is_symlink() and not other_crosswalk.is_symlink() and
                        dictionaries.sha256(other_registry) == core_hashes[1] and
                        dictionaries.sha256(other_crosswalk) == core_hashes[3]):
                    row.update(etat_preuve='rattachement_non_prouve', detail=(
                        'Même namespace mais registre/crosswalk non identiques à la révision sélectionnée'))
                else:
                    # Full Framework audit: hashes, source provenance, conflicts and IDs.
                    dictionaries.audit(path, snapshot.crosswalk, snapshot.registry)
                    by_locale, _layers = _preindexed_layers(
                        SimpleNamespace(catalog=path), catalog, registered, locales=target)
                    linked = 0
                    for locale in TARGET_LOCALES:
                        for sid, (priority, word, layer) in by_locale.get(locale, {}).items():
                            alternatives[locale, sid].append((word, str(path), layer))
                            linked += 1
                    row.update(etat_preuve='compatible_audite',
                               detail='Registre et crosswalk identiques, couches auditées',
                               identites_liees=linked)
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
            row.update(etat_preuve='audit_impossible', detail=f'{type(exc).__name__}: {exc}')
        rows.append(row)
    return rows, alternatives


def _proposed_action(state: str, proposals: list[tuple]) -> str:
    if state == 'direct':
        return 'aucune'
    if state == 'repli':
        return 'verifier_traduction_directe'
    if proposals:
        return ('revoir_conflit_de_candidats' if len({p[0] for p in proposals}) > 1
                else 'examiner_couche_alternative_a_integrer')
    return ('rechercher_et_qualifier_dans_dik' if state == 'manquant'
            else 'declarer_et_auditer_dictionnaire')


def scan_kristals14(*, root: str | Path, dik_root: str | Path | None = None,
                    reports_root: str | Path | None = None, min_kristals: int = 1) -> dict:
    """Scan all discoverable local Kristals and publish one coherent audit run.

    Runs without the network. Missing/invalid v11 inputs are 'non_evaluable', NOT
    missing translations. Source manifests/layers are read-only; no modifications.
    """
    source_arg = Path(root).expanduser().absolute()
    if source_arg.is_symlink():
        raise Kristals14Error('Racine source symbolique refusée')
    root = source_arg.resolve()
    if min_kristals < 1:
        raise Kristals14Error('--min-kristals doit être supérieur ou égal à 1')
    if dik_root is None:
        dik_root = Path(__file__).resolve().parents[2]
    dik_root = Path(dik_root).expanduser().resolve()
    reports = _output_directory(dik_root, Path(reports_root) if reports_root else None)
    # Scanning the reports folder would be self-referential, even if excluded by walk.
    if _within(root, reports):
        raise Kristals14Error('La racine des Kristals ne peut pas être le dossier des rapports')
    candidates = discover(root)
    if len(candidates) < min_kristals:
        raise Kristals14Error(f'{len(candidates)} Kristals découverts (< minimum {min_kristals}); aucun rapport publié')
    reports.mkdir(parents=True, exist_ok=True)
    when = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = reports / f'SCAN_{when}'
    i = 2
    while dest.exists():
        dest = reports / f'SCAN_{when}_{i}'
        i += 1
    stage = Path(tempfile.mkdtemp(prefix='.scan14-', dir=reports))
    files = {}
    summary = []
    alerts = []
    tallies = collections.Counter()
    totals = collections.Counter()
    duplicate_labels = collections.Counter(c.folder.name for c in candidates)
    representatives = {}
    # Pre-index all alternate catalogs from byte-identical copies BEFORE scanning.
    # Otherwise a later staging copy could hide a useful, properly proven layer.
    ordered = []
    catalogs_by_fingerprint = collections.defaultdict(set)
    for candidate in sorted(candidates, key=lambda c: _role_order(c, root)):
        snapshot, notice, older = _select(candidate)
        ordered.append((candidate, snapshot, notice, older))
        if snapshot is not None:
            try:
                catalogs_by_fingerprint[_fingerprint(snapshot)].update(candidate.catalogs)
            except (OSError, ValueError, KeyError, TypeError):
                pass
    try:
        for filename, columns in (
            ('matrice_14_langues.csv', DETAIL_COLUMNS),
            ('couverture_kristals_langues.csv', PER_LANGUAGE_COLUMNS),
            ('lacunes_14_langues.csv', DETAIL_COLUMNS),
            ('mots_a_completer_14_langues.csv', DETAIL_COLUMNS),
            ('traductions_a_recuperer_14_langues.csv', RECOVERY_COLUMNS),
            ('catalogues_candidats_14_langues.csv', CANDIDATE_COLUMNS),
            ('copies_exactes_14_langues.csv', ['kristal','dossier','canonique','revision','empreintes_identiques']),
            ('kristals_14_langues.csv', KRISTAL_COLUMNS + ['canonique', 'role_dossier']),
            ('catalogues_14_langues.csv', CATALOG_COLUMNS),
            ('alertes_14_langues.csv', ALERT_COLUMNS),
        ):
            files[filename] = _writer(stage/filename, columns)
        def emit(filename, row):
            files[filename][1].writerow(row)
        with (stage/'scan.log').open('w', encoding='utf-8') as log:
            def event(line):
                log.write(line+'\n')
                log.flush()
            event(f'diK scan14 intelligent v2, UTC={when}, racine={root}, lecture_seule=oui')
            for candidate, snapshot, notice, older in ordered:
                label = (candidate.folder.name if duplicate_labels[candidate.folder.name] == 1
                         else candidate.folder.relative_to(root).as_posix())
                role = 'staging_ou_archive' if _role_order(candidate, root)[0] >= 5 else 'projet'
                row = dict.fromkeys(KRISTAL_COLUMNS + ['canonique', 'role_dossier'], '')
                row.update(kristal=label, dossier=str(candidate.folder), role_dossier=role,
                           revision=str(snapshot.root) if snapshot else '',
                           etat='non_evaluable', cause=notice)
                if snapshot is None:
                    totals['non_evaluables'] += 1
                    msg = notice or 'Aucun projet v11 exploitable'
                    alert = dict(kristal=label, niveau='avertissement', code='SANS_SOURCE_V11',
                                 detail=msg, chemin=str(candidate.folder))
                    alerts.append(alert); emit('alertes_14_langues.csv', alert)
                    event(f'{label}: NON_EVALUABLE — {msg}')
                    for catalog_path in candidate.catalogs:
                        c_row = dict(kristal=label, catalogue=str(catalog_path), namespace_id='',
                                     locales='', etat_preuve='source_v11_absente',
                                     detail='Catalogue repéré, mais aucun registre v11 exploitable',
                                     identites_liees=0, empreinte_catalogue='')
                        try:
                            if catalog_path.is_symlink():
                                raise Kristals14Error('Catalogue symbolique refusé')
                            data = dictionaries.read_json(catalog_path)
                            dictionaries.check_schema(data, 'kristal-dictionary-catalog.schema.json')
                            c_row.update(namespace_id=data['namespace_id'],
                                         locales=','.join(x['tag'] for x in data['languages']),
                                         empreinte_catalogue=dictionaries.sha256(catalog_path))
                        except (OSError, ValueError, KeyError, TypeError) as exc:
                            c_row.update(etat_preuve='structure_invalide', detail=str(exc))
                        emit('catalogues_candidats_14_langues.csv', c_row)
                        totals['catalogues_sans_source_v11'] += 1
                else:
                    if older:
                        alert = dict(kristal=label, niveau='information', code='REVISIONS_IGNORES',
                                     detail=f'{older} ancienne(s) révision(s) complète(s) ignorée(s)',
                                     chemin=str(snapshot.root))
                        alerts.append(alert); emit('alertes_14_langues.csv', alert)
                    if notice:
                        alert = dict(kristal=label, niveau='avertissement', code='REVISIONS_PARTIELLES',
                                     detail=notice, chemin=str(candidate.folder))
                        alerts.append(alert); emit('alertes_14_langues.csv', alert)
                    try:
                        hashes = _fingerprint(snapshot)
                        original = representatives.get(hashes)
                        if original is not None:
                            _verify_copy_layers(snapshot)
                            row.update(etat='copie_exacte', cause='', canonique=original['kristal'],
                                       graphe_sha256=hashes[0], registre_sha256=hashes[1],
                                       catalogue_sha256=hashes[2], crosswalk_sha256=hashes[3],
                                       namespace_id=original['namespace_id'],
                                       identites_KQ_KP=original['identites_KQ_KP'],
                                       references_graphe=original['references_graphe'],
                                       langues_configurees=original['langues_configurees'],
                                       cellules_directes=original['cellules_directes'],
                                       cellules_repli=original['cellules_repli'],
                                       cellules_manquantes=original['cellules_manquantes'],
                                       cellules_non_configurees=original['cellules_non_configurees'])
                            totals['copies_exactes'] += 1
                            emit('copies_exactes_14_langues.csv', dict(
                                kristal=label, dossier=str(candidate.folder),
                                canonique=original['kristal'], revision=str(snapshot.root),
                                empreintes_identiques='4 fichiers v11 + couches SHA-256'))
                            event(f'{label}: COPIE_EXACTE de {original["kristal"]}')
                        else:
                            source_info = _source(snapshot)
                    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
                        row.update(etat='non_evaluable', cause=f'{type(exc).__name__}: {exc}')
                        totals['non_evaluables'] += 1
                        alert = dict(kristal=label, niveau='erreur', code='AUDIT_V11_ECHOUE',
                                     detail=row['cause'], chemin=str(snapshot.root))
                        alerts.append(alert); emit('alertes_14_langues.csv',alert)
                        event(f'{label}: NON_EVALUABLE — {row["cause"]}')
                    else:
                        if row['etat'] != 'copie_exacte':
                            ns, identities, active, languages, layers_index, layers = source_info
                            row.update(etat='evalue', namespace_id=ns, canonique=label,
                                       graphe_sha256=hashes[0], registre_sha256=hashes[1],
                                       catalogue_sha256=hashes[2], crosswalk_sha256=hashes[3],
                                       identites_KQ_KP=len(identities), references_graphe=len(active),
                                       langues_configurees=','.join(sorted(languages)), cause='')
                            catalog_rows, proposals = _alternatives(
                                candidate, snapshot, label=label, namespace=ns,
                                identities=identities, core_hashes=hashes,
                                extra_catalogs=catalogs_by_fingerprint.get(hashes, ()))
                            for catalog_row in catalog_rows:
                                emit('catalogues_candidats_14_langues.csv', catalog_row)
                                totals['catalogues_alternatifs_reperes'] += 1
                                if catalog_row['etat_preuve'] == 'compatible_audite':
                                    totals['catalogues_alternatifs_valides'] += 1
                            per = collections.Counter()
                            for layer in layers:
                                emit('catalogues_14_langues.csv', dict(kristal=label,
                                      revision=str(snapshot.root), namespace_id=ns, **layer))
                            for locale in TARGET_LOCALES:
                                locale_per = collections.Counter()
                                for sid, kind in identities:
                                    state, word, source_locale, source_layer = _resolve(
                                        locale, sid, languages, layers_index)
                                    matches = proposals.get((locale, sid), []) if state not in ('direct', 'repli') else []
                                    action = _proposed_action(state, matches)
                                    item = {
                                        'kristal': label, 'namespace_id': ns, 'semantic_id':sid,
                                        'famille':kind, 'dans_graphe':'oui' if sid in active else 'non',
                                        'locale':locale, 'etat':state, 'libelle_resolu':word,
                                        'langue_source':source_locale, 'preuve_couche':source_layer,
                                        'statut_preuve':'catalogue_selectionne_audite', 'action':action,
                                        'revision':str(snapshot.root),
                                    }
                                    emit('matrice_14_langues.csv', item)
                                    if state != 'direct':
                                        emit('lacunes_14_langues.csv',item)
                                    if state == 'manquant' and not matches:
                                        emit('mots_a_completer_14_langues.csv', item)
                                        totals['mots_a_completer_audites'] += 1
                                    if matches:
                                        totals['cellules_avec_candidat'] += 1
                                        for term, candidate_path, candidate_layer in matches:
                                            emit('traductions_a_recuperer_14_langues.csv', dict(
                                                kristal=label, namespace_id=ns, semantic_id=sid,
                                                famille=kind, locale=locale, libelle_candidat=term,
                                                catalogue_alternatif=candidate_path,
                                                preuve_couche=candidate_layer,
                                                etat_preuve=('conflit_a_revoir' if len({p[0] for p in matches}) > 1
                                                             else 'compatible_audite_mais_non_fusionne'),
                                                action='valider_puis_integrer_explicitement'))
                                    totals[state] += 1
                                    tallies[locale, state] += 1
                                    per[state] += 1
                                    locale_per[state] += 1
                                emit('couverture_kristals_langues.csv', {
                                    'kristal':label, 'revision':str(snapshot.root),
                                    'namespace_id':ns, 'locale':locale, 'etat_kristal':'evalue',
                                    'identites_KQ_KP':len(identities),
                                    **{key:locale_per[key] for key in (
                                        'direct','repli','manquant','langue_non_configuree')},
                                    'pourcentage_direct':round(100*locale_per['direct']/len(identities),2)
                                        if identities else '',
                                    'complet_direct':('oui' if locale_per['direct']==len(identities)
                                                     else 'non') if identities else 'non_applicable',
                                })
                            row.update(cellules_directes=per['direct'], cellules_repli=per['repli'],
                                       cellules_manquantes=per['manquant'],
                                       cellules_non_configurees=per['langue_non_configuree'])
                            representatives[hashes] = dict(row)
                            totals['evaluables'] += 1
                            totals['identites_KQ_KP_par_kristal'] += len(identities)
                            totals['couches_lues_14_langues'] += len(layers)
                            totals['couches_auditees_total'] += sum(len(x['layers']) for x in languages.values())
                            event(f'{label}: EVALUE UNIQUE — {len(identities)} KQ/KP, {per["direct"]} direct, '
                                  f'{per["repli"]} repli, {per["manquant"]} manquant, '
                                  f'{per["langue_non_configuree"]} langue_non_configuree')
                if row['etat'] in ('non_evaluable', 'copie_exacte'):
                    for locale in TARGET_LOCALES:
                        emit('couverture_kristals_langues.csv', {
                            'kristal':label, 'revision':row['revision'],
                            'namespace_id':row['namespace_id'], 'locale':locale,
                            'etat_kristal':row['etat'],
                            'cause':row['cause'] if row['etat']=='non_evaluable' else
                                f'Copie exacte de {row["canonique"]}; exclue des totaux',
                        })
                summary.append(row)
                emit('kristals_14_langues.csv', row)
            event('fin du scan')
        for stream, _ in files.values():
            stream.close()
        files.clear()
        result = {
            'schema':'dik.coverage.kristals14/2.0', 'etat':(
                'COMPLET_SUR_SOURCES_EVALUABLES' if not totals['non_evaluables'] else 'PARTIEL'),
            'mode':'LECTURE_SEULE', 'reseau_utilise':False,
            'date_utc':when, 'racine_scannee':str(root), 'dossier_rapports':str(dest),
            'locales_cibles':list(TARGET_LOCALES),
            'totaux':{
                'kristals_decouverts':len(candidates),
                'kristals_evalues':totals['evaluables'],
                'kristals_non_evaluables':totals['non_evaluables'],
                'copies_exactes':totals['copies_exactes'],
                'identites_KQ_KP_par_kristal':totals['identites_KQ_KP_par_kristal'],
                'verifications_linguistiques':sum(totals[x] for x in (
                    'direct','repli','manquant','langue_non_configuree')),
                'direct':totals['direct'], 'repli':totals['repli'],
                'manquant':totals['manquant'], 'langue_non_configuree':totals['langue_non_configuree'],
                'mots_a_completer_audites':totals['mots_a_completer_audites'],
                'cellules_avec_candidat':totals['cellules_avec_candidat'],
                'catalogues_alternatifs_reperes':totals['catalogues_alternatifs_reperes'],
                'catalogues_alternatifs_valides':totals['catalogues_alternatifs_valides'],
                'catalogues_sans_source_v11':totals['catalogues_sans_source_v11'],
                'couches_auditees_total':totals['couches_auditees_total'],
                'couches_lues_14_langues':totals['couches_lues_14_langues'],
            },
            'par_langue':[
                {'locale':locale, **{state:tallies[locale,state] for state in (
                    'direct','repli','manquant','langue_non_configuree')}}
                for locale in TARGET_LOCALES
            ],
            'kristals':summary,
            'alertes_nombre':len(alerts),
            'limites':[
                'Totaux calculés sur les ensembles v11 distincts; copies byte-identiques exclues.',
                'Un ensemble est identique si ses quatre fichiers v11 ont les mêmes SHA-256 et les couches ont été vérifiées.',
                'Une révision v11 complète est sélectionnée par Kristal; les historiques ne sont pas additionnés.',
                'Les KQ/KP sont comptés par Kristal (namespaces distincts jamais fusionnés).',
                'Les Kristals sans registre v11 valide sont non évaluables et exclus des taux.',
                'Manquant signifie absent des couches du catalogue sélectionné audité, pas de tous les dictionnaires du disque.',
                'Un dictionnaire externe ne devient candidat que si registre et crosswalk sont identiques et si audit Framework réussi.',
                'Les dictionnaires alternatifs ne sont jamais fusionnés ni appliqués automatiquement.',
                'Ce scan mesure les libellés canoniquement liés à des KQ/KP, pas tous les mots libres de chaque dépôt.',
                'Ni qualité linguistique, ni exhaustivité lexicale mondiale, ni traduction automatique certifiées.',
            ],
        }
        (stage/'rapport.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        stage.rename(dest)
        return result
    finally:
        for stream, _ in files.values():
            stream.close()
        if stage.exists():
            shutil.rmtree(stage)
