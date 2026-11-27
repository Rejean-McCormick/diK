# diK — Dictionaries and Semantic Identities for Kristal
<!-- DIK-DOCS-LOCAL-1 -->
> **Documentation de référence actualisée (22 novembre 2026)** : [localiser puis référencer les ressources linguistiques](docs/DIK_GUIDE_MAITRE_RESOLUTION_LOCALE.md). diK résout une forme à partir d’un KQ/KP et d’une locale ; aucune langue n'est traduite vers une autre. Les chemins GF/Wikidata repérés ne constituent pas une intégration automatiquement active. Le rapport V3 est `PARTIEL`.


**V5.4 :** nouveaux adaptateurs en lecture seule pour candidats d’identité locaux et assertions Wikidata, comparaison avec les liens acceptés *dans le bon namespace*, et rapports de preuves sans publication. [État exact et limites](docs/docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md).

**diK** is an offline-first Python toolkit for managing multilingual Kristal dictionaries, auditing language coverage, exploring semantic concepts, and reviewing external Wikidata mappings without changing canonical semantic identities.

> **Historical V5.4 checkpoint: `1.0.0-alpha.12`, experimental software, not a certified 1.0 release.** The dated note below reports `pyproject.toml` version `1.0.0a16` for the 24 November 2026 snapshot. Verify the active local package before asserting its current version. The Framework pin and historical evidence are unchanged.
> This repository combines the established v0.3 functionality with candidate 1.0 modules and the [diK 1.0 candidate specification](spec/diK-1.0/START_HERE.md). It targets **Kristal Framework `11.0.0-draft.3`**. See [Implementation Status](IMPLEMENTATION_STATUS.md) for unfinished work and limitations.

## Core principles

- **Stable semantic identities:** Kristal's KQ/KP graph is the source of truth. Language-specific lexical forms live in separate dictionary layers; no language-to-language translation is used by identity resolution.
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

### Scanner intégré — 14 langues ciblées

Le scanner natif `dik coverage scan14` produit des CSV (séparateur `;`, UTF-8 BOM) et un rapport JSON. Il inspecte **le projet diK sélectionné** (pas tous les dictionnaires locaux de façon implicite), confirme les couches et leurs empreintes, puis distingue les libellés directs, les replis, les lacunes et les langues non configurées.

```bash
python -m dik coverage scan14 \
  --project examples/demo/dik.project.json \
  --handoff integrations/unesco-mt1-10/handoff.json \
  --out /tmp/dik-scan14-demo
```

Ajoutez `--konstellation <dossier-ou-zip> [--corpus data/demo.pack.json]` pour obtenir un inventaire séparé du corpus et des chaînes UI **sans présumer que ses libellés sont alignés aux KQ/KP de diK**. L'option `--spek` accepte un dossier ou ZIP Spek afin de vérifier les 14 locales cibles. Utiliser un dossier de sortie neuf, hors des sources. Pour les données réelles, remplacez le projet de démonstration par son vrai `dik.project.json`. Voir [guide du scanner](docs/docs/31_SCANNER_14_LANGUES_DIK.md).

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
| `dik coverage scan14` | Produce an audited 14-language KQ/KP gap register with optional unaligned Konstellation inventory. |
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

## Discovery inventory for world dictionaries (proposed DIK-LEX-1)

The [world-dictionary discovery plan](docs/docs/25_COLLECTION_MONDE_DICTIONNAIRES.md) and [proposed ADR](docs/decisions/ADR-DIK-LEX-1-registre-mondial.md) add an **offline, discovery-only** source inventory, separate from the Framework v11 dictionary catalog and reviewed crosswalks. This is **not** a global dictionary import, a validated BCP 47 registry, or a GF integration. No translations are asserted as available.

```bash
python -m dik.source_inventory examples/world-dictionaries/source-inventory.json
python -m pytest -q tests/test_source_inventory.py
```

### World-language code candidates (discovery only)

The source discovery seed also records Wiktionary as a candidate external dictionary under separate attribution/share-alike terms (not imported). A reproducible, offline snapshot of **7,910 ISO 639-3 candidate codes** (including historical, constructed, macrolanguage, and special codes) is available under `examples/world-dictionaries/`. It does **not** certify BCP 47 tags, verify translations, or populate published dictionaries. See [language candidate documentation](docs/docs/26_LANGUES_MONDE_CANDIDATES.md).

```sh
PYTHONPATH=src python -m dik.world_languages inspect \
  examples/world-dictionaries/language-code-candidates.jsonl \
  examples/world-dictionaries/language-code-candidates.manifest.json
```


## DIK-LEX-1 v0.3 — collection mondiale (overlay candidat)

Ce dépôt peut recevoir l'overlay cumulatif **v0.1 + v0.2 + v0.3** (sans patch Git). Lire [DIK-LEX-1-README-OVERLAY.md](DIK-LEX-1-README-OVERLAY.md).

La nouvelle famille de commandes `dik world` gère : 7 910 codes ISO 639-3 candidats, 7 910 emplacements vides de collection, 25 sources de découverte, acquisition explicite et validation conservatrice de registres IANA BCP 47, réconciliation ISO→IANA, observations lexicographiques Wikidata L/S/F et handoff **candidat** vers GF/SemantiK. **Aucun** dictionnaire vérifié, traduction approuvée, crosswalk `exactMatch` ou grammaire GF n'est créé par ce pipeline.

```sh
dik world --help
dik world collection-audit --dir examples/world-dictionaries/collection-slots-v0.3
dik world resource-audit --catalog examples/world-dictionaries/resource-catalog.json
```

Guides : [IANA](docs/docs/27_BCP47_IANA_ET_RECONCILIATION.md), [L/S/F et GF](docs/docs/28_WIKIDATA_LEXEMES_GF_PIPELINE.md), [programme mondial](docs/docs/29_ROADMAP_COLLECTION_MONDE.md). Ces paragraphes décrivent le jalon historique `alpha.7` ; le `pyproject.toml` du snapshot du 24 novembre 2026 déclare le package **`1.0.0a16`**, toujours candidat et sans certification produit stable.

## SemantiK lexical candidate handoff

Use `dik world semantik-knowledge` and `dik world semantik-knowledge-audit` for knowledge-only lexical schema 1.1 outputs. Review of actual GF mappings occurs outside diK in WordBench. See `docs/docs/30_SEMANTIK_GF_HANDOFF_V09.md`.

## Branch 02 final-system alignment (2026-11-09)

See [the English functional handoff and qualification limits](docs/BRANCH02_FRAMEWORK_INTEROP.md). This is an additive, owner-scoped alignment; no canonical state, public release or production deployment is implied.

## V4 — Local resource registry and canonical resolution (alpha.8)

The new **offline, read-only** `dik sources discover` command locates **existing** local GF, Wikidata and Framework v11 resources without copying them or assuming that a spelling maps to a KQ/KP. It writes a dated `source-registry.json` under `diK/reports/resources` (not to a Kristal), with path references, SHA-256 when within budget, explicit candidate type and zero automatic activation. `dik sources verify` checks the saved references.

```bash
python -m dik sources discover --sources-root /path/to/mycode --dik-root .
python -m dik sources verify --registry reports/resources/resource-registry-latest.json
python -m dik coverage resolve14 --sources-root /path/to/mycode --resource-registry reports/resources/resource-registry-latest.json --min-kristals 126
```

`resolve14` audits only the **official portfolio** and validates each referenced v11 catalog with the Framework checks before lexical use. `--wikidata-source-id` requires explicit selection of a registered Q/P dump candidate; it does not approve source licensing or GF alignment. The GF `.gf`/`.pgf` files and Wikidata thematic JSONL files found are **not** automatically KQ/KP dictionaries. See [V4 implementation](docs/docs/44_SOURCE_MANAGER_V4_IMPLEMENTATION.md), [Windows procedure](docs/docs/45_COMMANDES_V4_WINDOWS.md) and [limitations](docs/docs/46_VALIDATION_ET_LIMITES_V4.md). No translation between languages.

### Distribution V4 révisée — note de sûreté

La distribution du 23 novembre 2026 corrige le lanceur PS7 à portefeuille unique et rend la commande `sources verify` non silencieuse sur les références périmées. La **copie du dépôt** et le **correctif installable** sont deux parties distinctes du ZIP : l'installation protégée ne remplace que les chemins présents dans son manifeste, et non chaque fichier historique. Les manifestes `RELEASE*` alpha.7 sont historiques. Voir [47 — Revue du pack](docs/docs/47_REVUE_PACK_V4_1.md).

## V5 — Qualify actual local resources before lexical use (alpha.9, experimental)

`dik sources qualify --registry <saved-registry> --dik-root <dik-repository>` creates an offline, read-only report about all located sources and their SHA-256/semantic-readiness state. `dik coverage resolve14 ... --resource-registry <saved-registry> --observe-qid-lexicon` optionally records explicitly labelled QID observations *separately*, without counting them as resolved words. GF dictionaries do not become KQ/KP-aligned by discovery; Wikidata L/S/F is distinct from Q/P. See [qualification](docs/docs/48_QUALIFICATION_SOURCES_REELLES_V5.md) and [QID/GF limits](docs/docs/49_OBSERVATIONS_QID_ET_LIMITES_GF_V5.md). No translations between languages, no network.


## V5.2 — Audit des JSONL Wikidata thématiques (alpha.10 expérimental)

La commande `dik coverage resolve14 --resource-registry <fichier> --observe-qid-lexicon --observe-wikidata-thematic` vérifie les pointeurs locaux et compare les Q/P explicites aux correspondances `exactMatch accepted` auditées des Kristals officiels. Les deux CSV thématiques produits contiennent **seulement des observations candidates** ; l'inventaire de 40 JSONL ne constitue **pas** un dump mondial. Aucun mot n'est inféré depuis une autre langue, depuis une `lemma` GF ou par similitude d'orthographe. Voir [chapitre 52](docs/docs/52_AUDIT_WIKIDATA_THEMATIQUE_V5_2.md) et [ADR 5](docs/decisions/ADR-DIK-LEX-5-jsonl-thematiques-en-candidats.md).


## Documentation de conception V5.3 (2026-11-23) — **pas encore du code**

Le bilan Windows V5.2 a confirmé 40 sources Wikidata thématiques, 37 effectivement inspectées, 2 tronquées et **aucun Q/P reconnu par le lecteur actuel**. Un schéma inconnu ne prouve pas qu'aucun Q/P existe. Les [chapitres 53 à 60](docs/README.md#v53--spécification-du-nouveau-système-de-lecture-2026-11-23) définissent maintenant les adaptateurs par schéma, la lecture streaming avec reprise, les statuts de preuve et les tests à implémenter **dans un second temps**. Le code et la version installée restent V5.2 ; aucune source n'est activée par ce pack documentaire.


### V5.3 alpha.11 — Inspection Wikidata avec reprise

`dik coverage resolve14 --observe-wikidata-thematic` utilise un lecteur de schémas JSONL explicites et des checkpoints SQLite sous `reports`. Seules les correspondances Q/P **acceptées** sont jointes ; aucune forme candidate n’est publiée. Voir [chapitre 61](docs/docs/61_IMPLEMENTATION_EFFECTIVE_V5_3.md).


## V5.5 alpha.13 — Tableau JSON GF-Wikidata réel

Quatre fichiers `.jsonl` de `gf-wikidata-tools/data` sont en réalité des tableaux JSON multiligne. Le lecteur détecte leur conteneur, examine les identités `url` et `labels` exacts, conserve la reprise SQLite et rapproche uniquement les QID des liens KQ/KP déjà acceptés. Libellés candidats uniquement, pas de traduction ou de publication. Voir [chapitre 63](docs/docs/63_ADAPTATEUR_GF_WIKIDATA_TABLEAUX_JSON_V5_5.md).


## V5.6 alpha.14 — Sources lexicales en ligne, ciblées par identité

La V5.6 ajoute `dik sources online-catalog` (Wikidata, Kaikki et GF) et `dik sources online-fetch --allow-network` (API officielle **Wikidata seulement**). Les requêtes utilisent exclusivement les Q/P des `exactMatch accepted` vérifiés avec preuves KS dans les v11 sélectionnées ; elles ne transmettent aucun namespace ni KQ/KP. Cache content-addressed SHA-256, reprise, restrictions de langue strictes, et nouvelles observations dans `coverage resolve14 --online-index` **sans approbation automatique**. `sources export-v56` crée un bilan expurgé. Kaikki et GF en ligne sont pour l'instant référencés, pas téléchargés ni alignés automatiquement. Voir [chapitre 64](docs/docs/64_SOURCE_MANAGER_EN_LIGNE_CIBLE_WIKIDATA_V5_6.md).


## V5.7 alpha.15 — DIK-LEX-1 : 14 dictionnaires candidats à partir de l’index EncyK local

La V5.7 transforme la collection mondiale **déclarative** en 14 bases SQLite
candidates persistantes, construites à partir de **toutes les lignes éligibles**
de l’index lexical EncyK déjà téléchargé sur `D:`. Commandes `dik world
local-plan14`, `local-build14`, `local-status14`, `local-lookup` et
`local-export14`. Lecture de la source en `mode=ro`, reprise par curseur,
dédoublonnage par ligne originale, dictionnaires sur `D:\diK\lexical`,
rapport expurgé. Une entrée lexicale observée ne devient jamais un sens ou une
forme publiée sans revue des sources et des licences. Voir [chapitre 65](docs/docs/65_COLLECTION_LOCALE_14_LANGUES_ENCYK_V5_7.md).

## V5.8 — Pont local des preuves EncyK, sans duplication massive

Les 14 bases lexicales V5.7 restent intactes. Les commandes `dik world local-semantic-plan14`,
`local-semantic-bind14`, `local-semantic-lookup` et `local-semantic-export14`
permettent de consulter, en lecture seule, les preuves candidates de la
réconciliation EncyK v0.5 et de l'enrichissement v0.6. Aucune activation,
licence ou équivalence KQ/KP automatique. Voir
[chapitre 66](docs/docs/66_PONT_ENCYK_PREUVES_DE_SENS_V5_8.md).

## Raccordement fédéré diK — candidat (23 novembre 2026)

Voir [`docs/docs/68_REGISTRE_SEMANTIQUE_FEDERE_INTEROP_V5_9.md`](docs/docs/68_REGISTRE_SEMANTIQUE_FEDERE_INTEROP_V5_9.md). Cette mise à jour fournit un précontrôle ou un index dérivé en lecture seule; aucune admission, migration ou publication n’est implicite.

### V5.10 — Canon multirévision sans renumérotation

Le registre fédéré dérivé (`dik world federation-build`) lit désormais aussi les
`canon/state.index.json` officiels, en préservant toutes les révisions V11
séparément dans des tables de preuves sources. La version source active n'est
**jamais inférée** : ses liens `accepted` ne sont pas promus automatiquement.
La consultation distincte est disponible via `dik world federation-revision-query`.
Guide : `docs/docs/69_INDEX_CANONIQUE_MULTIREVISIONS_V5_10.md`.

### V5.11 — Sélection contrôlée des révisions V11 pour une vue dérivée

Le registre fédéré indexe désormais les empreintes SHA-256 des artefacts V11
et propose `dik world federation-selection-query` / `federation-selection-review`.
Une seule révision complète déclarée peut être consultée en vue dérivée.
Plusieurs révisions ne sont jamais choisies par date ou nombre d'identités ;
une décision explicite et épinglée aux empreintes est nécessaire. **Aucune
nouvelle équivalence Wikidata n'est approuvée par ce mécanisme.** Les 13
langues cibles et les 14 bases historiques restent distinctes. Lire le
[chapitre 70](docs/docs/70_SELECTION_REVISIONS_CANONIQUES_V5_11.md)
et l'ADR de sélection.

**Durcissement de sélection (profil de décision `/0.2`) :** l'opérateur doit
également épingler le SHA-256 du graphe inspecté. Les fichiers de revue `/0.1`
ne sont plus acceptés pour construire de nouvelles vues dérivées ; aucune
sélection historique ou correspondance Wikidata n'est promue automatiquement.
Voir [ADR-DIK-FEDERATION-03](docs/decisions/ADR-DIK-FEDERATION-03-selection-graphe-epingle.md).
