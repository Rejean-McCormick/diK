# ADR-DIK-LEX-2 — Localiser les ressources existantes avant toute activation

**Date** : 2026-11-22  
**Statut** : **proposition documentaire, non ratifiée**  
**Périmètre** : diK Source Manager, compositeur lexical, audit des 126 Kristals officiels.

## Contexte

Les audits diK V1/V2/V3 ont d'abord mesuré des catalogues v11 trouvés au voisinage des Kristals. Le rapport V3 termine en état `PARTIEL` avec 126 officiels, 57 évaluables, 69 non évaluables et 283 176 couples non résolus. Des index GF et des chemins explicitement décrits dans Spek montrent d'autres ressources lexicales **candidates** qui n'ont pas été qualifiées/activées par V3. Interpréter les cellules non résolues comme des mots à traduire serait une erreur de modèle.

## Décision proposée

1. Faire de la **localisation et du référencement de sources existantes** la priorité de l'intégration suivante.
2. Utiliser un registre **propre à diK** avec états de preuve, chemins, empreintes et licence ; ne pas modifier le schéma normatif Framework.
3. Définir des adaptateurs distincts v11, Wikidata Q/P, Wikidata L/S/F, et GF ; aucun mapping KQ↔GF implicite.
4. Laisser les fichiers à leur place, ne pas copier les lexiques dans 126 Kristals, et ne publier de nouvelle couche que sur décision approuvée.
5. Compter uniquement les Kristals du portefeuille officiel pour le diagnostic linguistique, et traiter séparément copies/staging et sources d'apprentissage.
6. Ne jamais traduire une langue vers une autre ; une forme est résolue directement depuis la même identité canonique.
7. Exiger des traces testables, des résultats partiels explicites et des opérations en lecture seule par défaut.

## Conséquences

- **Positives** : audit plus juste ; réutilisation contrôlée des ressources ; sécurité des IDs ; réduction des doubles comptes ; reproductibilité.
- **Coûts** : inventaire et tests d'adaptateurs ; validation des licences ; revue des crosswalks et des mappages grammaticaux ; gestion des chemins déplacés.
- **Non-objectifs** : générateur de traductions, migration des graphes, publication automatique, téléchargement de dumps sans action explicite.

## Statut d'implémentation

**Non implémenté par cet ADR.** Le moteur V3 a ses limites documentées dans [33](../docs/33_RESOLUTION_IDENTITES_14_LANGUES_OFFICIELLES.md) et le [guide maître](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md). L'acceptation de l'ADR et le développement des lots se font séparément.
