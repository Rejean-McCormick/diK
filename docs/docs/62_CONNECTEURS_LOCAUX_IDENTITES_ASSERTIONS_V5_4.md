# 62 — V5.4 : candidats d’identité locaux et assertions Wikidata typées

**État : code effectivement développé en V5.4 (alpha.12) ; validation sur les fichiers réels de l'utilisateur à effectuer.** Ce document complète le [chapitre 61](61_IMPLEMENTATION_EFFECTIVE_V5_3.md), le contrat 55, les règles 57 et la décision ADR-DIK-LEX-6. Ne pas confondre les *formes de fixtures* des tests avec les enregistrements Windows.

## Pourquoi cette évolution

Le bilan Windows `DIK_V5_3_BILAN_20261123T153542Z.zip` a constaté 40 références thématiques, dont trois copies identiques et **37 sources classées `schema_unknown`**. Les noms de champs *réellement observés dans les rapports* établissent deux familles :

| Famille de fichiers | Nombre de fichiers profilés | Champs du rapport V5.3 | Sémantique de V5.4 |
|---|---:|---|---|
| `identity-candidates.jsonl` non vides | 14 | `semantic_id`, `external_id`, `namespace`, `identity_status`, `reason` | **proposition locale** `(namespace,KQ/KP) → Q/P`, jamais preuve d'acceptation |
| `statements.jsonl` | 18 | `wikidata_subject`, `wikidata_property`, `semantic_subject_candidates`, `semantic_property_candidates`, `evidence`, et métadonnées | **assertion** avec sujet Q et propriété P ; pas de texte lexical |
| Fichiers vides / copies dupliquées | 4 | aucun champ | `empty_source` explicite ou `same_bytes_as_prior_source` |
| Jeux GF-Wikidata (`City`, `Country`, `University`, `Part_of world`) | 4 | aucun champ interprétable dans le bilan V5.3 | **toujours inconnus**, aucune extraction inventée |

Les chiffres sont **des profils observés dans ce bilan**, et ne prouvent pas encore le succès d'analyse après installation V5.4. Les valeurs internes des JSONL n'avaient pas été transmises, seules leurs clés.

## Adaptateur `local_identity_candidate/1`

Il ne s'active que si les cinq champs explicites sont présents. `semantic_id` doit correspondre exactement à `KQ[1-9][0-9]*` ou `KP[1-9][0-9]*` ; `external_id` à `Q...` ou `P...` du **même type** ; `namespace` doit être une chaîne non vide. Aucun lien déduit des suffixes numériques, de la forme textuelle, du champ `reason`, ni du statut revendiqué par le fichier.

L'extraction produit une observation non lexicale `crosswalk_candidate`. Lorsqu'un index officiel audité contient un lien pour la **même paire `(namespace,semantic_id)`**, diK compare la valeur et retient l'un des statuts :

- `consistent_with_existing_accepted` : la proposition est égale au lien **déjà accepté** ; ceci n'est pas une seconde approbation.
- `contradicts_existing_accepted` : proposition différente du lien accepté dans le même namespace, à examiner.
- `no_existing_accepted` : aucun lien officiel accepté pour cette paire ; **ne pas la promouvoir**.

Le statut déclaré `identity_status` demeure une simple **affirmation de la source** (`source_claimed_status`), même s'il vaut `accepted`. Les données sont consignées localement avec référence de fichier SHA, offset et numéro de ligne. Elles ne sont jamais intégrées aux catalogues v11.

## Adaptateur `local_wikidata_statement/1`

Il exige les champs `wikidata_subject`, `wikidata_property`, `semantic_subject_candidates`, `semantic_property_candidates` et `evidence`. Le lecteur accepte uniquement une valeur Q/P explicite et canonique à l'endroit attendu :

- `wikidata_subject` → identifiant `Q...`, rôle `entity_subject` ; peut permettre une **observation de recoupement** avec l'index accepté, sans produire de libellé.
- `wikidata_property` → identifiant `P...`, rôle `property_predicate` ; conservé comme **observation non lexicale**, jamais confondu avec l'identité du sujet.
- `semantic_subject_candidates`, `semantic_property_candidates`, `evidence`, `external_seed_keys` et autres métadonnées ne sont pas parcourus pour y chercher des pseudo-identifiants et ne produisent **aucune forme**.

Des valeurs internes non conformes laissent la structure reconnue mais sans Q/P extrait. Les tableaux JSONL ou objets réellement mixtes restent inconnus/ambigus conformément à V5.3.

## Persistance, confidentialité et contrôles

Le traitement conserve le SHA-256, la validation des racines et l'analyse lecture seule ; la reprise SQLite est invalidée quand la version de l'adaptateur, les empreintes ou **l'index officiel `(namespace,KQ/KP) → Q/P`** changent. Les lignes candidates peuvent être nombreuses : le nombre d’observations identitaires stockées par source est borné par `--wikidata-max-candidates` (40 000 par défaut). En cas de dépassement, le statut est `partial_budget`, jamais une complétude supposée ; relever ce plafond permet la reprise. Le fichier SQLite et les rapports demeurent dans `diK/reports`, et **ne sont pas importés comme dictionnaires**.

Nouveaux CSV locaux et dans le ZIP expurgé :

- `wikidata_identity_links_candidates.csv` : identité, namespace, lien externe, statut revendiqué, comparaison officielle, SHA et localisation de la ligne. **Propositions uniquement.**
- `wikidata_nonlexical_qp_observations.csv` : Q/P accepté en observation de rôle non lexical (`property_predicate`, `crosswalk_candidate`), sans forme textuelle. Les observations sont dédupliquées par `(Q/P,rôle,champ)` pour conserver un aperçu borné.

Nouveaux champs agrégés : `candidate_identity_links`, `candidate_identity_links_consistent`, `candidate_identity_links_contradictory`, `nonlexical_qp_observations`, `statement_sources_completed`. `rapport.json` expose `wikidata_v54` et conserve `wikidata_v53` pour les consommateurs existants. Le partage utilise `dik sources export-v54`, avec `export-v53` conservé comme alias historique ; le ZIP produit est `DIK_V5_4_BILAN_*.zip` et ne contient pas les chemins Windows ou les mots candidats bruts.

## Invariants NON négociables

1. **126 Kristals officiels** ; seuls les 57 évaluables du baseline font partie du dénominateur historique et les 69 autres restent non évaluables.
2. **14 locales exactes** : `en, fr, es, de, nl, sv, da, no, nn, fi, et, af, it, pt`. Aucun repli `nb → no` ou `nn → no`.
3. **Aucune traduction** : une forme n'est récupérée que dans la locale demandée et sur identité prouvée.
4. **Aucune publication depuis les candidats** : le compteur de couverture ne change pas à partir d'une assertion ou d'une proposition de crosswalk.
5. **Aucune extrapolation GF / L/S/F**. Les quatre ensembles GF-Wikidata restent à étudier sur des données réelles.
6. Droits non attestés ≠ autorisation d'exploitation. Ni contenu des Kristals, ni crosswalks, ni sources GF/Wikidata ne sont modifiés.

## Validation et limites

La suite Python et les fixtures synthétiques couvrent la séparation `KQ/Q` vs `KP/P`, la comparaison par namespace, les contradictions, les statuts source non autoritaires, les rôles sujet/prédicat, les fichiers vides, la reprise avec index modifié, les doublons et l'absence d'activation. **La validation du comportement sur les 40 fichiers réels et de l'installateur sous Windows n'est pas encore faite** à la date de livraison du code V5.4. Les identifiants Wikidata présents comme URI non typée ou dans des conteneurs non attestés ne sont pas devinés.

Il faudra confronter le ZIP V5.4 Windows aux résultats V5.3 et examiner les **quatre schémas GF-Wikidata non identifiés**, ainsi que l'approbation des provenances/droits, avant toute fonction supplémentaire de publication.
