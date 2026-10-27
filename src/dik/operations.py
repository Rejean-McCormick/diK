"""diK local operations against pinned Framework v11 draft.3 contracts.

All canonical Kristals and dictionaries are read-only in these operations.
Imports publish NEW isolated snapshots; no existing snapshots are overwritten.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from . import FRAMEWORK_CONTRACT, __version__
from ._framework import dictionaries as ref
from ._framework import coverage as cov


class DiKError(ValueError):
    """User-visible invalid project or operation."""


@dataclass(frozen=True)
class Project:
    manifest: Path
    graph: Path
    registry: Path
    crosswalk: Path
    catalog: Path


def _project_file(root: Path, value: str) -> Path:
    # Project references never escape its root, even via symlinks.
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise DiKError(f"Chemin du projet invalide : {value!r}")
    return ref.safe_file(root, value)


def load_project(path: str | Path) -> Project:
    manifest = Path(path).resolve()
    data = ref.read_json(manifest)
    if not isinstance(data, dict) or set(data) != {
        'format_version', 'framework_contract', 'graph', 'registry', 'crosswalk', 'catalog'
    }:
        raise DiKError('Manifeste diK invalide (clés manquantes ou supplémentaires)')
    if data['format_version'] != '0.1' or data['framework_contract'] != FRAMEWORK_CONTRACT:
        raise DiKError('Version de projet ou contrat Framework non supporté')
    paths = {k: _project_file(manifest.parent, data[k]) for k in ('graph', 'registry', 'crosswalk', 'catalog')}
    return Project(manifest=manifest, **paths)


def inspect(project: Project) -> dict:
    """Validate full semantic references, dictionary layers, and crosswalk integrity."""
    graph = ref.read_json(project.graph)
    registry = ref.read_json(project.registry)
    crosswalk = ref.read_json(project.crosswalk)
    catalog = ref.read_json(project.catalog)
    refs = cov._references(graph, registry)
    ref.check_schema(crosswalk, 'kristal-external-crosswalk.schema.json')
    audit = ref.audit(project.catalog, project.crosswalk, project.registry)
    # Do not treat a stale or cross-namespace mapping as belonging to this project.
    known = {x['id']: x['kind'] for x in registry['identities']}
    for m in crosswalk['mappings']:
        if m['local_ref']['namespace_id'] != graph['namespace_id']:
            continue
        if known.get(m['local_ref']['id']) not in ('entity', 'property'):
            raise DiKError(f"Correspondance vers identité non enregistrée: {m['local_ref']['id']}")
        if m['status'] == 'accepted':
            if any(known.get(proof) != 'source' for proof in m['review']['evidence_refs']):
                raise DiKError(f"Preuve KS absente du registre: {m['mapping_id']}")
    if catalog['namespace_id'] != graph['namespace_id']:
        raise DiKError('Namespace du catalogue différent du graphe')
    accepted, _ = ref.accepted_exact(crosswalk, graph['namespace_id'])
    return {
        'dik_version': __version__,
        'framework_contract': FRAMEWORK_CONTRACT,
        'manifest': str(project.manifest),
        'namespace_id': graph['namespace_id'],
        'graph_id': graph['graph_id'],
        'graph_sha256': ref.sha256(project.graph),
        'catalog_id': catalog['catalog_id'],
        'catalog_sha256': ref.sha256(project.catalog),
        'semantic_reference_count': {k: len(v) for k, v in refs.items()},
        'assertions': len(graph['assertions']),
        'sources': len(graph['sources']),
        'catalog_locales': [x['tag'] for x in catalog['languages']],
        'lexical_records_by_locale': audit['records_by_locale'],
        'accepted_exact_wikidata_mappings': len(accepted),
        'safe_to_migrate_legacy': False,
    }


def dictionaries_audit(project: Project) -> dict:
    return ref.audit(project.catalog, project.crosswalk, project.registry)


def dictionary_resolve(project: Project, semantic_id: str, locale: str) -> dict:
    ref.audit(project.catalog, project.crosswalk, project.registry)
    registry = ref.read_json(project.registry)
    kinds = {e['id']: e['kind'] for e in registry['identities']}
    if semantic_id not in kinds or kinds[semantic_id] not in ('entity', 'property'):
        raise DiKError(f'Identifiant KQ/KP non enregistré: {semantic_id}')
    return ref.resolve(project.catalog, semantic_id, locale)


def coverage_report(project: Project, locales: list[str] | None = None, sample_limit: int = 25) -> dict:
    return cov.make_report(graph_path=project.graph, catalog_path=project.catalog,
                           registry_path=project.registry, crosswalk_path=project.crosswalk,
                           locales=locales, missing_sample_limit=sample_limit)


def import_wikidata_local(*, dump: Path, crosswalk: Path, registry: Path, namespace: str,
                           snapshot: str, locales: list[str], output: Path) -> dict:
    """Stage a streamed local import, verify it, atomically install a new directory.

    Imported labels are keyed only through accepted exact Q↔KQ / P↔KP mappings.
    No crosswalk, registry, source dump, existing dictionary or Kristal is modified.
    """
    if not snapshot or not re.fullmatch(r'[A-Za-z0-9._-]+', snapshot) or snapshot in {'.', '..'}:
        raise DiKError('Identifiant de snapshot invalide')
    output = Path(output).absolute()
    if output.exists():
        raise DiKError(f'Le snapshot existe déjà, refus de remplacer: {output}')
    if not Path(dump).is_file():
        raise DiKError('Dump Wikidata local introuvable')
    reg = ref.read_json(registry)
    ref.check_schema(reg, 'kristal-identity-registry.schema.json')
    if reg['namespace_id'] != namespace:
        raise DiKError('Namespace non conforme au registre')
    mappings = ref.read_json(crosswalk)
    accepted, _ = ref.accepted_exact(mappings, namespace)
    known = {i['id']:i['kind'] for i in reg['identities']}
    for m in mappings['mappings']:
        if m['status'] == 'accepted' and m['local_ref']['namespace_id'] == namespace:
            if any(known.get(proof) != 'source' for proof in m['review']['evidence_refs']):
                raise DiKError(f"Preuve KS absente du registre: {m['mapping_id']}")
    for external, local in accepted.items():
        if known.get(local) != ('entity' if external.startswith('Q') else 'property'):
            raise DiKError(f'Correspondance Wikidata orpheline: {local}')
    if not locales or len(locales) != len(set(locales)) or any(not loc for loc in locales):
        raise DiKError('Liste de langues manquante ou dupliquée')
    for locale in locales:
        ref.check_locale(locale)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.dik-stage-', dir=output.parent))
    try:
        opts = SimpleNamespace(dump=str(dump), crosswalk=str(crosswalk), namespace=namespace,
                               snapshot=snapshot, languages=','.join(locales), output=str(stage))
        result = ref.import_local(opts)
        ref.audit(stage / 'catalog.json', crosswalk, registry)
        # Atomic when staging/output are on the same filesystem. Do not overwrite.
        if output.exists():
            raise DiKError(f'Le snapshot existe déjà: {output}')
        os.rename(stage, output)
        result['catalog'] = str(output / 'catalog.json')
        result['source_dump_sha256'] = ref.sha256(dump)
        result['source_dump_bytes'] = Path(dump).stat().st_size
        result['framework_contract'] = FRAMEWORK_CONTRACT
        result['warning'] = 'Seules les correspondances exactMatch acceptées ont été importées.'
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def write_new(path: str | Path, content: str) -> None:
    """Create an output file exclusively; never overwrite a report or data file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as dst:
        dst.write(content)


def serialize_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'
