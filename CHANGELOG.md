## 2026-11-23 — Interface inter-dépôts diK / Wikidata (candidat)

- Références KQ/KP namespace-scoped, crosswalk Q/P, 13 langues cibles, lecture seule.
- Nouveau contrat documentaire, précontrôles ou index dérivé; aucune activation ni promotion.
- Tests de garde-fous et provenance de snapshot ; compatibilité historique conservée.

## V5.7 — 23 novembre 2026 — Pont lexical complet EncyK → diK (candidats)

- Production incrémentale de 14 dictionnaires SQLite depuis la totalité de l’index EncyK par langue (sources `complete`).
- Bilan complet de provenance, reprise transactionnelle et export expurgé compact, sans accès réseau.
- Aucun téléchargement de petites parties, aucune fusion sémantique ni promotion implicite, aucune modification des bases EncyK.
- Documents, intégration CLI, contrôles SHA/manifestes et tests de sécurité.

# Changelog

## 2026-11-23 — V5.4 / 1.0.0-alpha.12 : candidats locaux et assertions typés

- Lecteurs basés sur les **noms de champs réellement profilés sous Windows V5.3** : `local_identity_candidate/1` et `local_wikidata_statement/1`. Aucune inférence depuis le nom du fichier ou les chaînes rencontrées dans les preuves.
- Analyse des propositions `(namespace,KQ/KP) → Q/P` : cohérence, contradiction, ou absence de lien officiel accepté ; aucun statut revendiqué par la source ne devient une acceptation.
- Rapports d'observations non lexicales séparés, sans formes ni publication ; reprise SQLite invalidée si le mapping canonique accepté change.
- Statut `empty_source`, nouveau bilan expurgé V5.4 et CLI `sources export-v54` (`export-v53` conservé).
- Les 4 schémas GF-Wikidata restent inconnus en l'absence de valeurs JSONL certifiées. Voir [chapitre 62](docs/docs/62_CONNECTEURS_LOCAUX_IDENTITES_ASSERTIONS_V5_4.md).


## Intégration additive — scanner 14 langues (2026-11-21)

- Nouvelle commande native `dik coverage scan14` sur les 14 langues cibles UNESCO déjà déclarées (en, fr, es, de, nl, sv, da, no, nn, fi, et, af, it, pt).
- Rapports lecture seule JSON/CSV : registre KQ/KP complet, états directs/repli/manquant/langue non configurée, couches lexicales et liste des lacunes.
- Inventaire Konstellation facultatif, strictement **non aligné** : aucun `exactMatch`, aucune traduction ou modification du canon inférée à partir des mots.
- Contrôles d'intégrité diK Framework préalables à tout rapport, sortie neuve atomique et refus d'écrasement. Alpha non certifiée.


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


## DIK-LEX-1 v0.3 — overlay candidat cumulatif, sans changement de version de release

- Conserve les étapes v0.1/v0.2 : 7 910 candidats ISO 639-3, source inventory, tests, manifests.
- 7 910 emplacements de collection candidats (aucun dictionnaire publié), catalogue de 25 ressources à licence non revue.
- IANA TXT / tags BCP 47 conservateurs, acquisition HTTPS opt-in, réconciliation candidate avec SHA et publication immuable.
- Observation Lexemes Wikidata L/S/F indépendante, compteurs lexicaux et handoff GF non mappé; aucune promotion `exactMatch` ou `curated`.
- CLI `dik world`, documentation/ADR et tests adversariaux.

## 1.0.0-alpha.8 — Source Manager local et références réelles (2026-11-22)

- `dik sources discover|verify`: inventaire ciblé, sans réseau, registre immuable horodaté et pointeur courant sous diK/reports, SHA-256 borné, aucun déplacement ni activation implicite.
- `dik coverage resolve14 --resource-registry`: réutilisation des chemins des catalogues v11, validation Framework indépendante, aucune déduction d'identité depuis les mots.
- `--wikidata-source-id`: désignation explicite d'un candidat de dump Q/P, sans certification de licence/provenance ; GF, L/S/F et JSONL thématiques non alignés restent candidats.
- Détection des deux dispositions connues du portefeuille officiel; garde-fou `min-kristals`, tests unitaires et smoke sur 2 Kristals réels.
- Documentation actualisée dans 44–46 et ADR-DIK-LEX-3. Aucune traduction langue→langue, aucun changement du canon.


## 2026-11-23 — alpha.9 / V5 experimental qualification

- Added `dik sources qualify`: SHA-checked, read-only readiness report for existing local GF/Wikidata/v11 files, distinguishing test fixtures and fingerprint duplicates.
- Added optional `--observe-qid-lexicon` to `coverage resolve14`; only Q/P labels with reviewed crosswalk associations appear as **candidates** in a separate CSV; no coverage inflation or translation.
- Added alpha.9 documentation chapters 48–50 and ADR-DIK-LEX-4.
- No automatic GF→KQ mapping, Wikidata L/S/F publishing, licensing certification or migration of the 69 non-evaluable Kristals.

## 2026-11-23 — V5.1 : reconnaissance du format QID réellement fourni

- Le lecteur accepte les entrées JSONL `{"Q...": {"fr": "..."}}` en plus des lignes `{"qid":"Q...","labels":{...}}`.
- Diagnostics différenciant schéma reconnu, QID recoupant les correspondances acceptées et formes observées.
- Toujours **zéro publication ou traduction implicite**, avec contrôle des conflits QID+locale et codes de langue exacts.
- Documents 49 et 51 actualisés. Sur le fichier réel de 50 QID, aucun recoupement avec les QID acceptés du dernier rapport V5.


## 2026-11-23 — V5.2 : audit Wikidata thématique par Q/P accepté

- Nouveau module `wikidata_thematic` : lecture bornée des 40 JSONL thématiques référencés, contrôles SHA/chemins, schémas explicites et déduplication des copies.
- `coverage resolve14 --observe-wikidata-thematic` : rapproche les seuls Q/P non contradictoires, déjà acceptés et prouvés, des libellés explicites des 14 locales ; produit deux CSV candidats et le bilan dans `rapport.json`. **Aucune activation ni hausse de couverture artificielle.**
- `sources qualify` : sondage QID ramené aux **14 codes exacts** (exclusion de `nb` des compteurs officiels) ; distinction du schéma reconnu et des droits non qualifiés.
- Nouvelle documentation chapitre 52 et ADR-DIK-LEX-5, tests de conflits, SHA, doublons, conventions linguistiques et séparation des compteurs.
- Les sources thématiques réelles ne sont pas incluses dans le ZIP : audit sur le Windows du propriétaire encore requis.


## 2026-11-23 — Documentation V5.3 (proposition, **aucun code modifié**)

- Chapitres 53–60 : diagnostic V5.2 réel ; architecture des adaptateurs Wikidata thématiques ; profilage des schémas ; streaming et reprise ; preuves KQ/KP ↔ Q/P ; rapports et tests ; frontières GF/L/S/F.
- `ADR-DIK-LEX-6` proposé (non ratifié) et exemples non normatifs.
- Rectification documentaire : `no_accepted_qp_overlap` de V5.2 ne prouve **pas** l'absence de Q/P si le lecteur n'a reconnu aucune identité et si le fichier n'a pas été entièrement traité.
- **Statut logiciel inchangé : V5.2.** Ce document prépare V5.3, ne la livre pas.


## 1.0.0-alpha.11 — 2026-11-23

- Adaptateurs de découverte JSONL V5.3 typés et sans inférence linguistique.
- Reprise de lecture par offset/transaction SQLite, vérification SHA-256 avant/après et limites explicites.
- Jointure candidate Q/P vérifiés, rapports de schéma/progression/conflits, zéro activation.
- Documentation V5.3 passée de conception à état d’implémentation détaillé.


## 2026-11-23 — 1.0.0-alpha.13 / V5.5 : GF-Wikidata en tableaux JSON

- Lecture en streaming, avec reprise, des tableaux JSON multiligne malgré l'extension `.jsonl` des quatre fichiers réels `City`, `University`, `Country`, `Part_of world`.
- Profilage `container=json_array`, extraction des QID à partir des URL Wikidata exactes et des seuls `labels[locale]` explicites ; aucune description, traduction, alias ou équivalence devinée.
- Nouvel export `sources export-v55` et rapport `wikidata_v55`, sans écraser les commandes historiques.
- 46 889 entrées et 66 755 libellés en `en`/`sv` constatés dans les quatre fichiers transférés ; aucune publication implicite.
- Voir chapitre 63 et `tests/test_wikidata_v55.py`.


## 2026-11-23 — 1.0.0-alpha.14 / V5.6 : Source Manager local + en ligne

- Nouveau module `online_sources.py` : accès HTTPS Wikidata uniquement sur consentement explicite, pour les Q/P déjà acceptés dans les Kristals officiels v11 et preuves KS.
- Fournisseurs Kaikki et GF-RGL catalogués avec leurs licences, **pas** d'import automatique ni de mapping par mots.
- Cache des réponses API content-addressed avec SHA-256, progression atomique après chaque batch, absence de fallback linguistique, détection des redirections et refus des données altérées.
- Observations candidates dans `coverage resolve14 --online-index`, compteur du potentiel de couverture distinct, sans changement des totaux validés.
- `dik sources export-v56` pour la transmission d'un ZIP expurgé. Documentation [64](docs/docs/64_SOURCE_MANAGER_EN_LIGNE_CIBLE_WIKIDATA_V5_6.md), tests d'API simulée et de scan complet.

## V5.8 (23 novembre 2026) — Pont de preuves EncyK échantillonnées

- Nouvel adaptateur `semantic_evidence_bridge.py` dans le sous-système DIK-LEX-1.
- Réconciliation par `candidate_id` EncyK exact, langue stricte, provenance
  source/ligne et statut homographe vs preuve liée à la même entrée.
- Fédérer les bases v0.5/v0.6 en lecture seule au lieu de dupliquer les Go
  EncyK ; 14 petites liaisons privées et un ZIP de bilan expurgé.
- Vérification du fingerprint officiel de l'index EncyK, du contrat candidate
  et des colonnes/index SQLite ; refus de source obsolète.
- Aucune publication, ni validation de licences, ni mapping automatique KQ/KP.

## V5.10 — Registre canonique multirévision, diagnostic 126 Kristals (2026-11-24)

- Découverte supplémentaire de tous les registres et crosswalks V11 déclarés dans les `canon/state.index.json` ; pas de dépendance aux noms `identity-registry.json` / `registry.json`.
- Tables dérivées séparant **180 révisions sources** et les identités/crosswalks V5.9 déjà acceptés. Aucun choix implicite d'une révision active, aucune équivalence déduite et aucun nouveau Q/P approuvé.
- Mesure des liens dédoublonnés par Kristal + namespace + KQ/KP + Q/P ; préservation des preuves et des statuts par révision.
- Références des 49 formats non V11 et 7 artefacts manquants dans les diagnostics, sans migration des sources.
- Commande `dik world federation-revision-query` et audit renforcé ; documentation `docs/docs/69_INDEX_CANONIQUE_MULTIREVISIONS_V5_10.md`.
- Testé avec le snapshot officiel de 126 Kristals : 77 avec V11, 180 révisions, 25 741 liens source cumulés / 12 919 distincts ; **0 promotion automatique**.

## V5.11 — 2026-11-24 : sélection dérivée des révisions, sécurité renforcée

- Ajout `canonical_selection.py`, table des empreintes source et table des décisions de sélection dans le registre fédéré SQLite, sans changer l'interface V5.9.
- Sélection automatique limitée à une unique révision V11 complètement inspectée ; aucun choix automatique parmi plusieurs versions.
- Support facultatif d'un fichier de décisions explicitement revues et SHA-256 épinglées (`--selection-file`), **pour consultation dérivée uniquement**.
- Refus des décisions obsolètes, des graphes non inspectés et des conflits d'exactMatch acceptés au sein d'une révision.
- CLI `federation-selection-query` et `federation-selection-review` ; rapport expurgé, aucune nouvelle approbation, aucune écriture dans les Kristals.
- Test sur snapshot officiel : 126 Kristals, 77 V11, 180 révisions, 5 révisions uniques consultables en vue dérivée, 72 Kristals multirévisions sans sélection automatique, 49 sans V11.
- Documentation d'architecture et contrat de revue : chapitre 70 et ADR-DIK-FEDERATION-02.
