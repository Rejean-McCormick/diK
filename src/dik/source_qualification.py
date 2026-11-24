"""V5 source qualification and conservative Wikidata Q-ID observations.

Discovery is a pointer catalogue, never permission to use arbitrary words as
semantic forms. This module verifies pointers, records lexical readiness, and
can observe explicit Q/P labels only for pre-approved KQ/KP crosswalks.
It never rewrites input resources or grants publication authority.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from .resource_locator import _report_dir, _unsafe, load_registry

_QP = re.compile(r'^[QP][1-9][0-9]*$')
# This is deliberately NOT a Wikidata L/S/F <-> entity bridge.
_LABEL_KEYS = ('labels',)


def _verified_pointer(record: dict, *, max_bytes: int = 64 * 1024 * 1024):
    """Return (path, reason) after validating full ancestry and SHA-256."""
    path, root = Path(record['path']), Path(record['root'])
    if not path.is_absolute() or not root.is_absolute() or not path.is_relative_to(root):
        return None, 'hors_racine'
    if any(_unsafe(p) for p in (path, *(p for p in path.parents if p == root or p.is_relative_to(root)))):
        return None, 'lien_ou_jonction'
    if not path.is_file():
        return None, 'introuvable'
    if record.get('size_bytes') is not None and path.stat().st_size != record['size_bytes']:
        return None, 'taille_modifiee'
    expected = record.get('sha256')
    if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected):
        return None, 'empreinte_absente'
    if path.stat().st_size > max_bytes:
        return None, 'depasse_limite_verification'
    digest = hashlib.sha256()
    with path.open('rb') as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != expected.lower():
        return None, 'empreinte_modifiee'
    return path, 'empreinte_identique'


def _qid_lexicon_profile(path: Path, *, wanted: set[str] | None,
                         locales: tuple[str, ...], max_rows: int = 250000):
    """Observe exact Q/P labels from two explicit JSONL layouts, not translations.

    Supported:
      {"qid": "Q123", "labels": {"fr": "..."}}
      {"Q123": {"fr": "...", "en": "..."}}
    Language keys must match `locales` exactly. No `no` -> `nb`/`nn` fallback.
    Labels are ALWAYS non-publishable candidates until separate source review.
    """
    found: dict[tuple[str, str], str] = {}
    conflicted: set[tuple[str, str]] = set()
    counters = collections.Counter()
    observed_keys = collections.Counter()
    observed_locales = set()
    with path.open('r', encoding='utf-8-sig') as fp:
        for line_no, line in enumerate(fp, 1):
            if line_no > max_rows:
                counters['truncated'] += 1
                break
            if not line.strip():
                continue
            counters['rows'] += 1
            if len(line) > 2_000_000:
                counters['oversized_row'] += 1
                continue
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                counters['invalid_json'] += 1
                continue
            if not isinstance(row, dict):
                counters['invalid_structure'] += 1
                continue
            observed_keys.update(row.keys())
            qid = row.get('qid', row.get('id'))
            labels = row.get('labels')
            form = 'qid_labels'
            if qid is None and 'qid' not in row and 'id' not in row and len(row) == 1:
                key, value = next(iter(row.items()))
                if isinstance(key, str) and _QP.fullmatch(key) and isinstance(value, dict):
                    qid, labels, form = key, value, 'qp_keyed_locales'
            if not isinstance(qid, str) or not _QP.fullmatch(qid):
                counters['no_qp_id'] += 1
                continue
            counters['rows_with_qp_id'] += 1
            if not isinstance(labels, dict):
                counters['no_explicit_labels'] += 1
                continue
            counters['schema_' + form] += 1
            for loc, val in labels.items():
                if isinstance(loc, str) and isinstance(val, str) and val.strip():
                    observed_locales.add(loc)
                elif isinstance(loc, str) and isinstance(val, dict) and isinstance(val.get('value'), str) and val['value'].strip():
                    observed_locales.add(loc)
            if wanted is not None and qid not in wanted:
                continue
            counters['rows_matching_requested_qp'] += 1
            for locale in locales:
                term = labels.get(locale)
                if isinstance(term, dict):
                    term = term.get('value')
                if not isinstance(term, str) or not term.strip() or len(term) > 10000:
                    continue
                key = (qid, locale)
                term = term.strip()
                if key in found and found[key] != term:
                    conflicted.add(key)
                elif key not in conflicted:
                    found[key] = term
    for key in conflicted:
        found.pop(key, None)
    counters['rows_matching_requested_qp'] += 0
    counters['schema_qid_labels'] += 0
    counters['schema_qp_keyed_locales'] += 0
    counters['explicit_labels_accepted_for_observation'] = len(found)
    counters['conflicting_qp_locale'] = len(conflicted)
    return found, {
        'statistics': dict(counters),
        'observed_keys': dict(observed_keys.most_common(30)),
        'locales_seen': sorted(observed_locales),
        'schema_known': bool(counters['schema_qid_labels'] or counters['schema_qp_keyed_locales']),
        'candidate_only': True,
    }


def observe_registered_qid_lexicon(registry: dict, *, wanted: set[str],
                                   locales: tuple[str, ...]):
    """Return explicit labels for already-approved Q/P IDs, as CANDIDATES only."""
    matches = [row for row in registry['sources'] if row['kind'] == 'wikidata_qid_lexicon_candidate']
    if len(matches) != 1:
        return {}, {'status': 'absent_or_ambiguous', 'candidates': len(matches), 'candidate_only': True}
    record = matches[0]
    try:
        path, reason = _verified_pointer(record, max_bytes=16 * 1024 * 1024)
        if path is None:
            return {}, {'status': reason, 'source_id': record['source_id'], 'candidate_only': True}
        values, details = _qid_lexicon_profile(path, wanted=wanted, locales=locales)
    except (OSError, UnicodeError, ValueError) as exc:
        return {}, {'status': 'unreadable_or_unsupported', 'detail': type(exc).__name__,
                    'source_id': record['source_id'], 'candidate_only': True}
    return values, {'status': 'observed_candidate_only', 'source_id': record['source_id'],
                    'path': str(path), 'sha256': record['sha256'], **details}


def qualify_resources(*, registry_file: str | Path, dik_root: str | Path,
                      reports_root: str | Path = 'reports/resources',
                      max_hash_bytes: int = 64 * 1024 * 1024) -> dict:
    """Create a complete, read-only triage of discovered resources.

    All rows get a reason and a next step. Nothing gets published/activated.
    The registry is local and may contain sensitive paths: reports remain local.
    """
    registry = load_registry(registry_file)
    if registry.get('summary', {}).get('truncated'):
        truncated = True
    else:
        truncated = False
    folder = _report_dir(Path(dik_root), reports_root)
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest = folder / f'QUALIFICATION_{timestamp}'
    serial = 2
    while dest.exists():
        dest = folder / f'QUALIFICATION_{timestamp}_{serial}'; serial += 1
    stage = Path(tempfile.mkdtemp(prefix='.qualify-', dir=folder))
    by_kind, outcomes, root_counts = collections.Counter(), collections.Counter(), collections.Counter()
    hashes = collections.Counter(r.get('sha256') for r in registry['sources'] if r.get('sha256'))
    # Exact project scope: 14 official languages, never a silent 'nb' addition.
    from .scan14 import TARGET_LOCALES
    qid_sources = [x for x in registry['sources'] if x['kind']=='wikidata_qid_lexicon_candidate']
    probe = {'status':'absent_ou_multiple', 'candidates':len(qid_sources), 'candidate_only':True}
    if len(qid_sources)==1:
        p, reason = _verified_pointer(qid_sources[0], max_bytes=16 * 1024 * 1024)
        if p is None:
            probe = {'status':reason, 'candidate_only':True}
        else:
            try:
                _, probe = _qid_lexicon_profile(p, wanted=None, locales=tuple(TARGET_LOCALES))
                probe['status']='schema_observe_localement'
                probe['official_locales']=list(TARGET_LOCALES)
            except (ValueError, OSError, UnicodeError) as exc:
                probe={'status':'format_inconnu', 'detail':type(exc).__name__, 'candidate_only':True}
    try:
        with (stage / 'source-qualification.csv').open('w', encoding='utf-8', newline='') as stream:
            fields = ['source_id','kind','path','root','sha256','verification','equivalent_hash_copies',
                      'semantic_link','rights_status','status','action']
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for record in registry['sources']:
                by_kind[record['kind']] += 1; root_counts[record['root']] += 1
                try:
                    _, integrity = _verified_pointer(record, max_bytes=max_hash_bytes)
                except (OSError, ValueError):
                    integrity = 'lecture_impossible'
                if integrity != 'empreinte_identique':
                    status, action = 'non_verifie', 'retrouver_source_et_recalculer_empreinte'
                elif record['kind'] == 'wikidata_qid_lexicon_candidate':
                    status, action = (('lexique_qid_schema_reconnu_non_habilite',
                                       'verifier_droits_provenance_et_crosswalk_accepte') if probe.get('schema_known')
                                      else ('lexique_qid_a_inspecter', 'examiner_champs_id_et_labels_sans_inferer_KQ'))
                elif record['kind'] == 'wikidata_thematic_candidate':
                    status, action = 'wikidata_thematique_candidat', 'examiner_format_et_preuves_QP'
                elif record['kind'].startswith('framework_v11_'):
                    status, action = 'v11_a_auditer', 'auditer_schema_namespace_couches_crosswalk_et_preuves_KS'
                elif record['kind'] == 'gf_pgf_candidate' and '.pytest-tmp' in record['path'].casefold():
                    status, action = 'artefact_de_test', 'exclure_des_grammaires_de_production'
                elif record['kind'].startswith('gf_'):
                    status, action = 'gf_sans_lien_semantique', 'verifier_formes_paradigmes_et_mapping_KQ_KP_approuve'
                else:
                    status, action = 'candidat_inconnu', 'revoir_format_et_licence'
                outcomes[status] += 1
                row = {'source_id':record['source_id'], 'kind':record['kind'], 'path':record['path'],
                       'root':record['root'], 'sha256':record.get('sha256'), 'verification':integrity,
                       'equivalent_hash_copies':hashes.get(record.get('sha256'), 1)-1,
                       'semantic_link':'non_prouve_par_la_decouverte', 'rights_status':'non_qualifie',
                       'status':status, 'action':action}
                writer.writerow({k: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v
                                 for k,v in row.items()})
        report={'schema':'dik.source-qualification/1.0', 'state':'PARTIAL' if truncated or outcomes['non_verifie'] else 'TRIAGE_ONLY',
                'read_only':True,'translation_between_languages':False, 'activations':0,
                'sources_found':len(registry['sources']), 'roots_accessible':len(registry.get('roots_searched',[])),
                'roots_unavailable':len(registry.get('roots_unavailable',[])),
                'duplicate_path_entries':len(registry['sources'])-len({x['path'].casefold() for x in registry['sources']}),
                'duplicate_fingerprint_extra_files':sum(n-1 for n in hashes.values()),
                'by_kind':dict(sorted(by_kind.items())), 'by_status':dict(sorted(outcomes.items())),
                'by_root':dict(sorted(root_counts.items())), 'qid_lexicon_probe':probe,
                'registry_input':str(registry_file), 'report_dir':str(dest),
                'limits': ['SHA local ne prouve ni licence ni autorite',
                           'Un GF .gf ou .pgf ne contient pas implicitement un KQ/KP',
                           'Les Q/P sont distincts des L/S/F Wikidata',
                           'Les memes SHA peuvent avoir plusieurs copies, pas plusieurs mots',
                           'Aucune source activee par cette qualification.']}
        (stage/'rapport.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (stage/'scan.log').write_text(f"diK V5 qualification; sources={len(registry['sources'])}; activations=0\n"
                                       f"state={report['state']}\n",encoding='utf-8')
        stage.rename(dest)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)
