# 52 — V5.2 : audit des sources Wikidata thématiques et raccordement candidat aux IDs

**Statut : implémenté pour diagnostic hors-ligne. Pas de publication, pas de traduction.**

## Pourquoi cet adaptateur ?

Dans le registre local du 23 novembre 2026, 5 269 références ont été inventoriées sous 12 racines. La famille `wikidata_thematic_candidate` compte **40 fichiers**, mais ils ne forment **pas** un dump Wikidata unique : **36** sont des fichiers `identity-candidates.jsonl`/`statements.jsonl` dans des répertoires `Kristal/locals`, **4** sont des jeux thématiques GF-Wikidata (`City`, `Country`, `Part_of world`, `University`). Le registre contient leurs chemins, tailles et empreintes, **pas leurs enregistrements**. Le schéma réel de ces 40 sources n'a donc pas été validé ici.

Ce nouvel adaptateur lit localement les fichiers inventoriés, puis distingue **ressource intacte**, **schéma observé**, **Q/P recoupant un `exactMatch accepted` audité**, **forme explicite candidate** et **forme autorisée** (cette dernière **n'est pas accordée par V5.2**).

## Commande PS7 / CLI

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik coverage resolve14 `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --sources-root 'C:\mycode' `
  --dik-root 'C:\mycode\diK\diK' `
  --min-kristals 126 `
  --resource-registry 'C:\mycode\diK\diK\reports\resources\resource-registry-latest.json' `
  --observe-qid-lexicon `
  --observe-wikidata-thematic
```

La commande s'appuie **exclusivement sur le portefeuille officiel** : `(namespace_id, KQ/KP)` → `external-crosswalk.json` `exactMatch accepted` avec pièces KS → `Q/P` non contradictoire. Elle inspecte ensuite les JSONL thématiques sous les limites de taille et de ligne. **Aucune similarité de mot n'est utilisée pour établir un lien.**

## Contrats de lecture

- L'emplacement doit appartenir à la racine inventoriée, sans lien symbolique ni jonction ; taille et SHA-256 sont vérifiés **avant lecture**. Si la source a changé, on la signale sans l'utiliser.
- Schémas lexicaux explicitement reconnus en observation : `{"Q123":{"fr":"..."}}`, `{"qid":"Q123","labels":{"fr":"..."}}`, `{"id":"Q123","labels":{"fr":{"value":"..."}}}`.
- Les fichiers `statements.jsonl` et `identity-candidates.jsonl` peuvent contenir des références Q/P **sans contenir de libellés approuvés** ; les champs `subject`, `predicate`, `value`, `lemma`, `forms` et les identifiants `L/S/F` ne sont jamais transformés en mots pour un KQ/KP.
- Seuls les **14 codes exacts** de `TARGET_LOCALES` sont observés. `no`, `nb`, `nn` restent distincts, sans repli implicite : `nb` n'est **pas** l'une des 14 locales cibles.
- Une paire Q/P+locale contradictoire entre fichiers est signalée dans le CSV (`conflict_between_sources`). Des copies à SHA identique sont recensées sans compter deux fois le même contenu.
- Inspection bornée : 64 MiB par fichier, 150 000 lignes par fichier, 2 000 000 caractères par ligne, 40 000 paires de formes par fichier ; une source partielle est explicitement `truncated`. L'absence d'un mot dans une source tronquée n'est pas un manque prouvé.

## Résultats, dans `diK/reports/resolution_14_langues/RESOLUTION_*/`

- `wikidata_thematic_sources.csv` : une ligne par source, son chemin, état SHA, schémas/volumes et motifs de refus ou troncature.
- `wikidata_thematic_observations_candidates.csv` : formes explicites pour des Q/P déjà acceptés et non contradictoires, avec namespace KQ/KP, locale, chemin, `source_id`, SHA et conflit éventuel.
- `rapport.json` : bloc `wikidata_thematic`, compteurs de sources, paires candidate, conflits, aucune activation ; et `totaux.wikidata_thematic_observations_non_publiees`.
- Les CSV existants de couverture (`catalogue_courant`, `catalogue_raccorde`, `wikidata_observe`) **ne changent pas** du fait de ces observations candidates.

Les rapports contiennent des chemins absolus locaux : les partager seulement volontairement. Les dictionnaires et les Kristals ne sont pas modifiés.

## V5.2 ne fait pas

- Certifier la provenance ou la licence de la source Wikidata.
- Accepter automatiquement des correspondances candidates, identifier un Q/P à partir d'un mot ou rapprocher les `L/S/F` des entités Q/P.
- Activer les lexiques GF comme identités KQ/KP, inflechir un terme GF, réparer les 69 Kristals non évaluables.
- Garantir un gain de couverture : cela nécessite d'observer le **nouveau scan Windows** et de procéder à la revue des preuves/permissions avant la publication.

**Critères de validation :** tests de faux rapprochement, cas `L` non-`Q/P`, conflit intersource, falsification SHA, doublons, absence de repli norvégien, et invariance des totaux de couverture. L'installateur Windows doit également être vérifié localement après livraison.


## Résultat du scan Windows V5.2 du 23 novembre 2026 (ajout documentaire)

Le bilan `DIK_V5_2_BILAN_20261123T143508Z.zip` recense **40 sources enregistrées**, 37 inspectées, trois copies identiques dédupliquées, 35 `no_accepted_qp_overlap` et deux sources tronquées après 150 000 lignes chacune (`City.jsonl`, `University.jsonl`). Il compte **333 849 lignes lues, 0 Q/P reconnu, 0 observation thématique publiée**. Cela ne démontre pas que ces fichiers sont dépourvus de Q/P : les schémas réels n'ont pas été fournis dans le ZIP, et le lecteur ne connaît pas nécessairement leurs champs. **Ne pas utiliser `no_accepted_qp_overlap` de V5.2 comme absence prouvée.** La correction de conception est décrite dans les [chapitres 53 à 59](53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md) et l'[ADR proposée DIK-LEX-6](../decisions/ADR-DIK-LEX-6-lecteurs-schemas-reprise-sans-activation.md). Cette mise à jour ne modifie pas le code V5.2.
