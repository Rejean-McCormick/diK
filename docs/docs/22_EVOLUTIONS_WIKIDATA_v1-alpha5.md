# diK alpha.5 — impact des évolutions d'identité Wikidata

**Contrat applicatif candidat, non normatif Framework v11.**

## Invariants

- Les identifiants Kristal KQ/KP restent **inchangés**. Les identifiants Q/P restent externes.
- Une redirection Wikidata n'est **pas** une équivalence sémantique démontrée. Un rapprochement de deux Q n'autorise jamais la fusion de deux KQ.
- Une scission est une *hypothèse de révision* : les dumps lexicaux ne suffisent pas à la prouver.
- Le graphe canonique, les anciennes correspondances et les dictionnaires sont lus, jamais réécrits.
- Le rapport ne publie aucune décision ; `source_reference` et `source_snapshot` décrivent une provenance alléguée, pas une preuve cryptographiquement authentifiée.

## Entrée normalisée

La commande `sync evolution` prend un **JSONL de diK**, pas un dump Wikidata `latest-all.json` directement. Chaque objet suit `src/dik/contracts/dik-wikidata-evolution-event.schema.json`.

```json
{"event_type":"redirect","source_id":"Q8018","targets":["Q99000"],"source_snapshot":"illustrative-2026-10-16","source_reference":"fictional-offline-test:line-1"}
```

`event_type` : `redirect` (une cible), `retired` (aucune cible), ou `split_candidate` (au moins deux cibles). Les éléments sont homogènes Q→Q ou P→P. Le format n'admet pas les libellés comme identifiants. Toute entrée doit correspondre au `--snapshot` demandé et les doublons sont interdits. Les observations doivent être extraites de **sources Wikidata contrôlées indépendamment** par un adaptateur ; cette version ne propose pas encore d'adaptateur vérifié aux formats natifs de redirections/deltas Wikimedia.

Une empreinte SHA-256 approuvée peut être fournie avec `--approved-sha256` ; cela vérifie **les octets du JSONL normalisé**, pas l'authenticité des faits Wikidata ni la qualité de la normalisation.

## Utilisation

```bash
dik sync evolution \
  --observations examples/wikidata-evolution/observations.jsonl \
  --crosswalk examples/demo/external-crosswalk.example.json \
  --registry examples/demo/identity-registry.example.json \
  --namespace example.org/kristal-demo \
  --snapshot illustrative-2026-10-16 \
  --output /tmp/dik-evolution-report.json \
  --events /tmp/dik-evolution-impacts.jsonl
```

Ces fichiers doivent être absents avant l'exécution. La sortie JSONL fournit toutes les correspondances actives affectées ; le rapport JSON contient une synthèse et un échantillon limité (`--sample-limit`). Le choix de sortie reste non destructif.

## Résultats et interprétation

- `redirect_chain` : la cible Q/P proposée est celle de la chaîne observée. **Elle n'est pas automatiquement adoptée ni nécessairement vérifiée comme existante.**
- `redirect_collision_review` : deux KQ/KP différents aboutiraient au même Q/P externe après redirection ; c'est un **conflit potentiel**, pas une fusion.
- `retired_external_identifier` : la source est déclarée retirée, vérifier indépendamment.
- `possible_split` : plusieurs cibles proposées, intervention obligatoire.

Les chemins et `source_reference` sont explicitement conservés dans les résultats. Les observations hors du crosswalk restent dans l'ensemble d'entrées contrôlé mais ne créent pas de mapping.

## Limites de qualification

1. Pas d'ingestion native automatique des événements de redirection MediaWiki/Wikidata ni de rapprochement API en ligne.
2. Pas de publication automatique de crosswalk, ni d'édition du canon, ni de réécriture des engagements.
3. Les `retired` et `split_candidate` proviennent de constats **externes** et doivent être vérifiés ; ils ne sont pas inférés de simples disparitions de libellés.
4. Les observations sont indexées en mémoire avec plafond paramétrable (`--max-records`, 250 000 par défaut). Ne pas présenter cela comme une qualification de dump Wikidata massif.
5. Les noms de réviseurs existants ne sont pas des signatures authentifiées ; l'adoption d'une nouvelle correspondance nécessite une revue externe et un nouveau crosswalk versionné.
6. Les performances doivent encore être mesurées sur le corpus réel de l'utilisateur.

## Tests

`tests/test_wikidata_evolution_alpha5.py` inclut les cas valides et hostiles : collisions entre KQ, propriété KP/P, cycle, double observation, contrôle de hash, dépassement de limites, chemins non réinscriptibles et conservation des fichiers canoniques.
