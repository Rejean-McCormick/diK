# ADR — Sélection des révisions déclarées : vue dérivée, non autorité

Date : 2026-11-24. **Accepté pour l'index dérivé V5.11 uniquement ; décision d'autorité Framework en attente.**

## Contexte

`canon/state.index.json` déclare plusieurs artefacts V11 par Kristal mais ne désigne pas une révision active dans les snapshots examinés. Les 180 révisions observées n'ont pas toutes les mêmes identités. Choisir une date, un nom ou le plus grand registre produirait des pertes ou des fusions silencieuses.

## Décision

Conserver toutes les révisions dans la vue de preuve V5.10. Ajouter une sélection de **consultation** limitée aux révisions uniques complètes et aux décisions de revue explicites, épinglées aux SHA-256 de leurs entrées. Une révision multiple sans décision reste non sélectionnée, même si ses labels semblent similaires. Un graphe volontairement non inspecté bloque la sélection. Contrôler les conflits d'exactMatch accepté par identité et refuser le ciblage d'une révision invalide.

L'index dérivé ne devient jamais propriétaire d'un namespace, ne réécrit pas de fichiers Kristal, ne promulgue aucune identité globale, ne remplace pas les crosswalks déjà validés en V5.9 et n'autorise aucune publication. Un document de revue d'opérateur **ne fait pas autorité** sur le canon Framework ; le statut conserve explicitement `derived_view_only`.

## Conséquences

Meilleure visibilité sur les blocages, recherche bidirectionnelle des seules révisions retenues pour consultation, rapports reproductibles et falsifiables par SHA. Les 49 Kristals hors V11 et les vraies décisions d'autorité restent des chantiers séparés. Les consommateurs EncyK, SemantiK et Spek continuent d'exiger leurs validations et portes de publication existantes.
