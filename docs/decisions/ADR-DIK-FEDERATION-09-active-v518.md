# ADR-DIK-FEDERATION-09 — Active, namespace-scoped federation (V5.18)

**Status:** implemented locally as a derived candidate, not a normative
Framework amendment or independently qualified release.

## Decision

The total semantic search index is generated from exact local Kristal
authoring selections. Its key is `(namespace_id, semantic_id)`, with explicit
source provenance. Identity labels are secondary lexical records. Wikidata
Q/P references are external alignments, never canonical KQ/KP replacements.

The V5.14 historical inventory remains useful as evidence, but the active
federation must not mix unselected revision identities into current lookups.
Historical curated term consensus can enter an *unreviewed suggestion* table
without changing canonical dictionaries. Conflicting and ambiguous candidates
are reported rather than silently promoted.

V5.17 and V5.16 remain the local canonical-evolution and derived-view inputs.
V5.18 creates only a private indexed read model and an unapproved
local/public comparison plan. Public synchronization is the responsibility of
the separately authorized publishing path.
