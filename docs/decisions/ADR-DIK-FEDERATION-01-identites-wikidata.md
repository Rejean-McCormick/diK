# ADR-DIK-FEDERATION-01 — Répertoire dérivé des identités Kristal ↔ Wikidata

**Statut : proposition technique à qualifier, non ratification Framework.**

## Problème

Les 126 Kristals officiels contiennent des identités `KQ` / `KP`, dont la clé est
**(`namespace_id`, `semantic_id`)**. Un numéro local seul ne doit jamais être
interprété comme une référence globale. Les mots ne sont pas des identifiants.
Le crosswalk explicite vers Wikidata est séparé. Les lexèmes Wikidata `L/S/F`
représentent d'autres objets et ne sont pas une équivalence Q/P/KQ/KP.

## Décision proposée

- Framework/Kit et Kristals restent **sources d'autorité** du canon, des
  identités et assertions. diK produit un **index dérivé, reconstructible** ;
  il ne réécrit pas les Kristals.
- La référence externe commune est un `Q/P` **uniquement si** le crosswalk
  sélectionné est `accepted`, `exactMatch`, possède une décision de revue,
  des références `KS` et un type cohérent KQ→Q / KP→P.
- Même une correspondance acceptée est **lue depuis la source**, pas
  approuvée de nouveau par diK. Les autres relations/statuts restent visibles
  mais ne deviennent pas des équivalences.
- La recherche aller-retour est possible par `(namespace,id)` ou par `Q/P`.
  Aucune recherche par identifiant local seul. Un doublon de clé complète entre
  Kristals est **signalé**, jamais fusionné.
- Les libellés et définitions sont conservés **s'ils figurent dans les sources
  vérifiées**. Une valeur manquante reste `null`, jamais reconstruite à partir
  d'un nombre ou d'un homographe.
- EncyK fournit les candidats/provenances; Wikidata Q/P établit la référence
  externe; diK lexical conserve les 13 langues cibles; SemantiK planifie;
  GF/WordBench réalise; Orchestrator gère les gates; Spek compose/publie
  uniquement après ses décisions indépendantes.
- Les anciennes bases `no` restent archivées. **13 langues cibles** :
  `en fr es de nl sv da nn fi et af it pt`. La V5.8 et ses commandes `*14`
  restent en **compatibilité historique**, sans mutation ni falsification des
  anciens bilans. Migration vers 13 = chantier distinct.

## Contrat d'interface (candidat)

`dik.federated-semantic-registry/0.1-candidate` : nouveau dossier immuable
contenant `manifest.json` (empreinte SHA-256, 13 langues cibles, statistiques,
aucune approbation automatique) et `registry.sqlite3` (tables `identities`,
`crosswalk`, `kristals`). Les consommateurs peuvent vérifier **l'intégrité**
avec `tools/dik_federation_preflight.py` ; un précontrôle réussi ne constitue
**aucun RuntimeSet, aucune licence approuvée et aucune permission de publier**.

Les mêmes contrats et garde-fous sont documentés dans EncyK, SemantiK Architect,
SemantiK Runtime Orchestrator et Spek. Ce partage documentaire n'établit pas à
lui seul un déploiement ni une approbation inter-dépôts.

## Rejets explicites

Renuméroter les Kristals ; remplacer `KQ/KP` par `Q/P` ; dériver des sens de
termes identiques ; rabattre `no`, `nb` ou `nn` ; fusionner deux Kristals
sur le même QID ; écrire dans Wikidata ; ajouter des approvals automatiques ;
mettre le pont EncyK/diK dans une chaîne de publication par défaut.

## Qualification nécessaire

Exécuter la construction en lecture seule sur les 126 Kristals de production ;
examiner les 69 non évaluables, les collisions de namespaces, les conflits de
crosswalk et la dérive Framework draft.3 / draft.4 avant d'étendre les usages.
Les tests synthétiques, même réussis, ne certifient pas ces données vivantes.
