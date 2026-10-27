# 26 — Qualification performance, confidentialité et grande échelle

Ce chapitre **n'affirme aucune performance déjà atteinte par diK 1.0**. Les budgets de `14_PERFORMANCE.md` sont des candidats soumis à ratification ; toute qualification doit être mesurée puis archivée avec le commit.

## Profils distincts

- **S0** : fixture Framework v11, objectif exactitude, sans benchmark.
- **S1** : 1 000 assertions répétitives pour mesurer compact JSON et gzip ; documenter ratio sur données brutes et compressées.
- **S2** : 100 000 assertions de tailles variées (refs, qualifiers, littéraux, Unicode). Mesurer P50/P95, RSS, taille, pertes nulles après restore.
- **S3** : 1M de référents, 301 locales clairsemées. Ne préallouer aucune matrice dense ; mesurer couverture, index SQLite, mémoire et durées froid/chaud.
- **S4** : échantillon réel de la copie Wikidata avec provenance/attribution et snapshot digest ; import à mémoire bornée, sharding et delta.
- **S5** : interruption aux étapes d'import et de publication, index détruit/reconstruit, reprise après pointeur cassé ; la justesse prime sur le débit.

## Méthode de mesure reproductible

1. Déclarer OS, version Python, type CPU/cœurs, RAM, disque SSD/HDD, version SQLite, versions de dépendances et SHA du programme.
2. Établir un warmup, exécuter ≥ 30 mesures individuelles pour P95, rendre P50/P95/min/max et distribution de latence sans cacher les échecs.
3. Distinguer *cold index* / *warm index* / *warm cache*, I/O réseau interdit sauf test explicitement dédié. Inclure coût de validation à publication et de reconstruction d'index.
4. Mesurer CPU max/moy, pic RSS, disque temporaire maximal, volume du dump d'origine, taille lexicale totale, temps de reprise, nb de ressources mises en quarantaine et nb de fichiers ouverts.
5. Comparer diK v0.3 existant et diK 1.0 dans des conditions identiques ; chaque optimisation doit préserver l'oracle et les hashes historiques.
6. Publier les seuils **ratifiés** dans un manifest de benchmark approuvé ; avant cette étape on rapporte métriques, et on n'attribue pas de statut « optimisé/certifié ».

## Conditions de blocage indépendantes des budgets chiffrés

OOM, corruption, création de mapping fictif, double publication, utilisation d'un mot comme KQ, pertes d'historique, résultat de couverture inexact, résultat différent selon ordre des fichiers => **FAIL** même si rapide.

## Approches attendues

Index SQLite FTS (source dérivée) avec clé `(namespace,id,locale,catalog_sha)`, cache-aside invalidé par empreinte, lecture seule des snapshots et chargement de la langue demandée, pipeline stream JSONL par lots bornés, publication atomique, reproductibilité des sorties. Le modèle doit fonctionner sans 300 copies intégrales de Wikidata.
