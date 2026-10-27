# 09 — Architecture : monolithe modulaire et ports/adaptateurs

## OPS-001 — Structure recommandée

```text
src/dik/
  domain/           # IDs, résolution, décisions, composition, invariants ; sans SQL/HTTP/IO
  application/      # use cases : import, revue, audit, couverture, projection, migration candidate
  ports/            # interfaces Reader/Writer/Registry/Catalog/Crosswalk/Clock/Verifier
  adapters/
    framework/      # schémas/validations versionnées Framework (pas une réécriture)
    wikidata/       # dump parser, change feed, HTTP explicite
    filesystem/     # snapshots et publications atomiques
    sqlite/         # index dérivé, cache, transactions locales
    authoring/      # plans de migration vers producteur autorisé
    integration/    # lectures/projections Integration Pack
  entrypoints/      # cli, api, ui, jobs
  observability/    # logs/metrics/codes d'erreur
```

Structure **cible**, pas arborescence du code 0.3. Les modules peuvent commencer dans un même processus Python.

## OPS-002 — Règle des dépendances

`entrypoints -> application -> domain`, `adapters -> ports/domain` via injection. Le domaine n'importe ni SQLite ni requests/urllib ni frameworks web. Un `CatalogReader` vérifie les artefacts Framework ; un `IndexReader` sert les recherches mais ne crée aucun concept. Les writes passent par commandes explicites, les reads par vues dérivées (**CQRS local léger**, pas besoin Kafka).

## OPS-003 — Bounded contexts

- `identity` : référents et types, normalisation, namespace.
- `lexical` : couches, fallbacks et sélection.
- `alignment` : crosswalk/revue/décisions.
- `ingestion` : import/version/format/snapshot.
- `projection` : compact/verbose/render/restore.
- `coverage` : inventaire et calculs.
- `migration` : plans et demandes au producteur.
- `workspace` : stockage/transactions/index et sessions.

Chaque contexte expose DTOs/contrats stricts ; pas de `dict[str,Any]` non validé traversant toutes les couches.

## OPS-004 — Patterns retenus, sans sur-ingénierie

Anti-Corruption Layer pour Wikidata et legacy ; Hexagonal Architecture pour le domaine ; Modular Monolith pour déploiement simple ; CQRS interne pour index rapides ; Idempotency pour les jobs ; Cache-Aside pour résolutions ; Immutable Infrastructure (par analogie) pour snapshots ; Strangler Fig pour migration progressive des anciens Kristals. **Pas** de service mesh, microservices obligatoires, Event Sourcing global ou système distribué requis en 1.0.

## OPS-005 — Déterminisme

À entrées/version identiques, résultat sémantique identique. Ordre stable des entrées, canonical JSON pour hashes défini, gestion UTF-8/NFC explicite, horodatage/auteur séparés de la partie reproductible, politique de tie/conflict non basée sur l'ordre SQL ni un dictionnaire Python arbitraire.

## OPS-006 — Import Framework

Remplacer les copies vendoriées par un composant upstream épinglé **si disponible et contractuellement compatible** ; à défaut conserver avec hash et tests de comparaison. Ne jamais « améliorer » silencieusement les validateurs v11 embarqués.
