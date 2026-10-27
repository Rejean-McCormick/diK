# diK — Dictionnaires et identités Kristal

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
