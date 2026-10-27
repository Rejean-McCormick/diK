# 13 — Sécurité, provenance, licence et confiance

## SEC-001 — Modèle des menaces

Entrées potentiellement hostiles : dumps Wikidata, dictionnaires tiers, archives legacy, documents d'IA, labels avec Markdown/HTML/JSON malicieux, noms de fichiers, manifestes/path, fichiers trop volumineux et liens symboliques. Risques : exécution arbitraire, path traversal, zip/decompression bomb, injection SQL/HTML/Markdown, SSRF lors de téléchargement, effacement de couches curatées, falsification des décisions, empoisonnement de la recherche inverse.

## SEC-002 — Validation à chaque frontière

Utiliser parsing strict JSON Schema officiel pour artefacts Framework, validation de schéma applicatif pour documents diK, limites de taille/profondeur, UTF-8, contrôles namespace/type, chemins confinés au root, sorties JSON échappées, requêtes SQL paramétrées, quotas de ressources. Le contenu des dumps n'est jamais une instruction pour une IA, un appel système ou un interpréteur.

## SEC-003 — Intégrité vs authenticité

SHA-256 protège contre corruption accidentelle et permet adressage par contenu, mais ne prouve pas qui a émis un fichier. Le système affiche `hash_verified` distinct de `publisher_authenticated`. Pour des approbations distribuées, prévoir signature et contrôle des rôles ; aucune signature fictive ou « approved by AI » n'est acceptable.

## SEC-004 — Revue et rôles

Rôles conceptuels : `viewer`, `editor` (propositions), `reviewer` (approbations), `publisher` (snapshots), `operator` (imports). Un environnement mono-utilisateur peut implémenter un mode local explicite mais doit garder l'identité et les décisions d'audit. Un agent IA ne doit pas être compté comme réviseur humain ni contourner une approbation. Séparation des responsabilités pour décisions critiques, configurable suivant gouvernance.

## SEC-005 — Licences

Toute source externe exige métadonnées licence, origine, version, conditions d'usage/redistribution. Sans licence connue/compatible : quarantaine ; ne pas redistribuer automatiquement les entrées. Les données importées ne deviennent pas libres parce qu'elles sont encodées en JSONL. Les fichiers diK distribués doivent respecter l'AGPL et notices du code utilisé, sans inventer des permissions de redistribution.

## SEC-006 — Restauration historique

Les anciens commits/empreintes/bytes sont intouchables. La vérification d'un nouveau Kristal ne doit pas exiger la présence de Wikidata en ligne. Prévenir exfiltration de textes soumis en projet privé (pas de recherche distante implicite ni index central).

## SEC-007 — Déni de service

Quota taille fichier/shard, limite de langue sélectionnée par tâche, budget temps/mémoire, cancellation safe, nombre max de candidats/requêtes, liens symboliques et noms Unicode ambigus traités de manière explicite ; liste blanche de sources réseau, pas de téléchargement arbitraire sur URLs fournies par un dump.

## Cas de tests indispensables

SEC-T1 traversal JSON path, SEC-T2 HTML hostile rendu clean, SEC-T3 injection SQL dans alias, SEC-T4 réécriture d'une couche importée publiée, SEC-T5 faux SHA recalculé présenté comme signature, SEC-T6 reviewer absent, SEC-T7 quota dépassé et rollback, SEC-T8 import licence inconnue, SEC-T9 project multi-namespace fuite interdite.
