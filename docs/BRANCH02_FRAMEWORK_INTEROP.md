# Branch 02 — diK lexical candidate preparation versus Framework v11

**State:** diK alpha.7; implementation baseline `11.0.0-draft.3`; schema-byte-parity with supplied Framework draft.4 **locally verified**. No automatic normative upgrade.

## Functional split

- **Framework** owns semantic identity and the canonical KQ/KP/KA/KS graph.
- **diK** owns candidate linguistic dictionaries, external Wikidata observations, lexical coverage, and reviewable conversion/materialization inputs. A Q/P external identifier does not identify a KQ/KP, and a direct lexical match does not establish `exactMatch`.
- **Authoring Kit** decides whether to admit and register a specifically reviewed catalog; it owns the local canonical workspace and transaction journal.
- **Kristalizer and SenTient** may contribute proposals. No proposal is automatically accepted as a semantic identity or a permitted Kit write.

## Read-only source parity test

```bash
PYTHONPATH=src python -m dik.framework_compatibility --framework ../Framework
PYTHONPATH=src python -m pytest -q tests/test_branch02_framework_parity.py
```

This tool compares **all 11 vendored v11 schema files** to the provided independent Framework checkout and refuses an altered byte, missing schema or unknown version. The Framework 11.0.0-draft.4 snapshot supplied alongside this checkout retains the same v11 schema bytes. The script reports its source versions and states that runtime and import qualification are outside scope. It does not mutate either repository, download Wikidata or declare authenticity of an external source.

## Final-system integration gates

1. Preserve all historical imported records, source digests and curated layers; do not rewrite Framework contracts or legacy state to force a match.
2. Send proposed catalog/identity changes only through the Kit's versioned, authorized candidate importer, with explicit recipient rejection/receipt. Keep source Q/P/KS evidence and reviewer decisions separate.
3. Distinguish `direct`, `fallback`, `missing` and conflicts per locale. A fallback label is not a verified direct translation.
4. Source SHA-256 does not prove that a Wikidata mirror was authenticated upstream; `upstream_verified` needs independent approved evidence.
5. Use exact source, graph and catalog hashes, plus positive and negative tests on an actual Kit importer before elevating the handoff beyond `SOURCE_PARITY`.

**Unresolved decisions:** exact approved external candidate envelope, final Framework/diK compatibility version, reviewer authentication and complete end-to-end producer/consumer test. These require owner review, not an invented universal profile ID.
