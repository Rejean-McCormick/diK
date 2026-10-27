# 13 — Glossaire et exemples explicatifs

| Terme | Définition |
|---|---|
| Identifiant sémantique | Identité opaque d'un élément du graphe, indépendante des mots affichés |
| IRS | Identifiant de référent sémantique : généralement KQ dans Kristal |
| KQ | Identifiant canonique Kristal d'entité ou de concept, sous un namespace |
| KP | Identifiant canonique de propriété ou de relation |
| KA | Identifiant d'assertion |
| KS | Identifiant de source/provenance |
| QID / PID | Identifiants Wikidata Q/P externes |
| Crosswalk | Registre de correspondances entre identifiants, avec relation et provenance |
| Dictionnaire lexical | Ensemble de labels et alias rattachés aux KQ/KP et à une langue |
| Curated | Couche éditoriale locale, revue, versionnée, indépendante de l'import |
| Snapshot | Vue figée, datée/identifiée et vérifiable d'une source |
| Fallback | Utilisation déclarée d'une autre langue pour affichage, pas traduction directe |
| ExactMatch | Décision d'équivalence sémantique *acceptée et documentée* |
| Recherche inverse | Mot → liste de candidats KQ/KP ; ne constitue pas une preuve d'identité |
| Plan de conversion | Manifeste de modifications candidates, non exécutable lui-même |

## Exemple conceptuel : Augustin

- `example.org/kristal-demo + KQ1001` = référent Kristal illustratif.
- `wikidata:Q8018` = référence externe correspondante acceptée dans l'exemple.
- `Augustin d'Hippone` (fr) / `Augustine of Hippo` (en) = **libellés**, pas identifiants du graphe.

Cet exemple figure dans les fixtures copiées du Framework v11 draft.3. Les numéros KQ de démonstration ne sont pas des allocations de production.

## Exemple d'ambiguïté

Le mot « grâce » peut renvoyer à une doctrine théologique, une faveur ou une qualité esthétique. Un dictionnaire peut donc retourner plusieurs candidats. diK doit utiliser le contexte sémantique (types, relations, corpus, langue, sources), puis soumettre une proposition **au réviseur**. Aucun algorithme lexical ne transforme automatiquement la présence d'une chaîne de caractères en identité vraie.

## Exemple d'arrivée future Wikidata

Aujourd'hui : `KQ85001` sans entrée Wikidata. Demain : Wikidata publie `Q…` décrit comme équivalent potentiel. diK enregistre une proposition de mapping ; après revue, une nouvelle version du crosswalk lie `KQ85001` au Q externe. **Le KQ et les anciennes assertions restent identiques**.
