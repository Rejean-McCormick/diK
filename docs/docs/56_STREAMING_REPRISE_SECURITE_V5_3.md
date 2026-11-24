# 56 — Lecture progressive, reprise et intégrité des grandes sources (V5.3)

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Spécification future, non implémentée.** Les limites V5.2 restent en vigueur tant que le code n'a pas été modifié.

## Constat V5.2

`City.jsonl` et `University.jsonl` ont chacune atteint la limite de **150 000 lignes**, pour un total de **333 849 lignes lues** sur les 37 sources inspectées. Le flag `truncated=true` a été conservé ; il interdit de conclure qu'une source ne contient aucun Q/P commun. Les plafonds V5.2 sont 64 MiB/fichier, 2 000 000 caractères/ligne et 40 000 paires de formes. Des plafonds empêchent les plantages, mais ils ne constituent **pas** une lecture complète.

## Contrat de lecture de V5.3

- Traitement **streaming** d'un JSON par ligne, mémoire bornée ; ne pas charger un JSONL entier en RAM.
- Chaque source possède un `source_id`, un SHA-256 initial, un `schema_id`, une version d'adaptateur et une position de reprise. Conserver les **offsets binaires** et le numéro de ligne, en plus du nombre d'enregistrements valides.
- Les budgets (`bytes`, `rows`, durée, erreurs, paires) sont configurables et inscrits dans le manifeste du scan. Une limite atteinte donne `partial_budget`, jamais `completed` ni `no_overlap`.
- Checkpoint écrit **sous `diK/reports/`**, par écriture temporaire puis renommage atomique. Ne jamais écrire dans le répertoire source.
- Reprise uniquement si `(source_id, sha256, size, schema_id, adapter_version, policy_version)` et les paramètres impactant l'extraction correspondent. Sinon invalider le checkpoint et recommencer au début. Ne pas reprendre sur un fichier modifié.
- La reprise doit se placer sur une **frontière de ligne** vérifiée ; elle ne doit ni dupliquer ni oublier une observation. Les comptes doivent être reproductibles avec et sans interruption.
- Les observations doivent porter une clé de déduplication incluant source/empreinte/offset/Q/P/locale/type ; une copie identique du fichier n'augmente pas les comptes d'identités.
- Contrôler la signature de la source **avant et après** la lecture (ou par un mécanisme équivalent protégeant de la modification concurrente) ; une modification pendant le scan rend les observations non admissibles et l'exécution `stale`.
- Les erreurs UTF-8, JSON malformé, schéma incohérent ou ligne excessive sont comptées. Une politique de rejet déterministe s'applique ; une forte proportion d'erreurs rend le lot `incomplete_errors`.

## Décisions en cas de limite

| Condition | Statut | Conséquence autorisée |
|---|---|---|
| EOF atteint, fichier stable, parseur connu | `completed` | Peut tester l'absence d'intersection Q/P |
| Ligne 150 001 atteinte selon budget | `partial_budget` | Rapport partiel + checkpoint ; **pas** de « aucun Q/P » |
| Empreinte différente à la reprise | `stale_source` | Suspendre ; pas de réemploi des données précédentes |
| Format non validé | `schema_unknown` | Profil uniquement, aucune affirmation sur intersection |
| Erreur JSON/UTF-8 sous seuil | `completed_with_rejections` (si EOF) | Diagnostic avec exclusions, pas de couverture exhaustive sur les lignes rejetées |
| Trop de corruptions / source illisible | `incomplete_errors` | Refus de publication, réessai ou intervention |
| Contradiction entre deux labels | `conflict` | Paires concernées exclues des formes utilisables |

Le fait d'avoir atteint EOF ne prouve pas le contenu lexical : **l'extraction Q/P et le profil doivent aussi être valides**.

## Checkpoint proposé (exemple non normatif)

```json
{
  "profile": "dik.wikidata-scan-checkpoint/0.1-proposal",
  "source_id": "local-example",
  "sha256": "<empreinte source vérifiée>",
  "schema_id": "wikidata-topic/example-v1",
  "adapter_version": "future-5.3",
  "offset_bytes_next": 1024,
  "line_next": 16,
  "rows_valid_json": 15,
  "status": "partial_budget",
  "no_publication": true
}
```

Cette illustration **ne doit pas être chargée par la V5.2** ; elle ne définit pas un schéma canonique Framework.

## Traces et confidentialité

Les journaux doivent enregistrer la racine et le `source_id` dans la copie locale, les exceptions de parsing sous forme de catégorie et les positions de lecture. Ne jamais archiver automatiquement les 40 JSONL, des champs privés, des lignes brutes ou des chemins Windows dans un ZIP destiné au partage. Un mode local complet et un mode export expurgé doivent être distincts.

**Tests obligatoires :** scan continu = scan en deux reprises ; source modifiée avant/après lecture ; fichier coupé au milieu d'une ligne ; dernière ligne sans `\n` ; UTF-8 BOM ; caractères non latins ; gros JSON ; double exécution idempotente ; arrêt imposé aux 150 000 lignes puis reprise jusqu'à EOF ; désactivation de tout fallback de langue.
