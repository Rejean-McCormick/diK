# 25 — Collection mondiale de dictionnaires : démarrage prudent

**État : proposition DIK-LEX-1, exploration seulement.**

## Architecture retenue

- `Kristal-Framework` : source normative des identités `(namespace,KQ/KP)` et des couches de dictionnaires v11.
- `diK` : découverte des sources, audit, import et curation sans mutation du canon.
- `Wikidata Q/P` : libellés de concepts externes, utilisables seulement après crosswalk accepté `exactMatch`.
- `Wikidata L/S/F` : lemmes, sens et formes, **pas** des étiquettes KQ/KP par simple correspondance orthographique.
- `SemantiK/GF` : adaptation grammaticale éventuelle, indépendante de l'identité et des couches publiées.

## Démarrage du registre mondial

Le fichier `examples/world-dictionaries/source-inventory.json` est un **inventaire de découverte**, pas une collection téléchargée ou un dictionnaire publié. Chaque `candidate_sources` est une piste de vérification; `coverage=not_measured` signifie qu'aucune couverture n'est certifiée. Une locale peut être déclarée sans aucune entrée. Le seed recense Wikidata Q/P, Wikidata L/S/F et Wiktionary (conditions de réutilisation distinctes, non importé), et contient sept tags à titre de tests de scripts et variantes; il ne prétend pas couvrir toutes les langues.

Exécuter hors ligne :

```sh
python -m dik.source_inventory examples/world-dictionaries/source-inventory.json
python -m pytest -q tests/test_source_inventory.py
```

## Étapes à suivre (révisées par DIK-LEX-1 v0.3)

1. Réconcilier le registre IANA BCP 47 et les alias de locale avec une version pinée, en gardant le tag source original.
2. Inventorier toutes les langues cibles comme **locales connues mais non traduites**, avec script, variété et dénominations source distincts; ajouter sources/droits et attestations.
3. Construire l'adaptateur Q/P pour convertir uniquement les labels liés à un crosswalk exact accepté en couches Framework v11 vérifiées.
4. Construire un **adaptateur L/S/F indépendant** : sens, lemmes, flexion et provenance, sans promotion automatique dans le graphe.
5. Étudier Wiktionary, CLDR, ressources linguistiques et dictionnaires locaux **un par un**, avec analyse licence, qualité, fréquence de mise à jour et autorisation de redistribution. Les textes propriétaires ne sont pas importés parce qu'un ID Wikidata pointe vers eux.
6. Qualifier les couches `external`/`curated` via revue, hash, publication atomique et couverture directe/fallback/missing; tester l'interop avec Authoring Kit et GF.

## Ce qui est prouvé, et ce qui ne l'est pas

Le schéma et les tests démontrent uniquement que le registre refuse certaines incohérences et ne réclame aucune traduction disponible. Le code ne valide pas encore toute la grammaire BCP 47, ne télécharge pas de dumps, n'évalue pas les licences et n'exécute aucune qualification GF ou massivement multilingue.

Sources officielles consultées : https://www.wikidata.org/wiki/Wikidata:Licensing ; https://www.wikidata.org/wiki/Wikidata:Lexicographical_data/Documentation ; https://www.iana.org/assignments/language-subtags-tags-extensions

## Extension concrète — codes mondiaux candidats (étape 2)

Voir [`26_LANGUES_MONDE_CANDIDATES.md`](26_LANGUES_MONDE_CANDIDATES.md) : un index ISO 639-3 de 7 910 codes, manifesté et vérifié hors ligne. **Cela ne remplace pas le registre IANA, ne certifie aucune locale BCP 47 et n'ajoute aucun dictionnaire publié.** L'exemple initial de sept locales reste un échantillon indépendant de validation syntaxique.


## Mise à jour cumulative DIK-LEX-1 v0.3

Les modules expérimentaux IANA/BCP47, index clairsemé des 7 910 codes, import d’observations Wikidata L/S/F et handoff GF **existent désormais dans cette branche candidate**. Voir [27](27_BCP47_IANA_ET_RECONCILIATION.md), [28](28_WIKIDATA_LEXEMES_GF_PIPELINE.md) et [29](29_ROADMAP_COLLECTION_MONDE.md). Les étapes 1, 2 et 4 ci-dessus doivent donc être lues comme des programmes de **qualification, d’extension et de vérification sur données réelles**, pas comme une absence totale de code. Aucun dictionnaire publié ni alignement KQ approuvé n’est créé par ces nouveaux modules.
