# diK alpha.3 — Conciliation lexicale explicable

Statut : **implémentation alpha**, complément applicatif au Framework v11 draft.3, pas un contrat normatif nouveau du Framework.

## Objectif et autorité

Pour une langue donnée, diK rapproche les observations de dictionnaires distincts sur un même KQ/KP, ou signale les termes ambigus employés pour des KQ/KP distincts. Il **ne fusionne jamais d'identités**. Seul le Framework définit le sens des IDs, du catalogue et des priorités. diK lit un **index dérivé** créé à partir des couches lexicales à SHA-256 vérifiés.

Les désaccords observés ne sont pas tous des erreurs : « Saint Augustin » peut être un libellé de présentation préférable à « Augustin d'Hippone », sans rendre l'un des deux faux. En présence de deux identifiants KQ distincts portant le mot « grâce », diK **ne conclut pas** qu'ils désignent le même concept.

## Règles fixées

1. `competing_preferred` : au moins deux `preferred_term` distincts (normalisation Unicode NFC seulement) pour **un même** couple KQ/KP et langue. L'index stocke la catégorie et ses observations de provenance.
2. `shared_term` : un terme identique NFC présent dans les couches d'au moins deux identifiants de **même famille KQ ou KP**, dans le même namespace et la même langue. Les alias comptent comme signaux d'ambiguïté, pas comme identités.
3. Une priorité de couche supérieure est une **préférence d'affichage**. Elle ne constitue ni une vérité démontrée ni un vote de réconciliation.
4. Une traduction de repli (ex. `fr-CA → fr`) reste un repli : elle n'est pas reclassée comme traduction directe. Les analyses de conflits directs n'importent pas les langues de repli.
5. Chaque observation conserve `layer_id`, `priority`, `source_kind` et provenance de snapshot. L'index lui-même n'est pas source d'autorité.
6. Tous les rapports sont **lecture seule**, y compris leurs endpoints Web. Ni `exactMatch`, ni allocation KQ/KP, ni écriture dans un Kristal n'en découle.
7. Les correctifs facultatifs passent par `curate publish` ou la fiche de concept dans l'atelier : **nouveau catalogue candidat**, jamais remplacement de l'existant. Les acteurs ne sont pas authentifiés dans cette alpha.

## Formats et commandes

Construire l'index **avec alpha.3** (les index précédents doivent être reconstruits) :

```bash
 dik index build --project examples/demo/dik.project.json --output /tmp/dik-index-alpha3.sqlite
 dik dictionaries conflicts --project examples/demo/dik.project.json --index /tmp/dik-index-alpha3.sqlite --locale fr
 dik dictionaries compare --project examples/demo/dik.project.json --index /tmp/dik-index-alpha3.sqlite --locale fr --id KQ1001
 dik dictionaries conflict-detail --project examples/demo/dik.project.json --index /tmp/dik-index-alpha3.sqlite --locale fr --kind KQ --type competing_preferred --key KQ1001
```

API locale : `/api/conciliation?locale=fr&page=1`, `/api/variants?id=KQ1001&locale=fr`, `/api/conciliation/detail?locale=fr&kind=KQ&type=competing_preferred&key=KQ1001`.

Dans l'atelier, la liste de conflits apparaît dans le parcours **Concepts et traductions** et les sources détaillées sous la fiche de concept. La navigation principale reste orientée par tâches, comme le recommande le guide UX utilisé pour alpha.2.

## Performance et limites

Les catégories sont calculées **une seule fois** à la création de l'index SQLite, puis consultées de façon paginée (`page_size` 1–100, 10 par page dans l'interface). Les consultations ne chargent pas toutes les langues ni toutes les couches lexicales en mémoire. La fiche d'un conflit retourne au maximum 200 observations et signale une troncature. Toute modification du catalogue, du registre ou du crosswalk rend l'index obsolète.

La recherche est volontairement exacte en NFC : **pas de similarité probabiliste**, de fusion automatique, de preuve d'équivalence, de détection linguistique sophistiquée, de comparaison sémantique de définitions, ni de benchmark sur million d'entités. Les contrôles de fraîcheur s'appuient sur les empreintes des fichiers du projet au moment de l'indexation; les couches de dictionnaires sont vérifiées à la construction de l'index.

## Tests obligatoires

`tests/test_conciliation.py` vérifie la provenance et le désaccord KQ1001, l'isolation namespace/langue/famille, la pagination, l'homonymie de deux KQ, le rejet des index obsolètes et le rendu/API Web sans écriture canonique. Pour toute évolution, ajouter à la fois un cas positif et négatif sans réduire les tests historiques.
