"""V5.2: bounded, read-only observations from inventoried Wikidata JSONL.

The files are NOT trusted as lexicons by virtue of their path or name. A
candidate observation needs an explicit Q/P identifier, an explicit locale
and an exact accepted crosswalk from the official v11 portfolio. Even then,
licensing, provenance and semantic publishing approval remain outstanding.
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path
from typing import Any

from .source_qualification import _verified_pointer

_QP = re.compile(r'^[QP][1-9][0-9]*$')
_MAX_LINE = 2_000_000


def _explicit_row(row: Any) -> tuple[str | None, dict | None, str]:
    """Recognize *only* entity IDs and labeled values, not statement predicates.

    A Q/P-shaped id in a statements/identity-candidates file may be metadata.
    It does not become a lexical form unless an explicit labels map exists.
    """
    if not isinstance(row, dict):
        return None, None, 'non_object'
    ident = row.get('qid', row.get('id'))
    if isinstance(ident, str) and _QP.fullmatch(ident):
        labels = row.get('labels')
        return ident, labels if isinstance(labels, dict) else None, (
            'id_labels' if isinstance(labels, dict) else 'id_without_labels')
    if len(row) == 1:
        key, value = next(iter(row.items()))
        if isinstance(key, str) and _QP.fullmatch(key) and isinstance(value, dict):
            # Only a strict locale -> text map can be interpreted as labels.
            if all(isinstance(k, str) and isinstance(v, (str, dict)) for k, v in value.items()):
                return key, value, 'qp_keyed_locales'
    return None, None, 'unrecognized'


def _label(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get('value')
    if isinstance(value, str) and value.strip() and len(value) <= 10_000:
        return value.strip()
    return None


def _profile(path: Path, wanted: set[str], locales: tuple[str, ...], *,
             max_rows: int = 150_000, max_observations: int = 40_000) -> tuple[dict, dict]:
    """Return ({(Q/P, locale): {form}}, diagnostic), bounded JSONL inspection."""
    counts = collections.Counter()
    schemas = collections.Counter()
    seen_ids = set()
    overlap_ids = set()
    labels: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    truncated = False
    with path.open('r', encoding='utf-8-sig') as stream:
        for number, line in enumerate(stream, 1):
            if number > max_rows:
                truncated = True
                break
            if not line.strip():
                continue
            counts['rows'] += 1
            if len(line) > _MAX_LINE:
                counts['oversized_rows'] += 1
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                counts['malformed_json'] += 1
                continue
            qid, explicit, shape = _explicit_row(obj)
            schemas[shape] += 1
            if qid is None:
                continue
            seen_ids.add(qid)
            counts['rows_with_qp'] += 1
            if qid not in wanted:
                continue
            overlap_ids.add(qid)
            counts['rows_matching_accepted_qp'] += 1
            if explicit is None:
                continue
            for locale in locales:
                word = _label(explicit.get(locale))
                if word is None:
                    continue
                key = (qid, locale)
                # Protect memory on anomalous sources; never mislabel truncation as completeness.
                if key not in labels and len(labels) >= max_observations:
                    truncated = True
                    break
                if len(labels[key]) < 3:
                    labels[key].add(word)
    conflicts = {key for key, words in labels.items() if len(words) > 1}
    valid = {key: next(iter(words)) for key, words in labels.items() if len(words) == 1}
    status = ('truncated' if truncated else 'candidate_labels_observed' if valid else
              'accepted_qp_without_labels' if overlap_ids else 'no_accepted_qp_overlap')
    return valid, {
        'status': status, 'rows_read': counts['rows'], 'rows_with_qp': counts['rows_with_qp'],
        'rows_matching_accepted_qp': counts['rows_matching_accepted_qp'],
        'distinct_qp': len(seen_ids), 'distinct_qp_matching_accepted': len(overlap_ids),
        'explicit_labels_for_accepted_qp': len(valid),
        'conflicts_within_source': len(conflicts),
        'invalid_or_oversized_rows': counts['malformed_json'] + counts['oversized_rows'],
        'schemas': dict(sorted(schemas.items())), 'truncated': truncated,
        'candidate_only': True,
    }


def observe_thematic_sources(registry: dict, *, wanted: set[str],
                            locales: tuple[str, ...], max_bytes: int = 64 * 1024 * 1024):
    """Read all thematic entries after SHA-256 verification.

    Return (Q/P+locale -> observations, source profiles, summary). Sources
    with conflicting spellings are reported, not arbitrarily preferred.
    Neither the registry nor any dictionary is modified.
    """
    if len(set(locales)) != len(locales):
        raise ValueError('Localisations dupliquees')
    candidates = [x for x in registry.get('sources', [])
                  if x.get('kind') == 'wikidata_thematic_candidate']
    profiles = []
    observations: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    seen_sha: dict[str, str] = {}
    totals = collections.Counter()
    for entry in candidates:
        row = {'source_id': entry.get('source_id', ''), 'path': entry.get('path', ''),
               'sha256': entry.get('sha256') or '', 'candidate_only': True}
        try:
            path, reason = _verified_pointer(entry, max_bytes=max_bytes)
        except (OSError, ValueError, KeyError, TypeError):
            path, reason = None, 'invalid_pointer'
        if path is None:
            row['status'] = reason
            totals['not_verified'] += 1
            profiles.append(row)
            continue
        digest = entry['sha256'].lower()
        if digest in seen_sha:
            row['status'] = 'same_bytes_as_prior_source'
            row['identical_to_source_id'] = seen_sha[digest]
            totals['identical_copies_skipped'] += 1
            profiles.append(row)
            continue
        seen_sha[digest] = entry['source_id']
        try:
            data, report = _profile(path, wanted, locales)
        except (OSError, UnicodeError, ValueError):
            row['status'] = 'invalid_or_unreadable_jsonl'
            totals['unreadable'] += 1
            profiles.append(row)
            continue
        row.update(report)
        profiles.append(row)
        totals['files_inspected'] += 1
        totals['accepted_qp_overlaps_per_file'] += report['distinct_qp_matching_accepted']
        totals['candidate_labels_per_file'] += len(data)
        totals['files_truncated'] += bool(report['truncated'])
        for (qid, locale), word in data.items():
            observations[qid, locale].append({
                'qp': qid, 'locale': locale, 'form': word,
                'source_id': entry['source_id'], 'path': str(path),
                'sha256': digest, 'candidate_only': True,
            })
    conflicting = {key for key, vals in observations.items()
                   if len({x['form'] for x in vals}) > 1}
    # A conflict must remain clearly flagged, not covered by a better-looking label.
    for key, vals in observations.items():
        for value in vals:
            value['status'] = ('conflict_between_sources' if key in conflicting
                               else 'observation_non_publiee')
    summary = {
        'status': 'TRIAGE_ONLY', 'candidate_only': True, 'activations': 0,
        'sources_registered': len(candidates), 'sources_inspected': totals['files_inspected'],
        'sources_not_verified': totals['not_verified'],
        'identical_copies_skipped': totals['identical_copies_skipped'],
        'sources_unreadable': totals['unreadable'],
        'sources_truncated': totals['files_truncated'],
        'candidate_pairs_with_accepted_qp': len(observations),
        'candidate_forms': sum(map(len, observations.values())),
        'conflicting_pairs': len(conflicting),
        'locales_exact': list(locales),
        'scope': 'Q/P explicitement lie aux KQ/KP par crosswalk accepte; jamais de traduction',
        'warning': ('Formats de sources non prouves: aucun label n est autorise '
                    'pour publication sans revue provenance, licence et preuve de correspondance'),
    }
    return observations, profiles, summary
