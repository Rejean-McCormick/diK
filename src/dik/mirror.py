"""Explicit, resumable, quarantined Wikidata dump downloads.

Only official HTTPS dump URLs are permitted.  No network access happens on
import or during reads/projections. A download is NOT a semantic approval.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .operations import DiKError

CHUNK = 1024 * 1024
HOST = 'dumps.wikimedia.org'
NAME = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}$')
HEX_SHA256 = re.compile(r'^[0-9a-fA-F]{64}$')


def _safe_url(url: str) -> None:
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != HOST or parsed.port not in (None, 443)
            or parsed.username or parsed.password or parsed.fragment or parsed.query
            or not (parsed.path.startswith('/wikidatawiki/entities/') or
                    parsed.path.startswith('/other/incr/wikidatawiki/'))):
        raise DiKError('SOURCE_NOT_ALLOWED: only official Wikidata HTTPS dump URLs')


class _SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _safe_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _atomic_json(path: Path, obj: dict) -> None:
    tmp = path.with_name(path.name + '.writing')
    try:
        with tmp.open('x', encoding='utf-8') as f:
            json.dump(obj, f, sort_keys=True, indent=2)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(CHUNK), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _range_info(value: str) -> tuple[int, int, int | None] | None:
    m = re.fullmatch(r'bytes\s+(\d+)-(\d+)/(\d+|\*)', value.strip())
    if not m: return None
    start, end = int(m.group(1)), int(m.group(2))
    total = int(m.group(3)) if m.group(3) != '*' else None
    return (start,end,total) if end >= start and (total is None or total > end) else None


def _suffix(url: str) -> str:
    filename = Path(urlsplit(url).path).name
    if filename.endswith('.json.bz2'): return '.json.bz2'
    if filename.endswith('.json.gz'): return '.json.gz'
    if filename.endswith('.jsonl.gz'): return '.jsonl.gz'
    if filename.endswith('.jsonl'): return '.jsonl'
    if filename.endswith('.json'): return '.json'
    # Other incrementals do not implicitly become supported JSON entity dumps.
    raise DiKError('UNSUPPORTED_DUMP: supported extensions: .json, .jsonl, .json.gz, .json.bz2, .jsonl.gz')


def _fetch_impl(*, url: str, root: Path, snapshot: str, expected_sha256: str | None = None,
               max_bytes: int = 250 * 1024**3, timeout: int = 60, opener=None) -> dict:
    """Publish a content-addressed-evidence download under root/snapshot.

    On interruption .part and metadata remain for a checked range retry.
    Unverified upstream content is marked as such; a computed local hash does
    not become a verified upstream checksum. Call explicitly: never in startup.
    """
    _safe_url(url)
    if not NAME.fullmatch(snapshot) or snapshot in ('.', '..'):
        raise DiKError('INVALID_SNAPSHOT_NAME')
    if expected_sha256 is not None and not HEX_SHA256.fullmatch(expected_sha256):
        raise DiKError('INVALID_SHA256')
    if expected_sha256 is not None:
        expected_sha256 = expected_sha256.lower()
    if max_bytes <= 0 or timeout <= 0:
        raise DiKError('INVALID_RESOURCE_LIMIT')
    suffix = _suffix(url)
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    final = root / snapshot
    staging = root / ('.incoming-' + snapshot)
    dest = final / ('wikidata' + suffix)
    if final.is_symlink():
        raise DiKError('UNSAFE_SNAPSHOT: published directory is a symlink')
    if final.exists():
        manifest = final / 'mirror.json'
        if not manifest.is_file():
            raise DiKError('INTEGRITY_MISMATCH: published snapshot missing manifest')
        prev = json.loads(manifest.read_text(encoding='utf-8'))
        if (prev.get('url') != url or prev.get('expected_sha256') != expected_sha256
                or not dest.is_file() or prev.get('sha256') != _hash(dest)):
            raise DiKError('IDEMPOTENCY_CONFLICT: snapshot exists with different or invalid content')
        return {'status': 'already_published', 'dump': str(dest), 'manifest': str(manifest),
                'sha256': prev['sha256'], 'upstream_verified': prev['upstream_verified']}

    if staging.is_symlink():
        raise DiKError('UNSAFE_STAGING: symlinked snapshot staging is forbidden')
    staging.mkdir(exist_ok=True)
    part = staging / ('wikidata' + suffix + '.part')
    state = staging / 'transfer.json'
    if state.is_file():
        meta = json.loads(state.read_text(encoding='utf-8'))
        if meta.get('url') != url or meta.get('expected_sha256') != expected_sha256:
            raise DiKError('IDEMPOTENCY_CONFLICT: transfer parameters changed')
        if not part.is_file() and not ((staging / ('wikidata' + suffix)).is_file() and (staging / 'mirror.json').is_file()):
            raise DiKError('INTEGRITY_MISMATCH: missing partial download')
    else:
        if part.exists():
            raise DiKError('INTEGRITY_MISMATCH: orphan partial without metadata')
        meta = {'url': url, 'expected_sha256': expected_sha256, 'etag': None,
                'last_modified': None, 'total_size': None}
        _atomic_json(state, meta)

    # Crash after checksum/manifest publication but before directory rename.
    completed = staging / ('wikidata' + suffix)
    completed_manifest = staging / 'mirror.json'
    if completed.is_file() and completed_manifest.is_file() and not part.exists():
        final_state = json.loads(completed_manifest.read_text(encoding='utf-8'))
        if (final_state.get('url') != url or
            final_state.get('expected_sha256') != expected_sha256 or
            final_state.get('sha256') != _hash(completed)):
            raise DiKError('INTEGRITY_MISMATCH: completed staging differs from manifest')
        state.unlink(missing_ok=True)
        if final.exists(): raise DiKError('IDEMPOTENCY_CONFLICT: output appeared')
        os.rename(staging, final)
        return {'status':'recovered', 'dump':str(dest), 'manifest':str(final/'mirror.json'),
                'sha256':final_state['sha256'], 'upstream_verified':final_state['upstream_verified'],
                'size_bytes':final_state['size_bytes']}
    offset = part.stat().st_size if part.exists() else 0
    if offset > max_bytes:
        raise DiKError('RESOURCE_LIMIT: previous download exceeds budget')
    validator = meta.get('etag') if meta.get('etag') and not meta['etag'].startswith('W/') else meta.get('last_modified')
    if offset and not validator:
        raise DiKError('UNSAFE_RESUME: remote source supplied no validator; reset staging manually')
    headers = {'Accept-Encoding': 'identity', 'User-Agent': 'diK/1.0-alpha4 wikidata-mirror'}
    if offset:
        headers['Range'] = f'bytes={offset}-'
        headers['If-Range'] = validator
    op = opener or build_opener(_SafeRedirect())
    request = Request(url, headers=headers, method='GET')
    try:
        response = op.open(request, timeout=timeout)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise DiKError(f'DOWNLOAD_INTERRUPTED: {exc}') from exc
    with response as res:
        final_url = res.geturl() if hasattr(res, 'geturl') else url
        _safe_url(final_url)
        status = getattr(res, 'status', None) or res.getcode()
        res_headers = res.headers
        etag = res_headers.get('ETag')
        modified = res_headers.get('Last-Modified')
        range_info = _range_info(res_headers.get('Content-Range', '')) if offset else None
        if offset:
            if status != 206 or range_info is None or range_info[0] != offset:
                raise DiKError('UNSAFE_RESUME: server did not honour requested byte range')
            if (meta.get('etag') and etag != meta['etag']) or (
                    not meta.get('etag') and meta.get('last_modified') and modified != meta['last_modified']):
                raise DiKError('UNSAFE_RESUME: source validator changed')
            if (meta.get('total_size') is not None and range_info[2] is not None
                    and meta['total_size'] != range_info[2]):
                raise DiKError('UNSAFE_RESUME: upstream total size changed')
        elif status != 200:
            raise DiKError('DOWNLOAD_HTTP_STATUS: full download requires HTTP 200')
        content_length = res_headers.get('Content-Length')
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError as exc:
                raise DiKError('INVALID_CONTENT_LENGTH') from exc
            if length < 0 or length + offset > max_bytes:
                raise DiKError('RESOURCE_LIMIT: remote size exceeds limit')
        else:
            length = None
        if offset and length is not None and range_info[1] - range_info[0] + 1 != length:
            raise DiKError('INVALID_CONTENT_RANGE: range length disagrees with HTTP response')
        if not offset:
            meta['etag'], meta['last_modified'] = etag, modified
            if length is not None: meta['total_size'] = length
            _atomic_json(state, meta)
        mode = 'ab' if offset else ('wb' if part.exists() else 'xb')
        try:
            with part.open(mode) as out:
                while True:
                    chunk = res.read(CHUNK)
                    if not chunk: break
                    if not isinstance(chunk, bytes):
                        raise DiKError('INVALID_RESPONSE_DATA')
                    if out.tell() + len(chunk) > max_bytes:
                        raise DiKError('RESOURCE_LIMIT: stream exceeds budget')
                    out.write(chunk)
                out.flush(); os.fsync(out.fileno())
        except (OSError, TimeoutError) as exc:
            raise DiKError(f'DOWNLOAD_INTERRUPTED: {exc}') from exc
    size = part.stat().st_size
    if length is not None and size != offset + length:
        raise DiKError('DOWNLOAD_INTERRUPTED: incomplete response body')
    sha = _hash(part)
    if expected_sha256 is not None and sha != expected_sha256.lower():
        raise DiKError('CHECKSUM_MISMATCH: received dump differs from approved upstream checksum')
    destination = staging / ('wikidata' + suffix)
    if destination.exists():
        raise DiKError('INTEGRITY_MISMATCH: unexpected duplicate staged dump')
    os.rename(part, destination)
    manifest = {'profile': 'dik.wikidata-mirror/1.0-candidate', 'snapshot': snapshot,
        'url': url, 'sha256': sha, 'expected_sha256': expected_sha256,
        'upstream_verified': expected_sha256 is not None, 'size_bytes': size,
        'etag': meta.get('etag'), 'last_modified': meta.get('last_modified'),
        'dump_file': destination.name, 'imported_into_kristal': False}
    _atomic_json(staging / 'mirror.json', manifest)
    state.unlink()
    if final.exists():
        raise DiKError('IDEMPOTENCY_CONFLICT: output created concurrently')
    os.rename(staging, final)
    return {'status':'published', 'dump': str(dest), 'manifest': str(final/'mirror.json'),
            'sha256': sha, 'upstream_verified': expected_sha256 is not None, 'size_bytes': size}


def fetch_dump(*, url: str, root: Path, snapshot: str, expected_sha256: str | None = None,
               max_bytes: int = 250 * 1024**3, timeout: int = 60, opener=None) -> dict:
    """Serialize publication per snapshot even between independent diK processes."""
    _safe_url(url)
    if not NAME.fullmatch(snapshot) or snapshot in ('.', '..'):
        raise DiKError('INVALID_SNAPSHOT_NAME')
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ('.lock-' + snapshot)
    try:
        with lock.open('x', encoding='utf-8') as handle:
            handle.write(str(os.getpid()))
        return _fetch_impl(url=url, root=root, snapshot=snapshot,
            expected_sha256=expected_sha256, max_bytes=max_bytes,
            timeout=timeout, opener=opener)
    except FileExistsError as exc:
        raise DiKError('SNAPSHOT_BUSY: another operation holds the snapshot lock') from exc
    finally:
        # Only our successful exclusive creation may remove this lock.
        # The lock can outlive a crash and then needs operator recovery.
        if 'handle' in locals():
            lock.unlink(missing_ok=True)
