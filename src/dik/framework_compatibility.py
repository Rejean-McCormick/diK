"""Read-only compatibility preflight for vendored Framework v11 schema bytes.

The diK alpha.7 implementation targets the draft.3 semantics. Framework draft.4
states its v11 schema/TCK bytes were unchanged; this script checks that
assertion against *the caller's actual local source*, not a release-name guess.
It never imports/modifies the Framework, approves a crosswalk or changes canon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

VENDORED = Path(__file__).resolve().parent / '_framework/schemas/v11'
SUPPORTED_COMPARISON = {'11.0.0-draft.3', '11.0.0-draft.4'}


class FrameworkCompatibilityError(ValueError):
    pass


def inspect_schema_parity(framework: str | Path) -> dict:
    framework = Path(framework).expanduser().resolve()
    version_file = framework / 'VERSION'
    if not version_file.is_file():
        raise FrameworkCompatibilityError('Missing independent Framework VERSION file')
    version = version_file.read_text(encoding='utf-8').strip()
    if version not in SUPPORTED_COMPARISON:
        raise FrameworkCompatibilityError(f'Unsupported Framework source version: {version}')
    original = framework / 'schemas/v11'
    if not original.is_dir():
        raise FrameworkCompatibilityError('Missing independent Framework v11 schemas')
    local_files = {p.name: p for p in VENDORED.glob('*.schema.json')}
    source_files = {p.name: p for p in original.glob('*.schema.json')}
    if not local_files or local_files.keys() != source_files.keys():
        raise FrameworkCompatibilityError('Framework v11 schema inventory differs from diK vendor')
    verified = {}
    for name in sorted(local_files):
        digest = hashlib.sha256(local_files[name].read_bytes()).hexdigest()
        if hashlib.sha256(source_files[name].read_bytes()).hexdigest() != digest:
            raise FrameworkCompatibilityError('Framework v11 schema drift: ' + name)
        verified[name] = digest
    return {
        'format': 'dik.framework-v11-source-parity/1.0-read-only',
        'framework_source_version': version,
        'dik_implementation_baseline': '11.0.0-draft.3',
        'schema_count': len(verified), 'schemas_sha256': verified,
        'schemas_identical': True,
        'read_only': True, 'canonical_state_modified': False,
        'qualification': 'schema-byte-parity-only; not end-to-end Kit importer or TCK certification',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_schema_parity(args.framework)
    except (FrameworkCompatibilityError, OSError, ValueError) as exc:
        parser.exit(1, 'diK Framework v11 source parity REFUSED: ' + str(exc) + '\n')
    print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
