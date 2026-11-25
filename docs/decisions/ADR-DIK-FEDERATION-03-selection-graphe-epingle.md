# ADR — SHA du graphe requis pour la sélection dérivée `/0.2`

Date : 2026-11-24. **Décision d'implémentation diK (vue dérivée uniquement).**
Ne crée aucune décision d'autorité Framework et aucune approbation de mapping.

## Problème

Le profil candidat `dik.canonical-selection-decisions/0.1` épinglait l'index,
le registre, le crosswalk et le catalogue, mais pas `graph_sha256`. Le lecteur
V5.11 mesurait déjà cette empreinte. Une substitution du seul fichier de
graphe, avec index et trois autres artefacts inchangés, pouvait donc conserver
une décision de sélection destinée à d'autres octets.

## Décision

- Introduire `dik.canonical-selection-decisions/0.2`, exigeant les **cinq** SHA-256
  de l'index, du registre, du crosswalk, du graphe inspecté et du catalogue.
- Vérifier le SHA du graphe exact dans `canonical_revision_inputs` avant
  `OPERATOR_PINNED_DERIVED_VIEW` ; bloquer sur toute divergence.
- Refuser explicitement les anciens fichiers de décisions `/0.1` lors d'une
  **nouvelle** construction. Les fichiers et registres déjà produits ne sont
  pas réécrits ni déclarés rétroactivement qualifiés.
- Ajouter `graph_sha256` à la file d'options de revue, sans choisir une
  révision, un QID, une langue ni un `exactMatch`.

## Repli et compatibilité

Le profil `/0.1` demeure documenté comme historique. Le passage à `/0.2`
nécessite une revue explicite des nouvelles empreintes ; aucune conversion
silencieuse d'une décision humaine n'est autorisée. Les identités restent
`(namespace_id, KQ/KP)`. Le Framework `11.0.0-draft.4`, ses schémas et les
sources du Kristal restent inchangés. Aucun traitement de publication ou
d'admission de dictionnaire n'est déclenché.

Tests positifs/négatifs : `tests/test_selection_graph_pin_v02.py` et
`tests/test_canonical_selection_v511.py`.
