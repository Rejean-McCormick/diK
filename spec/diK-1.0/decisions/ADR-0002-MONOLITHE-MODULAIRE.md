# ADR-0002 — Monolithe modulaire + architecture hexagonale

- **Statut** : proposé (choix diK, non exigé par le Framework).
- **Contexte** : application locale polyvalente, reprise/import massif, absence d'exigence de distribution multi-services.
- **Décision** : domaines sans IO, use cases isolés, adaptateurs Wikidata/FS/SQLite/Authoring/UI ; CQRS local pour index dérivé ; import idempotent/snapshots immuables ; cache indexé par digests.
- **Options rejetées en 1.0** : microservices obligatoires, bus distribué, Event Sourcing global, architecture multi-cellules.
- **Conséquences** : déploiement simple et tests hors ligne ; modularité contrôlée par tests d'import ; évolution possible sans casser le modèle canonique.
- **Critères** : OPS-001..015, tests index rebuild/crash et audit de dépendances.
