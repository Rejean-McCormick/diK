"""Normalize *official MediaWiki Action API query redirects* into diK observations.

Accepts saved JSON responses or JSONL of response envelopes. This does NOT parse
Wikidata entity dumps, XML revision blobs, SQL redirect tables, or hypothetical
splits. Input is untrusted; the caller may pin its SHA-256 independently.

Semantics: query.redirects[].from -> .to is redirect evidence only.
No missing, retired, merged or split entities are inferred. No canon/crosswalk write.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .operations import DiKError

_ID = re.compile(r'^(?:Q|P)[1-9][0-9]*$')
_HEX = re.compile(r'^[a-f0-9]{64}$')
_SNAPSHOT = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,199}$')
_MAX_ENVELOPE_BYTES = 8 * 1024 * 1024


def _id_from_title(value: object) -> str:
    if not isinstance(value, str):
        raise DiKError('INVALID_MEDIAWIKI_TITLE: expected text')
    if value.startswith('Property:'):
        entity = value[len('Property:'):]
        if re.fullmatch(r'P[1-9][0-9]*', entity):
            return entity
    elif re.fullmatch(r'Q[1-9][0-9]*', value):
        return value
    raise DiKError('UNSUPPORTED_MEDIAWIKI_TITLE: expected Q… or Property:P…')


def _extract_envelope(envelope: object, snapshot: str, source_reference: str,
                      seen: set[str], remaining: int) -> list[dict]:
    if not isinstance(envelope, dict) or envelope.get('error') or not isinstance(envelope.get('query'), dict):
        raise DiKError('INVALID_MEDIAWIKI_RESPONSE: missing query or API error')
    if envelope.get('continue'):
        raise DiKError('INCOMPLETE_MEDIAWIKI_RESPONSE: pagination must be collected separately')
    entries = envelope['query'].get('redirects', [])
    if not isinstance(entries, list):
        raise DiKError('INVALID_MEDIAWIKI_RESPONSE: redirects must be an array')
    if len(entries) > remaining:
        raise DiKError('RESOURCE_LIMIT: max events reached')
    result = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get('from'), str) or not isinstance(entry.get('to'), str):
            raise DiKError('INVALID_MEDIAWIKI_REDIRECT: from/to required')
        source = _id_from_title(entry['from'])
        target = _id_from_title(entry['to'])
        if source[0] != target[0]:
            raise DiKError('IDENTITY_KIND_MISMATCH: Q/P redirect types differ')
        if source == target:
            raise DiKError('REDIRECT_CYCLE: self-reference')
        if source in seen:
            raise DiKError('DUPLICATE_EVOLUTION_EVENT: ' + source)
        seen.add(source)
        result.append({'event_type': 'redirect', 'source_id': source, 'targets': [target],
                       'source_snapshot': snapshot,
                       'source_reference': f'{source_reference}:redirect:{i + 1}'})
    return result


def _read_responses(input_file: Path, input_format: str, max_bytes: int):
    """Bound decompressed input bytes. One JSON envelope, or one per JSONL line."""
    if input_format == 'action-api-json':
        with input_file.open('rb') as f:
            data = f.read(min(max_bytes, _MAX_ENVELOPE_BYTES) + 1)
            if len(data) > min(max_bytes, _MAX_ENVELOPE_BYTES):
                raise DiKError('RESOURCE_LIMIT: MediaWiki response is too large')
            if f.read(1):
                raise DiKError('RESOURCE_LIMIT: MediaWiki response is too large')
        try:
            yield 1, json.loads(data)
        except (UnicodeError, ValueError) as exc:
            raise DiKError('INVALID_MEDIAWIKI_JSON') from exc
        return
    if input_format != 'action-api-jsonl':
        raise DiKError('UNSUPPORTED_MEDIAWIKI_FORMAT')
    total = 0
    with input_file.open('rb') as f:
        for lineno, line in enumerate(f, 1):
            total += len(line)
            if total > max_bytes or len(line) > _MAX_ENVELOPE_BYTES:
                raise DiKError('RESOURCE_LIMIT: MediaWiki input exceeds limit')
            if not line.strip():
                continue
            try:
                yield lineno, json.loads(line)
            except (UnicodeError, ValueError) as exc:
                raise DiKError(f'INVALID_MEDIAWIKI_JSONL: line {lineno}') from exc


def extract_api_redirects(*, source: Path, output: Path, snapshot: str,
                          input_format: str = 'action-api-json',
                          approved_sha256: str | None = None,
                          max_bytes: int = 128 * 1024 * 1024,
                          max_records: int = 250_000) -> dict:
    """Publish a validated, non-overwriting normalized JSONL and report its hash.

    SHA-256 over *raw input* is verified before parsing. The output reference
    includes the input content address. A hash alone does NOT authenticate
    that the file was obtained from Wikimedia.
    """
    source, output = Path(source), Path(output)
    if not _SNAPSHOT.fullmatch(snapshot):
        raise DiKError('INVALID_SNAPSHOT')
    if max_bytes <= 0 or max_bytes > 8 * 1024**3 or not 1 <= max_records <= 10_000_000:
        raise DiKError('INVALID_RESOURCE_LIMIT')
    if approved_sha256 is not None and not _HEX.fullmatch(approved_sha256.lower()):
        raise DiKError('INVALID_APPROVED_SHA256')
    if not source.is_file():
        raise DiKError('SOURCE_NOT_FOUND')
    if source.resolve() == output.resolve() or output.exists():
        raise DiKError('OUTPUT_EXISTS_OR_COLLIDES')
    digest = hashlib.sha256()
    with source.open('rb') as f:
        amount = 0
        for block in iter(lambda: f.read(1024 * 1024), b''):
            amount += len(block)
            if amount > max_bytes:
                raise DiKError('RESOURCE_LIMIT: source exceeds allowed bytes')
            digest.update(block)
    source_sha = digest.hexdigest()
    if approved_sha256 is not None and approved_sha256.lower() != source_sha:
        raise DiKError('INTEGRITY_MISMATCH: source digest differs from approved checksum')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.dik-redirect-', suffix='.tmp', dir=str(output.parent))
    temp = Path(tmp)
    seen = set()
    lines = 0
    records = 0
    output_digest = hashlib.sha256()
    try:
        with os.fdopen(fd, 'wb') as out:
            for lineno, envelope in _read_responses(source, input_format, max_bytes):
                lines += 1
                events = _extract_envelope(envelope, snapshot,
                            f'wikidata-action-api:sha256:{source_sha}:response:{lineno}',
                            seen, max_records - records)
                records += len(events)
                for event in events:
                    binary = (json.dumps(event, ensure_ascii=False, separators=(',', ':'), sort_keys=True) + '\n').encode('utf-8')
                    if len(binary) > 256 * 1024:
                        raise DiKError('RESOURCE_LIMIT: normalized record too large')
                    out.write(binary)
                    output_digest.update(binary)
            out.flush()
            os.fsync(out.fileno())
        # Detect input changing between verification and processing.
        after = hashlib.sha256()
        with source.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                after.update(block)
        if after.hexdigest() != source_sha:
            raise DiKError('SOURCE_CHANGED_DURING_EXTRACTION')
        try:
            os.link(temp, output)  # Atomic no-clobber publication on supported local filesystems.
        except FileExistsError as exc:
            raise DiKError('OUTPUT_EXISTS') from exc
    finally:
        temp.unlink(missing_ok=True)
    return {
        'profile': 'dik.mediawiki-redirect-extract/1.0-candidate',
        'source_type': 'wikidata-action-api-query-redirects',
        'source_snapshot': snapshot, 'source_sha256': source_sha,
        'source_digest_verified': approved_sha256 is not None,
        'output_sha256': output_digest.hexdigest(),
        'responses_processed': lines, 'redirect_events': records,
        'output': str(output), 'canonical_mutation': False,
        'crosswalk_mutation': False,
        'warning': 'Action API redirects are evidence, not an approved identity merger. '
                   'Local SHA-256 verification does not by itself authenticate Wikimedia origin. '
                   'Missing entities and splits are never inferred.'
    }
