# 34 — Résolution par identité, jamais par traduction

## A. Invariant fondamental

**Entrée** : identité canonique `(namespace_id, semantic_id)` et locale BCP 47 demandée, plus contexte facultatif (domaine, rôle grammatical) et politiques autorisées. **Sortie** : forme(s) attestée(s), langue réelle de la forme, statut, source, version, preuve et éventuel conflit.

```text
Kristal v11                   diK                                  Ressources locales
(namespace, KQ/KP) -----> Résolveur de clé -----> Catalogue v11 / couche curated
         |                      |                         |
         |                      +---- Crosswalk accepté --+---- Wikidata Q/P (labels)
         |                      |                         |
         |                      +---- observation L/S/F --+---- GF (morphologie qualifiée)
         |                      |                         |
         +------ locale --------+---- résultat traçable par (ID, locale)
```

Aucune flèche `fr → en`, `en → de` ou `mot A → mot B`. Une forme française ne prouve pas la forme allemande ; même une forme identique dans deux langues peut correspondre à des identités distinctes.

## B. Les quatre espaces ne fusionnent pas

| Espace | Exemple | Portée | Condition de raccordement |
|---|---|---|---|
| Kristal | `(kristal:catho:v11, KQ…)` | Identité canonique interne | Registre/namespace v11 validé |
| Wikidata entités | `Q…` / `P…` | Référent externe | Crosswalk `exactMatch`, `accepted`, preuve applicable et non contradictoire |
| Wikidata lexèmes | `L…`, `L…-S…`, `L…-F…` | Lexème, sens, forme | Adaptateur lexical revu, non identique au Q/P |
| GF | `DictFre.gf`, `LexiconEng.gf`, fonction/paradigme | Réalisation linguistique/grammaticale | Association explicite entre entrée sémantique et fonction/catégorie/locale |

Les nombres contenus dans `KQ123` et `Q123` ne sont pas une preuve de correspondance. La comparaison de deux libellés est seulement un signal de revue, jamais une autorité d'alignement.

## C. Algorithme cible (description, pas état implémenté)

1. **Valider** le graphe, registre, crosswalk et catalogue d'une révision v11, le namespace, la famille KQ/KP et la locale.
2. **Résoudre localement** dans les couches déclarées et contrôlées : formes directes, priorités, conflits et domaine ; journaliser identifiants de couche et empreintes.
3. **Examiner les sources cataloguées** à l'extérieur du Kristal : ne charger que les sources référencées et acceptées avec la même clé `(namespace, KQ/KP)` ou un crosswalk accepté.
4. **Pour Q/P** : résoudre la correspondance qualifiée, puis lire le label de la locale demandée depuis un snapshot Wikidata **disponible et approuvé** ; ne jamais déduire un `exactMatch` d'un label.
5. **Pour GF** : réaliser une morphologie uniquement si un adaptateur a été validé (catégorie/fonction/paradigme/locale + provenance). L'absence de ces liens => `gf_non_qualifie`, pas « mot introuvable ».
6. **Repli facultatif** : permis seulement si une politique explicite le définit ; afficher `fallback` en mentionnant la locale effectivement employée. Un repli **n'est pas une traduction** et ne compte pas comme forme directe de la locale demandée.
7. **Conserver la preuve** de la forme (source, révision, digests, règle, décisions de revue) ; sinon retourner un état explicite plutôt qu'un mot deviné.

## D. Invariants de refus

- Pas de promotion automatique de `candidate` à `accepted`.
- Pas de fusion inter-namespace sur égalité des graphies, des suffixes numériques ou des chemins.
- Pas d'activation d'une couche à partir de sa seule présence sur disque.
- Pas de valeur inventée pour remplir les 14 colonnes.
- Pas de rétroécriture des fichiers canon, pas de modification d'une révision historique.
- Un `missing` n'est vrai que relativement au *jeu de sources testé* ; la catégorie globale « absent du monde » n'existe pas.

## E. Exemple illustratif non canonique

Un concept fictif `(example.org/demo,KQ100)` demandé en `fr` et `en` est recherché indépendamment : un catalogue peut fournir `fr` sans `en`, un mapping Q accepté peut fournir `en` dans un snapshot local, ou aucun label peut être qualifié. Les objets d'exemple ne prouvent aucun ID ni mot réel.

## F. Propriété de l'identité et de la publication

Le Framework fixe les règles du canon. diK tient les références, les observations, la curation et la couverture ; il ne devient pas une seconde autorité KQ/KP. Spek présente des données conformes ; Konstellation consomme des vues; WordBench/GF réalise et teste la morphologie. Aucune application consommatrice n'est habilitée à inventer une identité lexicale acceptée.

Voir [03](03_IDENTITES_ET_ALIGNEMENTS.md), [04](04_DICTIONNAIRES_ET_LANGUES.md), [28](28_WIKIDATA_LEXEMES_GF_PIPELINE.md) et [37](37_CONNECTEURS_WIKIDATA_GF.md).
