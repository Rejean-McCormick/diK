# ADR-DIK-LEX-3 — Le registre de sources locales de diK

**Statut : implémenté comme fonctionnalité expérimentale V4, sans modifier les contrats Framework.**

## Contexte

Une source GF/Wikidata peut être physiquement présente sans être utilisable pour le même identifiant canonique KQ/KP. Les anciens audits V2/V3 confondaient parfois absence de lien et absence de mot ; un balayage de tout `C:\mycode` comptait aussi des copies comme Kristals officiels.

## Décision

Implémenter une découverte ciblée, hors-ligne, persistée sous `diK/reports/resources`, dont chaque entrée est un pointeur et non un dictionnaire activé. Autoriser `resolve14` à consulter les catalogues v11 référencés après validation Framework indépendante, avec des Q/P uniquement par crosswalk révisé. GF demeure une source candidate tant qu'une liaison prouvée et un adaptateur de réalisation ne sont pas disponibles.

## Conséquences

L'utilisateur n'a plus besoin de spécifier à la main **chaque catalogue v11**. Un registre peut être audité et rejoué ; les listes historiques et les chemins Spek restent des pistes, pas des preuves d'existence. Le mapping GF, les droits de publication et la qualification des dumps Wikidata restent à traiter séparément. Aucun réseau, aucune traduction, aucune modification des sources.
