# 63 — V5.5 : lecture réelle des quatre sources GF-Wikidata

**Date :** 23 novembre 2026. **Statut :** code implémenté, aucun dictionnaire ni lien KQ/KP publié.

## Diagnostic vérifié sur les quatre fichiers transmis

Contrairement à leur suffixe `.jsonl`, les fichiers de `gf-wikidata-tools/data` sont des **tableaux JSON multiligne** de la forme :

```json
[
  {
    "url": "http://www.wikidata.org/entity/Q16",
    "labels": {"en": "Canada", "sv": "Kanada", "jp": "カナダ", "bn": null},
    "descriptions": {"en": "country in North America"}
  }
]
```

| Source | Entités QID effectivement lues | Libellés `en` + `sv` dans le fichier |
| --- | ---: | ---: |
| City.jsonl | 32 496 | 50 802 |
| University.jsonl | 14 184 | 15 538 |
| Country.jsonl | 201 | 399 |
| Part_of world.jsonl | 8 | 16 |
| **Total** | **46 889** | **66 755** |

La lecture des quatre originaux fournis a confirmé leur structure, le caractère unique des QID dans chaque fichier et la présence des six codes `en`, `el`, `jp`, `sv`, `zh`, `bn`. Seuls `en` et `sv` coïncident avec les 14 locales officielles de diK : `en`, `fr`, `es`, `de`, `nl`, `sv`, `da`, `no`, `nn`, `fi`, `et`, `af`, `it`, `pt`. Le code **ne convertit pas** `jp` en `ja`, `nb` en `no`, ni une langue en une autre.

## Comportement implémenté

- `wikidata_json_array.py` lit les éléments un par un sans charger le tableau complet, et conserve un **offset en octets** à la fin de chaque objet ; les chaînes, séparateurs et imbrications JSON sont pris en compte.
- La détection distingue **le conteneur** `json_array` / `jsonl` du **schéma sémantique**. L'extension du fichier n'autorise aucune supposition sur son format.
- `wikidata_v53.recognize` ne reconnaît `wikidata_entity_url_labels/1` que lorsque l'URL d'identité est exactement `http(s)://www.wikidata.org/entity/Q...`, que `labels` est un dictionnaire de codes et que `descriptions` est un dictionnaire distinct.
- Les valeurs nulles ou absentes ne produisent pas de candidat. Seules les étiquettes explicites du code de langue demandé sont prises en compte ; **jamais** `descriptions`.
- Les étiquettes ne sont croisées qu'avec les Q/P déjà présents dans le registre des correspondances **acceptées et non contradictoires** des Kristals évaluables. Les résultats restent des **observations candidates non publiées**, avec source, SHA-256 et localisation par octet/ligne.
- Le stockage SQLite de reprise existant est conservé. Une modification de SHA, un changement de version d'adaptateur, un changement du jeu de Q/P ou de la politique linguistique invalide le checkpoint précédent.
- Un tableau tronqué, un séparateur invalide, un objet excessif ou un schéma différent est rapporté comme **incomplet/inconnu**, jamais comme une absence de recoupement prouvée.
- Aucun fichier GF, Wikidata, Kristal ou dictionnaire n'est modifié. La lecture n'accorde **ni licence ni autorité canonique** à la source.

## Rapports et commandes

Les commandes conservées sont `dik sources discover`, `dik sources verify`, `dik sources qualify`, `dik coverage resolve14 --observe-qid-lexicon --observe-wikidata-thematic`.

Nouveau : `dik sources export-v55 --dik-root C:\\mycode\\diK\\diK --resolution-dir <dossier> --registry <registre>` crée `DIK_V5_5_BILAN_*.zip` sans chemins Windows ni libellés bruts.

- `wikidata_schema_profiles.csv` expose désormais `container` (`jsonl` ou `json_array`) ainsi que `schema_id`.
- `rapport.json` ajoute `wikidata_v55` avec `json_array_sources_completed`, `json_array_rows_read`, `qp_overlapping_accepted_crosswalk` et `candidate_forms`.
- `wikidata_run_manifest.json` et `wikidata_schema_registry.json` conservent les empreintes, versions, décisions et statuts de lecture.
- `wikidata_forms_candidates.csv`, `wikidata_qp_overlap.csv` et `wikidata_conflicts.csv` continuent de préciser les preuves sans modifier les compteurs de couverture.

La validation intégrée confirme que même lorsqu'un QID trouvé correspond à une identité `KQ` acceptée, **`totaux` n'augmente pas** sans processus distinct de qualification et publication.

## Limites réelles et travaux suivants

La présence de **46 889 QID** dans les fichiers transmis ne signifie pas 46 889 liens KQ/KP approuvés, ni 66 755 mots résolus. Le recoupement réel avec les **1 776 liens acceptés** et les données des 126 Kristals devra être mesuré sur Windows. Les fichiers transmis n'ont pas les 14 langues : seuls `en`/`sv` sont explicitement disponibles dans ce lot. La provenance/licence des sources, les lexèmes Wikidata L/S/F, la morphologie GF et les 69 Kristals non évaluables restent des chantiers indépendants.

**Tests :** `tests/test_wikidata_v55.py` (format réel, reprises, tableaux invalides, URL/locale strictes, SHA et intégration à `resolve14`) et suite complète du dépôt.
