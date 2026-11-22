"""Inventaire externe *heuristique* du corpus et des chaînes d'UI Konstellation.

Adapté du scanner 14 langues autonome 2026-11-21. Ce module ne valide
aucun exactMatch et ne résout aucun libellé canonique diK.
"""
from __future__ import annotations
import html
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

MAX_BYTES = 35_000_000
class InventoryError(ValueError):
    pass
AuditError = InventoryError

class Source:
    def __init__(self, loc):
        self.path = Path(loc).expanduser().resolve()
        if self.path.is_file() and self.path.suffix.lower() == '.zip':
            self.zip = zipfile.ZipFile(self.path)
            self.root = None
            self.names = set(self.zip.namelist())
        elif self.path.is_dir():
            self.zip = None
            self.root = self.path
            self.names = None
        else:
            raise AuditError(f'Source ZIP ou répertoire absent : {loc}')

    @staticmethod
    def safe(rel):
        if not isinstance(rel, str) or not rel or '\\' in rel:
            raise AuditError('Chemin relatif dangereux : ' + repr(rel))
        parts = PurePosixPath(rel).parts
        if rel.startswith('/') or any(p in ('..', '.', '') for p in parts):
            raise AuditError('Chemin relatif dangereux : ' + repr(rel))
        if PurePosixPath(rel).as_posix() != rel:
            raise AuditError('Chemin non canonique : ' + rel)
        return rel

    def exists(self, rel):
        rel = self.safe(rel)
        return rel in self.names if self.zip else (self.root / rel).is_file()

    def read(self, rel):
        rel = self.safe(rel)
        if self.zip:
            if rel not in self.names:
                raise AuditError(f'Fichier absent dans {self.path.name}: {rel}')
            info = self.zip.getinfo(rel)
            if info.file_size > MAX_BYTES:
                raise AuditError(f'Fichier trop volumineux: {rel}')
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise AuditError(f'Lien symbolique refusé: {rel}')
            return self.zip.read(info)
        path = self.root / rel
        real = path.resolve()
        if not real.is_relative_to(self.root) or path.is_symlink() or not path.is_file():
            raise AuditError(f'Fichier absent ou lien interdit: {rel}')
        if path.stat().st_size > MAX_BYTES:
            raise AuditError(f'Fichier trop volumineux: {rel}')
        return path.read_bytes()

    def js(self, rel):
        try:
            return json.loads(self.read(rel))
        except (UnicodeError, ValueError) as e:
            raise AuditError(f'JSON invalide: {self.path.name}/{rel}: {e}') from e

    def paths(self, prefix, suffixes):
        if self.zip:
            return sorted(x for x in self.names if x.startswith(prefix) and x.endswith(suffixes))
        return sorted(x.relative_to(self.root).as_posix() for x in (self.root/prefix).rglob('*')
                      if x.is_file() and not x.is_symlink() and x.suffix in suffixes)

    def close(self):
        if self.zip:
            self.zip.close()



def corpus_terms(source, pack_path):
    pack = source.js(pack_path)
    result = []
    for item in pack.get('entities', []):
        result.append({'source': 'entite', 'id': item['id'], 'role': item.get('type', ''), 'texte_fr': item.get('label', ''), 'canal': 'libelle_entite'})
        if item.get('description'):
            result.append({'source': 'entite', 'id': item['id'], 'role': item.get('type', ''), 'texte_fr': item['description'], 'canal': 'description'})
    for item in pack.get('policies', []):
        for key in ('label', 'description'):
            if item.get(key):
                result.append({'source': 'politique', 'id': item['id'], 'role': '', 'texte_fr': item[key], 'canal': key})
    for item in pack.get('sources', []):
        for key in ('title', 'description'):
            if item.get(key):
                result.append({'source': 'source', 'id': item['id'], 'role': '', 'texte_fr': item[key], 'canal': key})
    for r in pack.get('registry', {}).get('relations', []):
        for loc, value in r.get('label', {}).items():
            result.append({'source': 'relation', 'id': r['id'], 'role': 'locale:' + loc,
                           'texte_fr': value, 'canal': 'libelle_registre'})
    for key in ('title', 'description'):
        if pack.get(key):
            result.append({'source': 'corpus', 'id': key, 'role': '', 'texte_fr': pack[key], 'canal': key})
    return result, pack


def ui_candidate_strings(source):
    """Inventaire approximatif des chaînes statiques de composants, PAS une preuve d'exhaustivité.

    Les expressions JS dynamiques, concaténations et i18n externes ne sont pas résolues.
    """
    candidates = []
    for root in ('src/components/', 'src/pages/'):
        for rel in source.paths(root, ('.svelte', '.astro')):
            body = source.read(rel).decode('utf-8-sig')
            # Preserve line numbers while discarding code and CSS.
            body = re.sub(r'<(script|style)\b[^>]*>.*?</\1\s*>',
                          lambda m: '\n'*m.group(0).count('\n'), body, flags=re.I|re.S)
            pieces = []
            pieces.extend((m.start(1),m.group(1), 'texte_HTML') for m in re.finditer(r'>([^<>]+)<', body, flags=re.S))
            pieces.extend((m.start(2),m.group(2),'attribut') for m in re.finditer(
                r'(?:^|\s)(placeholder|title|aria-label|alt)=(\"[^\"]+\"|\'[^\']+\')', body))
            for idx, raw, channel in pieces:
                if channel == 'attribut': raw = raw[1:-1]
                raw = re.sub(r'\{[^{}]*\}', '', raw)
                raw = ' '.join(html.unescape(raw).split()).strip()
                if not re.search(r'[A-Za-zÀ-ÿ]{2,}',raw) or len(raw)>280 or len(raw)<3:
                    continue
                if raw.startswith(('/', '$', '#')) or raw in ('else','if','each'):
                    continue
                candidates.append({'fichier':rel,'ligne_approx':body.count('\n',0,idx)+1,
                                   'texte_candidat':raw,'origine':channel,
                                   'etat':'CANDIDAT_A_REVOIR_non_prealigne_14_langues'})
    return candidates

