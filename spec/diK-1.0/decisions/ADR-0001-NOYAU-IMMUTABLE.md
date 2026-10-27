# ADR-0001 — Canon Framework et vues lexicales dérivées

- **Statut** : proposé pour diK 1.0 ; le principe canonique est déjà imposé par Framework v11 draft.3.
- **Contexte** : plusieurs sources de vocabulaire, Wikidata évolutif, 300 langues, migration d'anciens graphes nommés par mots.
- **Décision** : garder identités/graphe Framework comme source de vérité ; utiliser catalogues lexical/crosswalk comme métadonnées séparées, couches versionnées, projections dédupliquées et index recréables.
- **Motif** : conserve l'identité stable, la réversibilité, l'historique et limite les collisions futures avec Wikidata.
- **Conséquences** : complexité explicite de provenance/revue et besoin d'ancres ; aucun rendu Markdown seul ne peut être restauré.
- **Options rejetées** : Q Wikidata comme identifiant interne ; mots comme keys du graphe ; recherche de KQ depuis traduction ; SQLite comme canon.
- **Critères** : ID-R2, XW-T1, PRJ-T1/T3 et MIG-T1 dans le TCK.
