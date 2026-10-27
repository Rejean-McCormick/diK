# 16 — Qualification et publication diK 1.0

## GO / NO-GO

**GO seulement si :** toutes les exigences P0/P1 ont implémentation + preuves ; schémas Framework v11 épinglés ; formats de projection v0.2/v0.3 lus ; import Wikidata massif mesuré ; 301 langues sparse sans incohérence ; tests d'interruption et de sécurité ; migrations legacy produites via producteur autorisé ; graphiques/rapports fiables ; GUI et API documentées ; licence/attribution validées ; archive/package reproductible et installable sans mode réseau obligatoire.

**NO-GO si :** une assertion d'identité provient d'un mot sans revue ; un `Q` entre dans le canon ; une couche curated est écrasée ; `restore` déduit ID depuis `clean.md` ; `100%` inclut missing ; un outil modifie v9 commitments ; un test bloquant est `NOT_RUN` ; le Framework n'est plus identifiable par pin digest ; la reprise d'import perd ou duplique des données.

## Jalons de développement proposés

1. **0.4** : domaine hexagonal, conciliation multisource, revue/provenance, recherche inverse et idempotence.
2. **0.5** : inventaire legacy, plans de conversion, boucle d'intégration Authoring, édition linguistique/patch distincts.
3. **0.6** : miroir Wikidata, import/deltas/reprises, index durable rebuildable, 300+ locales et jeux massifs.
4. **0.8** : API CLI stabilisées, UI, rôles/audit, sécurité et accessibilité.
5. **0.9 RC** : TCK complet, benches ratifiés, compat Framework/Auth/Integration, audit de licences, guide opérateur.
6. **1.0.0** : artefacts reproductibles, release signée si la gouvernance l'exige, notes de migration, document d'écarts nul ou approuvé.

Ces numéros sont **planifiés**, pas livrés. Stabiliser Framework v11 séparément si draft.3 change ; pin de la release doit figer un artefact exact et son digest.

## Pièces obligatoires de la release

- SBOM dépendances + licences, CHANGELOG, MIGRATION_GUIDE, manifeste SHA-256, versions de schémas & API, rapport TCK avec tests NOT_RUN distingués, matrice couverture KQ/KP langues, benchmark machine/commandes, tests de restauration de snapshots.
- Guide sécurité, plan sauvegarde/restauration, politiques d'import, limites connues et décision de compatibilité cross-repo.
- Un paquet installable, CI reproductible, jeux d'exemples non fictivement certifiés, journal des exceptions.

## Changement de norme Framework

Une nouvelle draft du Framework ne modifie pas unilatéralement `diK 1.0`. Ouvrir ADR, comparer schémas, choisir une migration de profil/version, recréer golden fixtures, vérifier anciennes projections/crosswalks ; seule une nouvelle release compatible pourra utiliser le nouveau pin.

## Addendum candidate.2 — blocage de la version stable

La release est refusée si `tests/requirements.json` contient une exigence sans **deux** preuves exécutées (positive et négative), si `tests/TCK_CASES.json` conserve un `NOT_RUN` bloquant, si la validation `--strict` échoue ou si un artefact de D2/D3 de `docs/25_GATES_CI_EXECUTABLES.md` manque. Les décisions et budgets non ratifiés sont marqués explicitement comme `BLOCKED` et non comme valeurs par défaut approuvées.
