# 27 — DIK-LEX-1 : IANA BCP 47, réconciliation ISO 639-3 et collection mondiale clairsemée

**Statut** : complément applicatif candidat, **non normatif Framework**, sans migration d'identités.

## Problème résolu

- **ISO 639-3** identifie des codes de langues (y compris anciennes, éteintes, construites, spéciales ou macrolangues).
- **IANA Language Subtag Registry** déclare des composants BCP 47 : `language`, `extlang`, `script`, `region`, `variant`, `grandfathered` et `redundant`.
- Un **tag BCP 47** est une combinaison structurée, distincte d'un code ISO et distincte d'une locale qui aurait des traductions vérifiées.
- **diK** conserve ces identifiants comme **métadonnées de découverte**, en dehors des identités KQ/KP et des dictionnaires Framework v11.

La livraison DIK-LEX-1 v0.3 inclut `language-code-candidates.jsonl` (7 910 candidats ISO 639-3 provenant du snapshot v0.2), `collection-slots-v0.3/` (7 910 *emplacements* vides) et un catalogue de 25 ressources à explorer. **Il n'y a pas 7 910 dictionnaires.**

## Registre IANA : provenance

L'archive comprend `iana-fixtures/synthetic-language-subtag-registry.txt`, **uniquement pour les tests**, avec une date fictive et un nombre volontairement minuscule de subtags. Elle n'est pas un registre IANA complet et ne doit pas être utilisée pour annoncer une couverture réelle.

L'opérateur fournit une **copie officielle** du registre TXT :

- Source : <https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry>
- Références : <https://www.rfc-editor.org/rfc/rfc5646> et <https://www.iana.org/assignments/language-subtags-tags-extensions>
- L'acquisition est *opt-in*, protégée contre les redirections vers d'autres domaines, avec taille et délai bornés.
- Une empreinte locale atteste l'intégrité de **ces octets**, pas automatiquement leur origine. On peut donner un SHA attendu validé séparément.
- Ne pas écraser un ancien registre : chaque acquisition doit créer un nouveau fichier/version.

```sh
# Remplacer l'User-Agent de démonstration par les coordonnées de votre opérateur.
dik world iana-fetch \
  --output-file data/iana/language-subtag-registry-2026.txt \
  --user-agent 'diK-world (contact: admin@example.org)'

dik world iana-audit --registry data/iana/language-subtag-registry-2026.txt

dik world tag-check \
  --registry data/iana/language-subtag-registry-2026.txt \
  --tags fr-CA,en,zh-Hans,zh-Hant,sr-Latn,ar
```

**Limite explicite** : le vérificateur est **conservateur**. Il vérifie les structures courantes, l'enregistrement des composants et certains préfixes/doublons. Il ne réalise pas une canonicalisation CLDR exhaustive ni toutes les analyses de combinaisons/alias historiques de RFC 5646. `normalized_case` ne constitue pas une approbation de l'identité d'une langue. Les subtags dépréciés sont signalés, **pas réécrits**.

## Réconcilier les 7 910 codes avec la version IANA locale

```sh
dik world languages-audit \
  --index examples/world-dictionaries/language-code-candidates.jsonl \
  --manifest examples/world-dictionaries/language-code-candidates.manifest.json

dik world reconcile-iso \
  --index examples/world-dictionaries/language-code-candidates.jsonl \
  --manifest examples/world-dictionaries/language-code-candidates.manifest.json \
  --registry data/iana/language-subtag-registry-2026.txt \
  --output-dir data/reconciliations/iso-iana-2026

dik world reconcile-audit --dir data/reconciliations/iso-iana-2026
```

L'output contient un JSONL de correspondances **candidates** (enregistré, déprécié, absent du snapshot IANA) et un manifeste avec SHA-256 de l'ISO, du registre, des enregistrements et les comptes. **Aucun** `exactMatch`, KQ, dictionnaire vérifié ou locale couverte ne résulte de cette opération.

## Instancier un catalogue mondial clairsemé

Un inventaire de démarrage existe déjà sous `examples/world-dictionaries/collection-slots-v0.3/`.

Pour une nouvelle version :

```sh
dik world collection-init \
  --index examples/world-dictionaries/language-code-candidates.jsonl \
  --manifest examples/world-dictionaries/language-code-candidates.manifest.json \
  --output-dir data/world/slots-v1

dik world collection-audit --dir data/world/slots-v1
```

Chaque enregistrement est un **emplacement non peuplé**, avec le code ISO, la dénomination de source, les tags candidats, le type, la portée, et des statuts explicitement vides : `iana_status=not_checked`, `source_links=[]`, `crosswalk_status=none`, `verified_lexical_entries=0`, `gf_status=not_mapped`, `published_dictionary_shards=0`.

Une source effectivement observée, une locale supportée, une traduction vérifiée et un dictionnaire publié constituent des **états différents**. Les types de langues ne définissent pas le nombre exact des langues du monde et les 7 910 codes ne couvrent pas automatiquement toutes les variantes ou tous les dialectes.

## Garanties et limites

1. Toutes les écritures créent une destination nouvelle (aucun remplacement silencieux).
2. Les fichiers restent la source des preuves, les hash et rapports peuvent être réexécutés.
3. Les identités Framework, crosswalks et dictionnaires `curated` **ne sont jamais modifiés**.
4. Aucune licence des 25 ressources candidates n'est déclarée approuvée.
5. Les tests se servent d'une fixture IANA **synthétique**; la récupération HTTPS réelle et la validation contre le dernier registre disponible doivent être effectuées par l'opérateur.
