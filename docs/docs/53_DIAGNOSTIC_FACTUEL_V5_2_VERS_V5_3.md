# 53 — Diagnostic factuel V5.2 et périmètre du futur système V5.3

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Document de conception — 2026-11-23. Non implémenté.**  
**Base de preuve :** `DIK_V5_2_BILAN_20261123T143508Z.zip`, notamment `RESOLUTION_20261123T143503Z/rapport.json`, `wikidata_thematic_sources.csv`, `wikidata_thematic_observations_candidates.csv` et le rapport de qualification. Les chiffres ci-dessous décrivent **cette exécution locale**, pas une propriété permanente de diK.

## 1. Invariant métier

diK ne traduit pas une langue vers une autre. Il résout la clé `(namespace_id, KQ/KP, locale)` vers une forme explicitement attestée. Une ressource linguistique est référencée à son emplacement existant et reste inactive tant que provenance, droits et correspondances ne sont pas qualifiés. `KQ…` et `KP…` ne sont pas interchangeables avec `Q…` et `P…` ; un `L…`, `S…` ou `F…` de Wikidata nécessite un contrat distinct ; une fonction GF n'est pas un QID.

## 2. Mesures V5.2 réellement observées

| Objet | Valeur | Lecture correcte |
|---|---:|---|
| Kristals officiels découverts | 126 | Portefeuille `kristal-public/kristals`, non les 1 153 dossiers historiques |
| Kristals v11 évaluables | 57 | Dénominateur de couverture connu ; 69 restent non évaluables |
| Références locales découvertes | 5 269 | 12 racines accessibles ; ce ne sont pas 5 269 dictionnaires activés |
| Sources `wikidata_thematic_candidate` | 40 | 36 JSONL locaux (`identity-candidates`, `statements`) et 4 ensembles GF-Wikidata |
| Sources thématiques réellement inspectées | 37 | Trois copies identiques dédupliquées |
| Lignes thématiques lues | 333 849 | Dont deux sources arrêtées après 150 000 lignes chacune |
| Sources signalées `no_accepted_qp_overlap` | 35 | **Non probant** quand le schéma Q/P n'a pas été reconnu |
| Sources tronquées | 2 | `City.jsonl`, `University.jsonl` ; jamais conclure à une absence exhaustive |
| Q/P reconnus par le lecteur thématique | 0 | Peut être dû au parseur ; **pas** preuve qu'il n'y a aucun Q/P dans les fichiers |
| Q/P acceptés dans les crosswalks officiels | 1 776 | Liens acceptés selon l'audit existant, pas autant de libellés |
| Cellules ID–langue évaluées | 294 364 | 21 026 identifiants comptés par Kristal × 14 locales |
| Formes résolues | 11 188 | 11 175 catalogues courants + 13 catalogues raccordés |
| Cellules non résolues | 283 176 | Pas des « traductions manquantes » |
| Nouvelles observations thématiques publiées | 0 | Aucune activation en V5.2 |

Le statut d'exécution reste `PARTIEL`. La V5.2 a **terminé le processus**, mais n'a pas démontré une lecture sémantique complète des 40 sources.

## 3. Diagnostic : problème de *détection de schéma*, avant celui du recoupement

Dans V5.2, `_explicit_row` attend notamment `qid` / `id` ou une clé externe `Q123` / `P456` contenant un objet de locales. Un fichier de déclarations, un candidat d'identité ou un objet Wikidata thématique peut porter son identité dans un **autre champ, conteneur ou chemin**. Si aucun Q/P n'est extrait, l'étiquette `no_accepted_qp_overlap` est ambigüe et **ne doit pas être reconduite telle quelle**.

Le système V5.3 doit séparer :

1. fichier vérifié et lisible ;
2. schéma détecté et validé (ou inconnu) ;
3. identifiant Q/P extrait par une règle documentée ;
4. Q/P retrouvé ou non dans les liens *déjà acceptés* ;
5. présence éventuelle d'un champ lexical explicite de la locale demandée ;
6. éligibilité de la source et décision de publication, **séparées de l'observation**.

**Aucune absence d'intersection n'est démontrée tant que l'étape 3 n'a pas réussi sur un ensemble intégralement parcouru.**

## 4. Ce qui existe / ce qui est seulement spécifié

| Composant | V5.2 (observé dans le dépôt et le bilan) | V5.3 (cible documentaire, à coder après approbation) |
|---|---|---|
| Source Manager | Découverte, chemins, empreintes, qualification en triage | Profils de schéma versionnés et connecteurs configurés |
| QID → libellés | Lecteur de deux schémas explicites, candidats non publiés | Maintenu, validé avec régressions |
| JSONL thématiques | 40 ciblés, inspection bornée, 37 réellement lus | Lecteurs typés par famille + compteurs discriminants |
| Grands fichiers | Limite 150 000 lignes / fichier, `truncated` | Parcours complet ou arrêt explicite avec reprise reproductible |
| Crosswalk KQ/KP ↔ Q/P | `exactMatch accepted` avec pièces KS, par namespace | Contrôle toujours obligatoire ; aucune acceptation automatique |
| GF, Wikidata L/S/F | Observés ou candidats, pas d'alignement universel prouvé | Contrats séparés après V5.3, pas de fusion implicite |
| Publication | 0 source activée | Toujours interdite sans revue des preuves, droits et autorisations |

## 5. Frontières de travail

**Inclus dans la prochaine étape de code** : profilage et lecture hors-ligne des sources thématiques, lecture progressive avec reprise, détection de collisions et de données ambiguës, recoupement sur Q/P acceptés, rapports reproductibles ; aucun comptage candidat dans la couverture.

**Hors du prochain lot** : inventer de nouveaux KQ/KP, convertir les 69 Kristals non évaluables, compléter par inférence des liens GF ou L/S/F, traduction automatique, import réseau de dumps entiers, publication de dictionnaires tiers. Ces chantiers demeurent tracés, mais n'empêchent pas de réparer les lecteurs.

## 6. Source de vérité et non-régression

- Le *Framework v11* et ses validateurs définissent les formats canoniques. Les exemples de diK ne les remplacent pas.
- Le rapport V5.2 est le **baseline des tests de non-régression**, pas un chiffre cible de couverture.
- Les **14 locales exactes** sont `en,fr,es,de,nl,sv,da,no,nn,fi,et,af,it,pt`. Ne jamais ajouter `nb` à ce dénominateur, ni rabattre `no` sur `nn` ou `nb` sans politique explicite.
- Ce chapitre ne modifie ni le scanner ni les sources ; le futur code devra fournir ses propres preuves Windows.

**Suite de lecture :** [54 — architecture](54_ARCHITECTURE_LECTURE_WIKIDATA_V5_3.md) ; [55 — schémas](55_CONTRATS_SCHEMAS_JSONL_V5_3.md) ; [56 — parcours](56_STREAMING_REPRISE_SECURITE_V5_3.md) ; [57 — alignements](57_PREUVES_KQ_QP_LSF_GF_V5_3.md) ; [58 — rapports](58_STATUTS_ET_RAPPORTS_V5_3.md) ; [59 — plan d'implémentation](59_PLAN_IMPLEMENTATION_TESTS_V5_3.md).
