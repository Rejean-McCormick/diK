"""Explicit HTTPS-only IANA registry acquisition; disabled unless operator calls it.

The remote endpoint is pinned to the official IANA host. A successful download
and local digest do not independently attest the administrative authenticity of
the file; optional SHA-256 must come from a source checked by the operator.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .iana_registry import load_registry

REGISTRY_URL = 'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry'


class _OnlyIanaRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _check_url(url: str) -> None:
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != 'www.iana.org'
        or parsed.port not in (None, 443) or parsed.username or parsed.password
        or parsed.path != '/assignments/language-subtag-registry/language-subtag-registry'
        or parsed.query or parsed.fragment):
        raise ValueError('IANA source URL must be the pinned official registry')


def fetch_iana_registry(*, output: Path, user_agent: str, expected_sha256: str | None = None,
                        timeout: int = 30, max_bytes: int = 25_000_000, opener=None) -> dict:
    if not isinstance(user_agent, str) or len(user_agent.strip()) < 12 or len(user_agent) > 256:
        raise ValueError('identifiable User-Agent required')
    if not 1 <= timeout <= 180 or not 128 <= max_bytes <= 100_000_000:
        raise ValueError('invalid timeout or size limits')
    if expected_sha256 is not None and not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256):
        raise ValueError('invalid expected SHA-256')
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError('output exists; IANA snapshots are immutable')
    output.parent.mkdir(parents=True, exist_ok=True)
    _check_url(REGISTRY_URL)
    req = Request(REGISTRY_URL, headers={'User-Agent': user_agent,
                                         'Accept': 'text/plain', 'Accept-Encoding': 'identity'})
    client = opener if opener is not None else build_opener(_OnlyIanaRedirect())
    fd, filename = tempfile.mkstemp(prefix='.dik-iana-download-', dir=str(output.parent))
    staged = Path(filename)
    sha = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(fd, 'wb') as dest:
            with client.open(req, timeout=timeout) as response:
                final_url = response.geturl() if hasattr(response, 'geturl') else REGISTRY_URL
                _check_url(final_url)
                status = getattr(response, 'status', None) or response.getcode()
                if status != 200:
                    raise ValueError('unexpected HTTP response from IANA')
                while True:
                    chunk = response.read(min(1024 * 1024, max_bytes - size + 1))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_bytes:
                        raise ValueError('IANA registry too large')
                    sha.update(chunk)
                    dest.write(chunk)
            dest.flush()
            os.fsync(dest.fileno())
        digest = sha.hexdigest()
        if expected_sha256 and expected_sha256.lower() != digest:
            raise ValueError('IANA registry SHA-256 mismatch')
        reg = load_registry(staged, max_bytes=max_bytes)
        # Never replace an existing file, even under simultaneous invocations.
        try:
            os.link(staged, output)
        except FileExistsError as exc:
            raise FileExistsError('IANA snapshot path now exists') from exc
        return {'source': REGISTRY_URL, 'output': str(output), 'file_date': reg.file_date,
                'sha256': digest, 'bytes': size,
                'expected_digest_supplied': expected_sha256 is not None,
                'independent_source_attestation': False}
    finally:
        staged.unlink(missing_ok=True)
