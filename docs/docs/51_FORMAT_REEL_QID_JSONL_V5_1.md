# 51 — Lecteur QID JSONL réel (V5.1)

**État : implémenté pour observation candidate, pas pour publication.**

## Schéma vérifié

Le fichier local `gf-wikidata-tools/extraction/data/qid-lexicon.jsonl`, communiqué le 23 novembre 2026, contient **50 lignes JSONL**, chacune avec une clé Wikidata `Q...` et un objet des libellés par langue. Son index indique 60 083 octets ; les 50 lignes fournies contiennent **1 888 libellés sur 155 codes de langue**.

```json
{"Q132469":{"fr":"dernier théorème de Fermat","en":"Fermat's Last Theorem"}}
```

Le parseur `source_qualification._qid_lexicon_profile` accepte également le format antérieur `{"qid":"Q132469","labels":{"fr":"..."}}`. Il ne lit **que** les labels explicites. Les clés `fr`, `en`, `nn`, `nb`, `no` ne sont pas fusionnées, et aucun texte n'est traduit.

## Raccordement exact

1. Vérifier le chemin, la taille et SHA-256 contre le registre local (`source_id`).
2. Lire le QID explicitement présent dans le JSONL.
3. Exiger que ce QID figure dans une correspondance KQ/KP↔Q/P **acceptée et auditée**, avec son namespace.
4. Ne relever que les libellés des locales demandées, en candidats non publiés.
5. Exclure une paire QID+locale si le fichier contient deux valeurs différentes.
6. Aucune modification de `catalogue_courant`, `catalogue_raccorde` ou `wikidata_observe`.

**Observation sur le rapport V5 du 23 novembre :** aucun des 50 QID de ce fichier ne recoupe les QID acceptés des 57 Kristals évaluables. Le lecteur corrigé reconnaît donc la source, mais ne saurait augmenter la couverture à partir de ces seules lignes.

## Commandes

```powershell
$env:PYTHONPATH = 'C:\mycode\diK\diK\src'
py -3 -m dik sources qualify --registry '<chemin vers resource-registry.json>' --dik-root 'C:\mycode\diK\diK'
```

Le rapport de qualification consigne `qid_lexicon_probe.schema_known`, `schema_qp_keyed_locales`, `rows_with_qp_id`, `explicit_labels_accepted_for_observation`, `locales_seen` et `candidate_only=true`.

**Limites :** ni licence ni qualité sémantique ne sont certifiées par les lignes JSONL ; GF et Wikidata L/S/F relèvent de contrats distincts. Ne pas activer le lexique comme dictionnaire global sans revue.


## Correction de périmètre V5.2

`dik sources qualify` interroge désormais exactement `TARGET_LOCALES` (14 codes : `en,fr,es,de,nl,sv,da,no,nn,fi,et,af,it,pt`). Les libellés `nb` sont observables dans le JSONL source, mais **non comptés** parmi les 14 codes officiels. Le schéma reconnu vaut `lexique_qid_schema_reconnu_non_habilite` en CSV, **pas** `source approuvée`.
