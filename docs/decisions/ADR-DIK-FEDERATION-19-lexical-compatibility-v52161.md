# ADR-DIK-FEDERATION-19 — Scoped graph-only review

Use scripts/read_lexical_compatibility_v52161.py with --framework, --generation, --report-sha256 (trusted digest) and --purpose private-review to read an active-graph or active-assertion where lexical qualification is blocked. Default active-only refuses non-strict graphs. History subcommand takes namespace and KA and returns historical observation only, never active authority. Existing reader versions remain unchanged. No automatic lexical correction, no canonical/public changes.
