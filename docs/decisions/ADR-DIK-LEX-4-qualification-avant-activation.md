# ADR-DIK-LEX-4 — Qualification avant activation lexicale

- **Statut : proposé / implémentation conservatrice V5** ; pas de ratification multi-projets.
- **Date :** 2026-11-23.

## Décision

Aucune découverte de fichier, empreinte identique, suffixe `.gf`, QID Wikidata ou libellé ressemblant n'accorde d'autorité lexicale. Le Source Manager sépare découverte, intégrité, structure, preuve de correspondance, revue des droits et publication. Les observations QID n'augmentent pas la couverture officielle.

## Motivations

Le registre réel contient 5 269 chemins et 0 source activée. GF RGL, archives, dumps thématiques et artefacts de tests coexistants ne possèdent pas la même fonction. Les identifiants KQ/KP sont indépendants de la langue, et les correspondances Q/P nécessitent leur propre décision et pièces KS.

## Conséquences

- Qualification V5 uniquement en lecture seule avec rapports locaux.
- Aucune fusion par graphie, nom de fichier, SHA identique ou proximité de namespace.
- Tout futur adaptateur GF/L/S/F devra apporter des tests négatifs de conflits, homonymes, identité et droits.
- Pas de modification des fichiers sources ni de requête réseau dans ces commandes.
