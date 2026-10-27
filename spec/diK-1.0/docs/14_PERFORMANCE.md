# 14 — Performance, échelle et protocole de mesure

## PERF-001 — Objectifs, pas promesses déjà atteintes

diK 1.0 vise les centaines de langues, les dictionnaires clairsemés, millions d'enregistrements lexicaux et un gros miroir Wikidata local. Les performances doivent être **mesurées sur une configuration publiée** et ne peuvent pas être déduites des 36 tests de diK 0.3 ou du seul gain de 72,6 % sur 1 000 assertions synthétiques.

### Budgets cibles proposés (à ratifier après mesures)

| Scénario | Budget P95 cible | Conditions |
|---|---|---|
| Lookup index chaud `(namespace,KQ,locale)` | 20 ms local | sans I/O réseau, index SQLite chaud |
| Recherche inverse d'un terme | 100 ms | top 25 candidats, index chaud, domaine connu |
| Projection de 10 000 assertions | 2 s | locale déjà indexée, hors sérialisation physique longue |
| Couverture 100 000 références sur 10 langues | 30 s | mode batch, index chaud, mémoire plafonnée |
| Import 10 M entrées Wikidata | débit documenté | mesurer temps total, mémoire, disque, reprise |

Ces chiffres sont **des hypothèses de qualification** à mesurer et ajuster avec décision de version, pas une assertion de réussite. Le P95 doit porter sur au moins 30 répétitions pertinentes et inclure la variance. Un résultat sur machine non décrite n'a pas valeur de certification.

## PERF-002 — Métriques obligatoires

Taille brut vs compact vs gzip, CPU max/moyenne, RSS max, disque temporaire, lecture séquentielle, nb de shards, débit d'import, taux cache, nombre de fichiers lus, durée de vérification des hashes, temps de reprise/crash, couverture 300 langues sparse, latence UI. Faire essais froid/chaud séparément.

## PERF-003 — Techniques

- Joins via index par ID/crosswalk, pas scans complets de tous les 300 fichiers par lookup.
- Imports en flux ; chunks bornés ; sorted writes/shards ; indexes versionnés ; snapshots immuables.
- Cache-aside par digest de manifeste, pas TTL approximatif pour un cache sémantique.
- Audit complet à publication et incrémental dans le quotidien ; cache de checksums seulement quand fichier/manifest/version validés.
- Projection une seule langue demandée ; `lexicon.entries` unique par ID ; Markdown calculé à la demande.
- Option de sharding graphique future uniquement **nouveau profil**, pas altération `dik.compact-projection/1.0`.

## PERF-004 — Jeu d'essais

S0 : fixture Framework v11. S1 : 1 000 assertions répétitives (comparaison v0.3). S2 : 100k assertions mixtes (littéraux et qualifiers). S3 : 1M identifiants dont plusieurs langues clairsemées. S4 : échantillon représentatif d'un dump Wikidata local. S5 : snapshot énorme/import interrompu/snapshot changé. Toutes les fixtures ont hash, provenance et droits appropriés ; aucune distribution de dump massif dans le dépôt Git.

## PERF-005 — Critère de release

Le rapport de performances joint à la release doit préciser *réussite/échec* pour chaque budget ratifié, version Python/OS/disque/RAM, exact format de fichier et commandes. Pas de « optimisé » uniquement parce que l'archive est plus petite.

## Révision candidate.2

Le protocole de banc détaillé et les limites absolues figurent dans [`26_BANC_PERFORMANCES.md`](26_BANC_PERFORMANCES.md). **Les budgets non ratifiés ne sont pas des KPI atteints.** Le banc officiel est une condition de release, pas une optimisation présumée.
