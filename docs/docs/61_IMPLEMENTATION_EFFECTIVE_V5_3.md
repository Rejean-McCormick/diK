> **Successeur effectif :** [62 — V5.4](62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md) ajoute les adaptateurs correspondant aux champs révélés par le rapport V5.3. Le présent chapitre décrit le périmètre de V5.3 seulement.

# 61 — V5.3 : implémentation effective, limites et exploitation Windows

**État au 23 novembre 2026 : code livré dans le pack alpha.11, tests Linux en cours.** Ce chapitre est la **référence d'implémentation**, à distinguer des chapitres 53–60 rédigés comme spécifications et du rapport Windows V5.2 historique.

## Fonctionnement livré

- `dik coverage resolve14 --observe-wikidata-thematic` conserve le parcours strict **126 Kristals officiels × 14 locales** et utilise désormais `wikidata_v53` pour les sources thématiques du registre.
- Profilage conservateur de schémas JSONL à partir de leurs contenus (`qp_keyed_locales/1`, `id_labels/1`, `statement_triple/1`, `identity_candidate/1`, `entity_id_only/1`). Un schéma inconnu ou mélangé est déclaré `schema_unknown`/`schema_ambiguous`, **pas « pas de correspondance »**.
- Les rôles de déclarations (`entity_subject`, `property_predicate`, `entity_object`) et les `crosswalk_candidate` ne fournissent **aucun** libellé publié. Seuls les champs explicites `labels` ou `QID → locale → forme` peuvent produire des **observations candidates** ; aucune langue intermédiaire.
- Rapprochement par les Q/P déjà retenus par l'audit des `exactMatch accepted` avec preuves KS, sous namespace et sans correspondance par forme ou suffixe.
- Lecture séquentielle binaire, borne 2 Mo/ligne, SQLite transactionnel de reprise, SHA-256 avant/après, reprise par offset après budget, écritures **uniquement** sous `diK/reports/resolution_14_langues/checkpoints_v53`.
- Rapport V5.3 additionnel : `wikidata_schema_profiles.csv`, `wikidata_scan_progress.csv`, `wikidata_qp_overlap.csv`, `wikidata_forms_candidates.csv`, `wikidata_conflicts.csv`, `wikidata_source_decisions.csv`, `wikidata_schema_registry.json`, `wikidata_run_manifest.json` ; le format historique V5.2 reste présent.
- Statuts discriminants : `schema_unknown`, `schema_ambiguous`, `partial_budget`, `pointer_stale`, `schema_verified_no_qp_extracted`, `complete_no_accepted_qp_overlap` (seulement après EOF et sans rejet), `complete_overlap_no_lexical_field`, `no_eligible_lexical_identity` (Q/P trouvés uniquement comme objets/prédicats/candidats), `candidate_labels_observed`, `conflict`, `completed_with_rejections`.

## Commande et budgets

```powershell
py -3 -m dik coverage resolve14 `
  --official-root 'C:\mycode\Kristal\kristal-public\kristals' `
  --sources-root 'C:\mycode' --dik-root 'C:\mycode\diK\diK' `
  --resource-registry 'C:\mycode\diK\diK\reports\resources\resource-registry-latest.json' `
  --min-kristals 126 --observe-wikidata-thematic `
  --wikidata-max-rows-per-pass 0 --wikidata-max-bytes-per-pass 0
```

`0` signifie scanner jusqu'à EOF sans limite de lignes/bytes **par passage**, sous les bornes de taille de fichier et de mémoire prévues. Pour tester la reprise, définir `--wikidata-max-rows-per-pass 150000` : le premier lancement rend `partial_budget`, le suivant reprend au même offset, si les fichiers et l'index de Q/P acceptés n'ont pas changé. Le budget `--wikidata-max-candidates` est par source ; aucune forme n'est supprimée silencieusement si la limite est atteinte.

## Règles de décision

Une source avec `schema_unknown` doit faire l'objet d'un examen de son **vrai schéma** sur Windows. La classification `wikidata_thematic_candidate` et le nom `City.jsonl` ne prouvent rien concernant ses champs. Le code V5.3 **ne prétend pas prendre en charge les schémas encore inconnus** des 40 sources : il fournit un profil typé de leurs noms de champs, sans copier leurs lignes. Pour ajouter un nouvel adaptateur, obtenir une fixture authentique, un contrat de rôle, des tests de preuve et une validation de provenance/droits. La seule existence d'un Q/P dans une assertion ne constitue pas une forme lexicale.

Le module ne génère aucune traduction, n'utilise pas GF comme alignement lexical, ne traite pas Wikidata L/S/F comme Q/P, n'active pas de droits et ne transforme pas les 69 Kristals non évaluables. Il n'accroît **jamais** les compteurs historiques de couverture avec une observation candidate.

## Export et confidentialité

Les rapports locaux complets sont conservés dans `diK/reports`. Le lanceur propose un ZIP **expurgé** : source_id, empreintes et statistiques sans lignes JSONL complètes, sans chemins Windows ni libellés tiers. L'export ne change pas les rapports locaux. Les fichiers SQLite de reprise ne sont pas inclus dans le ZIP.

## Tests de non-régression

Les tests unitaires couvrent QID en clé externe, labels explicites, rôles de statements, candidats non promus, schémas inconnus, `no` ≠ `nb` ≠ `nn`, UTF-8 BOM, dernière ligne sans `\n`, SHA périmé, conflit, déduplication, pause/reprise, et un fichier de **150 001 lignes** dont la dernière entrée correspond à un Q/P accepté. Les tests Python en environnement isolé ne prouvent pas l'exécution Windows native.

## Sources et références

- Chapitres [53–60](53_DIAGNOSTIC_FACTUEL_V5_2_VERS_V5_3.md) : spécification détaillée du contrat.
- [ADR-DIK-LEX-6](../decisions/ADR-DIK-LEX-6-lecteurs-schemas-reprise-sans-activation.md) : décision de séparation inspection / habilitation.
- `src/dik/wikidata_v53.py` : implémentation observatrice.
- `src/dik/resolution14.py` et `src/dik/cli.py` : orchestration/rapports/CLI, dont `dik sources export-v53` pour préparer un ZIP expurgé.
- `src/dik/v53_export.py` : export sans chemins locaux ni formes candidates brutes.
- `tests/test_wikidata_v53.py` : preuve de tests sur fixtures.
