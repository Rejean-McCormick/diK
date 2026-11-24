> **État V5.7 / alpha.15 :** 14 dictionnaires SQLite candidats via EncyK local, chapitre [65](docs/65_COLLECTION_LOCALE_14_LANGUES_ENCYK_V5_7.md). Les chapitres historiques conservent leur contexte.

> **État logiciel au 23 novembre 2026 :** le code V5.6 (`1.0.0-alpha.14`) ajoute un Source Manager en ligne ciblé Wikidata. Les mentions ci-dessous de « code V5.2 » sont des notes **historiques** datées de la livraison documentaire V5.3. Voir [chapitre 64](docs/64_SOURCE_MANAGER_EN_LIGNE_CIBLE_WIKIDATA_V5_6.md).

# diK — Dictionnaires et identités Kristal
<!-- DIK-DOCS-LOCAL-1 -->
> **Note documentaire du 23 novembre 2026 :** le code livré demeure V5.2 (`1.0.0-alpha.10`) ; les chapitres 53–60 spécifient seulement V5.3 et ne sont pas une nouvelle livraison logicielle.
>
> **Mise à jour transversale (22 novembre 2026)** : la phrase historique « l'application n'est pas livrée » décrit la spécification v0.2.0 d'octobre ; elle ne décrit **pas** l'installation diK V3 observée en novembre. Voir [guide maître DIK-DOCS-LOCAL-1](DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md), chapitres 34–43, pour la résolution par identifiants sans traduction, la carte des ressources GF/Wikidata et les limites actuelles. Cette documentation n'active pas les sources.


**Documentation de conception et de développement — v0.2.0 (2026-10-16).**  
**Statut : spécification du futur logiciel. L'application diK n'est pas livrée dans cette archive.**  
**Référence normative : Kristal Framework `11.0.0-draft.3`, schémas `schemas/v11/`.**

## En une phrase

diK gère les dictionnaires multilingues de Kristal, rapproche plusieurs sources lexicales (dont Wikidata), vérifie la couverture des **identifiants sémantiques réellement employés** par chaque Kristal dans toutes les langues retenues et prépare une migration **contrôlée, réversible et non destructive** des anciens graphes utilisant des mots au lieu d'identifiants.

## Décision structurante

- **Identité canonique :** `(namespace_id, KQ…)` pour les référents, `(namespace_id, KP…)` pour les propriétés ; `KA…` identifie les assertions, `KS…` les sources.
- **Lexique :** `identifiant canonique + langue + domaine + source → libellé(s)` ; les mots ne servent jamais de clés d'identité du graphe.
- **Alignement :** `KQ↔Wikidata Q` / `KP↔Wikidata P` via un **registre distinct de correspondances typées et révisées**. Deux nombres identiques après des préfixes différents ne prouvent aucune identité.
- **Sources :** imports gelés, modifications locales révisées, priorités déterministes, provenance et droits de réutilisation.
- **Migration :** le mot est une **requête de résolution**, pas un résultat sûr ; aucun remplacement automatique des citations, textes documentaires ou valeurs littérales.

### Architecture en 5 blocs

```text
    Kristals historiques / canoniques
                |              \
        inventaire des IRS      résolution des mots
                |                       |
          couverture             candidats → revue → plan
                |                       |
      +---------+----------+------------+----+
      |         MOTEUR diK : validation       |
      |  lexicalisation, alignement, audit    |
      +---------+----------+------------+----+
                |          |             |
        dictionnaires   crosswalks    registres
         par langue    Wikidata Q/P    KQ/KP/KA/KS
                |          |             |
         Wikidata local, terminologies, curation

      Sorties : rapports versionnés + plans non exécutables
      Application de migration : Authoring Kit (future intégration)
```

## Sommaire de la documentation

| Document | Objet |
|---|---|
| [01 Vision et périmètre](docs/01_VISION_ET_PERIMETRE.md) | Objectifs, non-objectifs, définitions et garanties |
| [02 Architecture](docs/02_ARCHITECTURE.md) | Composants, responsabilités, stockage et flux |
| [03 Modèle d'identité](docs/03_IDENTITES_ET_ALIGNEMENTS.md) | KQ/KP/KA/KS, namespace, correspondances Wikidata |
| [04 Gestion des dictionnaires](docs/04_DICTIONNAIRES_ET_LANGUES.md) | 300+ langues, couches, priorité et édition |
| [05 Wikidata et sources](docs/05_IMPORT_WIKIDATA_ET_SOURCES.md) | Téléchargement, import local, mises à jour, droits |
| [06 Complétude](docs/06_COMPLETUDE_ET_AUDIT.md) | Mesures, matrice, seuils, états, agrégation |
| [07 Conversion](docs/07_CONVERSION_LEGACY.md) | Désambiguïsation, plan, revue, application future |
| [08 UX et parcours](docs/08_INTERFACE_ET_PARCOURS.md) | Écrans, navigation, validations et interactions |
| [09 CLI, API, événements](docs/09_CLI_API_ET_INTEROPERABILITE.md) | Interface produit proposée et contrats Framework existants |
| [10 Sécurité et gouvernance](docs/10_SECURITE_QUALITE_GOUVERNANCE.md) | Immutabilité, rôle des réviseurs, licences, confidentialité |
| [11 Tests d'acceptation](docs/11_TESTS_ET_ACCEPTATION.md) | Tests de non-régression et critères de livraison |
| [12 Roadmap](docs/12_ROADMAP_ET_DEPENDANCES.md) | Ordre de réalisation, versions, autres repos |
| [13 Glossaire](docs/13_GLOSSAIRE_ET_EXEMPLES.md) | Terminologie et cas concrets |
| [14 Décisions en suspens](docs/14_DECISIONS_OUVERTES.md) | Questions à trancher explicitement |
| [15 Repos déjà disponibles](docs/15_DEPOTS_ET_DEPENDANCES.md) | Snapshots connus et rôles |
| [17 Projections réversibles](docs/17_PROJECTIONS_BIDIRECTIONNELLES.md) | Lecture dans une langue, retour canonique, garanties et limites |
| [16 Traçabilité](docs/16_MATRICE_DE_TRACABILITE.md) | Exigence → schéma → test |
| [ADRs historiques](decisions/ADR-HISTORIQUE-v0.1.md) | Décisions déjà prises et conservées |

Le dossier [`examples/framework-v11-draft3/`](examples/framework-v11-draft3/) contient des **exemples copiés sans modification** depuis le Framework. Ils sont illustratifs et ne réservent aucun identifiant de production.

Pour commencer à développer : [Démarrage rapide](DEMARRAGE_RAPIDE.md). Journal de versions : [CHANGELOG](CHANGELOG.md).

## Compatibilité réelle vs objectif

**Déjà présent dans Framework draft.3 :** schémas d'identité, graphes, catalogues, couches lexicales, correspondances, rapports de complétude et plans de conversion ; validateurs hors-ligne et outils de référence.

**À développer dans diK :** application CLI/UI, gestion structurée de projets, import Wikidata à grande échelle avec reprise, moteur de conciliation multiréférentiel, index de recherche inverse, audit de 300 langues et workflows de revue.

**À développer dans Authoring Kit :** exécution *transactionnelle* et autorisée d'un plan approuvé vers un **nouveau Kristal**, avec conservation des engagements antérieurs. Aucun plan diK ne confère en lui-même ce droit.

## Priorité recommandée

1. Intégrité d'identité, provenance et couche lexicale : **d'abord**.
2. Audit/complétude fiable : **ensuite**.
3. Conciliation et migration contrôlée : **après**.
4. Optimisation 300+ langues et import massif : **sans fragiliser le canon**.

La documentation vise un code maintenable et testable, **pas une reprise littérale de chaque exemple**. En cas de contradiction, le Framework v11 spécifie les formats interopérables ; un changement incompatible exige un nouveau contrat versionné.

## Ajouts transversaux 2026-11-22

Voir [le guide maître](DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md) pour l’index complet des nouveaux chapitres 34 à 43, les modèles de manifestes et l’ADR DIK-LEX-2.

## Mise à jour moteur V4 (alpha.8)

**Le localisateur de ressources est maintenant réellement implémenté** (contrairement au contrat cible décrit dans la livraison documentaire de novembre) : `dik sources discover|verify`, registre daté sous `reports/resources` et option `dik coverage resolve14 --resource-registry`. Il découvre et pointe les fichiers, mais ne confère **aucune** autorité lexicale à un GF ou JSONL sans mapping accepté. Voir [44](docs/44_SOURCE_MANAGER_V4_IMPLEMENTATION.md), [45](docs/45_COMMANDES_V4_WINDOWS.md), [46](docs/46_VALIDATION_ET_LIMITES_V4.md).

## Distribution V4.1 revue

Lire [47 — Revue et limites du paquet V4 révisé](docs/47_REVUE_PACK_V4_1.md) avant une installation Windows. Les manifestes historiques `RELEASE*` ne désignent pas la distribution V4.1.

## V5 — Qualification des ressources réellement localisées (alpha.9)

Voir [48 — qualification](docs/48_QUALIFICATION_SOURCES_REELLES_V5.md), [49 — QID et GF](docs/49_OBSERVATIONS_QID_ET_LIMITES_GF_V5.md), [50 — plan de travail](docs/50_FEUILLE_DE_ROUTE_DIAGNOSTIC_REGISTRE_V5.md) et [ADR-DIK-LEX-4](decisions/ADR-DIK-LEX-4-qualification-avant-activation.md). La qualification n’active aucune source et ne traduit aucune langue.


## V5.1 — Schéma QID JSONL vérifié (2026-11-23)

- [51 — Format réel QID JSONL et limites](docs/51_FORMAT_REEL_QID_JSONL_V5_1.md)
- [49 — Observations QID/GF actualisées](docs/49_OBSERVATIONS_QID_ET_LIMITES_GF_V5.md)
- Ce schéma est maintenant reconnu en lecture seule, **sans activer la source ni traduire entre langues**.


## V5.2 — Raccordement thématique prudent (2026-11-23)

- [52 — Audit Wikidata thématique et raccordement candidat](docs/52_AUDIT_WIKIDATA_THEMATIQUE_V5_2.md)
- [ADR-DIK-LEX-5 — Pas d'activation implicite](decisions/ADR-DIK-LEX-5-jsonl-thematiques-en-candidats.md)
- [51 — Lecteur QID JSONL réel](docs/51_FORMAT_REEL_QID_JSONL_V5_1.md)

Les schémas locaux Wikidata ne sont pas tous validés. La V5.2 les inspecte et produit des observations non publiées, sans modifier les Kristals.


## V5.3 — Spécification du nouveau système de lecture (2026-11-23)

**Documentation cible, non implémentée** : le diagnostic V5.2 a retrouvé 40 sources Wikidata thématiques, dont 37 inspectées et 2 tronquées ; 0 Q/P reconnu par le lecteur actuel **ne prouve pas** l'absence de Q/P réels.

- [53 — Diagnostic V5.2 vérifié et objectifs V5.3](docs/53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md)
- [54 — Architecture des lecteurs et jointures sans traduction](docs/54_ARCHITECTURE_LECTURE_WIKIDATA_V5_3.md)
- [55 — Profils de schémas et adaptateurs JSONL](docs/55_CONTRATS_SCHEMAS_JSONL_V5_3.md)
- [56 — Lecture streaming, reprise et intégrité](docs/56_STREAMING_REPRISE_SECURITE_V5_3.md)
- [57 — Preuves KQ/KP ↔ Q/P et limites GF/L/S/F](docs/57_PREUVES_KQ_QP_LSF_GF_V5_3.md)
- [58 — Statuts et rapports proposés](docs/58_STATUTS_ET_RAPPORTS_V5_3.md)
- [59 — Plan d'implémentation et tests pour le prochain prompt](docs/59_PLAN_IMPLEMENTATION_TESTS_V5_3.md)
- [60 — Périmètres GF et Kristals non évaluables](docs/60_FRONTIERES_GF_ET_KRISTALS_NON_EVALUABLES.md)
- [ADR-DIK-LEX-6 — Décision proposée](decisions/ADR-DIK-LEX-6-lecteurs-schemas-reprise-sans-activation.md)
- [Exemples JSONL non normatifs](examples/wikidata-v5_3/README.md)

Le logiciel **reste V5.2** ; ce pack ne remplace aucun module Python et n'active aucune ressource.


- [61 — Implémentation effective V5.3 : lecture JSONL, reprise, limites](docs/61_IMPLEMENTATION_EFFECTIVE_V5_3.md)


### V5.5 — Implémentation de l'adaptateur GF-Wikidata à tableaux JSON

[Chapitre 63 — GF-Wikidata, tableaux JSON réels et règles de preuve](docs/63_ADAPTATEUR_GF_WIKIDATA_TABLEAUX_JSON_V5_5.md) — code livré, validation des quatre fichiers, mise en garde sur les langues et publication.

### V5.8 — Sens et preuves EncyK

Voir [chapitre 66 — Pont des preuves EncyK](docs/66_PONT_ENCYK_PREUVES_DE_SENS_V5_8.md)
pour le schéma fédéré, les commandes, la séparation candidat/approuvé
et les limitations des ancrages v0.6 échantillonnés.

> **V5.11 / 24 novembre 2026 :** [chapitre 70 — sélection contrôlée des révisions](docs/70_SELECTION_REVISIONS_CANONIQUES_V5_11.md). Ce chapitre décrit un **index dérivé non normatif**, pas une élection officielle des révisions Framework ni une admission des 12 919 liens sources. Lire aussi `docs/decisions/ADR-DIK-FEDERATION-02-selection-revisions-derivee.md`.
