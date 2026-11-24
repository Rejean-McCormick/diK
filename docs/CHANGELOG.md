# Journal des changements documentaires

## DIK-DOCS-LOCAL-1 — 2026-11-22 (documentation uniquement)

- Guide maître + dix chapitres 34 à 43 sur la résolution `KQ/KP + locale`, sans traduction entre langues.
- Carte des ressources locales Spek, Konstellation, GF RGL, GF Lexicons Archive et GF Wikidata, avec niveau de preuve.
- Contrat cible Source Manager, adaptateurs distincts Q/P, L/S/F et GF, sécurité, gouvernance et licence.
- Mesures V3 observées sur 126 Kristals officiels ; 57 évaluables, 69 non évaluables ; pas de fausse couverture.
- ADR DIK-LEX-2 proposé et exemples JSON **non normatifs** ; aucune activation de données par la documentation.

## v0.2.0 — 2026-10-16

- Transformation de la spécification initiale en documentation complète de développement.
- Détail de la distinction KQ/KP/KA/KS, lexicalisation, crosswalk externe, résolution des homonymes.
- Détail des processus d'import Wikidata, de suivi des snapshots et de gestion de 300+ langues.
- Définition des mesures strictes de complétude pour chaque Kristal, dont les cas d'absence et de repli.
- Définition des parcours GUI, du CLI projeté, des contrôles de sécurité et des tests d'acceptation.
- Inclusion de fixtures **non modifiées** issues du Framework v11 draft.3.
- Conservation des décisions et documents v0.1 comme historique.

## v0.1.0 — 2026-10-16

- Première spécification : mission, architecture générale, matrice de complétude, migration non destructive et contrats Framework v11 draft.3.

## 2026-11-22 — diK alpha.8

Le Source Manager local possède désormais une implémentation de découverte et de persistance ; consulter [44](docs/44_SOURCE_MANAGER_V4_IMPLEMENTATION.md), [45](docs/45_COMMANDES_V4_WINDOWS.md) et [46](docs/46_VALIDATION_ET_LIMITES_V4.md). Les anciennes mentions « à développer » représentent l'état historique de la livraison documentaire précédente. L'intégration complète de GF reste à développer.

## 2026-11-23 — V5 / alpha.9

Documentation for read-only qualification of the 5 269 local references, explicit Wikidata QID observations, GF boundaries, security and acceptance criteria: chapters 48–50 and ADR-DIK-LEX-4.


## 2026-11-23 — Spécification du futur lecteur Wikidata V5.3 (documentation uniquement)

Ajouts : chapitres 53–60, ADR-DIK-LEX-6 proposé, exemples d'objets JSONL non normatifs ; mise à jour des entrées et du diagnostic V5.2. Le statut de **l'application** reste V5.2. Aucune activation automatique, aucune traduction entre langues, aucun raccordement GF ou L/S/F présumé.
