# ADR-DIK-LEX-5 — Référencer les JSONL thématiques sans activation implicite

- Date : 2026-11-23
- Statut : **proposé, implémentation expérimentale V5.2** ; non ratifié comme politique de publication

## Décision

Les fichiers Wikidata thématiques repérés par Source Manager sont inspectés **hors-ligne** et **en lecture seule** avec vérification taille/SHA. Les libellés doivent être des champs explicites et leur Q/P doit déjà être relié à un `(namespace_id,KQ/KP)` par un `exactMatch accepted` et des preuves KS auditées. Les observations restent **candidates** et ne deviennent pas des dictionnaires actifs, quelle que soit leur proximité lexicale ou la qualité apparente de leur couverture linguistique.

`identity-candidates.jsonl` et `statements.jsonl` sont des sources de candidates/statements ; ils ne deviennent pas des lexiques de résolution par le seul suffixe JSONL. Le format doit être examiné. Conflits, troncature, copies et échecs d'empreinte sont explicitement rapportés.

## Conséquences

Aucun effet sur les compteurs de couverture ni les sources des 126 Kristals. La revue de provenance et licence demeure séparée, ainsi que le rattachement GF et Wikidata L/S/F. Pour publier un jour des formes, il faudra un **contrat de validation versionné** et une approbation explicite des sources, au-delà de la V5.2.
