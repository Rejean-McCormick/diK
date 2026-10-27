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
