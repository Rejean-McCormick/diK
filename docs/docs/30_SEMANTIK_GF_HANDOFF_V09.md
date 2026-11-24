# diK → SemantiK / GF lexical handoff — v0.9

Owner: **diK** (lexical observations and source identity). This document defines a
candidate exchange, not a new dictionary authority or automatic GF mapping.

## Inputs and public operations

Given a *verified* `dik.wikidata-lexeme-observations/0.1-candidate` directory:

```powershell
cd C:\mycode\diK\diK
$env:PYTHONPATH = 'src'
python -m dik.cli world gf-handoff --observations C:\lex-data\observations --locale fr --output-dir C:\lex-data\gf-fr
python -m dik.cli world semantik-knowledge --handoff C:\lex-data\gf-fr --output-dir C:\lex-data\sa-knowledge-fr
python -m dik.cli world semantik-knowledge-audit --dir C:\lex-data\sa-knowledge-fr
```

Outputs are immutable `semantik.knowledge.json` (SemantiK lexical-artifact 1.1),
`gf-mapping-review.template.json`, and an SHA-256 manifest.

- Each source Lexeme `L…` remains `wikidata:lexeme:L…`, **not** a Kristal identifier.
- Every lexical entry has `use_for=knowledge`, `binding_kind=lexeme_ref`,
  `source_kind=wikidata`. No GF constructor or grammatical sense is inferred.
- The review template contains no accepted decisions or GF functions.
- The source license, category, sense and semantic owner must be reviewed upstream
  before generating binding candidates in WordBench.
- A Lexeme `L…` alone is not a unique asserted sense or truth claim.

No file is activated as a RuntimeSet; existing diK contracts are unchanged.


<!-- DIK-DOCS-LOCAL-1 -->
## Actualisation documentaire — 22 novembre 2026

Les ressources GF indexées restent candidates tant qu’aucune fonction/catégorie n’est explicitement liée à un KQ/P par décision qualifiée. Voir le [guide maître](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md), les [chapitres 34–43](../DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md) et l’[ADR DIK-LEX-2](../decisions/ADR-DIK-LEX-2-localiser-et-referencer.md). Ce complément est documentaire et ne change pas les contrats du Framework.
