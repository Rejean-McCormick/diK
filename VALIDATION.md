## Validation V5.7 — DIK-LEX-1 / EncyK local

Commande : `PYTHONPATH=src python -m pytest -q`. Les tests de
`tests/test_local_lexical_library_v57.py` couvrent l’index SQLite EncyK
v0.2, les 14 langues exactes, l’absence de repli `nb→no/nn`, l’exclusion
des sources partielles, la reprise de curseur, la modification de source,
les droits non approuvés, la recherche et l’export ZIP expurgé.

Ce test utilise une fixture SQLite, **pas** l’index de 13 Gio sur Windows.
Aucune publication ou autorisation de licence n’est certifiée par les tests.

## V5.4 — Validation des adaptateurs locaux (2026-11-23)

Les tests supplémentaires utilisent des **valeurs synthétiques pour les noms de champs observés dans le vrai bilan Windows V5.3**, et ne prétendent pas avoir les lignes JSONL des sources réelles. Ils vérifient : namespace et type KQ/Q–KP/P stricts, absence de promotion du statut `accepted` revendiqué par un fichier, rôles sujets/prédicats non lexicaux, Q/P observés hors rôle sujet, édition de l'index officiel invalidant un checkpoint, suivi des fichiers vides et invariance des compteurs. Voir `tests/test_wikidata_v54.py` et [62](docs/docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md).

Les tests Windows PowerShell 7 natifs devront être confirmés par le ZIP de bilan local. L'installateur incrémental doit refuser tout fichier de code inconnu et préserver les fichiers tiers.

# Qualification — diK alpha.8 (22 novembre 2026)

## Validation additionnelle actuelle

- `PYTHONPATH=src pytest -q` : **269 tests réussis, 1 ignoré, 11 sous-tests réussis** dans l'environnement de préparation de ce correctif.
- `tests/test_resource_locator.py` et `tests/test_gf_manifest_guard.py` : cas positifs et adversariaux du localisateur, du manifeste GF non-objet et des registres forgés.
- Essai réel limité à deux Kristals extraits du snapshot du portefeuille officiel : 16 références localisées, 7 518 cellules ID-locale contrôlées en 14 langues ; résultats **non extrapolables** aux 126 sur le PC cible.
- Aucune exécution PowerShell 7/UAC sur le Windows utilisateur ; pas de dump Wikidata complet ni d'exécution GF certifiée. La qualité du futur mapping GF, la provenance de dumps et les licences restent non validées.
- Aucun transfert ou modification des sources. Les dossiers `reports/` sont exclus des archives du dépôt.

---

## Historique — qualification alpha.6

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

### Revue du paquet V4.1 (23 novembre 2026)

- Tests Python du dépôt fourni : 270 réussis, 1 ignoré, 11 sous-tests réussis.
- Corrections : tableau PS7 du portefeuille ; absence de succès trompeur sur registre périmé ; messages explicites sur ressources non hashées.
- Pack original V4 non recommandé sans ces corrections.
- PowerShell 7 et le scan complet sur la machine cible non exécutés dans cette revue.
- Les manifestes de release historiques alpha.7 ne certifient pas le contenu alpha.8.


## Qualification V5 (2026-11-23)

La suite du dépôt et les nouveaux tests QID/qualification ont été relancés dans l’environnement de préparation. Le registre de 5 269 références a été **analysé en métadonnées seulement** ; les 5 269 chemins Windows n’y sont pas montés. Les nombres du registre ne prouvent donc ni l’exécution des analyseurs sur tous les fichiers réels ni la disponibilité de formes lexicales approuvées. L’installateur PS7 doit encore être exécuté sur le poste cible. Voir chapitres 48–50.


## V5.2 — Tests supplémentaires et limites

Tests ciblés `tests/test_wikidata_thematic_v52.py` : comparaison de Q/P explicitement acceptés, refus de `L/S/F`, collision entre deux fichiers, SHA et fichier changé, copies identiques, 14 locales exactes et préservation des totaux `resolve14`. `qid-lexicon.jsonl` réel n'est pas modifié et ses mots ne sont pas automatiquement activés. Suite globale exécutée sur la copie de dépôt, voir le journal de validation dans le paquet de distribution. L'installation PS7 sur Windows et la vraie inspection des 40 JSONL nécessitent une exécution locale.


## Contrôle documentaire V5.3 (23 novembre 2026)

Contrôles attendus pour ce **pack de documentation** : chapitres 53–60, ADR-DIK-LEX-6, exemples non normatifs, liens relatifs, correspondance des chiffres au bilan V5.2, et absence de modifications `src/`, `tests/`, `pyproject.toml` ou des dictionnaires. **Aucun test du futur lecteur V5.3 ne peut être annoncé comme réussi tant que ce code n'existe pas.** Les critères à implémenter sont au chapitre [59](docs/docs/59_PLAN_IMPLEMENTATION_TESTS_V5_3.md).


## V5.3 (alpha.11)

Validation à effectuer avec `PYTHONPATH=src pytest -q` ; voir les nouveaux tests `tests/test_wikidata_v53.py`. Le test de reprise couvre 150 001 lignes et les conflits. **Aucune réussite Windows PS7 native n’est affirmée à ce stade.**


Validation en environnement isolé (23 novembre 2026) : **301 réussis, 1 ignoré, 11 sous-tests réussis**. Les vérifications de sécurité du paquet sont rapportées séparément ; elles ne prouvent pas PowerShell natif.


## V5.5 alpha.13 — Validation des quatre fichiers réels (2026-11-23)

Les quatre sources transférées ont été analysées jusqu'à la fin : **46 889 objets/QID distincts dans leurs fichiers**, et **66 755 étiquettes explicites** `en`/`sv`. Le lecteur V5.5 est testé sur ces quatre fichiers en lecture seule ; `tests/test_wikidata_v55.py` couvre également les tableaux malformés, les interruptions et reprises, les URL non autorisées, les langues strictes, les changements SHA et l'invariance de la couverture dans `resolve14`. **Ce résultat n'établit pas de recoupement avec les 1 776 liens acceptés du Windows**, lequel devra être mesuré par la prochaine exécution locale.


## V5.6 alpha.14 — Validation du Source Manager en ligne

- `PYTHONPATH=src python -m pytest -q` : **326 tests réussis, 1 ignoré, 11 sous-tests** (sur le code révisé, avant tests de paquet).
- `tests/test_online_sources_v56.py` : réseau mocké, consentement explicite, requête limitée aux Q/P et aux 14 langues, CC0, aucun fallback, cache SHA, reprise, corruption, redirections, et audit + export expurgé.
- Les téléchargements HTTP Wikidata **n'ont pas été effectués sur le PC Windows** lors de cette validation.
- Aucun tableau Kaikki/GF n'est téléchargé ni lié sémantiquement en V5.6. Les nouveaux résultats sont candidats et n'altèrent pas le canon ni les compteurs validés.

## Validation V5.8 — Pont de sens EncyK, lecture seule

Les tests de `tests/test_semantic_evidence_bridge_v58.py` répliquent les
schémas v0.5/v0.6 des outils EncyK : SHA/fingerprint de l'index, rapprochement
exact de candidat, exclusion des homographes non probants, lien source/ligne,
14 langues exactes, refus de modification locale et de source non autorisée,
ZIP sans données lexicales et absence de changement des bases V5.7.
Les tests utilisent un mini-corpus synthétique. L'exécution native avec les
bases EncyK réelles, dont WAL volumineux, doit être confirmée sur Windows.

## V5.10 — Validation canon multirévision

- Suite Python complète : 350 tests passés, 1 ignoré, 11 sous-tests passés.
- Test complémentaire : trois révisions dont deux liens Q/P répétés et un
  autre contradictoire ; dédoublonnage séparé et conflit signalé sans approbation.
- Test sur snapshot officiel du 24 novembre : 126 index, 77 Kristals V11,
  180 révisions, 25 741 liens exacts par révision et 12 919 distincts,
  7 artefacts absents, 0 conflit transrévision observé, 0 lien promu.
- 7 graphes volumineux non analysés dans le test local : présence constatée,
  contrôle de namespace de ces graphes **non effectué**.
- Installation native Windows : à valider sur les dépôts vivants.

## Validation V5.11 — sélection dérivée et refus de promotion

- Suite complète Python (Linux, Python compatible) : **355 tests passés, 1 ignoré, 11 sous-tests passés**.
- Cas contrôlés : singleton, divergence, observations équivalentes, absence de V11, conflit d'exactMatch, décision explicitement revuée + SHA, refus de décision obsolète après changement d'un octet, requêtes bidirectionnelles, export local non destructif.
- Test du snapshot officiel (extraction limitée aux artefacts V11 du snapshot, pas copie complète des autres artefacts canoniques) : 126 index, 77 Kristals V11, 180 révisions, 5 singletons consultables en vue dérivée, 67 multirévisions divergentes, 1 observations équivalentes, 4 ensembles avec graphes non inspectés, 49 sans V11, 0 approbation globale nouvelle.
- **Ne pas utiliser le nombre d'artefacts « manquants » de cette extraction partielle comme bilan Windows** : elle omet volontairement les contrats non V11. Le dernier diagnostic Windows complet indiquait 7 artefacts absents.
- Test d'installation native PowerShell 7 et contrôle des fichiers vivants **restent à exécuter sur Windows**. L'installation ne modifie ni Kristal ni EncyK.
