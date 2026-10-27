# 03 — Identités sémantiques et correspondances

## Clé canonique

L'identité n'est jamais `KQ123` seul : **`(namespace_id, KQ123)`**. Même principe pour `KP`, `KA`, `KS`. Les identifiants sont opaques, non recyclables dans leur namespace, et distincts de la manière dont on les affiche.

| Famille | Nature | Dans le graphe |
|---|---|---|
| KQ | référent (personne, chose, concept, événement…) | nœud, sujet ou objet référentiel |
| KP | propriété sémantique | prédicat / qualificateur |
| KA | assertion | fait attribuable et révisable |
| KS | source | provenance et pièce justificative |
| Wikidata Q / P | identifiant externe | **dans le crosswalk**, pas comme clé interne |

### Exemple illustratif

`(example.org/kristal-demo, KQ1001)` est relié à `wikidata:Q8018` par une correspondance `exactMatch` **acceptée** avec référence de preuve `KS4001` (exemple Framework). Il ne devient pas `Q8018` dans le graphe. Les chaînes `Augustin d'Hippone` et `Augustine of Hippo` demeurent des lexèmes de présentation.

## Contrat de crosswalk

Le schéma de référence est `schemas/v11/kristal-external-crosswalk.schema.json` avec : `crosswalk_id`, liste de `mappings`, `mapping_id`, `local_ref` (namespace/id), `external_ref` (system/id), `relation`, `status`, et `review` pour les décisions acceptées.

Relations possibles : `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch`, `relatedMatch`. Statuts : `candidate`, `accepted`, `rejected`, `superseded`.

**Seul `accepted + exactMatch` peut autoriser une substitution externe explicitement demandée dans une projection.** Une ressemblance de label, même dans 40 langues, ne démontre pas l'identité. Le validateur doit refuser le type incorrect (`KP ↔ Q`, `KQ ↔ P`), la collision d'équivalences exactes actives et la preuve absente selon le contrat.

## Réconciliation continue avec Wikidata

- **Avant un nouveau KQ :** rechercher le registre local et, si le miroir existe, des candidats Wikidata. Si aucun sens existant n'est validé, allouer un KQ propre à Kristal. **Ne jamais créer un Q factice.**
- **Quand Wikidata ajoute un Q :** créer une suggestion, comparer types, déclarations et portée, approuver ou rejeter, émettre un nouveau crosswalk. Aucun graphe ancien ne change.
- **Quand Wikidata fusionne/redirige :** documenter le nouvel état et la décision qui supersède la précédente ; ne pas fusionner les KQ sans procédure propre au namespace.
- **Quand les sens diffèrent :** utiliser close/broad/narrow/related, ou maintenir l'absence de correspondance.

## Sûreté multi-projet

Deux Kristals peuvent avoir un `KQ1001` avec des sens distincts dans deux namespaces. diK **n'unifie pas** ces référents. Une correspondance inter-namespace a besoin d'une décision et d'une provenance explicites ; ses formats définitifs restent une extension future.
