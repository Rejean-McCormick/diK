# Changelog

## 1.0.0-alpha.6 — Adaptateur de redirections MediaWiki Action API

- Extraction depuis les réponses réelles `action=query&redirects=1` (JSON ou JSONL de réponses), avec validation stricte des titres Q et `Property:P`, limites de ressources et sortie JSONL atomique sans écrasement.
- Consultation HTTPS **opt-in**, ciblée sur les identifiants externes déjà associés par correspondance exacte approuvée ; lots bornés, contrôle de l’origine et limitation de fréquence.
- Chaîne reproductible API (ou réponses archivées) → observations avec empreintes → analyse alpha.5 **sans mutation**.
- Aucun retrait, split, fusion ou `exactMatch` déduit de l’absence d’un Q, d’un libellé ou d’une redirection.
- Tests réseau simulés, adversariaux, d’intégrité et de non-régression. Le traitement intégral des SQL dumps, RDF, deltas et tests réseau réels reste hors périmètre.

## 1.0.0-alpha.5 — gestion préliminaire des évolutions Wikidata

- `dik sync evolution` : observation typée des changements d’identité externes, vérification, chains et collisions.
- Refus des événements cycliques, ambigus, cross-kind ou non conformes ; garde-fous de sortie.
- Nouveau schéma candidat `dik-wikidata-evolution-event.schema.json` et tests adversariaux.
- Graphe et registre des correspondances jamais réécrits. Pas d’ingestion native de redirections Wikidata revendiquée.

# Changelog

## 1.0.0-alpha.4 — 2026-10-16

- Téléchargement explicite de dumps Wikidata officiels HTTPS avec `.part`, ETag/Last-Modified, reprise validée par Range, hachage SHA-256, quota et publication isolée non destructive.
- Parcours `sync import-mirror` réservé à une empreinte approuvée indépendamment du fichier téléchargé ; aucun KQ/P créé automatiquement.
- Comparaison de snapshots Wikidata en flux, événements JSONL et échantillons bornés, sans modification des corrections curatées.
- Tests hors réseau des interruptions, changements de source, sécurité de reprise et non-régression.
- Les deltas, redirections, fusions/scissions, redémarrage d’import `.bz2` au milieu du flux et benchmarks industriels restent hors périmètre.


## 1.0.0-alpha.3 — 2026-10-16

- Ajout du moteur de conciliation lexicale **en lecture seule**, avec deux files : libellés préférés concurrents pour le même KQ/KP et homonymes entre plusieurs identifiants. Aucun `exactMatch` automatique.
- Index SQLite dérivé enrichi de listes de conflits pré-calculées et paginées; rapports d’observations avec provenance, priorité et source; reconstruction des index alpha.2 nécessaire pour conciliation.
- CLI `dictionaries conflicts|compare|conflict-detail`, API locale `/api/conciliation`, `/api/variants`, `/api/conciliation/detail`. Atelier augmenté dans le parcours de concepts existant.
- Tests supplémentaires d’isolation langue/famille, désaccord des couches, homonymes, index périmé et HTTP. Les opérations canoniques restent inchangées.
- CI alignée sur pytest pour exécuter les vrais tests du projet.


## 1.0.0-alpha.2 — 2026-10-16

- Atelier local UI organisé par intentions (guide UX fourni, principes UX-01/05/06/07/09/11/12/14), avec fiche de concept, alignements distingués, couverture paginée pour 301 langues, vue clean/annotated et téléchargement du JSON compact réversible.
- Curation locale opt-in `--workspace` : publie seulement un catalogue candidat immuable à l’extérieur du projet canonique; jamais de substitution du KQ/KP ni d’approbation Wikidata.
- Contrôles HTTP : loopback, Host, Origin, jeton CSRF, confirmation explicite, tailles bornées, échappement HTML, CSP et refus POST par défaut.
- Rétrocompatibilité de l’ancienne API `html_page` et des commandes existantes; 8 nouveaux tests d’interface.
- Les manques de 1.0 stable restent documentés.


## 1.0.0-alpha.1 — 2026-10-16

- Préservation du moteur diK 0.3, Framework v11 draft.3.
- Ajout index SQLite, recherche inverse déterministe, journal de décisions, nouveau crosswalk, curation immuable, portefeuille, plans legacy, patches, sync idempotent, interface locale de lecture.
- Formats applicatifs diK 1.0 issus de la spécification candidate.2; pas de ratification.
- Tests nouveaux et tests historiques séparés; voir VALIDATION.md.
- Voir IMPLEMENTATION_STATUS.md pour les fonctionnalités incomplètes.

## 1.0.0-alpha.7 — Import local transactionnel

- Ajout de `dik sync import-large` : traitement JSON/JSONL/gzip/bzip2 ligne par ligne, extraction des seuls alignements exacts acceptés, index SQLite temporaire.
- Checkpoints atomiques (données et progression), reprise à l'offset des sources non compressées ou par relecture des sources compressées.
- Publication de dictionnaires immuables compatibles Framework v11 draft.3, empreintes et import idempotent.
- Empreinte d'origine indépendante optionnelle, marquage explicite des sources non attestées.
- Nouveaux tests adversariaux et documentation d'exploitation `docs/docs/24_IMPORT_INDUSTRIEL_LOCAL_v1-alpha7.md`.
- **Non livré** : import de vrais deltas Wikidata, authentification multi-utilisateur, index crosswalk intégralement sur disque, qualification sur un dump complet.
