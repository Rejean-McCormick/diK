# 06 — Projections linguistiques réversibles

## PRJ-001 — Contrat des trois vues

- **Canonique** Framework v11 : KQ/KP/KA/KS + assertions/littéraux/qualificatifs/sources, aucun label servant d'identité.
- **Compact enrichi** diK `dik.compact-projection/1.0` (existant v0.3) : `canonical_graph` **une fois**, table `lexicon.entries` dédupliquée par ID, `anchors`, `digests` et locale. Représentation dérivée réversible, non un nouveau canon.
- **Lecture Markdown** `annotated|clean` : générée à la demande à partir de compact/verbose, jamais preuve de restauration. `clean` masque les IDs traduits à l'affichage, sans supprimer les IDs du JSON. IDs non traduits restent visibles pour signaler la lacune.

## PRJ-002 — Règles de réversibilité

La restauration extrait le graphe conservé et compare structure/hashes/ancres ; **aucun reverse lookup des mots**. En mode robuste, vérifier aussi le graphe, registre, catalogue, crosswalk et couches d'origine. Sans projet source/ancres authentifiées, les hashes auto-déclarés ne prouvent pas l'origine ; répondre `integrity_consistent` et non `authentic`.

Invariant formel : pour tout graphe canonique valide `G`, locale déclarée `L`, dictionnaires fixés `D`, si `E = export(G,L,D)` alors `restore(E) = G` selon sérialisation canonique normalisée et **égalité structurelle des données**. Le rendu libre `Markdown(E)` ne sert pas d'entrée à `restore`.

## PRJ-003 — Portée du lexique

Références couvertes : KQ entités et KP prédicats/qualificateurs ; KS/KA sont conservés mais leur dénomination n'est pas comptée comme couverture KQ. La table lexicale est indexée par identifiant **dans un namespace fixé et ancré**. En projet multi-namespace futur, les clés de table devront porter le namespace ou employer des namespaces isolés par enveloppe — jamais fusionner deux `KQ1001`.

## PRJ-004 — Bords importants

- Valeurs littérales/texte cité préservés octet logiquement (Unicode identique ; sérialisation JSON peut différer en whitespace).
- Fallback `fr-CA -> fr` explicitement marqué `fallback`, pas `direct`.
- Libellé inexistant = `null`, status `missing`, pas traduction plausible inventée.
- XSS/Markdown injection : sortie échappée, pas exécution HTML arbitraire.
- Le vocabulaire peut être mis à jour ultérieurement, mais une vieille enveloppe reste liée à ses versions/hashes ; une nouvelle projection devient une **nouvelle vue**, sans modifier son canon.
- La restauration refuse un graphe non conforme au profil attendu même si son hash interne a été recalculé.

## PRJ-005 — Compatibilité

Lire et vérifier `dik.compact-projection/1.0` et l'ancienne projection `verbose` v0.2 ; ne pas changer rétroactivement leur définition. Pour les rendre plus robustes : enveloppe externe versionnée optionnelle, sans altérer l'ancienne structure. Ne pas supprimer `--format verbose` avant décision de dépréciation publiée et tests de non-régression.

## PRJ-006 — Édition

Un utilisateur qui modifie un texte en mode `clean` ne crée pas un nouveau KQ ni une nouvelle assertion. L'éditeur lié au canon doit créer un **patch d'intention** : chemin de l'objet structuré, ancienne valeur/ID, candidat de nouvelle valeur/ID, preuves et statut `pending_review`. Une modification textuelle libre non ancrée ne peut pas se convertir automatiquement en patch accepté.

## PRJ-007 — Limites mémoire

Le format compact actuel incorpore le graphe entier. diK 1.0 DOIT conserver cette compatibilité mais MAY proposer un **nouveau profil de projection par références à des shards immuables**, uniquement si nécessaire à l'échelle, avec manifeste/empreintes, non une modification silencieuse du profil compact existant.

## Tests déterminants

`PRJ-T1` round-trip structure-identique avec littéral, sources, qualificatifs ; `PRJ-T2` modifier label mais recalculer hash => avec projet ancré, rejet ; `PRJ-T3` `clean.md` seul => refuse restore ; `PRJ-T4` namespace différent => rejet ; `PRJ-T5` champs étrangers KQ/Q => rejet ; `PRJ-T6` 300 locales n'alourdissent pas projection d'une seule locale ; `PRJ-T7` données sans traduction = missing explicite ; `PRJ-T8` ancres manquantes => jamais statut authentic.
