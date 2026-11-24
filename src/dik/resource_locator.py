"""diK local source manager: locate, fingerprint and point, never translate.

Discovery is metadata-only. Every reference is inactive until its adapter
independently establishes canonical identity, integrity, rights and policy.
No network, source mutations, symlink traversal or implicit GF->KQ mappings.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from .kristals14 import SKIP_DIRS

REGISTRY_PROFILE = 'dik.local-resource-registry/1.0'
ROOTS = (
    'Kristal/kristal-public/kristals',
    'Kristal/locals',
    'Grammatical-Framework/GF_Lexicons_Archive',
    'Grammatical-Framework/gf-rgl',
    'Grammatical-Framework/gf-wikidata_repos_source',
    'Grammatical-Framework/GF_Wordbench',
    'Grammatical-Framework/ars-magna-defluens',
    'Grammatical-Framework/SemantiK_Architect_GF_Source',
    'Grammatical-Framework/gf-core',
    'Grammatical-Framework/gf-3.12-windows',
    'SemantiK_Architect/SemantiK_Architect',
    'Konstellation/Konstellation',
)
COLUMNS = ('source_id', 'kind', 'state', 'path', 'size_bytes', 'sha256',
           'root', 'reason', 'allowed_for_resolution')


def _unsafe(path: Path) -> bool:
    """Reject symlinks and Windows junctions; never dereference them."""
    return path.is_symlink() or bool(getattr(path, 'is_junction', lambda: False)())


def _file_kind(path: Path) -> str | None:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    if name == 'catalog.json' and path.parent.name.lower() == 'dictionaries':
        return 'framework_v11_catalog'
    if name == 'external-crosswalk.json':
        return 'framework_v11_crosswalk'
    if name == 'identity-registry.json':
        return 'framework_v11_registry'
    if name == 'qid-lexicon.jsonl':
        return 'wikidata_qid_lexicon_candidate'
    if name in ('latest-all.json.bz2', 'latest-all.json.gz', 'latest-all.json',
                'wikidata-all.jsonl', 'wikidata-all.jsonl.gz', 'wikidata-all.jsonl.bz2'):
        return 'wikidata_qp_dump_candidate'
    if name.endswith(('.jsonl','.jsonl.gz','.jsonl.bz2')) and ('wikidata' in parts or 'gf-wikidata-tools' in parts):
        return 'wikidata_thematic_candidate'
    if name.endswith('.gf'):
        if re.match(r'^(dict|lexicon|irreg)', name):
            return 'gf_lexicon_candidate'
        if 'gf-rgl' in parts:
            return 'gf_rgl_candidate'
        return 'gf_grammar_candidate'
    if name.endswith('.pgf'):
        return 'gf_pgf_candidate'
    if name == 'manifest.json' and ('gf' in parts or 'grammatical-framework' in parts):
        return 'gf_manifest_candidate'
    return None


def _fingerprint(path: Path, limit: int) -> tuple[str | None, str]:
    size = path.stat().st_size
    if size > limit:
        return None, 'taille_superieure_limite_hash; chemin_reference_non_certifie'
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest(), 'empreinte_locale; provenance_et_licence_non_verifiees'


def _roots(base: Path, extra: tuple[Path, ...]) -> tuple[list[Path], list[dict]]:
    found, missing = [], []
    candidates = [base / relative for relative in ROOTS]
    # Fixtures/standalone workspaces and explicit extra roots are supported.
    if not any(p.is_dir() for p in candidates):
        candidates.insert(0, base)
    candidates.extend(extra)
    for candidate in candidates:
        candidate = candidate.absolute()
        if _unsafe(candidate):
            missing.append({'path': str(candidate), 'reason': 'lien_ou_jonction_refuse'}); continue
        if not candidate.is_dir():
            missing.append({'path': str(candidate), 'reason': 'absent'}); continue
        if candidate not in found:
            found.append(candidate)
    return found, missing


def discover_resources(*, sources_root: str | Path, extra_roots: tuple[str | Path, ...] = (),
                       max_files: int = 20000, max_hash_bytes: int = 64 * 1024 * 1024,
                       max_depth: int = 18) -> dict:
    """Return a bounded, source-only inventory; no files are written."""
    base = Path(sources_root).expanduser().absolute()
    if _unsafe(base) or not base.is_dir():
        raise ValueError(f'Racine source absente ou lien refuse: {base}')
    if not 1 <= max_files <= 1_000_000 or not 0 <= max_hash_bytes <= 2**45 or not 1 <= max_depth <= 80:
        raise ValueError('Budget de decouverte invalide')
    roots, unavailable = _roots(base, tuple(Path(x).expanduser() for x in extra_roots))
    records, seen_paths, exceeded = [], set(), False
    for root in roots:
        for current, dirs, files in os.walk(root, followlinks=False):
            here = Path(current)
            depth = len(here.relative_to(root).parts)
            dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP_DIRS and
                             depth < max_depth and not _unsafe(here / d))
            for filename in sorted(files):
                path = here / filename
                kind = _file_kind(path)
                if not kind or _unsafe(path) or not path.is_file():
                    continue
                absolute = str(path.absolute())
                if absolute in seen_paths:
                    continue
                seen_paths.add(absolute)
                if len(records) >= max_files:
                    exceeded = True; break
                try:
                    stat = path.stat()
                    sha, reason = _fingerprint(path, max_hash_bytes)
                    state = 'fingerprinted' if sha else 'found_unhashed'
                except (OSError, PermissionError) as exc:
                    stat = None
                    sha, state, reason = None, 'unreadable', type(exc).__name__
                # A path-based stable ID points to the location. SHA detects replacement.
                sid = 'local-' + hashlib.sha256(absolute.casefold().encode('utf-8')).hexdigest()[:24]
                records.append({'source_id': sid, 'kind': kind, 'state': state,
                                'path': absolute, 'root': str(root),
                                'size_bytes': stat.st_size if stat else None, 'sha256': sha,
                                'reason': reason, 'allowed_for_resolution': False})
            if exceeded:
                break
        if exceeded:
            break
    counts = Counter(r['kind'] for r in records)
    return {'profile': REGISTRY_PROFILE, 'source_root': str(base),
            'roots_searched': [str(root) for root in roots],
            'roots_unavailable': unavailable, 'sources': records,
            'summary': {'sources_found': len(records), 'by_kind': dict(sorted(counts.items())),
                        'truncated': exceeded, 'max_files': max_files,
                        'max_hash_bytes': max_hash_bytes},
            'policy': {'offline': True, 'read_only_sources': True,
                       'translation_between_languages': False,
                       'discovery_grants_lexical_authority': False}}


def _report_dir(dik_root: Path, reports_root: str | Path | None) -> Path:
    dik_root = dik_root.expanduser().absolute()
    if not dik_root.is_dir() or _unsafe(dik_root):
        raise ValueError(f'Depot diK invalide: {dik_root}')
    relative = Path(reports_root) if reports_root else Path('reports/resources')
    if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != 'reports':
        raise ValueError('Le registre doit rester dans un sous-dossier de diK/reports')
    target = dik_root / relative
    cursor = dik_root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.exists() and (_unsafe(cursor) or not cursor.is_dir()):
            raise ValueError('Dossier de rapport dangereux ou invalide')
    return target


def save_registry(registry: dict, *, dik_root: str | Path,
                  reports_root: str | Path | None = None) -> dict:
    """Write dated immutable inventory and an atomic latest pointer under diK/reports."""
    if registry.get('profile') != REGISTRY_PROFILE or not isinstance(registry.get('sources'), list):
        raise ValueError('Registre diK invalide')
    folder = _report_dir(Path(dik_root), reports_root)
    folder.mkdir(parents=True, exist_ok=True)
    when = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = folder / f'DISCOVERY_{when}'
    suffix = 2
    while run.exists():
        run = folder / f'DISCOVERY_{when}_{suffix}'
        suffix += 1
    stage = Path(tempfile.mkdtemp(prefix='.discovery-', dir=folder))
    try:
        payload = dict(registry, generated_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        document = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'
        (stage / 'resource-registry.json').write_text(document, encoding='utf-8')
        with (stage / 'resources-found.csv').open('w', encoding='utf-8', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=COLUMNS, extrasaction='ignore')
            writer.writeheader()
            for row in payload['sources']:
                safe = {k: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v
                        for k, v in row.items()}
                writer.writerow(safe)
        (stage / 'scan.log').write_text(f"diK source discovery offline\nrecords={len(payload['sources'])}\n"
                                        f"truncated={payload['summary']['truncated']}\n", encoding='utf-8')
        stage.rename(run)
        # Latest is itself a registry document, not an executable shortcut.
        latest = folder / 'resource-registry-latest.json'
        temporary = folder / f'.latest-{os.getpid()}-{run.name}.json'
        temporary.write_text(document, encoding='utf-8')
        temporary.replace(latest)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return {'etat': 'inventory_only', 'sources': len(registry['sources']),
            'truncated': registry['summary']['truncated'], 'rapport': str(run),
            'registry': str(run / 'resource-registry.json'), 'latest_registry': str(latest)}


def load_registry(path: str | Path, *, verify_paths: bool = True) -> dict:
    path = Path(path).expanduser().absolute()
    if _unsafe(path) or not path.is_file() or path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError('Registre absent, symbolique ou trop volumineux')
    document = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(document, dict) or document.get('profile') != REGISTRY_PROFILE or not isinstance(document.get('sources'), list):
        raise ValueError('Format de registre diK inconnu')
    seen = set()
    for source in document['sources']:
        if not isinstance(source, dict) or not all(isinstance(source.get(k), str) for k in ('source_id','kind','path','root')):
            raise ValueError('Entree de registre invalide')
        if source['source_id'] in seen:
            raise ValueError('source_id duplique')
        seen.add(source['source_id'])
        if verify_paths:
            p = Path(source['path'])
            root = Path(source['root'])
            if not p.is_absolute() or not root.is_absolute() or _unsafe(p) or not p.is_file():
                continue
            # Never admit paths outside the declared root, even if a forged registry lists them.
            if not p.is_relative_to(root):
                raise ValueError('Chemin en dehors de sa racine autorisee')
            if any(_unsafe(parent) for parent in (p, *list(p.parents)[:len(p.relative_to(root).parts)])):
                raise ValueError('Lien ou jonction dans le chemin enregistre')
    return document


def validate_registry(path: str | Path, *, max_hash_bytes: int = 64 * 1024 * 1024) -> dict:
    registry = load_registry(path)
    counts = Counter()
    for source in registry['sources']:
        p = Path(source['path'])
        if _unsafe(p) or not p.is_file():
            counts['unavailable'] += 1; continue
        if source.get('sha256'):
            try:
                sha, _ = _fingerprint(p, max_hash_bytes)
                counts['unchanged' if sha == source['sha256'] else 'modified_or_unverified'] += 1
            except OSError:
                counts['unavailable'] += 1
        else:
            counts['not_fingerprinted'] += 1
    # A successful verification must not be mistaken for an all-clear when
    # previously fingerprinted sources disappeared or changed. Unhashed files
    # remain visible as incomplete evidence, not verified integrity.
    status = ('STALE' if counts['unavailable'] or counts['modified_or_unverified']
              else 'INCOMPLETE' if counts['not_fingerprinted']
              else 'VERIFIED')
    return {'registry': str(path), 'counts': dict(counts), 'total': len(registry['sources']),
            'status': status, 'resolved_kq_kp': 0,
            'gf_semantic_mapping_automatic': False}


def catalog_references(registry: dict) -> list[Path]:
    """Get catalog pointers for a SECOND, independent, canonical v11 audit."""
    result = []
    for entry in registry['sources']:
        if entry.get('kind') != 'framework_v11_catalog':
            continue
        p = Path(entry['path'])
        if _unsafe(p) or not p.is_file() or not p.is_relative_to(Path(entry['root'])):
            continue
        if entry.get('sha256') and _fingerprint(p, 25_000_000)[0] != entry['sha256']:
            # A registry pointer may have become stale; never silently replace.
            raise ValueError(f'Catalogue modifie depuis sa decouverte: {p}')
        result.append(p)
    return result
