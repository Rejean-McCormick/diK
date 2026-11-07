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
