# diK — Dictionaries and Semantic Identities for Kristal

**diK** is an offline-first Python toolkit for managing multilingual Kristal dictionaries, auditing language coverage, exploring semantic concepts, and reviewing external Wikidata mappings without changing canonical semantic identities.

> **Status: `1.0.0-alpha.7` — experimental software, not a certified 1.0 release.**
> This repository combines the established v0.3 functionality with candidate 1.0 modules and the [diK 1.0 candidate specification](spec/diK-1.0/START_HERE.md). It targets **Kristal Framework `11.0.0-draft.3`**. See [Implementation Status](IMPLEMENTATION_STATUS.md) for unfinished work and limitations.

## Core principles

- **Stable semantic identities:** Kristal's KQ/KP graph is the source of truth. Words and translations live in separate dictionary layers.
- **External IDs stay external:** Wikidata Q/P identifiers are linked through reviewed crosswalks; they never replace or automatically merge KQ/KP identities.
- **Traceable changes:** Curated dictionaries, import snapshots, and proposed crosswalk revisions are published separately rather than silently overwriting canonical data.
- **Reversible projections:** Generate readable, language-specific views while preserving the information needed to restore the original graph.
- **Offline by default:** Inspection, coverage, indexing, projection, and local imports do not require a network connection. Network operations are explicit.

## Features

| Area | Capabilities |
| --- | --- |
| Project inspection | Validate Kristal graphs, identity registries, catalogs, and external crosswalks. |
| Multilingual dictionaries | Audit and resolve labels, compare lexical layers, and identify conflicting preferred terms or shared terms. |
| Language coverage | Report missing, fallback, and directly available labels for KQ/KP concepts, including multi-project portfolios. |
| Search | Build a rebuildable SQLite index and look up lexical candidates by term and language. A candidate is **not** an approved identity match. |
| Projections | Export compact or verbose, annotated or clean views; verify and restore reversible JSON projections. |
| Review and curation | Record append-only review decisions, publish new lexical catalogs, and propose controlled crosswalk revisions. |
| Wikidata | Import approved external labels, compare snapshots, inspect redirect observations, and process large local dumps with checkpoints. |
| Local web interface | Browse concepts and translations, inspect coverage, and export projections in a localhost-only workbench. |

## Requirements

- Python **3.11 or newer**
- `jsonschema >= 4.21, < 5` (installed automatically)
- No database server required; the optional search index uses SQLite.

## Quick start

Run these commands from the repository root:

```bash
python -m pip install -e .

dik --version
dik project inspect --project examples/demo/dik.project.json
dik dictionaries audit --project examples/demo/dik.project.json
dik coverage report --project examples/demo/dik.project.json --locales fr,en,fr-CA
```

Create a local search index and look up a term:

```bash
dik index build \
  --project examples/demo/dik.project.json \
  --output /tmp/dik-search.sqlite

dik index lookup \
  --project examples/demo/dik.project.json \
  --index /tmp/dik-search.sqlite \
  --term 'Saint Augustin' --locale fr --kind KQ
```

The lookup returns lexical **candidates**, not automatically accepted equivalences.

### Launch the local web workbench

```bash
dik serve \
  --project examples/demo/dik.project.json \
  --index /tmp/dik-search.sqlite \
  --port 8765
```

Open **http://127.0.0.1:8765/** in your browser.

The workbench supports three primary workflows: finding a concept and checking its translations, identifying missing language coverage, and reading or exporting a Kristal projection. It is **read-only by default**. Reverse term search requires an index created beforehand; coverage reporting does not.

For optional, isolated lexical curation, provide a workspace **outside the canonical project**:

```bash
dik serve \
  --project examples/demo/dik.project.json \
  --index /tmp/dik-search.sqlite \
  --workspace /tmp/dik-revisions \
  --port 8765
```

This creates **candidate dictionary revisions only**. It does not change the canonical graph, approve Wikidata mappings, or automatically activate new catalogs. Reviewer names are currently declarative, not cryptographically authenticated. The server binds to loopback and is **not intended for public or multi-user deployment**.

## Command reference

| Command | Purpose |
| --- | --- |
| `dik project inspect` | Inspect and validate a project. |
| `dik dictionaries audit\|resolve` | Audit dictionary layers and resolve labels. |
| `dik dictionaries compare\|conflicts\|conflict-detail` | Examine lexical disagreements with provenance, without merging identities. |
| `dik coverage report` | Analyze coverage by language and KQ/KP family. |
| `dik portfolio coverage` | Analyze coverage across multiple Kristal projects. |
| `dik index build\|lookup` | Build the local SQLite index and search for lexical candidates. |
| `dik projection export\|verify\|restore` | Produce, check, and restore reversible projections. |
| `dik review append\|list` | Maintain an append-only decision journal. |
| `dik curate publish` | Publish a new curated dictionary revision. |
| `dik reconcile` | Generate a candidate crosswalk revision from reviewed decisions. |
| `dik patch verify` | Validate a proposed semantic patch without applying it. |
| `dik legacy plan\|verify` | Prepare and verify non-executable legacy migration plans. |
| `dik wikidata import-local` | Import labels from an existing local Wikidata dump. |
| `dik sync ...` | Handle snapshots, mirrored imports, differences, and identity-evolution observations. |
| `dik serve` | Start the local web workbench. |

Use `dik --help` and `dik <command> --help` for the exact parameters.

## Reversible projections

Export an annotated, human-readable view together with the JSON information needed for restoration:

```bash
dik projection export \
  --project examples/demo/dik.project.json \
  --locale fr-CA \
  --format compact --style annotated \
  --output /tmp/dik-fr-CA.json \
  --markdown /tmp/dik-fr-CA.md

dik projection verify \
  --input /tmp/dik-fr-CA.json \
  --project examples/demo/dik.project.json

dik projection restore \
  --input /tmp/dik-fr-CA.json \
  --project examples/demo/dik.project.json \
  --output /tmp/dik-restored-graph.json
```

**Important:** The reversible **JSON** envelope contains the restoration references. The Markdown view alone is not reversible. Exporting a translation or readable view does not alter KQ/KP identities.

## Wikidata workflows

All Wikidata identifiers remain external observations or mappings. They are not imported as new canonical KQ/KP identities, and matching text is never sufficient to establish an `exactMatch`.

### Import a large local dump (alpha.7)

`dik sync import-large` reads supported JSON/JSONL, gzip, and bzip2 dumps, selects labels for **previously approved exact mappings**, and publishes immutable dictionary snapshots. SQLite checkpoints allow interrupted imports to resume.

```bash
dik sync import-large \
  --dump /path/to/wikidata.json.bz2 \
  --crosswalk examples/demo/external-crosswalk.example.json \
  --registry examples/demo/identity-registry.example.json \
  --namespace example.org/kristal-demo \
  --snapshot my-wikidata-snapshot \
  --locales fr,en,fr-CA \
  --root /tmp/dik-imports
```

Optionally supply `--approved-sha256` using a checksum obtained independently of diK. A locally computed hash checks file integrity; **it does not by itself establish source authenticity**.

For compressed inputs, resuming may require re-reading and decompressing earlier records up to the last checkpoint. Full-dump, industrial-scale performance has **not** been validated. See the [alpha.7 import guide](docs/docs/24_IMPORT_INDUSTRIEL_LOCAL_v1-alpha7.md).

### Review Wikidata changes (alpha.4–alpha.6)

The following commands are explicitly initiated by an operator:

- `dik sync fetch`: download a permitted official HTTPS Wikimedia dump with guarded byte-range resumption.
- `dik sync import-mirror`: import a mirrored dump after checking an independently approved SHA-256.
- `dik sync diff`: compare immutable imported lexical snapshots.
- `dik sync probe-redirects`: query the official MediaWiki API only for already-approved external Q/P mappings; **requires network access** and an identifiable User-Agent.
- `dik sync extract-redirects`: normalize archived MediaWiki API responses into immutable observations, offline.
- `dik sync evolution`: review possible mapping impacts from normalized redirect, removal, and split observations, without updating the crosswalk.

A redirect, missing API result, or changed label is **not** proof that two semantic identities should be merged. No automated crosswalk adoption occurs.

See the [mirror workflow](docs/docs/21_MIROIR_WIKIDATA_REPRENABLE_v1-alpha4.md), [evolution analysis](docs/docs/22_EVOLUTIONS_WIKIDATA_v1-alpha5.md), and [MediaWiki redirect adapter](docs/docs/23_EXTRACTION_REDIRECTIONS_MEDIAWIKI_v1-alpha6.md).

## Development and testing

```bash
python -m pip install -e .
python -m pip install 'pytest>=8,<10'
python -m pytest -q
```

GitHub Actions runs the Python test suite and a demo project inspection on pushes and pull requests (see [tests.yml](.github/workflows/tests.yml)). The [validation report](VALIDATION.md) documents the alpha.7 fixture tests and explicitly identifies what has **not** been tested on live or full-size data.

## Current limitations

This is an **alpha release**, not a production-ready, certified 1.0 system. In particular:

- Strong reviewer authentication, digital signatures, and trusted multi-user approvals are not implemented.
- The local web interface is not a hardened, hosted, multi-tenant service.
- Advanced lexical disambiguation and automatic identity reconciliation are not available.
- Complete Wikidata delta processing, industrial-scale redirect ingestion, and full-dump qualification remain unfinished.
- End-to-end publication of a new canonical Kristal through the Authoring Kit, full cross-repository certification, and complete TCK coverage are pending.
- Large-scale real-world benchmarks, recovery after physical failures, and fully validated multilingual coverage at production scale remain to be demonstrated.

**Do not use candidate outputs as canonical identities or treat this release as formally qualified.** For the detailed status, see [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) and [VALIDATION.md](VALIDATION.md).

## Documentation

- [Implementation status](IMPLEMENTATION_STATUS.md) — delivered capabilities and missing requirements
- [Validation](VALIDATION.md) — test evidence and qualification limits
- [Changelog](CHANGELOG.md) — version history
- [Candidate diK 1.0 specification](spec/diK-1.0/START_HERE.md) — contracts and design rationale
- [Project documentation](docs/README.md) — architecture, dictionaries, projections, and workflows (primarily in French)
- [Framework pin](FRAMEWORK-PIN.md) — reference Framework version and source integrity

## License

Licensed under **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**. See [LICENSE](LICENSE) for the repository's license notice and a link to the full license terms.
