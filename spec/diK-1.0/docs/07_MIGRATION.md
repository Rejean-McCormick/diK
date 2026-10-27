# 07 — Migration des Kristals legacy et patches approuvés

## MIG-001 — Découverte des rôles

Parcourir les sources historiques avec **adaptateur de version** qui identifie précisément les rôles sémantiques : sujet, propriété, cible d'entité, qualificateur sémantique. Les champs littéraux, citations, noms de personnes *dans du texte*, corps de document, URLs, références éditoriales ne sont pas des cibles à convertir par remplacement. S'il est impossible d'établir le rôle d'un champ, le laisser `unknown_role` et bloquer l'application.

## MIG-002 — Plan non exécutable Framework

Produire un `kristal_dik_conversion_plan` **conforme au schéma upstream** : source artefact/version/SHA, namespace, catalog/crosswalk, liste d'opérations chacune avec JSON Pointer exact, ancienne valeur, rôle, ID cible, décision `pending|approved|rejected` suivant schéma officiel. Les scores de correspondance restent consultatifs. Aucune opération `pending` ou `rejected` ne s'exécute.

## MIG-003 — Résolution et revue

Ordre de proposition : ID interne déjà connu -> mapping externe accepté/exact et typé -> recherche lexicale contextualisée -> candidats manuels. Vérifier toutes les hypothèses, ambiguïtés et absence de KQ. Créer un nouveau KQ éventuel **via l'autorité d'allocation**, après revue. Ne pas convertir un mot « grâce » automatiquement sans préciser le sens.

## MIG-004 — Exécution par producteur

L'Authoring Kit ou autre producteur autorisé exécute après relecture indépendante : comparer digest octets de l'ancien artefact, JSON pointers et anciennes valeurs, décision approuvée et preuves ; appliquer transactionnellement à une **nouvelle révision**, jamais à la source ; valider le nouveau graphe contre Framework ; conserver journal de conversion et lien de retour. diK ne se déclare pas implicitement producteur du canon.

## MIG-005 — Patch d'édition linguistique

Une vue annotée peut demander une modification sémantique : le système affiche avant/après et identifiants, produit `patch_candidate`, oblige revue. Si seule la traduction change et aucun ID/relation ne change, modifier **une couche curatée**, pas le graphe. Cette bifurcation est essentielle pour éviter la confusion « correction d'un mot » = « changement de sens ».

## MIG-006 — Échecs et reprises

L'opération est idempotente par `(source hash, plan ID/revision, decisions hash, producer version)`. Si une révision a déjà été produite, rendre son adresse ; pas de seconde mutation. En cas de crash pendant staging : révision non visible, rollback et possibilité de relance vérifiée. L'original historique et ses commitments v9 restent inchangés.

## Tests

`MIG-T1` mot dans citation inchangé ; `MIG-T2` JSON Pointer modifié -> rejet ; `MIG-T3` plan avec pending -> rejet ; `MIG-T4` deux sens candidats -> blocage ; `MIG-T5` KS preuve absent -> rejet ; `MIG-T6` source SHA changé -> rejet ; `MIG-T7` commit crée nouvelle révision seulement ; `MIG-T8` rollback crash ; `MIG-T9` ancien graph toujours vérifiable.
