# Exemples documentaires — futurs adaptateurs Wikidata V5.3

**Fichiers de démonstration non normatifs, jamais à activer** : ils ne proviennent pas des 40 JSONL thématiques locaux, dont le contenu n'est pas dans le bilan V5.2. Ils servent seulement à illustrer les tests à écrire lors du prochain développement.

## Exemple 1 — QID en clé externe : seul format effectivement confirmé

```json
{"Q132469":{"fr":"dernier théorème de Fermat","en":"Fermat's Last Theorem"}}
```

Ce schéma correspond au fichier `qid-lexicon.jsonl` fourni le 23 novembre. La forme existe en `fr` et `en` **pour Q132469** ; diK ne peut l'attribuer à un KQ que si un crosswalk officiel accepté et validé relie ce KQ à Q132469. Dans l'audit V5.1 précédent, aucune des 50 entrées QID de ce fichier ne recoupait les liens acceptés des 57 Kristals évaluables.

## Exemple 2 — Objet de déclaration *fictif* (non reconnu automatiquement)

```json
{"subject":{"id":"Q42"},"predicate":{"id":"P31"},"object":{"id":"Q5"}}
```

Si un futur schéma validé donnait ces rôles, cette ligne contiendrait **trois** identifiants, mais **aucune forme linguistique**. Le Q/P objet ou prédicat ne peut pas être choisi comme identité lexicale de la ligne. Cet exemple ne prouve **pas** que `statements.jsonl` réel utilise ces champs.

## Exemple 3 — Candidat d'identité *fictif* (pas une approbation)

```json
{"candidate":{"semantic_id":"KQ123","wikidata":"Q456","decision":"candidate"}}
```

Même si une telle structure était observée, elle ne suffirait **pas** pour `exactMatch accepted`, ni pour l'activation d'un libellé. La décision `candidate` reste une proposition.

## Exemple 4 — Forme JSONL inconnue

```json
{"record":{"entity_uri":"https://www.wikidata.org/entity/Q123","display":"terme"}}
```

Sans schéma validé décrivant le rôle de `record.entity_uri`, la locale et le sens de `display`, le statut doit être `schema_unknown` ou `schema_ambiguous`, **pas** `complete_no_accepted_qp_overlap` ni `candidate_labels_observed`.

## Tests d'acceptation associés

- Aucune activation automatique ; aucune traduction FR→EN.
- Séparer identité de la ligne, propriété et objet d'une assertion.
- `no`, `nb`, `nn` restent distincts et `nb` n'est pas dans la liste des 14 codes ciblés.
- Un objet invalide ou un modèle inconnu donne un statut explicite ; pas une absence de correspondance.
- Les **vrais** formats restent à identifier sur la machine locale avant de coder leur adaptateur.
