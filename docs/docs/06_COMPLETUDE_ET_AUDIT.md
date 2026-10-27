# 06 — Complétude lexicale et rapports

## Question centrale

> Pour ce Kristal, est-ce que **tous les identifiants sémantiques employés** sont affichables **dans chacune** des langues choisies, directement et/ou via un repli déclaré ?

La réponse a deux dénominateurs : **KQ** (entités/concepts) et **KP** (prédicats et qualificatifs). Les familles `KA/KS` sont vérifiées pour leur intégrité référentielle, **pas considérées automatiquement comme des mots à traduire**.

## Inventaire et unités de compte

L'inventaire KQ prend les **identifiants distincts du graphe**, y compris les entités dans ses déclarations. L'inventaire KP inclut les propriétés déclarées et les qualificateurs. L'implémentation doit utiliser le contrat du Framework pour décider exactement comment gérer déclarations, listes et répétitions. Les occurrences peuvent servir à classer les lacunes, mais **ne gonflent pas le dénominateur** des KQ/KP distincts.

Pour toute paire `(locale, famille)`, attribuer exactement un statut par ID :

- `direct` : libellé dans cette langue, issu d'une couche acceptée sans conflit.
- `fallback` : libellé trouvé **dans une autre langue explicitement autorisée par repli**.
- `missing` : aucune forme acceptable.
- `conflicted` : choix impossible à cause d'un conflit bloquant.

Pour `N = direct + fallback + missing + conflicted`, et `N > 0` :

`couverture_directe = direct / N` ; `couverture_utilisable = (direct + fallback) / N`.

**Cas N=0** : utiliser l'état `non applicable / aucun identifiant utilisé` (ne pas créer artificiellement 100 % de traduction). **Cas langue déclarée sans données et N>0** : couverture 0 %. Dans le contrat v11, les flags `complete_direct` et `complete_usable` concernent simultanément **KQ et KP**, sans assimiler les deux comptes.

## Couverture simultanée de toutes les langues

En plus des taux par locale, le rapport contient `all_locales.direct.{KQ,KP}` et `all_locales.usable.{KQ,KP}` : nombre de référents couverts **dans chacune des langues sélectionnées**, non somme des couvertures individuelles. La liste des locales doit être non vide et connue du catalogue.

## Exemple sur le Framework

Avec l'exemple livré dans `examples/framework-v11-draft3/`, le graphe utilise **2 KQ et 1 KP** :

| Langue | KQ directs | KQ repli | KQ manquants | KP directs | KP manquants |
|---|---:|---:|---:|---:|---:|
| fr | 1 | 0 | 1 | 0 | 1 |
| en | 1 | 0 | 1 | 0 | 1 |
| fr-CA | 0 | 1 | 1 | 0 | 1 |

Le repli `fr-CA → fr` ne donne donc **aucun** KQ traduit directement en français canadien. Cet exemple est extrait du rapport Framework, non une mesure de corpus réel.

## Sûreté de la mesure

Un Kristal ancien avec des champs identitaires rédigés en mots n'a pas encore d'inventaire canonique exhaustif : le résultat `100 %` est **interdit** ; produire à la place `audit d'identités incomplet` et une liste des champs à traiter. Le rapport doit porter `namespace`, `graph_id`, `graph_sha256`, `catalog_id`, `catalog_sha256`, et être reproductible.

Les pourcentages de **couverture de Wikidata** (KQ reliés à des Q) sont un autre rapport. Une absence de Q externe n'est ni une absence de sens ni une absence de traduction locale.

## Agrégation entre plusieurs Kristals — extension diK

Proposer trois lectures sans les mélanger :

1. **Par Kristal** : chaque graphe et chaque locale, périmètre explicite.
2. **Union des identités** : KQ/KP distincts dans le même namespace, sans compter deux fois le même ID partagé.
3. **Portefeuille** : Kristals de namespaces différents ; compte séparé et consolidation statistique sans fusionner les `KQ` homonymes.

Les rapports multi-Kristals constituent une **extension produit de diK** : le schéma actuel `kristal_dik_coverage_report` est centré sur **un graphe**. Ajouter un manifeste d'agrégation versionné au lieu de modifier en silence le contrat v11 draft.3.

## Exports proposés

JSON machine conforme à `kristal_dik_coverage_report`, CSV par langue et par identifiant (vue de présentation), matrice UI, JSONL des manques très volumineux avec empreintes. Toujours conserver l'état exact du graphe et du catalogue ayant servi au calcul.
