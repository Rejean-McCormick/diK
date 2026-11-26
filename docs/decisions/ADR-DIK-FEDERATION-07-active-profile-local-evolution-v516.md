# ADR-07 — Active profile and reversible local semantic evolution V5.16

**Decision:** A practical semantic dictionary is generated from each local
Kristal's already-adopted v11 authoring profile, not from a pooled vote across
every historical update. The identity key remains `(namespace_id, KQ/KP/...)`;
Wikidata Q/P values remain external identifiers. Human-readable terms, language
and source-layer priority are preserved.

Manager writes a versioned **derived** reading projection inside the local
workspace, with a backed-up pointer to the active projection. It does not
rewrite `canon/`, reclassify candidates as accepted, coalesce homonyms,
publish or change the authority of diK versus Authoring Kit.

V5.15's historical review cases remain valid as *historical observations*,
but are not automatically conflicts in the active effective view. V5.16
specifically fixes the user-facing inability to obtain the selected active
meaning and its Wikidata linkage from the total multi-revision inventory.

Changes of canonical meaning still require a new registered, reviewed v11
artifact using the Kit, and never an in-place mutation of an old artifact.
