# 59 — Plan de développement et d'acceptation pour le prochain prompt (V5.3)

> **Mise à jour du 23 novembre 2026 :** les composants dont les formats sont prouvés sont implémentés dans **alpha.11**. Lire le [chapitre 61 — état réellement livré](61_IMPLEMENTATION_EFFECTIVE_V5_3.md). Les parties visant des schémas locaux encore inconnus demeurent des spécifications, non des fonctionnalités certifiées.

**Document de passage à l'implémentation — 2026-11-23.** Cette livraison installe **uniquement de la documentation**. Aucune commande `dik` décrite ici comme *future* ne doit être supposée existante.

## Objectif mesurable

Remplacer les conclusions ambiguës de V5.2 par une lecture thématique **schema-aware, exhaustive ou explicitement partielle**, capable de retrouver les identifiants Q/P d'après leurs véritables chemins de champs et d'observer les formes explicitement présentes, **sans activer de source ni modifier la couverture lexicale**.

## Lots de développement proposés (dans cet ordre)

| Lot | Développement futur | Critère de sortie |
|---|---|---|
| 0 — Fixtures réelles | Prélever en local de petits exemples représentatifs des 36 JSONL Kristal locaux et des 4 GF-Wikidata ; expurger si nécessaire | Schéma/type/chemin d'identifiant et licence documentés pour chaque famille ; si non lisible, `schema_unknown` |
| 1 — Profilage | Détecteur déterministe de formes JSONL, registre d'adaptateurs versionné, chemins de champs prouvés | Les 35 « no overlap » V5.2 sans Q/P deviennent diagnostic explicite, **pas** fausse absence |
| 2 — Parsing | Adaptateurs typés pour QID key/labels, identity candidates, statements et datasets GF-Wikidata **selon fixtures** | Aucune confusion sujet/prédicat/objet, Q/P vs L/S/F, champ label vs description |
| 3 — Lecture longue | Streaming, budget configurable, checkpoint atomique, reprise par offset et SHA | `City.jsonl` / `University.jsonl` atteignent EOF ou `partial_*` avec motif et reprise ; résultats idempotents |
| 4 — Jointure | Index Q/P accepted de `(namespace,KQ/KP)` v11 + matching exact par schéma | Pas de nouveau `exactMatch` obtenu d'un mot ; conflits et ambiguïtés isolés |
| 5 — Diagnostics | CSV source/schema, lignes extraites, recoupements et observations candidates ; statuts discriminants | Rapport cohérent, zéro augmentation artificielle de couverture |
| 6 — Intégration | CLI existante préservée, documentation des **options réellement implémentées**, tests et emballage Windows | Revue des fichiers installés, sauvegardes, rollback et scan local en lecture seule |

## Tests obligatoires

### Schémas et identité

- QID en clé externe (fixture V5.1) ; `qid` et `id` explicites ; chemins imbriqués **validés seulement par une fixture**.
- JSONL d'une liste, d'une chaîne, d'un dictionnaire de locale sans Q/P, d'un objet invalide : pas de faux match.
- `subject`, `predicate`, `object` différenciés ; un QID apparaissant dans une valeur ne crée pas de lien canonique.
- `L1`, `L1-S1`, `L1-F1`, GF `LexiconFre` et des chiffres de nom similaires ne sont pas convertis en Q/P ou KQ/KP.
- Mapping KQ↔Q et KP↔P doit être exact, accepté, avec preuve KS dans le namespace ; le même nombre de suffixe n'est pas une preuve.
- Deux sources contradictoires pour Q/P+locale → conflit, aucune sélection silencieuse.
- Chaîne en `nb` ou `nn` n'alimente pas `no` ; les 14 codes exacts restent inchangés.

### Exhaustivité et fiabilité

- Fichier 150 001 lignes : V5.3 ne peut conclure `complete_no_accepted_qp_overlap` après 150 000 lignes.
- Reprise à partir d'un checkpoint = exécution sans interruption, y compris le nombre de candidats et de conflits.
- Arrêt au milieu d'une ligne, UTF-8 BOM, dernière ligne sans saut, caractères accentués et non latins.
- Changement SHA entre deux passages ou avant/après un scan : invalide la source, aucune publication.
- Sources identiques par SHA dédupliquées sans confondre provenance et nombre de fichiers.
- Aucun chemin hors racines autorisées, symlink/jonction, écriture dans les JSONL tiers ou dans les Kristals.

### Compteurs / rapports

- `schema_unknown` et `no_qp_extracted` distincts de `complete_no_accepted_qp_overlap`.
- Une source tronquée n'a pas une absence prouvée ; `PARTIAL` persiste.
- Le nombre d'observations candidates peut augmenter ; les `totaux.catalogue_courant`, `catalogue_raccorde`, `wikidata_observe` et `non_resolu` restent invariants si aucune source n'est activée.
- Aucun faux « 126 entièrement évalués » : les 69 hors v11 restent signalés.
- Rapport JSON/CSV versionné, sans données brutes ni chemins sensibles dans un export expurgé.

## Matrice de preuve requise avant livraison

1. Tests unitaires/contrats sur fixtures et suites existantes diK.
2. Tests d'intégration des vrais fichiers **en lecture seule**, sur Windows PS7 et Python installé.
3. Tableau de couverture **des 40 sources** : schema validé / inconnu, complet / partiel, Q/P extraits, intersection, labels observables, conflits et droits.
4. Comparaison numérique au baseline V5.2 : 126 / 57 / 69, 5 269, 40 sources, 11 188/294 364 ; toute différence de périmètre doit être expliquée.
5. Audit du paquet d'installation avec validation des chemins, SHA, sauvegardes, idempotence, refus des fichiers locaux modifiés et restauration simulée. Les tests Linux ne suffisent pas pour certifier PowerShell/Windows.

## Questions ouvertes à trancher au moment de coder

- Schémas effectifs de `identity-candidates.jsonl`, `statements.jsonl` et des quatre datasets GF-Wikidata : le bilan V5.2 **n'inclut pas leurs enregistrements**, seulement leurs chemins et les compteurs. Le code devra découvrir les champs sur le disque ou recevoir des exemples authentiques. **Ne pas figer les adaptateurs sur des suppositions.**
- Stratégie de profilage de source très volumineuse : volumes/budgets et modes d'expurgation à confirmer selon la machine.
- Droits de publication, politique d'attribution et gouvernance d'approbation : jamais déduits d'un chemin ou de la présence d'un label.
- Connecteur L/S/F et réalisation GF : prochain chantier distinct, après preuve du mapping.

## Instructions pour le prochain prompt de code

« Implémente dans diK le contrat documentaire V5.3 (chapitres 53–59, ADR-DIK-LEX-6), en conservant les CLI existantes, en lisant **les vrais formats** des fichiers JSONL locaux sans deviner, en terminant les scans longs par reprise, et en produisant des diagnostics candidats sans aucune traduction ou activation automatique. Mets ensuite la documentation à jour avec ce qui est *effectivement* codé, exécute les tests et prépare un installateur protégé. »

Ce texte est un **cahier de développement** et non un ordre d'exécuter du code dans la présente livraison.
