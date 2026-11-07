# 26 — Répertoire mondial de codes de langues (candidats, DIK-LEX-1)

**Statut : proposé, recherche uniquement — 2026-11-04.**

## Résultat reproductible

- `examples/world-dictionaries/language-code-candidates.jsonl` : **7 910 codes candidats ISO 639-3** issus de la copie locale de `pycountry 24.6.1` (source de référence `iso-codes`/Debian), et leurs *noms anglais de référence*, codes alpha-2 lorsque disponibles, portée et type.
- `language-code-candidates.manifest.json` : provenance du package/dataset, empreintes SHA-256, total et **statuts explicitement non validés**.
- `src/dik/world_languages.py` et son schéma : validation locale et reconstruction contrôlée, sans réseau. `pycountry` n'est requis que pour régénérer le snapshot, pas pour le consulter.
- Les types ISO sont `L` (vivante), `E` (éteinte), `A` (ancienne), `H` (historique), `C` (construite), `S` (spéciale). Portées `I` (individuelle), `M` (macrolangue), `S` (spéciale).

**Ne pas confondre :** code ISO 639-3, tag BCP 47, locale (script/région), lexème Wikidata L, identifiant Kristal KQ/KP, dictionnaire réellement importé. Ils ne s'équivalent pas. Le répertoire inclut des langues historiques, artificielles, des macrolangues et des codes spéciaux. Il n'est **pas** un comptage strict des langues vivantes ni une liste exhaustive de toutes les variétés linguistiques.

## Commandes

Depuis la racine du dépôt (avec `PYTHONPATH=src`, ou package installé) :

```sh
PYTHONPATH=src python -m dik.world_languages inspect \
  examples/world-dictionaries/language-code-candidates.jsonl \
  examples/world-dictionaries/language-code-candidates.manifest.json

# Développeurs : régénération explicite à partir du pycountry installé
PYTHONPATH=src python -m dik.world_languages build \
  examples/world-dictionaries/language-code-candidates.jsonl \
  examples/world-dictionaries/language-code-candidates.manifest.json
```

En production, **ne pas** régénérer sans verrouiller et vérifier la version et le SHA de `iso639-3.json`. Les différences sont soumises à revue humaine. `source_data_sha256` est consigné comme attestation du fichier vu au moment de la génération; l'inspection courante vérifie le SHA du **JSONL**, pas l'existence du dataset de construction original.

## Sécurité et droits

Cette extraction est un **index de découverte**, non une copie de dictionnaires tiers, un tableau de traductions, une preuve `exactMatch` ou une couverture linguistique. Les noms anglais proviennent de `pycountry` et de sa copie de `iso-codes`; consigner les avis de licences/attribution avant redistribution intégrée en produit (métadonnées `pycountry`: LGPL-2.1-only). Ne pas supposer que le statut de licence de dictionnaires externes est identique à celui des codes de langue.

La ressource IANA est la référence officielle pour la validation de tags BCP 47 (RFC 5646). Elle n'a **pas été importée** dans ce snapshot (accès réseau indisponible au moment de la génération). Les codes ISO ne sont donc pas marqués « IANA validés », et aucune règle d'alias, variante, script, région ou héritage CLDR n'est appliquée.

Sources : [pycountry](https://github.com/pycountry/pycountry), [IANA Language Subtag Registry](https://www.iana.org/assignments/language-subtags-tags-extensions), [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646.html), [Unicode CLDR](https://unicode.org/reports/tr35/).

## Intégration future (toujours hors du canon)

1. Épingler le registre **IANA** complet et construire un valideur BCP 47 + correspondances `alpha3 ↔ preferred tag` révisées.
2. Ajouter scripts/régions/variantes/aliases CLDR avec versions et licences séparées, **sans** prétendre à une couverture lexicale.
3. Relier les *sources candidates* de dictionnaires à chaque langue **après** examen des preuves d'existence et des droits; en l'absence de source, laisser le tableau clairsemé.
4. Importer Wikidata Q/P uniquement après crosswalks révisés, et L/S/F par un adaptateur indépendant; les extraits de dictionnaires tiers exigent licence et attestation.
5. Qualifier les étapes de promotion avec les gates DIK-LEX-1; ne pas toucher au Framework v11 vendorié.


## Étape 3 — réconciliation et catalogue clairsemé

Le code candidat DIK-LEX-1 v0.3 ajoute un parseur de registre IANA TXT local, un vérificateur conservateur de tags, une réconciliation ISO→IANA et un index de **7 910 emplacements vides**. Un véritable registre IANA courant doit encore être téléchargé/vérifié par l’opérateur : la fixture fournie est synthétique. Voir [27](27_BCP47_IANA_ET_RECONCILIATION.md). La sortie est candidate; aucun `exactMatch` ni dictionnaire n’en résulte.
