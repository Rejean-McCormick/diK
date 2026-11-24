# 58 — Statuts et rapports de lecture / rapprochement (contrat V5.3)

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Schémas proposés, pas implémentés.** Le dossier actuel reste `diK/reports/resolution_14_langues/RESOLUTION_*`; les nouvelles sorties viendront le **compléter**, sans changer rétroactivement la signification des champs V5.2.

## 1. Statuts distincts, pas un unique « absent »

### État par source

- `pointer_missing`, `pointer_stale`, `hash_unverified` : localité ou intégrité incertaine.
- `schema_unknown`, `schema_ambiguous` : JSON lisible mais adaptateur non validé.
- `schema_verified_no_qp_extracted` : format reconnu et scan achevé, mais aucune identité Q/P extraite ; ne pas dire « aucun Q/P commun ».
- `partial_budget`, `incomplete_errors`, `stale_source` : inspection non exhaustive ou invalidée.
- `complete_no_accepted_qp_overlap` : uniquement si **parcours complet**, schéma valide, Q/P extraits, et aucun recoupement avec l'index accepté du périmètre fixé.
- `complete_overlap_no_lexical_field` : Q/P communs sans labels explicites qualifiables.
- `candidate_labels_observed` : formes de langue explicites, **non publiées**.
- `conflict`, `source_not_eligible`, `eligible_not_active`, `active` : statuts de validation/autorisation distincts.

Le statut `active` n'est **pas** atteignable dans la simple inspection V5.3 ; une politique de publication versionnée reste nécessaire.

### État d'une cellule `(namespace, semantic_id, locale)`

Conserver la distinction entre `resolved_from_validated_catalog`, `candidate_external_label`, `unresolved_after_active_sources`, `source_not_configured`, `not_evaluable`, `conflict`, et `incomplete_source_scan`. **Une cellule candidate ou incomplète ne compte jamais comme résolue**. La V5.2 continue à publier ses compteurs historiques ; ces nouveaux libellés seront des champs additionnels.

## 2. Fichiers recommandés

Sous un dossier daté de `reports/resolution_14_langues/`, prévoir :

| Fichier (cible V5.3) | Granularité | Minimum de colonnes |
|---|---|---|
| `wikidata_schema_profiles.csv` | une ligne par source/version | `source_id`, `sha256`, `family`, `schema_id`, `status`, `evidence`, `adapter_version` |
| `wikidata_scan_progress.csv` | une ligne par source et passage | `source_id`, `bytes_read`, `lines_read`, `line_next`, `completed`, `checkpoint_ref`, `stop_reason` |
| `wikidata_qp_overlap.csv` | une ligne par Q/P commun + namespace / source | `namespace_id`, `semantic_id`, `wikidata_qp`, `crosswalk_ref`, `source_id`, `record_location`, `overlap_status` |
| `wikidata_forms_candidates.csv` | une ligne par Q/P+locale+forme+source | `semantic_id`, `wikidata_qp`, `locale`, `form`, `source_id`, `source_sha256`, `field_path`, `candidate_status` |
| `wikidata_conflicts.csv` | une ligne par conflit | `scope`, `namespace_id`, `semantic_id`, `wikidata_qp`, `locale`, `source_ids`, `reason` |
| `wikidata_source_decisions.csv` | une ligne par décision de qualification | `source_id`, `rights_status`, `provenance_status`, `review_state`, `decision_ref` |
| `rapport.json` | agrégat du scan | versions, exactitude périmètre, valeurs réelles et limites |

Ne pas mettre le contenu brut d'une source dans les rapports. Les libellés candidats peuvent être sensibles en matière de licence : les exports destinés au partage doivent pouvoir les **expurger**. Les fichiers ci-dessus sont des **noms proposés**, pas présents dans V5.2.

## 3. Exemple de métriques (cible)

```json
{
  "schema": "dik.wikidata-thematic-diagnostics/0.1-proposal",
  "mode": "read_only_candidate_observation",
  "sources_total": 40,
  "sources_completed": null,
  "sources_schema_unknown": null,
  "sources_incomplete": null,
  "rows_valid_json": null,
  "rows_with_qp": null,
  "distinct_qp_extracted": null,
  "qp_overlapping_accepted_crosswalk": null,
  "explicit_labels_observed": null,
  "candidate_labels_only": true,
  "activated_sources": 0,
  "baseline_v52_formes_resolues": 11188
}
```

Les `null` sont intentionnels : les mesures V5.3 n'ont **pas** encore été produites. Ne jamais remplir une mesure future par une valeur prédite.

## 4. Compatibilité / versionnement

- Conserver `totaux.catalogue_courant`, `catalogue_raccorde`, `wikidata_observe`, `non_resolu` et les 14 locales exactes tant que leur contrat historique n'est pas officiellement révisé.
- Ne modifier les compteurs de couverture qu'après **activation autorisée** de nouvelles couches, ce qui n'est pas le but de l'inspection V5.3.
- Versionner le schéma des nouveaux CSV et la politique de qualification ; inclure l'empreinte de la source, du crosswalk, la version des validateurs et l'empreinte de configuration.
- Produire `report_status=PARTIAL` tant qu'une source pertinente est tronquée, inconnue ou non évaluée. Éviter les badges « complet » basés sur une fin de processus sans EOF.
- Le ZIP à partager doit contenir uniquement les rapports indispensables, avec vérification des chemins et option d'expurgation des chemins Windows et libellés tiers.

## 5. Conditions de comparaison V5.2 → V5.3

Une comparaison valide doit présenter simultanément : nombre de Kristals évaluables/non évaluables, dénominateur ID–langue, nombre de sources examinées, nombre de sources complètes, nombre de schémas connus, nombre de Q/P extraits, de Q/P communs, de candidats et d'activations. Une augmentation des **Q/P reconnus** est un gain du lecteur ; elle ne doit pas apparaître comme une augmentation des **formes résolues** tant qu'aucune source n'est autorisée.
