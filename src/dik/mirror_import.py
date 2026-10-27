"""Import verified mirror bytes via the pre-existing immutable import workflow."""
from __future__ import annotations
import json
from pathlib import Path

from .mirror import _safe_url, _hash, HEX_SHA256
from .sync import import_idempotent
from .operations import DiKError


def import_verified_mirror(*, manifest: Path, crosswalk: Path, registry: Path,
                           namespace: str, locales: list[str], root: Path, approved_sha256: str) -> dict:
    """Strict hand-off between the transport and the semantic importer.

    A locally computed digest is not an upstream attestation.  A verified
    upstream digest must have been supplied when fetching.  This function
    never changes a canonical graph, original dictionary or crosswalk.
    """
    if not HEX_SHA256.fullmatch(approved_sha256):
        raise DiKError('INVALID_APPROVED_SHA256')
    approved_sha256 = approved_sha256.lower()
    manifest = Path(manifest).resolve()
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('profile') != 'dik.wikidata-mirror/1.0-candidate':
        raise DiKError('INVALID_MIRROR_MANIFEST')
    _safe_url(data.get('url',''))
    if not data.get('upstream_verified') or not data.get('expected_sha256'):
        raise DiKError('UNVERIFIED_UPSTREAM: explicit upstream SHA-256 required')
    filename = data.get('dump_file')
    if not isinstance(filename,str) or not filename.startswith('wikidata.') or '/' in filename or '\\' in filename:
        raise DiKError('INVALID_MIRROR_DUMP_FILE')
    dump = manifest.parent / filename
    if not dump.is_file() or dump.is_symlink():
        raise DiKError('MISSING_MIRROR_DUMP')
    sha = _hash(dump)
    if (sha != data.get('sha256') or sha != data.get('expected_sha256') or sha != approved_sha256):
        raise DiKError('INTEGRITY_MISMATCH: mirror differs from pinned upstream checksum')
    result = import_idempotent(dump=dump,crosswalk=Path(crosswalk),registry=Path(registry),
        namespace=namespace,snapshot=data['snapshot'],locales=locales,root=Path(root))
    return {**result,'mirror_manifest':str(manifest), 'mirror_sha256':sha,
            'upstream_verified':True}
