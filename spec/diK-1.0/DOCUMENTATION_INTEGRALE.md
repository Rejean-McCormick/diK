# diK 1.0 — Documentation intégrale révisée (candidate.2)

> **SPÉCIFICATION CIBLE.** Cette compilation ne remplace pas les JSON Schema officiels du Framework v11. Le logiciel diK 1.0 n’a pas été qualifié. Les décisions candidate.2 demandent encore ratification humaine.

## Table des matières

1. `START_HERE.md`
2. `README.md`
3. `REVISION.md`
4. `CHANGELOG.md`
5. `SPEC_LOCK.md`
6. `AGENTS.md`
7. `RUNBOOK_IA.md`
8. `DECISIONS_OUVERTES.md`
9. `SOURCES_ET_DECISIONS.md`
10. `VALIDATION.md`
11. `IMPLEMENTATION_BACKLOG.md`
12. `docs/01_CONTRATS_ET_FRONTIERES.md`
13. `docs/02_IDENTITES.md`
14. `docs/03_DICTIONNAIRES.md`
15. `docs/04_CONCILIATION.md`
16. `docs/05_WIKIDATA.md`
17. `docs/06_PROJECTIONS.md`
18. `docs/07_MIGRATION.md`
19. `docs/08_COMPLETUDE.md`
20. `docs/09_ARCHITECTURE.md`
21. `docs/10_STOCKAGE_INDEXATION.md`
22. `docs/11_API_CLI.md`
23. `docs/12_INTERFACE.md`
24. `docs/13_SECURITE.md`
25. `docs/14_PERFORMANCE.md`
26. `docs/15_TESTS_TCK.md`
27. `docs/16_RELEASE.md`
28. `docs/17_TRACABILITE.md`
29. `docs/18_INTEGRATION.md`
30. `docs/19_LOCALES.md`
31. `docs/20_ETATS_ET_TRANSACTIONS.md`
32. `docs/21_ERREURS_OBSERVABILITE.md`
33. `docs/22_EVOLUTION_DES_CONTRATS.md`
34. `docs/23_PROFIL_LOCAL_GOUVERNANCE.md`
35. `docs/24_ALGORITHMES_ORACLES.md`
36. `docs/25_GATES_CI_EXECUTABLES.md`
37. `docs/26_BANC_PERFORMANCES.md`
38. `decisions/ADR-0001-NOYAU-IMMUTABLE.md`
39. `decisions/ADR-0002-MONOLITHE-MODULAIRE.md`
40. `decisions/ADR-0003-PROFIL-LOCAL-1_0.md`
41. `contracts/README.md`
42. `examples/README.md`
43. `tests/README.md`
44. `.github/PULL_REQUEST_TEMPLATE.md`

---


---

<a id="doc-start-here-md"></a>

## Document : `START_HERE.md`

# Commencer ici — diK 1.0 candidate.2

1. Lire [README.md](#doc-readme-md), [REVISION.md](#doc-revision-md) et [SPEC_LOCK.md](#doc-spec-lock-md) avant de modifier du code.
2. Lire [AGENTS.md](#doc-agents-md) et [RUNBOOK_IA.md](#doc-runbook-ia-md) si une IA/agent développe le dépôt.
3. Utiliser le [profil local et les décisions ouvertes](#doc-docs-23-profil-local-gouvernance-md) : aucune décision humaine n'est simulée.
4. Lire les [algorithmes exacts](#doc-docs-24-algorithmes-oracles-md), [oracles](#doc-tests-reference-vectors-json) et [gates CI](#doc-docs-25-gates-ci-executables-md).
5. Parcourir les [87 exigences individualisées](#doc-tests-requirements-json) et les [30 tests TCK](#doc-tests-tck-cases-json), tous non exécutés pour le logiciel 1.0.
6. Avant qualification, lancer le [validateur en mode strict](#doc-validation-md) contre les sources exactes épinglées.
7. Pour le produit final, respecter [performance](#doc-docs-26-banc-performances-md) et [release GO/NO-GO](#doc-docs-16-release-md).

**Statut : spécification cible consolidée ; pas logiciel final et pas API stabilisée sans ratification.**


---

<a id="doc-readme-md"></a>

## Document : `README.md`

# diK 1.0 — Spécification normative de référence

**Statut : SPECIFICATION CIBLE / candidate 1.0 (et NON produit 1.0 livré).**  
**Langue principale : français.**  
**Sources figées :** diK `0.3.0`, Kristal Framework `11.0.0-draft.3`, Kristal Authoring Kit `4.0.0-draft.2`, Kristal Integration Pack `0.2.0-alpha.1`, archive de 33 patterns d'architecture fournie.  
**Référence de conformité primaire :** les schémas et textes normatifs de Kristal Framework v11 draft.3. Un document diK ne peut pas les remplacer unilatéralement.

## Mission

diK gère les dictionnaires lexicaux, les correspondances entre référentiels, les projections linguistiques et les migrations *proposées* de Kristals vers le modèle canonique. **Une identité sémantique ne doit jamais dépendre d'un mot.** Les graphes canoniques utilisent exclusivement des identifiants de leur espace de noms (`KQ`, `KP`, `KA`, `KS`). Les mots sont dérivés et les correspondances Wikidata sont externes.

### Non négociable

1. **Le canon reste unique :** graphe/registre Framework ; ni diK, ni SQLite, ni Wikidata, ni la langue n'en deviennent la source d'autorité.
2. **KQ n'est pas Q Wikidata :** clé interne composée `(namespace_id, KQ…)`; `KP` propriétés, `KA` assertions, `KS` sources. Aucune fabrication de Q/P Wikidata.
3. **Deux répertoires distincts :** couches lexicales locales/importées d'une part ; *crosswalk* externe KQ↔Q/KP↔P de l'autre.
4. **Aucun remplacement aveugle de texte :** les littéraux, citations et documents ne sont pas des identifiants.
5. **Projections réversibles :** conserver l'identité exacte et le canon ; le Markdown « clean » est une **vue non réversible à lui seul**.
6. **Provenance, décisions, immutabilité :** un rapprochement reste candidat jusqu'à revue ; publication versionnée, jamais mutation silencieuse.
7. **Absence ≠ traduction :** langue sans entrée = état `missing`, sans libellé inventé ; fallback explicitement déclaré ≠ couverture directe.
8. **Backward compatibility :** lecture des anciens formats et anciens engagements sans altération ; nouvelle révision lors d'une migration approuvée.

## Ordre de lecture et priorité des normes

1. [`AGENTS.md`](#doc-agents-md) et [`SPEC_LOCK.md`](#doc-spec-lock-md) — consignes obligatoires au développeur et aux agents IA.
2. [`docs/01_CONTRATS_ET_FRONTIERES.md`](#doc-docs-01-contrats-et-frontieres-md) — périmètre, statuts des exigences.
3. [`docs/02_IDENTITES.md`](#doc-docs-02-identites-md), [`docs/03_DICTIONNAIRES.md`](#doc-docs-03-dictionnaires-md), [`docs/04_CONCILIATION.md`](#doc-docs-04-conciliation-md).
4. [`docs/05_WIKIDATA.md`](#doc-docs-05-wikidata-md), [`docs/06_PROJECTIONS.md`](#doc-docs-06-projections-md), [`docs/07_MIGRATION.md`](#doc-docs-07-migration-md), [`docs/08_COMPLETUDE.md`](#doc-docs-08-completude-md).
5. [`docs/09_ARCHITECTURE.md`](#doc-docs-09-architecture-md), [`docs/10_STOCKAGE_INDEXATION.md`](#doc-docs-10-stockage-indexation-md), [`docs/11_API_CLI.md`](#doc-docs-11-api-cli-md), [`docs/12_INTERFACE.md`](#doc-docs-12-interface-md).
6. [`docs/13_SECURITE.md`](#doc-docs-13-securite-md), [`docs/14_PERFORMANCE.md`](#doc-docs-14-performance-md), [`docs/15_TESTS_TCK.md`](#doc-docs-15-tests-tck-md), [`docs/16_RELEASE.md`](#doc-docs-16-release-md).
7. [`docs/17_TRACABILITE.md`](#doc-docs-17-tracabilite-md), [`docs/18_INTEGRATION.md`](#doc-docs-18-integration-md), [`docs/19_LOCALES.md`](#doc-docs-19-locales-md), [`docs/20_ETATS_ET_TRANSACTIONS.md`](#doc-docs-20-etats-et-transactions-md), [`docs/21_ERREURS_OBSERVABILITE.md`](#doc-docs-21-erreurs-observabilite-md), [`docs/22_EVOLUTION_DES_CONTRATS.md`](#doc-docs-22-evolution-des-contrats-md).

**Priorité en cas de contradiction :** Framework v11 draft.3 > contrats applicatifs diK existants de v0.3 pour la rétrocompatibilité > nouvelles exigences cibles du présent dossier. Une contradiction = `BLOCKED: CONTRACT_CONFLICT`, jamais une correction silencieuse.

## État du logiciel vs exigences cibles

| Fonction | diK 0.3 existant | diK 1.0 requis |
|---|---|---|
| Inspecter graphe/registre/crosswalk | Oui | Durcir invariants et indexation |
| Audit catalogues + empreintes | Oui | Publication atomique, audit incrémental |
| Import Wikidata local sélectif | Oui, hors réseau | Dump complet + reprise/synchronisation contrôlées |
| Couverture graphe/locale | Oui | Multi-Kristal + qualité + exports |
| Projection compacte réversible | Oui, profil applicatif | Contrat figé + compat v0.2 + quotas |
| Concilier plusieurs sources | Non complet | Oui, provenance + approbation |
| Recherche inverse lexicale | Non complète | Index/contextes/désambiguïsation |
| Plan de migration | Framework : schéma seulement | Production/soumission, exécution déléguée sous autorisation |
| API + interface | Non | Oui, utilisables hors ligne |
| Gros volumes + 300+ langues | Structure, pas qualification | Mesures réelles et budgets explicites |

## Livrables et utilisation

Cette archive est un **cahier des charges exécutable par des équipes/agents**, pas le code diK 1.0. `contracts/` contient des schémas **proposés de l'application diK**, placés dans un namespace de contrat distinct des schémas officiels Framework. `examples/` et `tests/` servent de base à la qualification. Aucun schéma Framework n'est redéfini.

Pour obtenir `1.0.0` stable, satisfaire tous les `MUST` et les critères bloquants de [`docs/16_RELEASE.md`](#doc-docs-16-release-md), avec résultats d'essais vérifiables sur le code produit. Un tableau de conception ou des tests de schémas ne prouvent pas la certification du produit.

## Addendum candidate.2 — dernière consolidation avant implémentation

- [`REVISION.md`](#doc-revision-md) : portée, limites et changements de cette révision.
- [`docs/23_PROFIL_LOCAL_GOUVERNANCE.md`](#doc-docs-23-profil-local-gouvernance-md) : profil local par défaut, sans ajout d'un serveur obligatoire.
- [`docs/24_ALGORITHMES_ORACLES.md`](#doc-docs-24-algorithmes-oracles-md) : algorithmes précis de résolution, restauration, complétude et migration.
- [`docs/25_GATES_CI_EXECUTABLES.md`](#doc-docs-25-gates-ci-executables-md) : validation documentaire stricte et gates de future certification.
- [`docs/26_BANC_PERFORMANCES.md`](#doc-docs-26-banc-performances-md) : banc de mesure reproductible, pas de performances inventées.
- [`tests/requirements.json`](#doc-tests-requirements-json) et [`tests/reference_vectors.json`](#doc-tests-reference-vectors-json) : exigences par ID et cas d'oracle documentaire.

**Statut de la présente révision :** `1.0-candidate.2`, spécification améliorée, encore soumise à ratification des décisions produit avant de geler l'API. Les 5 nouveaux contrats demeurent candidats.


---

<a id="doc-revision-md"></a>

## Document : `REVISION.md`

# Révision de la spécification diK 1.0 — candidate.2

**Statut :** spécification *cible* consolidée, pas certification du produit diK 1.0. Cette révision **ne modifie pas** Kristal Framework v11 draft.3 ni le code diK v0.3.0.

## Corrections apportées après revue

1. **Décisions d'implémentation :** un profil local mono-utilisateur/hors ligne est défini pour lever les ambiguïtés qui bloquaient le codage ; ce sont des décisions **candidates de ce dossier**, non des acceptations de gouvernance effectuées par un humain. Le réseau multi-acteurs, les signatures, les nouvelles versions de formats et les choix de rétention organisationnels restent des *extensions conditionnelles*.
2. **Algorithmes reproductibles :** déductions de labels et fallbacks, résolution inverse, vérification d'alignements, couverture, changements de snapshots, ordre de tri, idempotence et migration sont décrits par entrées, sorties, codes d'échec et invariants (voir docs/24).
3. **Test oracle documentaire :** `tests/reference_vectors.json` + `tools/verify_reference_vectors.py`. Les cas exécutables vérifient les décisions du dossier ; ils ne certifient **pas** une future implémentation diK.
4. **CI bloquante :** `python tools/validate_documentation.py --strict` échoue en absence de tous les fichiers `SOURCE_LOCK` et de Framework monté ou en cas de hash incorrect ; la vérification standard reste utilisable pour consulter la documentation isolée.
5. **Traçabilité structurée :** `tests/requirements.json` énumère les identifiants normatifs, l'oracle attendu, les preuves positives/négatives et leur état futur `NOT_RUN`. L'exécutable documental ne transforme aucun test produit en `PASS`.
6. **Performances :** objectif chiffré séparé de budget **ratifié** et profil machine ; protocole froid/chaud, comparaisons brut/compressé, mémoire/disque, seuils de régression et datasets vérifiables.
7. **Critères release :** le blocage en absence de preuves (cross-repo, restore, crash, taille Wikidata, 301 langues, sécurité) est écrit comme un contrôle automatisable et non une déclaration générale.

### Décisions encore humaines

- Validation formelle du profil local et des interfaces applicatives candidates ; aucune IA ne peut auto-approuver une ADR.
- Choix des politiques de distribution multi-acteurs / signatures / SLA de production si ces modes deviennent obligatoires.
- Ratification des budgets performance sur matériel de référence après premières mesures.

Pour comprendre la portée : `VALIDATION.md`, `SPEC_LOCK.md`, `tests/requirements.json` et `docs/25_GATES_CI_EXECUTABLES.md`.


---

<a id="doc-changelog-md"></a>

## Document : `CHANGELOG.md`

# Évolution de la documentation diK 1.0

## 1.0-candidate.2 — 2026-10-16

- Ajout du **profil local** hors ligne et de l'ADR-0003 proposée ; aucune approbation humaine simulée.
- Précision des algorithmes (priorité numérique des couches, fallback déclaré, identité stable, contrôle de correspondance, complétude, restauration, idempotence, migration).
- Oracles documentaires vérifiables, avec cas positifs et négatifs, et un registre de 87 exigences fondées sur les titres normatifs réellement présents.
- Exigence de validation **stricte** du Framework et des empreintes du code source (13 fichiers et 5 archives) ; erreur en cas de source manquante, divergente ou corrompue.
- Protocole de performance à 301 langues et très grands corpus, avec budgets proposés et preuves mesurées obligatoires.
- Séparation explicite des niveaux de preuves D1 (documentation), D2 (implémentation) et D3 (qualification produit).
- Préservation des 5 schémas applicatifs *candidats* et des contrats officiels Framework v11 inchangés.

## 1.0-candidate.1

- Spécification initiale de 22 chapitres, exigences KQ/KP, dictionnaires, wikidata, conversions, projections compactes, CLI/UI, journalisation et sécurité.


---

<a id="doc-spec-lock-md"></a>

## Document : `SPEC_LOCK.md`

# SPEC LOCK — Verrou de conception anti-drift

**Identifiant :** `DIK-SPEC-1.0-CANDIDATE` · **État :** frozen design target, pas release logiciel.

## Autorités et épinglage

- Framework **11.0.0-draft.3** : `schemas/v11/*.json`, `spec/v11/*.md`, `tools/v11/*.py` dans `Kristal-Framework-v11.0.0-draft.3.zip`. Les SHAs réels sont recensés dans `SOURCE_LOCK.json` généré à partir des archives fournies.
- Implémentation de référence **diK 0.3.0** : `src/dik/{operations,projection,compact,cli}.py`; documentation v0.2 et v0.3 jointe dans cette version de diK.
- Adaptation externe : **Authoring Kit 4.0.0-draft.2**, **Integration Pack 0.2.0-alpha.1**. Aucun changement implicite de leurs contrats n'est autorisé.
- Patterns étudiés : anti-corruption layer, architecture hexagonale, monolithe modulaire, CQRS interne, idempotence, cache-aside, snapshots immuables, strangler fig. Ce sont des **choix de conception diK proposés**, pas des exigences déjà présentes dans le Framework.

## Ordre de précédence

`Framework normatif > profils diK existants (lecture rétrocompatible) > nouveaux contrats diK 1.0 proposés > tutoriels/exemples > intuition de l'IA`.

### Registres de responsabilité

| Ressource | Propriétaire | Peut modifier canon ? |
|---|---|---|
| Registre d'identité, graphe KQ/KP/KA/KS | Framework + producteur autorisé | Seulement nouvelle révision validée |
| Catalogues, couches lexicales, provenance | diK en tant que gestionnaire | Jamais le graphe |
| Crosswalk externe | diK propose / réviseur approuve | Jamais un KQ déjà alloué |
| Projection compact/verbose/markdown | diK | Jamais |
| Index SQLite et caches | diK (dérivés) | Jamais |
| Migration de graphe legacy | Authoring Kit ou producteur agréé | Nouvelle révision, pas ancien artefact |

## Choix expressément ouverts, sans hypothèse silencieuse

- Distribution réseau : facultative ; diK 1.0 doit fonctionner **localement**. L'API proposée est locale par défaut ; mode distant = profil de sécurité séparé.
- Édition linguistique par IA : candidate en brouillon, jamais automatiquement vérifiée.
- Signatures : empreintes SHA assurent l'intégrité accidentelle, **pas l'authenticité** ; une signature cryptographique est une extension si la confiance multi-acteurs l'exige.
- Performance : budgets proposés dans `docs/14_PERFORMANCE.md` doivent être mesurés sur matériel documenté, non présumés satisfaits.
- Compaction et diffusion d'énormes dictionnaires : politique locale configurable, pas réécriture du format Framework.
- Répertoire `contracts/` contient des formats diK *nouveaux* ; ils demandent une gouvernance avant stabilisation du wire format et ne doivent pas être présentés comme schémas Framework.

## Définition de « terminé »

Aucune fonctionnalité n'est dite terminée sans : code, schéma/vérification, cas normaux, erreurs négatives, tests de reprise et de migration, preuves de rétrocompatibilité, revue et documentation. Les TCK `tests/` de cette spécification sont à **implémenter et exécuter** lors du développement ; le dépôt présent ne constitue pas cette exécution.

## Addendum candidate.2 — verrou complémentaire

L'identifiant de cette révision documentaire est `DIK-SPEC-1.0-CANDIDATE.2`. Les choix du profil local définis par [`ADR-0003`](#doc-decisions-adr-0003-profil-local-1-0-md) sont **proposés**, pas approuvés humainement. L'IA peut les suivre comme baselines techniques pour une branche expérimentale mais ne peut pas déclarer l'API 1.0 stable sans ratification.

En qualification documentaire stricte, toute source Framework/diK manquante échoue ; vérifier les 13 empreintes `SOURCE_LOCK.json` via `--strict`. Un test oracle de cette spécification ne compte pas comme résultat produit diK 1.0. Les IDs normatifs et leurs tests positifs/négatifs sont à conserver dans `tests/requirements.json`.


---

<a id="doc-agents-md"></a>

## Document : `AGENTS.md`

# AGENTS.md — Règles obligatoires pour toute IA générant du code diK

**Portée :** intégralité du dépôt, tous langages, PR, assistants et agents. Ce document est normatif pour l'implémentation visée.

## Procédure de travail imposée (anti-drift)

1. **Lire** `SPEC_LOCK.md`, la présente page, puis l'exigence pertinente et le schéma Framework correspondant. Si aucun contrat disponible : **stopper la modification concernée et marquer `BLOCKED`**.
2. **Étiqueter** chaque demande avec au moins un identifiant d'exigence `ID-`, `LEX-`, `XW-`, `PRJ-`, `MIG-`, `COV-`, `IMP-`, `OPS-`, `SEC-`, `PERF-`, `UI-`, `API-`. Voir `docs/17_TRACABILITE.md`.
3. **Écrire d'abord** un test qui prouve l'invariant positif ET au moins un test de refus en cas de danger sémantique. Ne pas coder d'abord en « devinant » le comportement.
4. **Modifier uniquement** le module propriétaire : le cœur identités ne connaît ni SQLite ni réseau ; imports et formats historiques passent par adaptateurs.
5. **Lancer** les tests du module + TCK transversal + validation des exemples Framework. Aucune exception du linter/validateur pour faire passer une fonctionnalité.
6. **Rendre compte** avec tableau `exigence / fichiers modifiés / tests PASS, FAIL, NOT RUN / divergence / données préservées`, SHA des fixtures de comparaison ; ne pas déclarer la version stable si la suite n'a pas fini.
7. **Changer de contrat ?** Arrêter le patch ; écrire une ADR et une proposition de nouvelle version, demander validation humaine avant toute modification incompatible.

## Interdits absolus

- `label`, `name`, `preferred_label` ou une propriété en langage naturel dans le **graphe canonique v11** ; pas de `wikidata:Q…` ou `Q…` comme identifiant interne.
- Création d'un KQ par traduction, recherche textuelle ou score seul ; réutilisation d'un ID émis ; fusion implicite de KQ.
- Équivalence « accepted exact » basée sur la similarité des noms sans revue + preuve `KS` ; `relatedMatch`, `closeMatch`, candidats ≠ `exactMatch`.
- Réécriture en masse de chaînes, citations, valeurs littérales ou engagements historiques ; modification in situ des anciens Kristals.
- Inférence d'identité en restaurant une projection à partir du Markdown ou d'une traduction. La restauration provient des identifiants conservés.
- Écriture silencieuse d'un label automatique parmi les termes vérifiés ; invention de langues couvertes.
- Modification automatique des schémas Framework vendoriés, de leurs tests ou de leurs empreintes.
- Utilisation du cache SQLite comme registre canonique ; suppression d'une couche curatée lors de la mise à jour Wikidata.
- Appel réseau implicite pendant une opération purement locale, ni exécution de code depuis un dictionnaire.
- Déclaration « 300 langues complètes », « certifié Wikidata massif », « final » sans mesures/preuves.

## Règles d'interprétation

- `MUST` / **DOIT** : condition bloquante ; `SHOULD` : recommandation justifiée ; `MAY` : extension compatible.
- Source-of-truth : registre + graphe Framework, catalogues/crosswalks versionnés ; toute vue est dérivée.
- L'identifiant de référent sémantique **IRS** désigne KQ, pas KP ni KA/KS.
- Une traduction est une donnée linguistique contextualisée, pas un fait doctrinal ni une preuve d'identité.
- En cas d'ambiguïté : préserver les originaux, produire candidat+raison, bloquer l'application automatique.

## Contrat de sortie d'une IA (à inclure dans chaque PR)

```text
Exigences: ID-..., LEX-...
Autorité Framework: 11.0.0-draft.3, schémas SHA connus
Type de changement: additive | correction compatible | incompatible(BLOCKED)
État migration des données: aucune | proposition | appliquée par producteur autorisé
Tests: N pass, M fail, K not-run (liste)
Preuves: commandes, checksums, fichier de comparaison
Exceptions/ouvertures: ...
```

**Un agent ne peut ni inventer l'autorisation d'une migration ni approuver ses propres rapprochements en prétendant à une revue humaine.**

## Addendum candidate.2 — obligations vérifiables

- Traiter le **profil local** de `docs/23_...` comme le choix proposé par défaut seulement ; aucun agent ne peut marquer `ADR-0003` accepted ou décider du propriétaire du namespace KQ.
- Ne jamais annoncer une certification quand seule la commande documentaire passe : `--strict` exige 13/13 sources et les vrais schémas Framework. `tools/verify_reference_vectors.py` vérifie les oracles documentaires, pas le logiciel final.
- Toute implémentation doit relier sa PR aux IDs exacts de `tests/requirements.json`, à au moins un test positif et négatif ainsi qu'aux preuves de résultats `PASS / FAIL / NOT_RUN`. Zéro succès implicite.
- Conserver le comportement Framework pour la priorité lexicale (maximum numérique) et pour le fallback (ordre déclaré, locale demandée avant fallback). Pas d'algorithmes alternatifs inventés.


---

<a id="doc-runbook-ia-md"></a>

## Document : `RUNBOOK_IA.md`

# Manuel d'exécution pour l'IA — développer diK 1.0 sans drift

Ce document est une **procédure**, pas un prompt « fais tout ».

## Protocole d'une tâche

1. Vérifier le **SOURCE_LOCK.json** et la version de la branche courante ; énoncer ce qui est connu vs ce qui est encore proposé.
2. Choisir **une** fonction et ses exigences correspondantes dans `docs/17_TRACABILITE.md`. Ne jamais combiner simultanément renumérotation KQ, migration legacy et synchronisation Wikidata dans une seule PR.
3. Lire les sections Framework listées dans l'exigence et les schémas réels ; citer les chemins exacts, pas la mémoire d'une conversation.
4. Créer un ticket d'implémentation suivant le gabarit ci-dessous ; déclarer les préconditions, non-objectifs et risques.
5. Écrire tests positifs, négatifs et de non-régression **avant** la fonction. Import d'une source : inclure reprise/corruption ; projection : round-trip et cas clean.md ; conciliation : ambiguïtés/candidats.
6. Implémenter dans les modules désignés en injectant adaptateurs via interfaces. Interdire les hacks dans les validateurs Framework vendoriés.
7. Exécuter : tests module, 36 tests hérités v0.3, TCK pertinentes, tests de schéma, cross-repo si impact. Si timeout : rapporter les tests `NOT_RUN` et ne pas déclarer succès global.
8. Vérifier manuellement une fixture contrastant « mot label » et « identité sémantique », et une fixture contenant littéral/citation. Exiger que l'original historique soit toujours identique au SHA d'entrée.
9. Générer un diff et un compte rendu factuel. Ne pas publier ni merger sans revue humaine des changements normatifs.

## Gabarit de ticket/ordre de travail

```text
FEATURE: <nom court>
REQUIREMENTS: <liste IDs ex. LEX-003, XW-002>
UPSTREAM: <fichiers Framework concernés + SHA>
AS_IS: <comportement diK 0.3 vérifié, pas supposé>
TARGET: <comportement exact demandé par la spécification>
INVARIANTS: <KQ namespace; no text->identity; no mutable canon ...>
INPUT/OUTPUT CONTRACT: <schema & version, DTOs, error codes>
BOUNDARY: <domain/application/adapter, propriétaire de la mutation>
NEGATIVE TESTS: <noms et résultats attendus>
BACKCOMPAT: <verbose v0.2, compact v0.3, graphes anciens>
SAFETY/ROLLBACK: <idempotency, snapshots, preuves>
DONE WHEN: <commandes de vérification, pas promesses>
```

## Exemples de refus attendus d'une IA bien alignée

**Proposition** : « Remplace tous les `augustin` par `KQ1001` dans les JSON ».  
**Réponse** : *Refus de l'opération globale ; demander un inventaire des chemins à rôle d'identité, une désambiguïsation des références et un plan revu. Les citations ne doivent pas changer.*

**Proposition** : « Le dictionnaire anglais se trompe : corrigeons le KQ pour le rendre anglais ».  
**Réponse** : *Le KQ ne change pas ; proposer une nouvelle entrée curatée lexicale, versionnée, éventuellement liée au domaine.*

**Proposition** : « Wikidata vient de créer Q99999 : renumérotons KQ430 ».  
**Réponse** : *Conserver KQ430 ; enregistrer candidat crosswalk puis équivalence revue et versionnée.*

**Proposition** : « Retrouve KQ depuis la vue clean après modification ».  
**Réponse** : *Impossible de garantir la réversibilité d'un Markdown seul. Conserver l'enveloppe JSON, utiliser les ancres pour créer un patch candidat.*

**Proposition** : « 298 langues possèdent un fichier vide, donc complétude 100 % ».  
**Réponse** : *Non ; seules les traductions effectives directes comptent direct ; les fichiers vides sont manquants.*

## Checklist de fin d'une PR IA

- [ ] Fichiers et familles de contrats upstream identifiés et hashes vérifiés.
- [ ] Aucun nouvel ID ou prédicat textuel dans le canon.
- [ ] Aucune inférence d'équivalence à partir d'une similitude lexicale seule.
- [ ] Literal/citation inchangés ; provenance non perdue.
- [ ] Restauration sans reverse lookup ; ancien format lisible.
- [ ] Revue nécessaire pour toute promotion `exactMatch` / migration.
- [ ] Import reproductible, idempotent, sans écrasement.
- [ ] Index et cache reconstruisibles ; source de vérité inchangée.
- [ ] Tests positifs/négatifs, anciens tests, interop, statistiques réelles.
- [ ] Tableau PASS/FAIL/NOT_RUN et limites d'implémentation rendu.

## Addendum anti-drift candidate.2

Avant de générer un module : lire `docs/23` à `docs/26`, vérifier les sources avec `python tools/validate_documentation.py --strict`, puis exécuter `python tools/verify_reference_vectors.py`. Si l'un des contrôles ne peut être exécuté, inscrire le travail `BLOCKED` et ne pas prétendre terminer sa qualification. Ne pas modifier les décisions candidates en décisions humaines acceptées pour lever ce blocage.


---

<a id="doc-decisions-ouvertes-md"></a>

## Document : `DECISIONS_OUVERTES.md`

# Registre des décisions — révision candidate.2

**ATTENTION :** le profil ci-dessous est **proposé et spécifié**, pas formellement approuvé par un décideur humain. Un agent ne peut pas changer le statut d'une ADR pour contourner les contrôles.

| Sujet | Position candidate pour la 1.0 locale | Décision à ratifier avant release |
|---|---|---|
| UI | CLI toujours disponible ; web loopback *ou* desktop, avec accessibilité RTL | choisir l'implémentation concrète et vérifier tests UI |
| Signature | SHA-256 intégré, signature non exigée en mono-user local | activer signatures si publication multi-acteurs |
| Export massif | conserver profil compact 0.3 inchangé, génération en streaming | tout profil shardé est une nouvelle version |
| Allocation KQ | service/framework producteur indépendant ; diK non mint | préciser le registre externe du déploiement |
| Wikidata | miroir local fourni par opérateur, snapshot figé ; réseau opt-in | politiques de refresh, licence et redistribution |
| Workspaces | 1 utilisateur local, isolation fichiers et loopback | ACL/SSO si remote |
| Performance | budgets hypothétiques à mesurer sur hardware publié | p95 définitif après banc reproductible |
| Historique | append-only et sauvegarde/restauration ; pas de purge automatique | politique légale de rétention externe |

**Ce qui n'est pas une décision ouverte :** KQ/KP canoniques, séparation lexical/crosswalk, non-mint Wikidata, ambiguïté non promue, rollback vers dernier snapshot vérifié, restauration des projections depuis le canon, signatures distinctes de SHA.

Toute décision différente nécessite ADR avec tests et analyse de compatibilité. Les extensions réseau, SaaS, IA générative automatique, LLM d'approbation, et multi-tenant ne font pas partie du profil local de diK 1.0 tant qu'elles ne sont pas spécifiées puis validées.


---

<a id="doc-sources-et-decisions-md"></a>

## Document : `SOURCES_ET_DECISIONS.md`

# Traçage précis : ce que les archives démontrent, ce que diK 1.0 propose

## Contrats constatés dans les fichiers fournis

| Sources inspectées | Assertions étayées |
|---|---|
| Framework `spec/v11/Identity-and-Wikidata.md` | identités KQ/KP/KA/KS opaques et namespacées ; crosswalk approuvé ; Wikidata externe |
| Framework `spec/v11/Lexical-Boundary.md` | aucun label dans canon ; résolutions lexicales externes ; ambiguïté explicite |
| Framework `spec/v11/Dictionary-Management.md` | sources Wikidata/externes/curatées ; catalogue, priorités, SHA ; 300+ locales sparse |
| Framework `spec/v11/diK-Interoperability.md` | couverture KQ/KP, direct/fallback/missing/conflict, plan de conversion non exécutable |
| Framework `spec/v11/Legacy-Resolution.md` | aucun remplacement global ; original et commitments préservés ; plans soumis à revue |
| Framework `spec/v11/Conformance.md` | profils de conformité mais `V11-Full` pas revendiqué par draft fournie |
| diK 0.3 `src/dik/compact.py` | graphe canon unique + lexicon dédupliqué + anchors/digests ; profil diK applicatif |
| diK 0.3 `src/dik/cli.py` | project/dictionaries/coverage/wikidata import-local/projection export-verify-restore existent |
| diK 0.3 `README.md` | CLI hors ligne, projection compact/verbose, import sélectif, pas UI/sync massive |
| patterns archive #08/#10/#12/#15/#18/#25/#31/#07 | explication de principes architecturaux ; leur adoption diK est une **décision proposée** |

## Propositions de diK 1.0 qui NE SONT PAS encore livrées

Rapprochements multisource avec workflow GUI/revue ; index inverse et FTS durable ; synchronisation Wikidata complète/reprise réseau ; API locale, GUI et autorisations ; tâche d'import idempotente atomique et réparation d'index ; patch éditorial structuré ; rapports multi-Kristals ; TCK complet/benches massifs. Les nouveaux fichiers de `contracts/` sont des **propositions du produit** et ne doivent jamais être qualifiés de normes Framework existantes.

## Questions de produit laissées à ratifier avant la release

- Mode GUI (desktop natif vs interface web locale) ; lib de stockage SQL choisie ; politique de signatures multi-acteurs ; budget machines de performance ; granularité exacte des rôles review ; politique de téléchargement et distribution légale des dumps ; extension sharded des projections massives ; nomenclature et sémantique finales des nouvelles API.

Ces choix n'autorisent pas de déroger aux invariants du Framework ; les développeurs peuvent avancer sur les ports/contrats indépendants et soumettre une ADR quand un point bloquant est rencontré.


---

<a id="doc-validation-md"></a>

## Document : `VALIDATION.md`

# Validation effective — diK 1.0 spécification candidate.2

**Il s'agit de tests de DOCUMENTATION. Aucun code du futur logiciel diK 1.0 n'a été qualifié.**

## Réalisé sur cette révision

| Vérification | Résultat |
|---|---|
| Schémas applicatifs *proposés* + exemples | 5/5 valides |
| Cas négatifs JSON Schema | 3/3 rejetés |
| Oracles documentaires machine-lisibles | 27/27 PASS |
| Registre de traçabilité | 87 exigences réelles, 174 futurs tests positifs/négatifs **NOT_RUN** |
| Catalogue initial TCK | 30 cas **NOT_RUN** |
| Empreintes `SOURCE_LOCK.json` (sources épinglées) | 13/13 vérifiées |
| Archives sources épinglées | 5/5 vérifiées |
| Fixtures Framework v11 contre schémas officiels | 5/5 validées |
| Contrôle `--strict` avec sources présentes | PASS |
| Contrôle `--strict` sans sources | FAIL (comportement voulu) |
| Contrôle `--strict` avec source altérée | FAIL (comportement voulu) |
| Tests historiques de diK 0.3.0 | 36/36 PASS, **pas diK 1.0** |

## Reproduire le contrôle documentaire

```bash
python -m pip install 'jsonschema>=4.21,<5'
python tools/verify_reference_vectors.py
python tools/validate_documentation.py
DIK_SOURCE_DATA_ROOT=/mnt/data KRISTAL_FRAMEWORK_ROOT=/mnt/data/work_kristal_v11_draft3 \
  python tools/validate_documentation.py --strict
```

Les chemins `/mnt/data/...` sont ceux de l'environnement de vérification d'origine ; sur un autre poste, fournir les répertoires sources correspondants tels qu'ils figurent dans `SOURCE_LOCK.json`. La commande sans `--strict` peut indiquer `PASS` **tout en avertissant que les sources sont indisponibles** ; elle ne remplace jamais la commande stricte.

## Restant avant gel puis release 1.0

- **Approbation humaine** de l'ADR-0003 et des contrats applicatifs cibles ; budgets performance ratifiés après bench réel.
- Tests produit sur tous les P0/P1, 30 TCK initiaux et 87×2 exigences ; pas de `NOT_RUN` bloquant.
- Application réelle de diK 1.0 : conciliation multisource, import massif, migrations via producteur, UI/API, 301 langues sparse, sécurité/crash/reprise.
- Compatibilité qualifiée avec les versions exactes de Framework, Authoring Kit et Integration Pack.
- Benchmark du produit réel contre les seuils décidés et preuve de restauration historique.

**Statut :** documentation candidate.2 plus précise, avec contrôle anti-drift vérifiable. Ni version finale du logiciel ni API applicative formellement gelée.


---

<a id="doc-implementation-backlog-md"></a>

## Document : `IMPLEMENTATION_BACKLOG.md`

# Backlog découpé pour les agents — diK 1.0

Chaque tâche est **atomique**, avec préconditions et critères précis. Les agents ne doivent pas coder une tâche future en supposant que ses prérequis sont déjà disponibles.

| Ordre | Lot / exigences | Entrée | Sortie / Done when | Dépendance |
|---|---|---|---|---|
| A01 | Pin et TCK [ID,LEX,PRJ] | Code diK 0.3 + Framework draft.3 | harnais TCK, goldens, 36 tests historiques conservés | aucune |
| A02 | Domaine/ports [OPS-001..006] | A01 | règles extraites sans IO ; tests de frontières | A01 |
| A03 | Index reconstruisible [OPS-010..015] | snapshots Framework | recherche ID et lexique par index, rebuild bit-à-bit des réponses | A02 |
| A04 | Reverse search [XW-001, LEX-024] | ID, locale, type, domaine | candidats ordonnés + provenance, jamais preuve automatique | A03 |
| A05 | Moteur de décision [XW-002..005] | candidat, preuve KS, reviewer | workflow de statut, refus des doublons actifs exact | A04 |
| A06 | Composition multisource [LEX-002..006] | sources avec licence, catalogue | nouvelle révision curatée/externe, audit strict | A05 |
| A07 | Projection durcie [PRJ-001..007] | diK 0.3 compact/verbose | round-trip, ancres, clean et fallback sûr | A02, A03 |
| A08 | Migration candidate [MIG-001..005] | legacy adapter, crosswalk, source hash | plan Framework non exécutable, revue et refus de citation | A05 |
| A09 | Adaptateur producteur [MIG-004..006] | plan approuvé, Authoring Kit | révision nouvelle, ancien état intact, rollback | A08 |
| A10 | Import massif [IMP-001..005] | dump local, version, accepted exact crosswalk | staging/checkpoints/idempotence, version publiée atomiquement | A03, A06 |
| A11 | Multi-projet couverture [COV-001..006] | plusieurs graphes et catalogue | matrice KQ/KP, 301 langues, digest et delta | A03, A06 |
| A12 | Interface & API [UI,API] | cas d'usage stables | application locale usable, API locale, revue/rôles, RTL | A04..A11 |
| A13 | Sécurité/release [SEC,TCK,PERF] | logiciel complet | G1–G8, benchmarks/reprise/licences/packaging et docs | A01..A12 |

## Décomposition obligatoire de chaque lot

Pour chaque ligne : créer une branche, lier exigences, spécifier contrat d'entrée/sortie, écrire tests négatifs, coder, valider, vérifier backward compatibility, produire diff+rapport. Si une dépendance n'est pas satisfaite, bloquer avec une interface mock et documenter ce qu'elle ne prouve **pas**. Ne pas cocher A13 après les seuls tests du schéma de ce dossier.


---

<a id="doc-docs-01-contrats-et-frontieres-md"></a>

## Document : `docs/01_CONTRATS_ET_FRONTIERES.md`

# 01 — Mission, frontières, terminologie et conformité

## 1. Portée diK 1.0

**Produit cible** : application installable localement et automatisable par CLI/API, capable de gérer des dictionnaires multilingues, réconcilier des sources, importer/synchroniser Wikidata, auditer la complétude de Kristals, générer/restaurer des projections linguistiques, préparer des migrations supervisées.

**Hors portée** : héberger Wikidata lui-même, créer des identifiants Q/P officiels, enseigner un modèle IA, fusionner des KQ automatiquement, modifier les commitments d'anciens Kristals, garantir 300 traductions complètes, exécuter seul des migrations v9/v10, inventer un format concurrent du Framework.

### Niveaux de maturité

- **AS-IS** : comportement vérifié dans le code diK 0.3.0, décrit sans extrapolation.
- **UPSTREAM** : obligation Framework v11 draft.3 à respecter ; pas « fonctionnalité finie » dans diK.
- **TARGET** : comportement obligatoire à développer pour diK 1.0.
- **OPTIONAL** : extension isolée sans effet sur les invariants.

Le fait qu'un schéma/outil upstream sache valider un JSON n'implique pas qu'une interface de gestion complète existe.

## 2. Définitions invariantes

- **Référent sémantique / IRS** : identité de personne, objet, événement, concept ; `KQ…` dans l'espace Kristal. Clé vraie : `(namespace_id, id)`.
- **Propriété** : relation `KP…`. Assertion : `KA…`. Source : `KS…`.
- **Crosswalk** : correspondances type+statut+preuve avec Wikidata ou autres référentiels.
- **Dictionnaire lexical** : noms, variantes, alias, descriptions, préférences locales ; ne définit pas le sens d'une identité.
- **Projection** : vue linguistique dérivée d'un graphe canonique. **Restauration** : restitution de la structure sémantique conservée, pas « traduction inverse ».
- **Migration legacy** : opération nouvelle et auditable, après résolution du rôle sémantique exact de chaque champ.
- **Snapshot** : état publié, content-addressed ou hashé, non modifié après publication.

## 3. Frontières

1. **Import** est impur (IO) mais n'accède pas en écriture au graphe source.
2. **Réconciliation** produit décisions proposées puis approuvées, pas d'inférence d'identité.
3. **Lookup** est pur avec un catalogue/crosswalk/registre verrouillés par version.
4. **Projection** lit les données canoniques et crée un dérivé ; peut être supprimée et recréée.
5. **Édition d'une projection** devient un patch sémantique candidat ; pas une mutation du canon.
6. **Publication** écrit par staging + vérification + commit atomique ; le lecteur ne voit jamais un catalogue incomplet.

## 4. Classification des exigences

- Critique `P0` : perte sémantique, confusion identité/langue, données écrasées, migration non autorisée, correspondance fausse, intégrité manquante.
- `P1` : correction de complétude, échelle 300 langues, index/transactions, interopérabilité.
- `P2` : ergonomie, exports, rapports enrichis.

Toute faille `P0` bloque la livraison stable même si le nombre de tests réussis paraît bon.


---

<a id="doc-docs-02-identites-md"></a>

## Document : `docs/02_IDENTITES.md`

# 02 — Identités sémantiques et registre

## ID-001 — Clé canonique

La seule clé référentielle d'un KQ/KP est `(namespace_id, id)`. `KQ1001` dans `alpha` et `KQ1001` dans `beta` **ne sont pas interchangeables**. Toutes les API/domain objects portent le namespace ; l'affichage abrégé de `KQ1001` n'autorise pas sa résolution hors contexte.

## ID-002 — Types stricts

`KQ…` = entity; `KP…` = property; `KA…` = assertion; `KS…` = source. Le parser rejette `Q8018`, `P31`, `wikidata:Q8018`, `has_property`, `urn:legacy:…` **dans un rôle d'ID canonique**. Il peut les reconnaître dans des *champs externes* typés, des demandes de migration ou une valeur littérale.

## ID-003 — Allocation

- Allocation durable et non réutilisable au sein du namespace, y compris après suppression logique.
- Avant l'émission : chercher identités internes existantes ; consulter miroir externe **si disponible**, sans rendre Wikidata indispensable à l'émission locale.
- Retourner l'identifiant alloué + séquence/transaction d'émission + portée. Échec atomique en cas de compétition ; aucun recyclage sur rollback après émission publiée.
- Ne pas déduire le numéro du KQ du numéro Q externe ; ne pas précréer des Q Wikidata « en réserve ».
- **diK ne devient pas autorité d'allocation** : il demande un mint au registre/producteur désigné, ou propose des identités candidates via un canal séparé.

## ID-004 — Statuts, fusion, scission

Une erreur d'identité se corrige par des déclarations de remplacement/supersession versionnées et une décision auditée, pas en remplaçant la clé de l'histoire. Les fusions/splits Wikidata ne fusionnent pas les KQ de Kristal. La dépendance à Wikidata est la table de correspondance, jamais l'ID maître.

## ID-005 — Contrôles systématiques

- Champs `entities`, `properties`, assertions et sources v11 validés contre le schéma officiel et le registre.
- Références manquantes et KS inexistantes = erreur.
- Un ID peut apparaître dans mille assertions mais reste une identité unique pour les métriques de couverture.
- Le texte libre dans une citation doit rester inchangé.

### Cas de rejet obligatoires

`ID-R1` namespace absent, `ID-R2` Q brut en sujet, `ID-R3` KP comme entité, `ID-R4` allocation concurrente du même KQ, `ID-R5` source KS orpheline, `ID-R6` mutation rétroactive du registre déjà publié.

**Source upstream :** `spec/v11/Identity-and-Wikidata.md`, `kristal-identity-registry.schema.json`, `kristal-semantic-graph.schema.json`.


---

<a id="doc-docs-03-dictionnaires-md"></a>

## Document : `docs/03_DICTIONNAIRES.md`

# 03 — Dictionnaires multilingues et gouvernance des couches

## LEX-001 — Deux catégories qui ne fusionnent jamais

**Lexical** : `(namespace, KQ/KP, locale[, domaine]) → label, alias, définition descriptive, provenance, statut et priorité`. **Crosswalk** : `(namespace, KQ/KP) ↔ (source externe, Q/P ou autre)`, relation, statut, preuve, revue. Le libellé externe ne devient utilisable que via l'alignement approprié et la couche lexicalement admise. Un mot commun n'est pas une clé de jointure sémantique fiable.

## LEX-002 — Catalogue et fichiers

- Catalogue unique sélectionne les langues, fallbacks, couches ordonnées, chemins relatifs, SHA-256 et versions. **Ne jamais déduire la priorité d'un nom de fichier ou d'un ordre d'itération du dossier.**
- Couches `wikidata` (snapshot importé immuable), `external` (source tiers/licence/preuve) et `curated` (corrections revues, séparées et préservées).
- Entrée curatée supérieure = choix d'affichage, pas vérité sur l'identité ni droit d'altérer le dump importé.
- Égalité de priorité et labels contradictoires = `CONFLICT`, pas premier arrivé gagnant.
- **Les fichiers restent la source de vérité** ; index SQLite, recherches FTS et caches sont reconstruisibles.

## LEX-003 — Sélection et déterminisme

Pour `(namespace, semantic_id, locale, domaine)` : valider ID + langue ; consulter couches déclarées ; ordonner par priorité du catalogue ; en cas de tie incompatible -> erreur ; sinon rendre `{label,status,effective_locale,layer_id,provenance}`. Fallback uniquement si déclaré et sans cycle. Si aucun libellé : `{label:null,status:"missing"}` et ID conservé. Pas de traduction de secours silencieuse par IA.

## LEX-004 — Versions et corrections

Une correction crée un nouvel objet curaté/reviewed, journalise auteur, décision, justification, avant/après, KS le cas échéant, source et date. Les anciens snapshots restent accessibles pour reproduire une projection historique. Une mise à jour Wikidata ne supprime ni n'édite une couche curatée. Dictionnaire externe absent de licence ou d'alignement validé : `untrusted`, exclu du canal vérifié.

## LEX-005 — Sparsité et domaines

- 300+ langues supportées comme **données clairsemées** ; pas de matrice dense `KQ×300` à créer à l'import.
- Synonymes, sens multiples, variantes régionales et domaines coexistent sans fusion automatique.
- Les préférences lexicales selon domaine doivent être explicites et versionnées ; en absence de domaine unique, signaler la concurrence.
- Préserver Unicode ; politique de comparaison NFC, sans translittération ASCII ni minuscule destructrice par défaut.

## LEX-006 — Publication

Staging privé -> validation JSON Schema + hash + licences + collision + fallback -> écriture de tous shards -> publication atomique du pointeur de catalogue -> audit postpublication. Réexécuter avec la même clé idempotente retourne le snapshot existant, jamais un nouveau contenu conflictuel sous le même ID.

## Défauts bloquants

- LEX-R1 label d'identité dans graph ; LEX-R2 fallback implicite ; LEX-R3 conflit de même priorité résolu par hasard ; LEX-R4 overwrite curated par Wikidata ; LEX-R5 licence inconnue promue comme verified ; LEX-R6 empreinte incorrecte ; LEX-R7 source non déclarée utilisée ; LEX-R8 entrée d'un autre namespace.

**Référence upstream :** `spec/v11/Dictionary-Management.md` et schémas `kristal-*dictionary*`, `kristal-external-lexical-record.schema.json`.


---

<a id="doc-docs-04-conciliation-md"></a>

## Document : `docs/04_CONCILIATION.md`

# 04 — Conciliation multisource et résolution inverse

## XW-001 — Recherche candidate, pas attribution d'identité

Entrée obligatoire : `term`, `locale`, `expected_kind` (`KQ`/`KP`), `namespace_id` et facultativement domaine KQ, provenance et type de source. La recherche explore exact Unicode normalisé, alias, descriptions, relations existantes et types contextuels ; les variantes fuzzy sont **des candidats**. Sortie : ensemble déterministe de candidats identifiés, raison par signal, distance/type de relation, preuves, dictionnaires/snapshots consultés et état `ambiguous|unique_candidate|no_candidate`. Un seul candidat n'est **pas** une équivalence définitivement approuvée.

## XW-002 — Machine d'états des rapprochements

`proposed -> reviewed -> accepted | rejected`; `accepted -> superseded` avec nouvelle décision. Les rapprochements `closeMatch/broadMatch/narrowMatch/relatedMatch` ne deviennent jamais `exactMatch` implicitement. Une acceptation exige : identifiant de décision, réviseur autorisé, méthode, lien d'évidence `KS`, version des sources, justification et contrôle d'unicité active. Il n'existe pas d'acceptation simplement parce que le score est > 0.99.

## XW-003 — Multi-dictionnaires

- Comparer les sources sans confondre les clés locales des fournisseurs avec les clés KQ.
- Sources contradictoires : conserver les deux options avec score explicatif ; priorisation d'affichage dans le catalogue ; alignement sémantique via décision distincte.
- Importer uniquement si droit d'usage compatible ; stocker attribution/licence et obligations de redistribution par source.
- Conserver chaque décision, y compris rejet ; une prochaine synchronisation ne doit pas re-proposer en boucle un rejet identique sans nouvel élément de preuve.

## XW-004 — Crosswalk Wikidata

`(namespace,KQ) ↔ (wikidata,Q)` et `(namespace,KP) ↔ (wikidata,P)` seulement, sans mélange. Les contraintes de mapping `accepted exact` du Framework s'appliquent à chaque vue active. Pour un nouveau Q Wikidata : créer `candidate`, évaluer puis publier une révision ; **aucun KQ modifié**. Pour Q redirigé, supprimé, scindé, fusionné : événement de revue + éventuel superseding, pas substitution immédiate.

## XW-005 — Corrections et annulations

Toute promotion/rejet/supersession s'écrit dans un journal append-only pour audit et est matérialisée dans une nouvelle vue active. Les prévisualisations peuvent être annulées sans effet. Les décisions déjà publiées sont contredites par un événement nouveau, jamais éditées rétroactivement.

## TCK conciliation

- `XW-T1` mot identique lié à deux KQ -> deux candidats, aucun auto-mapping.
- `XW-T2` accepted exact sans KS/reviewer -> rejet.
- `XW-T3` double exact accepté actif dans la même vue -> rejet ou supersession explicite.
- `XW-T4` Q externe associé à KP -> rejet.
- `XW-T5` snapshot externe change de libellé -> KQ et anciennes décisions intacts.
- `XW-T6` couche externe sans licence -> quarantaine.
- `XW-T7` reverse lookup par locale incorrecte -> ne pas silencieusement rechercher dans toutes les langues.


---

<a id="doc-docs-05-wikidata-md"></a>

## Document : `docs/05_WIKIDATA.md`

# 05 — Copie Wikidata, import, synchronisation et reprise

## IMP-001 — Source externe et miroir

Le dump Wikidata est une **entrée non fiable** et non une autorité locale de KQ. Son format Q/P, ses alias, ses révisions, ses descriptions, redirections sont adaptés dans une couche anti-corruption. Le miroir local de l'utilisateur est supporté sans accès Internet. Un téléchargement depuis une source officielle est une opération **explicite** distincte du rendu/lookup.

## IMP-002 — Pipeline robuste

1. L'opérateur fournit URL ou chemin local, mode (`full`/`delta` si source fiable disponible), révision/date, langues ciblées, limites de ressources et destination.
2. Vérifier signature/checksum de l'amont *si disponible* ; toujours calculer empreinte locale ; ne jamais décompresser sans quotas ni écrire à une destination arbitraire contrôlée par le dump.
3. Parser **en flux**, supporter `.json`, `.jsonl`, `.gz`, `.bz2` compatibles ; préciser le format réellement accepté ; ne pas matérialiser des milliards de records en RAM.
4. Joindre uniquement `accepted + exactMatch` actif pour le namespace choisi ; `candidate`, `rejected`, `relatedMatch` sont exclus des imports vérifiés.
5. Générer shards immuables par locale/plage, provenance, hashes et statistiques; séparer erreurs isolées et erreurs bloquantes selon politique configurée et observable.
6. Comparer contre l'ancien snapshot : ajout/suppression/label/alias/redirect/merge/split, classer les changements et ouvrir une tâche de revue si le sens pourrait changer.
7. Vérifier puis publier atomiquement le nouveau catalogue ; conserver l'ancien ; ne jamais modifier `curated` ni réallouer des KQ.

## IMP-003 — Reprise/idempotence

Clé de tâche = hash canonique `(source snapshot, namespace, crosswalk revision, selected locales, transform version, settings)`. Même clé/mêmes octets -> résultat identique sans duplication ; même clé/octets différents -> conflit bloquant. Checkpoints portent compteur d'objets, shard terminé, empreintes ; reprise uniquement si source identique, transformation identique et point de reprise validé. Compresser et reprendre par blocs/fragments vérifiables, sans promettre seek arbitraire dans un `bz2` monolithique.

## IMP-004 — Téléchargements

HTTP(S) seulement si activé ; délais et budget total, retry avec backoff+jitter seulement sur erreurs transitoires, limite de débit, stockage temporaire de téléchargement, métadonnées ETag/Last-Modified *si la source les fournit*, checksum post-téléchargement, publication après validation. Aucun appel réseau dans `projection restore`, `coverage`, `lookup` ni au démarrage de diK.

## IMP-005 — Wikibase lexèmes

Les lexèmes Wikidata `L…` (formes/sens) sont différents des items `Q…` et propriétés `P…`. L'import 1.0 des labels Q/P **ne les traite pas** comme des KQ. Un connecteur L séparé demanderait des contrats explicitement typés et des tests distincts.

## Critères bloquants

- IMP-T1 interruption à 50% => aucun nouveau catalogue visible ; reprise identique.
- IMP-T2 nouveau snapshot Wikidata avec label changé => ancienne couche disponible, correction curatée intacte.
- IMP-T3 Q nouveau aligné uniquement `candidate` => aucune importation vérifiée.
- IMP-T4 dump contenant champs/path malveillants => aucun traversal ni exécution.
- IMP-T5 même import relancé => aucune duplication.
- IMP-T6 suppression ou redirection externe => événement de rapprochement, pas fusion de KQ.


---

<a id="doc-docs-06-projections-md"></a>

## Document : `docs/06_PROJECTIONS.md`

# 06 — Projections linguistiques réversibles

## PRJ-001 — Contrat des trois vues

- **Canonique** Framework v11 : KQ/KP/KA/KS + assertions/littéraux/qualificatifs/sources, aucun label servant d'identité.
- **Compact enrichi** diK `dik.compact-projection/1.0` (existant v0.3) : `canonical_graph` **une fois**, table `lexicon.entries` dédupliquée par ID, `anchors`, `digests` et locale. Représentation dérivée réversible, non un nouveau canon.
- **Lecture Markdown** `annotated|clean` : générée à la demande à partir de compact/verbose, jamais preuve de restauration. `clean` masque les IDs traduits à l'affichage, sans supprimer les IDs du JSON. IDs non traduits restent visibles pour signaler la lacune.

## PRJ-002 — Règles de réversibilité

La restauration extrait le graphe conservé et compare structure/hashes/ancres ; **aucun reverse lookup des mots**. En mode robuste, vérifier aussi le graphe, registre, catalogue, crosswalk et couches d'origine. Sans projet source/ancres authentifiées, les hashes auto-déclarés ne prouvent pas l'origine ; répondre `integrity_consistent` et non `authentic`.

Invariant formel : pour tout graphe canonique valide `G`, locale déclarée `L`, dictionnaires fixés `D`, si `E = export(G,L,D)` alors `restore(E) = G` selon sérialisation canonique normalisée et **égalité structurelle des données**. Le rendu libre `Markdown(E)` ne sert pas d'entrée à `restore`.

## PRJ-003 — Portée du lexique

Références couvertes : KQ entités et KP prédicats/qualificateurs ; KS/KA sont conservés mais leur dénomination n'est pas comptée comme couverture KQ. La table lexicale est indexée par identifiant **dans un namespace fixé et ancré**. En projet multi-namespace futur, les clés de table devront porter le namespace ou employer des namespaces isolés par enveloppe — jamais fusionner deux `KQ1001`.

## PRJ-004 — Bords importants

- Valeurs littérales/texte cité préservés octet logiquement (Unicode identique ; sérialisation JSON peut différer en whitespace).
- Fallback `fr-CA -> fr` explicitement marqué `fallback`, pas `direct`.
- Libellé inexistant = `null`, status `missing`, pas traduction plausible inventée.
- XSS/Markdown injection : sortie échappée, pas exécution HTML arbitraire.
- Le vocabulaire peut être mis à jour ultérieurement, mais une vieille enveloppe reste liée à ses versions/hashes ; une nouvelle projection devient une **nouvelle vue**, sans modifier son canon.
- La restauration refuse un graphe non conforme au profil attendu même si son hash interne a été recalculé.

## PRJ-005 — Compatibilité

Lire et vérifier `dik.compact-projection/1.0` et l'ancienne projection `verbose` v0.2 ; ne pas changer rétroactivement leur définition. Pour les rendre plus robustes : enveloppe externe versionnée optionnelle, sans altérer l'ancienne structure. Ne pas supprimer `--format verbose` avant décision de dépréciation publiée et tests de non-régression.

## PRJ-006 — Édition

Un utilisateur qui modifie un texte en mode `clean` ne crée pas un nouveau KQ ni une nouvelle assertion. L'éditeur lié au canon doit créer un **patch d'intention** : chemin de l'objet structuré, ancienne valeur/ID, candidat de nouvelle valeur/ID, preuves et statut `pending_review`. Une modification textuelle libre non ancrée ne peut pas se convertir automatiquement en patch accepté.

## PRJ-007 — Limites mémoire

Le format compact actuel incorpore le graphe entier. diK 1.0 DOIT conserver cette compatibilité mais MAY proposer un **nouveau profil de projection par références à des shards immuables**, uniquement si nécessaire à l'échelle, avec manifeste/empreintes, non une modification silencieuse du profil compact existant.

## Tests déterminants

`PRJ-T1` round-trip structure-identique avec littéral, sources, qualificatifs ; `PRJ-T2` modifier label mais recalculer hash => avec projet ancré, rejet ; `PRJ-T3` `clean.md` seul => refuse restore ; `PRJ-T4` namespace différent => rejet ; `PRJ-T5` champs étrangers KQ/Q => rejet ; `PRJ-T6` 300 locales n'alourdissent pas projection d'une seule locale ; `PRJ-T7` données sans traduction = missing explicite ; `PRJ-T8` ancres manquantes => jamais statut authentic.


---

<a id="doc-docs-07-migration-md"></a>

## Document : `docs/07_MIGRATION.md`

# 07 — Migration des Kristals legacy et patches approuvés

## MIG-001 — Découverte des rôles

Parcourir les sources historiques avec **adaptateur de version** qui identifie précisément les rôles sémantiques : sujet, propriété, cible d'entité, qualificateur sémantique. Les champs littéraux, citations, noms de personnes *dans du texte*, corps de document, URLs, références éditoriales ne sont pas des cibles à convertir par remplacement. S'il est impossible d'établir le rôle d'un champ, le laisser `unknown_role` et bloquer l'application.

## MIG-002 — Plan non exécutable Framework

Produire un `kristal_dik_conversion_plan` **conforme au schéma upstream** : source artefact/version/SHA, namespace, catalog/crosswalk, liste d'opérations chacune avec JSON Pointer exact, ancienne valeur, rôle, ID cible, décision `pending|approved|rejected` suivant schéma officiel. Les scores de correspondance restent consultatifs. Aucune opération `pending` ou `rejected` ne s'exécute.

## MIG-003 — Résolution et revue

Ordre de proposition : ID interne déjà connu -> mapping externe accepté/exact et typé -> recherche lexicale contextualisée -> candidats manuels. Vérifier toutes les hypothèses, ambiguïtés et absence de KQ. Créer un nouveau KQ éventuel **via l'autorité d'allocation**, après revue. Ne pas convertir un mot « grâce » automatiquement sans préciser le sens.

## MIG-004 — Exécution par producteur

L'Authoring Kit ou autre producteur autorisé exécute après relecture indépendante : comparer digest octets de l'ancien artefact, JSON pointers et anciennes valeurs, décision approuvée et preuves ; appliquer transactionnellement à une **nouvelle révision**, jamais à la source ; valider le nouveau graphe contre Framework ; conserver journal de conversion et lien de retour. diK ne se déclare pas implicitement producteur du canon.

## MIG-005 — Patch d'édition linguistique

Une vue annotée peut demander une modification sémantique : le système affiche avant/après et identifiants, produit `patch_candidate`, oblige revue. Si seule la traduction change et aucun ID/relation ne change, modifier **une couche curatée**, pas le graphe. Cette bifurcation est essentielle pour éviter la confusion « correction d'un mot » = « changement de sens ».

## MIG-006 — Échecs et reprises

L'opération est idempotente par `(source hash, plan ID/revision, decisions hash, producer version)`. Si une révision a déjà été produite, rendre son adresse ; pas de seconde mutation. En cas de crash pendant staging : révision non visible, rollback et possibilité de relance vérifiée. L'original historique et ses commitments v9 restent inchangés.

## Tests

`MIG-T1` mot dans citation inchangé ; `MIG-T2` JSON Pointer modifié -> rejet ; `MIG-T3` plan avec pending -> rejet ; `MIG-T4` deux sens candidats -> blocage ; `MIG-T5` KS preuve absent -> rejet ; `MIG-T6` source SHA changé -> rejet ; `MIG-T7` commit crée nouvelle révision seulement ; `MIG-T8` rollback crash ; `MIG-T9` ancien graph toujours vérifiable.


---

<a id="doc-docs-08-completude-md"></a>

## Document : `docs/08_COMPLETUDE.md`

# 08 — Complétude linguistique par Kristal, portefeuille et domaine

## COV-001 — Dénominateur

Inventorier les **KQ distincts utilisés comme entités** et les **KP distincts utilisés comme propriétés**, y compris qualificatifs, pour le graphe v11 visé. KA/KS sont contrôlés pour intégrité, pas additionnés arbitrairement au nombre de concepts traduisibles. Le rapport provient d'un graphe et d'un catalogue versionnés, pas du nombre de Q Wikidata ni du nombre de fichiers de langue.

## COV-002 — Statuts exclusifs

Par identifiant+locale : `direct` si terme approuvé dans locale demandée ; `fallback` seulement si chaîne déclarée ; `missing` si aucun terme ; `conflicted` si concurrence non résolue. Rapport par **famille KQ / KP**, par locale, et intersection de toutes les locales sélectionnées. `complete_direct` ne compte ni fallback ni missing/conflict. `complete_usable` tolère fallback, pas missing/conflict. `crosswalk coverage` est une métrique **séparée**.

## COV-003 — Reporting multi-Kristals

Sélection par manifestes explicites ; construire une matrice `(graph_id, namespace, locale, family)` et les unions/intersections de référents par namespaces. Pour une organisation, ne pas dédupliquer deux `KQ1001` de namespaces différents. Toute ligne conserve version, empreinte, compteur, date logique, nombre de conflits, exemples manquants et statut de troncature.

## COV-004 — Qualité != présence

Complétude nominale = présence validée du terme. Qualité de traduction = révision, domaine, profondeur lexicale, source, date, éventuel contrôle linguistique ; métrique distincte. Un terme généré automatiquement en attente de revue peut exister comme *proposal* mais **ne compte pas comme traduction directe vérifiée**.

## COV-005 — Historique et delta

Comparer rapports A/B avec mêmes graphes ou changements d'inventaire identifiés : nouveau concept, traduction ajoutée/supprimée, variante en conflit, fallback devenu direct. Conserver le dénominateur pour chaque état historique ; ne jamais attribuer la variation entière à « traduction » si les KQ du graphe ont changé.

## COV-006 — 300+ langues

Le rapport peut porter 301 langues sparse et plusieurs graphes ; afficher par défaut vue agrégée et pagination/drilldown. Ne pas prétendre à 100 % si un seul KQ/KP manque ou est conflictuel. Une entrée legacy non résolue interdit un taux fiable de 100 % pour l'ensemble ; le rapport doit signaler `legacy_denominator_unknown`.

## TCK

`COV-T1` KQ 2, KP 1 ; `fr-CA`: KQ direct 0/fallback 1/missing 1 ; KP missing 1 -> jamais complete. `COV-T2` 301 langues sans entrée -> 0% direct, pas couverture inventée. `COV-T3` conflit refuse complete. `COV-T4` namespace distinct non dédupliqué. `COV-T5` édition d'une traduction ne modifie pas graphe/hash. `COV-T6` vieux graphe texte => dénominateur inconnu.

**Format amont :** `kristal-dik-coverage-report.schema.json`. Ne pas le remplacer par une simple moyenne UX.


---

<a id="doc-docs-09-architecture-md"></a>

## Document : `docs/09_ARCHITECTURE.md`

# 09 — Architecture : monolithe modulaire et ports/adaptateurs

## OPS-001 — Structure recommandée

```text
src/dik/
  domain/           # IDs, résolution, décisions, composition, invariants ; sans SQL/HTTP/IO
  application/      # use cases : import, revue, audit, couverture, projection, migration candidate
  ports/            # interfaces Reader/Writer/Registry/Catalog/Crosswalk/Clock/Verifier
  adapters/
    framework/      # schémas/validations versionnées Framework (pas une réécriture)
    wikidata/       # dump parser, change feed, HTTP explicite
    filesystem/     # snapshots et publications atomiques
    sqlite/         # index dérivé, cache, transactions locales
    authoring/      # plans de migration vers producteur autorisé
    integration/    # lectures/projections Integration Pack
  entrypoints/      # cli, api, ui, jobs
  observability/    # logs/metrics/codes d'erreur
```

Structure **cible**, pas arborescence du code 0.3. Les modules peuvent commencer dans un même processus Python.

## OPS-002 — Règle des dépendances

`entrypoints -> application -> domain`, `adapters -> ports/domain` via injection. Le domaine n'importe ni SQLite ni requests/urllib ni frameworks web. Un `CatalogReader` vérifie les artefacts Framework ; un `IndexReader` sert les recherches mais ne crée aucun concept. Les writes passent par commandes explicites, les reads par vues dérivées (**CQRS local léger**, pas besoin Kafka).

## OPS-003 — Bounded contexts

- `identity` : référents et types, normalisation, namespace.
- `lexical` : couches, fallbacks et sélection.
- `alignment` : crosswalk/revue/décisions.
- `ingestion` : import/version/format/snapshot.
- `projection` : compact/verbose/render/restore.
- `coverage` : inventaire et calculs.
- `migration` : plans et demandes au producteur.
- `workspace` : stockage/transactions/index et sessions.

Chaque contexte expose DTOs/contrats stricts ; pas de `dict[str,Any]` non validé traversant toutes les couches.

## OPS-004 — Patterns retenus, sans sur-ingénierie

Anti-Corruption Layer pour Wikidata et legacy ; Hexagonal Architecture pour le domaine ; Modular Monolith pour déploiement simple ; CQRS interne pour index rapides ; Idempotency pour les jobs ; Cache-Aside pour résolutions ; Immutable Infrastructure (par analogie) pour snapshots ; Strangler Fig pour migration progressive des anciens Kristals. **Pas** de service mesh, microservices obligatoires, Event Sourcing global ou système distribué requis en 1.0.

## OPS-005 — Déterminisme

À entrées/version identiques, résultat sémantique identique. Ordre stable des entrées, canonical JSON pour hashes défini, gestion UTF-8/NFC explicite, horodatage/auteur séparés de la partie reproductible, politique de tie/conflict non basée sur l'ordre SQL ni un dictionnaire Python arbitraire.

## OPS-006 — Import Framework

Remplacer les copies vendoriées par un composant upstream épinglé **si disponible et contractuellement compatible** ; à défaut conserver avec hash et tests de comparaison. Ne jamais « améliorer » silencieusement les validateurs v11 embarqués.


---

<a id="doc-docs-10-stockage-indexation-md"></a>

## Document : `docs/10_STOCKAGE_INDEXATION.md`

# 10 — Stockage, index et caches

## OPS-010 — Autorité

La source de vérité est le **catalogue de fichiers versionnés** et les documents Framework signés/empreintés selon leur profil. SQLite est un index dérivé **reconstructible**, pas un registre KQ autonome. L'instance peut être détruite puis reconstruite à partir d'un manifeste publié et de ses shards.

## OPS-011 — Structure proposée

```text
workspace/
  projects/           # références à graphes/catalogues, non copies massives obligatoires
  manifests/          # pointeurs de révisions publiées
  snapshots/          # objets immuables de dictionnaires/crosswalks/lexiques
  curated/            # nouvelles révisions revues
  staging/            # zone de travail non publiée, nettoyable
  indexes/            # sqlite/fts reconstructibles et cache
  jobs/               # checkpoints sans autorité sémantique
  audits/             # décisions et preuves/manifestes
```

Toutes les écritures sont contenues dans un `workspace_root` sûr ; pas de `../`, symlinks dangereux ou chemins absolus dans les manifestes importés.

## OPS-012 — Index logique (dérivé)

Tables proposées : `active_manifest`, `semantic_key(namespace,id,kind)`, `lexeme(namespace,id,locale,domain,layer,priority,term,aliases,status)`, `reverse_terms(locale,normalized_term,namespace,id,kind,context)`, `external_mapping(namespace,id,system,external_id,relation,status,decision)`, `snapshot(hash,source,version)`, `job_checkpoint`, `audit_decision`. Indexer `locale + normalized_term + kind` et `namespace+id+locale`, pas une table de 300 colonnes. FTS utile pour suggestions, sans rôle de preuve d'identité.

## OPS-013 — MVCC / cohérence

Le lecteur fixe une révision complète de manifeste au début ; les jobs peuvent préparer une autre révision sans changer les données vues. Un pointer swap atomique rend la nouvelle version visible après validation. Caches clés : `(manifest_digest, namespace, KQ/KP, locale, domain, resolution_profile)` ; invalider par changement de digest, pas via TTL qui pourrait masquer une publication.

## OPS-014 — Tâches et transactions

Une mise à jour publie son catalogue et ses shards ensemble, jamais un par un visibles. Crash avant commit : ancien pointeur inchangé. Crash après commit : manifeste vérifié, index peut être reconstruit. Aucun état `partial-success` silencieux à une API qui annonce réussite.

## OPS-015 — Efficacité

Chargement par lots/shards, streaming, réutilisation des parseurs/index, mémoire plafonnée, index réparables ; comparaison incrémentale des hashes de shards ; limiter l'audit complet quotidien en préférant audit incrémental + audit intégral périodique au lancement d'une release.


---

<a id="doc-docs-11-api-cli-md"></a>

## Document : `docs/11_API_CLI.md`

# 11 — CLI et API : contrats publics cibles

## API-001 — CLI sans surprise

**Commandes diK 0.3 à préserver :** `project inspect`, `dictionaries audit|resolve`, `coverage report`, `wikidata import-local`, `projection export|verify|restore`. Compatibilité des options existantes, et `--format verbose` maintenu.

**Extensions 1.0 proposées**, après versionnement des DTO :

```text
dik workspace init|verify|repair-index
dik dictionaries sources list|add|disable
   ... reconcile scan|review|publish
   ... curate propose|review|publish
   ... search --locale fr --kind KQ --term ... [--domain KQ...]
dik wikidata mirror register|status|sync|diff|resume
dik coverage portfolio --projects manifest.json --locales fr,en,... --output ...
dik migration inventory|propose|review|submit --plan ...
dik projection export|verify|restore [--format compact|verbose] [--style clean|annotated]
dik jobs status|cancel|resume --job ...
dik audit verify|history|export
```

Les formes exactes seront finalisées avec tests d'API ; le tableau ci-dessus n'affirme pas l'existence de ces commandes dans diK 0.3.

## API-002 — Interface programme

Éviter les réponses polymorphes non typées. Résultat uniforme : `request_id`, `contract_version`, `status`, `data`, `errors[]`, `input_manifest_digest`, `output_manifest_digest?`, `warnings[]`. `status=success` uniquement si publication complète. `status=proposed` n'est pas `approved`, ni `published`.

### Opérations applicatives proposées

- `GET /v1/health`, `GET /v1/projects/{id}`, `GET /v1/catalogs/{id}/locales`, `GET /v1/identities/{namespace}/{id}`.
- `POST /v1/lookup/reverse`, `POST /v1/coverage/reports`, `POST /v1/projections`, `POST /v1/projections/verify`.
- `POST /v1/import-jobs`, `POST /v1/reconciliation-jobs`, `POST /v1/decisions/{id}/review`, `POST /v1/migration-plans`.
- `GET /v1/jobs/{id}`, `POST /v1/jobs/{id}/cancel`.

Ces routes sont **cibles de design**, non services déjà publiés. Le transport réseau n'est pas obligatoire pour exécuter le cœur ; la CLI doit appeler les mêmes use cases que l'API, sans dépendre du serveur.

## API-003 — Idempotence et conflits

Toute commande mutante accepte un `idempotency_key` ou en dérive une par opération ; même clé / mêmes paramètres => même résultat ; même clé / paramètres différents => `IDEMPOTENCY_CONFLICT`. Édition revue conditionnée à `expected_revision`/hash ; si changement simultané => `REVISION_CONFLICT`. Les opérations de lecture n'altèrent pas les manifestes.

## API-004 — Filtres et pagination

Recherches et matrice de couverture : pagination déterministe, curseur lié au snapshot, tri défini. Une API ne retourne pas silencieusement « tous les concepts de Wikidata » en RAM. Exports massifs en fichiers versionnés + manifestes/hashes.

## API-005 — Codes de sortie CLI

Proposition : `0 success`, `2 invalid_input`, `3 conflict_or_ambiguous`, `4 integrity_or_security_failure`, `5 external_source_unavailable`, `6 approval_required`, `7 contract_mismatch`, `8 partial_or_interrupted_job`, `9 internal_error`. Un code partiel ne doit pas se faire passer pour succès ; les exceptions doivent fournir `error_code` stable sans exposer secret/chemins sensibles.

## API-006 — Local d'abord

API bind `127.0.0.1` par défaut et authentification robuste si mode multiutilisateur; pas d'exposition réseau implicite. Pas de téléchargement réseau lors de la simple ouverture d'un projet. Formats JSON/JSONL strictement documentés et versions explicites.


---

<a id="doc-docs-12-interface-md"></a>

## Document : `docs/12_INTERFACE.md`

# 12 — Interface utilisateur complète

## UI-001 — Espaces principaux

1. **Vue Projets** : état de validité, Framework lié, namespace, graphes, dictionnaires, fraîcheur du miroir, tâches en cours.
2. **Sources de dictionnaires** : ajouter source Wikidata/tiers/fichier, licence, langues, provenance, statut, snapshot, priorité proposée ; jamais importer une source externe comme fiable sans contrôle.
3. **Atelier lexical** : chercher un KQ/KP ou un terme, comparer termes par langue et par domaine, revoir synonymes/corrections, preview des priorités/fallbacks.
4. **Conciliation** : file de candidats, vues côte à côte, relations exact/close/broad/narrow/related, preuves, décideur, raisons, refus/supersession.
5. **Complétude** : matrice Kristals × langues, filtres `KQ/KP`, direct/fallback/missing/conflicted, exports, delta entre snapshots.
6. **Projections** : choix graphe, langue/variante, clean/annotated, preview, export JSON réversible + rendu non réversible, verify, restore.
7. **Migration** : inventaire des rôles legacy, propositions/rejets, revue de chaque JSON Pointer, rapport source/commitment, plan envoyé au producteur.
8. **Audit et jobs** : historique, versions/hashes, erreurs structurées, téléchargements/imports/reprises et annulations.

## UI-002 — Modèle de confiance visible

Afficher **toujours** ce qui est `verified`, `candidate`, `unreviewed`, `missing`, `fallback`, `conflicted`. Aucun code couleur seul : statuts textuels, tooltip avec source et décision, icônes accessibles. Distinguer `un label disponible` de `une identité correctement alignée`. Un bouton « Accepter » doit indiquer les conséquences et nécessite un rôle autorisé.

## UI-003 — Lecture légère

Rendu clean ne montre pas obligatoirement les KQ mais chaque fragment peut ouvrir son détail (ID/namespace/source/langue/provenance). Les KQ manquants restent visibles comme lacune au lieu d'être remplacés par un mot conjectural. Mode annoté pour IA affiche références contextualisées, sans alourdir le canon. Un sélecteur de langue ne charge pas 300 dictionnaires.

## UI-004 — UX de revue

Vue diff avant/après ; afficher la phrase, l'ID cible, contexte type/propriété, source, licence et éventuelles ambiguïtés ; actions `proposer`, `rejeter`, `accepter avec preuve`, `différer`. La revue doit résister à double clic et perte réseau (clé idempotente, révision attendue). Impossible de passer `candidate` à accepted via simple tri/filtre.

## UI-005 — Accessibilité

Support navigation clavier, lecteurs d'écran, internationalisation, RTL (arabe, hébreu…), scripts multiples, très longs labels, et affichage d'alias non romains sans translittération forcée. Langue UI indépendante du choix de dictionnaire. La qualité des textes de 300 langues reste mesurée, non prétendue.

## UI-006 — Déploiement

Application locale utilisable sans compte cloud ; interface GUI portable selon technologie retenue. Une implémentation web locale ne doit pas exposer par défaut fichiers privés/dumps sans permission. Pas de télémétrie réseau cachée.


---

<a id="doc-docs-13-securite-md"></a>

## Document : `docs/13_SECURITE.md`

# 13 — Sécurité, provenance, licence et confiance

## SEC-001 — Modèle des menaces

Entrées potentiellement hostiles : dumps Wikidata, dictionnaires tiers, archives legacy, documents d'IA, labels avec Markdown/HTML/JSON malicieux, noms de fichiers, manifestes/path, fichiers trop volumineux et liens symboliques. Risques : exécution arbitraire, path traversal, zip/decompression bomb, injection SQL/HTML/Markdown, SSRF lors de téléchargement, effacement de couches curatées, falsification des décisions, empoisonnement de la recherche inverse.

## SEC-002 — Validation à chaque frontière

Utiliser parsing strict JSON Schema officiel pour artefacts Framework, validation de schéma applicatif pour documents diK, limites de taille/profondeur, UTF-8, contrôles namespace/type, chemins confinés au root, sorties JSON échappées, requêtes SQL paramétrées, quotas de ressources. Le contenu des dumps n'est jamais une instruction pour une IA, un appel système ou un interpréteur.

## SEC-003 — Intégrité vs authenticité

SHA-256 protège contre corruption accidentelle et permet adressage par contenu, mais ne prouve pas qui a émis un fichier. Le système affiche `hash_verified` distinct de `publisher_authenticated`. Pour des approbations distribuées, prévoir signature et contrôle des rôles ; aucune signature fictive ou « approved by AI » n'est acceptable.

## SEC-004 — Revue et rôles

Rôles conceptuels : `viewer`, `editor` (propositions), `reviewer` (approbations), `publisher` (snapshots), `operator` (imports). Un environnement mono-utilisateur peut implémenter un mode local explicite mais doit garder l'identité et les décisions d'audit. Un agent IA ne doit pas être compté comme réviseur humain ni contourner une approbation. Séparation des responsabilités pour décisions critiques, configurable suivant gouvernance.

## SEC-005 — Licences

Toute source externe exige métadonnées licence, origine, version, conditions d'usage/redistribution. Sans licence connue/compatible : quarantaine ; ne pas redistribuer automatiquement les entrées. Les données importées ne deviennent pas libres parce qu'elles sont encodées en JSONL. Les fichiers diK distribués doivent respecter l'AGPL et notices du code utilisé, sans inventer des permissions de redistribution.

## SEC-006 — Restauration historique

Les anciens commits/empreintes/bytes sont intouchables. La vérification d'un nouveau Kristal ne doit pas exiger la présence de Wikidata en ligne. Prévenir exfiltration de textes soumis en projet privé (pas de recherche distante implicite ni index central).

## SEC-007 — Déni de service

Quota taille fichier/shard, limite de langue sélectionnée par tâche, budget temps/mémoire, cancellation safe, nombre max de candidats/requêtes, liens symboliques et noms Unicode ambigus traités de manière explicite ; liste blanche de sources réseau, pas de téléchargement arbitraire sur URLs fournies par un dump.

## Cas de tests indispensables

SEC-T1 traversal JSON path, SEC-T2 HTML hostile rendu clean, SEC-T3 injection SQL dans alias, SEC-T4 réécriture d'une couche importée publiée, SEC-T5 faux SHA recalculé présenté comme signature, SEC-T6 reviewer absent, SEC-T7 quota dépassé et rollback, SEC-T8 import licence inconnue, SEC-T9 project multi-namespace fuite interdite.


---

<a id="doc-docs-14-performance-md"></a>

## Document : `docs/14_PERFORMANCE.md`

# 14 — Performance, échelle et protocole de mesure

## PERF-001 — Objectifs, pas promesses déjà atteintes

diK 1.0 vise les centaines de langues, les dictionnaires clairsemés, millions d'enregistrements lexicaux et un gros miroir Wikidata local. Les performances doivent être **mesurées sur une configuration publiée** et ne peuvent pas être déduites des 36 tests de diK 0.3 ou du seul gain de 72,6 % sur 1 000 assertions synthétiques.

### Budgets cibles proposés (à ratifier après mesures)

| Scénario | Budget P95 cible | Conditions |
|---|---|---|
| Lookup index chaud `(namespace,KQ,locale)` | 20 ms local | sans I/O réseau, index SQLite chaud |
| Recherche inverse d'un terme | 100 ms | top 25 candidats, index chaud, domaine connu |
| Projection de 10 000 assertions | 2 s | locale déjà indexée, hors sérialisation physique longue |
| Couverture 100 000 références sur 10 langues | 30 s | mode batch, index chaud, mémoire plafonnée |
| Import 10 M entrées Wikidata | débit documenté | mesurer temps total, mémoire, disque, reprise |

Ces chiffres sont **des hypothèses de qualification** à mesurer et ajuster avec décision de version, pas une assertion de réussite. Le P95 doit porter sur au moins 30 répétitions pertinentes et inclure la variance. Un résultat sur machine non décrite n'a pas valeur de certification.

## PERF-002 — Métriques obligatoires

Taille brut vs compact vs gzip, CPU max/moyenne, RSS max, disque temporaire, lecture séquentielle, nb de shards, débit d'import, taux cache, nombre de fichiers lus, durée de vérification des hashes, temps de reprise/crash, couverture 300 langues sparse, latence UI. Faire essais froid/chaud séparément.

## PERF-003 — Techniques

- Joins via index par ID/crosswalk, pas scans complets de tous les 300 fichiers par lookup.
- Imports en flux ; chunks bornés ; sorted writes/shards ; indexes versionnés ; snapshots immuables.
- Cache-aside par digest de manifeste, pas TTL approximatif pour un cache sémantique.
- Audit complet à publication et incrémental dans le quotidien ; cache de checksums seulement quand fichier/manifest/version validés.
- Projection une seule langue demandée ; `lexicon.entries` unique par ID ; Markdown calculé à la demande.
- Option de sharding graphique future uniquement **nouveau profil**, pas altération `dik.compact-projection/1.0`.

## PERF-004 — Jeu d'essais

S0 : fixture Framework v11. S1 : 1 000 assertions répétitives (comparaison v0.3). S2 : 100k assertions mixtes (littéraux et qualifiers). S3 : 1M identifiants dont plusieurs langues clairsemées. S4 : échantillon représentatif d'un dump Wikidata local. S5 : snapshot énorme/import interrompu/snapshot changé. Toutes les fixtures ont hash, provenance et droits appropriés ; aucune distribution de dump massif dans le dépôt Git.

## PERF-005 — Critère de release

Le rapport de performances joint à la release doit préciser *réussite/échec* pour chaque budget ratifié, version Python/OS/disque/RAM, exact format de fichier et commandes. Pas de « optimisé » uniquement parce que l'archive est plus petite.

## Révision candidate.2

Le protocole de banc détaillé et les limites absolues figurent dans [`26_BANC_PERFORMANCES.md`](#doc-docs-26-banc-performances-md). **Les budgets non ratifiés ne sont pas des KPI atteints.** Le banc officiel est une condition de release, pas une optimisation présumée.


---

<a id="doc-docs-15-tests-tck-md"></a>

## Document : `docs/15_TESTS_TCK.md`

# 15 — Test de conformité (TCK) et non-régression

## TCK-001 — Sources

Toujours exécuter : (a) tests unitaires/domain diK ; (b) tests des schémas et vecteurs réels Framework v11 draft.3 ; (c) tests compat `dik.compact-projection/1.0` et verbose v0.2 ; (d) cross-repo Authoring Kit + Integration Pack ; (e) tests historiques v9/v10 lecture ; (f) attaques et tests de reprise.

Les cas spécifiés dans ce dossier ne sont **pas déjà exécutés** ; c'est une liste normative destinée à la future implémentation.

## TCK-002 — Catégories bloquantes

| ID | Propriété | Test positif | Rejet exigé |
|---|---|---|---|
| ID | Canon KQ/KP et namespace | graphe exemple validé | Q brut, label canon, namespace croisé |
| LEX | Couches/fallback | `fr-CA -> fr` déclaré | conflit égal, fallback implicite, SHA faux |
| XW | Crosswalk approuvé | accepted exact avec KS | unreviewed, 2 exact actifs, mauvais type |
| PRJ | Round-trip | `restore(export(G))==G` | restaure depuis clean.md, graph altéré |
| MIG | Migration supervisée | plan approuvé puis nouveau commit producteur | global replace, citation convertie |
| COV | Couverture séparée | KQ/KP et direct/fallback | 100% avec missing/conflict |
| IMP | Idempotence/snapshot | import répétable | écrit sous ID publié différent |
| OPS | Crash atomique | ancien catalogue visible | partial catalogue visible |
| SEC | Entrées malveillantes | escaping et quotas | traversal, injection, chaîne hostile |
| PERF | Indices/rebuild | index supprimé puis reconstruit | SQLite devient canon |

## TCK-003 — Tests d'invariants génératifs

- Générer des IDs valides de multiples namespaces, y compris mêmes numéros ; vérifier non-fusion.
- Générer littéraux arbitraires, emojis, Unicode combinant, caractères RTL et Markdown ; round-trip exact sur valeurs sémantiques.
- Générer couches dans différents ordres de fichiers ; si priorité identique, sortie stable ou erreur de conflit, jamais choix dépendant de l'énumération.
- Générer 301 tags et couverture clairsemée ; zéro langage fictivement « complet ».
- Perturber dump ou annuler job à chaque frontière de publication ; aucune mutation partielle canonique.

## TCK-004 — Oracles

Un test doit comparer sorties diK au **calcul de référence Framework** quand il existe : validation v11, couverture, audit crosswalk ; pour projection comparer equality structurelle du graphe, pas comparaison de Markdown seul. L'Integration Pack doit afficher les mêmes IDs et le même décompte de couverture que diK. L'Authoring Kit doit revérifier un plan avant migration.

## TCK-005 — Gates CI

`G1` lint/docs + schémas, `G2` tests unitaires, `G3` négatifs et propriétés, `G4` contrats Framework, `G5` interop Authoring + Integration, `G6` sécurité + reprise, `G7` bench performance, `G8` package déterministe/manifest signature selon politique. Aucun `G1–G6` en échec ou non exécuté pour RC/stable. `G7` selon budgets ratifiés ; preuves jointes.

## TCK-006 — Traçabilité

Chaque nouveau test porte un ID exigence et un cas d'essai ; chaque MUST a au moins un test positif et un test d'échec. La matrice [`17_TRACABILITE.md`](#doc-docs-17-tracabilite-md) est le registre initial, à compléter par lien précis vers fichier/méthode/résultat lorsque le code sera produit.

## Révision candidate.2 — preuves machine et périmètres

`tests/requirements.json` inventorie individuellement les exigences `ID`, `LEX`, `XW`, `IMP`, `PRJ`, `MIG`, `COV`, `OPS`, `API`, `UI`, `SEC`, `PERF`, `TCK` ; pour chaque exigence, un scénario positif et négatif requis, initialement `NOT_RUN`. `tests/reference_vectors.json` sert d'oracle de décisions locales. Exécuter `tools/verify_reference_vectors.py` pour vérifier l'oracle, puis l'implémentation diK réelle contre **les mêmes vecteurs**. Le premier résultat ne remplace pas le second.


---

<a id="doc-docs-16-release-md"></a>

## Document : `docs/16_RELEASE.md`

# 16 — Qualification et publication diK 1.0

## GO / NO-GO

**GO seulement si :** toutes les exigences P0/P1 ont implémentation + preuves ; schémas Framework v11 épinglés ; formats de projection v0.2/v0.3 lus ; import Wikidata massif mesuré ; 301 langues sparse sans incohérence ; tests d'interruption et de sécurité ; migrations legacy produites via producteur autorisé ; graphiques/rapports fiables ; GUI et API documentées ; licence/attribution validées ; archive/package reproductible et installable sans mode réseau obligatoire.

**NO-GO si :** une assertion d'identité provient d'un mot sans revue ; un `Q` entre dans le canon ; une couche curated est écrasée ; `restore` déduit ID depuis `clean.md` ; `100%` inclut missing ; un outil modifie v9 commitments ; un test bloquant est `NOT_RUN` ; le Framework n'est plus identifiable par pin digest ; la reprise d'import perd ou duplique des données.

## Jalons de développement proposés

1. **0.4** : domaine hexagonal, conciliation multisource, revue/provenance, recherche inverse et idempotence.
2. **0.5** : inventaire legacy, plans de conversion, boucle d'intégration Authoring, édition linguistique/patch distincts.
3. **0.6** : miroir Wikidata, import/deltas/reprises, index durable rebuildable, 300+ locales et jeux massifs.
4. **0.8** : API CLI stabilisées, UI, rôles/audit, sécurité et accessibilité.
5. **0.9 RC** : TCK complet, benches ratifiés, compat Framework/Auth/Integration, audit de licences, guide opérateur.
6. **1.0.0** : artefacts reproductibles, release signée si la gouvernance l'exige, notes de migration, document d'écarts nul ou approuvé.

Ces numéros sont **planifiés**, pas livrés. Stabiliser Framework v11 séparément si draft.3 change ; pin de la release doit figer un artefact exact et son digest.

## Pièces obligatoires de la release

- SBOM dépendances + licences, CHANGELOG, MIGRATION_GUIDE, manifeste SHA-256, versions de schémas & API, rapport TCK avec tests NOT_RUN distingués, matrice couverture KQ/KP langues, benchmark machine/commandes, tests de restauration de snapshots.
- Guide sécurité, plan sauvegarde/restauration, politiques d'import, limites connues et décision de compatibilité cross-repo.
- Un paquet installable, CI reproductible, jeux d'exemples non fictivement certifiés, journal des exceptions.

## Changement de norme Framework

Une nouvelle draft du Framework ne modifie pas unilatéralement `diK 1.0`. Ouvrir ADR, comparer schémas, choisir une migration de profil/version, recréer golden fixtures, vérifier anciennes projections/crosswalks ; seule une nouvelle release compatible pourra utiliser le nouveau pin.

## Addendum candidate.2 — blocage de la version stable

La release est refusée si `tests/requirements.json` contient une exigence sans **deux** preuves exécutées (positive et négative), si `tests/TCK_CASES.json` conserve un `NOT_RUN` bloquant, si la validation `--strict` échoue ou si un artefact de D2/D3 de `docs/25_GATES_CI_EXECUTABLES.md` manque. Les décisions et budgets non ratifiés sont marqués explicitement comme `BLOCKED` et non comme valeurs par défaut approuvées.


---

<a id="doc-docs-17-tracabilite-md"></a>

## Document : `docs/17_TRACABILITE.md`

# 17 — Traçabilité exigences → modules → tests

**Règle IA :** chaque PR met à jour ce tableau pour ses exigences, sans retirer une ligne incommodante. `TARGET` = pas encore implémenté/certifié.

| ID | Exigence source | Module cible | Tests de preuve requis | État initial |
|---|---|---|---|---|
| ID-001..005 | Framework Identity-and-Wikidata | domain/identity | ID-R1..R6 | upstream + partiel v0.3 |
| LEX-001..006 | Framework Dictionary-Management | domain/lexical, adapters/fs | LEX-R1..R8 | partiel v0.3 |
| XW-001..005 | Framework Identity-and-Wikidata | domain/alignment | XW-T1..T7 | TARGET |
| IMP-001..005 | Framework Dictionary-Management | adapters/wikidata | IMP-T1..T6 | import local v0.3, reste TARGET |
| PRJ-001..007 | diK v0.3 compact/verbose + Framework | domain/projection | PRJ-T1..T8 | partiel v0.3 |
| MIG-001..006 | Framework Legacy-Resolution / diK-Interoperability | app/migration, authoring adapter | MIG-T1..T9 | TARGET |
| COV-001..006 | Framework diK-Interoperability | app/coverage | COV-T1..T6 | mono-graph v0.3, reste TARGET |
| OPS-001..015 | Patterns #08,#10,#12,#15,#18,#25,#31 | app/ports/adapters/workspace | atomic/crash/cache/rebuild | TARGET |
| API-001..006 | Décision diK cible | cli/api | compat v0.3, contrats erreurs | TARGET |
| UI-001..006 | Décision diK cible | ui | workflow, accessibility, RTL | TARGET |
| SEC-001..007 | Décision diK cible | boundaries | SEC-T1..T9 | TARGET |
| PERF-001..005 | Décision diK cible | benchmarks | S0..S5 | TARGET |
| TCK-001..006 | Framework Conformance + diK cible | tests/CI | G1..G8 | TARGET |

## Règle pour les changements

Dans un PR : `requirement_id`, `source_reference`, `acceptance_test`, `expected_failure`, `evidence_file`, `impact_legacy`, `state`. Ne jamais convertir `TARGET` en `DONE` sans test exécuté, output enregistré et preuve lisible. Une exigence contredisant le Framework est `BLOCKED` et une ADR est nécessaire.

## Révision candidate.2 — registre individualisé

Le fichier [`../tests/requirements.json`](#doc-tests-requirements-json) développe les plages d'identifiants ci-dessus en enregistrements individuels. Tous ont un résultat produit initial `NOT_RUN`, et deux scénarios `positive`/`negative`. L'enregistrement d'une preuve réelle est réalisé par CI d'implémentation, pas par édition à la main du tableau.


---

<a id="doc-docs-18-integration-md"></a>

## Document : `docs/18_INTEGRATION.md`

# 18 — Compatibilité Framework, Authoring, Integration et Kristals existants

## Contrats connus (snapshots fournis)

- **Framework v11 draft.3** : source normative des schémas, outils v11 de référence, profils lecteurs, lexique, crosswalk, coverage et plans non exécutables.
- **Authoring Kit 4.0.0-draft.2** : producteur pouvant qualifier v11 (`qualify-v11`), gardien de révision et migration potentielle ; **ne pas supposer que la migration automatisée universelle est déjà implémentée**.
- **Integration Pack 0.2.0-alpha.1** : adaptateurs de lecture et projections ; devrait consommer les IDs KQ/KP sans en faire du texte canonique.
- **diK 0.3.0** : import local, audit, rapport, projection compacte/verbose/restore ; les workflows nouveaux de 1.0 restent à coder.
- **A-Kristal-Catho** : corpus pilote legacy ; ne pas modifier les originaux sans sauvegarde/version et plan approuvé.

## Test croisé obligatoire

1. Charger fixtures Framework v11 draft.3 avec diK et Authoring Kit ; produire coverage identique structurellement, même dénominateur KQ/KP.
2. Exporter une projection compacte avec diK ; vérifier via diK et le consommateur si ce dernier revendique la compatibilité ; restituer `G` et comparer à l'original.
3. Présenter la vue dans Integration Pack : labels uniquement dans zone de présentation, jamais dans les IDs.
4. Générer plan legacy diK; Authoring Kit **revérifie** source hash, rôle du champ, décisions et KS, puis produit une nouvelle révision ; l'ancien artefact reste identique.
5. Tester une version de schéma modifiée -> rejet du pin, pas fallback silencieux.

## Publicités de compatibilité interdites

Ne pas dire « Full v11 certified » si seule la validation JSON Schema marche. Ne pas assimiler complétude lexical et alignement Wikidata. Une migration testée sur trois mots n'est pas une qualification de Catho entier.

## Dépendances de publication

- diK peut être livré avec snapshot Framework draft.3 épinglé et indiquer sa compatibilité **limitée**.
- Pour marquer diK 1.0 stable, l'équipe décide si Framework doit être stable ou si un draft exact peut être cible ; si draft, mentionner ce risque explicitement.
- Toute modification normative hors diK doit être proposée au repo Framework, pas injectée silencieusement dans un adaptateur diK.


---

<a id="doc-docs-19-locales-md"></a>

## Document : `docs/19_LOCALES.md`

# 19 — Langues, scripts, variantes et registres

## LEX-020 — Normalisation

Utiliser une bibliothèque/registre BCP 47 approprié, versionné et documenté : validité de la langue, canonicalisation (alias/variante/script/région) et tag source conservé à des fins d'audit. Une simple regex `fr-CA` ne prouve pas une langue valide. Choisir une seule politique d'égalité de tags et la tester sur `fr`, `fr-CA`, `zh-Hans`, `zh-Hant`, `sr-Latn`, `ar` et tags inattendus.

## LEX-021 — Fallback

Chaque repli est un arc déclaré dans le catalogue. `fr-CA -> fr` n'autorise pas `fr -> en` sans déclaration ; interdire cycles et ambiguïtés de priorité. Un libellé en langue de repli ne compte pas comme `direct`. Ne pas supposer que `zh-Hant` et `zh-Hans` sont interchangeables, ni qu'une translittération constitue une traduction.

## LEX-022 — Unicode et rendu

Conserver Unicode d'origine, normaliser pour **comparaison** par NFC si nécessaire, mais ne pas perdre les distinctions significatives ; sécuriser rendus HTML/Markdown ; RTL et scripts combinants testés ; normalisation ne sert jamais à fusionner des concepts. Les formes fléchies, sens lexicographiques et lemmes Wikidata L sont hors import Q/P par défaut.

## LEX-023 — 300+ langues

Les langues sont déclarées même avec zéro entrée ; couverture sparse évaluée avec `missing`. Le catalogue doit permettre shards compressés et nombreux locales sans charger l'ensemble pour résoudre une locale. TCK inclut **301 langues déclarées** et plusieurs scripts, avec fallback vérifié.

## LEX-024 — Préférence contextuelle

Terme de spécialité (théologie, physique) peut l'emporter sur le dictionnaire général par profil de domaine/version, jamais sur la seule orthographe ; termes homographes distincts peuvent référer à plusieurs KQ. Une interface affiche la provenance et la langue effective du terme rendu.


---

<a id="doc-docs-20-etats-et-transactions-md"></a>

## Document : `docs/20_ETATS_ET_TRANSACTIONS.md`

# 20 — Machines d'états, transactions et opérations idempotentes

## Décision de correspondance

`proposed -> in_review -> accepted | rejected`; `accepted/rejected -> superseded` seulement avec nouvelle décision référencée. `accepted` exige reviewer + méthode + preuve KS + unicité des `exactMatch`. Les décisions rejetées restent auditées.

## Import

`planned -> downloading? -> parsing -> staging -> validating -> ready -> published` ; de n'importe quel état prépublication : `failed|cancelled`, avec rollback du staging et reprise conditionnelle. Un manifest publié ne revient pas à editing : publier une révision supérieure. État `published` = tous shards/hashes accessibles et le pointeur atomique actif.

## Migration

`inventory -> proposed -> reviewed -> approved_for_submission -> producer_verified -> new_revision_published`. Aucun saut de `proposed` vers publication ; `approved` par une IA sans rôle vérifié invalide. Une modification de la source ou du plan retire l'autorisation précédente.

## Opération sûre

Chaque commande mutante stocke `idempotency_key`, hash entrée, version outils, statut, résultat/digest et journal d'étapes. En cas d'exécution répétée : même clé+même hash => replay du résultat ; clé égale/hash différent => erreur ; tentative concurrente => une seule publication, les autres détectent conflit. Stockage transactionnel local et atomic rename à l'étape d'activation.

## Exception/corruption

Si un artefact publié est corrompu, ne jamais corriger silencieusement ses octets. Marquer `quarantined`, conserver preuve, revenir au dernier snapshot vérifié si configuré et journaliser l'intervention. Ne pas supprimer des preuves historiques pour « réparer » des chiffres de couverture.

## Tests d'états

Transitions interdites, crash à chaque étape, double publication, révision périmée, nouvel ETag externe entre checkpoint/reprise, utilisateur non autorisé et plan changé après approbation doivent tous produire un échec propre et reproductible.


---

<a id="doc-docs-21-erreurs-observabilite-md"></a>

## Document : `docs/21_ERREURS_OBSERVABILITE.md`

# 21 — Taxonomie d'erreurs, audit et observabilité

## Codes d'erreur stables (cibles)

- `DIK_ID_INVALID` : type ou namespace d'ID invalide.
- `DIK_CONTRACT_MISMATCH` : schéma Framework ou profil de projection incompatible.
- `DIK_LEX_MISSING`, `DIK_LEX_CONFLICT`, `DIK_LOCALE_UNKNOWN`, `DIK_FALLBACK_CYCLE`.
- `DIK_XW_NOT_APPROVED`, `DIK_XW_CONFLICT`, `DIK_EVIDENCE_MISSING`.
- `DIK_PROJECTION_NOT_REVERSIBLE`, `DIK_PROJECTION_TAMPERED`, `DIK_ORIGIN_NOT_AUTHENTICATED`.
- `DIK_MIG_ROLE_UNKNOWN`, `DIK_MIG_SOURCE_CHANGED`, `DIK_MIG_APPROVAL_REQUIRED`.
- `DIK_SOURCE_UNAVAILABLE`, `DIK_IMPORT_INTERRUPTED`, `DIK_QUOTA_EXCEEDED`.
- `DIK_IDEMPOTENCY_CONFLICT`, `DIK_REVISION_CONFLICT`, `DIK_STORAGE_CORRUPT`.

Les messages humains peuvent être traduits sans changer le code machine. Les appels API doivent retourner le rôle du champ, chemin/pointeur pertinent et remédiation recommandée, sans exposer données secrètes ou dumps entiers dans les logs.

## Traçabilité minimum

`request_id/job_id`, command/version, namespace, hash manifeste, source snapshot, number examined/accepted/missing/conflicted, temps CPU/IO, cache hit, état des transitions et sortie SHA. **Ne pas logger automatiquement les contenus textuels complets**, ni les documents d'utilisateur ; exporter une preuve explicite à la demande.

## Audit de décisions

Journal append-only : qui/quoi/quand, rôle, source/avant/après, motif, preuves, hash de plan, version registre/crosswalk/catégorie lexicale, éventuelle supersession. Distinguer prévisualisation de publication. La présence d'un hash n'est pas une signature d'approbation.

## Observabilité sans serveur imposé

CLI affiche progression stable et sauvegarde logs structurés locaux ; interface suit les jobs et états partiels ; exporter métadonnées sans identités privées si l'utilisateur le veut. Aucune télémétrie réseau requise ou activée silencieusement.


---

<a id="doc-docs-22-evolution-des-contrats-md"></a>

## Document : `docs/22_EVOLUTION_DES_CONTRATS.md`

# 22 — Versionnement des formats et gestion des changements

## Profil vs version de l'application

- `diK 1.0.0` : version du logiciel cible.
- `dik.compact-projection/1.0` : **profil JSON préexistant** depuis diK 0.3 ; doit rester lisible.
- `kristal_* schema_version=11.0` : contrats **Framework**, et non diK.
- `dik.*` contrats dans `contracts/` de ce dossier : **propositions applicatives** `1.0-candidate`, non norme upstream adoptée.

Ne pas déduire qu'un changement de version de diK permet de changer la signification d'un schéma Framework. Toute rupture de profil doit recevoir un nouveau nom de profil et un adaptateur de lecture.

## Algorithme de comparaison de profils

Pour tout changement : comparer listes de champs/type/nullabilité, contraintes d'identité, hash algorithm, ordre canonique, comportements missing/fallback, provenance et sécurité. Tests de fixtures antigas dans chaque direction permise. Une modification au format de données de sources externes passe par adaptateur Anti-Corruption Layer.

## Gouvernance d'une ADR

Inclure : problème réel, source/contrat existant, options étudiées, changement proposé, tests positifs/négatifs, impact stockage/compatibilité, plan de migration/réversibilité, statut `proposed|accepted|rejected|superseded` et décideur. Une IA peut rédiger l'ADR, pas déclarer acceptée à la place des décideurs.

## Backward compatibility minimale

- Importer/valider les anciennes projections v0.2 verbose et v0.3 compact sans conversion implicite vers un faux canon.
- Lire les Kristals historiques avec adaptateurs explicitement versionnés ; ne pas les réécrire.
- Écrire **uniquement** de nouveaux artefacts conformes à Framework v11 fixé par manifest.
- Préserver registre et crosswalks historiques et leurs décisions.


---

<a id="doc-docs-23-profil-local-gouvernance-md"></a>

## Document : `docs/23_PROFIL_LOCAL_GOUVERNANCE.md`

# 23 — Profil local 1.0 et gouvernance des décisions

**Type : choix normatifs candidats diK, non modification du Framework.** Référence ADR-0003.

## Produit local fini

La version 1.0 cible un poste, fonctionne **hors ligne** (après installation), et peut exploiter un miroir Wikidata local. Les requêtes de téléchargement sont explicites ; une simple projection n'utilise jamais le réseau. La CLI reste un support de premier rang ; UI desktop ou web loopback possible, à décider au moment de l'implémentation avec contrôle d'authentification/CSRF si web.

Le moteur est un **monolithe modulaire** : `domain` pur (identity, lexical, alignment, projection, coverage), `application` (revue, import, publication, migration-plan), `adapters` (Framework, Wikidata, fichiers, SQLite, CLI/UI). Ports typés, interfaces versionnées, zéro import de SQLite ou de HTTP dans `domain`. Les caches n'allouent jamais de KQ et n'approuvent jamais une correspondance.

## Permissions de publication

Les fichiers historiques et catalogues publiés sont immuables. Une correction crée un nouveau snapshot avec manifeste et empreinte ; un pointeur atomique active le snapshot seulement après validation. Avant activation, aucune nouvelle donnée n'est visible. En cas de crash, le précédent manifeste vérifié reste actif. En cas de corruption, quarantaine, pas de réécriture silencieuse.

La provenance et les décisions sont distinctes des préférences lexicales. Le réviseur doit être enregistré comme **identité d'acteur existante**, jamais inventé par l'IA. Les décisions acceptées exigent preuves KS et contraintes de correspondance exactes imposées par Framework ; diK ne peut pas auto-conférer l'autorité de `reviewer`.

## Contrôle des changements

Toute ambiguïté entre ce profil et Framework v11 draft.3 = `BLOCKED: CONTRACT_CONFLICT`. Les 5 contrats JSON diK `1.0-candidate` ne deviennent **pas** des schémas ratifiés par le simple fait de compiler. Une release stable exigera leur gel explicite et une suite de compatibilité.


---

<a id="doc-docs-24-algorithmes-oracles-md"></a>

## Document : `docs/24_ALGORITHMES_ORACLES.md`

# 24 — Algorithmes de référence et vecteurs exacts

**Autorité :** Framework v11 draft.3 pour l'identité et la résolution lexicale. Les algorithmes ci-dessous explicitent son emploi dans diK ; ils ne remplacent pas le code ou les schémas officiels.

## 24.1 Résolution d'un libellé (`LEX-003`)

Entrée : `(namespace_id, semantic_id, requested_locale, catalog_sha256, optional domain)`. Charger le catalogue validé par manifest, sans énumérer le disque librement. Lire la locale demandée puis, **dans l'ordre déclaré**, les locales fallback ; refuser cycles et langues non déclarées. Pour chaque locale effective, prendre les couches déclarées ; la **plus grande valeur numérique** `priority` l'emporte (conforme au résolveur de référence v11 draft.3). Si plusieurs termes différents sont à la priorité maximale : `conflicted`; un même terme répété à la même priorité n'invente pas plusieurs sens. Si aucune couche ne fournit le terme, passer au fallback explicite ; sinon `missing`. La locale demandée a préséance sur un fallback même si la couche fallback possède une priorité numériquement supérieure.

Sortie normative de base : `status, semantic_id, requested_locale`; si résolu, `effective_locale, fallback, term, layer`. Pour diK, ajouter provenance et digests dans une **enveloppe dérivée** sans réécrire la sortie Framework. Ne pas promettre qu'un label suffit à définir le sens.

## 24.2 Recherche inverse (`XW-001`)

Entrée `(namespace, term, locale, expected_kind KQ|KP[,domain], index_digest)`. Comparer Unicode NFC, rechercher exclusivement la langue demandée (à moins d'un paramètre séparé de fallback) et le type attendu, renvoyer les **identifiants candidats** triés par `(namespace_id, semantic_id)` pour une représentation déterministe. Pas de `exactMatch` par égalité du terme. Un seul candidat donne `unique_candidate`, jamais `accepted`. Plusieurs candidats : `ambiguous` ; zéro : `no_candidate`. Les alias ne sont pas nécessairement des traductions. Un moteur de similarité peut enrichir les candidats, mais doit fournir provenance, méthode et score sans pouvoir approuver.

## 24.3 Correspondance externe (`XW-002..004`)

Valider : espace de noms, classe KQ→Q ou KP→P, relation exacte, statut `accepted`, décision et méthode, identité de réviseur autorisé et preuves KS, unicité active des deux côtés dans le même snapshot. Toute correspondance `candidate|rejected|superseded` ou `related|close|broad|narrow` est non substituable. Réception d'un nouveau Q externe : proposer et réviser un nouveau crosswalk ; conserver le KQ, le graphe et les SHA historiques inchangés.

## 24.4 Couverture (`COV-001..006`)

Inventorier les *références distinctes* par `(namespace_id, KQ|KP)` dans le graphe, y compris les qualificatifs ; KA et KS n'entrent pas au dénominateur lexical. Pour chaque langue demandée : `direct` si label validé dans cette langue, `fallback` si label résolu uniquement par repli déclaré, `missing` sans terme, `conflicted` si conflit non résolu. Les classes sont disjointes ; leur somme = dénominateur. `complete_direct = (direct == denominator && conflicted == 0)` ; `complete_usable = (direct + fallback == denominator && conflicted == 0)`, **sous réserve que le dénominateur soit connu**. Un dénominateur vide est marqué `not_applicable`, pas « 100 % traduit », dans les tableaux diK (ce statut de présentation ne modifie pas le schéma Framework). Un graphe historique contenant un mot non résolu signale `legacy_denominator_unknown` et ne peut être déclaré complet à 100 %.

## 24.5 Projection et restauration (`PRJ-001..007`)

Export : charger le canon validé ; construire table des libellés une seule fois par ID utilisé ; conserver **le graphe canonique complet** dans l'enveloppe réversible et joindre digest du graphe/cat/version du résolveur. Rendu annoté inclut les IDs ; rendu épuré masque l'ID en UI/Markdown seulement. Restore : vérifier intégrité et provenance selon le profil ; renvoyer `canonical_graph` **sans** inférer depuis `label`/Markdown. Vue `clean.md` seule : `NOT_REVERSIBLE` ; changement sémantique en lecture : produire intent de patch, sans mutation canonique.

## 24.6 Écritures, reprise et idempotence (`OPS-001..015`)

Avant chaque mutation, calculer une clé stable à partir du manifeste et de paramètres fixés ou demander une clé explicite, liée au *digest de l'entrée*. Journaliser `idempotency_key`, `input_digest`, `tool_version`, `state`, `result_digest`. Même clé + même digest : retourner le résultat existant ; même clé + digest différent : `IDEMPOTENCY_CONFLICT`. Concurrence : sérialiser publication avec verrou et comparer pointeur actif attendu ; jamais deux publications concurrentes sous une révision. Écrire temporairement tous les fichiers, vérifier SHA et droits, synchroniser stockage, **puis seulement** publier atomiquement un manifeste/pointeur. Un crash antérieur ne doit pas rendre le staging visible. Un crash post-publication doit permettre une lecture cohérente ou un rollback explicite vers snapshot antérieur validé.

## 24.7 Migration des anciens graphes (`MIG-001..006`)

Identifier uniquement les champs jouant le rôle de références sémantiques, **pas** les citations/valeurs littérales ; enregistrer chemin JSON exact, ancien texte/URN, namespace, candidats, preuves et `source_graph_sha256`. Le plan reste non exécutable dans diK. Toute ambiguïté nécessite revue humaine. L'Authoring Kit/producteur valide de nouveau la source et chaque choix avant de publier une **nouvelle révision** ; l'original et son engagement sont inchangés.

## 24.8 Formes d'échec stables

`BLOCKED: CONTRACT_CONFLICT`, `INVALID_NAMESPACE`, `AMBIGUOUS_IDENTITY`, `UNVERIFIED_ALIGNMENT`, `LEXICAL_CONFLICT`, `MISSING_TRANSLATION`, `INTEGRITY_MISMATCH`, `STALE_SOURCE`, `IDEMPOTENCY_CONFLICT`, `NOT_REVERSIBLE`, `UNAUTHORIZED_MIGRATION`, `UNDECLARED_LOCALE`, `UNTRUSTED_SOURCE`. Le code CLI/API peut posséder une enveloppe typée additionnelle, mais ces erreurs ne doivent pas être transformées silencieusement en succès.

## 24.9 Source des oracles

`tests/reference_vectors.json` contient des cas **documentaires reproductibles**. `tools/verify_reference_vectors.py` les vérifie indépendamment d'une future implémentation. Les tests d'intégration de diK 1.0 doivent charger les mêmes vecteurs et produire les mêmes résultats, ainsi que les fixtures complètes Framework v11. Un succès de ce petit oracle documentaire **ne** prouve **pas** la conformité de diK.


---

<a id="doc-docs-25-gates-ci-executables-md"></a>

## Document : `docs/25_GATES_CI_EXECUTABLES.md`

# 25 — Gates CI anti-drift : du dossier à l'implémentation

## Différence cruciale entre 3 niveaux de preuve

- **D1 : validation du dossier.** Schémas candidats, liens, référence SHA, matrice, vecteurs oracles, aucun résultat TCK inventé.
- **D2 : conformité du logiciel.** Même jeux de vecteurs exécutés sur **diK 1.0 réel** et sur validateurs Framework officiels ; preuves liées à commit, versions et environnement.
- **D3 : qualification produit.** Tests de reprise/crash, sécurité, cross-repo, benchmarks et restauration sur corpus représentatifs, 301 langues sparse, revue humaine des écarts.

**Jamais D1 ⇒ D2 ni D2 ⇒ D3.** Exécuter `--strict` sur D1 est un garde-fou documentaire, pas une certification produit.

## Commandes D1 reproductibles

```bash
python -m pip install 'jsonschema>=4.21,<5'
python tools/validate_documentation.py
python tools/verify_reference_vectors.py
# Blocage si les fichiers source et le Framework montés ne correspondent pas au verrou :
DIK_SOURCE_DATA_ROOT=/mnt/data KRISTAL_FRAMEWORK_ROOT=/mnt/data/work_kristal_v11_draft3 \
  python tools/validate_documentation.py --strict
```

Sans montages, la commande stricte **DOIT échouer** : il est interdit d'émettre `PASS` au lieu de `NOT_VERIFIED`. Une CI diK 1.0 réelle installera les sources épinglées dans un emplacement dédié de façon reproductible.

## Gates D2/D3 (à développer dans le dépôt applicatif)

| Gate | Tests obligatoires | Bloque release stable si |
|---|---|---|
| G1 Documentation | D1 strict + schémas et versions | sources absentes, SHA différents, contrats inconnus |
| G2 Module | positifs+négatifs liés aux IDs des exigences | scénario attendu `NOT_RUN/FAIL` |
| G3 Invariants | fuzz/Unicode/RTL, intégrité, aucun Q dans canon, non-fusion | un seul contre-exemple |
| G4 Framework | validateurs réels, golden fixtures, graphe v11, compat v0.2/v0.3 | hash ou sortie diverge |
| G5 Intégrations | Authoring Kit et Integration Pack en versions verrouillées | interprétation différente d'un même graphe |
| G6 Sûreté | corruption, crash chaque étape, quarantaine, import malveillant, rollback | mutation canonique ou perte de snapshot |
| G7 Performance | banc mesuré et budgets ratifiés, mémoire et tailles | dépassement ratifié, rapport absent |
| G8 Packaging | reproductibilité, installation offline, SBOM et attribution | manifeste divergent ou install impossible |

## Traçabilité bloquante

`tests/requirements.json` fournit un identifiant **individuel** pour les 87 exigences titrées de la spécification ; chaque ligne doit pointer vers un test positif ET un test négatif (ou justification de non-applicabilité signée en ADR), une preuve d'exécution et une version source. Tant que `NOT_RUN`, la couverture D2/D3 est 0 %, non pas « implicite par la documentation ». Les résultats doivent être produits par CI, pas édités à la main.

## Revue automatique de dérive

Échec si le diff introduit une identité interne `Q[0-9]+` à la place de KQ, un champ `label` de propriété canonique, un accès réseau implicite dans une fonction pure, une suppression d'historique, une approbation construite avec score seul, une désactivation de schéma ou un changement de profil compact sans version. Analyse statique heuristique = alerte ; les validateurs structurés/fixtures sont la preuve. On ne « corrige » pas la CI en supprimant son test.

## Résultats et gouvernance

Chaque PR conserve `.evidence/<sha>/` (outside documentation spec) : commandes exactes, logs structurés avec PASS/FAIL/NOT_RUN, SHA entrées/sorties, version Python et plateforme. Un agent n'est pas habilité à signer une revue humaine. Avant release, toutes décisions bloquantes passent par une ADR approuvée par propriétaire réel.


---

<a id="doc-docs-26-banc-performances-md"></a>

## Document : `docs/26_BANC_PERFORMANCES.md`

# 26 — Qualification performance, confidentialité et grande échelle

Ce chapitre **n'affirme aucune performance déjà atteinte par diK 1.0**. Les budgets de `14_PERFORMANCE.md` sont des candidats soumis à ratification ; toute qualification doit être mesurée puis archivée avec le commit.

## Profils distincts

- **S0** : fixture Framework v11, objectif exactitude, sans benchmark.
- **S1** : 1 000 assertions répétitives pour mesurer compact JSON et gzip ; documenter ratio sur données brutes et compressées.
- **S2** : 100 000 assertions de tailles variées (refs, qualifiers, littéraux, Unicode). Mesurer P50/P95, RSS, taille, pertes nulles après restore.
- **S3** : 1M de référents, 301 locales clairsemées. Ne préallouer aucune matrice dense ; mesurer couverture, index SQLite, mémoire et durées froid/chaud.
- **S4** : échantillon réel de la copie Wikidata avec provenance/attribution et snapshot digest ; import à mémoire bornée, sharding et delta.
- **S5** : interruption aux étapes d'import et de publication, index détruit/reconstruit, reprise après pointeur cassé ; la justesse prime sur le débit.

## Méthode de mesure reproductible

1. Déclarer OS, version Python, type CPU/cœurs, RAM, disque SSD/HDD, version SQLite, versions de dépendances et SHA du programme.
2. Établir un warmup, exécuter ≥ 30 mesures individuelles pour P95, rendre P50/P95/min/max et distribution de latence sans cacher les échecs.
3. Distinguer *cold index* / *warm index* / *warm cache*, I/O réseau interdit sauf test explicitement dédié. Inclure coût de validation à publication et de reconstruction d'index.
4. Mesurer CPU max/moy, pic RSS, disque temporaire maximal, volume du dump d'origine, taille lexicale totale, temps de reprise, nb de ressources mises en quarantaine et nb de fichiers ouverts.
5. Comparer diK v0.3 existant et diK 1.0 dans des conditions identiques ; chaque optimisation doit préserver l'oracle et les hashes historiques.
6. Publier les seuils **ratifiés** dans un manifest de benchmark approuvé ; avant cette étape on rapporte métriques, et on n'attribue pas de statut « optimisé/certifié ».

## Conditions de blocage indépendantes des budgets chiffrés

OOM, corruption, création de mapping fictif, double publication, utilisation d'un mot comme KQ, pertes d'historique, résultat de couverture inexact, résultat différent selon ordre des fichiers => **FAIL** même si rapide.

## Approches attendues

Index SQLite FTS (source dérivée) avec clé `(namespace,id,locale,catalog_sha)`, cache-aside invalidé par empreinte, lecture seule des snapshots et chargement de la langue demandée, pipeline stream JSONL par lots bornés, publication atomique, reproductibilité des sorties. Le modèle doit fonctionner sans 300 copies intégrales de Wikidata.


---

<a id="doc-decisions-adr-0001-noyau-immutable-md"></a>

## Document : `decisions/ADR-0001-NOYAU-IMMUTABLE.md`

# ADR-0001 — Canon Framework et vues lexicales dérivées

- **Statut** : proposé pour diK 1.0 ; le principe canonique est déjà imposé par Framework v11 draft.3.
- **Contexte** : plusieurs sources de vocabulaire, Wikidata évolutif, 300 langues, migration d'anciens graphes nommés par mots.
- **Décision** : garder identités/graphe Framework comme source de vérité ; utiliser catalogues lexical/crosswalk comme métadonnées séparées, couches versionnées, projections dédupliquées et index recréables.
- **Motif** : conserve l'identité stable, la réversibilité, l'historique et limite les collisions futures avec Wikidata.
- **Conséquences** : complexité explicite de provenance/revue et besoin d'ancres ; aucun rendu Markdown seul ne peut être restauré.
- **Options rejetées** : Q Wikidata comme identifiant interne ; mots comme keys du graphe ; recherche de KQ depuis traduction ; SQLite comme canon.
- **Critères** : ID-R2, XW-T1, PRJ-T1/T3 et MIG-T1 dans le TCK.


---

<a id="doc-decisions-adr-0002-monolithe-modulaire-md"></a>

## Document : `decisions/ADR-0002-MONOLITHE-MODULAIRE.md`

# ADR-0002 — Monolithe modulaire + architecture hexagonale

- **Statut** : proposé (choix diK, non exigé par le Framework).
- **Contexte** : application locale polyvalente, reprise/import massif, absence d'exigence de distribution multi-services.
- **Décision** : domaines sans IO, use cases isolés, adaptateurs Wikidata/FS/SQLite/Authoring/UI ; CQRS local pour index dérivé ; import idempotent/snapshots immuables ; cache indexé par digests.
- **Options rejetées en 1.0** : microservices obligatoires, bus distribué, Event Sourcing global, architecture multi-cellules.
- **Conséquences** : déploiement simple et tests hors ligne ; modularité contrôlée par tests d'import ; évolution possible sans casser le modèle canonique.
- **Critères** : OPS-001..015, tests index rebuild/crash et audit de dépendances.


---

<a id="doc-decisions-adr-0003-profil-local-1-0-md"></a>

## Document : `decisions/ADR-0003-PROFIL-LOCAL-1_0.md`

# ADR-0003 — Profil local diK 1.0 (proposition normative du dossier)

**Statut : PROPOSED / candidate.2 ; ratification humaine requise avant gel final.**

## Contexte

Huit choix ouverts étaient laissés aux agents IA. Ils risquaient de produire des implémentations incompatibles, notamment un serveur imposé, un allocateur KQ incorporé à diK et un cache considéré comme canon.

## Profil proposé pour implémenter sans dérive

| Question | Comportement par défaut du profil local | Extension, jamais présumée |
|---|---|---|
| UI | UI web servie sur loopback avec session locale ou interface desktop ; **CLI obligatoire** même sans UI | serveur distant ou collaboration |
| Réseau | **hors ligne** et aucun appel automatique ; import depuis un miroir/fichier explicitement sélectionné | téléchargement HTTPS explicite/reprise |
| Acteurs | espace local mono-utilisateur avec journal des décisions | ACL multi-utilisateur et signatures |
| Authentification | aucune exposition hors loopback ; opérations locales limitées au propriétaire du workspace | jetons authentifiés, TLS, audit distant |
| Attribution KQ/KP | diK ne mint **jamais** ; le registre/producteur Framework reste seul autorisé | allocateur externe déclaré par interface |
| Migrations | plans proposés uniquement ; l'Authoring Kit/producteur applique après revalidation | aucun exécuteur implicite |
| Stockage | snapshots signalisés par SHA-256 et pointeur atomique ; SQLite dérivé | base distante synchronisée |
| Import Wikidata | miroir local versionné, snapshot explicite, extraction en flux | connecteur réseau activable séparément |
| Projections massives | profil compact diK v0.3 inchangé ; export séquentiel sans inventer nouveau wire format | profil shardé futur et versionné |
| Conservation | ne jamais supprimer automatiquement les artefacts engagés ni les décisions ; sauvegarde/restauration documentée | politique de purge validée par gouvernance |
| Signatures | SHA-256 pour intégrité, pas preuve d'auteur | signatures de publication si acteurs multiples |

## Impacts de compatibilité et sécurité

Pas de nouvelle identité canonique ni de modification des schémas Framework. Les endpoints réseau ne peuvent pas être exposés par défaut ; les droits d'import doivent être établis et le journal de décisions contrôlé. L'absence de signature doit être affichée comme limite en contexte multi-acteurs.

## Tests d'acceptation à implémenter

API bloquée hors loopback ; démarrage sans réseau ; diK refuse d'allouer un KQ ; crash prépublication et après publication ; reprise idempotente ; import de source inconnue mis en quarantaine ; restauration sans réécriture d'historique.


---

<a id="doc-contracts-readme-md"></a>

## Document : `contracts/README.md`

# Contrats diK 1.0 — proposés

Ces cinq schémas `draft 2020-12` sont **des DTOs/applicatifs candidats** : *decision*, *import job*, *patch intent*, *portfolio coverage* et *workspace manifest*. Ils ne sont ni les schémas du Framework v11, ni des données production vérifiées. Chaque fichier emploie `contract_profile` suffixé `/1.0-candidate`. Les exemples correspondants sont dans `examples/proposed/`.

Les identités et graphes canoniques restent régis exclusivement par les schémas Framework originaux. `dik-review-decision` ne constitue pas, à lui seul, une preuve qu'une validation humaine réelle a eu lieu : un moteur d'autorisation, une provenance KS vérifiée et la publication du crosswalk Framework restent nécessaires.

**Règle de livraison :** avant d'utiliser un DTO sur le wire, ratifier son schéma/sa version, tester ses transitions et ajouter un adaptateur pour le profil précédent. Un exemple `accepted` est purement illustratif et n'attribue aucune approbation réelle.


---

<a id="doc-examples-readme-md"></a>

## Document : `examples/README.md`

# Jeux d'exemples et limites

## Exemples officiels non altérés

`framework-v11-unaltered/` recopie uniquement certains fichiers de test fournis avec **Framework 11.0.0-draft.3** : graphe, registre, crosswalk, rapport de couverture et plan de migration. Ces fichiers prouvent le **contrat historique de la fixture**, pas la validité de tous les cas de production. Les exemples Wikidata identifient notamment Augustin d'Hippone `Q8018` ; les autres `KQ/KP` des fixtures ne sont pas des IDs de production.

## Exemples applicatifs candidats

`proposed/` contient cinq payloads construits pour les **schémas diK candidats**, avec SHA de démonstration (`aaaa…`, `bbbb…`, `cccc…`). **Ne pas utiliser leurs empreintes comme checksums de fichiers réels**, ni leurs décisions accepted comme une vraie revue. Les exemples démontrent seulement forme et contraintes du schéma.

## Trois scénarios contractuels incontournables

1. **Wikidata ajoute un nouveau Q** : ajouter `candidate` puis `accepted exact` seulement après revue et KS ; `KQ` préexistant inchangé ; projections historiques inchangées.
2. **Projection diK `clean`** : lecteur voit texte localisé ; export JSON garde le canon, `clean.md` seul n'est pas une source de restauration ; statut missing explicit.
3. **Ancien Kristal avec « grâce »** : identifier rôle JSON Pointer, proposer éventuellement plusieurs KQ distincts, garder citation/littéral inchangés, émettre plan non exécutable ; producteur autorisé génère nouvelle révision uniquement après approbation.

La validation de schéma positive et négative est effectuée par `tools/validate_documentation.py`, pas par un faux serveur diK 1.0.


---

<a id="doc-tests-readme-md"></a>

## Document : `tests/README.md`

# TCK diK 1.0 — catalogue de tests à exécuter

`TCK_CASES.json` décrit 30 cas de conformité initiaux, **tous `NOT_RUN` dans cette documentation**. Lorsqu'on code diK 1.0, créer de vrais tests automatisés et enregistrer leur exécution (`PASS`, `FAIL`, `NOT_RUN`) avec commandes, environnement et SHA du code. Aucun résultat du catalogue n'est une affirmation de test déjà réussi.

Pour valider le contenu de ce dossier (sans tester diK 1.0), exécuter :

```bash
python tools/validate_documentation.py
```

Le script vérifie les schémas applicatifs et fixtures, le lock des sources si celles-ci sont disponibles, les liens Markdown locaux et la cohérence du manifeste TCK. Les **36 tests unitaires de diK 0.3** ont été exécutés séparément sur le snapshot source : ils ne démontrent pas la conformité 1.0.

## Éléments candidate.2

- `requirements.json` : liste exhaustive des **87 identifiants réellement titrés** dans `docs/17_TRACABILITE.md`. Paires de tests encore `NOT_RUN`.
- `reference_vectors.json` : cas compacts, lisibles par machine, pour les principes hors-Framework de la cible.
- `../tools/verify_reference_vectors.py` : exécute les cas documentaires, **pas** la future application.


---

<a id="doc-github-pull-request-template-md"></a>

## Document : `.github/PULL_REQUEST_TEMPLATE.md`

## Contrat de changement

- Exigences (ID exact) :
- Documents/Framework consultés et SHA :
- Contrat d'API et sens des KQ/KP inchangés :
- Types de sources/dictionnaires concernés :
- Tests positifs :
- Tests négatifs (ambigüité, injection, corruption, reprise) :
- Compat v0.2 verbose + v0.3 compact + v11 :
- Entrées et sorties déterministes + hashes :
- Statut revue et approbation humaine (le cas échéant) :
- Tests exécutés PASS / FAIL / NOT_RUN :
- Écarts / ADR / risques :


---

# Annexes : contrats et jeux machine-lisibles


<a id="doc-contracts-dik-import-job-schema-json"></a>

### `contracts/dik-import-job.schema.json`

```json
{
  "$id": "https://example.invalid/dik/contracts/dik-import-job.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "allOf": [
    {
      "if": {
        "properties": {
          "status": {
            "const": "published"
          }
        },
        "required": [
          "status"
        ]
      },
      "then": {
        "required": [
          "output_catalog_sha256"
        ]
      }
    },
    {
      "if": {
        "properties": {
          "status": {
            "enum": [
              "failed",
              "cancelled"
            ]
          }
        },
        "required": [
          "status"
        ]
      },
      "then": {
        "required": [
          "error_code"
        ]
      }
    }
  ],
  "description": "Cible de diK 1.0, contrat candidat à ratifier; ne remplace aucun schéma Framework.",
  "properties": {
    "checkpoint": {
      "additionalProperties": false,
      "properties": {
        "last_completed_shard": {
          "type": [
            "string",
            "null"
          ]
        },
        "processed_records": {
          "minimum": 0,
          "type": "integer"
        },
        "staged_files": {
          "items": {
            "minLength": 1,
            "type": "string"
          },
          "type": "array"
        }
      },
      "required": [
        "processed_records",
        "last_completed_shard",
        "staged_files"
      ],
      "type": "object"
    },
    "contract_profile": {
      "const": "dik.import-job/1.0-candidate"
    },
    "crosswalk_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "error_code": {
      "minLength": 1,
      "type": "string"
    },
    "idempotency_key": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "job_id": {
      "minLength": 1,
      "type": "string"
    },
    "namespace_id": {
      "minLength": 1,
      "type": "string"
    },
    "output_catalog_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "requested_locales": {
      "items": {
        "minLength": 1,
        "type": "string"
      },
      "minItems": 1,
      "type": "array",
      "uniqueItems": true
    },
    "source_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "source_snapshot": {
      "minLength": 1,
      "type": "string"
    },
    "source_system": {
      "minLength": 1,
      "type": "string"
    },
    "status": {
      "enum": [
        "planned",
        "downloading",
        "parsing",
        "staging",
        "validating",
        "ready",
        "published",
        "failed",
        "cancelled"
      ]
    },
    "transform_version": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required": [
    "contract_profile",
    "job_id",
    "status",
    "source_system",
    "source_snapshot",
    "source_sha256",
    "namespace_id",
    "crosswalk_sha256",
    "requested_locales",
    "transform_version",
    "idempotency_key",
    "checkpoint"
  ],
  "title": "dik-import-job — DIK PROPOSED, NOT FRAMEWORK",
  "type": "object"
}
```


<a id="doc-contracts-dik-portfolio-coverage-schema-json"></a>

### `contracts/dik-portfolio-coverage.schema.json`

```json
{
  "$id": "https://example.invalid/dik/contracts/dik-portfolio-coverage.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "description": "Cible de diK 1.0, contrat candidat à ratifier; ne remplace aucun schéma Framework.",
  "properties": {
    "catalog_id": {
      "minLength": 1,
      "type": "string"
    },
    "catalog_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "contract_profile": {
      "const": "dik.portfolio-coverage/1.0-candidate"
    },
    "graph_reports": {
      "items": {
        "additionalProperties": false,
        "properties": {
          "framework_report_sha256": {
            "pattern": "^[0-9a-f]{64}$",
            "type": "string"
          },
          "graph_id": {
            "minLength": 1,
            "type": "string"
          },
          "graph_sha256": {
            "pattern": "^[0-9a-f]{64}$",
            "type": "string"
          },
          "namespace_id": {
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "namespace_id",
          "graph_id",
          "graph_sha256",
          "framework_report_sha256"
        ],
        "type": "object"
      },
      "minItems": 1,
      "type": "array"
    },
    "legacy_unresolved_graph_ids": {
      "items": {
        "minLength": 1,
        "type": "string"
      },
      "type": "array",
      "uniqueItems": true
    },
    "notes": {
      "minLength": 1,
      "type": "string"
    },
    "report_id": {
      "minLength": 1,
      "type": "string"
    },
    "requested_locales": {
      "items": {
        "minLength": 1,
        "type": "string"
      },
      "minItems": 1,
      "type": "array",
      "uniqueItems": true
    }
  },
  "required": [
    "contract_profile",
    "report_id",
    "catalog_id",
    "catalog_sha256",
    "graph_reports",
    "requested_locales",
    "legacy_unresolved_graph_ids"
  ],
  "title": "dik-portfolio-coverage — DIK PROPOSED, NOT FRAMEWORK",
  "type": "object"
}
```


<a id="doc-contracts-dik-review-decision-schema-json"></a>

### `contracts/dik-review-decision.schema.json`

```json
{
  "$id": "https://example.invalid/dik/contracts/dik-review-decision.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "allOf": [
    {
      "if": {
        "properties": {
          "status": {
            "const": "accepted"
          }
        },
        "required": [
          "status"
        ]
      },
      "then": {
        "properties": {
          "evidence_refs": {
            "minItems": 1
          }
        },
        "required": [
          "reviewer_id",
          "decision_method",
          "evidence_refs"
        ]
      }
    },
    {
      "if": {
        "properties": {
          "status": {
            "const": "superseded"
          }
        },
        "required": [
          "status"
        ]
      },
      "then": {
        "required": [
          "supersedes"
        ]
      }
    }
  ],
  "description": "Cible de diK 1.0, contrat candidat à ratifier; ne remplace aucun schéma Framework.",
  "properties": {
    "actor_id": {
      "minLength": 1,
      "type": "string"
    },
    "candidate": {
      "additionalProperties": false,
      "properties": {
        "locale": {
          "minLength": 1,
          "type": "string"
        },
        "source_record_id": {
          "minLength": 1,
          "type": "string"
        },
        "source_snapshot": {
          "minLength": 1,
          "type": "string"
        },
        "source_system": {
          "minLength": 1,
          "type": "string"
        },
        "term": {
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "source_system",
        "source_snapshot",
        "source_record_id"
      ],
      "type": "object"
    },
    "contract_profile": {
      "const": "dik.review-decision/1.0-candidate"
    },
    "decision_id": {
      "minLength": 1,
      "type": "string"
    },
    "decision_method": {
      "minLength": 1,
      "type": "string"
    },
    "evidence_refs": {
      "items": {
        "pattern": "^KS[1-9][0-9]*$",
        "type": "string"
      },
      "type": "array",
      "uniqueItems": true
    },
    "input_manifest_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "mapping_kind": {
      "enum": [
        "lexical_preference",
        "external_alignment"
      ]
    },
    "reason": {
      "minLength": 1,
      "type": "string"
    },
    "relation": {
      "enum": [
        "exactMatch",
        "closeMatch",
        "broadMatch",
        "narrowMatch",
        "relatedMatch",
        "not_applicable"
      ]
    },
    "reviewer_id": {
      "minLength": 1,
      "type": "string"
    },
    "revision": {
      "minimum": 1,
      "type": "integer"
    },
    "status": {
      "enum": [
        "proposed",
        "in_review",
        "accepted",
        "rejected",
        "superseded"
      ]
    },
    "supersedes": {
      "minLength": 1,
      "type": "string"
    },
    "target": {
      "additionalProperties": false,
      "properties": {
        "id": {
          "pattern": "^K[QP][1-9][0-9]*$",
          "type": "string"
        },
        "kind": {
          "enum": [
            "KQ",
            "KP"
          ]
        },
        "namespace_id": {
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "namespace_id",
        "id",
        "kind"
      ],
      "type": "object"
    }
  },
  "required": [
    "contract_profile",
    "decision_id",
    "mapping_kind",
    "target",
    "status",
    "relation",
    "candidate",
    "reason",
    "revision",
    "actor_id",
    "input_manifest_sha256"
  ],
  "title": "dik-review-decision — DIK PROPOSED, NOT FRAMEWORK",
  "type": "object"
}
```


<a id="doc-contracts-dik-semantic-patch-intent-schema-json"></a>

### `contracts/dik-semantic-patch-intent.schema.json`

```json
{
  "$id": "https://example.invalid/dik/contracts/dik-semantic-patch-intent.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "allOf": [
    {
      "if": {
        "properties": {
          "review_status": {
            "const": "approved"
          }
        },
        "required": [
          "review_status"
        ]
      },
      "then": {
        "required": [
          "reviewer_id",
          "evidence_refs"
        ]
      }
    }
  ],
  "description": "Cible de diK 1.0, contrat candidat à ratifier; ne remplace aucun schéma Framework.",
  "properties": {
    "change_kind": {
      "enum": [
        "lexical_only",
        "semantic_identity",
        "semantic_relation",
        "literal_value"
      ]
    },
    "contract_profile": {
      "const": "dik.semantic-patch-intent/1.0-candidate"
    },
    "evidence_refs": {
      "items": {
        "pattern": "^KS[1-9][0-9]*$",
        "type": "string"
      },
      "type": "array",
      "uniqueItems": true
    },
    "namespace_id": {
      "minLength": 1,
      "type": "string"
    },
    "new_catalog_revision": {
      "minLength": 1,
      "type": "string"
    },
    "original": {},
    "patch_id": {
      "minLength": 1,
      "type": "string"
    },
    "proposed": {},
    "reason": {
      "minLength": 1,
      "type": "string"
    },
    "review_status": {
      "enum": [
        "pending",
        "approved",
        "rejected"
      ]
    },
    "reviewer_id": {
      "minLength": 1,
      "type": "string"
    },
    "source_graph_id": {
      "minLength": 1,
      "type": "string"
    },
    "source_graph_sha256": {
      "pattern": "^[0-9a-f]{64}$",
      "type": "string"
    },
    "source_path": {
      "pattern": "^/",
      "type": "string"
    }
  },
  "required": [
    "contract_profile",
    "patch_id",
    "source_graph_id",
    "namespace_id",
    "source_graph_sha256",
    "source_path",
    "change_kind",
    "original",
    "proposed",
    "review_status",
    "reason"
  ],
  "title": "dik-semantic-patch-intent — DIK PROPOSED, NOT FRAMEWORK",
  "type": "object"
}
```


<a id="doc-contracts-dik-workspace-manifest-schema-json"></a>

### `contracts/dik-workspace-manifest.schema.json`

```json
{
  "$id": "https://example.invalid/dik/contracts/dik-workspace-manifest.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "description": "Cible de diK 1.0, contrat candidat à ratifier; ne remplace aucun schéma Framework.",
  "properties": {
    "active_catalog": {
      "additionalProperties": false,
      "properties": {
        "relative_path": {
          "minLength": 1,
          "type": "string"
        },
        "sha256": {
          "pattern": "^[0-9a-f]{64}$",
          "type": "string"
        }
      },
      "required": [
        "relative_path",
        "sha256"
      ],
      "type": "object"
    },
    "active_crosswalk": {
      "additionalProperties": false,
      "properties": {
        "relative_path": {
          "minLength": 1,
          "type": "string"
        },
        "sha256": {
          "pattern": "^[0-9a-f]{64}$",
          "type": "string"
        }
      },
      "required": [
        "relative_path",
        "sha256"
      ],
      "type": "object"
    },
    "active_registry": {
      "additionalProperties": false,
      "properties": {
        "relative_path": {
          "minLength": 1,
          "type": "string"
        },
        "sha256": {
          "pattern": "^[0-9a-f]{64}$",
          "type": "string"
        }
      },
      "required": [
        "relative_path",
        "sha256"
      ],
      "type": "object"
    },
    "contract_profile": {
      "const": "dik.workspace/1.0-candidate"
    },
    "framework_version": {
      "const": "11.0.0-draft.3"
    },
    "projects": {
      "items": {
        "additionalProperties": false,
        "properties": {
          "project_id": {
            "minLength": 1,
            "type": "string"
          },
          "relative_path": {
            "minLength": 1,
            "type": "string"
          },
          "sha256": {
            "pattern": "^[0-9a-f]{64}$",
            "type": "string"
          }
        },
        "required": [
          "project_id",
          "relative_path",
          "sha256"
        ],
        "type": "object"
      },
      "type": "array"
    },
    "workspace_id": {
      "minLength": 1,
      "type": "string"
    }
  },
  "required": [
    "contract_profile",
    "workspace_id",
    "framework_version",
    "active_registry",
    "active_catalog",
    "active_crosswalk",
    "projects"
  ],
  "title": "dik-workspace-manifest — DIK PROPOSED, NOT FRAMEWORK",
  "type": "object"
}
```


<a id="doc-examples-proposed-dik-import-job-example-json"></a>

### `examples/proposed/dik-import-job.example.json`

```json
{
  "checkpoint": {
    "last_completed_shard": null,
    "processed_records": 0,
    "staged_files": []
  },
  "contract_profile": "dik.import-job/1.0-candidate",
  "crosswalk_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "idempotency_key": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "job_id": "demo-import",
  "namespace_id": "example.org/kristal-demo",
  "requested_locales": [
    "fr",
    "en",
    "fr-CA"
  ],
  "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_snapshot": "demo-snapshot",
  "source_system": "wikidata",
  "status": "planned",
  "transform_version": "prototype-1"
}
```


<a id="doc-examples-proposed-dik-portfolio-coverage-example-json"></a>

### `examples/proposed/dik-portfolio-coverage.example.json`

```json
{
  "catalog_id": "wikidata-import-demo-snapshot",
  "catalog_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "contract_profile": "dik.portfolio-coverage/1.0-candidate",
  "graph_reports": [
    {
      "framework_report_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "graph_id": "demo-graph",
      "graph_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "namespace_id": "example.org/kristal-demo"
    }
  ],
  "legacy_unresolved_graph_ids": [],
  "report_id": "demo-portfolio",
  "requested_locales": [
    "fr",
    "en",
    "fr-CA"
  ]
}
```


<a id="doc-examples-proposed-dik-review-decision-example-json"></a>

### `examples/proposed/dik-review-decision.example.json`

```json
{
  "actor_id": "demo-author",
  "candidate": {
    "locale": "fr",
    "source_record_id": "Q8018",
    "source_snapshot": "demo-snapshot",
    "source_system": "wikidata",
    "term": "Augustin d’Hippone"
  },
  "contract_profile": "dik.review-decision/1.0-candidate",
  "decision_id": "demo-rev-1",
  "decision_method": "human",
  "evidence_refs": [
    "KS4001"
  ],
  "input_manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "mapping_kind": "external_alignment",
  "reason": "Correspondance vérifiée à titre d’exemple, sans approbation réelle de production.",
  "relation": "exactMatch",
  "reviewer_id": "demo-reviewer",
  "revision": 1,
  "status": "accepted",
  "target": {
    "id": "KQ1001",
    "kind": "KQ",
    "namespace_id": "example.org/kristal-demo"
  }
}
```


<a id="doc-examples-proposed-dik-semantic-patch-intent-example-json"></a>

### `examples/proposed/dik-semantic-patch-intent.example.json`

```json
{
  "change_kind": "semantic_relation",
  "contract_profile": "dik.semantic-patch-intent/1.0-candidate",
  "namespace_id": "example.org/kristal-demo",
  "original": "KP2001",
  "patch_id": "demo-patch-1",
  "proposed": "KP2002",
  "reason": "Proposition à revoir, jamais automatiquement appliquée.",
  "review_status": "pending",
  "source_graph_id": "demo-graph",
  "source_graph_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_path": "/assertions/0/predicate"
}
```


<a id="doc-examples-proposed-dik-workspace-manifest-example-json"></a>

### `examples/proposed/dik-workspace-manifest.example.json`

```json
{
  "active_catalog": {
    "relative_path": "dictionaries/catalog.json",
    "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "active_crosswalk": {
    "relative_path": "external-crosswalk.example.json",
    "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
  },
  "active_registry": {
    "relative_path": "identity-registry.example.json",
    "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "contract_profile": "dik.workspace/1.0-candidate",
  "framework_version": "11.0.0-draft.3",
  "projects": [
    {
      "project_id": "demo",
      "relative_path": "dik.project.json",
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ],
  "workspace_id": "demo-workspace"
}
```


<a id="doc-tests-requirements-json"></a>

### `tests/requirements.json`

```json
{
  "suite_id": "DIK-1.0-REQUIREMENTS-CANDIDATE.2",
  "status": "REQUIREMENTS_PLANNED_NOT_EXECUTED",
  "framework_pin": "11.0.0-draft.3",
  "requirement_count": 87,
  "requirements": [
    {
      "requirement_id": "API-001",
      "title": "CLI sans surprise",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-001 — CLI sans surprise",
      "normative_summary": "Commandes diK 0.3 à préserver : project inspect, dictionaries audit|resolve, coverage report, wikidata import-local, projection export|verify|restore. Compatibilité des options existantes, et --format verbose maintenu.",
      "positive_test": {
        "id": "API-001-POS",
        "scenario": "Comportement conforme : CLI sans surprise (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-001-NEG",
        "scenario": "Refus ou signalement de violation : CLI sans surprise (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "API-002",
      "title": "Interface programme",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-002 — Interface programme",
      "normative_summary": "Éviter les réponses polymorphes non typées. Résultat uniforme : request_id, contract_version, status, data, errors[], input_manifest_digest, output_manifest_digest?, warnings[]. status=success uniquement si publication complète. status=proposed n'est pas approved, ni published.",
      "positive_test": {
        "id": "API-002-POS",
        "scenario": "Comportement conforme : Interface programme (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-002-NEG",
        "scenario": "Refus ou signalement de violation : Interface programme (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "API-003",
      "title": "Idempotence et conflits",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-003 — Idempotence et conflits",
      "normative_summary": "Toute commande mutante accepte un idempotency_key ou en dérive une par opération ; même clé / mêmes paramètres => même résultat ; même clé / paramètres différents => IDEMPOTENCY_CONFLICT. Édition revue conditionnée à expected_revision/hash ; si changement simultané => REVISION_CONFLICT. Les opérations de lecture n'altèrent pas les manifestes.",
      "positive_test": {
        "id": "API-003-POS",
        "scenario": "Comportement conforme : Idempotence et conflits (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-003-NEG",
        "scenario": "Refus ou signalement de violation : Idempotence et conflits (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "API-004",
      "title": "Filtres et pagination",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-004 — Filtres et pagination",
      "normative_summary": "Recherches et matrice de couverture : pagination déterministe, curseur lié au snapshot, tri défini. Une API ne retourne pas silencieusement « tous les concepts de Wikidata » en RAM. Exports massifs en fichiers versionnés + manifestes/hashes.",
      "positive_test": {
        "id": "API-004-POS",
        "scenario": "Comportement conforme : Filtres et pagination (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-004-NEG",
        "scenario": "Refus ou signalement de violation : Filtres et pagination (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "API-005",
      "title": "Codes de sortie CLI",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-005 — Codes de sortie CLI",
      "normative_summary": "Proposition : 0 success, 2 invalid_input, 3 conflict_or_ambiguous, 4 integrity_or_security_failure, 5 external_source_unavailable, 6 approval_required, 7 contract_mismatch, 8 partial_or_interrupted_job, 9 internal_error. Un code partiel ne doit pas se faire passer pour succès ; les exceptions doivent fournir error_code stable sans exposer secret/chemins sensibles.",
      "positive_test": {
        "id": "API-005-POS",
        "scenario": "Comportement conforme : Codes de sortie CLI (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-005-NEG",
        "scenario": "Refus ou signalement de violation : Codes de sortie CLI (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "API-006",
      "title": "Local d'abord",
      "source_document": "11_API_CLI.md",
      "source_heading": "## API-006 — Local d'abord",
      "normative_summary": "API bind 127.0.0.1 par défaut et authentification robuste si mode multiutilisateur; pas d'exposition réseau implicite. Pas de téléchargement réseau lors de la simple ouverture d'un projet. Formats JSON/JSONL strictement documentés et versions explicites.",
      "positive_test": {
        "id": "API-006-POS",
        "scenario": "Comportement conforme : Local d'abord (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "API-006-NEG",
        "scenario": "Refus ou signalement de violation : Local d'abord (voir 11_API_CLI.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-001",
      "title": "Dénominateur",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-001 — Dénominateur",
      "normative_summary": "Inventorier les KQ distincts utilisés comme entités et les KP distincts utilisés comme propriétés, y compris qualificatifs, pour le graphe v11 visé. KA/KS sont contrôlés pour intégrité, pas additionnés arbitrairement au nombre de concepts traduisibles. Le rapport provient d'un graphe et d'un catalogue versionnés, pas du nombre de Q Wikidata ni du nombre de fichiers de langue.",
      "positive_test": {
        "id": "COV-001-POS",
        "scenario": "Comportement conforme : Dénominateur (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-001-NEG",
        "scenario": "Refus ou signalement de violation : Dénominateur (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-002",
      "title": "Statuts exclusifs",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-002 — Statuts exclusifs",
      "normative_summary": "Par identifiant+locale : direct si terme approuvé dans locale demandée ; fallback seulement si chaîne déclarée ; missing si aucun terme ; conflicted si concurrence non résolue. Rapport par famille KQ / KP, par locale, et intersection de toutes les locales sélectionnées. complete_direct ne compte ni fallback ni missing/conflict. complete_usable tolère fallback, pas missing/conflict. crosswalk cover",
      "positive_test": {
        "id": "COV-002-POS",
        "scenario": "Comportement conforme : Statuts exclusifs (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-002-NEG",
        "scenario": "Refus ou signalement de violation : Statuts exclusifs (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-003",
      "title": "Reporting multi-Kristals",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-003 — Reporting multi-Kristals",
      "normative_summary": "Sélection par manifestes explicites ; construire une matrice (graph_id, namespace, locale, family) et les unions/intersections de référents par namespaces. Pour une organisation, ne pas dédupliquer deux KQ1001 de namespaces différents. Toute ligne conserve version, empreinte, compteur, date logique, nombre de conflits, exemples manquants et statut de troncature.",
      "positive_test": {
        "id": "COV-003-POS",
        "scenario": "Comportement conforme : Reporting multi-Kristals (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-003-NEG",
        "scenario": "Refus ou signalement de violation : Reporting multi-Kristals (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-004",
      "title": "Qualité != présence",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-004 — Qualité != présence",
      "normative_summary": "Complétude nominale = présence validée du terme. Qualité de traduction = révision, domaine, profondeur lexicale, source, date, éventuel contrôle linguistique ; métrique distincte. Un terme généré automatiquement en attente de revue peut exister comme proposal mais ne compte pas comme traduction directe vérifiée.",
      "positive_test": {
        "id": "COV-004-POS",
        "scenario": "Comportement conforme : Qualité != présence (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-004-NEG",
        "scenario": "Refus ou signalement de violation : Qualité != présence (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-005",
      "title": "Historique et delta",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-005 — Historique et delta",
      "normative_summary": "Comparer rapports A/B avec mêmes graphes ou changements d'inventaire identifiés : nouveau concept, traduction ajoutée/supprimée, variante en conflit, fallback devenu direct. Conserver le dénominateur pour chaque état historique ; ne jamais attribuer la variation entière à « traduction » si les KQ du graphe ont changé.",
      "positive_test": {
        "id": "COV-005-POS",
        "scenario": "Comportement conforme : Historique et delta (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-005-NEG",
        "scenario": "Refus ou signalement de violation : Historique et delta (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "COV-006",
      "title": "300+ langues",
      "source_document": "08_COMPLETUDE.md",
      "source_heading": "## COV-006 — 300+ langues",
      "normative_summary": "Le rapport peut porter 301 langues sparse et plusieurs graphes ; afficher par défaut vue agrégée et pagination/drilldown. Ne pas prétendre à 100 % si un seul KQ/KP manque ou est conflictuel. Une entrée legacy non résolue interdit un taux fiable de 100 % pour l'ensemble ; le rapport doit signaler legacy_denominator_unknown.",
      "positive_test": {
        "id": "COV-006-POS",
        "scenario": "Comportement conforme : 300+ langues (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "COV-006-NEG",
        "scenario": "Refus ou signalement de violation : 300+ langues (voir 08_COMPLETUDE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "ID-001",
      "title": "Clé canonique",
      "source_document": "02_IDENTITES.md",
      "source_heading": "## ID-001 — Clé canonique",
      "normative_summary": "La seule clé référentielle d'un KQ/KP est (namespace_id, id). KQ1001 dans alpha et KQ1001 dans beta ne sont pas interchangeables. Toutes les API/domain objects portent le namespace ; l'affichage abrégé de KQ1001 n'autorise pas sa résolution hors contexte.",
      "positive_test": {
        "id": "ID-001-POS",
        "scenario": "Comportement conforme : Clé canonique (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "ID-001-NEG",
        "scenario": "Refus ou signalement de violation : Clé canonique (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "ID-002",
      "title": "Types stricts",
      "source_document": "02_IDENTITES.md",
      "source_heading": "## ID-002 — Types stricts",
      "normative_summary": "KQ… = entity; KP… = property; KA… = assertion; KS… = source. Le parser rejette Q8018, P31, wikidata:Q8018, has_property, urn:legacy:… dans un rôle d'ID canonique. Il peut les reconnaître dans des champs externes typés, des demandes de migration ou une valeur littérale.",
      "positive_test": {
        "id": "ID-002-POS",
        "scenario": "Comportement conforme : Types stricts (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "ID-002-NEG",
        "scenario": "Refus ou signalement de violation : Types stricts (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "ID-003",
      "title": "Allocation",
      "source_document": "02_IDENTITES.md",
      "source_heading": "## ID-003 — Allocation",
      "normative_summary": "- Allocation durable et non réutilisable au sein du namespace, y compris après suppression logique.",
      "positive_test": {
        "id": "ID-003-POS",
        "scenario": "Comportement conforme : Allocation (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "ID-003-NEG",
        "scenario": "Refus ou signalement de violation : Allocation (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "ID-004",
      "title": "Statuts, fusion, scission",
      "source_document": "02_IDENTITES.md",
      "source_heading": "## ID-004 — Statuts, fusion, scission",
      "normative_summary": "Une erreur d'identité se corrige par des déclarations de remplacement/supersession versionnées et une décision auditée, pas en remplaçant la clé de l'histoire. Les fusions/splits Wikidata ne fusionnent pas les KQ de Kristal. La dépendance à Wikidata est la table de correspondance, jamais l'ID maître.",
      "positive_test": {
        "id": "ID-004-POS",
        "scenario": "Comportement conforme : Statuts, fusion, scission (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "ID-004-NEG",
        "scenario": "Refus ou signalement de violation : Statuts, fusion, scission (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "ID-005",
      "title": "Contrôles systématiques",
      "source_document": "02_IDENTITES.md",
      "source_heading": "## ID-005 — Contrôles systématiques",
      "normative_summary": "- Champs entities, properties, assertions et sources v11 validés contre le schéma officiel et le registre.",
      "positive_test": {
        "id": "ID-005-POS",
        "scenario": "Comportement conforme : Contrôles systématiques (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "ID-005-NEG",
        "scenario": "Refus ou signalement de violation : Contrôles systématiques (voir 02_IDENTITES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "IMP-001",
      "title": "Source externe et miroir",
      "source_document": "05_WIKIDATA.md",
      "source_heading": "## IMP-001 — Source externe et miroir",
      "normative_summary": "Le dump Wikidata est une entrée non fiable et non une autorité locale de KQ. Son format Q/P, ses alias, ses révisions, ses descriptions, redirections sont adaptés dans une couche anti-corruption. Le miroir local de l'utilisateur est supporté sans accès Internet. Un téléchargement depuis une source officielle est une opération explicite distincte du rendu/lookup.",
      "positive_test": {
        "id": "IMP-001-POS",
        "scenario": "Comportement conforme : Source externe et miroir (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "IMP-001-NEG",
        "scenario": "Refus ou signalement de violation : Source externe et miroir (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "IMP-002",
      "title": "Pipeline robuste",
      "source_document": "05_WIKIDATA.md",
      "source_heading": "## IMP-002 — Pipeline robuste",
      "normative_summary": "1. L'opérateur fournit URL ou chemin local, mode (full/delta si source fiable disponible), révision/date, langues ciblées, limites de ressources et destination. 2. Vérifier signature/checksum de l'amont si disponible ; toujours calculer empreinte locale ; ne jamais décompresser sans quotas ni écrire à une destination arbitraire contrôlée par le dump. 3. Parser en flux, supporter .json, .jsonl, .gz",
      "positive_test": {
        "id": "IMP-002-POS",
        "scenario": "Comportement conforme : Pipeline robuste (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "IMP-002-NEG",
        "scenario": "Refus ou signalement de violation : Pipeline robuste (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "IMP-003",
      "title": "Reprise/idempotence",
      "source_document": "05_WIKIDATA.md",
      "source_heading": "## IMP-003 — Reprise/idempotence",
      "normative_summary": "Clé de tâche = hash canonique (source snapshot, namespace, crosswalk revision, selected locales, transform version, settings). Même clé/mêmes octets -> résultat identique sans duplication ; même clé/octets différents -> conflit bloquant. Checkpoints portent compteur d'objets, shard terminé, empreintes ; reprise uniquement si source identique, transformation identique et point de reprise validé. Co",
      "positive_test": {
        "id": "IMP-003-POS",
        "scenario": "Comportement conforme : Reprise/idempotence (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "IMP-003-NEG",
        "scenario": "Refus ou signalement de violation : Reprise/idempotence (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "IMP-004",
      "title": "Téléchargements",
      "source_document": "05_WIKIDATA.md",
      "source_heading": "## IMP-004 — Téléchargements",
      "normative_summary": "HTTP(S) seulement si activé ; délais et budget total, retry avec backoff+jitter seulement sur erreurs transitoires, limite de débit, stockage temporaire de téléchargement, métadonnées ETag/Last-Modified si la source les fournit, checksum post-téléchargement, publication après validation. Aucun appel réseau dans projection restore, coverage, lookup ni au démarrage de diK.",
      "positive_test": {
        "id": "IMP-004-POS",
        "scenario": "Comportement conforme : Téléchargements (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "IMP-004-NEG",
        "scenario": "Refus ou signalement de violation : Téléchargements (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "IMP-005",
      "title": "Wikibase lexèmes",
      "source_document": "05_WIKIDATA.md",
      "source_heading": "## IMP-005 — Wikibase lexèmes",
      "normative_summary": "Les lexèmes Wikidata L… (formes/sens) sont différents des items Q… et propriétés P…. L'import 1.0 des labels Q/P ne les traite pas comme des KQ. Un connecteur L séparé demanderait des contrats explicitement typés et des tests distincts.",
      "positive_test": {
        "id": "IMP-005-POS",
        "scenario": "Comportement conforme : Wikibase lexèmes (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "IMP-005-NEG",
        "scenario": "Refus ou signalement de violation : Wikibase lexèmes (voir 05_WIKIDATA.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-001",
      "title": "Deux catégories qui ne fusionnent jamais",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-001 — Deux catégories qui ne fusionnent jamais",
      "normative_summary": "Lexical : (namespace, KQ/KP, locale[, domaine]) → label, alias, définition descriptive, provenance, statut et priorité. Crosswalk : (namespace, KQ/KP) ↔ (source externe, Q/P ou autre), relation, statut, preuve, revue. Le libellé externe ne devient utilisable que via l'alignement approprié et la couche lexicalement admise. Un mot commun n'est pas une clé de jointure sémantique fiable.",
      "positive_test": {
        "id": "LEX-001-POS",
        "scenario": "Comportement conforme : Deux catégories qui ne fusionnent jamais (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-001-NEG",
        "scenario": "Refus ou signalement de violation : Deux catégories qui ne fusionnent jamais (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-002",
      "title": "Catalogue et fichiers",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-002 — Catalogue et fichiers",
      "normative_summary": "- Catalogue unique sélectionne les langues, fallbacks, couches ordonnées, chemins relatifs, SHA-256 et versions. Ne jamais déduire la priorité d'un nom de fichier ou d'un ordre d'itération du dossier.",
      "positive_test": {
        "id": "LEX-002-POS",
        "scenario": "Comportement conforme : Catalogue et fichiers (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-002-NEG",
        "scenario": "Refus ou signalement de violation : Catalogue et fichiers (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-003",
      "title": "Sélection et déterminisme",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-003 — Sélection et déterminisme",
      "normative_summary": "Pour (namespace, semantic_id, locale, domaine) : valider ID + langue ; consulter couches déclarées ; ordonner par priorité du catalogue ; en cas de tie incompatible -> erreur ; sinon rendre {label,status,effective_locale,layer_id,provenance}. Fallback uniquement si déclaré et sans cycle. Si aucun libellé : {label:null,status:\"missing\"} et ID conservé. Pas de traduction de secours silencieuse par I",
      "positive_test": {
        "id": "LEX-003-POS",
        "scenario": "Comportement conforme : Sélection et déterminisme (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-003-NEG",
        "scenario": "Refus ou signalement de violation : Sélection et déterminisme (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-004",
      "title": "Versions et corrections",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-004 — Versions et corrections",
      "normative_summary": "Une correction crée un nouvel objet curaté/reviewed, journalise auteur, décision, justification, avant/après, KS le cas échéant, source et date. Les anciens snapshots restent accessibles pour reproduire une projection historique. Une mise à jour Wikidata ne supprime ni n'édite une couche curatée. Dictionnaire externe absent de licence ou d'alignement validé : untrusted, exclu du canal vérifié.",
      "positive_test": {
        "id": "LEX-004-POS",
        "scenario": "Comportement conforme : Versions et corrections (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-004-NEG",
        "scenario": "Refus ou signalement de violation : Versions et corrections (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-005",
      "title": "Sparsité et domaines",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-005 — Sparsité et domaines",
      "normative_summary": "- 300+ langues supportées comme données clairsemées ; pas de matrice dense KQ×300 à créer à l'import.",
      "positive_test": {
        "id": "LEX-005-POS",
        "scenario": "Comportement conforme : Sparsité et domaines (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-005-NEG",
        "scenario": "Refus ou signalement de violation : Sparsité et domaines (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-006",
      "title": "Publication",
      "source_document": "03_DICTIONNAIRES.md",
      "source_heading": "## LEX-006 — Publication",
      "normative_summary": "Staging privé -> validation JSON Schema + hash + licences + collision + fallback -> écriture de tous shards -> publication atomique du pointeur de catalogue -> audit postpublication. Réexécuter avec la même clé idempotente retourne le snapshot existant, jamais un nouveau contenu conflictuel sous le même ID.",
      "positive_test": {
        "id": "LEX-006-POS",
        "scenario": "Comportement conforme : Publication (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-006-NEG",
        "scenario": "Refus ou signalement de violation : Publication (voir 03_DICTIONNAIRES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-020",
      "title": "Normalisation",
      "source_document": "19_LOCALES.md",
      "source_heading": "## LEX-020 — Normalisation",
      "normative_summary": "Utiliser une bibliothèque/registre BCP 47 approprié, versionné et documenté : validité de la langue, canonicalisation (alias/variante/script/région) et tag source conservé à des fins d'audit. Une simple regex fr-CA ne prouve pas une langue valide. Choisir une seule politique d'égalité de tags et la tester sur fr, fr-CA, zh-Hans, zh-Hant, sr-Latn, ar et tags inattendus.",
      "positive_test": {
        "id": "LEX-020-POS",
        "scenario": "Comportement conforme : Normalisation (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-020-NEG",
        "scenario": "Refus ou signalement de violation : Normalisation (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-021",
      "title": "Fallback",
      "source_document": "19_LOCALES.md",
      "source_heading": "## LEX-021 — Fallback",
      "normative_summary": "Chaque repli est un arc déclaré dans le catalogue. fr-CA -> fr n'autorise pas fr -> en sans déclaration ; interdire cycles et ambiguïtés de priorité. Un libellé en langue de repli ne compte pas comme direct. Ne pas supposer que zh-Hant et zh-Hans sont interchangeables, ni qu'une translittération constitue une traduction.",
      "positive_test": {
        "id": "LEX-021-POS",
        "scenario": "Comportement conforme : Fallback (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-021-NEG",
        "scenario": "Refus ou signalement de violation : Fallback (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-022",
      "title": "Unicode et rendu",
      "source_document": "19_LOCALES.md",
      "source_heading": "## LEX-022 — Unicode et rendu",
      "normative_summary": "Conserver Unicode d'origine, normaliser pour comparaison par NFC si nécessaire, mais ne pas perdre les distinctions significatives ; sécuriser rendus HTML/Markdown ; RTL et scripts combinants testés ; normalisation ne sert jamais à fusionner des concepts. Les formes fléchies, sens lexicographiques et lemmes Wikidata L sont hors import Q/P par défaut.",
      "positive_test": {
        "id": "LEX-022-POS",
        "scenario": "Comportement conforme : Unicode et rendu (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-022-NEG",
        "scenario": "Refus ou signalement de violation : Unicode et rendu (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-023",
      "title": "300+ langues",
      "source_document": "19_LOCALES.md",
      "source_heading": "## LEX-023 — 300+ langues",
      "normative_summary": "Les langues sont déclarées même avec zéro entrée ; couverture sparse évaluée avec missing. Le catalogue doit permettre shards compressés et nombreux locales sans charger l'ensemble pour résoudre une locale. TCK inclut 301 langues déclarées et plusieurs scripts, avec fallback vérifié.",
      "positive_test": {
        "id": "LEX-023-POS",
        "scenario": "Comportement conforme : 300+ langues (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-023-NEG",
        "scenario": "Refus ou signalement de violation : 300+ langues (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "LEX-024",
      "title": "Préférence contextuelle",
      "source_document": "19_LOCALES.md",
      "source_heading": "## LEX-024 — Préférence contextuelle",
      "normative_summary": "Terme de spécialité (théologie, physique) peut l'emporter sur le dictionnaire général par profil de domaine/version, jamais sur la seule orthographe ; termes homographes distincts peuvent référer à plusieurs KQ. Une interface affiche la provenance et la langue effective du terme rendu.",
      "positive_test": {
        "id": "LEX-024-POS",
        "scenario": "Comportement conforme : Préférence contextuelle (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "LEX-024-NEG",
        "scenario": "Refus ou signalement de violation : Préférence contextuelle (voir 19_LOCALES.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-001",
      "title": "Découverte des rôles",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-001 — Découverte des rôles",
      "normative_summary": "Parcourir les sources historiques avec adaptateur de version qui identifie précisément les rôles sémantiques : sujet, propriété, cible d'entité, qualificateur sémantique. Les champs littéraux, citations, noms de personnes dans du texte, corps de document, URLs, références éditoriales ne sont pas des cibles à convertir par remplacement. S'il est impossible d'établir le rôle d'un champ, le laisser u",
      "positive_test": {
        "id": "MIG-001-POS",
        "scenario": "Comportement conforme : Découverte des rôles (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-001-NEG",
        "scenario": "Refus ou signalement de violation : Découverte des rôles (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-002",
      "title": "Plan non exécutable Framework",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-002 — Plan non exécutable Framework",
      "normative_summary": "Produire un kristal_dik_conversion_plan conforme au schéma upstream : source artefact/version/SHA, namespace, catalog/crosswalk, liste d'opérations chacune avec JSON Pointer exact, ancienne valeur, rôle, ID cible, décision pending|approved|rejected suivant schéma officiel. Les scores de correspondance restent consultatifs. Aucune opération pending ou rejected ne s'exécute.",
      "positive_test": {
        "id": "MIG-002-POS",
        "scenario": "Comportement conforme : Plan non exécutable Framework (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-002-NEG",
        "scenario": "Refus ou signalement de violation : Plan non exécutable Framework (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-003",
      "title": "Résolution et revue",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-003 — Résolution et revue",
      "normative_summary": "Ordre de proposition : ID interne déjà connu -> mapping externe accepté/exact et typé -> recherche lexicale contextualisée -> candidats manuels. Vérifier toutes les hypothèses, ambiguïtés et absence de KQ. Créer un nouveau KQ éventuel via l'autorité d'allocation, après revue. Ne pas convertir un mot « grâce » automatiquement sans préciser le sens.",
      "positive_test": {
        "id": "MIG-003-POS",
        "scenario": "Comportement conforme : Résolution et revue (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-003-NEG",
        "scenario": "Refus ou signalement de violation : Résolution et revue (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-004",
      "title": "Exécution par producteur",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-004 — Exécution par producteur",
      "normative_summary": "L'Authoring Kit ou autre producteur autorisé exécute après relecture indépendante : comparer digest octets de l'ancien artefact, JSON pointers et anciennes valeurs, décision approuvée et preuves ; appliquer transactionnellement à une nouvelle révision, jamais à la source ; valider le nouveau graphe contre Framework ; conserver journal de conversion et lien de retour. diK ne se déclare pas implicit",
      "positive_test": {
        "id": "MIG-004-POS",
        "scenario": "Comportement conforme : Exécution par producteur (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-004-NEG",
        "scenario": "Refus ou signalement de violation : Exécution par producteur (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-005",
      "title": "Patch d'édition linguistique",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-005 — Patch d'édition linguistique",
      "normative_summary": "Une vue annotée peut demander une modification sémantique : le système affiche avant/après et identifiants, produit patch_candidate, oblige revue. Si seule la traduction change et aucun ID/relation ne change, modifier une couche curatée, pas le graphe. Cette bifurcation est essentielle pour éviter la confusion « correction d'un mot » = « changement de sens ».",
      "positive_test": {
        "id": "MIG-005-POS",
        "scenario": "Comportement conforme : Patch d'édition linguistique (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-005-NEG",
        "scenario": "Refus ou signalement de violation : Patch d'édition linguistique (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "MIG-006",
      "title": "Échecs et reprises",
      "source_document": "07_MIGRATION.md",
      "source_heading": "## MIG-006 — Échecs et reprises",
      "normative_summary": "L'opération est idempotente par (source hash, plan ID/revision, decisions hash, producer version). Si une révision a déjà été produite, rendre son adresse ; pas de seconde mutation. En cas de crash pendant staging : révision non visible, rollback et possibilité de relance vérifiée. L'original historique et ses commitments v9 restent inchangés.",
      "positive_test": {
        "id": "MIG-006-POS",
        "scenario": "Comportement conforme : Échecs et reprises (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "MIG-006-NEG",
        "scenario": "Refus ou signalement de violation : Échecs et reprises (voir 07_MIGRATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-001",
      "title": "Structure recommandée",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-001 — Structure recommandée",
      "normative_summary": "text src/dik/ domain/ # IDs, résolution, décisions, composition, invariants ; sans SQL/HTTP/IO application/ # use cases : import, revue, audit, couverture, projection, migration candidate ports/ # interfaces Reader/Writer/Registry/Catalog/Crosswalk/Clock/Verifier adapters/ framework/ # schémas/validations versionnées Framework (pas une réécriture) wikidata/ # dump parser, change feed, HTTP explici",
      "positive_test": {
        "id": "OPS-001-POS",
        "scenario": "Comportement conforme : Structure recommandée (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-001-NEG",
        "scenario": "Refus ou signalement de violation : Structure recommandée (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-002",
      "title": "Règle des dépendances",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-002 — Règle des dépendances",
      "normative_summary": "entrypoints -> application -> domain, adapters -> ports/domain via injection. Le domaine n'importe ni SQLite ni requests/urllib ni frameworks web. Un CatalogReader vérifie les artefacts Framework ; un IndexReader sert les recherches mais ne crée aucun concept. Les writes passent par commandes explicites, les reads par vues dérivées (CQRS local léger, pas besoin Kafka).",
      "positive_test": {
        "id": "OPS-002-POS",
        "scenario": "Comportement conforme : Règle des dépendances (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-002-NEG",
        "scenario": "Refus ou signalement de violation : Règle des dépendances (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-003",
      "title": "Bounded contexts",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-003 — Bounded contexts",
      "normative_summary": "- identity : référents et types, normalisation, namespace.",
      "positive_test": {
        "id": "OPS-003-POS",
        "scenario": "Comportement conforme : Bounded contexts (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-003-NEG",
        "scenario": "Refus ou signalement de violation : Bounded contexts (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-004",
      "title": "Patterns retenus, sans sur-ingénierie",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-004 — Patterns retenus, sans sur-ingénierie",
      "normative_summary": "Anti-Corruption Layer pour Wikidata et legacy ; Hexagonal Architecture pour le domaine ; Modular Monolith pour déploiement simple ; CQRS interne pour index rapides ; Idempotency pour les jobs ; Cache-Aside pour résolutions ; Immutable Infrastructure (par analogie) pour snapshots ; Strangler Fig pour migration progressive des anciens Kristals. Pas de service mesh, microservices obligatoires, Event ",
      "positive_test": {
        "id": "OPS-004-POS",
        "scenario": "Comportement conforme : Patterns retenus, sans sur-ingénierie (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-004-NEG",
        "scenario": "Refus ou signalement de violation : Patterns retenus, sans sur-ingénierie (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-005",
      "title": "Déterminisme",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-005 — Déterminisme",
      "normative_summary": "À entrées/version identiques, résultat sémantique identique. Ordre stable des entrées, canonical JSON pour hashes défini, gestion UTF-8/NFC explicite, horodatage/auteur séparés de la partie reproductible, politique de tie/conflict non basée sur l'ordre SQL ni un dictionnaire Python arbitraire.",
      "positive_test": {
        "id": "OPS-005-POS",
        "scenario": "Comportement conforme : Déterminisme (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-005-NEG",
        "scenario": "Refus ou signalement de violation : Déterminisme (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-006",
      "title": "Import Framework",
      "source_document": "09_ARCHITECTURE.md",
      "source_heading": "## OPS-006 — Import Framework",
      "normative_summary": "Remplacer les copies vendoriées par un composant upstream épinglé si disponible et contractuellement compatible ; à défaut conserver avec hash et tests de comparaison. Ne jamais « améliorer » silencieusement les validateurs v11 embarqués.",
      "positive_test": {
        "id": "OPS-006-POS",
        "scenario": "Comportement conforme : Import Framework (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-006-NEG",
        "scenario": "Refus ou signalement de violation : Import Framework (voir 09_ARCHITECTURE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-010",
      "title": "Autorité",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-010 — Autorité",
      "normative_summary": "La source de vérité est le catalogue de fichiers versionnés et les documents Framework signés/empreintés selon leur profil. SQLite est un index dérivé reconstructible, pas un registre KQ autonome. L'instance peut être détruite puis reconstruite à partir d'un manifeste publié et de ses shards.",
      "positive_test": {
        "id": "OPS-010-POS",
        "scenario": "Comportement conforme : Autorité (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-010-NEG",
        "scenario": "Refus ou signalement de violation : Autorité (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-011",
      "title": "Structure proposée",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-011 — Structure proposée",
      "normative_summary": "text workspace/ projects/ # références à graphes/catalogues, non copies massives obligatoires manifests/ # pointeurs de révisions publiées snapshots/ # objets immuables de dictionnaires/crosswalks/lexiques curated/ # nouvelles révisions revues staging/ # zone de travail non publiée, nettoyable indexes/ # sqlite/fts reconstructibles et cache jobs/ # checkpoints sans autorité sémantique audits/ # dé",
      "positive_test": {
        "id": "OPS-011-POS",
        "scenario": "Comportement conforme : Structure proposée (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-011-NEG",
        "scenario": "Refus ou signalement de violation : Structure proposée (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-012",
      "title": "Index logique (dérivé)",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-012 — Index logique (dérivé)",
      "normative_summary": "Tables proposées : active_manifest, semantic_key(namespace,id,kind), lexeme(namespace,id,locale,domain,layer,priority,term,aliases,status), reverse_terms(locale,normalized_term,namespace,id,kind,context), external_mapping(namespace,id,system,external_id,relation,status,decision), snapshot(hash,source,version), job_checkpoint, audit_decision. Indexer locale + normalized_term + kind et namespace+id+",
      "positive_test": {
        "id": "OPS-012-POS",
        "scenario": "Comportement conforme : Index logique (dérivé) (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-012-NEG",
        "scenario": "Refus ou signalement de violation : Index logique (dérivé) (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-013",
      "title": "MVCC / cohérence",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-013 — MVCC / cohérence",
      "normative_summary": "Le lecteur fixe une révision complète de manifeste au début ; les jobs peuvent préparer une autre révision sans changer les données vues. Un pointer swap atomique rend la nouvelle version visible après validation. Caches clés : (manifest_digest, namespace, KQ/KP, locale, domain, resolution_profile) ; invalider par changement de digest, pas via TTL qui pourrait masquer une publication.",
      "positive_test": {
        "id": "OPS-013-POS",
        "scenario": "Comportement conforme : MVCC / cohérence (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-013-NEG",
        "scenario": "Refus ou signalement de violation : MVCC / cohérence (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-014",
      "title": "Tâches et transactions",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-014 — Tâches et transactions",
      "normative_summary": "Une mise à jour publie son catalogue et ses shards ensemble, jamais un par un visibles. Crash avant commit : ancien pointeur inchangé. Crash après commit : manifeste vérifié, index peut être reconstruit. Aucun état partial-success silencieux à une API qui annonce réussite.",
      "positive_test": {
        "id": "OPS-014-POS",
        "scenario": "Comportement conforme : Tâches et transactions (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-014-NEG",
        "scenario": "Refus ou signalement de violation : Tâches et transactions (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "OPS-015",
      "title": "Efficacité",
      "source_document": "10_STOCKAGE_INDEXATION.md",
      "source_heading": "## OPS-015 — Efficacité",
      "normative_summary": "Chargement par lots/shards, streaming, réutilisation des parseurs/index, mémoire plafonnée, index réparables ; comparaison incrémentale des hashes de shards ; limiter l'audit complet quotidien en préférant audit incrémental + audit intégral périodique au lancement d'une release.",
      "positive_test": {
        "id": "OPS-015-POS",
        "scenario": "Comportement conforme : Efficacité (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "OPS-015-NEG",
        "scenario": "Refus ou signalement de violation : Efficacité (voir 10_STOCKAGE_INDEXATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PERF-001",
      "title": "Objectifs, pas promesses déjà atteintes",
      "source_document": "14_PERFORMANCE.md",
      "source_heading": "## PERF-001 — Objectifs, pas promesses déjà atteintes",
      "normative_summary": "diK 1.0 vise les centaines de langues, les dictionnaires clairsemés, millions d'enregistrements lexicaux et un gros miroir Wikidata local. Les performances doivent être mesurées sur une configuration publiée et ne peuvent pas être déduites des 36 tests de diK 0.3 ou du seul gain de 72,6 % sur 1 000 assertions synthétiques.",
      "positive_test": {
        "id": "PERF-001-POS",
        "scenario": "Comportement conforme : Objectifs, pas promesses déjà atteintes (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PERF-001-NEG",
        "scenario": "Refus ou signalement de violation : Objectifs, pas promesses déjà atteintes (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PERF-002",
      "title": "Métriques obligatoires",
      "source_document": "14_PERFORMANCE.md",
      "source_heading": "## PERF-002 — Métriques obligatoires",
      "normative_summary": "Taille brut vs compact vs gzip, CPU max/moyenne, RSS max, disque temporaire, lecture séquentielle, nb de shards, débit d'import, taux cache, nombre de fichiers lus, durée de vérification des hashes, temps de reprise/crash, couverture 300 langues sparse, latence UI. Faire essais froid/chaud séparément.",
      "positive_test": {
        "id": "PERF-002-POS",
        "scenario": "Comportement conforme : Métriques obligatoires (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PERF-002-NEG",
        "scenario": "Refus ou signalement de violation : Métriques obligatoires (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PERF-003",
      "title": "Techniques",
      "source_document": "14_PERFORMANCE.md",
      "source_heading": "## PERF-003 — Techniques",
      "normative_summary": "- Joins via index par ID/crosswalk, pas scans complets de tous les 300 fichiers par lookup.",
      "positive_test": {
        "id": "PERF-003-POS",
        "scenario": "Comportement conforme : Techniques (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PERF-003-NEG",
        "scenario": "Refus ou signalement de violation : Techniques (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PERF-004",
      "title": "Jeu d'essais",
      "source_document": "14_PERFORMANCE.md",
      "source_heading": "## PERF-004 — Jeu d'essais",
      "normative_summary": "S0 : fixture Framework v11. S1 : 1 000 assertions répétitives (comparaison v0.3). S2 : 100k assertions mixtes (littéraux et qualifiers). S3 : 1M identifiants dont plusieurs langues clairsemées. S4 : échantillon représentatif d'un dump Wikidata local. S5 : snapshot énorme/import interrompu/snapshot changé. Toutes les fixtures ont hash, provenance et droits appropriés ; aucune distribution de dump m",
      "positive_test": {
        "id": "PERF-004-POS",
        "scenario": "Comportement conforme : Jeu d'essais (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PERF-004-NEG",
        "scenario": "Refus ou signalement de violation : Jeu d'essais (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PERF-005",
      "title": "Critère de release",
      "source_document": "14_PERFORMANCE.md",
      "source_heading": "## PERF-005 — Critère de release",
      "normative_summary": "Le rapport de performances joint à la release doit préciser réussite/échec pour chaque budget ratifié, version Python/OS/disque/RAM, exact format de fichier et commandes. Pas de « optimisé » uniquement parce que l'archive est plus petite.",
      "positive_test": {
        "id": "PERF-005-POS",
        "scenario": "Comportement conforme : Critère de release (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PERF-005-NEG",
        "scenario": "Refus ou signalement de violation : Critère de release (voir 14_PERFORMANCE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-001",
      "title": "Contrat des trois vues",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-001 — Contrat des trois vues",
      "normative_summary": "- Canonique Framework v11 : KQ/KP/KA/KS + assertions/littéraux/qualificatifs/sources, aucun label servant d'identité.",
      "positive_test": {
        "id": "PRJ-001-POS",
        "scenario": "Comportement conforme : Contrat des trois vues (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-001-NEG",
        "scenario": "Refus ou signalement de violation : Contrat des trois vues (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-002",
      "title": "Règles de réversibilité",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-002 — Règles de réversibilité",
      "normative_summary": "La restauration extrait le graphe conservé et compare structure/hashes/ancres ; aucun reverse lookup des mots. En mode robuste, vérifier aussi le graphe, registre, catalogue, crosswalk et couches d'origine. Sans projet source/ancres authentifiées, les hashes auto-déclarés ne prouvent pas l'origine ; répondre integrity_consistent et non authentic.",
      "positive_test": {
        "id": "PRJ-002-POS",
        "scenario": "Comportement conforme : Règles de réversibilité (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-002-NEG",
        "scenario": "Refus ou signalement de violation : Règles de réversibilité (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-003",
      "title": "Portée du lexique",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-003 — Portée du lexique",
      "normative_summary": "Références couvertes : KQ entités et KP prédicats/qualificateurs ; KS/KA sont conservés mais leur dénomination n'est pas comptée comme couverture KQ. La table lexicale est indexée par identifiant dans un namespace fixé et ancré. En projet multi-namespace futur, les clés de table devront porter le namespace ou employer des namespaces isolés par enveloppe — jamais fusionner deux KQ1001.",
      "positive_test": {
        "id": "PRJ-003-POS",
        "scenario": "Comportement conforme : Portée du lexique (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-003-NEG",
        "scenario": "Refus ou signalement de violation : Portée du lexique (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-004",
      "title": "Bords importants",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-004 — Bords importants",
      "normative_summary": "- Valeurs littérales/texte cité préservés octet logiquement (Unicode identique ; sérialisation JSON peut différer en whitespace).",
      "positive_test": {
        "id": "PRJ-004-POS",
        "scenario": "Comportement conforme : Bords importants (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-004-NEG",
        "scenario": "Refus ou signalement de violation : Bords importants (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-005",
      "title": "Compatibilité",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-005 — Compatibilité",
      "normative_summary": "Lire et vérifier dik.compact-projection/1.0 et l'ancienne projection verbose v0.2 ; ne pas changer rétroactivement leur définition. Pour les rendre plus robustes : enveloppe externe versionnée optionnelle, sans altérer l'ancienne structure. Ne pas supprimer --format verbose avant décision de dépréciation publiée et tests de non-régression.",
      "positive_test": {
        "id": "PRJ-005-POS",
        "scenario": "Comportement conforme : Compatibilité (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-005-NEG",
        "scenario": "Refus ou signalement de violation : Compatibilité (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-006",
      "title": "Édition",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-006 — Édition",
      "normative_summary": "Un utilisateur qui modifie un texte en mode clean ne crée pas un nouveau KQ ni une nouvelle assertion. L'éditeur lié au canon doit créer un patch d'intention : chemin de l'objet structuré, ancienne valeur/ID, candidat de nouvelle valeur/ID, preuves et statut pending_review. Une modification textuelle libre non ancrée ne peut pas se convertir automatiquement en patch accepté.",
      "positive_test": {
        "id": "PRJ-006-POS",
        "scenario": "Comportement conforme : Édition (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-006-NEG",
        "scenario": "Refus ou signalement de violation : Édition (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "PRJ-007",
      "title": "Limites mémoire",
      "source_document": "06_PROJECTIONS.md",
      "source_heading": "## PRJ-007 — Limites mémoire",
      "normative_summary": "Le format compact actuel incorpore le graphe entier. diK 1.0 DOIT conserver cette compatibilité mais MAY proposer un nouveau profil de projection par références à des shards immuables, uniquement si nécessaire à l'échelle, avec manifeste/empreintes, non une modification silencieuse du profil compact existant.",
      "positive_test": {
        "id": "PRJ-007-POS",
        "scenario": "Comportement conforme : Limites mémoire (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "PRJ-007-NEG",
        "scenario": "Refus ou signalement de violation : Limites mémoire (voir 06_PROJECTIONS.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-001",
      "title": "Modèle des menaces",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-001 — Modèle des menaces",
      "normative_summary": "Entrées potentiellement hostiles : dumps Wikidata, dictionnaires tiers, archives legacy, documents d'IA, labels avec Markdown/HTML/JSON malicieux, noms de fichiers, manifestes/path, fichiers trop volumineux et liens symboliques. Risques : exécution arbitraire, path traversal, zip/decompression bomb, injection SQL/HTML/Markdown, SSRF lors de téléchargement, effacement de couches curatées, falsifica",
      "positive_test": {
        "id": "SEC-001-POS",
        "scenario": "Comportement conforme : Modèle des menaces (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-001-NEG",
        "scenario": "Refus ou signalement de violation : Modèle des menaces (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-002",
      "title": "Validation à chaque frontière",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-002 — Validation à chaque frontière",
      "normative_summary": "Utiliser parsing strict JSON Schema officiel pour artefacts Framework, validation de schéma applicatif pour documents diK, limites de taille/profondeur, UTF-8, contrôles namespace/type, chemins confinés au root, sorties JSON échappées, requêtes SQL paramétrées, quotas de ressources. Le contenu des dumps n'est jamais une instruction pour une IA, un appel système ou un interpréteur.",
      "positive_test": {
        "id": "SEC-002-POS",
        "scenario": "Comportement conforme : Validation à chaque frontière (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-002-NEG",
        "scenario": "Refus ou signalement de violation : Validation à chaque frontière (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-003",
      "title": "Intégrité vs authenticité",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-003 — Intégrité vs authenticité",
      "normative_summary": "SHA-256 protège contre corruption accidentelle et permet adressage par contenu, mais ne prouve pas qui a émis un fichier. Le système affiche hash_verified distinct de publisher_authenticated. Pour des approbations distribuées, prévoir signature et contrôle des rôles ; aucune signature fictive ou « approved by AI » n'est acceptable.",
      "positive_test": {
        "id": "SEC-003-POS",
        "scenario": "Comportement conforme : Intégrité vs authenticité (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-003-NEG",
        "scenario": "Refus ou signalement de violation : Intégrité vs authenticité (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-004",
      "title": "Revue et rôles",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-004 — Revue et rôles",
      "normative_summary": "Rôles conceptuels : viewer, editor (propositions), reviewer (approbations), publisher (snapshots), operator (imports). Un environnement mono-utilisateur peut implémenter un mode local explicite mais doit garder l'identité et les décisions d'audit. Un agent IA ne doit pas être compté comme réviseur humain ni contourner une approbation. Séparation des responsabilités pour décisions critiques, config",
      "positive_test": {
        "id": "SEC-004-POS",
        "scenario": "Comportement conforme : Revue et rôles (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-004-NEG",
        "scenario": "Refus ou signalement de violation : Revue et rôles (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-005",
      "title": "Licences",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-005 — Licences",
      "normative_summary": "Toute source externe exige métadonnées licence, origine, version, conditions d'usage/redistribution. Sans licence connue/compatible : quarantaine ; ne pas redistribuer automatiquement les entrées. Les données importées ne deviennent pas libres parce qu'elles sont encodées en JSONL. Les fichiers diK distribués doivent respecter l'AGPL et notices du code utilisé, sans inventer des permissions de red",
      "positive_test": {
        "id": "SEC-005-POS",
        "scenario": "Comportement conforme : Licences (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-005-NEG",
        "scenario": "Refus ou signalement de violation : Licences (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-006",
      "title": "Restauration historique",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-006 — Restauration historique",
      "normative_summary": "Les anciens commits/empreintes/bytes sont intouchables. La vérification d'un nouveau Kristal ne doit pas exiger la présence de Wikidata en ligne. Prévenir exfiltration de textes soumis en projet privé (pas de recherche distante implicite ni index central).",
      "positive_test": {
        "id": "SEC-006-POS",
        "scenario": "Comportement conforme : Restauration historique (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-006-NEG",
        "scenario": "Refus ou signalement de violation : Restauration historique (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "SEC-007",
      "title": "Déni de service",
      "source_document": "13_SECURITE.md",
      "source_heading": "## SEC-007 — Déni de service",
      "normative_summary": "Quota taille fichier/shard, limite de langue sélectionnée par tâche, budget temps/mémoire, cancellation safe, nombre max de candidats/requêtes, liens symboliques et noms Unicode ambigus traités de manière explicite ; liste blanche de sources réseau, pas de téléchargement arbitraire sur URLs fournies par un dump.",
      "positive_test": {
        "id": "SEC-007-POS",
        "scenario": "Comportement conforme : Déni de service (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "SEC-007-NEG",
        "scenario": "Refus ou signalement de violation : Déni de service (voir 13_SECURITE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-001",
      "title": "Sources",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-001 — Sources",
      "normative_summary": "Toujours exécuter : (a) tests unitaires/domain diK ; (b) tests des schémas et vecteurs réels Framework v11 draft.3 ; (c) tests compat dik.compact-projection/1.0 et verbose v0.2 ; (d) cross-repo Authoring Kit + Integration Pack ; (e) tests historiques v9/v10 lecture ; (f) attaques et tests de reprise.",
      "positive_test": {
        "id": "TCK-001-POS",
        "scenario": "Comportement conforme : Sources (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-001-NEG",
        "scenario": "Refus ou signalement de violation : Sources (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-002",
      "title": "Catégories bloquantes",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-002 — Catégories bloquantes",
      "normative_summary": "| ID | Propriété | Test positif | Rejet exigé |",
      "positive_test": {
        "id": "TCK-002-POS",
        "scenario": "Comportement conforme : Catégories bloquantes (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-002-NEG",
        "scenario": "Refus ou signalement de violation : Catégories bloquantes (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-003",
      "title": "Tests d'invariants génératifs",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-003 — Tests d'invariants génératifs",
      "normative_summary": "- Générer des IDs valides de multiples namespaces, y compris mêmes numéros ; vérifier non-fusion.",
      "positive_test": {
        "id": "TCK-003-POS",
        "scenario": "Comportement conforme : Tests d'invariants génératifs (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-003-NEG",
        "scenario": "Refus ou signalement de violation : Tests d'invariants génératifs (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-004",
      "title": "Oracles",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-004 — Oracles",
      "normative_summary": "Un test doit comparer sorties diK au calcul de référence Framework quand il existe : validation v11, couverture, audit crosswalk ; pour projection comparer equality structurelle du graphe, pas comparaison de Markdown seul. L'Integration Pack doit afficher les mêmes IDs et le même décompte de couverture que diK. L'Authoring Kit doit revérifier un plan avant migration.",
      "positive_test": {
        "id": "TCK-004-POS",
        "scenario": "Comportement conforme : Oracles (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-004-NEG",
        "scenario": "Refus ou signalement de violation : Oracles (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-005",
      "title": "Gates CI",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-005 — Gates CI",
      "normative_summary": "G1 lint/docs + schémas, G2 tests unitaires, G3 négatifs et propriétés, G4 contrats Framework, G5 interop Authoring + Integration, G6 sécurité + reprise, G7 bench performance, G8 package déterministe/manifest signature selon politique. Aucun G1–G6 en échec ou non exécuté pour RC/stable. G7 selon budgets ratifiés ; preuves jointes.",
      "positive_test": {
        "id": "TCK-005-POS",
        "scenario": "Comportement conforme : Gates CI (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-005-NEG",
        "scenario": "Refus ou signalement de violation : Gates CI (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "TCK-006",
      "title": "Traçabilité",
      "source_document": "15_TESTS_TCK.md",
      "source_heading": "## TCK-006 — Traçabilité",
      "normative_summary": "Chaque nouveau test porte un ID exigence et un cas d'essai ; chaque MUST a au moins un test positif et un test d'échec. La matrice [17_TRACABILITE.md](17_TRACABILITE.md) est le registre initial, à compléter par lien précis vers fichier/méthode/résultat lorsque le code sera produit.",
      "positive_test": {
        "id": "TCK-006-POS",
        "scenario": "Comportement conforme : Traçabilité (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "TCK-006-NEG",
        "scenario": "Refus ou signalement de violation : Traçabilité (voir 15_TESTS_TCK.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-001",
      "title": "Espaces principaux",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-001 — Espaces principaux",
      "normative_summary": "1. Vue Projets : état de validité, Framework lié, namespace, graphes, dictionnaires, fraîcheur du miroir, tâches en cours. 2. Sources de dictionnaires : ajouter source Wikidata/tiers/fichier, licence, langues, provenance, statut, snapshot, priorité proposée ; jamais importer une source externe comme fiable sans contrôle. 3. Atelier lexical : chercher un KQ/KP ou un terme, comparer termes par langu",
      "positive_test": {
        "id": "UI-001-POS",
        "scenario": "Comportement conforme : Espaces principaux (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-001-NEG",
        "scenario": "Refus ou signalement de violation : Espaces principaux (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-002",
      "title": "Modèle de confiance visible",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-002 — Modèle de confiance visible",
      "normative_summary": "Afficher toujours ce qui est verified, candidate, unreviewed, missing, fallback, conflicted. Aucun code couleur seul : statuts textuels, tooltip avec source et décision, icônes accessibles. Distinguer un label disponible de une identité correctement alignée. Un bouton « Accepter » doit indiquer les conséquences et nécessite un rôle autorisé.",
      "positive_test": {
        "id": "UI-002-POS",
        "scenario": "Comportement conforme : Modèle de confiance visible (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-002-NEG",
        "scenario": "Refus ou signalement de violation : Modèle de confiance visible (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-003",
      "title": "Lecture légère",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-003 — Lecture légère",
      "normative_summary": "Rendu clean ne montre pas obligatoirement les KQ mais chaque fragment peut ouvrir son détail (ID/namespace/source/langue/provenance). Les KQ manquants restent visibles comme lacune au lieu d'être remplacés par un mot conjectural. Mode annoté pour IA affiche références contextualisées, sans alourdir le canon. Un sélecteur de langue ne charge pas 300 dictionnaires.",
      "positive_test": {
        "id": "UI-003-POS",
        "scenario": "Comportement conforme : Lecture légère (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-003-NEG",
        "scenario": "Refus ou signalement de violation : Lecture légère (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-004",
      "title": "UX de revue",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-004 — UX de revue",
      "normative_summary": "Vue diff avant/après ; afficher la phrase, l'ID cible, contexte type/propriété, source, licence et éventuelles ambiguïtés ; actions proposer, rejeter, accepter avec preuve, différer. La revue doit résister à double clic et perte réseau (clé idempotente, révision attendue). Impossible de passer candidate à accepted via simple tri/filtre.",
      "positive_test": {
        "id": "UI-004-POS",
        "scenario": "Comportement conforme : UX de revue (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-004-NEG",
        "scenario": "Refus ou signalement de violation : UX de revue (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-005",
      "title": "Accessibilité",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-005 — Accessibilité",
      "normative_summary": "Support navigation clavier, lecteurs d'écran, internationalisation, RTL (arabe, hébreu…), scripts multiples, très longs labels, et affichage d'alias non romains sans translittération forcée. Langue UI indépendante du choix de dictionnaire. La qualité des textes de 300 langues reste mesurée, non prétendue.",
      "positive_test": {
        "id": "UI-005-POS",
        "scenario": "Comportement conforme : Accessibilité (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-005-NEG",
        "scenario": "Refus ou signalement de violation : Accessibilité (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "UI-006",
      "title": "Déploiement",
      "source_document": "12_INTERFACE.md",
      "source_heading": "## UI-006 — Déploiement",
      "normative_summary": "Application locale utilisable sans compte cloud ; interface GUI portable selon technologie retenue. Une implémentation web locale ne doit pas exposer par défaut fichiers privés/dumps sans permission. Pas de télémétrie réseau cachée.",
      "positive_test": {
        "id": "UI-006-POS",
        "scenario": "Comportement conforme : Déploiement (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "UI-006-NEG",
        "scenario": "Refus ou signalement de violation : Déploiement (voir 12_INTERFACE.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "XW-001",
      "title": "Recherche candidate, pas attribution d'identité",
      "source_document": "04_CONCILIATION.md",
      "source_heading": "## XW-001 — Recherche candidate, pas attribution d'identité",
      "normative_summary": "Entrée obligatoire : term, locale, expected_kind (KQ/KP), namespace_id et facultativement domaine KQ, provenance et type de source. La recherche explore exact Unicode normalisé, alias, descriptions, relations existantes et types contextuels ; les variantes fuzzy sont des candidats. Sortie : ensemble déterministe de candidats identifiés, raison par signal, distance/type de relation, preuves, dictio",
      "positive_test": {
        "id": "XW-001-POS",
        "scenario": "Comportement conforme : Recherche candidate, pas attribution d'identité (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "XW-001-NEG",
        "scenario": "Refus ou signalement de violation : Recherche candidate, pas attribution d'identité (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "XW-002",
      "title": "Machine d'états des rapprochements",
      "source_document": "04_CONCILIATION.md",
      "source_heading": "## XW-002 — Machine d'états des rapprochements",
      "normative_summary": "proposed -> reviewed -> accepted | rejected; accepted -> superseded avec nouvelle décision. Les rapprochements closeMatch/broadMatch/narrowMatch/relatedMatch ne deviennent jamais exactMatch implicitement. Une acceptation exige : identifiant de décision, réviseur autorisé, méthode, lien d'évidence KS, version des sources, justification et contrôle d'unicité active. Il n'existe pas d'acceptation sim",
      "positive_test": {
        "id": "XW-002-POS",
        "scenario": "Comportement conforme : Machine d'états des rapprochements (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "XW-002-NEG",
        "scenario": "Refus ou signalement de violation : Machine d'états des rapprochements (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "XW-003",
      "title": "Multi-dictionnaires",
      "source_document": "04_CONCILIATION.md",
      "source_heading": "## XW-003 — Multi-dictionnaires",
      "normative_summary": "- Comparer les sources sans confondre les clés locales des fournisseurs avec les clés KQ.",
      "positive_test": {
        "id": "XW-003-POS",
        "scenario": "Comportement conforme : Multi-dictionnaires (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "XW-003-NEG",
        "scenario": "Refus ou signalement de violation : Multi-dictionnaires (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "XW-004",
      "title": "Crosswalk Wikidata",
      "source_document": "04_CONCILIATION.md",
      "source_heading": "## XW-004 — Crosswalk Wikidata",
      "normative_summary": "(namespace,KQ) ↔ (wikidata,Q) et (namespace,KP) ↔ (wikidata,P) seulement, sans mélange. Les contraintes de mapping accepted exact du Framework s'appliquent à chaque vue active. Pour un nouveau Q Wikidata : créer candidate, évaluer puis publier une révision ; aucun KQ modifié. Pour Q redirigé, supprimé, scindé, fusionné : événement de revue + éventuel superseding, pas substitution immédiate.",
      "positive_test": {
        "id": "XW-004-POS",
        "scenario": "Comportement conforme : Crosswalk Wikidata (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "XW-004-NEG",
        "scenario": "Refus ou signalement de violation : Crosswalk Wikidata (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    },
    {
      "requirement_id": "XW-005",
      "title": "Corrections et annulations",
      "source_document": "04_CONCILIATION.md",
      "source_heading": "## XW-005 — Corrections et annulations",
      "normative_summary": "Toute promotion/rejet/supersession s'écrit dans un journal append-only pour audit et est matérialisée dans une nouvelle vue active. Les prévisualisations peuvent être annulées sans effet. Les décisions déjà publiées sont contredites par un événement nouveau, jamais éditées rétroactivement.",
      "positive_test": {
        "id": "XW-005-POS",
        "scenario": "Comportement conforme : Corrections et annulations (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "negative_test": {
        "id": "XW-005-NEG",
        "scenario": "Refus ou signalement de violation : Corrections et annulations (voir 04_CONCILIATION.md)",
        "result": "NOT_RUN",
        "evidence": null
      },
      "level": "TARGET",
      "artifact_sha256": null
    }
  ]
}
```


<a id="doc-tests-reference-vectors-json"></a>

### `tests/reference_vectors.json`

```json
{
  "suite_id": "DIK-1.0-DOC-ORACLE-CANDIDATE.2",
  "notice": "Spec oracle; tests future product NOT RUN",
  "vectors": [
    {
      "case_id": "D-LEX-01",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr",
        "fallbacks": {
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "resolved",
        "id": "KQ1",
        "effective_locale": "fr",
        "term": "Saint Augustin",
        "fallback": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-02",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr-CA",
        "fallbacks": {
          "fr-CA": [
            "fr"
          ],
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "resolved",
        "id": "KQ1",
        "effective_locale": "fr",
        "term": "Saint Augustin",
        "fallback": true
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-03",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ2",
        "locale": "fr",
        "fallbacks": {
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "missing",
        "id": "KQ2"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-04",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr",
        "fallbacks": {
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Alpha",
            "layer": "a"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Bêta",
            "layer": "b"
          }
        ]
      },
      "expected": {
        "status": "conflicted",
        "id": "KQ1",
        "effective_locale": "fr"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-05",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr-CA",
        "fallbacks": {
          "fr-CA": [],
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "missing",
        "id": "KQ1"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-06",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr-CA",
        "fallbacks": {
          "fr-CA": [
            "fr"
          ],
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          },
          {
            "locale": "fr-CA",
            "id": "KQ1",
            "priority": 1,
            "term": "Augustin local",
            "layer": "regional"
          }
        ]
      },
      "expected": {
        "status": "resolved",
        "id": "KQ1",
        "effective_locale": "fr-CA",
        "term": "Augustin local",
        "fallback": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-07",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr",
        "fallbacks": {
          "fr": [
            "fr-CA"
          ],
          "fr-CA": [
            "fr"
          ]
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "reject",
        "code": "FALLBACK_CYCLE"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-08",
      "operation": "label",
      "requirement_id": "ID-001",
      "input": {
        "id": "Q8018",
        "locale": "fr",
        "fallbacks": {
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 10,
            "term": "Augustin",
            "layer": "wd"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Saint Augustin",
            "layer": "curated"
          }
        ]
      },
      "expected": {
        "status": "reject",
        "code": "INVALID_SEMANTIC_ID"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-LEX-09",
      "operation": "label",
      "requirement_id": "LEX-003",
      "input": {
        "id": "KQ1",
        "locale": "fr",
        "fallbacks": {
          "fr": []
        },
        "entries": [
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Augustin",
            "layer": "z"
          },
          {
            "locale": "fr",
            "id": "KQ1",
            "priority": 20,
            "term": "Augustin",
            "layer": "a"
          }
        ]
      },
      "expected": {
        "status": "resolved",
        "id": "KQ1",
        "effective_locale": "fr",
        "term": "Augustin",
        "fallback": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-REV-01",
      "operation": "reverse",
      "requirement_id": "XW-001",
      "input": {
        "term": "grâce",
        "locale": "fr",
        "kind": "KQ",
        "namespace": "demo",
        "entries": [
          {
            "id": "KQ1",
            "term": "grâce",
            "locale": "fr",
            "kind": "KQ"
          },
          {
            "id": "KQ2",
            "term": "grâce",
            "locale": "fr",
            "kind": "KQ"
          }
        ]
      },
      "expected": {
        "status": "ambiguous",
        "ids": [
          "KQ1",
          "KQ2"
        ]
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-REV-02",
      "operation": "reverse",
      "requirement_id": "XW-001",
      "input": {
        "term": "Grâce",
        "locale": "fr",
        "kind": "KQ",
        "namespace": "demo",
        "entries": [
          {
            "id": "KQ1",
            "term": "Grâce",
            "locale": "fr",
            "kind": "KQ"
          },
          {
            "id": "KQ3",
            "term": "Grace",
            "locale": "en",
            "kind": "KQ"
          }
        ]
      },
      "expected": {
        "status": "unique_candidate",
        "ids": [
          "KQ1"
        ]
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-REV-03",
      "operation": "reverse",
      "requirement_id": "XW-001",
      "input": {
        "term": "grâce",
        "locale": "fr",
        "kind": "KP",
        "namespace": "demo",
        "entries": [
          {
            "id": "KQ1",
            "term": "grâce",
            "locale": "fr",
            "kind": "KQ"
          }
        ]
      },
      "expected": {
        "status": "no_candidate",
        "ids": []
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-REV-04",
      "operation": "reverse",
      "requirement_id": "XW-001",
      "input": {
        "term": "grâce",
        "locale": "fr",
        "kind": "KQ",
        "namespace": "demo",
        "entries": [
          {
            "id": "KQ2",
            "term": "grâce",
            "locale": "fr",
            "kind": "KQ"
          },
          {
            "id": "KQ1",
            "term": "grâce",
            "locale": "fr",
            "kind": "KQ"
          }
        ]
      },
      "expected": {
        "status": "ambiguous",
        "ids": [
          "KQ1",
          "KQ2"
        ]
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-01",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-002",
      "input": {
        "internal": "KQ12",
        "external": "Q8018",
        "relation": "exactMatch",
        "status": "accepted",
        "reviewer": "human:alice",
        "evidence": [
          "KS1"
        ],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": true
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-02",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-004",
      "input": {
        "internal": "KP2",
        "external": "Q8018",
        "relation": "exactMatch",
        "status": "accepted",
        "reviewer": "human:alice",
        "evidence": [
          "KS1"
        ],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-03",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-002",
      "input": {
        "internal": "KQ12",
        "external": "Q8018",
        "relation": "closeMatch",
        "status": "accepted",
        "reviewer": "human:alice",
        "evidence": [
          "KS1"
        ],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-04",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-002",
      "input": {
        "internal": "KQ12",
        "external": "Q8018",
        "relation": "exactMatch",
        "status": "candidate",
        "reviewer": "human:alice",
        "evidence": [
          "KS1"
        ],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-05",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-002",
      "input": {
        "internal": "KQ12",
        "external": "Q8018",
        "relation": "exactMatch",
        "status": "accepted",
        "reviewer": "",
        "evidence": [
          "KS1"
        ],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-XW-06",
      "operation": "eligible_crosswalk",
      "requirement_id": "XW-002",
      "input": {
        "internal": "KQ12",
        "external": "Q8018",
        "relation": "exactMatch",
        "status": "accepted",
        "reviewer": "human:alice",
        "evidence": [],
        "decision": "DEC-1",
        "method": "manual"
      },
      "expected": {
        "eligible": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-COV-01",
      "operation": "coverage",
      "requirement_id": "COV-002",
      "input": {
        "ids": [
          "KQ1",
          "KQ2",
          "KP1"
        ],
        "states": {
          "KQ1": "direct",
          "KQ2": "fallback",
          "KP1": "missing"
        },
        "denominator_known": true
      },
      "expected": {
        "total": 3,
        "direct": 1,
        "fallback": 1,
        "missing": 1,
        "conflicted": 0,
        "complete_direct": false,
        "complete_usable": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-COV-02",
      "operation": "coverage",
      "requirement_id": "COV-002",
      "input": {
        "ids": [
          "KQ1",
          "KQ2"
        ],
        "states": {
          "KQ1": "direct",
          "KQ2": "direct"
        },
        "denominator_known": true
      },
      "expected": {
        "total": 2,
        "direct": 2,
        "fallback": 0,
        "missing": 0,
        "conflicted": 0,
        "complete_direct": true,
        "complete_usable": true
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-COV-03",
      "operation": "coverage",
      "requirement_id": "COV-006",
      "input": {
        "ids": [
          "KQ1"
        ],
        "states": {
          "KQ1": "direct"
        },
        "denominator_known": false
      },
      "expected": {
        "total": 1,
        "direct": 1,
        "fallback": 0,
        "missing": 0,
        "conflicted": 0,
        "complete_direct": false,
        "complete_usable": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-COV-04",
      "operation": "coverage",
      "requirement_id": "COV-002",
      "input": {
        "ids": [
          "KQ1",
          "KQ2"
        ],
        "states": {
          "KQ1": "direct",
          "KQ2": "conflicted"
        },
        "denominator_known": true
      },
      "expected": {
        "total": 2,
        "direct": 1,
        "fallback": 0,
        "missing": 0,
        "conflicted": 1,
        "complete_direct": false,
        "complete_usable": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-OPS-01",
      "operation": "idempotence",
      "requirement_id": "OPS-001",
      "input": {
        "previous_key": "job-1",
        "previous_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new_key": "job-1",
        "new_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      "expected": {
        "action": "replay"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-OPS-02",
      "operation": "idempotence",
      "requirement_id": "OPS-001",
      "input": {
        "previous_key": "job-1",
        "previous_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new_key": "job-1",
        "new_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      },
      "expected": {
        "action": "reject",
        "code": "IDEMPOTENCY_CONFLICT"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-OPS-03",
      "operation": "idempotence",
      "requirement_id": "OPS-001",
      "input": {
        "previous_key": "job-1",
        "previous_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new_key": "job-2",
        "new_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      },
      "expected": {
        "action": "start"
      },
      "run_status": "DOC_ORACLE_ONLY"
    },
    {
      "case_id": "D-COV-05",
      "operation": "coverage",
      "requirement_id": "COV-002",
      "input": {
        "ids": [],
        "states": {},
        "denominator_known": true
      },
      "expected": {
        "total": 0,
        "direct": 0,
        "fallback": 0,
        "missing": 0,
        "conflicted": 0,
        "complete_direct": false,
        "complete_usable": false
      },
      "run_status": "DOC_ORACLE_ONLY"
    }
  ]
}
```


<a id="doc-tests-tck-cases-json"></a>

### `tests/TCK_CASES.json`

```json
{
  "cases": [
    {
      "case_id": "ID-R2",
      "expected": "reject",
      "mandatory": true,
      "module": "identity",
      "result": "NOT_RUN",
      "scenario": "Raw Wikidata Q as graph subject"
    },
    {
      "case_id": "ID-R4",
      "expected": "reject",
      "mandatory": true,
      "module": "identity",
      "result": "NOT_RUN",
      "scenario": "Same KQ allocated concurrently"
    },
    {
      "case_id": "LEX-R2",
      "expected": "reject",
      "mandatory": true,
      "module": "lexical",
      "result": "NOT_RUN",
      "scenario": "Locale fallback not declared"
    },
    {
      "case_id": "LEX-R3",
      "expected": "reject",
      "mandatory": true,
      "module": "lexical",
      "result": "NOT_RUN",
      "scenario": "Equal priority conflicting terms"
    },
    {
      "case_id": "LEX-R4",
      "expected": "reject",
      "mandatory": true,
      "module": "lexical",
      "result": "NOT_RUN",
      "scenario": "Wikidata update overwrites curated"
    },
    {
      "case_id": "LEX-R6",
      "expected": "reject",
      "mandatory": true,
      "module": "lexical",
      "result": "NOT_RUN",
      "scenario": "Tampered dictionary SHA"
    },
    {
      "case_id": "XW-T1",
      "expected": "ambiguous",
      "mandatory": true,
      "module": "alignment",
      "result": "NOT_RUN",
      "scenario": "Same spelling on two different KQ"
    },
    {
      "case_id": "XW-T2",
      "expected": "reject",
      "mandatory": true,
      "module": "alignment",
      "result": "NOT_RUN",
      "scenario": "accepted exact without KS evidence"
    },
    {
      "case_id": "XW-T3",
      "expected": "reject",
      "mandatory": true,
      "module": "alignment",
      "result": "NOT_RUN",
      "scenario": "Duplicate active exact crosswalk"
    },
    {
      "case_id": "XW-T4",
      "expected": "reject",
      "mandatory": true,
      "module": "alignment",
      "result": "NOT_RUN",
      "scenario": "Q to KP mismatch"
    },
    {
      "case_id": "PRJ-T1",
      "expected": "identical",
      "mandatory": true,
      "module": "projection",
      "result": "NOT_RUN",
      "scenario": "Export and restore with qualifiers and literals"
    },
    {
      "case_id": "PRJ-T2",
      "expected": "reject",
      "mandatory": true,
      "module": "projection",
      "result": "NOT_RUN",
      "scenario": "Edited labels and recomputed self-hash against source"
    },
    {
      "case_id": "PRJ-T3",
      "expected": "reject",
      "mandatory": true,
      "module": "projection",
      "result": "NOT_RUN",
      "scenario": "Restore only from Markdown clean view"
    },
    {
      "case_id": "PRJ-T7",
      "expected": "missing",
      "mandatory": true,
      "module": "projection",
      "result": "NOT_RUN",
      "scenario": "Missing language label"
    },
    {
      "case_id": "MIG-T1",
      "expected": "unchanged",
      "mandatory": true,
      "module": "migration",
      "result": "NOT_RUN",
      "scenario": "Quotations not targeted"
    },
    {
      "case_id": "MIG-T2",
      "expected": "reject",
      "mandatory": true,
      "module": "migration",
      "result": "NOT_RUN",
      "scenario": "Source pointer changed before apply"
    },
    {
      "case_id": "MIG-T3",
      "expected": "reject",
      "mandatory": true,
      "module": "migration",
      "result": "NOT_RUN",
      "scenario": "Pending migration op executes"
    },
    {
      "case_id": "MIG-T7",
      "expected": "new_revision",
      "mandatory": true,
      "module": "migration",
      "result": "NOT_RUN",
      "scenario": "Approved plan emits new revision"
    },
    {
      "case_id": "COV-T1",
      "expected": "reference_match",
      "mandatory": true,
      "module": "coverage",
      "result": "NOT_RUN",
      "scenario": "Framework fixture fr-CA counts"
    },
    {
      "case_id": "COV-T2",
      "expected": "not_falsely_complete",
      "mandatory": true,
      "module": "coverage",
      "result": "NOT_RUN",
      "scenario": "301 sparse languages"
    },
    {
      "case_id": "IMP-T1",
      "expected": "atomic_resume",
      "mandatory": true,
      "module": "import",
      "result": "NOT_RUN",
      "scenario": "Crash in mid-import"
    },
    {
      "case_id": "IMP-T3",
      "expected": "reject",
      "mandatory": true,
      "module": "import",
      "result": "NOT_RUN",
      "scenario": "Candidate mapping imported as verified"
    },
    {
      "case_id": "IMP-T5",
      "expected": "idempotent",
      "mandatory": true,
      "module": "import",
      "result": "NOT_RUN",
      "scenario": "Re-import exact same source"
    },
    {
      "case_id": "SEC-T1",
      "expected": "reject",
      "mandatory": true,
      "module": "security",
      "result": "NOT_RUN",
      "scenario": "Path traversal in import path"
    },
    {
      "case_id": "SEC-T2",
      "expected": "escaped",
      "mandatory": true,
      "module": "security",
      "result": "NOT_RUN",
      "scenario": "HTML labels rendered"
    },
    {
      "case_id": "SEC-T7",
      "expected": "safe_rollback",
      "mandatory": true,
      "module": "security",
      "result": "NOT_RUN",
      "scenario": "Quota reached during import"
    },
    {
      "case_id": "PERF-S2",
      "expected": "benchmark",
      "mandatory": true,
      "module": "performance",
      "result": "NOT_RUN",
      "scenario": "100k assertions projection"
    },
    {
      "case_id": "OPS-INDEX",
      "expected": "same_answers",
      "mandatory": true,
      "module": "operations",
      "result": "NOT_RUN",
      "scenario": "Delete SQLite index then rebuild"
    },
    {
      "case_id": "OPS-CRASH",
      "expected": "old_snapshot_visible",
      "mandatory": true,
      "module": "operations",
      "result": "NOT_RUN",
      "scenario": "Crash before catalog pointer publication"
    },
    {
      "case_id": "INTEGRATION",
      "expected": "same_structured_report",
      "mandatory": true,
      "module": "integration",
      "result": "NOT_RUN",
      "scenario": "Framework vs diK vs Integration coverage"
    }
  ],
  "status": "test plan, not executed",
  "suite_id": "DIK-1.0-TCK-CANDIDATE"
}
```
