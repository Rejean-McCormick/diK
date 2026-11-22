# Qualification — diK 1.0.0-alpha.6

**Statut :** alpha locale, pas diK 1.0 final ni certification industrielle.

## Tests exécutés

- `PYTHONPATH=src pytest -q` : **111 tests Python réussis et 11 sous-tests**. Dont 17 tests additionnels alpha.6 pour extraction, pipeline, intégrité, fichiers malformés, absence de réponse et consultation simulée de l'API.
- `DIK_SOURCE_DATA_ROOT=... KRISTAL_FRAMEWORK_ROOT=... python spec/diK-1.0/tools/validate_documentation.py --strict` : **PASS** ; 13 sources épinglées, 5 archives, 5 fixtures Framework, 27 oracles documentaires, 3 tests négatifs de schéma.
- `dik sync extract-redirects` : JSON/JSONL MediaWiki conservé et normalisé pour le moteur `sync evolution` de l'alpha.5 ; le graphe et le crosswalk restent inchangés.
- `dik sync probe-redirects` : requêtes simulées sur endpoint HTTPS officiel, scope crosswalk, limites, refus des URL redirigées vers des sites tiers et des réponses contenant un identifiant inattendu.
- Aucun accès réel à l’API Wikidata effectué dans cette qualification. La couverture des dumps massifs et des deltas n'est pas démontrée.

## Règles vérifiées

- Aucun Q Wikidata ne remplace un KQ dans le canon ; aucune corrélation lexicale ne génère d'`exactMatch`.
- Une redirection Wikimedia est une **observation** à réviser, et non une décision de fusion ; les sorties sont non destructives.
- `query.pages[].missing` ne signifie pas une suppression ni une scission prouvée.
- `--approved-sha256` est facultatif pour l'extraction hors réseau; sans hash approuvé indépendamment la preuve d'intégrité amont est limitée. Même un hash vérifié ne prouve pas à lui seul l'origine des données.
- Le serveur Web local, les autres fonctions CLI et les formats compact/verbose restent disponibles et leurs tests historiques passent.

## Limitations / travaux restants

1. Qualification par des appels effectifs à `www.wikidata.org` avec quotas et gestion des erreurs réseau réelles.
2. Parseur natif des redirects Wikidata en dumps SQL/RDF et exports historiques, séparé de l'API ciblée.
3. Deltas incrémentaux massifs, reprise d'import segmentée, monitoring des fusions/scissions avec preuves de révisions.
4. Authentification de réviseurs, signatures des décisions, finalisation du workflow d'approbation.
5. Publication de nouveaux Kristals avec l'Authoring Kit et tests croisés complets.
6. TCK intégral, benchmarks Wikidata réel/300 langues, résilience et tests de charge.

Se référer à `docs/docs/23_EXTRACTION_REDIRECTIONS_MEDIAWIKI_v1-alpha6.md`.

## Alpha.7 — contrôles effectués dans cet environnement

- `PYTHONPATH=src pytest -q --disable-warnings` : **123 tests Python réussis, 11 sous-tests réussis**.
- Les 12 tests alpha.7 couvrent les formats, les interruptions, l'intégrité, les doublons, les limites, la CLI et 301 tags syntaxiquement valides.
- Import comparé octet à octet à l'ancien importeur sur la fixture à deux langues.
- Essai synthétique de 50 000 entités / 4,3 Mo JSONL : ~1,80 s, ~121 Mo pic RSS (une seule correspondance acceptée ; machine de test uniquement).
- **Non exécuté** : validation sur dump Wikidata complet, 300 vraies langues avec traductions, multi-utilisateurs, pannes système physiques.


## DIK-LEX-1 v0.3 — qualification de l'overlay cumulatif (2026-11-04)

- Suite locale exécutée avec `PYTHONPATH=src python -m pytest -q` sur la copie préparée : **206 tests réussis et 11 sous-tests** dans cette copie de préparation; la validation post-overlay sur la racine du snapshot est à contrôler séparément.
- Import des fixtures L/S/F (JSONL, JSON array, gzip, bzip2), contrôles de collision, taille, empreintes et création de handoff GF **sans mapping**.
- Réconciliation de 7 910 codes contre une **fixture IANA synthétique**, audit d'index et refus d'alterations/affirmations de couverture.
- Récupération HTTPS IANA uniquement avec **opener simulé** : hôte/destination verrouillés et refus des redirections suspectes; aucun accès réel réseau validé.
- Les valeurs calculées à partir de la fixture ne sont **pas** des métriques officielles IANA.
- Pas de qualification industrielle ni de TCK inter-dépôts; Framework vendorié et contrats gelés conservés.

## Scanner 14 langues — qualification additionnelle 2026-11-21 (copie isolée)

- Exigences : **COV- (complétude), LEX- (libellés/provenance), ID-/XW- (identité/alignment), SEC- (sortie non destructive)**.
- Base : snapshot `znapshot_diK_11211131.zip` ; Framework v11 `11.0.0-draft.3` inchangé.
- `PYTHONPATH=src pytest -q tests/test_scan14.py --disable-warnings` : **8 tests réussis** (mode scanner, déterminisme des 14 cibles, intégrité, refus d'écrasement, langue non déclarée, corpus non aligné, repli, refus mapping CSV non qualifié).
- `PYTHONPATH=src python -m pytest -q --disable-warnings` : **231 tests réussis, 1 ignoré, 11 sous-tests réussis** sur cette copie isolée (voir les journaux livrés avec le patch).
- Fixture : `examples/demo/dik.project.json` uniquement. Les 42 cellules (3 KQ/KP × 14 langues) sont **2 directes, 4 manquantes dans les langues déclarées, 36 non configurées**. Ces chiffres **ne couvrent pas** les dictionnaires du poste de l'utilisateur.
- **NON EXÉCUTÉ** : qualification sur tous les dictionnaires réels, couverture industrielle, comparaison live inter-dépôts, approbation d'alignements inter-projets, tests Windows du correctif.
- Aucune mutation de graphe, registre, crosswalk, schéma Framework ni snapshot lexical. Aucun accès réseau.
