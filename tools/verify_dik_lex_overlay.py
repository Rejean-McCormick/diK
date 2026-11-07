"""Validate every file delivered by the DIK-LEX-1 root-overlay ZIP; no Git needed."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'DIK-LEX-1-OVERLAY-MANIFEST.json'


def verify(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    doc = json.loads((root / MANIFEST.name).read_text(encoding='utf-8'))
    if doc.get('profile') != 'dik.lex-1-overlay/0.3-candidate' or doc.get('archive_root') != 'repository-root':
        raise ValueError('unexpected DIK-LEX-1 overlay manifest')
    files = doc.get('files')
    if not isinstance(files, list) or len(files) < 20:
        raise ValueError('truncated overlay manifest')
    seen = set()
    total = 0
    for entry in files:
        rel = entry['path']
        if (not isinstance(rel, str) or rel.startswith('/') or '\\' in rel
            or '..' in Path(rel).parts or rel in seen
            or rel.startswith(('spec/diK-1.0/', 'src/dik/_framework/'))):
            raise ValueError(f'unsafe overlay path: {rel!r}')
        seen.add(rel)
        candidate = root / rel
        if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root):
            raise ValueError(f'missing/untrusted file: {rel}')
        data = candidate.read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f'overlay mismatch: {rel}')
        total += len(data)
    if len(files) != doc['file_count'] or total != doc['total_file_bytes']:
        raise ValueError('overlay file totals mismatch')
    return {'valid': True, 'overlay': doc['profile'], 'files_verified': len(files),
            'total_file_bytes': total, 'archive_root': 'repository-root',
            'git_required': False}


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'Overlay DIK-LEX-1 incorrect : {exc}', file=sys.stderr)
        raise SystemExit(2)
