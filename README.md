# diK — Implémentation 1.0.0-alpha.6

**Statut : version alpha**, pas le logiciel 1.0 certifié. Ce dépôt inclut le socle fonctionnel v0.3, de nouveaux modules 1.0 et la [spécification candidate.2](spec/diK-1.0/START_HERE.md).

Le graphe KQ/KP reste la source de vérité; les mots sont dans les dictionnaires, et les Wikidata Q/P sont des identifiants *externes* reliés par crosswalk approuvé. Une projection enrichie ne supprime ni ne renomme les identifiants KQ/KP.

## Démarrage hors ligne

```bash
python -m pip install -e .
dik project inspect --project examples/demo/dik.project.json
dik coverage report --project examples/demo/dik.project.json --locales fr,en,fr-CA
dik index build --project examples/demo/dik.project.json --output /tmp/dik-search.sqlite
dik index lookup --project examples/demo/dik.project.json --index /tmp/dik-search.sqlite --term 'Saint Augustin' --locale fr --kind KQ
dik serve --project examples/demo/dik.project.json --index /tmp/dik-search.sqlite --port 8765
# Option locale : créer des catalogues candidats sans écrire dans le Kristal
dik serve --project examples/demo/dik.project.json --index /tmp/dik-search.sqlite --workspace /tmp/dik-revisions --port 8765
```

### Flux de travail

- `dik dictionaries audit|resolve|compare|conflicts|conflict-detail` : contrôler les lexiques, rapprocher les observations de couches et expliquer les ambiguïtés **sans fusionner les KQ/KP**.
- `dik curate publish` : créer une **nouvelle** version de dictionnaires revue, sans modifier les anciens.
- `dik index build|lookup` : index local reconstructible et candidats lexicaux (jamais identité acceptée).
- `dik review append|list` : journal append-only de décisions avec preuves KS; aucune signature d'identité forte.
- `dik reconcile` : nouvelle révision de crosswalk externe, contrôlée par le Framework et soumise au propriétaire.
- `dik portfolio coverage` : complétude multi-Kristals et par langue.
- `dik legacy plan|verify` : plan non exécutable; l'Authoring Kit est seul responsable de publier un nouveau canon.
- `dik patch verify` : vérifier un patch candidat, sans appliquer.
- `dik wikidata import-local` et `dik sync import-local` : importer depuis un dump local, garder provenance et snapshots.
- `dik projection export|verify|restore` : sortie annotée/épurée et retour exact au canon depuis le JSON réversible.
- `dik serve` : atelier Web local : concepts, correspondances, matrice linguistique paginée, projection épurée/annotée et export réversible. Par défaut **lecture seule**; avec `--workspace`, création de **catalogues lexicaux candidats isolés**, sans modification canonique ni authentification multi-acteur.

Voir `dik --help`, puis `dik <module> --help` pour les paramètres exacts.

## Conformité et sécurité

Les nouveaux `contracts/*.json` sont **candidats** et ne modifient pas les contrats officiels du Framework 11.0.0-draft.3. Les sources référencées sont verrouillées dans la spécification; leurs empreintes doivent être vérifiées avant une release stable.

Les noms de réviseurs sont pour l'instant déclaratifs; une preuve d'authentification est nécessaire avant de considérer une gouvernance multi-acteurs comme fiable. Les sauvegardes, les benchmarks réels, la synchronisation Wikidata distribuée et la certification cross-repo restent à effectuer.

Lire [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) pour la liste précise de ce qui n'est **pas** encore livré.

Licence : AGPL-3.0-or-later (voir `LICENSE`). Python >= 3.11; `jsonschema >=4.21,<5`.

## Interface locale alpha.2 — parcours

Après `dik serve`, ouvrir `http://127.0.0.1:8765/`. L'interface suit trois tâches : **chercher un concept et vérifier sa traduction**, **voir les manques linguistiques**, **lire ou exporter un Kristal**. Les diagnostics et endpoints JSON sont secondaires.

La recherche inverse demande un index SQLite `--index` construit auparavant; sans index, le formulaire explique comment le créer. La couverture fonctionne sans cet index. L’atelier est exclusivement lié à `127.0.0.1`. Aucun service public, aucune API d’approbation Wikidata et aucune signature de réviseur ne sont fournis.

L’option `--workspace` permet seulement de créer une nouvelle révision de dictionnaire avec nom de réviseur *déclaratif*. Le dossier doit être distinct du projet canonique. Le fichier de projet ne bascule pas automatiquement vers la nouvelle révision. Consultez [la spécification UI et sécurité](docs/docs/19_ATELIER_WEB_v1-alpha2.md).

## Nouveauté alpha.3 — détecter les désaccords entre dictionnaires

```bash
dik index build --project examples/demo/dik.project.json --output /tmp/dik-alpha3-index.sqlite
dik dictionaries conflicts --project examples/demo/dik.project.json --index /tmp/dik-alpha3-index.sqlite --locale fr
dik dictionaries compare --project examples/demo/dik.project.json --index /tmp/dik-alpha3-index.sqlite --locale fr --id KQ1001
```

La fiche KQ présente désormais les observations de chaque couche et leur provenance. Un écran de liste des contradictions se trouve dans **Concepts et traductions**, sans nouvel onglet technique. Les anciens index SQLite doivent être reconstruits pour les nouvelles commandes, tandis que les anciennes projections diK restent compatibles. Voir [la spécification d'implémentation](docs/docs/20_CONCILIATION_LEXICALE_v1-alpha3.md).


## Alpha.4 — téléchargements Wikidata et comparaison de snapshots

Les nouveaux parcours sont **explicites** : `dik sync fetch` récupère un dump HTTPS officiel avec possibilité de reprise HTTP conditionnelle ; `dik sync import-mirror` exige un SHA-256 approuvé indépendamment ; `dik sync diff` détecte les changements lexicaux entre catalogues importés, en flux et sans modifier le canon. Voir [la documentation détaillée](docs/docs/21_MIROIR_WIKIDATA_REPRENABLE_v1-alpha4.md).

Les dumps locaux historiques restent pris en charge. Aucun traitement automatique de redirections Wikidata ni ingestion de deltas arbitraires n'est annoncé.


## Alpha.5 — évolutions d’identité Wikidata

`dik sync evolution` produit un **rapport de revue uniquement** sur des observations externes **normalisées** de redirections Q/P, de retraits et de scissions candidates. Il suit les chaînes de redirection et détecte les collisions avec les mappings actifs sans fusionner de KQ/KP et sans modifier le crosswalk. Le rapport indique les informations de provenance fournies par la source et les empreintes, mais ne les confond pas avec une preuve d’équivalence.

Voir [la documentation alpha.5](docs/docs/22_EVOLUTIONS_WIKIDATA_v1-alpha5.md) pour le format, les commandes et les limites. **L’extraction ciblée des redirections depuis les réponses officielles MediaWiki est fournie en alpha.6 ; le moteur de deltas global reste à développer.**


## Alpha.6 — Sources officielles de redirection Wikidata

Deux parcours **explicites et séparés** :

1. `dik sync probe-redirects` interroge par lots l’API officielle MediaWiki **uniquement** pour les Q/P déjà présents dans des alignements exacts approuvés. Nécessite l’accès Internet, un User-Agent identifiable et un opérateur conscient des quotas. Archive les réponses JSONL sans modifier d’identités.
2. `dik sync extract-redirects` normalise les réponses API enregistrées (`action=query&redirects=1`, JSON ou JSONL) en événements immuables compatibles avec `dik sync evolution`. Les SHA-256 sont vérifiables et les sources conservées. Les pages manquantes ne deviennent **jamais** automatiquement des retraits.

```bash
# Parcours réseau ciblé (sur demande seulement)
dik sync probe-redirects \
  --crosswalk examples/demo/external-crosswalk.example.json \
  --registry examples/demo/identity-registry.example.json \
  --namespace example.org/kristal-demo \
  --user-agent 'diK Wikidata audit (contact: admin@example.org)' \
  --output /tmp/wikidata-queries.jsonl

# Extraction HORS réseau, archivable puis révisable
dik sync extract-redirects --source /tmp/wikidata-queries.jsonl \
  --format action-api-jsonl --snapshot wd-review-2026-10-16 \
  --output /tmp/wikidata-observations.jsonl

# Analyse sans mutation du crosswalk ou du graphe
dik sync evolution --observations /tmp/wikidata-observations.jsonl \
  --crosswalk examples/demo/external-crosswalk.example.json \
  --registry examples/demo/identity-registry.example.json \
  --namespace example.org/kristal-demo --snapshot wd-review-2026-10-16
```

L’analyse d’un snapshot historique ne doit pas supposer que l’API actuelle permet de le reconstituer. Aucune suppression, scission ni fusion n'est inférée d'une absence de résultat. Voir [le guide alpha.6](docs/docs/23_EXTRACTION_REDIRECTIONS_MEDIAWIKI_v1-alpha6.md).

### Alpha.7 — traiter ta copie locale Wikidata

Une nouvelle commande `dik sync import-large` importe les lexiques associés aux KQ/KP qui possèdent déjà une correspondance Wikidata exacte approuvée. Elle reprend après interruption grâce à SQLite et publie un nouveau snapshot sans modifier le canon.

```bash
dik sync import-large --dump /chemin/vers/wikidata.json.bz2 \
  --crosswalk /projet/crosswalk.json --registry /projet/registry.json \
  --namespace mon.espace --snapshot 2026-10-16 \
  --locales fr,en,fr-CA --root /imports-dik
```

La lecture des fichiers comprimés est en flux, mais la **reprise** se fait en relisant les lignes décompressées jusqu'au checkpoint. Pour la provenance externe, utiliser en plus `--approved-sha256` avec une empreinte obtenue par une voie indépendante.

[Limites, protections et plan d'exploitation](docs/docs/24_IMPORT_INDUSTRIEL_LOCAL_v1-alpha7.md).
