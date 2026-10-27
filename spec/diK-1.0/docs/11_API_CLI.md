# 11 — CLI et API : contrats publics cibles

## API-001 — CLI sans surprise

**Commandes diK 0.3 à préserver :** `project inspect`, `dictionaries audit|resolve`, `coverage report`, `wikidata import-local`, `projection export|verify|restore`. Compatibilité des options existantes, et `--format verbose` maintenu.

**Extensions 1.0 proposées**, après versionnement des DTO :

```text
dik workspace init|verify|repair-index
dik dictionaries sources list|add|disable
   ... reconcile scan|review|publish
   ... curate propose|review|publish
   ... search --locale fr --kind KQ --term ... [--domain KQ...]
dik wikidata mirror register|status|sync|diff|resume
dik coverage portfolio --projects manifest.json --locales fr,en,... --output ...
dik migration inventory|propose|review|submit --plan ...
dik projection export|verify|restore [--format compact|verbose] [--style clean|annotated]
dik jobs status|cancel|resume --job ...
dik audit verify|history|export
```

Les formes exactes seront finalisées avec tests d'API ; le tableau ci-dessus n'affirme pas l'existence de ces commandes dans diK 0.3.

## API-002 — Interface programme

Éviter les réponses polymorphes non typées. Résultat uniforme : `request_id`, `contract_version`, `status`, `data`, `errors[]`, `input_manifest_digest`, `output_manifest_digest?`, `warnings[]`. `status=success` uniquement si publication complète. `status=proposed` n'est pas `approved`, ni `published`.

### Opérations applicatives proposées

- `GET /v1/health`, `GET /v1/projects/{id}`, `GET /v1/catalogs/{id}/locales`, `GET /v1/identities/{namespace}/{id}`.
- `POST /v1/lookup/reverse`, `POST /v1/coverage/reports`, `POST /v1/projections`, `POST /v1/projections/verify`.
- `POST /v1/import-jobs`, `POST /v1/reconciliation-jobs`, `POST /v1/decisions/{id}/review`, `POST /v1/migration-plans`.
- `GET /v1/jobs/{id}`, `POST /v1/jobs/{id}/cancel`.

Ces routes sont **cibles de design**, non services déjà publiés. Le transport réseau n'est pas obligatoire pour exécuter le cœur ; la CLI doit appeler les mêmes use cases que l'API, sans dépendre du serveur.

## API-003 — Idempotence et conflits

Toute commande mutante accepte un `idempotency_key` ou en dérive une par opération ; même clé / mêmes paramètres => même résultat ; même clé / paramètres différents => `IDEMPOTENCY_CONFLICT`. Édition revue conditionnée à `expected_revision`/hash ; si changement simultané => `REVISION_CONFLICT`. Les opérations de lecture n'altèrent pas les manifestes.

## API-004 — Filtres et pagination

Recherches et matrice de couverture : pagination déterministe, curseur lié au snapshot, tri défini. Une API ne retourne pas silencieusement « tous les concepts de Wikidata » en RAM. Exports massifs en fichiers versionnés + manifestes/hashes.

## API-005 — Codes de sortie CLI

Proposition : `0 success`, `2 invalid_input`, `3 conflict_or_ambiguous`, `4 integrity_or_security_failure`, `5 external_source_unavailable`, `6 approval_required`, `7 contract_mismatch`, `8 partial_or_interrupted_job`, `9 internal_error`. Un code partiel ne doit pas se faire passer pour succès ; les exceptions doivent fournir `error_code` stable sans exposer secret/chemins sensibles.

## API-006 — Local d'abord

API bind `127.0.0.1` par défaut et authentification robuste si mode multiutilisateur; pas d'exposition réseau implicite. Pas de téléchargement réseau lors de la simple ouverture d'un projet. Formats JSON/JSONL strictement documentés et versions explicites.
