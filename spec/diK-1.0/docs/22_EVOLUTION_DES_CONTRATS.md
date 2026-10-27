# 22 — Versionnement des formats et gestion des changements

## Profil vs version de l'application

- `diK 1.0.0` : version du logiciel cible.
- `dik.compact-projection/1.0` : **profil JSON préexistant** depuis diK 0.3 ; doit rester lisible.
- `kristal_* schema_version=11.0` : contrats **Framework**, et non diK.
- `dik.*` contrats dans `contracts/` de ce dossier : **propositions applicatives** `1.0-candidate`, non norme upstream adoptée.

Ne pas déduire qu'un changement de version de diK permet de changer la signification d'un schéma Framework. Toute rupture de profil doit recevoir un nouveau nom de profil et un adaptateur de lecture.

## Algorithme de comparaison de profils

Pour tout changement : comparer listes de champs/type/nullabilité, contraintes d'identité, hash algorithm, ordre canonique, comportements missing/fallback, provenance et sécurité. Tests de fixtures antigas dans chaque direction permise. Une modification au format de données de sources externes passe par adaptateur Anti-Corruption Layer.

## Gouvernance d'une ADR

Inclure : problème réel, source/contrat existant, options étudiées, changement proposé, tests positifs/négatifs, impact stockage/compatibilité, plan de migration/réversibilité, statut `proposed|accepted|rejected|superseded` et décideur. Une IA peut rédiger l'ADR, pas déclarer acceptée à la place des décideurs.

## Backward compatibility minimale

- Importer/valider les anciennes projections v0.2 verbose et v0.3 compact sans conversion implicite vers un faux canon.
- Lire les Kristals historiques avec adaptateurs explicitement versionnés ; ne pas les réécrire.
- Écrire **uniquement** de nouveaux artefacts conformes à Framework v11 fixé par manifest.
- Préserver registre et crosswalks historiques et leurs décisions.
