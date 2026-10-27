# 17 — Traçabilité exigences → modules → tests

**Règle IA :** chaque PR met à jour ce tableau pour ses exigences, sans retirer une ligne incommodante. `TARGET` = pas encore implémenté/certifié.

| ID | Exigence source | Module cible | Tests de preuve requis | État initial |
|---|---|---|---|---|
| ID-001..005 | Framework Identity-and-Wikidata | domain/identity | ID-R1..R6 | upstream + partiel v0.3 |
| LEX-001..006 | Framework Dictionary-Management | domain/lexical, adapters/fs | LEX-R1..R8 | partiel v0.3 |
| XW-001..005 | Framework Identity-and-Wikidata | domain/alignment | XW-T1..T7 | TARGET |
| IMP-001..005 | Framework Dictionary-Management | adapters/wikidata | IMP-T1..T6 | import local v0.3, reste TARGET |
| PRJ-001..007 | diK v0.3 compact/verbose + Framework | domain/projection | PRJ-T1..T8 | partiel v0.3 |
| MIG-001..006 | Framework Legacy-Resolution / diK-Interoperability | app/migration, authoring adapter | MIG-T1..T9 | TARGET |
| COV-001..006 | Framework diK-Interoperability | app/coverage | COV-T1..T6 | mono-graph v0.3, reste TARGET |
| OPS-001..015 | Patterns #08,#10,#12,#15,#18,#25,#31 | app/ports/adapters/workspace | atomic/crash/cache/rebuild | TARGET |
| API-001..006 | Décision diK cible | cli/api | compat v0.3, contrats erreurs | TARGET |
| UI-001..006 | Décision diK cible | ui | workflow, accessibility, RTL | TARGET |
| SEC-001..007 | Décision diK cible | boundaries | SEC-T1..T9 | TARGET |
| PERF-001..005 | Décision diK cible | benchmarks | S0..S5 | TARGET |
| TCK-001..006 | Framework Conformance + diK cible | tests/CI | G1..G8 | TARGET |

## Règle pour les changements

Dans un PR : `requirement_id`, `source_reference`, `acceptance_test`, `expected_failure`, `evidence_file`, `impact_legacy`, `state`. Ne jamais convertir `TARGET` en `DONE` sans test exécuté, output enregistré et preuve lisible. Une exigence contredisant le Framework est `BLOCKED` et une ADR est nécessaire.

## Révision candidate.2 — registre individualisé

Le fichier [`../tests/requirements.json`](../tests/requirements.json) développe les plages d'identifiants ci-dessus en enregistrements individuels. Tous ont un résultat produit initial `NOT_RUN`, et deux scénarios `positive`/`negative`. L'enregistrement d'une preuve réelle est réalisé par CI d'implémentation, pas par édition à la main du tableau.
