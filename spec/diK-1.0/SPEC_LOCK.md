# SPEC LOCK — Verrou de conception anti-drift

**Identifiant :** `DIK-SPEC-1.0-CANDIDATE` · **État :** frozen design target, pas release logiciel.

## Autorités et épinglage

- Framework **11.0.0-draft.3** : `schemas/v11/*.json`, `spec/v11/*.md`, `tools/v11/*.py` dans `Kristal-Framework-v11.0.0-draft.3.zip`. Les SHAs réels sont recensés dans `SOURCE_LOCK.json` généré à partir des archives fournies.
- Implémentation de référence **diK 0.3.0** : `src/dik/{operations,projection,compact,cli}.py`; documentation v0.2 et v0.3 jointe dans cette version de diK.
- Adaptation externe : **Authoring Kit 4.0.0-draft.2**, **Integration Pack 0.2.0-alpha.1**. Aucun changement implicite de leurs contrats n'est autorisé.
- Patterns étudiés : anti-corruption layer, architecture hexagonale, monolithe modulaire, CQRS interne, idempotence, cache-aside, snapshots immuables, strangler fig. Ce sont des **choix de conception diK proposés**, pas des exigences déjà présentes dans le Framework.

## Ordre de précédence

`Framework normatif > profils diK existants (lecture rétrocompatible) > nouveaux contrats diK 1.0 proposés > tutoriels/exemples > intuition de l'IA`.

### Registres de responsabilité

| Ressource | Propriétaire | Peut modifier canon ? |
|---|---|---|
| Registre d'identité, graphe KQ/KP/KA/KS | Framework + producteur autorisé | Seulement nouvelle révision validée |
| Catalogues, couches lexicales, provenance | diK en tant que gestionnaire | Jamais le graphe |
| Crosswalk externe | diK propose / réviseur approuve | Jamais un KQ déjà alloué |
| Projection compact/verbose/markdown | diK | Jamais |
| Index SQLite et caches | diK (dérivés) | Jamais |
| Migration de graphe legacy | Authoring Kit ou producteur agréé | Nouvelle révision, pas ancien artefact |

## Choix expressément ouverts, sans hypothèse silencieuse

- Distribution réseau : facultative ; diK 1.0 doit fonctionner **localement**. L'API proposée est locale par défaut ; mode distant = profil de sécurité séparé.
- Édition linguistique par IA : candidate en brouillon, jamais automatiquement vérifiée.
- Signatures : empreintes SHA assurent l'intégrité accidentelle, **pas l'authenticité** ; une signature cryptographique est une extension si la confiance multi-acteurs l'exige.
- Performance : budgets proposés dans `docs/14_PERFORMANCE.md` doivent être mesurés sur matériel documenté, non présumés satisfaits.
- Compaction et diffusion d'énormes dictionnaires : politique locale configurable, pas réécriture du format Framework.
- Répertoire `contracts/` contient des formats diK *nouveaux* ; ils demandent une gouvernance avant stabilisation du wire format et ne doivent pas être présentés comme schémas Framework.

## Définition de « terminé »

Aucune fonctionnalité n'est dite terminée sans : code, schéma/vérification, cas normaux, erreurs négatives, tests de reprise et de migration, preuves de rétrocompatibilité, revue et documentation. Les TCK `tests/` de cette spécification sont à **implémenter et exécuter** lors du développement ; le dépôt présent ne constitue pas cette exécution.

## Addendum candidate.2 — verrou complémentaire

L'identifiant de cette révision documentaire est `DIK-SPEC-1.0-CANDIDATE.2`. Les choix du profil local définis par [`ADR-0003`](decisions/ADR-0003-PROFIL-LOCAL-1_0.md) sont **proposés**, pas approuvés humainement. L'IA peut les suivre comme baselines techniques pour une branche expérimentale mais ne peut pas déclarer l'API 1.0 stable sans ratification.

En qualification documentaire stricte, toute source Framework/diK manquante échoue ; vérifier les 13 empreintes `SOURCE_LOCK.json` via `--strict`. Un test oracle de cette spécification ne compte pas comme résultat produit diK 1.0. Les IDs normatifs et leurs tests positifs/négatifs sont à conserver dans `tests/requirements.json`.
