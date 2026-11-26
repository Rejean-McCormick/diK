# ADR-08 — Recorded-accepted precedence in new local crosswalk revisions

**Decision:** If the selected local crosswalk already contains a single
accepted, registered-KS-backed Wikidata exactMatch for `(namespace_id,
semantic_id)`, other still-candidate `exactMatch` targets for that SAME
scoped ID are superseded in a NEW registered canonical crosswalk revision.

This does not infer semantic truth from lexical similarity, change any KQ/KP
identifier, accept a new Wikidata QID, merge terms or delete prior candidates.
The source-recorded accepted target and its original review are preserved
unchanged. Cases with multiple unapproved candidate targets and no accepted
target remain unresolved and need domain evidence before future promotion.

The Authoring Kit, not diK, registers the new crosswalk and archives the old
authoring selection. Manager refreshes the active derived lookup afterward.
Historical V5.14/V5.15 inventories remain auditable, and publication is
separate from this local authoring operation.
