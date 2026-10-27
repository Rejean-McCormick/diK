# Alpha.6 — Extraction de redirections Wikidata depuis MediaWiki Action API

## Objectif et périmètre

diK sait maintenant convertir **les réponses réelles de l’API MediaWiki** avec `action=query&redirects=1` en `dik-wikidata-evolution-event` v1 candidat. Il peut interroger l'API **sur demande** pour les identifiants externes Q/P ayant un `exactMatch` accepté dans le registre Kristal. Ce sont des **observations**, pas des décisions ni des commandes de migration.

Source amont : https://www.mediawiki.org/wiki/API:Query et https://www.mediawiki.org/wiki/Wikibase/API. Le dump recommandé des entités Wikidata est un tableau JSON d’entités : son format **n’inclut pas** automatiquement toutes les redirections comme un historique de migrations; ne pas le traiter comme une source de redirections exhaustive. Les fichiers SQL, RDF, XML et dumps incrémentaux ont des contrats différents et ne sont pas pris en charge par cet adaptateur.

## Contrat d’entrée

- `--format action-api-json`: une réponse JSON de l’API contenant `query.redirects` (tableau facultatif).
- `--format action-api-jsonl`: une réponse JSON MediaWiki complète par ligne, pour archiver les lots interrogés.
- `query.redirects`: chaque entrée `from`, `to` doit porter un titre exact `Q123` ou `Property:P123`. Les namespaces incompatibles, faux identifiants KQ, cycles, doublons et réponses API `error` sont refusés.
- `query.pages` avec `missing` ou sans `query.redirects` n’est **pas** une preuve de suppression : aucun événement `retired` n'est généré.
- Toute réponse nécessitant une pagination (`continue`) est refusée : l'opérateur doit archiver séparément les pages correctes selon leur contrat.
- Entrées et sorties bornées; extraction en flux des fichiers JSONL, les réponses unitaires ont une taille limitée; les événements de sortie ne sont publiés qu’après validation complète. Pas d’écrasement de fichier existant.

## Parcours recommandé

1. `dik sync probe-redirects --crosswalk ... --registry ... --namespace ... --user-agent ... --output replies.jsonl` — consultation **réseau explicite**, HTTPS `www.wikidata.org` uniquement, IDs approuvés, 25 par lot (max 50), temporisation 1 s (minimum 0,5 s), nombre d'IDs limité (500 par défaut, maximum 5000).
2. Archiver `replies.jsonl` et le SHA-256 affiché. Le résultat décrit les redirections observées **au moment du test**, pas l'état historique d'un ancien dump.
3. `dik sync extract-redirects --source replies.jsonl --format action-api-jsonl --snapshot <id> --approved-sha256 <hash> --output observations.jsonl` — extraction hors réseau. Un hash approuvé indépendamment protège l'intégrité des octets mais ne prouve pas l'authenticité de l'amont.
4. `dik sync evolution --observations observations.jsonl --approved-sha256 <hash_sortie> --crosswalk ... --registry ... --namespace ... --snapshot <id> --events impacts.jsonl` — audit non destructif des mappings affectés.
5. Révision humaine des preuves; toute création d’une nouvelle révision de crosswalk relève du circuit de gouvernance approuvé. diK ne fusionne pas de KQ/KP.

## Invariants anti-drift

- Identifiants Q/P **externes**, KQ/KP **internes**, jamais substitués silencieusement.
- Extraction = observation ; analyse = proposition ; revue = décision ; publication sémantique = outil autorisé distinct.
- Une absence, une modification de libellé ou une redirection ne signifie pas qu'un concept Kristal a disparu.
- Sorties et archives brutes conservées séparément, avec empreintes; pas de mutation du graphe, des catalogues lexicalisés ou du crosswalk.
- Les URL redirigées hors domaine Wikimedia approuvé sont refusées, pas seulement les URL initiales.

## Limites

Non démontrés : exécution contre l'API publique en conditions réelles; export exhaustif des redirects du wiki; ingestion de dumps SQL/RDF, incrémentaux ou des splits; téléchargements massifs; quotas auprès de Wikimedia en charge réelle; signatures/authentification des données; gestion de réviseurs multi-utilisateur; publication des Kristals.
